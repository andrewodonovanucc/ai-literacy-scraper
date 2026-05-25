import re
from config import RATES_TO_EUR, CURRENCY_PATTERNS
from currency_converter import CurrencyConverter as curr
import logging
import parse_salary as ps


UNPARSEABLE = {"n/a", "not specified", "competitive", "per hour"}

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
            num_match = re.match(r"\s*([\d,]+(?:\.\d+)?)", remainder)
            if num_match:
                raw = num_match.group(1).replace(",", "")
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
    # logging.info("=" * 100)
    # logging.info("GETTING UP TO DATE CURRENCY RATES...")
    ps.get_updated_currency_rates()
    rate = RATES_TO_EUR.get(first_currency, 1.0)

    same_currency = [v for v, c in amounts if c == first_currency]

    if len(same_currency) >= 2:
        lower = round(same_currency[0] * rate)
        upper = round(same_currency[1] * rate)
    else:
        lower = round(same_currency[0] * rate)
        upper = None

    return lower, upper