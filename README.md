# Evaluating and Enhancing LLM-Assisted Smart Contract Vulnerability Detection

An engineered, multi-stage hybrid framework that combines **Dual-View Semantic Parsing** along with an **Adversarial Verification Oracle** loop to maximize vulnerability detection recall while systematically crushing false-positive rates.

## Architectural Design Overview
The pipeline breaks away from simple one-pass prompt models by implementing a structured verification state machine:
1. **Structural Feature Extractor:** Evaluates Abstract Syntax Tree (AST) patterns, tracking modifiers, external function interfaces, and state-mutation profiles.
2. **Dual-View Candidate Generator:** Integrates the code layout sequence and structural parameters into a unified prompt matrix to surface candidate vulnerabilities.
3. **Adversarial Verification Oracle:** Executes a localized counter-evaluation loop to attempt to logically falsify every flagged error target, verifying that an exploitable execution path genuinely exists.

## Installation & Setup
Ensure dependencies are verified within your active terminal environment:
```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-high-fidelity-api-key"