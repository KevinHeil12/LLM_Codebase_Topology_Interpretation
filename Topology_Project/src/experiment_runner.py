import json
from src.utils import log_result
from src.code_analysis import modify_and_extract
from src.graph_utils import _normalise_adj, _without_main, flip_adjacency, safe_flip
from src.test_engine import run_llm_tests, precision_and_err_rate, static_completeness_ok
from src.llm_interface import send_message
from pydantic import BaseModel

class CodeProperties(BaseModel):
    nodes: list
    adjacency: dict

class CodePropertiesWithTests(BaseModel):
    nodes: list
    adjacency: dict
    tests: dict

def run_topology_experiment_with_provider(topology_mode, codebase_generator, client, structured_prompt, structured_prompt_2, ai_data, avg_length, num_changes, provider, model, debug_callback=None):
    for obj_count in range(10, 51, 5):
        code, nodes, adj = codebase_generator(
            num_objects=obj_count,
            avg_length=avg_length,
            branching_factor=0,
            loop_factor=0,
            connectivity=1.0 if topology_mode != "random" else 0.6,
            topology_mode=topology_mode
        )

        tokens = len(code.encode("utf-8"))
        if tokens >= 50000:
            continue

        ai_data["Number of Nodes"].append(len(nodes))
        ai_data["Avg Length"].append(avg_length)
        ai_data["Input Tokens"].append(tokens)

        gold_adj = {"from": [], "to": []}
        for index, parents in enumerate(adj):
            for parent in parents:
                gold_adj["from"].append(parent)
                gold_adj["to"].append(index)

        conversation = [
            {"role": "system", "content": "You are a helpful assistant specialized in Python. Only return valid JSON conforming to the CodeProperties schema."},
            {"role": "user", "content": structured_prompt}
        ]

        try:
            reply = send_message(client, provider, conversation, model)
            conversation.append({"role": "assistant", "content": reply})
            if debug_callback:
                debug_callback(
                    f"Initial Adjacency - {topology_mode.upper()} | Nodes: {len(nodes)} | AvgLen: {avg_length}",
                    gold_adj,
                    reply
                )

            parsed = json.loads(reply)
            validated = CodeProperties(**parsed)

            parsed["nodes"] = [int(n.split("_")[-1]) for n in parsed["nodes"] if isinstance(n, str) and n != "main"]
            new_from, new_to = [], []
            for f, t in zip(parsed["adjacency"]["from"], parsed["adjacency"]["to"]):
                if f != "main" and t != "main":
                    try:
                        new_to.append(int(f.split("_")[-1]))
                        new_from.append(int(t.split("_")[-1]))
                    except Exception:
                        continue
            parsed["adjacency"]["from"] = new_from
            parsed["adjacency"]["to"] = new_to

            gold_pairs = set(_without_main(_normalise_adj(gold_adj)))
            llm_pairs = set(_without_main(_normalise_adj(parsed["adjacency"])))
            ai_data["Correct Adjacency?"].append(gold_pairs == llm_pairs)

        except Exception as e:
            ai_data["Correct Adjacency?"].append(False)
            ai_data["Number of Changes"].append(0)
            ai_data["Correct After Changes?"].append(False)
            return

        new_code, changes, new_nodes, new_adj = modify_and_extract(code, num_changes)
        ai_data["Number of Changes"].append(changes)
        conversation.append({"role": "user", "content": structured_prompt_2})

        try:
            reply = send_message(client, provider, conversation, model)
            if debug_callback:
                debug_callback(
                    f"Modified Adjacency - {topology_mode.upper()} | Nodes: {len(new_nodes)} | Changes: {changes}",
                    new_adj,
                    reply
                )

            parsed_new = json.loads(reply)

            try:
                parsed_new["adjacency"] = flip_adjacency(parsed_new["adjacency"])
            except:
                parsed_new["adjacency"] = safe_flip(parsed_new["adjacency"])

            gold = set(_without_main(_normalise_adj(new_adj)))
            pred = set(_without_main(_normalise_adj(parsed_new["adjacency"])))
            ai_data["Correct After Changes?"].append(gold == pred)

            complete = static_completeness_ok(parsed_new, new_nodes)
            test_results = run_llm_tests(new_code, parsed_new)
            precision, err_rate = precision_and_err_rate(test_results)
            ai_data["Tests Complete?"].append(complete)
            ai_data["Pass/Fail Precision"].append(precision)
            ai_data["Exception Match Rate"].append(err_rate)

        except Exception:
            ai_data["Correct After Changes?"].append(False)

        log_result(topology_mode.capitalize(), len(nodes), avg_length, tokens, changes, ai_data)

def display_debug_info(title, adjacency, response=None):
    print("\n" + "=" * 60)
    print(f"{title}")
    print("Adjacency Matrix:")
    print(json.dumps(adjacency, indent=2))
    if response:
        print("\nLLM Response:")
        print(response)
    print("=" * 60 + "\n")
