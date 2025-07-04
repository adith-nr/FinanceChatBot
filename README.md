# 💼 FinanceBot – AI-Powered Stock Market Advisor

**FinanceBot** is an AI-powered financial assistant that provides stock analysis using real-time price data, financial metrics, and sentiment from news articles. It uses Groq's `llama3-70b` model for reasoning and LangChain-style tool invocation to perform structured financial evaluation. Built for investors of all levels — beginner to seasoned — it gives data-backed insights and final investment verdicts.


---

## 🧠 Architecture Overview

The workflow of FinanceBot follows a modular toolchain:

1. **Ticker Resolver**: Extracts and corrects stock tickers from user queries (e.g., maps "ICICI" → `ICICIBANK.NS`).
2. **Price Fetcher**: Pulls latest and 30-day average stock prices using `yfinance`.
3. **News Sentiment Analyzer**: Scrapes and summarizes recent news to classify sentiment as 📈 Positive, 📉 Negative, or 📎 Neutral.
4. **Financial Analyzer**: Gathers Free Cash Flow, P/E Ratio, ROE, margins, and more.
5. **Sector Comparator** *(Optional)*: Evaluates stock performance vs. peers in the same sector.
6. **Report Generator**: Combines all components into a structured, emoji-rich investment summary with a ⭐ Final Verdict.

---

## ⚙️ Features

- 📈 Fetches stock price & trend analysis (e.g., 30-day average)
- 🧾 Summarizes financial fundamentals (FCF, ROE, Margins, P/E, etc.)
- 📰 Classifies sentiment using news headlines + Groq-powered reasoning
- 📊 Adds sector-level comparison if needed
- 🗂️ Formats response with structured headings and emojis

---



