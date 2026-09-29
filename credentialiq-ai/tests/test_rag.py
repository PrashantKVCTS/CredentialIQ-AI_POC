"""Unit tests for local policy RAG repository."""

from app.repositories.rag_repository import RAGRepository


def test_rag_repository_search():
    repo = RAGRepository()
    matches = repo.search_policies("NCQA license verification standards", top_k=2)

    assert len(matches) > 0
    top_match = matches[0]
    assert top_match.similarity_score > 0.0
    assert top_match.chunk_id is not None
    assert top_match.content is not None


def test_rag_repository_empty_query():
    repo = RAGRepository()
    matches = repo.search_policies("", top_k=2)
    assert isinstance(matches, list)
