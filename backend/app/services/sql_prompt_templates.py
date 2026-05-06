def build_sql_prompt(table_name: str, schema_text: str, question: str):
    return f"""
You are a PostgreSQL SQL expert.

You MUST generate only SQL query.
Do NOT explain anything.
Do NOT use markdown.
Do NOT add comments.
Only output the SQL.

Rules:
- Only SELECT queries allowed.
- Do not use INSERT/UPDATE/DELETE/DROP.
- Always query from this dataset table: "{table_name}"
- Use correct column names exactly as provided.
- If question cannot be answered, output:
  SELECT 'NOT_POSSIBLE' as error;

Dataset Table:
{table_name}

Schema:
{schema_text}

User Question:
{question}

SQL:
"""