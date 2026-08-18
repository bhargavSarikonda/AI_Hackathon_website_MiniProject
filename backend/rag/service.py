"""
Complete 5-Stage RAG Pipeline Orchestrator
Source Data (.docx) -> Ingestion -> Chunking -> Embedding -> Vector DB -> Retrieval -> Generation
"""

from typing import Any
from rag.ingestion import DocxIngestor, RawDocument
from rag.chunker import SemanticChunker, TextChunk
from rag.embedder import VectorEmbedder
from rag.vector_db import VectorStore
from rag.retriever import HybridRetriever
from rag.generator import ResponseGenerator
from rag.knowledge_base import FAQ_LIST
from rag.schemas import ChatMessage, ChatResponse, FAQItem


import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class RAGService:
    """Orchestrates the complete 5-stage RAG Pipeline."""

    def __init__(self):
        print("\n=======================================================")
        print("[RAG Pipeline] Initializing 5-Stage RAG Pipeline")
        print("=======================================================")

        # Stage 1: Ingest Source Data
        self.ingestor = DocxIngestor()
        self.raw_doc = self.ingestor.ingest()
        print(f"[Stage 1 - Ingestion] Ingested source: {self.raw_doc.filename}")

        # Stage 2: Semantic Chunking
        self.chunker = SemanticChunker()
        self.chunks: list[TextChunk] = self.chunker.chunk_document(self.raw_doc)
        print(f"[Stage 2 - Chunking]  Created {len(self.chunks)} semantic knowledge chunks")

        # Stage 3: Vector Embeddings
        self.embedder = VectorEmbedder()
        self.embedder.fit_chunks(self.chunks)
        self.chunk_embeddings = [self.embedder.embed_chunk(c) for c in self.chunks]
        print(f"[Stage 3 - Embedding] Generated {len(self.chunk_embeddings)} vector embeddings")

        # Stage 4: Vector Database (ChromaDB)
        self.vector_store = VectorStore()
        self.vector_store.add_documents(self.chunks, self.chunk_embeddings)
        print(f"[Stage 4 - Vector DB] Indexed {self.vector_store.get_document_count()} vectors in VectorStore")

        # Stage 4.5: Retriever
        self.retriever = HybridRetriever(self.vector_store, self.embedder)

        # Stage 5: Response Generator
        self.generator = ResponseGenerator()
        self.faqs = FAQ_LIST

        print("[RAG Pipeline]        Ready to serve queries!\n")

    def process_query(self, query: str, history: list[ChatMessage] = []) -> ChatResponse:
        """Processes user query through Vector DB search and Grounded Generation."""
        retrieved = self.retriever.retrieve(query, top_k=3)
        top_score = retrieved[0][1] if retrieved else 0.0
        reply, sources, suggested = self.generator.generate(query, retrieved, history)

        return ChatResponse(
            reply=reply,
            sources=sources,
            suggested_questions=suggested,
            confidence=round(top_score, 3)
        )

    def get_faqs(self) -> list[FAQItem]:
        """Returns curated hackathon FAQs."""
        return self.faqs

    def get_stats(self) -> dict[str, Any]:
        """Returns diagnostic statistics of the RAG pipeline."""
        return {
            "source_document": self.raw_doc.filename,
            "total_chunks": len(self.chunks),
            "vector_db_records": self.vector_store.get_document_count(),
            "vocabulary_size": len(self.embedder.vocabulary),
        }


# Singleton Service Instance
_rag_service: RAGService | None = None


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
