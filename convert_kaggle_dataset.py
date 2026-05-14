import pandas as pd
import os

# ==============================
# 📂 INPUT CSV
# ==============================
CSV_PATH = "dataset-1_35228.csv"

# ==============================
# 📁 OUTPUT DIR
# ==============================
OUTPUT_DIR = "datasets/kaggle"

vuln_dir = os.path.join(OUTPUT_DIR, "vulnerable")
safe_dir = os.path.join(OUTPUT_DIR, "safe")

os.makedirs(vuln_dir, exist_ok=True)
os.makedirs(safe_dir, exist_ok=True)

# ==============================
# 📖 LOAD CSV
# ==============================
df = pd.read_csv(CSV_PATH)

print("Total rows:", len(df))

# ==============================
# 🔄 CONVERT
# ==============================
for i, row in df.iterrows():
    code = str(row["code"])

    # Skip bad rows
    if code.strip() == "" or code == "nan":
        continue

    # Label
    label = row["label_encoded"]

    # Normalize label
    if label == 0:
        folder = safe_dir
    else:
        folder = vuln_dir

    filename = f"{i}.sol"
    filepath = os.path.join(folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)

print("✅ Conversion complete")
