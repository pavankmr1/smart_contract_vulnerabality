import os
import re

from openai import OpenAI

from pipeline.load_env import load_env

load_env()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "YOUR_API_KEY"))


def verify_vulnerability(code: str, vuln_type: str, rag_context: str):
    prompt = f"""
You are an expert Ethereum smart contract security auditor.

A previous detector suspects:
{vuln_type}

Relevant security knowledge:
{rag_context}

Your task:

1. Analyze exploitability carefully
2. Determine whether the vulnerability is REAL
3. Ignore outdated syntax unless exploitable
4. Reduce false positives

Respond EXACTLY:

ANALYSIS:
<brief reasoning>

FINAL VERDICT:
VULNERABLE

OR

FINAL VERDICT:
SAFE

Contract:
{code}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-5.4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        output = (response.choices[0].message.content or "").lower()

        if re.search(r"final verdict:\s*vulnerable", output):
            return 1, output
        if re.search(r"final verdict:\s*safe", output):
            return 0, output
        if "vulnerable" in output and "not vulnerable" not in output:
            return 1, output
        return 0, output

    except Exception as e:
        print("Verifier Error:", e)
        return -1, ""
