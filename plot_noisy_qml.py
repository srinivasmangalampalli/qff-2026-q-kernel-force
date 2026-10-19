import csv
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

input_file = Path("results/noisy_qml_processor_pilot.csv")
output_file = Path("results/figures/noisy_qml_accuracy.png")

rows = list(csv.DictReader(input_file.open(newline="")))
results = {
    (row["processor"], row["condition"]): float(row["accuracy"]) * 100
    for row in rows
}

processors = ["A", "B"]
ideal = [results[(p, "ideal")] for p in processors]
noisy = [results[(p, "noisy")] for p in processors]

x = np.arange(len(processors))
width = 0.32

fig, ax = plt.subplots(figsize=(9, 6))

bars1 = ax.bar(
    x - width / 2, ideal, width,
    label="Ideal (finite-shot simulation)",
    color="#2563EB"
)
bars2 = ax.bar(
    x + width / 2, noisy, width,
    label="Illustrative noise simulation",
    color="#F59E0B"
)

for bars in (bars1, bars2):
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.2f}%",
            (bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            fontsize=11,
            fontweight="bold"
        )

ax.set_title(
    "Quantum Kernel Classification: Processor A vs B",
    fontsize=15,
    fontweight="bold"
)
ax.set_ylabel("Test Accuracy (%)")
ax.set_xticks(x, ["Processor A", "Processor B"])
ax.set_ylim(0, 105)
ax.legend(loc="upper right")
ax.grid(axis="y", alpha=0.2)
ax.set_axisbelow(True)

fig.text(
    0.5, 0.02,
    "Digits 0 vs 1 | 12 train / 6 test | 256 shots | "
    "One split and seed | Simulated, not hardware",
    ha="center",
    fontsize=9,
    color="#555555"
)

output_file.parent.mkdir(parents=True, exist_ok=True)
fig.tight_layout(rect=(0, 0.055, 1, 1))
fig.savefig(output_file, dpi=180)
plt.close(fig)

print("Figure generated:", output_file)
print("Accuracy values:", results)
