"""
Innovate AI Hackathon 2026 - RAG AI Chatbot Module
==================================================
Modular Retrieval-Augmented Generation (RAG) system grounded in the official
event rulebook, policies, and logistics dataset.
"""

from rag.router import router
from rag.service import RAGService, get_rag_service
from rag.ingestion import DocxIngestor, RawDocument
from rag.chunker import SemanticChunker, TextChunk
from rag.embedder import VectorEmbedder
from rag.vector_db import VectorStore, ChromaVectorStore
from rag.retriever import HybridRetriever
from rag.generator import ResponseGenerator
from rag.schemas import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatSource,
    FAQItem,
    FAQResponse,
)

__all__ = [
    "router",
    "RAGService",
    "get_rag_service",
    "DocxIngestor",
    "RawDocument",
    "SemanticChunker",
    "TextChunk",
    "VectorEmbedder",
    "VectorStore",
    "ChromaVectorStore",
    "HybridRetriever",
    "ResponseGenerator",
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "ChatSource",
    "FAQItem",
    "FAQResponse",
]
