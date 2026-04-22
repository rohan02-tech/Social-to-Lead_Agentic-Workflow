# Social-to-Lead_Agentic-Workflow
AutoStream Social-to-Lead Agent is a Python + LangGraph conversational AI project that simulates a SaaS sales assistant. It answers pricing and policy questions using a local RAG knowledge base, detects high-intent users, and collects lead details across multiple turns before triggering a mock lead capture tool.

# AutoStream Social-to-Lead Agent

This project is a submission-ready scaffold for the ServiceHive Inflx assignment. It implements a conversational AI agent for the fictional SaaS product AutoStream using LangGraph for workflow orchestration, a local JSON knowledge base for RAG, and a guarded tool call for lead capture.

## Folder Structure

```text
autostream_social_to_lead_agent/
├── docs/
│   └── assignment.pdf
├── knowledge_base/
│   └── autostream_kb.json
├── src/
│   ├── config.py
│   ├── graph.py
│   ├── intents.py
│   ├── llm.py
│   ├── main.py
│   ├── rag.py
│   ├── state.py
│   └── tools.py
├── tests/
│   └── test_agent.py
├── .env.example
├── README.md
└── requirements.txt
```

## How To Run Locally

1. Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your API key if you want LLM-generated wording:

```bash
cp .env.example .env
```

4. Run the agent:

```bash
python -m src.main
```

5. Run tests:

```bash
pytest
```

## Expected Demo Flow

Try a conversation like this:

```text
Hi, tell me about your pricing.
That sounds good. I want to try the Pro plan for my YouTube channel.
My name is Rohan Rajak.
rohan@example.com
YouTube
```

The agent should answer with local knowledge first, detect the intent shift, collect the missing details, and only then trigger `mock_lead_capture()`.

## Architecture Explanation

I chose LangGraph because the assignment is not a single prompt-response chatbot; it is a small workflow with clear state transitions. The graph makes the behavior explicit: first detect intent, then either retrieve knowledge, answer a greeting, or enter lead qualification mode. That keeps the logic easy to debug and easy to explain in an interview or demo.

State is stored in a shared `ConversationState` object that carries the latest user message, retrieved knowledge chunks, detected intent, conversation history, and partially collected lead fields. This lets the agent remember details across 5 to 6 turns, which is important when a user shares their name, email, and creator platform separately. For retrieval, I used a local JSON knowledge base and a lightweight TF-IDF retriever so the project stays easy to run locally while still following a RAG pattern. Tool execution is intentionally guarded: the lead capture function is called only when all three required fields are present, preventing premature backend actions.

## WhatsApp Deployment Using Webhooks

To deploy this on WhatsApp, I would place the agent behind a lightweight FastAPI or Flask webhook service. WhatsApp messages would arrive through the Meta WhatsApp Business API webhook endpoint. The backend would validate the webhook signature, extract the sender ID and message text, restore that sender's conversation state from a database or Redis, and pass the text into the LangGraph workflow. After the graph returns the next response, the service would send it back through the WhatsApp send-message API. Lead captures could be stored in a CRM, Google Sheet, or internal sales API. This setup works well because each WhatsApp user maps naturally to one persistent conversation state, which makes multi-turn lead qualification reliable. 

## Clone the Repository

```bash
git clone https://github.com/rohan02-tech/Social-to-Lead_Agentic-Workflow.git
cd Social-to-Lead_Agentic-Workflow
