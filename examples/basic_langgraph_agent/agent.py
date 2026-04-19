"""
agent.py — Basic LangGraph ReAct agent with three tools.

Architecture:
  StateGraph (MessagesState)
    ├── node: "agent"   — calls the LLM with bound tools
    └── node: "tools"   — ToolNode executes whichever tool the LLM chose

  Edge routing:
    agent → tools_condition → "tools"  (if tool call requested)
                            → END       (if no tool call — final answer)
    tools → agent                       (always return to agent after tool)

This is a standard ReAct (Reason + Act) loop. The agent reasons about
the query, decides which tool to call, observes the result, and repeats
until it has enough information to produce a final answer.

Usage:
    python agent.py                         # runs the built-in demo queries
    python agent.py --query "your question" # runs a single query

Environment:
    OPENAI_API_KEY must be set in .env or the shell environment.
    Optionally set OPENAI_MODEL (default: gpt-4o-mini).

AUDIT SURFACE NOTE:
    Every node transition, tool call, and LLM response in this graph is
    a logging point. The llm-audit-logger middleware (Week 3) wraps this
    agent by attaching an AuditCallbackHandler to the graph's callbacks.
    The prompt injection test harness (Week 2) sends adversarial inputs
    through the same run() interface used here.
"""

import os
import sys
import argparse
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode, tools_condition

from tools import TOOLS

load_dotenv()


# ── Model setup ───────────────────────────────────────────────────────────────

def get_model() -> ChatOpenAI:
    """Initialise the LLM with tools bound.

    The model is bound to TOOLS at construction time. LangChain's
    bind_tools() converts each @tool function into an OpenAI function
    schema and attaches it to every request.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY not found. "
            "Set it in .env or as a shell environment variable."
        )

    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    llm = ChatOpenAI(
        model=model_name,
        temperature=0,          # deterministic — important for security testing
        api_key=api_key,
    )
    return llm.bind_tools(TOOLS)


# ── Node definitions ──────────────────────────────────────────────────────────

def agent_node(state: MessagesState, model) -> dict:
    """Agent node — calls the LLM and returns its response.

    Receives the current message history and passes it to the LLM.
    The LLM either:
      (a) returns a tool_call → graph routes to ToolNode
      (b) returns a plain AIMessage → graph routes to END

    This is the node the prompt injection test harness targets.
    Adversarial content arriving via retrieve_document() or web_search()
    is present in state["messages"] when this node executes.
    """
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}


# ── Graph construction ────────────────────────────────────────────────────────

def build_graph(model=None) -> StateGraph:
    """Construct and compile the LangGraph StateGraph.

    Returns a compiled graph ready for invocation. Accepts an optional
    pre-built model for testing (e.g. with a mock LLM).
    """
    if model is None:
        model = get_model()

    tool_node = ToolNode(TOOLS)

    graph = StateGraph(MessagesState)

    # Nodes
    graph.add_node("agent", lambda state: agent_node(state, model))
    graph.add_node("tools", tool_node)

    # Entry point
    graph.set_entry_point("agent")

    # Conditional routing after agent node
    graph.add_conditional_edges(
        "agent",
        tools_condition,        # returns "tools" or END
    )

    # After tools always return to agent
    graph.add_edge("tools", "agent")

    return graph.compile()


# ── Public interface ──────────────────────────────────────────────────────────

def run(query: str, graph=None, verbose: bool = True) -> str:
    """Run the agent on a single query and return the final response.

    Args:
        query:   The user's input string.
        graph:   Optional pre-compiled graph (for testing / reuse).
        verbose: If True, prints intermediate steps to stdout.

    Returns:
        The agent's final text response as a string.

    This function is the entry point used by:
      - The CLI demo below
      - The prompt injection test harness (imports run() directly)
      - The audit logger wrapper (attaches callbacks before calling run())
    """
    if graph is None:
        graph = build_graph()

    initial_state = {"messages": [HumanMessage(content=query)]}

    if verbose:
        print(f"\n{'─'*60}")
        print(f"Query: {query}")
        print(f"{'─'*60}")

    result = graph.invoke(initial_state)

    messages = result["messages"]
    final_message = messages[-1]

    if verbose:
        # Print all intermediate steps
        for msg in messages[1:]:            # skip the original HumanMessage
            if isinstance(msg, AIMessage):
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        print(f"\n[tool call]  {tc['name']}({tc['args']})")
                else:
                    print(f"\n[final answer]\n{msg.content}")
            else:
                # ToolMessage
                tool_name = getattr(msg, "name", "tool")
                print(f"\n[tool result — {tool_name}]\n{msg.content[:300]}{'...' if len(msg.content) > 300 else ''}")

    return final_message.content


# ── CLI entry point ───────────────────────────────────────────────────────────

DEMO_QUERIES = [
    "What is 2 to the power of 10, plus the square root of 144?",
    "Search for recent research on prompt injection in LLM agents.",
    "Retrieve documents about model risk management requirements.",
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Basic LangGraph ReAct agent — demo runner"
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        default=None,
        help="Single query to run. If omitted, runs all demo queries.",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress intermediate step output.",
    )
    args = parser.parse_args()

    try:
        compiled_graph = build_graph()
    except EnvironmentError as e:
        print(f"\nConfiguration error: {e}")
        print("Copy .env.example to .env and add your OPENAI_API_KEY.")
        sys.exit(1)

    queries = [args.query] if args.query else DEMO_QUERIES

    for q in queries:
        answer = run(q, graph=compiled_graph, verbose=not args.quiet)
        if args.quiet:
            print(f"Q: {q}\nA: {answer}\n")
