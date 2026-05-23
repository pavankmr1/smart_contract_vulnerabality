import os
import pandas as pd
from openai import OpenAI
from sklearn.metrics import accuracy_score
from pipeline.load_env import load_env

# ==========================================================
# LOAD ENV
# ==========================================================

load_env()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# ==========================================================
# LOAD SMARTBUGS REENTRANCY DATASET
# ==========================================================

DATASET = "/Users/pavan/Downloads/Final Project/final-project/datasets/smartbugs_curated/dataset/reentrancy"

contracts = []

for file in os.listdir(DATASET):

    if file.endswith(".sol"):

        path = os.path.join(DATASET, file)

        with open(path, "r", encoding="utf-8") as f:

            code = f.read()

        contracts.append({
            "code": code,
            "actual": 1,
            "file": file
        })

# SMALL SAMPLE FOR QUICK ABLATION
contracts = contracts[:10]

# ==========================================================
# OPENAI CALL
# ==========================================================

def ask(prompt):

    try:

        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        out = response.choices[0].message.content.lower()

        if "vulnerable" in out:
            return 1
        else:
            return 0

    except Exception as e:

        print("ERROR:", e)

        return -1

# ==========================================================
# RUN ABLATION
# ==========================================================

results = []

for row in contracts:

    code = row["code"]

    actual = row["actual"]

    # ======================================================
    # ZERO SHOT
    # ======================================================

    zero = ask(f"""
You are a blockchain smart contract auditor.

Determine whether the following Solidity contract is vulnerable.

Respond ONLY:
VULNERABLE
or
SAFE

{code}
""")

    # ======================================================
    # CHAIN OF THOUGHT
    # ======================================================

    cot = ask(f"""
You are an expert blockchain security researcher.

Analyze the Solidity contract step-by-step.

Carefully inspect for:
- reentrancy
- unsafe external calls
- integer overflows
- access control flaws
- dangerous state updates

Reason internally before deciding.

Respond ONLY:
VULNERABLE
or
SAFE

{code}
""")

    # ======================================================
    # FEW SHOT
    # ======================================================

    few = ask(f"""
Example Vulnerable Contract:

contract A {{

mapping(address=>uint) balances;

function withdraw() public {{

msg.sender.call.value(
balances[msg.sender]
)();

balances[msg.sender] = 0;

}}

}}

This contract is VULNERABLE because the external call occurs before the balance update, enabling reentrancy.

Example Safe Contract:

contract B {{

mapping(address=>uint) balances;

function withdraw() public {{

uint amount = balances[msg.sender];

balances[msg.sender] = 0;

msg.sender.transfer(amount);

}}

}}

This contract is SAFE because state is updated before transfer.

Now analyze the following contract.

Respond ONLY:
VULNERABLE
or
SAFE

{code}
""")

    results.append({
        "file": row["file"],
        "actual": actual,
        "zero": zero,
        "cot": cot,
        "few": few
    })

# ==========================================================
# RESULTS
# ==========================================================

rdf = pd.DataFrame(results)

print("\n==============================")
print("PROMPT ABLATION RESULTS")
print("==============================\n")

print("ZERO SHOT :", accuracy_score(rdf.actual, rdf.zero))
print("CHAIN-OF-THOUGHT :", accuracy_score(rdf.actual, rdf.cot))
print("FEW-SHOT :", accuracy_score(rdf.actual, rdf.few))

print("\n==============================")
print("SAMPLE OUTPUT")
print("==============================\n")

print(rdf.head())

# ==========================================================
# SAVE
# ==========================================================

rdf.to_csv(
    "results/prompt_ablation_results.csv",
    index=False
)

print("\nSaved: results/prompt_ablation_results.csv")