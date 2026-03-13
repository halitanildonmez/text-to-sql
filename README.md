# Text-to-SQL

![Demo with charts](demo3.gif)

A local AI-powered Streamlit app that converts plain-English questions into SQL queries and runs them against a DuckDB database.

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | [Streamlit](https://streamlit.io) |
| LLM | [Ollama](https://ollama.com) + `gemma3:1b` |
| Database | [DuckDB](https://duckdb.org) (TPC-H benchmark data) |
| Data validation | [Pydantic](https://docs.pydantic.dev) |

---

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running
- The `gemma3:1b` model pulled locally

---

## Setup

**1. Clone the repo**
```bash
git clone <your-repo-url>
cd text-to-sql
```

**2. Install Python dependencies**
```bash
pip install -r requirements.txt
```

**3. Pull the model**
```bash
ollama pull gemma3:1b
```

**4. Run the app**
```bash
streamlit run app_ui.py
```

Streamlit will open in a new tab automatically

> Ollama will start automatically if it isn't already running.

---

## How It Works

1. On startup, DuckDB loads the TPC-H benchmark dataset (scale factor 0.1)
2. The app introspects the schema and includes it in every prompt
3. The user's question is sent to `gemma3:1b` via Ollama with a structured output schema
4. The model returns a SQL query + explanation as JSON
5. The query is executed against DuckDB and results are displayed as a dataframe
6. If execution fails, the error is fed back into the next prompt (up to 3 retries)

---

## Example Questions

- *What are the top 10 customers by total order value?*
- *How many orders were placed each month in 1995?*
- *Which supplier has the highest average part price?*
- *Show me all line items where the discount is greater than 5%*

---

## Configuration

To swap the model, edit `llm_agent.py`:
```python
response = chat(model='gemma3:1b', ...)  # replace with any Ollama model
```

To use a different database, replace the `create_db()` function in `schema_loader.py` with your own DuckDB connection.
