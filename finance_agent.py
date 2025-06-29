import os
from groq import Groq
import yfinance as yf
import datetime
import pandas as pd
import json
from scrapeNews import extract_news

def get_Full_ticker(ticker):
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
    return f"The 30-day average for {ticker}: ₹{avg[ticker]:.2f}\nLast closed price: ₹{recent:.2f}"

def analyze_financials(symbol):
    symbol = symbol.upper()
    symbol=get_Full_ticker(symbol)
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




client = Groq(api_key="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")


tools=[
        {
            "type":"function",
            "function":{
                "name":"get_stock_price",
                "description":"Get the stock price of the given stock",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "symbol":{
                            "type":"string",
                            "description":"Fetch real-time stock price by using the ticker symbol. Always use this when the user asks about a stock price."
                        }
                    },
                    "required":["symbol"]
                }
            }
        },

        {
            "type":"function",
            "function":{
                "name":"analyze_financials",
                "description":"Summarize the key financial metrics for a given stock including FCF, Net Income, P/E Ratio, etc.",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "symbol":{
                            "type":"string",
                            "description":"Analyze key financial metrics of a company using its stock ticker. Use this to provide investment insights based on revenue, profit, growth trends and different ratios"
                        }
                    },
                    "required":["symbol"]
                }
            }
        },

    ]


def sentiment_analysis(symbol):
    news = extract_news(symbol)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role":"system",
                "content":"You are a financial news sentiment analyzer and give brief explantion as to how you classified them"
            },
            {
                "role":"user",
                "content":f"""Classify the market sentiment as Neutral,Positive or Negative according to the 

                //{news}//
                Also, briefly explain why.

                When giving the explantions be crisp and to point
                
                Summarize the most influential news item

                Use emojis like ✅ 📈 💰 🚀 🟢 for positive, ❌ ⚠️ 📉 🔻 🔴 for negative and📎 🟡 🤝 for neutral and give good spacing
                
                """
            }
        ],
        
        model="llama3-70b-8192",
        max_tokens=300
    )

    return chat_completion.choices[0].message.content


def classify_levl(user_prompt):
    level_identifier_prompt= f""""
             Classify the user's knowledge as:

            - **Beginner**: Asks basic questions like "Whats the price of the stock",,asks to explain basic finance terms like P/E ratio,free cash flow,Income statement and similar terms and says "what to buy",phrases like "I am new to this","explain in simple terms" and so on.
            
            -**Amateur**: Uses terms like "risk vs return","undervalued","overvalued","Company financials and stability" etc.

            --**Seasoned**: Asks detailed questions based on phrases such as "capital allocation","long term stability of stock","FCF","beta" and similar advanced financial terms and short forms.

            Analyze // {user_prompt} //
            
             Which category does it most closely reflect? Respond only with one of: **beginner**, **amateur**, or **seasoned**.

             If unclear dont make any assumption and carry on

                    """
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role":"system",
                "content":"You classify the level of the investor based on user queries"
            },
            {
                "role":"user",
                "content":level_identifier_prompt
            }
        ],
        
        model="llama3-70b-8192",
        max_tokens=5
    )
    return chat_completion.choices[0].message.content.strip().lower()


def run_finance_agent(user_prompt,conversation_hist):
    level = classify_levl(user_prompt)
    print(len(conversation_hist))
    print(user_prompt)
    conversation_hist=conversation_hist[-3:]
    chat_completion = client.chat.completions.create(
        messages=[
        {    "role":"system",
                "content":f"""
        You are a smart AI finance chatbot.

        The user is a **{level}** investor:
        
        -  Beginner: explain financial terms briefly and clearly.
        -  Amateur: use relevant financial vocabulary, but keep things clear.
        - Seasoned: go deep into financial metrics, use ratios, and be concise.

        Your goal is to analyze the stock data, adapt your tone accordingly, and provide a summary + investment verdict.
        
        - Use good spacing and give section wise content 
        -Please include relevant emojis to make the response more engaging.
            Use emojis like 📈 for growth, 💰 for profits, ⚠️ for risk, ✅ for strong fundamentals, 📉 for decline, and ⭐️ for final verdicts.
            """
            
        },
        *conversation_hist,
        {
                "role":"user",
            "content":user_prompt
    ,
        }
        ],
        model="llama3-70b-8192"
    ,
        tools=tools,
        tool_choice="auto",
        max_completion_tokens=500
    )
    #print(chat_completion.choices[0].message)
    message = chat_completion.choices[0].message
    if message.tool_calls is None:
        return message.content  # This is a true fallback — no tool was ever planned


    tool_outputs = []

    for tool_call in message.tool_calls:
        function_name = tool_call.function.name
        argument = json.loads(tool_call.function.arguments)
        print(function_name)

        if argument['symbol']:
            sentiment = sentiment_analysis(argument['symbol'])
            tool_outputs.append(f"📰 **Market Sentiment Analysis for {argument['symbol']}**:\n{sentiment}")

        
        if function_name=='get_stock_price':
            result = get_stock_price(argument['symbol'])
            tool_outputs.append(f"📈 Stock Price Info:\n{result}")
            
        elif function_name=='analyze_financials':
            summary = analyze_financials(argument['symbol'])
            prompt = f"""
            Here is the financial summary of {argument['symbol']}:

            {summary}

            Give an investment attractiveness score out of 100 and explain briefly.
            - Use `**bold headings**` for sections like Stock Price,Sentiment Analysis,Financial Insights, Verdict, etc.
            "Use emojis like ✅ 📈 💰 🚀 🟢 for positive, ❌ ⚠️ 📉 🔻 🔴 for negative, and 📎 🟡 🤝 for neutral. Add them at the start of bullet points or section headers."
            - Use bullet points `*` or `-` for each fact or insight.
            - Add line breaks between paragraphs for better readability.
            -Please include relevant emojis to make the response more engaging.
            Use emojis like 📈 for growth, 💰 for profits, ⚠️ for risk, ✅ for strong fundamentals, 📉 for decline, and ⭐️ for final verdicts.            

            """
            tool_outputs.append(f"{prompt}")



    final_prompt = "\n\n".join(tool_outputs)

    followup_messages = [
        {
            "role":"system",
            "content": """
            You are a helpful financial assistant. Use clear, engaging, and structured formatting with relevant emojis.

            - Use emojis like ✅ 📈 💰 🚀 🟢 for positive, ❌ ⚠️ 📉 🔻 🔴 for negative, and 📎 🟡 🤝 for neutral.
            - Start section headings and bullet points with appropriate emojis.
            - Add section headers like **Stock Price**, **Market Sentiment**, **Financials**, and **Final Verdict**.
            - Make your response not less than 300 words.
            - When doing sentiment analysis try to explain them in sentences rather than giving short verdicts
            """
        },
       
        {
            "role":"user",
            "content": final_prompt,
        }
    ]


    summary_response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=followup_messages,
            max_tokens=500
        )
    
    assistant_reply= summary_response.choices[0].message.content

    return assistant_reply

# print(run_finance_agent("AAPL stock price",[]))



