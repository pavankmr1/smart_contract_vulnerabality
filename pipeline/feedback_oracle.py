import os
import re
import json
from openai import OpenAI

class FeedbackGroundingOracle:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = "gpt-4o-mini"

    def mock_rag_retrieve(self, vulnerability_type: str) -> str:
        """
        Simulates your FAISS vector store query. In production, this pulls 
        real expert audit documents matching the discovered threat class.
        """
        knowledge_base = {
            "Reentrancy": "Security Bound: State changes (balances[msg.sender] = 0) MUST occur before external low-level transfer calls. If call{value: amt}(\"\") is executed while state variables remain un-mutated, an adversarial fallback receive() loop can execute recursive entries, completely liquidating contract funds.",
            "Access Control": "Security Bound: Critical administrative operations mutating ownership state or executing balance withdrawals must enforce strict permission modifiers such as onlyOwner or check conditions using internal role configurations.",
            "Integer Overflow": "Security Bound: In Solidity versions pre-0.8.0, arithmetic operations wrap silently. Mathematical modifications must utilize SafeMath assertions or explicit check conditions to prevent state boundary manipulation."
        }
        return knowledge_base.get(vulnerability_type, "General contract safety constraints.")

    def execute_post_detection_grounding(self, source_code: str, initial_finding: dict) -> dict:
        """
        Your Proposed Loop: Takes an initial bug detection, pulls specialized RAG context, 
        and executes a secondary confirmation alignment check.
        """
        v_type = initial_finding.get("type")
        v_line = initial_finding.get("line")
        v_rationale = initial_finding.get("rationale")

        # 1. Fetch targeted domain knowledge based on the initial finding
        retrieved_context = self.mock_rag_retrieve(v_type)

        # 2. Construct the strict alignment challenge prompt
        confirmation_prompt = f"""
        You are a skeptical smart contract verification oracle. An initial security scanner has flagged a potential vulnerability in this code.
        
        ### Target Smart Contract Source Code
        ```solidity
        {source_code}
        ```
        
        ### Proposed Vulnerability Flag
        - Discovered Type: {v_type}
        - Estimated Location: Line {v_line}
        - Scanner Rationale: {v_rationale}
        
        ### Expert Security Reference Context (Retrieved via RAG)
        {retrieved_context}
        
        Evaluate whether the proposed vulnerability is a true exploit path or an invalid false alarm.
        Respond strictly in this JSON format:
        {{
            "is_verified": true/false,
            "alignment_justification": "Detailed analysis showing if the code aligns with or breaks the RAG security bounds."
        }}
        """

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": confirmation_prompt}],
            temperature=0.0
        )

        try:
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            return json.loads(content)
        except Exception:
            return {"is_verified": False, "alignment_justification": "Failed to parse oracle validation output."}

if __name__ == "__main__":
    # Test sample reentrancy snippet
    contract_sample = """
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
    initial_bug = {
        "type": "Reentrancy",
        "line": 7,
        "rationale": "The contract calls msg.sender before setting balance to zero."
    }
    
    oracle = FeedbackGroundingOracle()
    verification = oracle.execute_post_detection_grounding(contract_sample, initial_bug)
    print(json.dumps(verification, indent=4))