"""Acceso a ChromaDB: embedding function unica, rebuild idempotente y apertura."""
from __future__ import annotations

from typing import List, Optional

from chromadb.errors import NotFoundError
from chromadb.utils import embedding_functions

from rag.chunking import Chunk

_SEP = " > "


def embedding_function():
    """Unico punto de cambio del embedding (default local de Chroma, ONNX MiniLM)."""
    return embedding_functions.DefaultEmbeddingFunction()


def rebuild_collection(client, name: str, chunks: List[Chunk], ef=None) -> int:
    """Borra la coleccion (si existe), la crea de cero e indexa `chunks`. Devuelve el conteo."""
    try:
        client.delete_collection(name)
    except (NotFoundError, ValueError):
        pass
    collection = client.create_collection(name, embedding_function=ef or embedding_function())
    if chunks:
        collection.add(
            ids=[c.id for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[
                {
                    "source": c.source,
                    "section": c.section,
                    "heading": c.section.split(_SEP)[-1],
                    "chunk_index": c.chunk_index,
                }
                for c in chunks
            ],
        )
    return len(chunks)


def open_collection(client, name: str, ef: Optional[object] = None):
    """Abre una coleccion existente con el mismo embedding usado al indexar.

    Devuelve None si no existe. Conviene llamarla en cada run (no cachear el handle):
    `rebuild_collection` recrea la coleccion con un id nuevo y deja obsoleto el handle viejo.
    """
    try:
        return client.get_collection(name, embedding_function=ef or embedding_function())
    except (NotFoundError, ValueError):
        return None
