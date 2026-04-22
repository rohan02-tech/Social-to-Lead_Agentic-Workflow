from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
KB_PATH = ROOT_DIR / "knowledge_base" / "autostream_kb.json"

load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    model_name: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    openai_api_key: str | None = os.getenv("OPEN_API_KEY")
    knowledge_base_path: Path = KB_PATH


settings = Settings()
