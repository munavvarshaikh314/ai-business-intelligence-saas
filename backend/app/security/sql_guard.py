import re
from fastapi import HTTPException

# These are actual dangerous SQL operations
# NOT included: truncate (blocks DATE_TRUNC), create (blocks created_at)
FORBIDDEN_STATEMENTS = [
    "drop",
    "delete",
    "alter",
    "update",
    "insert",
    "grant",
    "revoke",
]

class SQLGuard:
    @staticmethod
    def validate(sql_query: str):
        # Strip trailing semicolon before validation
        q = sql_query.rstrip(";").strip().lower()

        # Block multiple statements (semicolon in middle of query)
        if ";" in q:
            raise HTTPException(
                status_code=400,
                detail="Multiple SQL statements are not allowed"
            )

        # Block dangerous operations using word boundaries
        for word in FORBIDDEN_STATEMENTS:
            if re.search(rf"\b{word}\b", q):
                raise HTTPException(
                    status_code=403,
                    detail=f"Forbidden SQL operation: {word}"
                )

        # Must start with SELECT or WITH (CTEs)
        if not (q.startswith("select") or q.startswith("with")):
            raise HTTPException(
                status_code=403,
                detail="Only SELECT queries are allowed"
            )

        return True
