from tools.chart import generate_chart
from tools.search import search_financial_docs
from tools.lookup import exact_lookup, list_available_files
from tools.web_search import web_search
from tools.finance import get_financial_data
from tools.sql import sql_query, list_tables

all_tools = [
    search_financial_docs,      # semantic search over PDFs/docs
    exact_lookup,               # exact CSV row lookup
    list_available_files,       # list files
    web_search,                     # web search for news, stock prices, etc.
    get_financial_data,         # live market data
    sql_query,                  # exact SQL on Neon
    list_tables,                # list DB tables
    generate_chart              # generate charts from data
]