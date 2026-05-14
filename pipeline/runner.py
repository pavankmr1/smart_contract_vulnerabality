import os

import pandas as pd
from sklearn.metrics import classification_report

from pipeline.detector import detect_candidate
from pipeline.rag import retrieve_knowledge
from pipeline.slither_tool import analyze_slither
from pipeline.verifier import verify_vulnerability

try:
    from tqdm.auto import tqdm
except Exception:  # pragma: no cover
    tqdm = None


def read_contract(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def run_experiment(name, dataset_map):
    print(f"\n=== {name} ===")

    results = []

    work_items = []
    for folder, label in dataset_map.items():
        base = f"datasets/{folder}"
        if not os.path.isdir(base):
            print(f"Skip missing folder: {base}")
            continue
        for file in os.listdir(base):
            if file.endswith(".sol"):
                work_items.append((folder, label, base, file))
    # work_items = work_items[:10]+work_items[-10:]
    iterator = work_items
    pbar = None
    if tqdm is not None and work_items:
        pbar = tqdm(work_items, desc=f"Analyzing ({name})", unit="contract")
        iterator = pbar

    for folder, label, base, file in iterator:
        path = os.path.join(base, file)
        code = read_contract(path)

        # vuln_type, detector_output = detect_candidate(code)
        task = name.replace("_eval", "")
        candidate, detector_output = detect_candidate(code, task)
        # rag_context = retrieve_knowledge(vuln_type)
        rag_context = retrieve_knowledge(task)
        llm_result, verifier_output = verify_vulnerability(
            code,
            # vuln_type,
            candidate,
            rag_context,
        )

        slither_result = analyze_slither(path)

        results.append(
            {
                "contract": file,
                "actual": label,
                "candidate": candidate,
                "llm": llm_result,
                "slither": slither_result,
            }
        )

        line = f"{file} {candidate} {llm_result}"
        if pbar is not None:
            pbar.set_postfix_str(file[:24] + ("…" if len(file) > 24 else ""), refresh=False)
            tqdm.write(line)
        else:
            print(line)

    df = pd.DataFrame(results)
    os.makedirs("results", exist_ok=True)
    df.to_csv(f"results/{name}.csv", index=False)

    if df.empty:
        print("No contracts processed.")
        return

    print("\nLLM:")
    print(classification_report(df["actual"], df["llm"], zero_division=0))

    print("\nSLITHER:")
    print(classification_report(df["actual"], df["slither"], zero_division=0))
