import re
from config import RATES_TO_EUR, CURRENCY_PATTERNS
from currency_converter import CurrencyConverter as curr
import logging

UNPARSEABLE = {"n/a", "not specified", "competitive", "per hour"}

min_stipend = 15_000
max_stipend = 40_000
_STIPEND_KEYWORDS = [
    "stipend", "ukri", "maintenance", "per year", "per annum", "annually",
    "tax-free", "tax free",
]


def get_updated_currency_rates():
    global RATES_TO_EUR
    conv = curr()
    try:
        for code in RATES_TO_EUR.keys():
            RATES_TO_EUR[code] = conv.convert(1, code, "EUR")
    except Exception as e:
        logging.warning(f"Currency conversion failed: {e}. Using default rates.")


def _extract_amounts(salary_str):
    """Return list of (value, currency_code) in left-to-right order."""
    results = []
    for sym_pattern, code in CURRENCY_PATTERNS:
        for m in re.finditer(sym_pattern, salary_str, re.IGNORECASE):
            remainder = salary_str[m.end():]
            # Allow optional whitespace inside the number (e.g. "£21, 805")
            num_match = re.match(r"\s*([\d,\s]+(?:\.\d+)?)", remainder)
            if num_match:
                raw = re.sub(r"[\s,]", "", num_match.group(1))
                try:
                    results.append((float(raw), code, m.start()))
                except ValueError:
                    pass
    results.sort(key=lambda x: x[2])
    return [(val, code) for val, code, _ in results]


def parse_salary_bounds(salary_str):
    if not salary_str or salary_str.strip().lower() in UNPARSEABLE:
        return None, None

    amounts = _extract_amounts(salary_str)
    if not amounts:
        return None, None

    first_currency = amounts[0][1]
    rate = RATES_TO_EUR.get(first_currency, 1.0)

    same_currency = [v for v, c in amounts if c == first_currency]

    if len(same_currency) >= 2:
        # Use min/max rather than positional order -- some strings list the FTE figure
        # before the actual figure (e.g. "Up to £52,776 pro rata; actual salary £26,388"),
        # which would otherwise produce lower > upper.
        lower = round(min(same_currency[0], same_currency[1]) * rate)
        upper = round(max(same_currency[0], same_currency[1]) * rate)
    else:
        # Single figure is the lower bound (floor salary), not the upper.
        lower = round(same_currency[0] * rate)
        upper = None

    return lower, upper


def parse_stipend_from_jd(jd_text):
    if not jd_text or jd_text.strip() in ("N/A", ""):
        return None, None, None

    # Allow optional internal whitespace in numbers (e.g. "£21, 805")
    pattern = re.compile(r"£\s*([\d,\s]+(?:\.\d+)?)")
    candidates = []

    for match in pattern.finditer(jd_text):
        raw = re.sub(r"[\s,]", "", match.group(1))
        try:
            val = float(raw)
        except ValueError:
            continue
        if not (min_stipend <= val <= max_stipend):
            continue
        context = jd_text[max(0, match.start() - 80) : match.end() + 80].lower()
        if any(keyword in context for keyword in _STIPEND_KEYWORDS):
            candidates.append((val, match.start()))

    if not candidates:
        return None, None, None

    # Prefer the largest value (enhanced UKRI > standard UKRI)
    candidates.sort(key=lambda x: -x[0])
    best_val, char_pos = candidates[0]
    snippet = jd_text[max(0, char_pos - 20) : char_pos + 20].strip()

    rate = RATES_TO_EUR.get("GBP", 1.0)
    return snippet, round(best_val * rate), None