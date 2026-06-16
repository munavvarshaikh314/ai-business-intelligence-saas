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
    import re
    sql_clean = sql.rstrip(";").strip().lower()
    if not (sql_clean.startswith("select") or sql_clean.startswith("with")):
        return False
    blocked = ["drop", "delete", "update", "insert", "alter", "grant", "revoke"]
    for keyword in blocked:
        if re.search(rf"\b{keyword}\b", sql_clean):
            return False
    return True
