from __future__ import annotations

from src.config import settings


def build_chat_model():
    if not settings.openai_api_key:
        return None

    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        return None

    return ChatOpenAI(model=settings.model_name, temperature=0)
