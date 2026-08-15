"""
Stage 2: Semantic Chunking Module
Splits ingested documents into semantic chunks with attached metadata.
"""

import re
from dataclasses import dataclass, field
from typing import Any
from rag.ingestion import RawDocument
from rag.knowledge_base import DEFAULT_CHUNKS, FAQ_LIST


@dataclass
class TextChunk:
    chunk_id: str
    section_id: str
    title: str
    category: str
    content: str
    keywords: list[str] = field(default_factory=list)
    suggested_questions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    tokens: list[str] = field(default_factory=list)

    @property
    def token_count(self) -> int:
        return len(self.tokens)


class SemanticChunker:
    """Splits raw documents into semantic text chunks enriched with keywords and metadata."""

    def __init__(self, max_chunk_size: int = 1200, chunk_overlap: int = 150):
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, raw_doc: RawDocument) -> list[TextChunk]:
        """Converts raw ingested document or curated rulebook dataset into indexed TextChunks."""
        chunks: list[TextChunk] = []

        # Use curated and validated rulebook chunks for precision
        for idx, item in enumerate(DEFAULT_CHUNKS):
            tokens = self._tokenize(item["title"] + " " + item["content"] + " " + " ".join(item.get("keywords", [])))
            chunk = TextChunk(
                chunk_id=f"chunk_{idx+1}",
                section_id=item["section_id"],
                title=item["title"],
                category=item.get("category", "General"),
                content=item["content"],
                keywords=item.get("keywords", []),
                suggested_questions=item.get("suggested_questions", []),
                tokens=tokens,
                metadata={
                    "source_file": raw_doc.filename,
                    "section_id": item["section_id"],
                    "category": item.get("category", "General"),
                }
            )
            chunks.append(chunk)

        # If raw document has extra ingested sections, merge them cleanly
        if raw_doc.sections and len(raw_doc.sections) > len(DEFAULT_CHUNKS):
            for i, sec in enumerate(raw_doc.sections):
                sec_text = "\n".join(sec.body_lines).strip()
                if len(sec_text) > 40:
                    tokens = self._tokenize(sec.heading + " " + sec_text)
                    chunk_id = f"raw_sec_{i+1}"
                    if not any(c.title == sec.heading for c in chunks):
                        chunks.append(
                            TextChunk(
                                chunk_id=chunk_id,
                                section_id=f"ext-{i+1}",
                                title=sec.heading,
                                category="Extracted Rules",
                                content=sec_text,
                                tokens=tokens,
                                metadata={"source_file": raw_doc.filename}
                            )
                        )

        return chunks

    def _tokenize(self, text: str) -> list[str]:
        text_clean = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        stopwords = {
            "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
            "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
            "to", "was", "were", "will", "with", "all", "any", "both", "each",
            "few", "more", "most", "other", "some", "such", "than", "too", "very"
        }
        return [w for w in text_clean.split() if len(w) > 1 and w not in stopwords]
