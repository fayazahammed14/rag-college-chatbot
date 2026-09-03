from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks, status
from typing import List, Optional
from app.services.auth_service import require_admin
from app.services.document_service import (
    create_document,
    process_and_index_document,
    list_all_documents,
    get_document_by_id,
    update_document_metadata,
    delete_document,
)
from app.models.document import DocumentResponse, DocumentStatusResponse

router = APIRouter(prefix="/documents", tags=["Documents (Admin Only)"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    admin_user: dict = Depends(require_admin)
):
    """
    Upload a PDF document and start the background text extraction, chunking, and embedding pipeline.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents (.pdf) are supported."
        )

    doc_title = title.strip() if title and title.strip() else file.filename.replace(".pdf", "")
    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty."
        )

    # 1. Create document record
    doc = await create_document(
        title=doc_title,
        filename=file.filename,
        uploader_id=admin_user["id"]
    )

    # 2. Trigger asynchronous processing & indexing in background
    background_tasks.add_task(process_and_index_document, doc["id"], file_bytes)

    return DocumentResponse(**doc)


@router.get("", response_model=List[DocumentResponse])
async def get_all_documents(admin_user: dict = Depends(require_admin)):
    """List all documents with processing statuses and metadata."""
    docs = await list_all_documents()
    return [DocumentResponse(**d) for d in docs]


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def poll_document_status(document_id: str, admin_user: dict = Depends(require_admin)):
    """Poll processing status of a specific document."""
    doc = await get_document_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return DocumentStatusResponse(**doc)


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_or_replace_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    title: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    admin_user: dict = Depends(require_admin)
):
    """
    Update document title or replace its PDF file (which triggers re-extraction & re-embedding).
    """
    doc = await get_document_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    # If new file provided, update metadata and reprocess
    if file:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF documents (.pdf) are supported."
            )
        file_bytes = await file.read()
        updated_title = title or doc["title"]
        updated_doc = await update_document_metadata(document_id, title=updated_title)
        
        # Schedule re-indexing
        background_tasks.add_task(process_and_index_document, document_id, file_bytes)
        return DocumentResponse(**updated_doc)

    # If only title update
    updated_doc = await update_document_metadata(document_id, title=title)
    return DocumentResponse(**updated_doc)


@router.delete("/{document_id}")
async def remove_document(document_id: str, admin_user: dict = Depends(require_admin)):
    """Delete a document and its cascading chunks."""
    doc = await get_document_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    await delete_document(document_id)
    return {"message": f"Document '{doc['title']}' and its associated embeddings deleted successfully."}
