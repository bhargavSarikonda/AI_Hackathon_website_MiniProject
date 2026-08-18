"""
Stage 4: ChromaDB Vector Database Module
Provides persistent and in-memory ChromaDB vector storage with automatic cosine index fallback.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any
from rag.chunker import TextChunk

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False


@dataclass
class VectorRecord:
    id: str
    chunk: TextChunk
    vector: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)


class ChromaVectorStore:
    """ChromaDB Vector Database implementation with metadata indexing and semantic search."""

    COLLECTION_NAME = "innovate_hackathon_rulebook"

    def __init__(self, persist_directory: str | Path | None = None):
        self.has_chroma = HAS_CHROMADB
        self.chroma_client = None
        self.collection = None
        self.records: list[VectorRecord] = []
        self._index: dict[str, VectorRecord] = {}

        if persist_directory is None:
            if os.getenv("VERCEL"):
                self.persist_directory = Path("/tmp") / "chroma_db"
            else:
                base_dir = Path(__file__).resolve().parent.parent.parent
                self.persist_directory = base_dir / "data" / "chroma_db"
        else:
            self.persist_directory = Path(persist_directory)

        if self.has_chroma:
            try:
                self.persist_directory.mkdir(parents=True, exist_ok=True)
                self.chroma_client = chromadb.PersistentClient(path=str(self.persist_directory))
                self.collection = self.chroma_client.get_or_create_collection(
                    name=self.COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"}
                )
                print(f"[ChromaDB] Initialized ChromaDB Persistent Client at: {self.persist_directory}")
            except Exception as e:
                print(f"[ChromaDB Notice] Using in-memory Chroma client: {e}")
                try:
                    self.chroma_client = chromadb.Client()
                    self.collection = self.chroma_client.get_or_create_collection(
                        name=self.COLLECTION_NAME,
                        metadata={"hnsw:space": "cosine"}
                    )
                except Exception:
                    self.has_chroma = False

    def add_documents(self, chunks: list[TextChunk], embeddings: list[dict[str, float]]):
        """Adds documents, embeddings, and metadata into ChromaDB."""
        # 1. In-memory record indexing
        for chunk, vector in zip(chunks, embeddings):
            record = VectorRecord(
                id=chunk.chunk_id,
                chunk=chunk,
                vector=vector,
                metadata=chunk.metadata
            )
            self.records.append(record)
            self._index[chunk.chunk_id] = record

        # 2. Add to ChromaDB collection if active
        if self.has_chroma and self.collection is not None:
            try:
                ids = [c.chunk_id for c in chunks]
                documents = [c.content for c in chunks]
                metadatas = [
                    {
                        "section_id": c.section_id,
                        "title": c.title,
                        "category": c.category,
                    }
                    for c in chunks
                ]
                # Upsert into Chroma collection
                self.collection.upsert(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                print(f"[ChromaDB] Successfully indexed {len(ids)} documents into Chroma collection '{self.COLLECTION_NAME}'")
            except Exception as exc:
                print(f"[ChromaDB Warning] Chroma indexing exception: {exc}")

    def similarity_search(self, query_vector: dict[str, float], top_k: int = 3) -> list[tuple[TextChunk, float]]:
        """Searches for top_k most similar chunks using Cosine Vector Similarity."""
        scored: list[tuple[TextChunk, float]] = []

        for record in self.records:
            # Cosine dot product
            score = 0.0
            for term, q_val in query_vector.items():
                if term in record.vector:
                    score += q_val * record.vector[term]

            scored.append((record.chunk, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def get_document_count(self) -> int:
        """Returns the total number of documents in the vector database."""
        if self.has_chroma and self.collection is not None:
            try:
                return self.collection.count()
            except Exception:
                pass
        return len(self.records)

    def get_chunk_by_id(self, chunk_id: str) -> TextChunk | None:
        """Retrieves a chunk by its ID."""
        record = self._index.get(chunk_id)
        return record.chunk if record else None

    def clear(self):
        """Clears all records in the database."""
        self.records.clear()
        self._index.clear()
        if self.has_chroma and self.collection is not None:
            try:
                self.chroma_client.delete_collection(self.COLLECTION_NAME)
                self.collection = self.chroma_client.create_collection(
                    name=self.COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception:
                pass


# Export alias
VectorStore = ChromaVectorStore
