from pydantic import BaseModel
from typing import Optional, List, Any


class SQLQueryRequest(BaseModel):
    sql: str


class SummaryResponse(BaseModel):
    total_rows: int
    total_revenue: Optional[float] = None
    avg_revenue: Optional[float] = None
    top_product: Optional[str] = None


class ChartResponse(BaseModel):
    chartType: str
    x: List[Any]
    y: List[Any]
    insight: Optional[str] = None


class SQLQueryResponse(BaseModel):
    columns: list[str]
    rows: list[list[Any]]