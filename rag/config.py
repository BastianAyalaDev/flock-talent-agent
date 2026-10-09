"""Configuracion de la app: lee variables de entorno (y .env opcional)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

DEFAULT_MODEL = "google/gemma-4-31b-it:free"  # elegido en tarea 7.3 (ver apply-progress)


class ConfigError(Exception):
    """Configuracion invalida o incompleta (mensaje en espanol)."""


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str
    chroma_path: str = "./chroma_db"
    collection: str = "gestion_talento"
    top_k: int = 6
    history_turns: int = 3


def load_settings(env_file: Optional[str] = ".env") -> Settings:
    """Carga Settings. El entorno real tiene prioridad sobre el archivo .env."""
    if env_file is not None:
        load_dotenv(env_file, override=False)

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise ConfigError(
            "Falta OPENROUTER_API_KEY. Definila en el archivo .env (ver .env.example)."
        )

    model = os.environ.get("OPENROUTER_MODEL", "").strip() or DEFAULT_MODEL

    raw_top_k = os.environ.get("TOP_K", "").strip()
    try:
        top_k = int(raw_top_k) if raw_top_k else 6
    except ValueError:
        raise ConfigError("TOP_K debe ser un numero entero positivo.")
    if top_k < 1:
        raise ConfigError("TOP_K debe ser un numero entero positivo.")

    chroma_path = os.environ.get("CHROMA_PATH", "").strip()
    if chroma_path:
        return Settings(api_key=api_key, model=model, top_k=top_k, chroma_path=chroma_path)
    return Settings(api_key=api_key, model=model, top_k=top_k)
