import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import confusion_matrix

df = pd.read_csv("results/kaggle_sample.csv")

methods = ["llm", "slither"]

for method in methods:

    cm = confusion_matrix(df["actual"], df[method])

    disp = ConfusionMatrixDisplay(cm)

    disp.plot()

    plt.title(method.upper())

    plt.savefig(f"results/{method}_cm.png")

    plt.close()