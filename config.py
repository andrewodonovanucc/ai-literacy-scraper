SEARCH_TERMS = [
    "Lecturer",
    "Professor",
    "Instructional Designer",
    "Educational Developer",
    "Academic Developer",
    "Faculty Position",
    # "Researcher",
]

AI_TERMS = [
    "artificial intelligence",
    "ai",
    "machine learning",
    "deep learning",
    "neural network",
    "generative ai",
    "gen ai",
    "genai",
    "large language model",
    "llm",
    "foundation model",
    "chatgpt",
    "gpt-4",
    "gpt4",
    "openai",
    "gpt-5",
    "claude",
    "anthropic",
    "gemini",
    "copilot",
    "llama",
    "ai literacy",
    "ai tool",
    "ai-powered",
    "ai-enabled",
    "ai in education",
    "ai in teaching",
    "ai in learning",
    "ai policy",
]

LOCATIONS = {
    "GB": "United Kingdom",
    "IE": "Ireland"
}

# =================================================================================
# HEADERS TO PASS FOR REQUEST
# =================================================================================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Referer": "https://www.jobs.ac.uk/",
}


# =================================================================================
# CURRENCY PARSING VALUES
# =================================================================================

RATES_TO_EUR = {
    #   Default values if currency conversion fails.
    "GBP": 1.19,
    "CAD": 0.63,
    "EUR": 1.00,
    "USD": 0.93,
    "NZD": 0.55,
    "AUD": 0.59,
    "CNY": 0.13,
}


# Ordered longest-first so $USD isn't automatically parsed instead of NZ$/AU$/CA$
CURRENCY_PATTERNS = [
    (r"NZ\$", "NZD"),
    (r"AU\$", "AUD"),
    (r"A\$",  "AUD"),
    (r"CA\$", "CAD"),
    (r"£",    "GBP"),
    (r"€",    "EUR"),
    (r"¥",    "CNY"),
    (r"\$",   "USD"),
]

REQUEST_DELAY = 1.5
