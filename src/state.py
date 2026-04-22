from __future__ import annotations

from typing import Literal, TypedDict


IntentLabel = Literal[
    "casual_greeting",
    "product_pricing_inquiry",
    "high_intent_lead",
]


class LeadInfo(TypedDict):
    name: str
    email: str
    platform: str


class RetrievedChunk(TypedDict):
    id: str
    title: str
    category: str
    content: str
    score: float


class ConversationState(TypedDict, total=False):
    user_input: str
    conversation_history: list[dict[str, str]]
    current_intent: IntentLabel
    intent_reason: str
    retrieved_docs: list[RetrievedChunk]
    response: str
    lead_info: LeadInfo
    missing_fields: list[str]
    awaiting_lead_details: bool
    ready_for_capture: bool
    lead_captured: bool
    captured_message: str
    turn_count: int
