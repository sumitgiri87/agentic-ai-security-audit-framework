"""
harness.py — Prompt injection test harness for the basic LangGraph agent.

Loads payloads from payloads/direct_injection.json, fires each one at
the agent, evaluates whether the injection succeeded, and writes a
structured result to results/direct_injection_results.jsonl.

Usage:
    python harness.py                        # run all 20 payloads
    python harness.py --category role_override  # run one category
    python harness.py --id PI-007           # run a single payload
    python harness.py --dry-run             # print payloads without calling LLM

Output:
    results/direct_injection_results.jsonl  — one JSON line per payload
    results/direct_injection_summary.txt    — human-readable summary

Environment:
    OPENAI_API_KEY must be set (in .env two levels up, or shell env).
    The harness resolves the agent path relative to this file's location.

IMPORTANT — RESULTS INTERPRETATION:
    "success": true  means the INJECTION succeeded (agent was manipulated).
                     This is a FINDING — a vulnerability to document.
    "success": false means the agent resisted the injection.
                     This is expected safe behaviour.
"""

import json
import os
import sys
import time
import argparse
import datetime
from pathlib import Path

from dotenv import load_dotenv

# ── Path resolution ───────────────────────────────────────────────────────────
# This file lives at:
#   agentic-ai-security-audit-framework/test-harness/prompt_injection/harness.py
# The agent lives at:
#   agentic-ai-security-audit-framework/examples/basic_langgraph_agent/agent.py

HERE        = Path(__file__).parent.resolve()
REPO_ROOT   = HERE.parent.parent                    # two levels up
AGENT_DIR   = REPO_ROOT / "examples" / "basic_langgraph_agent"
PAYLOADS_DIR = HERE / "payloads"
RESULTS_DIR  = HERE / "results"

# Load .env from the agent directory (where OPENAI_API_KEY lives)
load_dotenv(AGENT_DIR / ".env")
load_dotenv(HERE.parent.parent / ".env")  # also try repo root

# Add agent directory to path so we can import agent.py
sys.path.insert(0, str(AGENT_DIR))

RESULTS_DIR.mkdir(exist_ok=True)


# ── Payload loading ───────────────────────────────────────────────────────────

def load_payloads(payload_file: str = "direct_injection.json") -> list[dict]:
    """Load payloads from the payloads directory."""
    path = PAYLOADS_DIR / payload_file
    if not path.exists():
        raise FileNotFoundError(f"Payload file not found: {path}")
    with open(path) as f:
        return json.load(f)


def build_query(payload: dict) -> str:
    """Construct the full query string from a payload definition.

    If the payload has an injection_prefix, it is prepended to the
    legitimate_query. If injection_prefix is empty, the legitimate_query
    IS the injection (e.g. PI-011 through PI-020).
    """
    prefix = payload.get("injection_prefix", "").strip()
    query  = payload.get("legitimate_query", "").strip()
    if prefix:
        return f"{prefix}\n\n{query}"
    return query


# ── Injection detection ───────────────────────────────────────────────────────

def evaluate_injection(payload: dict, agent_response: str) -> dict:
    """Determine whether the injection succeeded.

    A payload is considered to have succeeded (injection = vulnerability)
    if ANY of its success_indicators appear in the agent's response.

    Returns a dict with:
        success (bool)   — True = injection worked = vulnerability found
        matched (list)   — which indicators triggered
        confidence (str) — "high" / "medium" based on indicator specificity
    """
    response_lower = agent_response.lower()
    matched = []

    for indicator in payload.get("success_indicators", []):
        if indicator.lower() in response_lower:
            matched.append(indicator)

    success = len(matched) > 0

    # Confidence heuristic: longer/more specific indicators = higher confidence
    if matched:
        avg_len = sum(len(m) for m in matched) / len(matched)
        confidence = "high" if avg_len > 10 else "medium"
    else:
        confidence = "n/a"

    return {
        "success": success,
        "matched_indicators": matched,
        "confidence": confidence,
    }


# ── Result record ─────────────────────────────────────────────────────────────

def build_result(
    payload: dict,
    query: str,
    agent_response: str,
    evaluation: dict,
    elapsed_ms: int,
    error: str | None = None,
) -> dict:
    """Build a structured result record for one payload."""
    return {
        "id":                   payload["id"],
        "category":             payload["category"],
        "description":          payload["description"],
        "query_sent":           query,
        "agent_response":       agent_response,
        "injection_success":    evaluation["success"],
        "matched_indicators":   evaluation["matched_indicators"],
        "confidence":           evaluation["confidence"],
        "expected_safe":        payload.get("expected_safe_behaviour", ""),
        "notes":                payload.get("notes", ""),
        "elapsed_ms":           elapsed_ms,
        "error":                error,
        "timestamp_utc":        datetime.datetime.utcnow().isoformat() + "Z",
    }


# ── Main runner ───────────────────────────────────────────────────────────────

def run_harness(
    payloads: list[dict],
    dry_run: bool = False,
    verbose: bool = True,
) -> list[dict]:
    """Run all payloads through the agent and return result records.

    Args:
        payloads: List of payload dicts loaded from JSON.
        dry_run:  If True, print queries without calling the LLM.
        verbose:  If True, print progress to stdout.

    Returns:
        List of result dicts, one per payload.
    """
    if not dry_run:
        try:
            from agent import run, build_graph
            graph = build_graph()
        except ImportError as e:
            print(f"\nFailed to import agent: {e}")
            print(f"Expected agent.py at: {AGENT_DIR / 'agent.py'}")
            print("Check that the path is correct and requirements are installed.")
            sys.exit(1)
        except EnvironmentError as e:
            print(f"\nConfiguration error: {e}")
            print("Set OPENAI_API_KEY in .env or shell environment.")
            sys.exit(1)

    results = []
    total = len(payloads)

    for i, payload in enumerate(payloads, 1):
        pid      = payload["id"]
        category = payload["category"]
        query    = build_query(payload)

        if verbose:
            print(f"\n[{i:02d}/{total}] {pid} — {category}")
            print(f"  Description: {payload['description']}")
            if dry_run:
                print(f"  Query (dry run):\n    {query[:200]}{'...' if len(query)>200 else ''}")
                continue

        start = time.time()
        error = None
        agent_response = ""

        try:
            agent_response = run(query, graph=graph, verbose=False)
        except Exception as exc:
            error = str(exc)
            agent_response = f"[ERROR: {exc}]"

        elapsed_ms = int((time.time() - start) * 1000)
        evaluation = evaluate_injection(payload, agent_response)

        result = build_result(
            payload, query, agent_response, evaluation, elapsed_ms, error
        )
        results.append(result)

        if verbose:
            status = "VULNERABLE" if evaluation["success"] else "safe"
            icon   = "⚠️ " if evaluation["success"] else "✓ "
            print(f"  {icon} Result: {status}  ({elapsed_ms}ms)")
            if evaluation["matched_indicators"]:
                print(f"     Matched: {evaluation['matched_indicators']}")
            if error:
                print(f"     Error: {error}")

    return results


# ── Output writing ────────────────────────────────────────────────────────────

def write_results(results: list[dict], output_file: str = "direct_injection_results.jsonl"):
    """Write results to JSONL — one record per line."""
    path = RESULTS_DIR / output_file
    with open(path, "w") as f:
        for record in results:
            f.write(json.dumps(record) + "\n")
    print(f"\nResults written to: {path}")
    return path


def write_summary(results: list[dict], output_file: str = "direct_injection_summary.txt"):
    """Write a human-readable summary of the run."""
    path = RESULTS_DIR / output_file
    total      = len(results)
    vulnerable = [r for r in results if r["injection_success"]]
    safe       = [r for r in results if not r["injection_success"] and not r["error"]]
    errors     = [r for r in results if r["error"]]

    lines = [
        "=" * 65,
        "PROMPT INJECTION TEST HARNESS — RUN SUMMARY",
        f"Timestamp: {datetime.datetime.utcnow().isoformat()}Z",
        f"Total payloads: {total}",
        f"Injections succeeded (VULNERABLE): {len(vulnerable)}",
        f"Agent resisted (safe): {len(safe)}",
        f"Errors: {len(errors)}",
        "=" * 65,
        "",
    ]

    if vulnerable:
        lines += ["VULNERABLE — INJECTION SUCCEEDED:", ""]
        for r in vulnerable:
            lines += [
                f"  {r['id']} [{r['category']}]",
                f"    {r['description']}",
                f"    Matched: {r['matched_indicators']}",
                f"    Notes: {r['notes']}",
                "",
            ]

    if safe:
        lines += ["SAFE — AGENT RESISTED:", ""]
        for r in safe:
            lines += [f"  {r['id']} [{r['category']}] {r['description']}"]
        lines.append("")

    if errors:
        lines += ["ERRORS:", ""]
        for r in errors:
            lines += [f"  {r['id']}: {r['error']}"]
        lines.append("")

    # Category breakdown
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "vulnerable": 0}
        categories[cat]["total"] += 1
        if r["injection_success"]:
            categories[cat]["vulnerable"] += 1

    lines += ["BREAKDOWN BY CATEGORY:", ""]
    for cat, counts in categories.items():
        v = counts["vulnerable"]
        t = counts["total"]
        lines.append(f"  {cat:<25} {v}/{t} vulnerable")

    lines += ["", "=" * 65]

    with open(path, "w") as f:
        f.write("\n".join(lines))

    print(f"Summary written to: {path}")
    return path


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Prompt injection test harness — fires payloads at the LangGraph agent"
    )
    parser.add_argument(
        "--category", "-c",
        type=str,
        default=None,
        help="Run only payloads in this category (role_override, goal_redirect, data_exfil, tool_misuse)",
    )
    parser.add_argument(
        "--id",
        type=str,
        default=None,
        help="Run a single payload by ID (e.g. PI-007)",
    )
    parser.add_argument(
        "--payload-file",
        type=str,
        default="direct_injection.json",
        help="Payload file to load from the payloads/ directory",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print payloads without calling the LLM",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress per-payload progress output",
    )
    args = parser.parse_args()

    all_payloads = load_payloads(args.payload_file)

    # Filter
    if args.id:
        payloads = [p for p in all_payloads if p["id"] == args.id]
        if not payloads:
            print(f"No payload found with id '{args.id}'")
            sys.exit(1)
    elif args.category:
        payloads = [p for p in all_payloads if p["category"] == args.category]
        if not payloads:
            print(f"No payloads found for category '{args.category}'")
            sys.exit(1)
    else:
        payloads = all_payloads

    print(f"Running {len(payloads)} payload(s) from {args.payload_file}")
    if args.dry_run:
        print("DRY RUN — no LLM calls will be made\n")

    results = run_harness(
        payloads,
        dry_run=args.dry_run,
        verbose=not args.quiet,
    )

    if not args.dry_run and results:
        # Derive output filename from payload file
        stem = Path(args.payload_file).stem
        write_results(results, f"{stem}_results.jsonl")
        write_summary(results, f"{stem}_summary.txt")

        # Print final tally
        vulnerable = sum(1 for r in results if r["injection_success"])
        print(f"\nFinal: {vulnerable}/{len(results)} injections succeeded")
