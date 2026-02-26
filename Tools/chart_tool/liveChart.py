import yfinance as yf
import matplotlib.pyplot as plt
from langchain.tools import tool
import pandas as pd

@tool
def plot_stock_trend(ticker: str, period: str = "6mo") -> str:
    """
    Generate a stock price trend chart.
    period: 1mo, 3mo, 6mo, 1y, 5y
    """

    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)

    if hist.empty:
        return "No data available."

    plt.figure()
    plt.plot(hist.index, hist["Close"])
    plt.title(f"{ticker} Price Trend ({period})")
    plt.xlabel("Date")
    plt.ylabel("Price")

    file_path = f"{ticker}_trend.png"
    plt.savefig(file_path, bbox_inches="tight")
    plt.close()

    return f"Chart saved as {file_path}"


plot_stock_trend.invoke({"ticker": "AAPL", "period": "6mo"})