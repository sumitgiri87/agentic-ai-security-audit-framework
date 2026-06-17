# Audit Methodology

The phase-structured procedure for auditing an enterprise agentic AI deployment
against the [six attack dimensions](../README.md#2-the-six-attack-dimensions-existing-frameworks-miss).
It follows the engagement workflow: scope, then threat-model, then test, then
map findings to controls and regulation.

## Phases

1. **Pre-engagement scoping** — agent inventory, tool-graph mapping, data-flow
   documentation. Output: the set of dimensions in scope.
2. **Threat modelling** — enumerate the attack surface specific to the
   deployment architecture, per dimension.
3. **Technical testing** — run the structured tests for each dimension in scope.
   Reusable harnesses live in [`../test-harness`](../test-harness); reproduce the
   cognitive/temporal attacks against the companion
   [`agentic-rag-security-lab`](https://github.com/sumitgiri87/agentic-rag-security-lab).
4. **Evidence collection** — capture per the evidence column of the
   [control mapping](control-mapping.md); a structured, tamper-evident trail can
   be produced with
   [`llm-audit-logger`](https://github.com/sumitgiri87/llm-audit-logger).
5. **Control & regulatory mapping** — translate each finding to framework
   controls and regulatory articles using
   [`control-mapping.md`](control-mapping.md) /
   [`control-mapping.csv`](control-mapping.csv).
6. **Risk rating & reporting** — severity classification adapted for agentic
   findings; remediation roadmap.

## Artifacts in this directory

| File | Purpose |
|------|---------|
| [`control-mapping.md`](control-mapping.md) | Six dimensions → OWASP / NIST / ATLAS / EU AI Act / OSFI E-23, plus per-dimension audit evidence |
| [`control-mapping.csv`](control-mapping.csv) | Machine-readable mapping for tooling / gap-analysis import |

**Status:** the control mapping (phase 5) is available now. Phase-by-phase test
procedures and evidence templates are being added in the build order described
in the [root README](../README.md#7-current-status).
