import pytest
from src.code_analysis import modify_codebase, extract_graph

def test_modify_codebase_single_change():
    code = """
    def foo(): pass
    def bar(): foo()
    """
    modified_code, changes = modify_codebase(code, num_changes=1)
    assert changes == 1
    assert "foo()" not in modified_code

def test_extract_graph_simple_call():
    code = """
    def foo(): pass
    def bar(): foo()
    """
    nodes, adjacency = extract_graph(code)
    assert "foo" in nodes
    assert "bar" in nodes
    assert {"from": "foo", "to": "bar"} in adjacency
