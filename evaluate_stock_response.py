import re
import textstat
from finance_agent import run_finance_agent

def evaluate_stock_analysis(response):
    
    results = {}

    # Check presence of required sections
    sections = ["Stock Price", "Sentiment", "Financials", "Final Verdict"]
    results["section_coverage"] = sum(1 for s in sections if s.lower() in response.lower())
    results["structure_score (0-1)"] = round(results["section_coverage"] / len(sections), 2)

    #  Count relevant emojis
    emojis = ["📈", "💰", "⚠️", "✅", "📉", "⭐", "📎", "🟢", "🔴", "🟡"]
    results["emoji_count"] = sum(response.count(e) for e in emojis)

    # Basic text stats
    results["word_count"] = len(response.split())

    # Readability metrics
    results["readability"] = {
        "flesch_reading_ease": textstat.flesch_reading_ease(response),
        "flesch_kincaid_grade": textstat.flesch_kincaid_grade(response),
        "gunning_fog": textstat.gunning_fog(response),
        "automated_readability_index": textstat.automated_readability_index(response)
    }

    #  Try to classify sentiment from the Verdict section
    results["verdict_sentiment"] = "Missing"
    verdict_match = re.search(r"\*\*⭐ Final Verdict\*\*(.*?)\*\*", response, re.DOTALL | re.IGNORECASE)
    if verdict_match:
        verdict_text = verdict_match.group(1).strip().lower()
        if "buy" in verdict_text or "positive" in verdict_text:
            results["verdict_sentiment"] = "Positive"
        elif "sell" in verdict_text or "negative" in verdict_text:
            results["verdict_sentiment"] = "Negative"
        elif "neutral" in verdict_text or "caution" in verdict_text:
            results["verdict_sentiment"] = "Neutral"
        else:
            results["verdict_sentiment"] = "Unclear"
    if results["verdict_sentiment"] == "Missing":
        lower_text = response.lower()
        if "bullish" in lower_text or "buy" in lower_text or "positive" in lower_text:
            results["verdict_sentiment"] = "Positive"
        elif "bearish" in lower_text or "sell" in lower_text or "negative" in lower_text:
            results["verdict_sentiment"] = "Negative"
        elif "neutral" in lower_text or "caution" in lower_text:
            results["verdict_sentiment"] = "Neutral"
        else:
            results["verdict_sentiment"] = "Unclear"
    evaluation = ""
    for key, value in results.items():
        evaluation += f"{key}: {value}\n"
    return evaluation


# 🧪 Example Usage
# if __name__ == "__main__":
#     try:
#         with open("tatamotors_sample.txt", "r") as f:
#             response_text = f.read()
#     except FileNotFoundError:
#         print("❌ File 'tatamotors_sample.txt' not found. Please place it in the same folder.")
#         exit()

#     print("📊 Evaluation Report:")
#     evaluation = evaluate_stock_analysis(response_text)
#     for key, value in evaluation.items():
#         print(f"{key}: {value}")

test_prompts = [
    "What’s the investment outlook for Apple?",
    "Should I invest in Infosys this quarter?",
    "How is the sentiment around Meta after recent news?",
    "What’s the current price and trend of HDFC Bank?",
    "Is Tesla overvalued at current levels?",
    "Analyze TCS’s financial performance and give a final verdict.",
    "What are analysts saying about Nvidia?",
    "Is it a good time to buy Netflix stock?",
    "Evaluate the fundamentals of Sun Pharma.",
    "Give me a full stock analysis report on Oracle.",
    "What’s the sentiment around Mahindra & Mahindra this week?",
    "What’s the latest on Power Grid’s financial health?",
    "Does Pepsi have long-term growth potential?",
    "What are the risks associated with Salesforce right now?",
    "Summarize the performance and sentiment of ITC stock.",
    "Is Asian Paints a strong buy based on recent data?",
    "Break down the financial metrics of JPMorgan.",
    "How is Titan performing in the consumer sector?",
    "Is the current decline in Intel’s stock price justified?",
    "Give me a hold/sell/buy verdict for Ultratech Cement.",
    "Should I buy shares of Coca Cola now?",
    "Tell me about the current valuation of Zoom.",
    "Is Shopify a good investment for long-term growth?",
    "How has Bajaj Finance been performing lately?",
    "What’s the financial outlook for Larsen & Toubro?"
]

f = open("results.txt","w")

for prompt in test_prompts:
    response = run_finance_agent(prompt,[])
    eval=evaluate_stock_analysis(response)
    f.write(f"{prompt}\n{response}\n{eval}\n\n")
    print("----------")

f.close()
    
