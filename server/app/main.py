from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import get_settings
from app.routers import profile_router, document_router, chat_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("campusmind-backend")

settings = get_settings()

app = FastAPI(
    title="CampusMind AI Backend",
    description="RAG-Powered College Information Assistant API built with FastAPI, Supabase pgvector, and Google Gemini.",
    version="1.0.0"
)

# CORS Configuration
origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "*"  # Allow all for development flexibility
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(profile_router.router, prefix="/api")
app.include_router(document_router.router, prefix="/api")
app.include_router(chat_router.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "CampusMind AI API",
        "status": "online",
        "docs_url": "/docs",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
