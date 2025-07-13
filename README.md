# LLM_Codebase_Topology_Interpretation

This project evaluates how well different language models (LLMs) can interpret and repair the structure of Python codebases. Codebases are synthetically generated with configurable topology, and LLMs are tasked with predicting or repairing the function/class call graph (adjacency).

---

## 🔧 Features
- Generate Python codebases with chain, branch, or random topologies
- Modify codebases by changing output types
- Evaluate LLM adjacency predictions against gold standard
- Ask LLMs to repair modified codebases
- Toggle between OpenAI, Groq, Anthropic, and Gemini APIs

---

## 📦 Requirements
Install Python dependencies:
```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables
Create a `.env` file at the root:
```env
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
ANTHROPIC_API_KEY=your_anthropic_key
GEMINI_API_KEY=your_gemini_key
```
Only the keys for the models you plan to use are required.

---

## 🚀 Running an Experiment
```bash
python -m src.main
```
This will:
1. Generate a codebase
2. Ask the LLM to extract its adjacency
3. Compare it to the gold adjacency
4. Modify the codebase
5. Ask the LLM to find the structural failure and propose a fix
6. Evaluate the fix

---

## 📊 Outputs
Results are logged in `experiment_results.csv` and printed to the console.

Tracked metrics:
- `Adjacency Match %` before changes
- `Fixes` and `Failures` reported by the LLM
- `Adjacency Match After %` (if applied)
- Token count, number of nodes, etc.

---

## 🧠 Model Configuration
In `main.py`, toggle models like:
```python
provider = "openai"  # or "groq", "gemini", "anthropic"
model_name = "gpt-4"  # or "llama3-70b-8192", "claude-3-opus-20240229", etc.
```

---

## 📁 Project Structure
```
verification_project/
├── gen.py                    # Codebase generator
├── src/
│   ├── main.py              # Experiment launcher
│   ├── experiment_runner.py # LLM interaction logic
│   ├── llm_interface.py     # API wrapper
│   ├── utils.py             # Logging and CSV output
│   ├── test_engine.py       # Test case evaluation
│   └── graph_utils.py       # Adjacency helpers
├── .env
├── requirements.txt
└── README.md
```

---

## 🧪 Example Adjacency Format
LLMs must return adjacency in this format:
```json
{
  "adjacency": {
    "from": [0, 1, 2],
    "to": [1, 2, 3]
  }
}
```

---

## 📬 Contact
For questions or contributions, please open an issue or pull request.
