import re
from fastapi import HTTPException


FORBIDDEN_SQL = [
    "drop",
    "delete",
    "truncate",
    "alter",
    "update",
    "insert",
    "grant",
    "revoke",
    "commit",
    "rollback"
]


class SQLGuard:

    @staticmethod
    def validate(sql_query: str):
        q = sql_query.lower().strip()

        # Block multiple queries (semicolon)
        if ";" in q:
            raise HTTPException(status_code=400, detail="Multiple SQL statements are not allowed")

        # Block forbidden keywords
        for word in FORBIDDEN_SQL:
            if re.search(rf"\b{word}\b", q):
                raise HTTPException(status_code=403, detail=f"Forbidden SQL operation detected: {word}")

        # Only allow SELECT queries
        if not q.startswith("select"):
            raise HTTPException(status_code=403, detail="Only SELECT queries are allowed")

        return True