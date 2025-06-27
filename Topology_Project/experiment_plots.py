
"""
experiment_plots.py
-------------------
Generate exploratory plots for the `experiment_results.csv` dataset.

Required columns:
timestamp, topology, num_nodes, avg_length, input_tokens, num_changes,
correct_initial_adj, correct_adj_after_changes, tests_complete,
pf_precision, exception_match_rate
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import make_scorer, accuracy_score
from scipy.special import expit  # logistic sigmoid
from sklearn.utils import resample

def logistic_curve_plot(y_col, x_col, title, y_label, x_label, fname):
    """Fit logistic regression model and plot probability curve for each topology."""
    fig, ax = plt.subplots()
    x_plot = np.linspace(df[x_col].min(), df[x_col].max(), 300)

    for topo, g in df.groupby("topology"):
        # Binary labels
        X = g[[x_col]].values
        y = g[y_col].astype(int).values

        if len(np.unique(y)) == 1:
            print(f"Skipping {topo} for {y_col} (only one class present).")
            continue

        # Fit logistic regression
        model = LogisticRegression()
        model.fit(X, y)

        # Predict probabilities
        y_prob = model.predict_proba(x_plot.reshape(-1, 1))[:, 1]
        ax.plot(x_plot, y_prob, label=f"{topo} (logit)", linestyle="--")

        # Also scatter the actual binned means for visual check
        bins = np.linspace(X.min(), X.max(), 10)
        g["bin"] = pd.cut(g[x_col], bins)
        means = g.groupby("bin")[y_col].mean()
        centers = [b.mid for b in means.index.categories]
        ax.scatter(centers, means.values, label=f"{topo} (binned)", marker='o')

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend(title="Topology")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, fname), dpi=300, bbox_inches="tight")
    if SHOW_FIGURES:
        plt.show()
    plt.close(fig)

# ---------- Configuration ----------
CSV_PATH = "experiment_results.csv"
OUTPUT_DIR = "plots"
SHOW_FIGURES = False  # flip to True if you want the script to display windows
# -----------------------------------

# Make sure we don't accidentally use any matplotlib styles
plt.rcParams.update(plt.rcParamsDefault)

# Create output dir
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load data
df = pd.read_csv(CSV_PATH)

# Ensure boolean columns are actually boolean
bool_cols = [
    "correct_initial_adj",
    "correct_adj_after_changes",
    "tests_complete",
]
for col in bool_cols:
    if df[col].dtype != bool:
        df[col] = df[col].astype(bool)

# Helper to group and plot
def line_plot(y_col, x_col, title, y_label, x_label, fname):
    """Plot mean(y_col) vs x_col for each topology."""
    fig, ax = plt.subplots()
    for topo, g in df.groupby("topology"):
        # Compute mean of y per x
        summary = (
            g.groupby(x_col)[y_col].mean().sort_index()
        )  # mean of bool gives proportion
        ax.plot(
            summary.index,
            summary.values,
            marker="o",
            label=topo,
        )
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend(title="Topology")
    fig.tight_layout()
    fig_path = os.path.join(OUTPUT_DIR, fname)
    fig.savefig(fig_path, dpi=300, bbox_inches="tight")
    if SHOW_FIGURES:
        plt.show()
    plt.close(fig)

# ---------- Scatter plots ----------
def scatter_plot(y_col, x_col, title, y_label, x_label, fname):
    """Scatter plot of mean(y_col) vs x_col for each topology – no connecting lines."""
    fig, ax = plt.subplots()
    for topo, g in df.groupby("topology"):
        summary = g.groupby(x_col)[y_col].mean().sort_index()
        ax.scatter(summary.index, summary.values, marker="o", label=topo)  # <-- no lines
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend(title="Topology")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, fname), dpi=300, bbox_inches="tight")
    if SHOW_FIGURES:
        plt.show()
    plt.close(fig)

BIN_EDGES = np.arange(0, df["input_tokens"].max() + 1000, 1000)  # 0-49, 50-99, ...
#    ↑ adjust the 50 to any bin width (or provide an explicit list)
df["token_range"] = pd.cut(
    df["input_tokens"],
    bins=BIN_EDGES,
    include_lowest=True,
    right=False,                 # [0,50) style intervals
    labels=[
        f"{int(l)}–{int(r-1)}"   # pretty labels like “0–49”
        for l, r in zip(BIN_EDGES[:-1], BIN_EDGES[1:])
    ],
)

def binned_bar(y_col, title, y_label, fname):
    """
    Aggregate y_col by token_range and plot bars for each topology.
    For booleans, the height is the proportion correct; for floats (pf_precision),
    it’s the average within the bin.
    """
    fig, ax = plt.subplots()
    token_levels = df["token_range"].cat.categories
    x = np.arange(len(token_levels))
    bar_width = 0.25

    for i, (topo, g) in enumerate(df.groupby("topology")):
        means = g.groupby("token_range")[y_col].mean().reindex(token_levels)
        ax.bar(
            x + i * bar_width,
            means.values,
            bar_width,
            label=topo,
        )

    ax.set_xticks(x + bar_width)
    ax.set_xticklabels(token_levels, rotation=45, ha="right")
    ax.set_xlabel("Input-token range")
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend(title="Topology")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, fname), dpi=300, bbox_inches="tight")
    if SHOW_FIGURES:
        plt.show()
    plt.close(fig)

# ---------- Line / scatter plots ----------
line_plot(
    "correct_initial_adj",
    "num_nodes",
    "Correct Initial Adjacency vs Number of Nodes",
    "Proportion Correct",
    "Number of Nodes",
    "correct_initial_vs_nodes.png",
)

# Correct Initial Adjacency vs token ranges
logistic_curve_plot(
    "correct_initial_adj",
    "input_tokens",
    "Logistic Regression: Correct Initial Adjacency vs Input Tokens",
    "Probability of Correct Initial Adjacency",
    "Input Tokens",
    "logit_correct_initial_vs_tokens.png"
)

line_plot(
    "correct_initial_adj",
    "avg_length",
    "Correct Initial Adjacency vs Average Object Length",
    "Proportion Correct",
    "Average Object Length",
    "correct_initial_vs_length.png",
)

line_plot(
    "correct_adj_after_changes",
    "num_nodes",
    "Correct Final Adjacency vs Number of Nodes",
    "Proportion Correct",
    "Number of Nodes",
    "correct_final_vs_nodes.png",
)

# Correct Final Adjacency vs token ranges
logistic_curve_plot(
    "correct_adj_after_changes",
    "input_tokens",
    "Logistic Regression: Final Adjacency vs Input Tokens",
    "Probability of Correct Final Adjacency",
    "Input Tokens",
    "logit_final_adj_vs_tokens.png"
)

line_plot(
    "correct_adj_after_changes",
    "avg_length",
    "Correct Final Adjacency vs Average Object Length",
    "Proportion Correct",
    "Average Object Length",
    "correct_final_vs_length.png",
)

line_plot(
    "correct_adj_after_changes",
    "num_changes",
    "Correct Final Adjacency vs Number of Changes",
    "Proportion Correct",
    "Number of Changes",
    "correct_final_vs_changes.png",
)

line_plot(
    "pf_precision",
    "num_nodes",
    "Pass/Fail Precision vs Number of Nodes",
    "Precision",
    "Number of Nodes",
    "precision_vs_nodes.png",
)

line_plot(
    "pf_precision",
    "avg_length",
    "Pass/Fail Precision vs Average Object Length",
    "Precision",
    "Average Object Length",
    "precision_vs_length.png",
)

line_plot(
    "pf_precision",
    "num_changes",
    "Pass/Fail Precision vs Number of Changes",
    "Precision",
    "Number of Changes",
    "precision_vs_changes.png",
)

# ---------- Bar charts ----------
import numpy as np

def bar_chart(values_dict, title, y_label, fname, group_labels=None):
    fig, ax = plt.subplots()
    # Single-level bar chart
    labels = list(values_dict.keys())
    values = list(values_dict.values())
    x = np.arange(len(labels))
    ax.bar(x, values)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    fig.tight_layout()
    fig_path = os.path.join(OUTPUT_DIR, fname)
    fig.savefig(fig_path, dpi=300, bbox_inches="tight")
    if SHOW_FIGURES:
        plt.show()
    plt.close(fig)

# 1. Percentage correct adjacency before and after changes
bar_width = 0.35
fig, ax = plt.subplots()
topologies = sorted(df["topology"].unique())
x = np.arange(len(topologies))
pre = []
post = []
for topo in topologies:
    subset = df[df["topology"] == topo]
    pre.append(subset["correct_initial_adj"].mean())
    post.append(subset["correct_adj_after_changes"].mean())

ax.bar(x - bar_width / 2, pre, bar_width, label="Before Changes")
ax.bar(x + bar_width / 2, post, bar_width, label="After Changes")
ax.set_xticks(x)
ax.set_xticklabels(topologies)
ax.set_ylabel("Proportion Correct")
ax.set_title("Correct Adjacency Before vs After Changes by Topology")
ax.legend()
fig.tight_layout()
fig_path = os.path.join(OUTPUT_DIR, "adjacency_before_after_bar.png")
fig.savefig(fig_path, dpi=300, bbox_inches="tight")
if SHOW_FIGURES:
    plt.show()
plt.close(fig)

# 2. Percentage of tests complete for each topology
tests_complete_values = {
    topo: df[df["topology"] == topo]["tests_complete"].mean()
    for topo in topologies
}
bar_chart(
    tests_complete_values,
    "Percentage of Tests Complete by Topology",
    "Proportion Complete",
    "tests_complete_bar.png",
)

# 3. Average precision of each topology
precision_values = {
    topo: df[df["topology"] == topo]["pf_precision"].mean()
    for topo in topologies
}
bar_chart(
    precision_values,
    "Average PF Precision by Topology",
    "Precision",
    "precision_bar.png",
)

print(f"All plots saved to '{OUTPUT_DIR}/' directory.")

print( df.groupby("topology")["correct_adj_after_changes"].value_counts(dropna=False))
print( df.groupby("topology")["tests_complete"].value_counts(dropna=False))
