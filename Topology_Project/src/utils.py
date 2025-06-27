import os
import csv
import time

CSV_FILE = "experiment_results.csv"
FIELDNAMES = [
    "timestamp", "topology", "num_nodes", "avg_length", "input_tokens",
    "num_changes", "correct_initial_adj", "correct_adj_after_changes",
    "tests_complete", "pf_precision", "exception_match_rate",
]

def append_result(row_dict):
    new_file = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        if new_file:
            writer.writeheader()
        writer.writerow({**{k: "" for k in FIELDNAMES}, **row_dict})
        fh.flush()

def log_result(topology, node_count, avg_len, tokens, changes, data_dict):
    append_result({
        "timestamp":             time.strftime("%Y-%m-%d %H:%M:%S"),
        "topology":              topology,
        "num_nodes":             node_count,
        "avg_length":            avg_len,
        "input_tokens":          tokens,
        "num_changes":           changes,
        "correct_initial_adj":       data_dict["Correct Adjacency?"][-1],
        "correct_adj_after_changes": data_dict["Correct After Changes?"][-1],
        "tests_complete":        data_dict["Tests Complete?"][-1],
        "pf_precision":          data_dict["Pass/Fail Precision"][-1],
        "exception_match_rate":  data_dict["Exception Match Rate"][-1],
    })

def initialize_data_dict():
    return {
        "Number of Nodes": [],
        "Avg Length": [],
        "Input Tokens": [],
        "Correct Adjacency?": [],
        "Number of Changes": [],
        "Correct After Changes?": [],
        "Tests Complete?": [],
        "Pass/Fail Precision": [],
        "Exception Match Rate": []
    }