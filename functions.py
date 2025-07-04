import yfinance as yf
import json
from tickerMap import nse_sector_map,bse_sector_map,us_sector_map,company_ticker_map
import datetime
from difflib import get_close_matches

def get_Full_ticker(ticker):
    if ticker.lower() in company_ticker_map:
        return company_ticker_map[ticker.lower()]
    
    matches = get_close_matches(ticker.lower(), company_ticker_map.keys(), n=1, cutoff=0.6)
    if matches:
        return company_ticker_map[matches[0]]

    today_price = yf.Ticker(ticker).history(period="1d")
    if today_price.empty:
        for suffix in [".NS",".BO"]:
            full_ticker = ticker+suffix
            data = yf.Ticker(full_ticker).history(period="1d")
            if not data.empty:
                ticker = full_ticker
                break
    else:
        return ticker
    
       
    today_price = yf.Ticker(ticker).history(period="1d")
    if today_price.empty:
        return None
    else:
        return ticker


def get_stock_price(symbol):
    ticker = symbol.upper()
    end_date = datetime.date.today()
    start_date = end_date-datetime.timedelta(days=30)
    
    ticker = get_Full_ticker(ticker)
       
    today_price = yf.Ticker(ticker).history(period="1d")
   
    data = yf.download(ticker,start=start_date,end=end_date,auto_adjust=True, progress=False)
   
    close_prices=data['Close']
    avg = close_prices.mean()
    
    recent =today_price['Close'].iloc[-1]
    return f"The 30-day average for {ticker}: {avg[ticker]:.2f}\nLast closed price: {recent:.2f}"

def analyze_financials(symbol):
    symbol = symbol.upper()
    symbol = get_Full_ticker(symbol)
    ticker = yf.Ticker(symbol)
    info = ticker.info

    try:
        quarterly_cash_flow = ticker.quarterly_cashflow
        if quarterly_cash_flow.empty:
            raise ValueError("Empty cash flow data.")

        latest_column = quarterly_cash_flow.columns[0]

        keys = [
            "Free Cash Flow",
            "Capital Expenditure",
            "Operating Cash Flow",
            "Net Income From Continuing Operations"
        ]

        cash_summary = {}
        for key in keys:
            if key in quarterly_cash_flow.index:
                cash_summary[key] = quarterly_cash_flow.loc[key, latest_column]
            else:
                cash_summary[key] = "N/A"
    except Exception as e:
        cash_summary = {k: "N/A" for k in [
            "Free Cash Flow",
            "Capital Expenditure",
            "Operating Cash Flow",
            "Net Income From Continuing Operations"
        ]}

    valuation_summary = {
        "Market Cap": f"{info.get('marketCap', 0):,}",
        "P/E Ratio": info.get("trailingPE", "N/A"),
        "Profit Margins": f"{info.get('profitMargins', 0) * 100:.2f}%" if info.get("profitMargins") else "N/A",
        "Gross Margin": f"{info.get('grossMargins', 0) * 100:.2f}%" if info.get("grossMargins") else "N/A",
        "Revenue Growth": f"{info.get('revenueGrowth', 0) * 100:.2f}%" if info.get("revenueGrowth") else "N/A",
        "Earnings Growth": f"{info.get('earningsGrowth', 0) * 100:.2f}%" if info.get("earningsGrowth") else "N/A",
        "Return on Equity (ROE)": f"{info.get('returnOnEquity', 0) * 100:.2f}%" if info.get("returnOnEquity") else "N/A",
        "Return on Assets (ROA)": f"{info.get('returnOnAssets', 0) * 100:.2f}%" if info.get("returnOnAssets") else "N/A",
        "Free Cash Flow": f"{info.get('freeCashflow', 0):,}",
        "Operating Cash Flow": f"{info.get('operatingCashflow', 0):,}",
        "Debt to Equity": info.get("debtToEquity", "N/A"),
        "Dividend Rate": f"{info.get('dividendRate', 'N/A')}",
        "Dividend Yield": f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get("dividendYield") else "N/A",
        "Payout Ratio": info.get("payoutRatio", "N/A"),
        "52 Week High": f"{info.get('fiftyTwoWeekHigh', 'N/A')}",
        "52 Week Low": f"{info.get('fiftyTwoWeekLow', 'N/A')}",
        "Target Price": f"{info.get('targetMeanPrice', 'N/A')} (High: {info.get('targetHighPrice', 'N/A')} | Low: {info.get('targetLowPrice', 'N/A')})",
        "Analyst Rating": info.get("averageAnalystRating", "N/A"),
        "Recommendation": info.get("recommendationKey", "N/A")
    }

    # Format output
    lines = ["📊 **Financial Overview**\n"]

    lines.append("**💰 Cash Flow Metrics:**")
    for key, val in cash_summary.items():
        formatted = f"{val:,.0f}" if isinstance(val, (int, float)) else val
        lines.append(f"- {key}: {formatted}")

    lines.append("\n**📈 Valuation & Ratios:**")
    for key, val in valuation_summary.items():
        lines.append(f"- {key}: {val}")

    return "\n".join(lines)

#print(analyze_financials("INFY.NS"))


def analyze_sector(identifier,sector):
    sector_name = sector
    top_comp = []
    if(identifier!=""):
        identifier=get_Full_ticker(identifier)
    # Check if identifier looks like a ticker (e.g., "TCS.NS", "AAPL")
    if "." in identifier or identifier.isupper():
        # Treat as ticker
        ticker_obj = yf.Ticker(identifier)
        info = ticker_obj.info
        sector_name = info.get("sector", "").lower()

        # Determine exchange
        if '.' in identifier:
            exchange = identifier.split('.')[1].upper()
        else:
            exchange = 'US'

        if exchange == 'NS':
            top_comp = nse_sector_map.get(sector_name, [])
        elif exchange == 'BO':
            top_comp = bse_sector_map.get(sector_name, [])
        else:
            top_comp = us_sector_map.get(sector_name, [])

    else:
        
        sector_name = sector.lower()
        top_comp = (
            nse_sector_map.get(sector_name)
            or bse_sector_map.get(sector_name)
            or us_sector_map.get(sector_name)
            or []
        )

    # Analyze each company in the sector
    sector_analysis = []
    for comp in top_comp:
        try:
            summary = analyze_financials(comp)
            sector_analysis.append(f"📊 **{comp}**\n{summary}\n")
        except Exception as e:
            sector_analysis.append(f"⚠️ Could not analyze {comp}: {e}")

    if not sector_analysis:
        return f"❌ No companies found for sector `{sector_name}`."

    return f"🏭 **Sector Analysis: {sector_name.title()}**\n\n" + "\n".join(sector_analysis)



#print(analyze_sector("tcs",""))

    


