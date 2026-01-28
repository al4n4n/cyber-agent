"""Simple RAG-style knowledge store."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from agent.ingest import ReportSummary


@dataclass
class KnowledgeChunk:
    id: str
    text: str
    source: str


class KnowledgeBase:
    def __init__(self, index_path: Path, chunk_size: int, chunk_overlap: int) -> None:
        self.index_path = index_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunks: list[KnowledgeChunk] = []

    @classmethod
    def from_config(cls, config: dict) -> "KnowledgeBase":
        rag_config = config["rag"]
        return cls(
            index_path=Path(rag_config["index_path"]),
            chunk_size=rag_config["chunk_size"],
            chunk_overlap=rag_config["chunk_overlap"],
        )

    def ingest(self, summaries: list[ReportSummary]) -> None:
        for summary in summaries:
            text = "\n".join(
                [
                    summary.title,
                    summary.url,
                    summary.technique,
                    summary.root_cause,
                    summary.remediation,
                    summary.raw_text,
                ]
            ).strip()
            for chunk in self._chunk_text(text):
                chunk_id = f"{summary.title}-{len(self.chunks)}"
                self.chunks.append(
                    KnowledgeChunk(id=chunk_id, text=chunk, source=summary.url)
                )

    def _chunk_text(self, text: str) -> list[str]:
        words = text.split()
        if not words:
            return []
        chunks: list[str] = []
        start = 0
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start = end - self.chunk_overlap
            if start <= 0:
                start = end
        return chunks

    def search(self, query: str, limit: int = 5) -> list[KnowledgeChunk]:
        scored = [
            (self._score(query, chunk.text), chunk) for chunk in self.chunks
        ]
        scored.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in scored[:limit]]

    def _score(self, query: str, text: str) -> float:
        query_terms = set(query.lower().split())
        text_terms = set(text.lower().split())
        if not query_terms or not text_terms:
            return 0.0
        return len(query_terms & text_terms) / len(query_terms | text_terms)

    def persist(self) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(chunk) for chunk in self.chunks]
        self.index_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
