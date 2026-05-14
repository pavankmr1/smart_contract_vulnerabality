import os

from openai import OpenAI

from pipeline.load_env import load_env

load_env()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "YOUR_API_KEY"))


# def detect_candidate(code: str,task):
#     prompt = f"""
# You are a smart contract vulnerability detector.

# Analyze the Solidity contract.

# Identify:
# 1. Whether vulnerabilities MAY exist
# 2. Which vulnerability type is MOST likely

# Possible types:
# - reentrancy
# - overflow
# - access control
# - timestamp dependency
# - unchecked external call
# - safe

# Be conservative.

# Respond EXACTLY:

# CANDIDATE: <type>
# CONFIDENCE: <low/medium/high>

# Contract:
# {code}
# """
def detect_candidate(code, task):
    prompt = f"""
You are a smart contract security detector.

Focus ONLY on:
{task}

Detect whether this vulnerability exists.

Respond EXACTLY:

CANDIDATE: yes
OR
CANDIDATE: no

Contract:
{code}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        output = (response.choices[0].message.content or "").lower()

        vuln = "safe"
        for v in [
            "reentrancy",
            "overflow",
            "access control",
            "timestamp",
            "unchecked",
        ]:
            if v in output:
                vuln = v
                break

        return vuln, output

    except Exception as e:
        print("Detector Error:", e)
        return "safe", ""
