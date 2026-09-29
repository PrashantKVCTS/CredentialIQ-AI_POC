import json
import os
from typing import List
from app.core.models import PolicyChunk

class LocalRagRepository:
    def __init__(self, knowledge_dir: str = "knowledge"):
        self.knowledge_dir = knowledge_dir
        self._chunks: List[PolicyChunk] = []
        self._load_policies()

    def _load_policies(self):
        if not os.path.exists(self.knowledge_dir):
            return

        for fname in os.listdir(self.knowledge_dir):
            if fname.endswith(".json"):
                fpath = os.path.join(self.knowledge_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                chunk = PolicyChunk(
                                    id=item.get("id", f"POL-{len(self._chunks)+1:03d}"),
                                    source_type=item.get("sourceType", "InternalPolicy"),
                                    jurisdiction=item.get("jurisdiction", "Federal"),
                                    provider_type=item.get("providerType", "All"),
                                    rule_reference=item.get("ruleReference", "REF-001"),
                                    title=item.get("title", "Credentialing Policy"),
                                    content=item.get("content", ""),
                                    effective_date=item.get("effectiveDate", "2024-01-01"),
                                    is_synthetic=item.get("isSynthetic", True)
                                )
                                self._chunks.append(chunk)
                except Exception as e:
                    print(f"Error loading policy file {fname}: {e}")

    async def retrieve_relevant_policies_async(self, query: str, state: str = "", top_k: int = 5) -> List[PolicyChunk]:
        query_terms = set(query.lower().split())
        scored_chunks = []

        for chunk in self._chunks:
            score = 0.0
            content_lower = chunk.content.lower()
            title_lower = chunk.title.lower()

            for term in query_terms:
                if len(term) > 2:
                    if term in title_lower:
                        score += 3.0
                    if term in content_lower:
                        score += 1.0

            if state and (chunk.jurisdiction.lower() == state.lower() or chunk.jurisdiction.lower() == "national" or chunk.jurisdiction.lower() == "federal"):
                score += 2.0

            if score > 0:
                chunk_copy = chunk.model_copy()
                chunk_copy.score = score
                scored_chunks.append(chunk_copy)

        scored_chunks.sort(key=lambda c: c.score, reverse=True)
        return scored_chunks[:top_k] if scored_chunks else self._chunks[:top_k]
