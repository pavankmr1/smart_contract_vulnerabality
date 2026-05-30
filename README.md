# Evaluating and Enhancing LLM-Assisted Smart Contract Vulnerability Detection

An engineered, multi-stage hybrid framework that combines **Dual-View Semantic Parsing** along with an **Adversarial Verification Oracle** loop to maximize vulnerability detection recall while systematically crushing false-positive rates.

## Architectural Design Overview
The pipeline breaks away from simple one-pass prompt models by implementing a structured verification state machine:
1. **Structural Feature Extractor:** Evaluates Abstract Syntax Tree (AST) patterns, tracking modifiers, external function interfaces, and state-mutation profiles.
2. **Dual-View Candidate Generator:** Integrates the code layout sequence and structural parameters into a unified prompt matrix to surface candidate vulnerabilities.
3. **Adversarial Verification Oracle:** Executes a localized counter-evaluation loop to attempt to logically falsify every flagged error target, verifying that an exploitable execution path genuinely exists.
## Advanced Extension: Automated Proof-of-Concept Exploit Generation
The pipeline incorporates an automated validation loop that translates verified abstract text vulnerabilities into compilable, sandbox-ready **Foundry Solidity Test Cases**. 

When a structural threat (such as a reentrancy vector violating the checks-effects-interactions pattern) survives the post-detection retrieval sieve, the pipeline passes the exploit mechanics to the synthesis sub-engine. The module automatically crafts an explicit adversarial actor framework containing targeted execution routines (e.g., recursive state-liquidation hooks) to physically demonstrate the exploit path in a development sandbox environment, removing the verification burden from the security analyst.
## Installation & Setup
Ensure dependencies are verified within your active terminal environment:
```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-high-fidelity-api-key"