from bs4 import BeautifulSoup
import requests
import os
from transformers import AutoTokenizer,AutoModelForSequenceClassification
import torch



#API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
API_KEY="8N8ZQQP1YJLYBG2R"
# url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AMZN&apikey={API_KEY}"
# r = requests.get(url)
# data = r.json()

# print(data)

def format_news_sentiment(data):
    news_arr = []
    for item in data:
        formatted = ""

        
        formatted += f"Summary: {item.get('summary', 'No summary')}"
       
        news_arr.append(formatted)
    
    return "\n".join(news_arr)



def extract_news_sentiment(symbol):
    query=symbol.upper()
    API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={query}&apikey={API_KEY}"
    r = requests.get(url)
    data = r.json()
    
    if len(data['feed'])<10:
        return format_news_sentiment(data['feed'][:len(data['feed'])])
    return format_news_sentiment(data['feed'][:10])

# #print(extract_news_sentiment("AMZN"))



# import finnhub
# finnhub_client = finnhub.Client(api_key="d1k0jf9r01ql1h39t920d1k0jf9r01ql1h39t92g")

# data = (finnhub_client.company_news('AAPL', _from="2025-06-01", to="2025-06-10"))


# data = data[:10]

# for item in data:
#     print(item['headline'])
#     print(item['summary'])
#     print("\n")




import finnhub

def extract_finnhub_news(symbol):
    query = symbol.upper()
    finnhub_client = finnhub.Client(api_key="d1k0jf9r01ql1h39t920d1k0jf9r01ql1h39t92g")

    try:
        data = finnhub_client.company_news(query, _from="2025-06-01", to="2025-06-10")
    except Exception as e:
        return "No news"

    if not data:
        return "No news"

    news_arr = [item['headline'] for item in data[:10]]
    return "\n".join(news_arr)

#print(extract_finnhub_news("AAPL"))





def extract_news(symbol):
    query=symbol.upper()
    if(extract_finnhub_news(symbol)!="No news"):
        return extract_finnhub_news(symbol)


    API_KEY = "2a024a2accd8f073a798a2acb52ee923"
    url = f"https://gnews.io/api/v4/search?q={query}&country=in&lang=en&token={API_KEY}"

    r = requests.get(url)
    data = r.json()
    news=[]

    if "articles" not in data or not isinstance(data["articles"], list):
        return "No news articles found or failed to retrieve news."
    for article in data['articles']:

        if query in article['title']:
            news.append(article['content'])

        if len(news)>=5:
            break
    
    formatted = "\n".join(news)

    return formatted


