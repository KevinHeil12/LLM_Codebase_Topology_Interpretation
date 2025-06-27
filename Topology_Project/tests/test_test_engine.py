from src.test_engine import run_llm_tests

def test_run_llm_tests_pass_case():
    code = """
    def add(x, y):
        return x + y
    """
    tests = {
        "tests": [
            {
                "node": "add",
                "test": "assert add(2, 3) == 5",
                "input": "",
                "output": "",
                "result": "pass"
            }
        ]
    }
    results = run_llm_tests(code, tests)
    assert len(results) == 1
    assert results[0]["actual_pass"] is True
    assert results[0]["actual_err"] == ""