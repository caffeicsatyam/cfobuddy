import os
import json
from dotenv import load_dotenv
from langchain_core.tools import tool
from sqlalchemy import create_engine, text, inspect

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))


def get_available_tables() -> dict:
    """Get all tables and their columns from Neon."""
    inspector = inspect(engine)
    tables = {}
    for table_name in inspector.get_table_names():
        # Skip vector store tables
        if "embed" in table_name or "vector" in table_name or "llamaindex" in table_name:
            continue
        columns = [col["name"] for col in inspector.get_columns(table_name)]
        tables[table_name] = columns
    return tables


def format_results(rows, columns) -> str:
    """Format SQL results as readable table."""
    if not rows:
        return "No results found."

    # Header
    col_widths = [max(len(str(col)), max((len(str(row[i])) for row in rows), default=0)) for i, col in enumerate(columns)]
    header = " | ".join(str(col).ljust(col_widths[i]) for i, col in enumerate(columns))
    separator = "-+-".join("-" * w for w in col_widths)
    lines = [header, separator]

    # Rows (limit to 50)
    for row in rows[:50]:
        lines.append(" | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row)))

    if len(rows) > 50:
        lines.append(f"... ({len(rows) - 50} more rows)")

    return "\n".join(lines)


@tool
def sql_query(sql: str) -> str:
    """
    Execute SQL on financial data stored in Neon PostgreSQL for EXACT calculations.
    Use this for: aggregations, averages, sums, counts, filters, rankings, comparisons.
    ALWAYS use this instead of search_financial_docs when math or exact numbers are needed.

    Available tables (auto-detected from your data folder):
    - financialstatements: year, company, category, revenue, net_income, market_cap, etc.
    - cards_data: id, client_id, card_brand, card_type, credit_limit, etc.

    Example queries:
    - SELECT AVG(revenue) FROM financialstatements WHERE category = 'IT'
    - SELECT company, MAX(market_cap_in_b_usd_) FROM financialstatements GROUP BY company
    - SELECT COUNT(*) FROM cards_data WHERE card_brand = 'Visa'
    - SELECT company, revenue FROM financialstatements WHERE year = 2022 ORDER BY revenue DESC LIMIT 5

    Args:
        sql: Valid PostgreSQL SQL query (SELECT only — no INSERT/UPDATE/DELETE)
    """
    # Safety check — only allow SELECT
    sql_clean = sql.strip().upper()
    if not sql_clean.startswith("SELECT") and not sql_clean.startswith("WITH"):
        return "Only SELECT queries are allowed for safety."

    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = result.fetchall()
            columns = list(result.keys())
            return f"Query: {sql}\n\nResults ({len(rows)} rows):\n\n{format_results(rows, columns)}"

    except Exception as e:
        # Try to be helpful about what went wrong
        tables = get_available_tables()
        table_info = "\n".join([f"  - {t}: {', '.join(cols)}" for t, cols in tables.items()])
        return f"SQL Error: {e}\n\nAvailable tables:\n{table_info}"


@tool
def list_tables() -> str:
    """
    List all available database tables and their columns.
    Use this when you need to know what structured data is available for SQL queries.
    """
    try:
        tables = get_available_tables()
        if not tables:
            return "No tables found. Run: python load_data.py"

        result = ["Available tables in Neon DB:\n"]
        for table_name, columns in tables.items():
            result.append(f"📋 {table_name}")
            result.append(f"   Columns: {', '.join(columns)}\n")

        return "\n".join(result)

    except Exception as e:
        return f"Error listing tables: {e}"