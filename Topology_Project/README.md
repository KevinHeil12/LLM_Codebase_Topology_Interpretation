# GenAI Codebase Understanding Project

This project evaluates how well different AI models (e.g., OpenAI's `o3-mini`, Groq's `llama3-70b`) understand synthetic Python codebases and extract their structure.

## Features
- Generates codebases with controlled topologies (chain, branch, random)
- Optionally adds semantic names to aid graph inference
- Extracts adjacency graphs using LLMs (OpenAI or Groq)
- Modifies codebases and reruns evaluation
- Runs test suites and scores results
- Logs precision, correctness, and error rates

## Installation
```bash
pip install -r requirements.txt
```

## Environment Variables
Create a `.env` file at the root with:
```
OPENAI_API_KEY=your-openai-key
GROQ_API_KEY=your-groq-key
```

## Running the Experiments
From the project root:
```bash
python -m src.main
```
To toggle providers or semantic naming, edit `main()` in `src/main.py`:
```python
provider = "groq"  # or "openai"
model_name = "llama3-70b-8192"  # or "o3-mini"
use_semantics = True  # optional toggle for semantic naming
```

## Running Tests
```bash
pytest
```

## Project Structure
```
src/
├── main.py              # Entry point
├── utils.py             # Logging + data helpers
├── llm_interface.py     # Unified API for OpenAI + Groq
├── code_analysis.py     # AST parsing, adjacency extraction
├── test_engine.py       # LLM test evaluation
├── experiment_runner.py # Orchestrates experiment runs
├── graph_utils.py       # Adjacency comparison helpers
├── gen.py               # Synthetic codebase generator
├── experiment_plots.py  # Generates various data visualizations
.env                     # API keys (not checked into git)
requirements.txt
README.md
```

## Output
Experiment results are saved to `experiment_results.csv` and printed in terminal debug view.