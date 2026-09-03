from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.auth_service import get_current_user
from app.services.rag_service import answer_student_question
from app.services.chat_service import (
    get_or_create_conversation,
    list_conversations_for_user,
    get_conversation_history,
    add_message_to_conversation,
    delete_user_conversation,
)
from app.models.message import AskQuestionRequest, AskQuestionResponse, MessageSource
from app.models.conversation import ConversationResponse, ConversationDetailResponse

router = APIRouter(tags=["Chat & Conversations"])


@router.post("/chat/ask", response_model=AskQuestionResponse)
async def ask_question(
    payload: AskQuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    RAG endpoint for student queries.
    1. Creates or resolves existing conversation.
    2. Persists the user question.
    3. Runs RAG retrieval + grounding pipeline with Gemini.
    4. Persists the AI response with source citations.
    5. Returns the generated answer and citations.
    """
    user_id = current_user["id"]
    question = payload.question.strip()

    # 1. Resolve or create conversation
    conv = await get_or_create_conversation(
        user_id=user_id,
        conversation_id=payload.conversationId,
        title_hint=question
    )
    conversation_id = conv["id"]

    # 2. Fetch existing history for context
    conv_history = await get_conversation_history(user_id=user_id, conversation_id=conversation_id)
    history_messages = (conv_history or {}).get("messages", [])

    # 3. Save user's question to messages table
    await add_message_to_conversation(
        conversation_id=conversation_id,
        role="user",
        content=question,
        sources=[]
    )

    # 4. Run RAG Pipeline
    answer, sources = await answer_student_question(
        question=question,
        conversation_history=history_messages
    )

    # 5. Save assistant's answer and sources
    await add_message_to_conversation(
        conversation_id=conversation_id,
        role="assistant",
        content=answer,
        sources=sources
    )

    return AskQuestionResponse(
        answer=answer,
        sources=[MessageSource(**s) for s in sources],
        conversationId=conversation_id
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_user_conversations(current_user: dict = Depends(get_current_user)):
    """List all past conversations for the authenticated student/admin."""
    convs = await list_conversations_for_user(current_user["id"])
    return [ConversationResponse(**c) for c in convs]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation_by_id(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Fetch full message history for a specific conversation."""
    conv = await get_conversation_history(
        user_id=current_user["id"],
        conversation_id=conversation_id
    )
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or access denied."
        )
    return ConversationDetailResponse(**conv)


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a conversation and all its messages."""
    await delete_user_conversation(
        user_id=current_user["id"],
        conversation_id=conversation_id
    )
    return {"message": "Conversation deleted successfully."}
