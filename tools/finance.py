import os
from typing import Union

import yfinance as yf
from dotenv import load_dotenv
from langchain_core.tools import tool
from twelvedata import TDClient

load_dotenv()

TD_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
_td_client: TDClient | None = None


def get_td_client() -> TDClient:
    global _td_client

    if _td_client is not None:
        return _td_client

    if not TD_API_KEY:
        raise RuntimeError("TWELVE_DATA_API_KEY is not set")

    _td_client = TDClient(apikey=TD_API_KEY)
    return _td_client


def format_number(value) -> str:
    if value is None:
        return "N/A"
    try:
        value = float(value)
        if abs(value) >= 1_000_000_000:
            return f"${value / 1_000_000_000:.2f}B"
        if abs(value) >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"
        return f"${value:,.2f}"
    except Exception:
        return str(value)


def _yf_quote(symbol: str) -> str:
    info = yf.Ticker(symbol).info
    if not info:
        return f"No data found for {symbol}."
    return f"""
    {info.get('longName', symbol)} ({symbol})
Price:        ${info.get('currentPrice', 'N/A')}
Change:       {info.get('regularMarketChange', 'N/A')} ({info.get('regularMarketChangePercent', 'N/A')}%)
Open/High/Low: ${info.get('open', 'N/A')} / ${info.get('dayHigh', 'N/A')} / ${info.get('dayLow', 'N/A')}
Volume:       {info.get('volume', 'N/A')}
Market Cap:   {format_number(info.get('marketCap'))}
PE Ratio:     {info.get('trailingPE', 'N/A')}  |  EPS: {info.get('trailingEps', 'N/A')}
52W High/Low: ${info.get('fiftyTwoWeekHigh', 'N/A')} / ${info.get('fiftyTwoWeekLow', 'N/A')}
Exchange:     {info.get('exchange', 'N/A')}""".strip()


def _yf_income(symbol: str, limit: int) -> str:
    df = yf.Ticker(symbol).financials
    if df is None or df.empty:
        return f"No income statement found for {symbol}."
    result = [f"Income Statement - {symbol}"]
    for col in list(df.columns)[:limit]:
        result.append(f"""
Period:        {str(col)[:10]}
Revenue:       {format_number(df[col].get('Total Revenue'))}
Gross Profit:  {format_number(df[col].get('Gross Profit'))}
Operating Inc: {format_number(df[col].get('Operating Income'))}
Net Income:    {format_number(df[col].get('Net Income'))}
EBITDA:        {format_number(df[col].get('EBITDA'))}""")
    return "\n---".join(result)


def _yf_balance(symbol: str, limit: int) -> str:
    df = yf.Ticker(symbol).balance_sheet
    if df is None or df.empty:
        return f"No balance sheet found for {symbol}."
    result = [f"Balance Sheet - {symbol}"]
    for col in list(df.columns)[:limit]:
        result.append(f"""
Period:             {str(col)[:10]}
Total Assets:       {format_number(df[col].get('Total Assets'))}
Total Liabilities:  {format_number(df[col].get('Total Liabilities Net Minority Interest'))}
Total Equity:       {format_number(df[col].get('Stockholders Equity'))}
Cash & Equiv:       {format_number(df[col].get('Cash And Cash Equivalents'))}
Total Debt:         {format_number(df[col].get('Total Debt'))}""")
    return "\n---".join(result)


def _yf_cashflow(symbol: str, limit: int) -> str:
    df = yf.Ticker(symbol).cashflow
    if df is None or df.empty:
        return f"No cash flow found for {symbol}."
    result = [f"Cash Flow - {symbol}"]
    for col in list(df.columns)[:limit]:
        result.append(f"""
Period:         {str(col)[:10]}
Operating CF:   {format_number(df[col].get('Operating Cash Flow'))}
Investing CF:   {format_number(df[col].get('Investing Cash Flow'))}
Financing CF:   {format_number(df[col].get('Financing Cash Flow'))}
Free CF:        {format_number(df[col].get('Free Cash Flow'))}
CapEx:          {format_number(df[col].get('Capital Expenditure'))}""")
    return "\n---".join(result)


def _yf_metrics(symbol: str) -> str:
    info = yf.Ticker(symbol).info
    if not info:
        return f"No metrics found for {symbol}."
    return f"""
    Key Metrics - {symbol}
    PE Ratio:       {info.get('trailingPE', 'N/A')}
    Forward PE:     {info.get('forwardPE', 'N/A')}
    PB Ratio:       {info.get('priceToBook', 'N/A')}
    EV/EBITDA:      {info.get('enterpriseToEbitda', 'N/A')}
    ROE:            {info.get('returnOnEquity', 'N/A')}
    ROA:            {info.get('returnOnAssets', 'N/A')}
    Net Margin:     {info.get('profitMargins', 'N/A')}
    Current Ratio:  {info.get('currentRatio', 'N/A')}
    Debt/Equity:    {info.get('debtToEquity', 'N/A')}
    Dividend Yield: {info.get('dividendYield', 'N/A')}""".strip()


def _yf_ratings(symbol: str) -> str:
    try:
        recs = yf.Ticker(symbol).recommendations
        if recs is None or recs.empty:
            raise ValueError("empty")
        result = [f"Analyst Ratings - {symbol}"]
        for _, row in recs.tail(5).iterrows():
            result.append(
                f"{str(row.name)[:10]} | {row.get('Firm', 'N/A')} | "
                f"{row.get('To Grade', 'N/A')} (from {row.get('From Grade', 'N/A')})"
            )
        return "\n".join(result)
    except Exception:
        return f"No analyst ratings available for {symbol}."


def _yf_news(symbol: str, limit: int) -> str:
    news = yf.Ticker(symbol).news
    if not news:
        return f"No news found for {symbol}."
    result = [f"Latest News - {symbol}"]
    for article in news[:limit]:
        content = article.get("content", {})
        title = content.get("title", "No title")
        url = content.get("canonicalUrl", {}).get("url", "")
        date = content.get("pubDate", "")[:10]
        result.append(f"- [{date}] {title}\n  {url}")
    return "\n\n".join(result)


def _yf_profile(symbol: str) -> str:
    info = yf.Ticker(symbol).info
    if not info:
        return f"No profile found for {symbol}."
    return f"""
    {info.get('longName', symbol)} ({symbol})
Sector:     {info.get('sector', 'N/A')}  |  Industry: {info.get('industry', 'N/A')}
Exchange:   {info.get('exchange', 'N/A')}  |  Country: {info.get('country', 'N/A')}
Employees:  {info.get('fullTimeEmployees', 'N/A')}
Market Cap: {format_number(info.get('marketCap'))}
Website:    {info.get('website', 'N/A')}

{info.get('longBusinessSummary', 'N/A')[:400]}...""".strip()


def _td_price_history(symbol: str, interval: str = "1day", limit: int = 30) -> str:
    try:
        ts = get_td_client().time_series(
            symbol=symbol,
            interval=interval,
            outputsize=limit,
        ).as_json()
        if not ts:
            return f"No price history found for {symbol}."
        result = [f"Price History - {symbol} ({interval})"]
        for bar in ts[:10]:
            result.append(
                f"{bar.get('datetime')} | O: {bar.get('open')} "
                f"H: {bar.get('high')} L: {bar.get('low')} "
                f"C: {bar.get('close')} V: {bar.get('volume', 'N/A')}"
            )
        return "\n".join(result)
    except Exception as exc:
        return f"Twelve Data error: {exc}"


def _td_quote(symbol: str) -> str:
    try:
        quote = get_td_client().quote(symbol=symbol).as_json()
        if not quote:
            return f"No quote found for {symbol}."
        return f"""
    {quote.get('name', symbol)} ({symbol}) - Twelve Data
Price:         ${quote.get('close', 'N/A')}
Change:        {quote.get('change', 'N/A')} ({quote.get('percent_change', 'N/A')}%)
Open/High/Low: ${quote.get('open', 'N/A')} / ${quote.get('high', 'N/A')} / ${quote.get('low', 'N/A')}
Volume:        {quote.get('volume', 'N/A')}
52W High/Low:  ${quote.get('fifty_two_week', {}).get('high', 'N/A')} / ${quote.get('fifty_two_week', {}).get('low', 'N/A')}
Market Open:   {quote.get('is_market_open', 'N/A')}""".strip()
    except Exception as exc:
        return f"Twelve Data error: {exc}"


def _best_quote(symbol: str) -> str:
    try:
        result = _yf_quote(symbol)
        if result and "No data found" not in result:
            return result
    except Exception:
        pass
    return _td_quote(symbol)


HANDLERS = {
    "quote": lambda s, p, l: _best_quote(s),
    "income": lambda s, p, l: _yf_income(s, l),
    "balance": lambda s, p, l: _yf_balance(s, l),
    "cashflow": lambda s, p, l: _yf_cashflow(s, l),
    "metrics": lambda s, p, l: _yf_metrics(s),
    "ratings": lambda s, p, l: _yf_ratings(s),
    "news": lambda s, p, l: _yf_news(s, l),
    "profile": lambda s, p, l: _yf_profile(s),
    "history": lambda s, p, l: _td_price_history(s, limit=l),
    "realtime": lambda s, p, l: _td_quote(s),
}


@tool
def get_financial_data(
    symbol: str,
    data_type: str,
    period: str = "annual",
    limit: Union[int, str] = 3,
) -> str:
    """
    Fetch any financial data for a publicly traded company.
    Uses yfinance (fundamentals) and Twelve Data (price history & real-time).
    """

    symbol = symbol.upper().strip()
    data_type = data_type.lower().strip()
    limit = int(limit)
    period = str(period)

    if data_type not in HANDLERS:
        return f"Unknown data_type '{data_type}'. Valid options: {', '.join(HANDLERS.keys())}"

    try:
        return HANDLERS[data_type](symbol, period, limit)
    except Exception as exc:
        return f"Unable to fetch {data_type} data for {symbol}: {exc}"
