"""Retrieval top-k contra una coleccion de Chroma."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    source: str
    section: str
    distance: float


def retrieve(collection, question: str, k: int) -> List[RetrievedChunk]:
    """Devuelve los top-k chunks (orden de relevancia). Coleccion vacia -> []."""
    res = collection.query(query_texts=[question], n_results=k)
    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    dists = (res.get("distances") or [[]])[0]
    return [
        RetrievedChunk(
            text=doc,
            source=(meta or {}).get("source", ""),
            section=(meta or {}).get("section", ""),
            distance=float(dist),
        )
        for doc, meta, dist in zip(docs, metas, dists)
    ]
