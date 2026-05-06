import re


class QueryRouterService:
    """
    Simple rule-based router (fast + reliable).
    Later you can upgrade to LLM-based router.
    """

    @staticmethod
    def detect_query_type(question: str) -> str:
        q = question.lower().strip()

        # Prediction type keywords
        prediction_keywords = [
            "predict", "forecast", "next month", "future", "estimate", "expected",
            "churn", "probability", "will happen", "trend prediction"
        ]

        # SQL analytics keywords
        sql_keywords = [
            "total", "sum", "average", "avg", "count", "maximum", "minimum",
            "group by", "top", "highest", "lowest", "compare", "distribution",
            "how many", "sales", "revenue", "profit", "orders"
        ]

        # Document / PDF keywords
        rag_keywords = [
            "according to pdf", "according to document", "policy", "terms",
            "clause", "section", "explain this paragraph", "from the file"
        ]

        # Decide
        if any(k in q for k in prediction_keywords):
            return "PREDICTION"

        if any(k in q for k in rag_keywords):
            return "RAG"

        if any(k in q for k in sql_keywords):
            return "SQL"

        # Default: SQL if it looks like analytics
        if re.search(r"(sum|avg|count|max|min)", q):
            return "SQL"

        return "RAG"