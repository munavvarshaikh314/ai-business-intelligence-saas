from pydantic import BaseModel


class SQLGenerateRequest(BaseModel):
    question: str


class SQLGenerateResponse(BaseModel):
    sql: str