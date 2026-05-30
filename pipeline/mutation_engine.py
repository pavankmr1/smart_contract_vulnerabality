import os
import re
import json

class SmartContractMutator:
    def __init__(self):
        pass

    def inject_reentrancy_mutation(self, secure_code: str) -> str:
        """
        Locates the secure Checks-Effects-Interactions order and purposefully
        inverts it to inject an artificial reentrancy mutant flaw.
        """
        # Checks if code has a secure balance reset AFTER a transfer call
        if "balances[msg.sender] = 0;" in secure_code and ".call{value:" in secure_code:
            # Simple mock demonstration pattern swap
            mutated = secure_code.replace(
                "balances[msg.sender] = 0;\n            (bool success, ) = msg.sender.call{value: bal}(\"\");",
                "(bool success, ) = msg.sender.call{value: bal}(\"\");\n            balances[msg.sender] = 0;"
            )
            return mutated
        
        # Generic fallback mutation if exact block matches are absent
        return secure_code + "\n/* MUTANT_INJECTION: REENTRANCY_INVERTED_STATE_ORDER */"

    def generate_mutant_suite(self, secure_code: str) -> dict:
        """Generates a comprehensive suite of security mutants for evaluation."""
        return {
            "original_safe_code": secure_code,
            "reentrancy_mutant": self.inject_reentrancy_mutation(secure_code)
        }

if __name__ == "__main__":
    secure_sample = """
    contract SecureBank {
        mapping(address => uint256) public balances;
        function withdraw() public {
            uint256 bal = balances[msg.sender];
            require(bal > 0);
            balances[msg.sender] = 0;
            (bool success, ) = msg.sender.call{value: bal}("");
            require(success);
        }
    }
    """
    mutator = SmartContractMutator()
    mutated_suite = mutator.generate_mutant_suite(secure_sample)
    print("--- INJECTED MUTANT SOURCE CODE ---")
    print(mutated_suite["reentrancy_mutant"])