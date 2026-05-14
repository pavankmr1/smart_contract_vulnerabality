import pandas as pd
import os

# ==============================
# CONFIG
# ==============================
CSV_PATH = "dataset-1_35228.csv"
OUTPUT_DIR = "datasets/kaggle_sample"

SAMPLE_SIZE = 100  # per class

# ==============================
# CREATE FOLDERS
# ==============================
vuln_dir = os.path.join(OUTPUT_DIR, "vulnerable")
safe_dir = os.path.join(OUTPUT_DIR, "safe")

os.makedirs(vuln_dir, exist_ok=True)
os.makedirs(safe_dir, exist_ok=True)

# ==============================
# LOAD DATA
# ==============================
df = pd.read_csv(CSV_PATH)

print("Total rows:", len(df))

# ==============================
# SPLIT BY LABEL
# ==============================
vuln_df = df[df["label_encoded"] != 0]
safe_df = df[df["label_encoded"] == 0]

# ==============================
# SAMPLE
# ==============================
vuln_sample = vuln_df.sample(n=SAMPLE_SIZE, random_state=42)
safe_sample = safe_df.sample(n=SAMPLE_SIZE, random_state=42)

# ==============================
# SAVE FILES
# ==============================
def save_contracts(df_subset, folder):
    for i, row in df_subset.iterrows():
        code = str(row["code"])

        if code.strip() == "" or code == "nan":
            continue

        filename = f"{i}.sol"
        path = os.path.join(folder, filename)

        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

# Save both
save_contracts(vuln_sample, vuln_dir)
save_contracts(safe_sample, safe_dir)

print(f"✅ Saved {SAMPLE_SIZE} vulnerable and {SAMPLE_SIZE} safe contracts")