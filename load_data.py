import os
import glob
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from cfobuddy_logging import configure_logging

load_dotenv()
logger = configure_logging()

DATABASE_URL = os.getenv("DATABASE_URL")
DATA_FOLDER = "data"


def sanitize_table_name(filename: str) -> str:
    """Convert filename to valid PostgreSQL table name."""
    name = os.path.splitext(filename)[0]
    name = name.lower()
    name = name.replace(" ", "_").replace("-", "_").replace(".", "_")
    return name


def load_csvs_to_neon():
    engine = create_engine(DATABASE_URL)

    csv_files = glob.glob(os.path.join(DATA_FOLDER, "*.csv"))

    if not csv_files:
        logger.warning("No CSV files found in '%s/'", DATA_FOLDER)
        return

    logger.info("Found %d CSV files", len(csv_files))
    loaded_tables = []

    for filepath in csv_files:
        filename = os.path.basename(filepath)
        table_name = sanitize_table_name(filename)

        try:
            df = pd.read_csv(filepath)

            # Clean column names
            df.columns = (
                df.columns
                .str.strip()
                .str.lower()
                .str.replace(" ", "_")
                .str.replace(r"[^\w]", "_", regex=True)
            )

            # Clean currency values before loading
            for col in df.columns:
                if df[col].dtype == object:
                    cleaned = df[col].str.replace(r'[\$,]', '', regex=True)
                    try:
                        df[col] = pd.to_numeric(cleaned)
                    except Exception:
                        pass

            df.to_sql(
                table_name,
                engine,
                if_exists="replace",
                index=False
            )

            loaded_tables.append(table_name)
            logger.info(
                "Loaded '%s' → table '%s' | rows=%d | cols=%s",
                filename, table_name, len(df), ', '.join(df.columns.tolist())
            )

        except Exception as e:
            logger.error("Failed to load '%s' | error=%s", filename, str(e))

    logger.info("Loaded %d tables into Neon: %s", len(loaded_tables), loaded_tables)
    logger.info("CFOBuddy can now run exact SQL queries on your data")


if __name__ == "__main__":
    load_csvs_to_neon()