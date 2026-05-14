# from pipeline.runner import run_experiment

# run_experiment(
#     "kaggle_sample",
#     {
#         "kaggle_sample/vulnerable": 1,
#         "kaggle_sample/safe": 0,
#     },
# )

from pipeline.runner import run_experiment

# =========================
# REENTRANCY
# =========================
run_experiment(
    "reentrancy_eval",
    {
        "smartbugs_curated/dataset/reentrancy": 1,
        "smartbugs_curated/dataset/arithmetic": 0
    }
)

# =========================
# OVERFLOW
# =========================
run_experiment(
    "overflow_eval",
    {
        "smartbugs_curated/dataset/arithmetic": 1,
        "smartbugs_curated/dataset/reentrancy": 0
    }
)

# =========================
# ACCESS CONTROL
# =========================
run_experiment(
    "access_control_eval",
    {
        "smartbugs_curated/dataset/access_control": 1,
        "smartbugs_curated/dataset/arithmetic": 0
    }
)