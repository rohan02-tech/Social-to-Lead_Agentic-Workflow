from __future__ import annotations

from src.graph import build_graph
from src.state import ConversationState


def run_cli() -> None:
    app = build_graph()
    state: ConversationState = {
        "conversation_history": [],
        "lead_info": {"name": "", "email": "", "platform": ""},
        "awaiting_lead_details": False,
        "lead_captured": False,
        "turn_count": 0,
    }

    print("AutoStream Social-to-Lead Agent")
    print("Type 'exit' to stop.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Session ended.")
            break

        state["user_input"] = user_input
        state["turn_count"] = state.get("turn_count", 0) + 1
        updated_state = app.invoke(state)

        response = updated_state["response"]
        print(f"Agent: {response}\n")

        history = state.get("conversation_history", [])
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})

        updated_state["conversation_history"] = history
        state = updated_state


if __name__ == "__main__":
    run_cli()
