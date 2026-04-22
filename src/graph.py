from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from src.config import settings
from src.intents import classify_intent, extract_lead_fields, missing_lead_fields
from src.llm import build_chat_model
from src.rag import LocalRetriever
from src.state import ConversationState
from src.tools import mock_lead_capture


retriever = LocalRetriever(settings.knowledge_base_path)
chat_model = build_chat_model()


def _history_as_text(history: list[dict[str, str]]) -> str:
    return "\n".join(f"{item['role']}: {item['content']}" for item in history[-6:])


def detect_intent_node(state: ConversationState) -> ConversationState:
    lead_info = extract_lead_fields(state["user_input"], state.get("lead_info"))
    missing_fields = missing_lead_fields(lead_info)
    awaiting_details = state.get("awaiting_lead_details", False)

    if awaiting_details:
        intent = "high_intent_lead"
        if missing_fields:
            reason = "Lead collection is already in progress."
        else:
            reason = "Lead collection is complete and ready for tool execution."
    else:
        intent, reason = classify_intent(state["user_input"])

    return {
        "lead_info": lead_info,
        "missing_fields": missing_fields,
        "current_intent": intent,
        "intent_reason": reason,
        "ready_for_capture": intent == "high_intent_lead" and not missing_fields,
    }


def retrieve_knowledge_node(state: ConversationState) -> ConversationState:
    docs = retriever.retrieve(state["user_input"])
    return {"retrieved_docs": docs}


def _fallback_rag_response(state: ConversationState) -> str:
    docs = state.get("retrieved_docs", [])
    if not docs:
        return (
            "I can help with AutoStream pricing, features, refunds, and support. "
            "Ask me about the Basic or Pro plan and I’ll break it down."
        )

    lines = ["Here’s what I found about AutoStream:"]
    for doc in docs:
        lines.append(f"- {doc['content']}")

    if any(doc["id"] == "pricing_pro" for doc in docs):
        lines.append(
            "If you want to try the Pro plan, I can also help capture your details."
        )

    return "\n".join(lines)


def answer_inquiry_node(state: ConversationState) -> ConversationState:
    docs = state.get("retrieved_docs", [])

    if chat_model and docs:
        context = "\n".join(
            f"{doc['title']}: {doc['content']}" for doc in docs
        )
        prompt = (
            "You are a helpful SaaS sales assistant for AutoStream.\n"
            "Use only the provided knowledge base context.\n"
            "Be concise, accurate, and do not invent policy details.\n\n"
            f"Knowledge base context:\n{context}\n\n"
            f"Conversation so far:\n{_history_as_text(state.get('conversation_history', []))}\n\n"
            f"User question: {state['user_input']}"
        )
        result = chat_model.invoke(prompt)
        return {"response": result.content}

    return {"response": _fallback_rag_response(state)}


def respond_greeting_node(state: ConversationState) -> ConversationState:
    response = (
        "Hi! I can help with AutoStream pricing, features, refunds, or support. "
        "If you're ready to try a plan, I can also help capture your details."
    )
    return {"response": response}


def collect_lead_node(state: ConversationState) -> ConversationState:
    lead_info = state.get("lead_info", {"name": "", "email": "", "platform": ""})
    missing_fields = state.get("missing_fields", [])

    if not missing_fields:
        return {
            "awaiting_lead_details": False,
            "ready_for_capture": True,
        }

    prompts = {
        "name": "What’s your name?",
        "email": "What’s your email address?",
        "platform": "Which creator platform do you primarily use, like YouTube or Instagram?",
    }

    collected_labels = []
    if lead_info.get("name"):
        collected_labels.append(f"name: {lead_info['name']}")
    if lead_info.get("email"):
        collected_labels.append(f"email: {lead_info['email']}")
    if lead_info.get("platform"):
        collected_labels.append(f"platform: {lead_info['platform']}")

    prefix = "Awesome, I can help you get started on AutoStream."
    if collected_labels:
        prefix += " I already have your " + ", ".join(collected_labels) + "."

    next_field = missing_fields[0]
    response = f"{prefix} {prompts[next_field]}"

    return {
        "response": response,
        "awaiting_lead_details": True,
        "ready_for_capture": False,
    }


def capture_lead_node(state: ConversationState) -> ConversationState:
    lead_info = state["lead_info"]
    captured_message = mock_lead_capture(
        lead_info["name"],
        lead_info["email"],
        lead_info["platform"],
    )
    response = (
        f"{captured_message}\n"
        "You’re all set. A sales follow-up can now reach out with next steps for the plan you want."
    )
    return {
        "captured_message": captured_message,
        "response": response,
        "lead_captured": True,
        "awaiting_lead_details": False,
        "ready_for_capture": False,
    }


def route_after_intent(state: ConversationState) -> str:
    if state["current_intent"] == "high_intent_lead" or state.get("awaiting_lead_details"):
        return "collect_lead"
    if state["current_intent"] == "product_pricing_inquiry":
        return "retrieve_knowledge"
    return "respond_greeting"


def route_after_collection(state: ConversationState) -> str:
    if state.get("ready_for_capture"):
        return "capture_lead"
    return END


def build_graph():
    graph = StateGraph(ConversationState)

    graph.add_node("detect_intent", detect_intent_node)
    graph.add_node("retrieve_knowledge", retrieve_knowledge_node)
    graph.add_node("answer_inquiry", answer_inquiry_node)
    graph.add_node("respond_greeting", respond_greeting_node)
    graph.add_node("collect_lead", collect_lead_node)
    graph.add_node("capture_lead", capture_lead_node)

    graph.add_edge(START, "detect_intent")
    graph.add_conditional_edges(
        "detect_intent",
        route_after_intent,
        {
            "retrieve_knowledge": "retrieve_knowledge",
            "respond_greeting": "respond_greeting",
            "collect_lead": "collect_lead",
        },
    )
    graph.add_edge("retrieve_knowledge", "answer_inquiry")
    graph.add_edge("answer_inquiry", END)
    graph.add_edge("respond_greeting", END)
    graph.add_conditional_edges(
        "collect_lead",
        route_after_collection,
        {
            "capture_lead": "capture_lead",
            END: END,
        },
    )
    graph.add_edge("capture_lead", END)

    return graph.compile()
