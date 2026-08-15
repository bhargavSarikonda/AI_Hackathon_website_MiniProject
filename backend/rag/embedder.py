"""
Stage 3: Vector Embedding Module
Converts semantic text chunks and user queries into normalized high-dimensional vectors.
"""

import os
import math
import re
from typing import Any
from rag.chunker import TextChunk


class VectorEmbedder:
    """Generates normalized vector representations for documents and search queries."""

    SYNONYMS: dict[str, list[str]] = {
        "solo": ["alone", "individual", "single", "1", "one", "person", "team size"],
        "alone": ["solo", "individual", "single", "team size"],
        "chatgpt": ["ai tools", "claude", "copilot", "llm", "generative ai", "ai assistants", "ai"],
        "claude": ["chatgpt", "copilot", "llm", "ai tools", "ai"],
        "copilot": ["chatgpt", "claude", "llm", "ai tools", "ai"],
        "ai": ["chatgpt", "claude", "copilot", "models", "artificial intelligence", "llm", "tools"],
        "food": ["meal", "meals", "dinner", "breakfast", "lunch", "snacks", "tea", "coffee", "vegan", "vegetarian", "jain", "eat", "dining", "refreshment"],
        "eat": ["food", "meal", "meals", "dinner", "breakfast", "lunch", "snacks", "catering"],
        "sleep": ["nap", "rest", "quiet zone", "overnight", "dormitory", "stay", "accommodation"],
        "nap": ["sleep", "rest", "quiet zone", "dorm", "accommodation"],
        "stay": ["accommodation", "hotel", "dormitory", "rooms", "outstation", "bedding"],
        "accommodation": ["stay", "dorm", "rooms", "outstation", "hotel"],
        "prize": ["money", "cash", "award", "reward", "winner", "runner up", "trophy", "disbursement", "prizes"],
        "prizes": ["prize", "money", "cash", "award", "reward", "winner", "runner up", "trophy"],
        "money": ["prize", "cash", "disbursement", "bank transfer", "tds", "fee", "refund"],
        "rubric": ["judging", "score", "scoring", "criteria", "evaluation", "weights", "rounds", "evaluated", "scored"],
        "score": ["rubric", "judging", "criteria", "evaluation", "appeal", "dispute", "scored", "scoring", "weights"],
        "scored": ["rubric", "judging", "criteria", "evaluation", "score", "scoring", "weights"],
        "scoring": ["rubric", "judging", "criteria", "evaluation", "score", "weights", "rounds"],
        "judging": ["rubric", "score", "scoring", "criteria", "evaluation", "weights", "rounds", "judges", "jury"],
        "judges": ["judging", "rubric", "score", "criteria", "jury", "evaluation"],
        "evaluation": ["judging", "rubric", "score", "scoring", "criteria", "weights"],
        "evaluated": ["judging", "rubric", "score", "scoring", "criteria", "weights"],
        "criteria": ["rubric", "judging", "score", "scoring", "evaluation", "weights"],
        "track": ["tracks", "problem statements", "themes", "healthcare", "fintech", "climate", "agentic", "accessibility"],
        "tracks": ["track", "problem statements", "themes", "healthcare", "fintech", "climate", "agentic", "accessibility"],
        "theme": ["tracks", "track", "problem statements", "format", "topic"],
        "urgent": ["emergency", "medical", "harassment", "helpline", "safety", "help desk", "contact"],
        "emergency": ["urgent", "medical", "helpline", "first aid", "safety", "police", "contact"],
        "harassment": ["code of conduct", "complaint", "safety", "confidential", "zero tolerance", "incident"],
        "rules": ["prohibited", "allowed", "submission", "guidelines", "regulations", "disqualification"],
        "disqualification": ["disqualify", "banned", "penalties", "plagiarism", "sabotage", "cheating"],
        "submit": ["submission", "github", "video", "deck", "deadline", "package"],
        "submission": ["submit", "github", "video", "deck", "deadline", "package"],
        "certificate": ["cert", "participation", "achievement", "digital", "email", "certificates"],
        "certificates": ["certificate", "participation", "achievement", "digital", "email"],
        "ip": ["intellectual property", "ownership", "copyright", "license", "who owns"],
        "wifi": ["internet", "network", "ethernet", "connection", "speed", "power"],
        "mentor": ["mentors", "mentorship", "guidance", "help desk", "booking"],
        "mentors": ["mentor", "mentorship", "guidance", "help desk", "booking"]
    }

    def __init__(self):
        self.vocabulary: dict[str, int] = {}
        self.idf: dict[str, float] = {}
        self.is_fitted: bool = False

    def fit_chunks(self, chunks: list[TextChunk]):
        """Builds vocabulary and IDF statistics from corpus chunks."""
        doc_count = len(chunks)
        df_counts: dict[str, int] = {}

        for chunk in chunks:
            unique_terms = set(chunk.tokens)
            for term in unique_terms:
                df_counts[term] = df_counts.get(term, 0) + 1

        self.vocabulary = {term: idx for idx, term in enumerate(sorted(df_counts.keys()))}
        self.idf = {
            term: math.log((doc_count + 1) / (df + 1)) + 1.0
            for term, df in df_counts.items()
        }
        self.is_fitted = True

    def embed_chunk(self, chunk: TextChunk) -> dict[str, float]:
        """Generates TF-IDF vector embedding for a chunk."""
        return self._vectorize_tokens(chunk.tokens)

    def embed_query(self, query: str) -> dict[str, float]:
        """Generates an expanded vector embedding for a search query."""
        tokens = self._tokenize(query)
        expanded: list[str] = list(tokens)

        for t in tokens:
            if t in self.SYNONYMS:
                for syn in self.SYNONYMS[t]:
                    expanded.extend(self._tokenize(syn))

        return self._vectorize_tokens(expanded)

    def _vectorize_tokens(self, tokens: list[str]) -> dict[str, float]:
        tf: dict[str, float] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0.0) + 1.0

        vec: dict[str, float] = {}
        for t, count in tf.items():
            if t in self.idf:
                tf_weight = 1.0 + math.log(count)
                vec[t] = tf_weight * self.idf[t]

        # L2-normalize
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {t: v / norm for t, v in vec.items()}

    def _tokenize(self, text: str) -> list[str]:
        text_clean = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        stopwords = {
            "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
            "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
            "to", "was", "were", "will", "with", "all", "any", "both", "each",
            "few", "more", "most", "other", "some", "such", "than", "too", "very"
        }
        return [w for w in text_clean.split() if len(w) > 1 and w not in stopwords]
