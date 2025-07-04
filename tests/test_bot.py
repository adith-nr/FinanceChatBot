#--------------------------------------------------------------------------------
# # test_bot.py – End-to-End Evaluation for Finance Agent
# # Author: Auto-generated
# # Usage: python test_bot.py or run with pytest
# # Requires: run_finance_agent() from your main app
# --------------------------------------------------------------------------------

import time
from finance_agent import run_finance_agent

def validate_response_structure(response):
    required_sections = ["📈", "💰", "⭐", "Final Verdict"]
    return all(keyword in response for keyword in required_sections)

def test_full_bot(prompt):
    print(f"🧪 Testing prompt: {prompt}")
    start = time.time()
    response = run_finance_agent(prompt, [])
    duration = round(time.time() - start, 2)

    passed = validate_response_structure(response)
    emoji_count = sum(response.count(e) for e in ["📈", "📉", "📎", "🟢", "🔴", "✅", "⚠️", "💰", "⭐"])

    print("⏱️ Response Time:", duration, "s")
    print("📊 Emoji Used:", emoji_count)
    print("✅ Structure Valid:", passed)
    print("📝 Word Count:", len(response.split()))
    print("------ Preview ------")
    print(response[:500], "...")
    return passed, duration, emoji_count

test_prompts = [
    "Analyze Reliance stock",
    "Is Infosys a good buy?",
    "Show me ICICI Bank financials",
    "What is the market sentiment for TCS?",
    "Give full analysis for HDFC",
    "Any insight on Tata Motors?",
    "Should I invest in SBI now?",
    "Sentiment and stock price for Wipro"
]

def run_all_tests():
    total = len(test_prompts)
    passed_tests = 0
    total_time = 0
    total_emojis = 0
    total_words = 0

    for prompt in test_prompts:
        passed, duration, emoji_count = test_full_bot(prompt)
        total_time += duration
        total_emojis += emoji_count
        total_words += len(run_finance_agent(prompt, []).split())
        if passed:
            passed_tests += 1

    print(f"✅ Passed {passed_tests}/{total} tests")
    print(f"📊 Avg Time: {round(total_time/total,2)}s | Avg Emojis: {round(total_emojis/total,2)} | Avg Words: {round(total_words/total,2)}")

if __name__ == "__main__":
    run_all_tests()
