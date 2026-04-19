"""
tools.py — Tool definitions for the basic LangGraph agent.

Three tools:
  - web_search:        Simulates a web search (stub — replace with real
                       Tavily/SerpAPI key in production).
  - retrieve_document: Simulates document retrieval from a knowledge base
                       (stub — replace with real Chroma/FAISS retriever).
  - calculator:        Evaluates a basic arithmetic expression safely.

These tools are intentionally minimal. Their purpose is to give the agent
a realistic tool surface — search, retrieval, computation — so the
prompt injection test harness (Week 2) has meaningful attack vectors to
probe.

SECURITY NOTE: The calculator uses a restricted eval. Do not widen the
allowed names without reviewing the injection implications first.
"""

import math
import re
from langchain_core.tools import tool


# ── Web search (stub) ─────────────────────────────────────────────────────────

@tool
def web_search(query: str) -> str:
    """Search the web for current information about a topic.

    Args:
        query: The search query string.

    Returns:
        A string containing simulated search results.
        Replace the body of this function with a real API call
        (Tavily, SerpAPI, DuckDuckGo) when running against a live LLM.
    """
    # Stub — returns a clearly labelled fake result so tests are
    # deterministic without an API key.
    return (
        f"[STUB SEARCH RESULT for: '{query}']\n"
        f"Result 1: Example article about '{query}' — published 2025-01-15.\n"
        f"Result 2: Another source discussing '{query}' in detail.\n"
        f"Note: Replace this stub with a real search API for production use."
    )


# ── Document retrieval (stub) ─────────────────────────────────────────────────

@tool
def retrieve_document(query: str) -> str:
    """Retrieve relevant document chunks from the knowledge base.

    Searches a vector store for chunks semantically similar to the query
    and returns the top results.

    Args:
        query: The retrieval query string.

    Returns:
        Retrieved document chunks as a single string.
        Replace the body of this function with a real vector store
        retriever (Chroma, FAISS, pgvector) for production use.

    ATTACK SURFACE NOTE: In a real deployment this function fetches
    arbitrary document content from the vector store and injects it
    directly into the agent context. This is the primary injection
    point for the RAG prompt injection scenarios in the test harness.
    """
    # Stub — returns clearly labelled fake chunks.
    return (
        f"[STUB RETRIEVAL RESULT for: '{query}']\n"
        f"Chunk 1 (source: policy_doc_2024.pdf, page 3):\n"
        f"  'Standard operating procedure for {query} requires written approval.'\n\n"
        f"Chunk 2 (source: guidelines_v2.pdf, page 7):\n"
        f"  'All requests related to {query} must be logged in the audit system.'\n\n"
        f"Note: Replace this stub with a real vector store retriever."
    )


# ── Calculator ────────────────────────────────────────────────────────────────

# Whitelist of safe names for the restricted evaluator.
_SAFE_NAMES = {
    "abs": abs, "round": round, "min": min, "max": max, "sum": sum,
    "pow": pow, "sqrt": math.sqrt, "floor": math.floor, "ceil": math.ceil,
    "log": math.log, "log10": math.log10, "pi": math.pi, "e": math.e,
}

# Only allow digits, operators, parentheses, dots, spaces, and the safe names.
_ALLOWED_PATTERN = re.compile(r'^[\d\s\+\-\*\/\(\)\.\,\%\*\*]+$')


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression and return the result.

    Supports standard arithmetic (+, -, *, /, **), modulo (%), and
    common math functions (sqrt, log, floor, ceil, abs, round, min, max).

    Args:
        expression: A mathematical expression as a string.
                    Example: "2 ** 10 + sqrt(144)"

    Returns:
        The numeric result as a string, or an error message.

    SECURITY NOTE: Uses a restricted evaluator — only whitelisted names
    are available. Do not pass arbitrary Python expressions.
    """
    # Strip whitespace and validate
    expr = expression.strip()

    # Allow safe names in addition to numeric operators
    # Remove known safe function names before pattern-checking operators/digits
    cleaned = expr
    for name in _SAFE_NAMES:
        cleaned = cleaned.replace(name, "")

    if not re.match(r'^[\d\s\+\-\*\/\(\)\.\,\%\_]+$', cleaned):
        return (
            f"Error: expression contains disallowed characters. "
            f"Only arithmetic operators and whitelisted math functions are permitted. "
            f"Input was: '{expression}'"
        )

    try:
        result = eval(  # noqa: S307
            expr,
            {"__builtins__": {}},
            _SAFE_NAMES,
        )
        return f"{expression} = {result}"
    except ZeroDivisionError:
        return f"Error: division by zero in expression '{expression}'"
    except Exception as exc:
        return f"Error evaluating '{expression}': {exc}"


# ── Tool registry (imported by agent.py) ──────────────────────────────────────

TOOLS = [web_search, retrieve_document, calculator]
