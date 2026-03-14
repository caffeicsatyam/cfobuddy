import os
import requests
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

FMP_API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/api/v3"


def fmp_get(endpoint: str, params: dict = {}) -> dict | list | str:
    """Base FMP API caller with error handling."""
    params["apikey"] = FMP_API_KEY
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and "Error Message" in data:
            return f"FMP Error: {data['Error Message']}"
        return data
    except requests.exceptions.Timeout:
        return "FMP API request timed out."
    except requests.exceptions.RequestException as e:
        return f"FMP API request failed: {e}"


def format_number(value) -> str:
    if value is None:
        return "N/A"
    try:
        value = float(value)
        if abs(value) >= 1_000_000_000:
            return f"${value / 1_000_000_000:.2f}B"
        elif abs(value) >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"
        else:
            return f"${value:,.2f}"
    except:
        return str(value)


def _quote(symbol, p, l):
    data = fmp_get(f"quote/{symbol}")
    if isinstance(data, str): return data
    if not data: return f"No quote data found for {symbol}."
    q = data[0]
    return f"""📈 {q.get('name')} ({q.get('symbol')})
Price:        ${q.get('price')}
Change:       {q.get('change')} ({q.get('changesPercentage')}%)
Open:         ${q.get('open')}  |  High: ${q.get('dayHigh')}  |  Low: ${q.get('dayLow')}
Volume:       {q.get('volume'):,}
Market Cap:   {format_number(q.get('marketCap'))}
PE Ratio:     {q.get('pe')}  |  EPS: {q.get('eps')}
52W High:     ${q.get('yearHigh')}  |  52W Low: ${q.get('yearLow')}
Exchange:     {q.get('exchange')}""".strip()


def _income(symbol, period, limit):
    data = fmp_get(f"income-statement/{symbol}", {"period": period, "limit": limit})
    if isinstance(data, str): return data
    if not data: return f"No income statement found for {symbol}."
    result = [f"📊 Income Statement — {symbol} ({period})"]
    for e in data:
        result.append(f"""
Period:        {e.get('date')} ({e.get('period')})
Revenue:       {format_number(e.get('revenue'))}
Gross Profit:  {format_number(e.get('grossProfit'))}
Operating Inc: {format_number(e.get('operatingIncome'))}
Net Income:    {format_number(e.get('netIncome'))}
EPS:           {e.get('eps')}
EBITDA:        {format_number(e.get('ebitda'))}""")
    return "\n---".join(result)


def _balance(symbol, period, limit):
    data = fmp_get(f"balance-sheet-statement/{symbol}", {"period": period, "limit": limit})
    if isinstance(data, str): return data
    if not data: return f"No balance sheet found for {symbol}."
    result = [f" Balance Sheet — {symbol} ({period})"]
    for e in data:
        result.append(f"""
Period:             {e.get('date')}
Total Assets:       {format_number(e.get('totalAssets'))}
Total Liabilities:  {format_number(e.get('totalLiabilities'))}
Total Equity:       {format_number(e.get('totalStockholdersEquity'))}
Cash & Equiv:       {format_number(e.get('cashAndCashEquivalents'))}
Total Debt:         {format_number(e.get('totalDebt'))}""")
    return "\n---".join(result)


def _cashflow(symbol, period, limit):
    data = fmp_get(f"cash-flow-statement/{symbol}", {"period": period, "limit": limit})
    if isinstance(data, str): return data
    if not data: return f"No cash flow found for {symbol}."
    result = [f" Cash Flow — {symbol} ({period})"]
    for e in data:
        result.append(f"""
Period:         {e.get('date')}
Operating CF:   {format_number(e.get('operatingCashFlow'))}
Investing CF:   {format_number(e.get('investingCashFlow'))}
Financing CF:   {format_number(e.get('financingCashFlow'))}
Free CF:        {format_number(e.get('freeCashFlow'))}
CapEx:          {format_number(e.get('capitalExpenditure'))}""")
    return "\n---".join(result)


def _metrics(symbol, period, l):
    data = fmp_get(f"key-metrics/{symbol}", {"period": period, "limit": 1})
    if isinstance(data, str): return data
    if not data: return f"No key metrics found for {symbol}."
    m = data[0]
    return f""" Key Metrics — {symbol} ({m.get('date')})
PE Ratio:       {m.get('peRatio')}
PB Ratio:       {m.get('pbRatio')}
EV/EBITDA:      {m.get('enterpriseValueOverEBITDA')}
ROE:            {m.get('roe')}
ROA:            {m.get('returnOnTangibleAssets')}
Net Margin:     {m.get('netProfitMargin')}
Current Ratio:  {m.get('currentRatio')}
Debt/Equity:    {m.get('debtToEquity')}
FCF/Share:      {m.get('freeCashFlowPerShare')}
Book Value:     {m.get('bookValuePerShare')}""".strip()


def _ratings(symbol, p, l):
    data = fmp_get(f"analyst-stock-recommendations/{symbol}", {"limit": 5})
    if isinstance(data, str): return data
    if not data: return f"No analyst ratings found for {symbol}."
    result = [f" Analyst Ratings — {symbol}"]
    for e in data[:5]:
        result.append(
            f"{e.get('date')} | Buy: {e.get('analystRatingsBuy')} | "
            f"Hold: {e.get('analystRatingsHold')} | Sell: {e.get('analystRatingsSell')} | "
            f"Strong Buy: {e.get('analystRatingsStrongBuy')} | "
            f"Strong Sell: {e.get('analystRatingsStrongSell')}"
        )
    return "\n".join(result)


def _news(symbol, p, limit):
    data = fmp_get("stock_news", {"tickers": symbol, "limit": limit})
    if isinstance(data, str): return data
    if not data: return f"No news found for {symbol}."
    result = [f" Latest News — {symbol}"]
    for a in data:
        result.append(f"• [{a.get('publishedDate', '')[:10]}] {a.get('title')}\n  {a.get('url')}")
    return "\n\n".join(result)


def _profile(symbol, p, l):
    data = fmp_get(f"profile/{symbol}")
    if isinstance(data, str): return data
    if not data: return f"No profile found for {symbol}."
    p = data[0]
    return f""" {p.get('companyName')} ({p.get('symbol')})
Sector:     {p.get('sector')}  |  Industry: {p.get('industry')}
Exchange:   {p.get('exchangeShortName')}  |  Country: {p.get('country')}
CEO:        {p.get('ceo')}
Employees:  {p.get('fullTimeEmployees')}
Market Cap: {format_number(p.get('mktCap'))}
IPO Date:   {p.get('ipoDate')}
Website:    {p.get('website')}

{p.get('description', 'N/A')[:400]}...""".strip()


# ==========================
# SINGLE UNIFIED TOOL
# ==========================

HANDLERS = {
    "quote":    _quote,
    "income":   _income,
    "balance":  _balance,
    "cashflow": _cashflow,
    "metrics":  _metrics,
    "ratings":  _ratings,
    "news":     _news,
    "profile":  _profile,
}

@tool
def get_financial_data(symbol: str, data_type: str, period: str = "annual", limit: int = 3) -> str:
    """
    Fetch any financial data for a publicly traded company using FMP API.
    Use this for ANY question about stocks, company financials, or market data.

    Args:
        symbol: Stock ticker e.g. 'AAPL', 'MSFT', 'GOOGL', 'TSLA'
        data_type: Type of data to fetch. Must be one of:
            'quote'    — live price, change, volume, market cap, PE, EPS
            'income'   — revenue, gross profit, net income, EPS, EBITDA
            'balance'  — total assets, liabilities, equity, cash, debt
            'cashflow' — operating, investing, financing, free cash flow
            'metrics'  — PE, PB, ROE, ROA, margins, current ratio, debt/equity
            'ratings'  — analyst buy/hold/sell recommendations
            'news'     — latest news articles
            'profile'  — company overview, sector, CEO, employees
        period: 'annual' or 'quarter' (default: 'annual')
        limit: Number of periods to return (default: 3)
    """
    symbol = symbol.upper().strip()
    data_type = data_type.lower().strip()

    if data_type not in HANDLERS:
        return (
            f"Unknown data_type '{data_type}'. "
            f"Valid options: {', '.join(HANDLERS.keys())}"
        )

    return HANDLERS[data_type](symbol, period, limit)