from openai import OpenAI

import os
from pipeline.load_env import load_env

load_env()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "YOUR_API_KEY"))


VULNS = [
    "reentrancy",
    "overflow",
    "access control",
    "unchecked external call",
    "timestamp dependency"
]

def detect_candidates(code):

    prompt = f"""
You are a smart contract vulnerability discovery engine.

Analyze the Solidity contract carefully.

Identify ALL plausible vulnerabilities.

Possible vulnerabilities:
- reentrancy
- overflow
- access control
- unchecked external call
- timestamp dependency

Return ONLY a comma-separated list.

Examples:
reentrancy, unchecked external call

OR

safe

Contract:
{code}
"""

    try:

        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        output = response.choices[0].message.content.lower()

        candidates = []

        for vuln in VULNS:
            if vuln in output:
                candidates.append(vuln)

        if len(candidates) == 0:
            candidates = ["safe"]

        return candidates, output

    except Exception as e:
        print("Detector Error:", e)
        return ["safe"], ""