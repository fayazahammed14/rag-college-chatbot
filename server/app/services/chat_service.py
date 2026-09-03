from typing import List, Dict, Any, Optional
from app.config.db import get_supabase_client
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


async def list_conversations_for_user(user_id: str) -> List[Dict[str, Any]]:
    """Fetches all conversations belonging to a user, ordered by most recently updated."""
    supabase = get_supabase_client()
    res = (
        supabase.table("conversations")
        .select("*")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .execute()
    )
    return res.data or []


async def get_or_create_conversation(
    user_id: str,
    conversation_id: Optional[str] = None,
    title_hint: Optional[str] = None
) -> Dict[str, Any]:
    """
    Finds an existing conversation or creates a new one for the user.
    """
    supabase = get_supabase_client()
    if conversation_id:
        res = (
            supabase.table("conversations")
            .select("*")
            .eq("id", conversation_id)
            .eq("user_id", user_id)
            .execute()
        )
        if res.data and len(res.data) > 0:
            return res.data[0]

    # Create new conversation
    title = (title_hint[:40] + "...") if title_hint and len(title_hint) > 40 else (title_hint or "New Chat")
    res = supabase.table("conversations").insert({
        "user_id": user_id,
        "title": title
    }).execute()
    return res.data[0]


async def get_conversation_history(user_id: str, conversation_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetches a conversation and all its messages in chronological order.
    """
    supabase = get_supabase_client()
    conv_res = (
        supabase.table("conversations")
        .select("*")
        .eq("id", conversation_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not conv_res.data:
        return None

    conv = conv_res.data[0]

    msg_res = (
        supabase.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=False)
        .execute()
    )
    conv["messages"] = msg_res.data or []
    return conv


async def add_message_to_conversation(
    conversation_id: str,
    role: str,
    content: str,
    sources: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Inserts a user or assistant message and touches the conversation updated_at timestamp.
    """
    supabase = get_supabase_client()
    sources_payload = sources or []
    msg_res = supabase.table("messages").insert({
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "sources": sources_payload
    }).execute()

    # Update conversation updated_at
    supabase.table("conversations").update({
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", conversation_id).execute()

    return msg_res.data[0]


async def delete_user_conversation(user_id: str, conversation_id: str) -> bool:
    """Deletes a conversation and cascaded messages."""
    supabase = get_supabase_client()
    supabase.table("conversations").delete().eq("id", conversation_id).eq("user_id", user_id).execute()
    return True
