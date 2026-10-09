"""Cliente OpenRouter (SDK openai) detras de un callable inyectable."""
from __future__ import annotations

from typing import Callable, Dict, List, Optional

import openai
from openai import OpenAI

BASE_URL = "https://openrouter.ai/api/v1"

LLM = Callable[[List[Dict]], str]

MSG_RATE_LIMIT = "El modelo gratuito está saturado, probá en unos segundos."
MSG_AUTH = "La API key de OpenRouter es inválida."
MSG_GENERIC = "No pude contactar al modelo. Intentá de nuevo."


class LLMError(Exception):
    """Fallo al llamar al LLM (el mensaje es amigable, en espanol)."""


def make_llm(api_key: str, model: str, client: Optional[object] = None) -> LLM:
    """Devuelve `llm(messages) -> str`. Traduce errores del SDK a LLMError."""
    if client is None:
        client = OpenAI(base_url=BASE_URL, api_key=api_key)

    def llm(messages: List[Dict]) -> str:
        try:
            resp = client.chat.completions.create(model=model, messages=messages)
        except openai.RateLimitError:
            raise LLMError(MSG_RATE_LIMIT)
        except openai.AuthenticationError:
            raise LLMError(MSG_AUTH)
        except (openai.APIConnectionError, openai.APIStatusError):
            raise LLMError(MSG_GENERIC)

        choices = getattr(resp, "choices", None) or []
        content = choices[0].message.content if choices else None
        if not content or not content.strip():
            raise LLMError(MSG_GENERIC)
        return content

    return llm
