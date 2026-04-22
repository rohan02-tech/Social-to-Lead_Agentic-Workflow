from __future__ import annotations

import re
from typing import Iterable

from src.state import IntentLabel, LeadInfo


GREETING_KEYWORDS = {
    "hi",
    "hello",
    "hey",
    "good morning",
    "good evening",
}
INQUIRY_KEYWORDS = {
    "price",
    "pricing",
    "cost",
    "plan",
    "plans",
    "feature",
    "features",
    "support",
    "refund",
    "policy",
}
HIGH_INTENT_KEYWORDS = {
    "sign up",
    "signup",
    "start",
    "get started",
    "trial",
    "interested",
    "want to try",
    "want the pro plan",
    "ready",
    "give me details",
    "more details",
    "tell me more",
}
KNOWN_PLATFORMS = {
    "youtube": "YouTube",
    "instagram": "Instagram",
    "tiktok": "TikTok",
    "snapchat": "Snapchat", 
    "linkedin": "LinkedIn",
    "twitch": "Twitch",
    "facebook": "Facebook",
    "podcast": "Podcast",
}


def _contains_any(text: str, keywords: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)


def classify_intent(message: str) -> tuple[IntentLabel, str]:
    lowered = message.lower().strip()

    if _contains_any(lowered, HIGH_INTENT_KEYWORDS):
        return "high_intent_lead", "The user expressed purchase or sign-up intent."

    if _contains_any(lowered, INQUIRY_KEYWORDS):
        return "product_pricing_inquiry", "The user asked about pricing, features, or company policy."

    if _contains_any(lowered, GREETING_KEYWORDS):
        return "casual_greeting", "The message looks like a greeting or a short opener."

    return "product_pricing_inquiry", "Defaulted to inquiry because the message may need product information."


def extract_email(text: str) -> str | None:
    match = re.search(r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})", text)
    return match.group(1) if match else None


def extract_platform(text: str) -> str | None:
    lowered = text.lower()
    for key, value in KNOWN_PLATFORMS.items():
        if key in lowered:
            return value
    return None


def extract_name(text: str) -> str | None:
    patterns = [
        r"\bmy name is ([A-Za-z][A-Za-z\s'-]{1,40})",
        r"\bi am ([A-Za-z][A-Za-z\s'-]{1,40})",
        r"\bi'm ([A-Za-z][A-Za-z\s'-]{1,40})",
        r"\bthis is ([A-Za-z][A-Za-z\s'-]{1,40})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            candidate = match.group(1).strip(" .,")
            return " ".join(part.capitalize() for part in candidate.split())

    words = text.strip().split()
    blocked_tokens = {
        "ok",
        "okay",
        "hi",
        "hello",
        "hey",
        "thanks",
        "thank",
        "thankyou",
        "please",
        "details",
        "give",
        "more",
        "yes",
        "no",
        "cool",
    }
    if (
        1 <= len(words) <= 3
        and all(word.replace("-", "").isalpha() for word in words)
        and not extract_platform(text)
        and not extract_email(text)
        and not any(word.lower() in blocked_tokens for word in words)
    ):
        return " ".join(part.capitalize() for part in words)

    return None


def extract_lead_fields(text: str, existing: LeadInfo | None = None) -> LeadInfo:
    current = {
        "name": "",
        "email": "",
        "platform": "",
    }
    if existing:
        current.update(existing)

    email = extract_email(text)
    platform = extract_platform(text)
    name = extract_name(text)

    if email:
        current["email"] = email
    if platform:
        current["platform"] = platform
    if name and not current.get("name"):
        current["name"] = name

    return current


def missing_lead_fields(lead_info: LeadInfo) -> list[str]:
    required = ("name", "email", "platform")
    return [field for field in required if not lead_info.get(field)]
