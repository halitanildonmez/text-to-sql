from ollama import chat
from visualization_model import VizResponse
import plotly.express as px

class VizChartAgent:
    def __init__(self, df):
        self.df = df
    def describe_dataframe(self):
        return {
                "columns": list(self.df.columns),
                "dtypes": self.df.dtypes.astype(str).to_dict(),
                "n_rows": len(self.df),
                "sample": self.df.head(5).to_dict(orient="records")
            }
    def prompt_agent(self):
        prompt = f"""
        You are a data visualization expert.
        Based on this DataFrame description:
         
        {self.describe_dataframe()}
         
        Choose the best chart type and which columns to use.
        chart_type must be one of: bar, line, pie
        x_col and y_col must be exact column names from the DataFrame.
        """
        response = chat(model='gemma3:1b', messages=[
            {
                'role': 'user',
                'content': f'{prompt}',
            },
        ], format=VizResponse.model_json_schema())

        return VizResponse.model_validate_json(response.message.content)

    def plot(self):
        viz = self.prompt_agent()
        numeric_cols = self.df.select_dtypes(include="number").columns.tolist()
        text_cols = self.df.select_dtypes(exclude="number").columns.tolist()
        x = viz.x_col if viz.x_col in self.df.columns else (text_cols or numeric_cols)[0]
        y = viz.y_col if viz.y_col in self.df.columns else numeric_cols[0] if numeric_cols else text_cols[0]

        if viz.chart_type == "bar":
            return px.bar(self.df, x=x, y=y, title=viz.title)
        elif viz.chart_type == "scatter":
            return px.scatter(self.df, x=x, y=y, title=viz.title)
        elif viz.chart_type == "pie":
            return px.pie(self.df, names=x, values=y, title=viz.title)
        elif viz.chart_type == "histogram":
            return px.histogram(self.df, x=x, title=viz.title)
        return px.line(self.df, x=x, y=y, title=viz.title)
