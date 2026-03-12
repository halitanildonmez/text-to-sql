from ollama import chat
from chat_response_model import ChatResponse
import subprocess
import requests
import time
import re
from schema_loader import Database
from error_agent import ErrorAgent

def _clean_sql(sql: str) -> str:
    sql = re.sub(r"```sql|```", "", sql).strip()
    sql = sql.rstrip(";").strip()
    return sql

class LlmAgent:
    def __init__(self, db: Database):
        self.db = db
        self.schema = self.db.get_table_information()
        self.error_agent = ErrorAgent()

    def start_ollama_if_not_running(self):
        try:
            requests.get("http://localhost:11434")
        except requests.ConnectionError:
            print("Starting Ollama...")
            subprocess.Popen(["ollama", "serve"])
            time.sleep(2)

    def generate_prompt(self, question: str, error_message: str = "") -> str:
        error_hint = f"\nPrevious attempt failed: {error_message}\nFix the query." if error_message else ""
        return f"""You are an expert SQL assistant working with a DuckDB database.

Available tables and columns:
{self.schema}

User question: {question}
{error_hint}

Rules:
- Use DuckDB SQL syntax only
- Only reference columns that exist in the schema above
- Return a complete, runnable SQL query
- Also provide a brief plain-English explanation of what the query does
- Make sure SQL is valid, when returning the explanation place it in another json property called explanation so it is 
  not mixed with SQL statements
        """

    def prompt_agent(self, question: str, max_retries: int = 3) -> dict:
        error_msg = ""
        exceptions = []
        error_analysis = []
        last_sql_query = ""
        for _ in range(max_retries):
            try:
                prompt = self.generate_prompt(question, error_msg)
                response = chat(model='gemma3:1b', messages=[
                    {
                        'role': 'user',
                        'content': f'{prompt}',
                    },
                ], format=ChatResponse.model_json_schema())

                parsed = ChatResponse.model_validate_json(response.message.content)

                result_sql = _clean_sql(parsed.SQL)
                last_sql_query = result_sql
                result_df = self.db.run_query(result_sql)
                return {
                    "sql": result_sql,
                    "df": result_df,
                    "explanation": parsed.explanation,
                    "exceptions": exceptions,
                    "analysis": error_analysis,
                }
            except Exception as e:
                error_msg = f"Failed to run: {e} Fix the query"
                exceptions.append(e)
                error_analysis.append(self.error_agent.analyse(question, last_sql_query, self.schema, str(e)))
        return {
            "analysis": error_analysis
        }
