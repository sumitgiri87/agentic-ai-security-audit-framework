# Control Mapping — Six Attack Dimensions → Frameworks & Regulation

This is the cross-reference promised in §5.3 of the root README: it maps each of
the [six attack dimensions](../README.md#2-the-six-attack-dimensions-existing-frameworks-miss)
to the controls in the major security frameworks and to the regulatory
instruments a Canadian, EU, or US-regulated enterprise has to answer to.

Use it two ways:

1. **Scoping an audit** — for each dimension in scope, the row tells you which
   framework controls and regulatory articles the finding will need to be
   reported against.
2. **Gap analysis** — if a dimension has no corresponding control in your
   current program, that is the gap.

> **Caveat.** This mapping is *indicative for scoping*, not a compliance
> attestation. Framework taxonomies evolve; in particular, confirm MITRE ATLAS
> technique IDs against the current [ATLAS matrix](https://atlas.mitre.org/) at
> audit time. OSFI E-23 is principles-based, so its column names the lifecycle
> expectation the dimension touches rather than a clause number. A
> machine-readable version of this table is in
> [`control-mapping.csv`](control-mapping.csv).

| # | Dimension | OWASP LLM Top 10 (2025) | NIST AI RMF | MITRE ATLAS | EU AI Act | OSFI E-23 |
|---|-----------|-------------------------|-------------|-------------|-----------|-----------|
| 1 | **Cognitive — Prompt Injection** | LLM01 Prompt Injection; LLM05 Improper Output Handling | MEASURE 2.7; MANAGE 2.1 | LLM Prompt Injection (AML.T0051) | Art. 15 (accuracy, robustness & cybersecurity) | Input controls; ongoing monitoring |
| 2 | **Temporal — Memory Poisoning** | LLM04 Data & Model Poisoning; LLM08 Vector & Embedding Weaknesses | MEASURE 2.6; MAP 5.1 | Data poisoning / RAG poisoning (verify ID) | Art. 10 (data governance); Art. 15 | Data integrity; ongoing monitoring |
| 3 | **Tool Integration — Action Chains** | LLM06 Excessive Agency | MANAGE 4.1; MEASURE 2.5 | LLM Plugin/Tool abuse (verify ID) | Art. 14 (human oversight); Art. 9 (risk management) | Controls design; change management |
| 4 | **Trust Boundary — Multi-Agent** | LLM06 Excessive Agency; LLM01 (propagated) | GOVERN 1.5; MAP 3.4 | LLM Jailbreak (AML.T0054) | Art. 9 (risk management); Art. 15 | Governance; third-party / component risk |
| 5 | **Identity Fluidity** | LLM06 Excessive Agency; LLM07 System Prompt Leakage | GOVERN 1.2; MANAGE 2.2 | LLM Data Leakage (verify ID) | Art. 12 (record-keeping); Art. 14 | Accountability; auditable trail |
| 6 | **Governance Gap** | LLM06 Excessive Agency; LLM10 Unbounded Consumption | GOVERN 2.1; MANAGE 4.2 | — (organisational, not a single technique) | Art. 14 (human oversight) | Senior-management accountability; oversight |

## Per-dimension audit evidence

What an auditor should expect to *see*, per dimension, to consider the control
operating effectively:

1. **Cognitive — Prompt Injection:** isolation of retrieved/untrusted content
   from instructions; deny-by-default tool gating; logged block/escalate
   decisions on injected content. *(See the guardrail in
   `secure-enterprise-knowledge-hub`.)*
2. **Temporal — Memory Poisoning:** provenance and integrity checks on anything
   written to persistent memory / the vector store; ability to attribute a
   memory record to its source and time. *(Reproduce the attack in
   `agentic-rag-security-lab`.)*
3. **Tool Integration — Action Chains:** a complete tool graph; every tool
   invocation bounded (allowlist + argument policy), logged, and reversible.
4. **Trust Boundary — Multi-Agent:** a formally specified inter-agent trust
   model; inter-agent messages treated as untrusted by default.
5. **Identity Fluidity:** every action attributable to an authorised human
   principal. *(See the structured trail in `llm-audit-logger`.)*
6. **Governance Gap:** evidence that human oversight is *operationally feasible*
   at the agent's speed and volume — not merely nominal.

## Sources

- OWASP Top 10 for LLM Applications (2025) — https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/
- NIST AI Risk Management Framework (AI RMF 1.0) and the Generative AI Profile (NIST AI 600-1) — https://www.nist.gov/itl/ai-risk-management-framework
- MITRE ATLAS — https://atlas.mitre.org/
- EU Artificial Intelligence Act (Regulation 2024/1689), Articles 9–15
- OSFI Guideline E-23, *Model Risk Management* (effective May 2027)
