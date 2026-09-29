"""Local policy RAG repository using TF-IDF and cosine similarity."""

import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import settings
from app.core.exceptions import RAGRepositoryError
from app.core.logging import logger
from app.schemas.common import PolicyChunkMatch


class RAGRepository:
    """In-memory vector-like policy retrieval repository using scikit-learn TF-IDF."""

    def __init__(self, knowledge_dir: Path | None = None):
        self.knowledge_dir = knowledge_dir or settings.knowledge_path
        self.chunks: list[dict] = []
        self.vectorizer: TfidfVectorizer | None = None
        self.tfidf_matrix = None
        self._load_and_index()

    def _load_and_index(self) -> None:
        """Load JSON policy files and fit TF-IDF vectorizer."""
        try:
            if not self.knowledge_dir.exists():
                logger.warning(f"Knowledge directory {self.knowledge_dir} does not exist.")
                return

            self.chunks = []
            for json_file in self.knowledge_dir.glob("*.json"):
                try:
                    with open(json_file, encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            self.chunks.extend(data)
                except Exception as e:
                    logger.error(f"Error reading policy file {json_file}: {e}")

            if not self.chunks:
                logger.warning("No policy chunks loaded into RAG repository.")
                return

            corpus = [
                f"{c.get('title', '')} {c.get('category', '')} {c.get('content', '')}"
                for c in self.chunks
            ]
            self.vectorizer = TfidfVectorizer(stop_words="english")
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
            logger.info(f"Loaded and indexed {len(self.chunks)} policy chunks for local RAG.")

        except Exception as e:
            logger.error(f"Failed to initialize RAG repository: {e}")
            raise RAGRepositoryError(str(e)) from e

    def search_policies(self, query: str, top_k: int = 3) -> list[PolicyChunkMatch]:
        """Search policy repository using query TF-IDF vector similarity."""
        if not self.chunks or not self.vectorizer or self.tfidf_matrix is None:
            return []

        try:
            query_vector = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]

            top_indices = similarities.argsort()[::-1][:top_k]
            results: list[PolicyChunkMatch] = []

            for idx in top_indices:
                score = float(similarities[idx])
                if score > 0.01:  # Relevance threshold
                    chunk = self.chunks[idx]
                    results.append(
                        PolicyChunkMatch(
                            chunk_id=chunk.get("chunk_id", f"CHUNK-{idx}"),
                            title=chunk.get("title", "Policy Rule"),
                            category=chunk.get("category", "General"),
                            content=chunk.get("content", ""),
                            similarity_score=round(score, 4),
                            source=chunk.get("source", "Internal Policy"),
                        )
                    )

            return results
        except Exception as e:
            logger.error(f"Error during policy RAG search: {e}")
            return []
