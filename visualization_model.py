from pydantic import BaseModel

class VizResponse(BaseModel):
    chart_type: str
    x_col: str
    y_col: str
    title: str