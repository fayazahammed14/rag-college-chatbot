from pydantic import BaseModel
from typing import Optional, List


class ChunkBase(BaseModel):
    document_id: str
    chunk_index: int
    text: str
    page_number: int


class ChunkCreate(ChunkBase):
    embedding: Optional[List[float]] = None


class ChunkResponse(ChunkBase):
    id: str

    class Config:
        from_attributes = True


class ChunkWithSimilarity(ChunkBase):
    id: str
    similarity: float
    document_title: str
