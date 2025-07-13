import os
import csv
import time
import json
import openai
from openai import OpenAI


from src.gen import generate_codebase
from src.utils import append_result, log_result, initialize_data_dict
from src.code_analysis import modify_codebase, extract_graph, modify_and_extract
from src.graph_utils import flip_adjacency, safe_flip, _normalise_adj, _without_main
from src.test_engine import run_llm_tests, precision_and_err_rate, static_completeness_ok
from src.experiment_runner import run_topology_experiment_with_provider, display_debug_info
from src.llm_interface import setup_client, send_message

CSV_FILE = "experiment_results.csv"
FIELDNAMES = [
    "timestamp",
    "topology",
    "num_nodes",
    "avg_length",
    "input_tokens",
    "num_changes",
    "adjacency_match_percentage",
    "correct_adj_after_changes",
    "tests_complete",
    "pf_precision",
    "exception_match_rate",
]

structured_prompt = """
Generate a JSON object that describes a codebase with the following properties:
- nodes: list
- adjacency: dict {"from": [], "to": []}
The output must be valid JSON.
"""

structured_prompt_2 = """
Generate a JSON object that describes a codebase with the following properties:
- nodes: list
- adjacency: dict {"from": [], "to": []}
- tests: dict {"node": [], "test": [], "input": [], "output": [], "result": []}
"""

def main():
    provider = "groq"  # Change to "openai" or "groq"
    model_name = "llama3-70b-8192" if provider == "groq" else "o3-mini"

    client = setup_client(provider)
    chain_ai_data, branch_ai_data, random_ai_data = initialize_data_dict(), initialize_data_dict(), initialize_data_dict()

    for length in [5, 7, 9, 11, 13, 15]:
        for changes in [1, 2, 3, 4, 5]:
            run_topology_experiment_with_provider(
                "chain",
                generate_codebase,
                client,
                structured_prompt,
                structured_prompt_2,
                chain_ai_data,
                avg_length=length,
                num_changes=changes,
                provider=provider,
                model=model_name,
                debug_callback=display_debug_info,
                use_semantics=False
            )
            run_topology_experiment_with_provider(
                "branch",
                generate_codebase,
                client,
                structured_prompt,
                structured_prompt_2,
                branch_ai_data,
                avg_length=length,
                num_changes=changes,
                provider=provider,
                model=model_name,
                debug_callback=display_debug_info,
                use_semantics=False
            )
            run_topology_experiment_with_provider(
                "random",
                generate_codebase,
                client,
                structured_prompt,
                structured_prompt_2,
                random_ai_data,
                avg_length=length,
                num_changes=changes,
                provider=provider,
                model=model_name,
                debug_callback=display_debug_info,
                use_semantics=False
            )

if __name__ == "__main__":
    main()
