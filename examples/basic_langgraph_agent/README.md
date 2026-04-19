# basic_langgraph_agent

A minimal LangGraph ReAct agent with three tools — web search, document retrieval, and a calculator. This is the base architecture for the `agentic-ai-security-audit-framework` example suite: the prompt injection test harness (Week 2) sends adversarial payloads through this agent, the `llm-audit-logger` middleware (Week 3) wraps it to produce compliance evidence, and the `agent-compliance-mapper` (Week 5) analyses its configuration against OSFI E-23 and EU AI Act requirements.

---

## Architecture

```
StateGraph (MessagesState)
  ├── node: agent   ← LLM with tools bound (ReAct reasoning)
  └── node: tools   ← ToolNode executes tool calls

Routing:
  agent → tools_condition → tools   (tool call requested)
                          → END     (final answer ready)
  tools → agent                     (always loop back)
```

## Files

| File | Purpose |
|---|---|
| `agent.py` | LangGraph StateGraph, graph construction, `run()` interface |
| `tools.py` | Tool definitions: `web_search`, `retrieve_document`, `calculator` |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |

## Setup

```bash
# 1. Clone the repo and navigate here
cd agentic-ai-security-audit-framework/examples/basic_langgraph_agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 4. Run the demo
python agent.py

# 5. Run a single query
python agent.py --query "What is the square root of 256?"
```

## Tool stubs

The `web_search` and `retrieve_document` tools are stubs — they return clearly labelled fake results so the agent runs without external API keys. Replace them with real implementations (Tavily, Chroma, FAISS) for production use. The `calculator` tool is fully functional.

## Attack surface

This agent is the target for the prompt injection test harness. The three attack vectors are:

- `web_search` — adversarial content embedded in simulated search results
- `retrieve_document` — poisoned document chunks injected via the retrieval step
- `calculator` — expression injection (restricted evaluator in place — tested to resist `__import__` and `os` calls)

The `run()` function in `agent.py` is the entry point for all test harness scenarios.

---

*Part of [agentic-ai-security-audit-framework](https://github.com/sumitgiri/agentic-ai-security-audit-framework)*
