from ollama import chat
from error_analysis_model import ErrorAnalysis

class ErrorAgent:
    def analyse(self, question: str, sql_query:str = "", schema:str = "", error:str = "") -> str:
        prompt = f"""User ran a query in DuckDB and got exceptions.
        User asked {question}
        error: {error}
        schema: {schema}
        query user tried to run: {sql_query}
        Respond with:
        - root_cause: one sentence identifying exactly what went wrong
        - explanation: plain English explanation a non-technical user would understand
        - suggested_fix: what should be changed and why
        """
        response = chat(model='gemma3:1b', messages=[
            {
                'role': 'user',
                'content': f'{prompt}',
            },
        ], format=ErrorAnalysis.model_json_schema())

        return ErrorAnalysis.model_validate_json(response.message.content)