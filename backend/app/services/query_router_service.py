import re

class QueryRouterService:

    # SQL keywords — covers simple and complex analytical questions
    SQL_KEYWORDS = [
        # Basic aggregations
        "total", "sum", "count", "average", "avg", "minimum", "maximum",
        "min", "max", "how many", "how much",

        # Comparisons and rankings
        "top", "bottom", "highest", "lowest", "largest", "smallest",
        "rank", "ranking", "ranked", "compare", "comparison", "versus", "vs",
        "exceed", "exceeds", "exceeded", "above", "below", "greater than", "less than",

        # Analytical patterns
        "percentage", "percent", "contribution", "share", "breakdown",
        "distribution", "trend", "growth", "growth rate", "running total",
        "cumulative", "month over month", "year over year",

        # SQL-specific patterns
        "group by", "order by", "per region", "per category", "per product",
        "by region", "by category", "by month", "by year", "by product",
        "in each", "for each", "per each",

        # Data retrieval
        "show", "list", "display", "give me", "find", "get",
        "what is the", "what are the", "which", "where",
        "rows", "records", "entries", "transactions", "sales",

        # Business terms
        "revenue", "profit", "income", "expense", "cost", "price",
        "quantity", "units", "sold", "purchases", "orders",
        "region", "category", "product", "department", "channel",
        "monthly", "weekly", "daily", "quarterly", "annually",
    ]

    # RAG keywords — document reading questions
    RAG_KEYWORDS = [
        "document", "pdf", "file", "policy", "clause", "section",
        "mentioned", "written", "states", "according to", "based on document",
        "what does it say", "resume", "cv", "certificate", "contract",
        "agreement", "terms", "conditions", "rules", "guidelines",
        "procedure", "protocol", "about me", "my background",
    ]

    # Prediction keywords
    PREDICTION_KEYWORDS = [
        "predict", "forecast", "estimate future", "next month", "next year",
        "next quarter", "will be", "expected", "projection", "churn",
        "likelihood", "probability", "risk",
    ]

    @staticmethod
    def detect_query_type(question: str) -> str:
        q = question.lower().strip()

        # Check prediction first — most specific
        if any(kw in q for kw in QueryRouterService.PREDICTION_KEYWORDS):
            return "PREDICTION"

        # Count keyword matches for SQL vs RAG
        sql_score = sum(1 for kw in QueryRouterService.SQL_KEYWORDS if kw in q)
        rag_score = sum(1 for kw in QueryRouterService.RAG_KEYWORDS if kw in q)

        # SQL wins if it has more matches OR equal matches
        # Default to SQL when ambiguous — SQL is more common for business data
        if sql_score >= rag_score and sql_score > 0:
            return "SQL"

        if rag_score > 0:
            return "RAG"

        # Final fallback — if dataset has CSV data, default SQL
        # If only PDF, default RAG
        return "SQL"


# import re


# class QueryRouterService:
#     """
#     Simple rule-based router (fast + reliable).
#     Later you can upgrade to LLM-based router.
#     """

#     @staticmethod
#     def detect_query_type(question: str) -> str:
#         q = question.lower().strip()

#         # Prediction type keywords
#         prediction_keywords = [
#             "predict", "forecast", "next month", "future", "estimate", "expected",
#             "churn", "probability", "will happen", "trend prediction"
#         ]

#         # SQL analytics keywords
#         sql_keywords = [
#             "total", "sum", "average", "avg", "count", "maximum", "minimum",
#             "group by", "top", "highest", "lowest", "compare", "distribution",
#             "how many", "sales", "revenue", "profit", "orders"
#         ]

#         # Document / PDF keywords
#         rag_keywords = [
#             "according to pdf", "according to document", "policy", "terms",
#             "clause", "section", "explain this paragraph", "from the file",
#             "pdf", "document", "file", "resume", "cv", "profile",
#             "experience", "skills", "education", "qualification", "project",
#             "certificate", "certification", "email", "phone", "contact",
#             "mentioned", "written", "uploaded", "about me", "candidate"
#         ]

#         # Decide
#         if any(k in q for k in prediction_keywords):
#             return "PREDICTION"

#         if any(k in q for k in rag_keywords):
#             return "RAG"

#         if any(k in q for k in sql_keywords):
#             return "SQL"

#         # Default: SQL if it looks like analytics
#         if re.search(r"(sum|avg|count|max|min)", q):
#             return "SQL"

#         return "RAG"
