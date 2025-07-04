import time
from finance_agent import run_finance_agent

def validate_response_structure(response):
    return all(keyword in response for keyword in [
        "📈", "💰", "⭐", "Final Verdict"
    ])

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
    print(response[:500], "...\n")
    return passed, duration, emoji_count

# List of real-world queries to test
test_prompts = [
    "Analyze Tata Motors stock",
    "Is Infosys a good buy?",
    "Show me ICICI Bank financials",
    "What is the market sentiment for TCS?",
    "Give full analysis for HDFC",
    "Any insight on Tata Motors?",
    "Should I invest in SBI now?",
    "Sentiment and stock price for Wipro"
]

# Run all tests
def run_all_tests():
    total = len(test_prompts)
    passed_tests = 0
    for prompt in test_prompts:
        passed, *_ = test_full_bot(prompt)
        if passed:
            passed_tests += 1

    print(f"\n✅ Passed {passed_tests}/{total} end-to-end tests")

if __name__ == "__main__":
    run_all_tests()
