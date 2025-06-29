from bs4 import BeautifulSoup
import requests
import os
from transformers import AutoTokenizer,AutoModelForSequenceClassification
import torch

def extract_news(symbol):
    query=symbol.upper()
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

