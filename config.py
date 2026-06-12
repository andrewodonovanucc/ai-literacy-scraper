JOB_SEARCH_TERMS = [
    "Lecturer",
    "Professor",
    "Teaching Fellow",
    "Teaching Associate",
    "Stipendiary",
    "Dean",
    "Head of Department",
    "Chair",
    "Reader"
]

PHD_SEARCH_TERMS = [
    "Research Associate",
    "Research Fellow",
    "Postdoctoral"
]

COMBINED_SEARCH_TERMS = [
    "Lecturer",
    "Professor",
    "Teaching Fellow",
    "Teaching Associate",
    "Stipendiary",
    "Dean",
    "Head of Department",
    "Chair",
    "Reader",
    "Research Associate",
    "Research Fellow",
    "Postdoctoral"
]

AI_TERMS = [
    # General AI
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "neural network",
    "reinforcement learning",
    "natural language processing",
    "nlp",
    "computer vision",

    # Generative AI
    "generative ai",
    "gen ai",
    "genai",
    "large language model",
    "llm",
    "foundation model",

    # Specific tools / companies
    "chatgpt",
    "gpt-4",
    "gpt4",
    "gpt-4o",
    "gpt-5",
    "openai",
    "anthropic",
    "github copilot",

    # AI in education / policy framing
    "ai literacy",
    "ai fluency",
    "ai tool",
    "ai-powered",
    "ai-enabled",
    "ai in education",
    "ai in teaching",
    "ai in learning",
    "ai policy",
    "ai ethics",
    "ai governance",
    "responsible ai",
    "prompt engineering",

    # Data / adjacent
    "data science",
    "predictive model",

    "ai",
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
    "GBP": 1.16,
    "CAD": 0.62,
    "EUR": 1.00,
    "USD": 0.86,
    "NZD": 0.51,
    "AUD": 0.61,
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