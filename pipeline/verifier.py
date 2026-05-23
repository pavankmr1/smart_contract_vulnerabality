from openai import OpenAI
import os
from pipeline.load_env import load_env

load_env()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "YOUR_API_KEY"))


def verify_candidate(code, vuln_type, rag_context):

    prompt = f"""
You are an expert Ethereum smart contract auditor.

Potential vulnerability:
{vuln_type}

Security knowledge:
{rag_context}

Your task:
1. Determine if this vulnerability is REAL
2. Check exploitability carefully
3. Ignore superficial patterns
4. Reduce false positives

Respond EXACTLY:

VERDICT: VULNERABLE

OR

VERDICT: SAFE

REASON:
<short explanation>

Contract:
{code}
"""

    try:

        response = client.chat.completions.create(
            model="gpt-5.4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        output = response.choices[0].message.content.lower()

        if "vulnerable" in output:
            return 1, output

        return 0, output

    except Exception as e:
        print("Verifier Error:", e)
        return -1, ""