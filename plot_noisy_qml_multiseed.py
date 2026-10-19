import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "results/noisy_qml_multiseed.csv"
OUT = ROOT / "results/figures"
OUT.mkdir(parents=True, exist_ok=True)

with SOURCE.open(newline="") as f:
    rows = list(csv.DictReader(f))

processors = ["A", "B"]
conditions = ["ideal", "noisy"]
seeds = sorted({int(r["seed"]) for r in rows})

values = {}
for processor in processors:
    for condition in conditions:
        values[(processor, condition)] = np.array([
            float(r["accuracy"]) * 100
            for seed in seeds
            for r in rows
            if int(r["seed"]) == seed
            and r["processor"] == processor
            and r["condition"] == condition
        ])

# Figure 1: Mean accuracy with sample standard deviation.
fig, ax = plt.subplots(figsize=(9, 6))
x = np.arange(2)
width = 0.34

for index, condition in enumerate(conditions):
    means = [
        values[(p, condition)].mean()
        for p in processors
    ]
    stds = [
        values[(p, condition)].std(ddof=1)
        for p in processors
    ]
    bars = ax.bar(
        x + (index - 0.5) * width,
        means,
        width,
        yerr=stds,
        capsize=6,
        label=condition.capitalize()
    )
    for bar, mean in zip(bars, means):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            mean + 2,
            f"{mean:.1f}%",
            ha="center",
            fontsize=10
        )

ax.set_xticks(x, ["Processor A", "Processor B"])
ax.set_ylim(0, 105)
ax.set_ylabel("Test accuracy (%)")
ax.set_title("Quantum Kernel Accuracy Across Three Seeds")
ax.legend(title="Simulation condition")
ax.grid(axis="y", alpha=0.2)
ax.set_axisbelow(True)

fig.text(
    0.5, 0.02,
    "Mean ± sample SD | 24 train / 12 test per split | "
    "256 shots | Illustrative simulated noise",
    ha="center",
    fontsize=9
)
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(OUT / "noisy_qml_multiseed_mean.png", dpi=180)
plt.close(fig)

# Figure 2: Accuracy for each seed.
fig, ax = plt.subplots(figsize=(9, 6))

for processor in processors:
    for condition in conditions:
        ax.plot(
            seeds,
            values[(processor, condition)],
            marker="o",
            linewidth=2,
            label=f"Processor {processor} — {condition}"
        )

ax.set_xticks(seeds)
ax.set_ylim(0, 105)
ax.set_xlabel("Dataset split seed")
ax.set_ylabel("Test accuracy (%)")
ax.set_title("Quantum Kernel Accuracy by Dataset Split")
ax.legend()
ax.grid(alpha=0.25)

fig.text(
    0.5, 0.02,
    "Three stratified splits | 12 test samples per split | "
    "Simulated processors, not hardware",
    ha="center",
    fontsize=9
)
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(OUT / "noisy_qml_multiseed_by_seed.png", dpi=180)
plt.close(fig)

print("Generated:", OUT / "noisy_qml_multiseed_mean.png")
print("Generated:", OUT / "noisy_qml_multiseed_by_seed.png")

for processor in processors:
    for condition in conditions:
        v = values[(processor, condition)]
        print(
            f"Processor {processor}, {condition}: "
            f"mean={v.mean():.2f}%, SD={v.std(ddof=1):.2f}%"
        )
