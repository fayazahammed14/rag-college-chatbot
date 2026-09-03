from typing import List, Dict, Any
from app.config.db import get_supabase_client
from app.config.settings import get_settings
from app.services.embedding_service import generate_embedding
import logging

logger = logging.getLogger(__name__)


async def retrieve_relevant_chunks(
    query: str,
    match_threshold: float = None,
    match_count: int = None
) -> List[Dict[str, Any]]:
    """
    Generates embedding for student query, calls Supabase RPC 'match_chunks',
    and returns relevant document chunks with similarity scores.
    """
    settings = get_settings()
    threshold = match_threshold if match_threshold is not None else settings.SIMILARITY_THRESHOLD
    count = match_count if match_count is not None else settings.TOP_K_CHUNKS

    # 1. Embed query
    query_vector = generate_embedding(query)

    # 2. Query Supabase vector match function via RPC
    supabase = get_supabase_client()
    try:
        response = supabase.rpc(
            "match_chunks",
            {
                "query_embedding": query_vector,
                "match_threshold": threshold,
                "match_count": count
            }
        ).execute()

        chunks = response.data or []
        logger.info(f"Retrieved {len(chunks)} chunks for query: '{query[:50]}...' with threshold {threshold}")
        return chunks

    except Exception as e:
        logger.error(f"Error executing vector retrieval RPC 'match_chunks': {e}")
        # Return empty list on failure to allow graceful fallback
        return []
