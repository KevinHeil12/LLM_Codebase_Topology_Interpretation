def _normalise_adj(adj_block):
    """
    Accepts the two formats the LLM (or your extractor) might return:

      • list[dict]         [{"from": x, "to": y}, ...]
      • dict[str, list]    {"from": [...], "to": [...]}

    Returns a list of (parent, child) tuples.
    """
    if isinstance(adj_block, list):
        return [
            (edge.get("from"), edge.get("to"))
            for edge in adj_block
            if "from" in edge and "to" in edge
        ]

    if isinstance(adj_block, dict):
        return list(zip(adj_block.get("from", []), adj_block.get("to", [])))

    return []   # unknown structure

def _without_main(pairs):
    """Return all (parent, child) tuples that do *not* mention 'main'."""
    return [(p, c) for (p, c) in pairs if p != "main" and c != "main"]

def flip_adjacency(edge_dict: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Return a new adjacency dict whose 'from' and 'to' lists are swapped,
    preserving order and multiplicity.

    Parameters
    ----------
    edge_dict : {"from": list, "to": list}
        The LLM-produced adjacency.  Lengths must match.

    Returns
    -------
    {"from": list, "to": list}
        A copy with parent/child directions reversed.
    """
    if not edge_dict or "from" not in edge_dict or "to" not in edge_dict:
        raise ValueError("adjacency must have 'from' and 'to' lists")

    if len(edge_dict["from"]) != len(edge_dict["to"]):
        raise ValueError("'from' and 'to' lists are different lengths")

    return {
        "from": edge_dict["to"][:],   # shallow-copy
        "to":   edge_dict["from"][:]
    }

def safe_flip(edge_dict):
    """Flip 'from' and 'to'.  If the lists are different lengths, truncate the
    longer one so the operation never throws."""
    if not edge_dict or "from" not in edge_dict or "to" not in edge_dict:
        return {"from": [], "to": []}          # or raise
    m = min(len(edge_dict["from"]), len(edge_dict["to"]))
    return {"from": edge_dict["to"][:m], "to": edge_dict["from"][:m]}