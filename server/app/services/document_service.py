import io
from typing import List, Dict, Any, Optional
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config.db import get_supabase_client
from app.config.settings import get_settings
from app.services.embedding_service import generate_embeddings_batch
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def extract_text_by_pages(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Extracts text from PDF bytes page by page.
    Returns list of dicts with 'page_number' and 'text'.
    """
    reader = PdfReader(io.BytesIO(file_bytes))
    pages_data = []
    
    for idx, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        clean_text = page_text.strip()
        if clean_text:
            pages_data.append({
                "page_number": idx + 1,
                "text": clean_text
            })
            
    return pages_data, len(reader.pages)


def chunk_document_pages(pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Splits page texts into chunks of ~500-800 tokens (~2000 chars) with ~100 token overlap,
    preserving the page number attribution for each chunk.
    """
    settings = get_settings()
    # Approx 4 chars per token: 600 tokens ~ 2400 chars, 100 token overlap ~ 400 chars
    chunk_size = settings.CHUNK_SIZE * 4
    chunk_overlap = settings.CHUNK_OVERLAP * 4

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = []
    chunk_index = 0

    for page in pages_data:
        page_num = page["page_number"]
        page_text = page["text"]
        page_chunks = splitter.split_text(page_text)

        for chunk_text in page_chunks:
            if chunk_text.strip():
                chunks.append({
                    "chunk_index": chunk_index,
                    "text": chunk_text.strip(),
                    "page_number": page_num
                })
                chunk_index += 1

    return chunks


async def process_and_index_document(document_id: str, file_bytes: bytes):
    """
    Orchestrates the PDF extraction, chunking, embedding generation,
    and storage in Supabase document_chunks.
    """
    supabase = get_supabase_client()
    try:
        # 1. Extract text and page count
        pages_data, total_pages = extract_text_by_pages(file_bytes)
        
        if not pages_data:
            logger.warning(f"No extractable text found in document {document_id}.")
            supabase.table("documents").update({
                "status": "failed",
                "page_count": total_pages,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", document_id).execute()
            return

        # 2. Chunk text
        chunks = chunk_document_pages(pages_data)
        logger.info(f"Generated {len(chunks)} chunks across {total_pages} pages for document {document_id}.")

        # 3. Generate embeddings
        chunk_texts = [c["text"] for c in chunks]
        embeddings = generate_embeddings_batch(chunk_texts)

        # 4. Clear any existing chunks for this document (e.g. if re-processing / replacing)
        supabase.table("document_chunks").delete().eq("document_id", document_id).execute()

        # 5. Insert chunks with embeddings into document_chunks table
        rows_to_insert = []
        for i, chunk in enumerate(chunks):
            rows_to_insert.append({
                "document_id": document_id,
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"],
                "page_number": chunk["page_number"],
                "embedding": embeddings[i] if i < len(embeddings) else None
            })

        # Insert in batches of 50
        batch_size = 50
        for i in range(0, len(rows_to_insert), batch_size):
            supabase.table("document_chunks").insert(rows_to_insert[i:i + batch_size]).execute()

        # 6. Mark document as ready
        supabase.table("documents").update({
            "status": "ready",
            "page_count": total_pages,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", document_id).execute()

        logger.info(f"Successfully processed and indexed document {document_id}.")

    except Exception as e:
        logger.error(f"Failed to process document {document_id}: {e}", exc_info=True)
        try:
            supabase.table("documents").update({
                "status": "failed",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", document_id).execute()
        except Exception:
            pass


async def create_document(title: str, filename: str, uploader_id: str) -> Dict[str, Any]:
    """Creates a new document record with status 'processing'."""
    supabase = get_supabase_client()
    res = supabase.table("documents").insert({
        "title": title,
        "filename": filename,
        "uploaded_by": uploader_id,
        "status": "processing",
        "page_count": 0
    }).execute()
    return res.data[0]


async def list_all_documents() -> List[Dict[str, Any]]:
    """Retrieves all documents ordered by upload date."""
    supabase = get_supabase_client()
    res = supabase.table("documents").select("*").order("uploaded_at", desc=True).execute()
    return res.data or []


async def get_document_by_id(document_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves single document by ID."""
    supabase = get_supabase_client()
    res = supabase.table("documents").select("*").eq("id", document_id).execute()
    if res.data and len(res.data) > 0:
        return res.data[0]
    return None


async def update_document_metadata(document_id: str, title: Optional[str] = None) -> Dict[str, Any]:
    """Updates document title or metadata."""
    supabase = get_supabase_client()
    update_payload = {"updated_at": datetime.utcnow().isoformat()}
    if title:
        update_payload["title"] = title

    res = supabase.table("documents").update(update_payload).eq("id", document_id).execute()
    if not res.data:
        raise ValueError(f"Document {document_id} not found.")
    return res.data[0]


async def delete_document(document_id: str) -> bool:
    """Deletes a document and its cascading chunks."""
    supabase = get_supabase_client()
    res = supabase.table("documents").delete().eq("id", document_id).execute()
    return True
