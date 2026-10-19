
import csv
from pathlib import Path
from statistics import mean, stdev

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "results/qml_processor_architecture.csv"
OUTPUT = ROOT / "results/figures"
OUTPUT.mkdir(parents=True, exist_ok=True)

with INPUT.open(newline="") as file:
    rows = list(csv.DictReader(file))

processors = ["A", "B"]
entanglements = ["linear", "full"]

def measurements(processor, entanglement, metric):
    return [
        float(row[metric])
        for row in rows
        if row["processor"] == processor
        and row["entanglement"] == entanglement
    ]

def make_plot(metric, ylabel, filename, title):
    x = np.arange(len(entanglements))
    width = 0.34

    fig, ax = plt.subplots(figsize=(8, 5))

    for index, processor in enumerate(processors):
        groups = [
            measurements(processor, ent, metric)
            for ent in entanglements
        ]

        averages = [mean(values) for values in groups]
        errors = [
            stdev(values) if len(values) > 1 else 0
            for values in groups
        ]

        positions = x + (index - 0.5) * width

        bars = ax.bar(
            positions,
            averages,
            width,
            yerr=errors,
            capsize=4,
            label=f"Processor {processor}"
        )

        for bar, value in zip(bars, averages):
            ax.annotate(
                f"{value:.1f}",
                (bar.get_x() + bar.get_width() / 2,
                 bar.get_height()),
                xytext=(0, 7),
                textcoords="offset points",
                ha="center",
                fontsize=10
            )

    ax.set_xticks(x)
    ax.set_xticklabels(["Linear", "Full"])
    ax.set_xlabel("ZZ feature-map entanglement")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", alpha=0.2)

    fig.tight_layout()
    path = OUTPUT / filename
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print("Saved:", path)

make_plot(
    "depth",
    "Transpiled circuit depth",
    "qml_processor_depth.png",
    "Processor A vs B — Circuit Depth"
)

make_plot(
    "cx_gates",
    "CX gate count",
    "qml_processor_cx.png",
    "Processor A vs B — CX Gates"
)
