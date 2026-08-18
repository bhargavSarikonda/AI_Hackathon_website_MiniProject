"""
Stage 4.5: Hybrid Vector Retriever
Bridges the VectorEmbedder and VectorStore to deliver fast, highly accurate semantic search.
"""

from typing import Any
from rag.chunker import TextChunk
from rag.embedder import VectorEmbedder
from rag.vector_db import VectorStore


class HybridRetriever:
    """Retrieves the top-k most relevant knowledge chunks using vector search."""

    def __init__(self, vector_store: VectorStore, embedder: VectorEmbedder):
        self.vector_store = vector_store
        self.embedder = embedder

    def retrieve(self, query: str, top_k: int = 3) -> list[tuple[dict[str, Any], float]]:
        """Generates query vector embedding, queries Vector DB, and returns scored chunks."""
        # 1. Embed query into vector space
        query_vector = self.embedder.embed_query(query)

        # 2. Query Vector DB via Cosine Similarity Index
        search_results = self.vector_store.similarity_search(query_vector, top_k=top_k)

        # 3. Format into dictionary representations
        formatted: list[tuple[dict[str, Any], float]] = []
        for chunk, score in search_results:
            chunk_dict = {
                "chunk_id": chunk.chunk_id,
                "section_id": chunk.section_id,
                "title": chunk.title,
                "category": chunk.category,
                "content": chunk.content,
                "keywords": chunk.keywords,
                "suggested_questions": chunk.suggested_questions,
                "metadata": chunk.metadata,
            }
            formatted.append((chunk_dict, score))

        return formatted
