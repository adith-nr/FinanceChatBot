import os
from groq import Groq
import yfinance as yf
import datetime
import pandas as pd
import json
from dotenv import load_dotenv
load_dotenv()
from scrapeNews import extract_news
from tickerMap import company_ticker_map
from functions import analyze_financials,analyze_sector,get_Full_ticker,get_stock_price



client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


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
        {
                "type": "function",
                "function": {
                    "name": "analyze_sector",
                    "description": "Analyze the sector by inferring it from a stock ticker (e.g., 'TCS sector analysis','Tell me how the sector related to CIPLA is doing ').",

                    "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                        "type": "string",
                        "description": "A stock ticker (e.g., TCS.NS or AAPL). If provided, the sector will be inferred from this ticker."
                        },
                        "sector": {
                        "type": "string",
                        "description": "The name of the sector (e.g., 'it', 'pharma', 'banking'). If no ticker is provided, this will be used directly."
                        }
                    },
                    "required": []
                }
            }
        }

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


# def run_finance_agent(user_prompt,conversation_hist):
#     level = classify_levl(user_prompt)
#     print(len(conversation_hist))
#     sector_analysis_added = False

#     print(user_prompt)
#     conversation_hist=conversation_hist[-3:]
#     chat_completion = client.chat.completions.create(
#         messages=[
#         {    "role":"system",
#                 "content":f"""
#         You are a smart AI finance chatbot.

#         The user is a **{level}** investor:
        
#         -  Beginner: explain financial terms briefly and clearly.
#         -  Amateur: use relevant financial vocabulary, but keep things clear.
#         - Seasoned: go deep into financial metrics, use ratios, and be concise.

#         Your goal is to analyze the stock data, adapt your tone accordingly, and provide a summary + investment verdict.
        
#         - Use good spacing and give section wise content 
#         -Please include relevant emojis to make the response more engaging.
#             Use emojis like 📈 for growth, 💰 for profits, ⚠️ for risk, ✅ for strong fundamentals, 📉 for decline, and ⭐️ for final verdicts.
#             """
            
#         },
#         *conversation_hist,
#         {
#                 "role":"user",
#             "content":user_prompt
#     ,
#         }
#         ],
#         model="llama3-70b-8192"
#     ,
#         tools=tools,
#         tool_choice="auto",
#         max_completion_tokens=500
#     )
#     #print(chat_completion.choices[0].message)
#     message = chat_completion.choices[0].message
#     if message.tool_calls is None:
#         return message.content  # This is a true fallback — no tool was ever planned


#     tool_outputs = []
#     sentiment_added = False


#     for tool_call in message.tool_calls:
#         function_name = tool_call.function.name
#         argument = json.loads(tool_call.function.arguments)
#         print(function_name)

#         if argument.get('symbol') and not sentiment_added:
#             sentiment = sentiment_analysis(argument['symbol'])
#             #print(sentiment)
#             tool_outputs.append(f"📰 **Market Sentiment Analysis for {argument['symbol']}**:\n{sentiment}")
#             sentiment_added=True

        
#         if function_name=='get_stock_price':
#             result = get_stock_price(argument['symbol'])
#             tool_outputs.append(f"📈 Stock Price Info:\n{result}")
#             print(result)
            
#         elif function_name=='analyze_financials':
#             summary = analyze_financials(argument['symbol'])
#             prompt = f"""
#             Here is the financial summary of {argument['symbol']}:

#             {summary}

#             Give an investment attractiveness score out of 100 and explain briefly.
#             - Use `**bold headings**` for sections like Stock Price,Sentiment Analysis,Financial Insights, Verdict, etc.
#             "Use emojis like ✅ 📈 💰 🚀 🟢 for positive, ❌ ⚠️ 📉 🔻 🔴 for negative, and 📎 🟡 🤝 for neutral. Add them at the start of bullet points or section headers."
#             - Use bullet points `*` or `-` for each fact or insight.
#             - Add line breaks between paragraphs for better readability.
#             -Please include relevant emojis to make the response more engaging.
#             Use emojis like 📈 for growth, 💰 for profits, ⚠️ for risk, ✅ for strong fundamentals, 📉 for decline, and ⭐️ for final verdicts.            

#             """
#             tool_outputs.append(f"{prompt}")
#         elif function_name=='analyze_sector':
#             if argument.get('symbol'):
#                 sector_analysis=analyze_sector(argument['symbol'],"")
            
#                 prompt = f"""
#                         📊 **Sector Financial Analysis**

#                         Here is a summary of the financial performance of the top companies in this sector:

#                         {sector_analysis}

#                         ✅ Use this information to evaluate the overall health of the sector based on profitability, valuation, and growth metrics.

#                         📌 If a stock ticker was provided, compare its performance with these top companies across key metrics like Free Cash Flow, P/E Ratio, and Revenue Growth like:
                                        
#                             📌 Mention 1–2 quick insights at the end such as:
#                             - Which company leads in revenue growth?
#                             - Which has the strongest cash flow or best valuation?

#                         """
#                 tool_outputs.append(prompt)
#                 sector_analysis_added = True

#     # Fallback: if no tool call was made, but user asked for sector info
#     if message.tool_calls is None and "sector" in user_prompt.lower() and not sector_analysis_added:
#         # Try to extract ticker from prompt
#         from difflib import get_close_matches

#         def extract_ticker_from_prompt(prompt):
#             prompt = prompt.lower()
#             company_names = list(company_ticker_map.keys())
#             matches = get_close_matches(prompt, company_names, n=1, cutoff=0.6)
#             if matches:
#                 return company_ticker_map[matches[0]]
#             return None

#         fallback_ticker = extract_ticker_from_prompt(user_prompt)
#         if fallback_ticker:
#             sector_analysis = analyze_sector(fallback_ticker, "")
#             prompt = f"""
#     📊 **Sector Financial Analysis (via {fallback_ticker})**

#     Here is a summary of the financial performance of the top companies in this sector:

#     {sector_analysis}

#     ✅ Use this information to evaluate the overall health of the sector based on profitability, valuation, and growth metrics.

#     📌 Compare this company with sector peers on:
#     - Free Cash Flow
#     - P/E Ratio
#     - Revenue Growth
#     - Net Income
#     - Debt-to-Equity
#     - Market Cap

#     🎯 Format insights cleanly with a markdown table if possible.
#     """
#             tool_outputs.append(prompt)


#     final_prompt = "\n\n".join(tool_outputs)

#     followup_messages = [
#         {
#             "role":"system",
#             "content": """
#             You are a helpful financial assistant. Use clear, engaging, and structured formatting with relevant emojis.

#             - Use emojis like ✅ 📈 💰 🚀 🟢 for positive, ❌ ⚠️ 📉 🔻 🔴 for negative, and 📎 🟡 🤝 for neutral.
#             - Start section headings and bullet points with appropriate emojis.
#             - Add section headers like **Stock Price**, **Market Sentiment**, **Financials**, and **Final Verdict**.
#             - Make your response not less than 300 words.
#             - When doing sentiment analysis try to explain them in sentences rather than giving short verdicts
#             -If relevant news not found skip it.
#             """
#         },
       
#         {
#             "role":"user",
#             "content": final_prompt,
#         }
#     ]


#     summary_response = client.chat.completions.create(
#             model="llama3-70b-8192",
#             messages=followup_messages,
#             max_tokens=500
#         )
    
#     assistant_reply= summary_response.choices[0].message.content

#     return assistant_reply




def clean_response(text):
    text = text.replace("\n\n\n", "\n\n").strip()
    if "final verdict" not in text.lower():
        text += "\n\n⭐ Final Verdict: More information is needed for a conclusive analysis."
    return text


def run_finance_agent(user_prompt, conversation_hist):
    level = classify_levl(user_prompt)
    conversation_hist = conversation_hist[-3:]
    price_called = False
    tool_outputs = {
        "price": "",
        "sentiment": "",
        "financials": "",
        "sector": ""
    }

    # Initial system + user message to let LLM route tools
    chat_completion = client.chat.completions.create(
        messages=[
            {
                                    "role": "system",
                                    "content": f"""
                    You are a smart AI finance chatbot.

                    The user is a **{level}** investor:
                    - Beginner: explain financial terms briefly and clearly.
                    - Amateur: use relevant financial vocabulary, but keep things clear.
                    - Seasoned: go deep into financial metrics, use ratios, and be concise.

                    Provide a well-structured analysis with section headers like **Stock Price**, **Sentiment**, **Financials**, **Verdict**. Use emojis like 📈, 💰, ⚠️, ✅, 📉, and ⭐.
                    """
            },
            *conversation_hist,
            {"role": "user", "content": user_prompt}
        ],
        model="llama3-70b-8192",
        tools=tools,
        tool_choice="auto",
        max_completion_tokens=500
    )

    message = chat_completion.choices[0].message
    tool_calls = message.tool_calls

    if tool_calls is None:
        return message.content

    sentiment_added = False

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        argument = json.loads(tool_call.function.arguments)
        symbol = argument.get("symbol", "").upper()

        if symbol and not sentiment_added:
            try:
                sentiment = sentiment_analysis(symbol)
                tool_outputs["sentiment"] = f"📰 **Market Sentiment Analysis for {symbol}**:\n{sentiment}"
                sentiment_added = True
            except Exception as e:
                tool_outputs["sentiment"] = f"⚠️ Failed to fetch sentiment: {str(e)}"

        try:
            if function_name == "get_stock_price":
                result = get_stock_price(symbol)
                tool_outputs["price"] = f"📈 **Stock Price Info for {symbol}**:\n{result}"
                price_called = True
            elif function_name == "analyze_financials":
                summary = analyze_financials(symbol)
                tool_outputs["financials"] = f"""💰 **Financial Analysis for {symbol}**:

                                            {summary}

                                            Give an investment attractiveness score out of 100 and explain briefly using:
                                            - ✅ for positives
                                            - ⚠️ for risks
                                            - ⭐ for final verdict"""

            elif function_name == "analyze_sector":
                sector_data = analyze_sector(symbol, argument.get("sector", ""))
                tool_outputs["sector"] = f"""📊 **Sector Analysis (via {symbol})**:

                        {sector_data}

                        Compare company metrics like FCF, P/E, growth, and summarize 1–2 insights.
                        """
        except Exception as e:
            tool_outputs[function_name] = f"❌ Tool `{function_name}` failed: {str(e)}"

   
    if tool_calls is None and "sector" in user_prompt.lower():
        from difflib import get_close_matches
        prompt = user_prompt.lower()
        company_names = list(company_ticker_map.keys())
        matches = get_close_matches(prompt, company_names, n=1, cutoff=0.6)
        if matches:
            fallback_symbol = company_ticker_map[matches[0]]
            try:
                sector_data = analyze_sector(fallback_symbol, "")
                tool_outputs["sector"] = f"""📊 **Sector Analysis (via {fallback_symbol})**:\n{sector_data}"""
            except:
                pass
    # Enforce stock price if missed
    if not price_called:
    # Try to extract a fallback symbol from tool calls or prompt
        fallback_symbol = None

        for tool_call in tool_calls:
            args = json.loads(tool_call.function.arguments)
            if "symbol" in args:
                fallback_symbol = args["symbol"]
                break

        if not fallback_symbol:
            # Try to extract from user_prompt using fuzzy match
            from difflib import get_close_matches
            matches = get_close_matches(user_prompt.lower(), company_ticker_map.keys(), n=1, cutoff=0.6)
            if matches:
                fallback_symbol = company_ticker_map[matches[0]]

        if fallback_symbol:
            try:
                result = get_stock_price(fallback_symbol)
                tool_outputs["price"] = f"📈 **Stock Price Info for {fallback_symbol} (forced)**:\n{result}"
            except Exception as e:
                tool_outputs["price"] = f"⚠️ Could not fetch stock price for {fallback_symbol}: {str(e)}"

        if not tool_outputs["price"]:
                tool_outputs["price"] = "📈 **Stock Price:** Not available due to missing data."
    
        if not tool_outputs["financials"]:
                 tool_outputs["financials"] = "💰 **Financials:** Not available at the moment."

        if not tool_outputs["sentiment"]:
                tool_outputs["sentiment"] = "📰 **Sentiment:** No relevant news or data found. 📎"

    # Assemble final prompt
    final_prompt = "\n\n".join(
        section for section in tool_outputs.values() if section.strip()
    )

    followup_messages = [
        {
                        "role": "system",
                        "content": """
            You are a helpful financial assistant. Your goals:
            - Use section headers like 📈 Stock Price, 📰 Sentiment, 💰 Financials, ⭐ Final Verdict.
            - Use bullet points for clarity, and keep tone professional.
            - Use emojis: ✅ 📈 💰 🚀 🟢 for positives, ❌ ⚠️ 📉 🔻 🔴 for negatives, 📎 🟡 🤝 for neutral.
            - Response should be informative, not less than 300 words.
            """
        },
        {
            "role": "user",
            "content": final_prompt,
        }
    ]

    summary_response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=followup_messages,
        max_tokens=800,
        temperature=0.2
    )

    return clean_response(summary_response.choices[0].message.content)


#print(run_finance_agent("Can you analyze TCS's stock price",[]))
#print(sentiment_analysis("TCS"))



#print(sentiment_analysis("CIPLA"))