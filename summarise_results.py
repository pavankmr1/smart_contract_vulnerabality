import pandas as pd
from sklearn.metrics import classification_report

files = {
    "reentrancy": "results/reentrancy_eval.csv",
    "overflow": "results/overflow_eval.csv",
    "access_control": "results/access_control_eval.csv",
    "kaggle": "results/kaggle_sample.csv"
}

summary = []

for dataset, path in files.items():

    df = pd.read_csv(path)

    for method in ["llm", "rag", "slither", "mythril"]:

        if method not in df.columns:
            continue

        report = classification_report(
            df["actual"],
            df[method],
            output_dict=True,
            zero_division=0
        )

        summary.append({
            "dataset": dataset,
            "method": method.upper(),
            "accuracy": report["accuracy"],
            "precision": report["1"]["precision"],
            "recall": report["1"]["recall"],
            "f1": report["1"]["f1-score"]
        })

summary_df = pd.DataFrame(summary)

summary_df.to_csv("results/final_summary.csv", index=False)

print(summary_df)