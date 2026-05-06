import re

def sanitize_column_name(col: str) -> str:
    """
    Convert column names to safe SQL column names.
    Example: "Total Revenue $" -> "total_revenue"
    """
    col = col.strip().lower()
    col = re.sub(r"[^a-z0-9_]+", "_", col)
    col = re.sub(r"_+", "_", col)
    col = col.strip("_")

    if col == "":
        col = "col"

    if col[0].isdigit():
        col = f"col_{col}"

    return col


def sanitize_table_name(name: str) -> str:
    """
    Ensure safe SQL table name.
    """
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_]+", "_", name)
    name = re.sub(r"_+", "_", name)
    name = name.strip("_")

    if name == "":
        name = "dataset_table"

    if name[0].isdigit():
        name = f"t_{name}"

    return name


def is_safe_select_query(sql: str) -> bool:
    """
    Allow only SELECT queries. Block dangerous keywords.
    """
    sql_clean = sql.strip().lower()

    blocked_keywords = [
        "drop", "delete", "update", "insert",
        "alter", "truncate", "create", "grant",
        "revoke", "commit", "rollback"
    ]

    if not sql_clean.startswith("select"):
        return False

    for keyword in blocked_keywords:
        if keyword in sql_clean:
            return False

    return True