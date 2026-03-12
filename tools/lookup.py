import os
import glob
import pandas as pd
from langchain_core.tools import tool

def load_dataframes(folder="data"):
    dataframes = {}
    for filepath in glob.glob(os.path.join(folder, "*.csv")):
        filename = os.path.basename(filepath)
        try:
            df = pd.read_csv(filepath)
            df.columns = df.columns.str.strip().str.lower()
            dataframes[filename] = df
        except Exception as e:
            print(f"Warning: Could not load {filename}: {e}")
    return dataframes

dataframes = load_dataframes()

@tool
def exact_lookup(file_name: str, column: str, value: str) -> str:
    """
    Perform an exact lookup in a CSV file by matching a column to a value.
    Use this for specific ID lookups, account numbers, card numbers, client IDs etc.

    Args:
        file_name: CSV filename e.g. 'cards_data.csv'
        column: column name to search in e.g. 'client_id', 'id', 'card_number'
        value: exact value to match e.g. '825'
    """
    if file_name not in dataframes:
        available = ", ".join(dataframes.keys())
        return f"File '{file_name}' not found. Available files: {available}"

    df = dataframes[file_name]
    col = column.strip().lower()

    if col not in df.columns:
        available = ", ".join(df.columns.tolist())
        return f"Column '{column}' not found in {file_name}. Available columns: {available}"

    matches = df[df[col].astype(str).str.strip() == str(value).strip()]

    if matches.empty:
        return f"No records found in {file_name} where {column} = {value}"

    results = [row.to_string() for _, row in matches.iterrows()]
    return f"[Source: {file_name}]\nFound {len(matches)} record(s):\n\n" + "\n\n---\n\n".join(results)


@tool
def list_available_files() -> str:
    """List all available files in the data folder including CSVs, PDFs, Excel and Word docs."""
    DATA_FOLDER = "data"
    SUPPORTED = {".csv", ".pdf", ".xlsx", ".xls", ".docx"}
    result = []

    all_files = [
        f for f in os.listdir(DATA_FOLDER)
        if os.path.splitext(f)[1].lower() in SUPPORTED
    ]

    if not all_files:
        return "No files found in data folder."

    for filename in all_files:
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".csv":
            if filename in dataframes:
                cols = ", ".join(dataframes[filename].columns.tolist())
                result.append(f"CSV: {filename} — columns: {cols}")
            else:
                result.append(f"CSV: {filename} — (not loaded)")
        elif ext == ".pdf":
            result.append(f"PDF: {filename} — use search_financial_docs to query")
        elif ext in {".xlsx", ".xls"}:
            result.append(f"Excel: {filename} — use search_financial_docs to query")
        elif ext == ".docx":
            result.append(f"Word: {filename} — use search_financial_docs to query")

    return "\n".join(result)