"""Fixtures compartidas de pytest (vacio por ahora)."""


import chromadb
import pytest
from chromadb.config import Settings as ChromaSettings


@pytest.fixture
def client():
    """Cliente Chroma en memoria, aislado entre tests."""
    c = chromadb.EphemeralClient(settings=ChromaSettings(allow_reset=True))
    c.reset()
    yield c
    c.reset()
