import google.generativeai as genai
from typing import List, Union
from app.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)

_initialized = False


def _init_gemini():
    global _initialized
    if not _initialized:
        settings = get_settings()
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.startswith("your-"):
            logger.warning("GEMINI_API_KEY is not properly configured.")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _initialized = True


def generate_embedding(text: str) -> List[float]:
    """
    Generates a 768-dimensional vector embedding for the given text using gemini-embedding-001.
    """
    _init_gemini()
    settings = get_settings()
    try:
        clean_text = text.replace("\n", " ").strip()
        if not clean_text:
            return [0.0] * 768

        result = genai.embed_content(
            model=settings.EMBEDDING_MODEL,
            content=clean_text,
            task_type="retrieval_query",
            output_dimensionality=768,
        )
        return result["embedding"]
    except Exception as e:
        logger.error(f"Error generating embedding with Gemini: {e}")
        raise e


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generates 768-dimensional embeddings for a batch of document chunks.
    """
    _init_gemini()
    settings = get_settings()
    try:
        embeddings = []
        # Batch in chunks of 20 to avoid payload size limits
        batch_size = 20
        for i in range(0, len(texts), batch_size):
            batch = [t.replace("\n", " ").strip() for t in texts[i:i + batch_size]]
            valid_batch = [t if t else "empty" for t in batch]
            
            result = genai.embed_content(
                model=settings.EMBEDDING_MODEL,
                content=valid_batch,
                task_type="retrieval_document",
                output_dimensionality=768,
            )
            
            batch_embeddings = result["embedding"]
            # Ensure it's a list of lists
            if batch_embeddings and isinstance(batch_embeddings[0], float):
                embeddings.append(batch_embeddings)
            else:
                embeddings.extend(batch_embeddings)
                
        return embeddings
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {e}")
        # Fallback to one-by-one if batch call fails
        embeddings = []
        for text in texts:
            embeddings.append(generate_embedding(text))
        return embeddings
