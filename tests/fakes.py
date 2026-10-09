"""Fakes deterministas para tests offline."""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List

from chromadb.api.types import Documents, EmbeddingFunction, Embeddings


class FakeEmbeddingFunction(EmbeddingFunction[Documents]):
    """Embedding determinista (hash -> 8 floats). Nunca descarga modelos."""

    def __init__(self) -> None:
        pass

    def __call__(self, input: Documents) -> Embeddings:
        out = []
        for text in input:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            out.append([b / 255.0 for b in digest[:8]])
        return out

    @staticmethod
    def name() -> str:
        return "fake-embedding"

    def get_config(self) -> Dict[str, Any]:
        return {}

    @staticmethod
    def build_from_config(config: Dict[str, Any]) -> "FakeEmbeddingFunction":
        return FakeEmbeddingFunction()
