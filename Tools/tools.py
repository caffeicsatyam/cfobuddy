import yfinance as yf
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from langchain.agents import create_agent
from Tools.chart_tool.liveChart import plot_stock_trend

search_engine = DuckDuckGoSearchResults()

@tool('stock_summary')
def get_stock_summary(ticker: str) -> str:
    """
    Get financial summary of a stock using its ticker symbol.
    Example: AAPL, MSFT, TCS.NS
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info:
            return "No data found for this ticker."

        data = f"""
            Company: {info.get('longName')}
            Current Price: {info.get('currentPrice')}
            Market Cap: {info.get('marketCap')}
            PE Ratio: {info.get('trailingPE')}
            52 Week High: {info.get('fiftyTwoWeekHigh')}
            52 Week Low: {info.get('fiftyTwoWeekLow')}
            """
        return data

    except Exception as e:
        return f"Error fetching stock data: {str(e)}"
    
@tool('stock_history')
def get_stock_history(ticker: str, period: str = "1mo") -> str:
    """
    Get historical stock price.
    period options: 1d,5d,1mo,6mo,1y,5y and more
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return "No historical data available."

        latest = hist.tail(5)

        return latest.to_string()

    except Exception as e:
        return f"Error fetching history: {str(e)}"
    
@tool("web_search")
def web_search(query: str) -> str:
    """Search the web for recent information."""
    return search_engine.invoke(query)

@tool('stock_data')
def stock_data(company: str) :
    """ Search for the Company stocks"""
    plot_stock_trend


tools = [
    get_stock_summary,
    get_stock_history,
    web_search,
    plot_stock_trend,
    YahooFinanceNewsTool(),
]
