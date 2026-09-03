import google.generativeai as genai
from typing import List, Dict, Any, Tuple
from app.config.settings import get_settings
from app.services.retrieval_service import retrieve_relevant_chunks
import logging

logger = logging.getLogger(__name__)

FALLBACK_RESPONSE = "I don't have information on that in the uploaded college documents. Please contact the administrative office or check the official website for details on this topic."


def _format_context(chunks: List[Dict[str, Any]]) -> str:
    """Formats retrieved chunks into a clear referenced text block for Gemini."""
    formatted_sections = []
    for idx, chunk in enumerate(chunks, 1):
        doc_title = chunk.get("document_title", "Document")
        page_num = chunk.get("page_number", 1)
        text = chunk.get("text", "").strip()
        formatted_sections.append(
            f"--- SOURCE {idx}: [{doc_title} - Page {page_num}] ---\n{text}"
        )
    return "\n\n".join(formatted_sections)


def _format_history(history: List[Dict[str, Any]]) -> str:
    """Formats past messages in conversation for context."""
    if not history:
        return "No prior messages in this conversation."
    
    formatted = []
    for msg in history[-6:]:  # Use last 6 messages for context
        role = "Student" if msg.get("role") == "user" else "CampusMind AI"
        content = msg.get("content", "").strip()
        formatted.append(f"{role}: {content}")
    return "\n".join(formatted)


async def answer_student_question(
    question: str,
    conversation_history: List[Dict[str, Any]] = None
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Executes the full RAG pipeline:
    1. Vector retrieval of top chunks.
    2. Fallback check if no relevant content found.
    3. Grounded answer generation via Gemini 2.0 Flash with history context.
    4. Extraction of source references.
    """
    settings = get_settings()

    # 1. Retrieve top-k chunks
    chunks = await retrieve_relevant_chunks(
        query=question,
        match_threshold=settings.SIMILARITY_THRESHOLD,
        match_count=settings.TOP_K_CHUNKS
    )

    # 2. Strict Fallback if no relevant documents match
    if not chunks:
        logger.info(f"No chunks exceeded similarity threshold for query: '{question}'")
        return FALLBACK_RESPONSE, []

    # 3. Format sources list (deduplicated by doc_id and page_number)
    unique_sources = []
    seen = set()
    for chunk in chunks:
        key = (chunk.get("document_id"), chunk.get("page_number"))
        if key not in seen:
            seen.add(key)
            unique_sources.append({
                "document_id": str(chunk.get("document_id")),
                "document_title": chunk.get("document_title", "Official Notice"),
                "page_number": int(chunk.get("page_number", 1)),
                "similarity": round(float(chunk.get("similarity", 0.0)), 3)
            })

    # 4. Construct Grounded Prompt
    context_text = _format_context(chunks)
    history_text = _format_history(conversation_history or [])

    system_instruction = (
        "You are CampusMind AI, the official and intelligent college information assistant.\n"
        "Your mission is to provide accurate, helpful, and polite answers to students, faculty, and visitors.\n\n"
        "STRICT GROUNDING RULES:\n"
        "1. Answer the student's question STRICTLY and ONLY using the provided Official College Document Excerpts.\n"
        "2. Do NOT use outside general knowledge or make assumptions. If the document excerpt does not contain the answer, explicitly state that the uploaded documents do not contain this information.\n"
        "3. Maintain a warm, clear, professional, and supportive tone.\n"
        "4. When referring to facts, mention the document and page where relevant (e.g. 'According to the Academic Calendar (Page 3)...').\n"
        "5. Support follow-up questions naturally by referencing the conversation history.\n"
        "6. Format your response cleanly using Markdown (bullet points, bold highlights, tables where applicable)."
    )

    prompt = (
        f"{system_instruction}\n\n"
        f"=== RECENT CONVERSATION HISTORY ===\n{history_text}\n\n"
        f"=== OFFICIAL COLLEGE DOCUMENT EXCERPTS ===\n{context_text}\n\n"
        f"=== STUDENT QUESTION ===\n{question}\n\n"
        f"=== ANSWER ==="
    )

    # 5. Call Gemini
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(model_name=settings.GEMINI_MODEL)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,  # Low temperature for factual precision
                max_output_tokens=1024,
            )
        )
        
        answer_text = response.text.strip() if response.text else FALLBACK_RESPONSE
        return answer_text, unique_sources

    except Exception as e:
        logger.error(f"Error during Gemini generation: {e}", exc_info=True)
        return (
            "I encountered an issue generating an answer. Please verify that the AI service is properly configured.",
            unique_sources
        )
