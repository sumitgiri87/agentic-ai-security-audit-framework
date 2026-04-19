# agentic-ai-security-audit-framework

![Status](https://img.shields.io/badge/status-active--development-orange)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)
![Framework](https://img.shields.io/badge/scope-agentic--AI--systems-red)
![Regulatory](https://img.shields.io/badge/regulatory-OSFI%20E--23%20%7C%20EU%20AI%20Act-darkgreen)

> A structured methodology for auditing enterprise agentic AI deployments against adversarial attack vectors and regulatory compliance requirements. Built from real red team research. Not a vendor product.

---

## Table of Contents

1. [Why This Exists](#1-why-this-exists)
2. [The Six Attack Dimensions Existing Frameworks Miss](#2-the-six-attack-dimensions-existing-frameworks-miss)
3. [Why Existing Frameworks Are Insufficient](#3-why-existing-frameworks-are-insufficient)
4. [Regulatory Context for Canadian Enterprises](#4-regulatory-context-for-canadian-enterprises)
5. [What This Framework Contains](#5-what-this-framework-contains)
6. [Repository Structure](#6-repository-structure)
7. [Current Status](#7-current-status)
8. [Who This Is For](#8-who-this-is-for)
9. [References](#9-references)

---

## 1. Why This Exists

In 2025, researchers at Columbia University achieved a **10/10 success rate** extracting credit card numbers from Anthropic's commercial Computer Use agent. The attack vector was a Reddit post. No machine learning knowledge was required. The same research demonstrated agents sending phishing emails from users' own Gmail accounts, executing malware, and redirecting a scientific research agent to produce nerve gas synthesis routes.

Anthropic is one of the most safety-focused AI companies in the world. This is not a criticism of their engineering. It is evidence of a structural problem: **agentic AI systems introduce attack surfaces that did not exist in isolated LLMs, and the security industry has not caught up.**

The fundamental issue is that an AI agent is not just a language model. It is a language model that:

- Holds persistent memory across sessions
- Calls external tools and APIs with real-world consequences
- Browses the web and reads arbitrary external content
- Sends emails, executes code, and writes to databases
- Coordinates with other agents, trusting their outputs by default
- Operates at a speed and autonomy that outpaces human oversight

When a system can read a Reddit post and then exfiltrate your credit card data, the threat model is not a chatbot threat model. The security evaluation methodology has to change accordingly.

This repository is the beginning of that methodology.

---

## 2. The Six Attack Dimensions Existing Frameworks Miss

Current security frameworks were designed for isolated LLMs or traditional software. They handle some of these dimensions partially. None handle all six together — and in agentic systems, the combination is what creates the most severe vulnerabilities.

### 2.1 Cognitive — Prompt Injection

The agent's reasoning process can be directly manipulated by adversarial content embedded in the environment the agent reads. Unlike SQL injection, the attack surface is anything the agent perceives: web pages, documents, emails, database records, tool outputs. The agent does not distinguish between instructions from its operator and instructions embedded in external content unless explicitly designed to do so — and most production deployments are not.

**Why this is different in agentic systems:** In a single-turn LLM, a prompt injection has limited blast radius. In an agent with tool access, a successful injection can trigger a chain of real-world actions before any human sees the output.

### 2.2 Temporal — Memory Attacks

Agents with persistent memory (vector stores, episodic memory, session state) can be poisoned at time T and exploited at time T+N. An attacker plants a malicious instruction in a document the agent reads today. Six weeks later, that instruction surfaces when the agent encounters a specific trigger. The attack and the exploitation are temporally decoupled, which defeats most real-time monitoring approaches.

**Why this is different in agentic systems:** Traditional application security has no equivalent. There is no existing audit methodology for evaluating whether an agent's memory has been compromised.

### 2.3 Tool Integration — Real-World Action Chains

A compromised agent does not just produce bad text. It takes actions: it sends the email, executes the query, calls the API, modifies the file. The security boundary is not the model — it is every system the model can reach. Evaluating this requires mapping the complete tool graph of the deployment and assessing whether each tool invocation is bounded, logged, and reversible.

**Why this is different in agentic systems:** Penetration testing methodology exists for APIs and systems. It does not exist for the autonomous AI orchestration layer that calls those APIs.

### 2.4 Trust Boundary — Multi-Agent Systems

In multi-agent architectures (LangGraph, CrewAI, AutoGen), agents communicate with each other. By default, most frameworks treat inter-agent messages as trusted inputs. A compromised subagent can instruct an orchestrator agent. A malicious external agent injected into a workflow can issue commands that propagate through the entire system. The trust model that regulates what one agent can instruct another to do is almost never formally specified in production deployments.

**Why this is different in agentic systems:** This attack surface does not exist in single-model deployments. It is entirely new and entirely unaddressed by existing frameworks.

### 2.5 Identity Fluidity

The line between agent identity and user identity is structurally blurred in most agentic frameworks. Agents act on behalf of users, impersonate system roles, and delegate authority to subagents. The question of which entity is responsible for a given action — and whether that action was authorised by the human principal — is often unanswerable after the fact without deliberate audit logging design.

**Why this is different in agentic systems:** In regulated industries, the ability to attribute actions to authorised human principals is a compliance requirement. Agentic systems break this by design unless attribution is explicitly built in.

### 2.6 Governance Gap

An agent that operates autonomously, at machine speed, across multiple systems, produces more decisions per hour than any human oversight process can review. The governance gap is not a failure of intent — it is a structural property of the architecture. Evaluating whether adequate human oversight exists requires assessing not just whether a human is nominally in the loop, but whether the human oversight mechanism is operationally feasible at the speed and scale the agent operates.

**Why this is different in agentic systems:** The EU AI Act's requirements for human oversight of high-risk AI systems were written with this problem in mind. Most enterprises deploying agents have not operationalised what human oversight means in practice.

---

## 3. Why Existing Frameworks Are Insufficient

This is not a criticism of the teams that built these frameworks. They were built for different problems. The issue is category mismatch, not quality.

### OWASP LLM Top 10

The OWASP LLM Top 10 is the most practically useful existing resource. It correctly identifies prompt injection, insecure output handling, and supply chain risks. Its limitations in the agentic context:

- It addresses individual LLM vulnerabilities, not multi-agent system architectures
- It does not address temporal attack vectors (memory poisoning)
- It has no methodology for assessing inter-agent trust boundaries
- It does not map to regulatory compliance frameworks
- It provides a vulnerability taxonomy, not an audit methodology

**What it gives you:** A useful starting checklist for individual agent components. **What it does not give you:** A structured engagement methodology for assessing an enterprise agentic deployment end-to-end.

### NIST AI RMF

The NIST AI RMF is a governance framework, not a security testing methodology. Its four functions (Govern, Map, Measure, Manage) are conceptually sound and provide a useful organisational structure for AI risk programs. Its limitations:

- It is framework-agnostic by design, which means it provides no specific testing procedures
- It does not address adversarial testing of agentic systems specifically
- Its measurement function does not define what constitutes adequate evidence for regulated industries
- Canadian regulatory bodies (OSFI) reference NIST but do not treat it as sufficient for model risk management obligations

**What it gives you:** Organisational vocabulary and a governance structure. **What it does not give you:** A way to test whether an agent can be exploited.

### MITRE ATLAS

MITRE ATLAS is the most technically sophisticated of the three. Its adversarial ML taxonomy is rigorous and the case studies are well-documented. Its limitations in the agentic context:

- It was designed for ML models in the traditional sense: training data attacks, model evasion, model inversion
- It does not address prompt injection as a primary attack class (it is listed but not developed)
- Multi-agent trust boundary attacks are not represented
- Memory poisoning attacks are not addressed
- It does not map to the operational reality of enterprise LangChain/LangGraph deployments

**What it gives you:** A rigorous taxonomy for ML-specific attacks on model components. **What it does not give you:** Coverage of the attack surface introduced by agentic orchestration.

### The Combined Gap

None of these three frameworks, individually or combined, provides:

1. A structured methodology for testing prompt injection resilience across an agent's full tool-accessible environment
2. A procedure for assessing memory integrity in vector-store-backed persistent memory systems
3. A framework for mapping and assessing inter-agent trust boundaries
4. Audit evidence templates acceptable to regulated-industry compliance functions
5. Mapping to OSFI E-23, EU AI Act Articles 9-15, HIPAA technical safeguards, or PHIPA requirements

This repository addresses that gap.

---

## 4. Regulatory Context for Canadian Enterprises

Two regulatory instruments create mandatory compliance spend for Canadian enterprises deploying agentic AI. This is not discretionary.

### OSFI Guideline E-23 — Model Risk Management

The Office of the Superintendent of Financial Institutions revised Guideline E-23 to explicitly include AI/ML models within the scope of model risk management obligations. For Canadian federally regulated financial institutions (FRFIs) — the Big Five banks, major insurers, federally regulated pension funds — the compliance deadline is **May 2027**.

E-23 requires FRFIs to maintain:

- Model inventory covering all models in production use
- Independent validation of model performance and risk
- Documentation of model limitations and failure modes
- Ongoing monitoring and governance

Agentic AI deployments meet the definition of "model" under E-23. The independent validation requirement creates structural demand for third-party audit. A bank cannot satisfy independent validation using the same vendor that built the agent system.

### EU AI Act — Articles 9-15

The EU AI Act entered force August 2024. High-risk AI system obligations under Articles 9-15 phase in through 2025-2026. For Canadian enterprises with EU operations, EU-facing products, or EU data subjects, these obligations apply extraterritorially.

Articles 9-15 require high-risk AI systems to have:

- Risk management systems (Article 9)
- Data governance procedures (Article 10)
- Technical documentation (Article 11)
- Record-keeping and logging (Article 12)
- Transparency and human oversight mechanisms (Articles 13-14)
- Accuracy, robustness, and cybersecurity (Article 15)

Article 15 explicitly requires that high-risk AI systems be resilient to adversarial manipulation. This is the first regulatory instrument to create a mandatory cybersecurity testing requirement specifically for AI systems.

### What This Means in Practice

A Canadian bank deploying an agentic AI system for loan decisioning, fraud detection, or customer interaction faces:

- OSFI E-23 independent validation requirements
- EU AI Act high-risk system obligations (if any EU nexus exists)
- Potentially PHIPA (if health data is involved in any workflow)

None of these obligations can be satisfied by an automated compliance checklist tool. They require documented methodology, qualified independent assessors, and audit evidence acceptable to regulators. This framework is designed to produce that evidence.

---

## 5. What This Framework Contains

This repository is structured as a complete audit engagement methodology. It is being built incrementally — see [Current Status](#7-current-status) for what is available now.

### 5.1 Audit Methodology (`/methodology`)

A phase-structured audit procedure covering:

- **Pre-engagement scoping** — agent inventory, tool graph mapping, data flow documentation
- **Threat modelling** — attack surface enumeration specific to the deployment architecture
- **Technical testing** — structured test procedures for each of the six attack dimensions
- **Evidence collection** — what to capture, how to capture it, chain of custody procedures
- **Risk rating** — severity classification adapted for agentic system findings
- **Reporting** — findings documentation and remediation roadmap structure

### 5.2 Test Harness (`/test-harness`)

Executable test cases for each attack dimension:

- Prompt injection payload library (20+ payloads categorised by injection vector)
- Memory poisoning test scenarios for vector-store-backed agents
- Tool invocation boundary tests
- Multi-agent trust boundary probes
- Identity attribution stress tests
- Human oversight latency measurements

### 5.3 Compliance Mapper (`/compliance-mapper`)

A CLI tool and mapping document that translates audit findings to specific regulatory obligations:

- OSFI E-23 section mapping
- EU AI Act Articles 9-15 mapping
- HIPAA technical safeguard mapping
- NIST AI RMF cross-reference

Given a LangChain agent configuration, the compliance mapper outputs a gap analysis against applicable regulatory requirements.

### 5.4 Evidence Templates (`/evidence-templates`)

Structured templates for producing audit evidence acceptable to regulated-industry compliance functions:

- Agent inventory documentation template
- Tool access control matrix template
- Test execution log format
- Finding report template (structured for CISO and legal review)
- Attestation letter template

---

## 6. Repository Structure

The repository is being built in sequence — methodology before tooling, tooling before templates. The build order follows the engagement workflow.

**Current:** README and methodology foundation.  
**In progress:** Prompt injection test harness and OSFI E-23 compliance mapper.  
**Planned:** Memory poisoning tests, multi-agent trust boundary tests, evidence templates.

See [Current Status](#7-current-status) below for specifics.

---

## 7. Current Status

This repository is under active development. The build sequence follows the engagement methodology — scoping and threat modelling before testing, testing before compliance mapping.

| Component | Status |
|---|---|
| Audit methodology (cognitive + tool dimensions) | 🔄 In progress |
| Prompt injection test harness | 🔄 In progress |
| OSFI E-23 compliance mapper | 📅 Planned |
| EU AI Act Articles 9-15 mapper | 📅 Planned |
| Memory poisoning test cases | 📅 Planned |
| Multi-agent trust boundary tests | 📅 Planned |
| Evidence templates | 📅 Planned |

Updates are pushed as components are validated against real test environments. Nothing is published before it works.

---

## 8. Who This Is For

**CISOs and security architects at regulated enterprises** deploying agentic AI systems who need to answer the question: *is this deployment secure, and can I demonstrate that to a regulator?* This framework gives you a structured way to find out and document the answer.

**Compliance officers at Canadian FRFIs and Ontario health systems** working on OSFI E-23 model risk management programs or EU AI Act high-risk system documentation. The compliance mapper translates technical audit findings into the regulatory language your documentation requires.

**Internal red teams and security engineers** who have been asked to assess an agentic AI deployment and are finding that their existing penetration testing methodology does not map cleanly to the problem. The test harness is designed to be runnable against live deployments with minimal setup.

**Independent security researchers** building in this space. Everything here is open. If the methodology is wrong, open an issue. If you have attack research that belongs in the test harness, open a pull request.

**This framework is not for:** general LLM security (use OWASP LLM Top 10 as your starting point), traditional penetration testing engagements, or organisations that have not yet deployed agentic systems. The scope is deliberately narrow — autonomous agents with persistent memory, tool access, and multi-agent coordination. That specificity is the point.

---

## 9. References

- Liao, Q. et al. (2025). *Attacking Agentic AI: Empirical Findings from Red Teaming Commercial Computer Use Agents.* Columbia University. — The 10/10 credit card extraction result. Primary empirical basis for the cognitive attack dimension.
- OSFI Guideline E-23 — *Model Risk Management* (revised, effective May 2027). Office of the Superintendent of Financial Institutions, Canada.
- EU Artificial Intelligence Act (Regulation 2024/1689) — Articles 9-15. European Parliament, August 2024.
- OWASP Top 10 for Large Language Model Applications (v1.1, 2023).
- NIST AI Risk Management Framework (AI RMF 1.0, January 2023).
- MITRE ATLAS — Adversarial Threat Landscape for Artificial-Intelligence Systems. MITRE Corporation.
- NIST SP 800-53 Rev 5 — Security and Privacy Controls for Information Systems.
- CSA MAESTRO — Multi-Agent Environment Security and Trust Risk Overview (2024).

---

## Author

**Sumit Giri**  
Security Engineer · AI Red Teamer · PhD Mathematics (Cryptography)  
Toronto, Ontario, Canada

AI red teaming at Mindrift. Cybersecurity consulting at CyStack. Building an independent AI agent security audit practice for Canadian regulated enterprises.

[LinkedIn](https://www.linkedin.com/in/sumit-giri-0111/) · [GitHub](https://github.com/sumitgiri87)

---

*This is independent research. No vendor relationship. No affiliation with any of the frameworks or organisations referenced. Findings and methodology represent the author's own work.*

