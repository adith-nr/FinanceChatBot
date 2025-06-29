import yfinance as yf
import json
# Ticker to Sector and Industry
ticker = yf.Ticker('TCS.BO')
info = ticker.info
sector = info.get("sector")
sector=sector.lower()
tech = yf.Sector(sector)
incm_stat=ticker.get_income_stmt(freq='quarterly',pretty=True)
#print(incm_stat)
quarterly_cash_flow = ticker.quarterly_cashflow
latest_column = quarterly_cash_flow.columns[0]
fcf = quarterly_cash_flow.loc["Free Cash Flow", latest_column]
#print(fcf)
# tech = yf.Sector(ticker.info.get('sectorKey'))
# software = yf.Industry(ticker.info.get('industryKey'))

# print(ticker.ticker)
# print(tech)
# prin

def analyze_financials(symbol):
    symbol = symbol.lower()
    ticker = yf.Ticker(symbol)
    info = ticker.info
    quarterly_cash_flow = ticker.quarterly_cashflow
    latest_column=quarterly_cash_flow.columns[0]

    keys = [
    "Free Cash Flow",
    "Capital Expenditure",
    "Operating Cash Flow",
    "Net Income From Continuing Operations"
    ]
    summary={}
    for key in keys:
        if key in quarterly_cash_flow.index:
            value = quarterly_cash_flow.loc[key,latest_column]
            summary[key]=value
        else:
            summary[key] = "N/A"

    summary['Market Cap']=info.get("marketCap")
    summary['P/E Ratio'] = info.get("trailingPE")
    lines=[]
    for key,value in summary.items():
        lines.append(f"{key}: Rupees {value:.0f}")
    formatted = "\n".join(lines)
    return formatted

#print(analyze_financials("TCS.BO"))




