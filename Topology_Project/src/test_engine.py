import collections
import types

_BAD_TEST = object()                     # sentinel for impossible key look‑ups
_ALT_NODE_KEYS = {"name", "target", "id"}      # common mistakes by the LLM
_REQ_KEYS      = {"node", "test", "result"}    # minimum we need

def _normalise_tests(tests_block):
    """
    Accepts:
      • list[dict]          ← preferred
      • dict[str, list]     ← parallel lists that may be ragged
      • None / anything else
    Returns list[dict] with safe, uniform rows.
    """
    # ── nothing provided ────────────────────────────────────────────────
    if not tests_block:
        return []

    # ── already list[dict] ──────────────────────────────────────────────
    if isinstance(tests_block, list):
        return [_repair_keys(t) for t in tests_block if isinstance(t, dict)]

    # ── dict[str, list]  → transpose safely ─────────────────────────────
    if isinstance(tests_block, dict):
        # keep only the items that really are lists
        list_cols = {k: v for k, v in tests_block.items() if isinstance(v, list)}
        if not list_cols:                       # nothing usable
            return []

        min_len = min(len(v) for v in list_cols.values())
        out = []
        for i in range(min_len):
            row = {k: list_cols[k][i] for k in list_cols}
            out.append(_repair_keys(row))
        return out

    # ── unrecognised structure ─────────────────────────────────────────
    return []

def _repair_keys(d: dict) -> dict:
    """
    Ensures the dict has a 'node' key.  If it's using an alternative key
    (e.g. 'name'), rename it.  Leaves other fields untouched.
    """
    if "node" in d:
        return d
    for alt in _ALT_NODE_KEYS:
        if alt in d:
            d["node"] = d.pop(alt)
            return d
    return d

def static_completeness_ok(tests_dict: dict, node_list: list) -> bool:
    """
    True ⇢ every node appears exactly twice (pass + fail).
    If the tests block is missing or malformed, returns False.
    """
    tests = _normalise_tests(tests_dict.get("tests"))
    if not tests:
        return False                            # no tests at all

    # quick schema guard
    if not all(_REQ_KEYS <= t.keys() for t in tests):
        return False

    wanted = collections.Counter({n: 2 for n in node_list})
    seen   = collections.Counter(t.get("node", _BAD_TEST) for t in tests)
    return wanted == seen

def run_llm_tests(code_str: str, tests_dict: dict):
    """
    Executes each test and records ground‑truth outcome.
    Returns list[dict]; empty list if no runnable tests.
    """
    tests = _normalise_tests(tests_dict.get("tests"))
    if not tests:
        return []                               # nothing to run

    mod = types.ModuleType("sut")
    exec(compile(code_str, "<sut>", "exec"), mod.__dict__)

    out = []
    for t in tests:
        if not _REQ_KEYS <= t.keys():           # schema incomplete
            continue

        want_pass   = t["result"].lower() == "pass"
        predicted_e = t.get("error", "")
        try:
            exec(t["test"], mod.__dict__)
            actual_pass, actual_err = True, ""
        except Exception as e:
            actual_pass, actual_err = False, type(e).__name__

        out.append({
            "node":         t["node"],
            "want_pass":    want_pass,
            "actual_pass":  actual_pass,
            "predicted_err":predicted_e,
            "actual_err":   actual_err,
        })
    return out

def precision_and_err_rate(results: list[dict]) -> tuple[float, float]:
    """
    Returns (pass_fail_precision, exception_match_rate)
    """
    if not results:
        return 0.0, 0.0
    pf_prec = sum(r["want_pass"] == r["actual_pass"] for r in results) / len(results)

    err_records = [r for r in results if not r["actual_pass"]]
    if not err_records:
        err_rate = 1.0                                    # no failures ⇒ trivially 100 %
    else:
        err_rate = sum(r["predicted_err"] == r["actual_err"]
                       for r in err_records) / len(err_records)
    return pf_prec, err_rate