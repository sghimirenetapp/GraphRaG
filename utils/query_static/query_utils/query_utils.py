import sqlparse

def clean_llm_sql(query: str):
    """
    Always use this after calling a SQL Generation Pipeline

    Args:
        query (str): Query Generated from LLM Service
    """
    query = query.split("</s>")[0]
    query = query.strip()
    query = query.rstrip("```")
    query = query.replace("```sql", "")
    query = query.replace("\\", "")
    query = query.split(";")[0]
    # Only use the first statement
    query = sqlparse.parse(query)[0].value
    return query