import os
import pandas as pd

from tqdm import tqdm
from sklearn.metrics import classification_report

from pipeline.detector import detect_candidates
from pipeline.verifier import verify_candidate
from pipeline.rag import retrieve_knowledge
from pipeline.slither_tool import analyze_slither


# =========================================
# READ CONTRACT
# =========================================
def read_contract(path):

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# =========================================
# MAIN EXPERIMENT RUNNER
# =========================================
def run_experiment(name, datasets):

    print(f"\n=== {name} ===")

    results = []

    # -------------------------------------
    # BUILD WORK ITEMS
    # -------------------------------------
    work_items = []

    for folder, label in datasets.items():

        base = f"datasets/{folder}"

        if not os.path.isdir(base):
            print(f"Dataset folder not found: {base}")
            continue

        for file in os.listdir(base):

            if file.endswith(".sol"):

                work_items.append(
                    (folder, label, base, file)
                )

    if len(work_items) == 0:
        print("No .sol files found.")
        return

    # -------------------------------------
    # PROCESS CONTRACTS
    # -------------------------------------
    for folder, label, base, file in tqdm(
        work_items,
        desc=f"Analyzing ({name})"
    ):

        try:

            path = os.path.join(base, file)

            code = read_contract(path)

            # =====================================
            # MULTI-CANDIDATE DETECTION
            # =====================================
            candidates, detector_output = detect_candidates(code)

            verified_results = []

            verifier_logs = []

            # =====================================
            # VERIFY EACH CANDIDATE
            # =====================================
            for vuln in candidates:

                if vuln == "safe":
                    continue

                try:

                    rag_context = retrieve_knowledge(vuln)

                    verdict, verifier_output = verify_candidate(
                        code,
                        vuln,
                        rag_context
                    )

                    verified_results.append(verdict)

                    verifier_logs.append({
                        "candidate": vuln,
                        "verdict": verdict,
                        "reasoning": verifier_output
                    })

                except Exception as e:
                    print(f"Verifier Error ({file}):", e)

            # =====================================
            # FINAL LLM DECISION
            # =====================================
            if any(v == 1 for v in verified_results):
                llm_result = 1
            else:
                llm_result = 0

            # =====================================
            # SLITHER
            # =====================================
            try:
                slither_result = analyze_slither(path)
            except Exception as e:
                print(f"Slither Error ({file}):", e)
                slither_result = -1

            # =====================================
            # STORE RESULTS
            # =====================================
            results.append({
                "contract": file,
                "dataset": folder,
                "actual": label,
                "candidates": ", ".join(candidates),
                "llm": llm_result,
                "slither": slither_result
            })

            print(
                f"{file} | "
                f"Candidates: {candidates} | "
                f"LLM: {llm_result}"
            )

        except Exception as e:

            print(f"Processing Error ({file}):", e)

    # =========================================
    # SAVE RESULTS
    # =========================================
    df = pd.DataFrame(results)

    os.makedirs("results", exist_ok=True)

    csv_path = f"results/{name}.csv"

    df.to_csv(csv_path, index=False)

    print(f"\n✅ Results saved: {csv_path}")

    # =========================================
    # LLM REPORT
    # =========================================
    print("\nLLM:")

    print(
        classification_report(
            df["actual"],
            df["llm"],
            zero_division=0
        )
    )

    # =========================================
    # SLITHER REPORT
    # =========================================
    print("\nSLITHER:")

    valid_df = df[df["slither"] != -1]

    if len(valid_df) > 0:

        print(
            classification_report(
                valid_df["actual"],
                valid_df["slither"],
                zero_division=0
            )
        )

    else:
        print("No valid Slither results.")

    # =========================================
    # SUMMARY
    # =========================================
    print("\n📊 SUMMARY")

    print(df.head())

    print("\nTotal Contracts:", len(df))

    print(
        "\nLLM Vulnerable Predictions:",
        (df["llm"] == 1).sum()
    )

    print(
        "LLM Safe Predictions:",
        (df["llm"] == 0).sum()
    )

    print(
        "\nSlither Vulnerable Predictions:",
        (df["slither"] == 1).sum()
    )

    print(
        "Slither Safe Predictions:",
        (df["slither"] == 0).sum()
    )