"""CLI: reconstruye el indice de ChromaDB desde docs/*.md."""
from __future__ import annotations

import os
import sys
from typing import List, Optional, Tuple

from rag.chunking import chunk_markdown
from rag.store import rebuild_collection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")
COLLECTION = "gestion_talento"


class IngestError(Exception):
    """Error de ingesta con mensaje en espanol."""


def read_docs(docs_dir: str) -> List[Tuple[str, str]]:
    """Devuelve [(nombre, contenido)] de los .md del directorio, ordenados por nombre."""
    if not os.path.isdir(docs_dir):
        raise IngestError("No encontré el directorio de documentos: %s" % docs_dir)
    names = sorted(n for n in os.listdir(docs_dir) if n.lower().endswith(".md"))
    if not names:
        raise IngestError("No encontré archivos .md en %s. Agregá documentación y reintentá." % docs_dir)
    docs = []
    for name in names:
        with open(os.path.join(docs_dir, name), encoding="utf-8") as f:
            docs.append((name, f.read()))
    return docs


def run_ingest(docs_dir: str, client, ef=None, collection_name: str = COLLECTION) -> int:
    """Lee docs, hace chunking y reconstruye la coleccion. Devuelve el numero de chunks."""
    chunks = []
    for name, text in read_docs(docs_dir):
        chunks.extend(chunk_markdown(text, name))
    return rebuild_collection(client, collection_name, chunks, ef=ef)


def main(argv: Optional[List[str]] = None) -> int:
    import chromadb

    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        count = run_ingest(DOCS_DIR, client)
    except IngestError as e:
        print("Error: %s" % e, file=sys.stderr)
        return 1
    print("Indexados %d chunks en %s" % (count, CHROMA_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
