import os
import re
import json
from openai import OpenAI

from pipeline.load_env import load_env

load_env()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "YOUR_API_KEY"))


def extract_structural_features(source_code: str) -> dict:
    """
    Simulates AST structural view extraction by identifying modifiers,
    state variable declarations, and inheritance boundaries.
    """
    features = {
        "contract_names": re.findall(r"contract\s+(\w+)", source_code),
        "modifiers": re.findall(r"modifier\s+(\w+)", source_code),
        "external_calls": re.findall(r"\.\s*call\s*\(", source_code),
        "state_variables": re.findall(r"(uint256|address|mapping)\s+(?:public|private|internal)?\s*(\w+);", source_code)
    }
    return features

def generation_stage(source_code: str, structural_view: dict) -> list:
    """
    Stage 1: Generates candidate vulnerability hypotheses using an explicit Dual-View context.
    """
    prompt = f"""
    You are an expert blockchain security auditor. Analyze the following smart contract using both its structural layout and sequential code view.
    
    ### Structural Representation
    - Contract Scope: {structural_view['contract_names']}
    - Found Modifiers: {structural_view['modifiers']}
    - State Layout: {structural_view['state_variables']}
    - Low-Level Target Interactions: {len(structural_view['external_calls'])} external calls identified.
    
    ### Source Code Sequence
    ```solidity
    {source_code}
    ```
    
    Identify all potential security vulnerabilities (e.g., Reentrancy, Access Control, Integer Overflow).
    Return your findings STRICTLY as a JSON array of objects, where each object has 'type', 'line', and 'rationale'.
    Do not add extra text formatting outside the raw JSON array.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini", # Replace with your required version or fallback model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    
    try:
        content = response.choices[0].message.content.strip()
        # Clean JSON markdown wrapper if present
        if content.startswith("```json"):
            content = content[7:-3].strip()
        return json.loads(content)
    except Exception:
        return []

def adversarial_verification_stage(source_code: str, candidates: list) -> list:
    """
    Stage 2: Actively attempts to disprove each candidate vulnerability hypothesis.
    """
    verified_vulnerabilities = []
    
    for vulnerability in candidates:
        verification_prompt = f"""
        You are a skeptical adversarial security oracle. Your single task is to closely review a proposed vulnerability flag and determine if it is a FALSE POSITIVE.
        
        ### Target Smart Contract
        ```solidity
        {source_code}
        ```
        
        ### Proposed Vulnerability Hypotheses
        - Target Type: {vulnerability.get('type')}
        - Code Marker Location: Line {vulnerability.get('line')}
        - Proposed Reason: {vulnerability.get('rationale')}
        
        Analyze the state-transitions and function guards. Can an execution modifier, state lock (like reentrancyGuard), or validation check prevent this exploit?
        Respond strictly in this structured JSON format:
        {{
            "is_false_positive": true/false,
            "verification_justification": "Your detailed tracking analysis text here."
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": verification_prompt}],
            temperature=0.0
        )
        
        try:
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            verification_result = json.loads(content)
            
            if not verification_result.get("is_false_positive", True):
                vulnerability["verification_proof"] = verification_result.get("verification_justification")
                verified_vulnerabilities.append(vulnerability)
        except Exception:
            # If parsing fails, default to safety to ensure higher precision
            continue
            
    return verified_vulnerabilities

def run_pipeline(source_code: str) -> dict:
    """
    Coordinates the complete multi-candidate verification architecture.
    """
    # 1. Structural View Component
    struct_view = extract_structural_features(source_code)
    
    # 2. Dual-View Generator Stage
    initial_candidates = generation_stage(source_code, struct_view)
    
    # 3. Adversarial Validation Stage
    final_findings = adversarial_verification_stage(source_code, initial_candidates)
    
    return {
        "status": "VULNERABLE" if len(final_findings) > 0 else "SAFE",
        "vulnerabilities": final_findings
    }

if __name__ == "__main__":
    # Test sample reentrancy snippet
    test_contract = """
    contract VulnerableBank {
        mapping(address => uint256) public balances;
        function withdraw() public {
            uint256 bal = balances[msg.sender];
            require(bal > 0);
            (bool success, ) = msg.sender.call{value: bal}("");
            require(success);
            balances[msg.sender] = 0;
        }
    }
    """
    results = run_pipeline(test_contract)
    print(json.dumps(results, indent=4))