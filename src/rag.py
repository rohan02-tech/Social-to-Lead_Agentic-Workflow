from __future__ import annotations

import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.state import RetrievedChunk


class LocalRetriever:
    def __init__(self, kb_path: Path) -> None:
        raw_data = json.loads(kb_path.read_text(encoding="utf-8"))
        self.documents: list[dict[str, str]] = raw_data["documents"]
        self.corpus = [
            f"{doc['title']}. {doc['category']}. {doc['content']}"
            for doc in self.documents
        ]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(self.corpus)

    def retrieve(self, query: str, top_k: int = 3) -> list[RetrievedChunk]:
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.matrix).flatten()
        ranked_indices = similarities.argsort()[::-1][:top_k]

        results: list[RetrievedChunk] = []
        for index in ranked_indices:
            score = float(similarities[index])
            if score <= 0:
                continue
            document = self.documents[index]
            results.append(
                {
                    "id": document["id"],
                    "title": document["title"],
                    "category": document["category"],
                    "content": document["content"],
                    "score": round(score, 4),
                }
            )
        return results
