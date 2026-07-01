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

# --- LinkedIn jd_text salary parsing -------------------------------------
_LI_CUR_SYMBOLS = {"£": "GBP", "€": "EUR", "$": "USD"}

_LI_MONTHLY_KEYWORDS = [
    "per month", "/month", "p/m", "per maand", "por mes", "al mese",
    "per mese", "mensile", "maandelijks", "brut mensuel", "netto",
    "por mês", "ao mês", "meses)",  # PT/BR "14 meses" annual bonus months, excluded below
]
_LI_ANNUAL_KEYWORDS = [
    "per annum", "per year", "annuel", "annum", "brut annuel", "gross per year",
    "jaarsalaris", "annuo", "anual", "annual",
]
_LI_SALARY_KEYWORDS = [
    "salary", "compensation", "pay range", "remuneration", "package", "wage",
    "salaire", "rémunération", "fourchette",
    "salario", "sueldo", "retribución",
    "salário", "salarial", "remuneração", "pacote salarial",
    "retributiv", "stipendio", "compenso", "ral",
    "gehalt", "vergütung",
    "salaris",
]

_LI_RANGE_SEP = r"(?:-|–|—|to|and|et|a|entre|da)"

_LI_PAIR_RE = re.compile(
    rf"(?P<v1_sym_pre>[£€$])?\s*(?P<v1_num>\d[\d.,]*)\s*(?P<v1_k>[kK])?\s*(?P<v1_sym_post>[£€$])?"
    rf"\s*(?:{_LI_RANGE_SEP})\s*"
    rf"(?P<v2_sym_pre>[£€$])?\s*(?P<v2_num>\d[\d.,]*)\s*(?P<v2_k>[kK])?\s*(?P<v2_sym_post>[£€$])?",
    re.IGNORECASE,
)

_LI_SINGLE_RE = re.compile(
    r"(?P<sym_pre>[£€$])\s*(?P<num>\d[\d.,]*)\s*(?P<k>[kK])?\s*(?P<sym_post>[£€$])?"
)


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


def _li_parse_number(raw, k_suffix):
    raw = raw.strip()
    if re.match(r"^\d{1,3}(\.\d{3})+(,\d+)?$", raw):
        # European: dot thousands, comma decimal -> 5.485,70 / 4.000
        raw = raw.replace(".", "").replace(",", ".")
    elif re.match(r"^\d{1,3}(,\d{3})+(\.\d+)?$", raw):
        # English: comma thousands, dot decimal -> 5,485.70 / 50,000
        raw = raw.replace(",", "")
    elif re.match(r"^\d+\.\d{3}$", raw):
        # single dot-thousands group, no decimal -> 4.000
        raw = raw.replace(".", "")
    elif re.match(r"^\d+,\d{3}$", raw):
        raw = raw.replace(",", "")
    elif re.match(r"^\d+,\d{1,2}$", raw):
        # European decimal comma -> 1,5
        raw = raw.replace(",", ".")
    # else: plain int or dot-decimal, leave as-is
    try:
        val = float(raw)
    except ValueError:
        return None
    if k_suffix:
        val *= 1000
    return val


def _li_has_salary_context(jd_text, start, end):
    window = jd_text[max(0, start - 90): end + 20].lower()
    return any(kw in window for kw in _LI_SALARY_KEYWORDS)


def parse_salary_linkedin(jd_text):
    if not jd_text:
        return None, None, None

    candidates = []  # (score, -start, lower, upper, currency)

    for m in _LI_PAIR_RE.finditer(jd_text):
        sym = m.group("v1_sym_pre") or m.group("v1_sym_post") or m.group("v2_sym_pre") or m.group("v2_sym_post")
        if not sym:
            continue
        v1 = _li_parse_number(m.group("v1_num"), m.group("v1_k"))
        v2 = _li_parse_number(m.group("v2_num"), m.group("v2_k"))
        if v1 is None or v2 is None:
            continue
        # shorthand range e.g. "60-75K" / "£40-42k" -> the k applies to both numbers
        if bool(m.group("v1_k")) != bool(m.group("v2_k")):
            base1 = _li_parse_number(m.group("v1_num"), None)
            base2 = _li_parse_number(m.group("v2_num"), None)
            if base1 is not None and base2 is not None and base1 < 1000 and base2 < 1000:
                if m.group("v2_k") and not m.group("v1_k"):
                    v1 = base1 * 1000
                elif m.group("v1_k") and not m.group("v2_k"):
                    v2 = base2 * 1000
        lower, upper = sorted((v1, v2))
        # a coherent salary range shouldn't span two orders of magnitude --
        # large ratios usually mean a number got mangled by stray whitespace/
        # line breaks in the scraped text (e.g. "£90,00" + orphaned "0")
        if lower <= 0 or upper / lower > 20:
            continue
        # discard small ranges (referral bonuses, vouchers, percentages) unless
        # explicitly anchored by a salary keyword right next to them
        has_context = _li_has_salary_context(jd_text, m.start(), m.end())
        if lower < 1000 and not has_context:
            continue
        currency = _LI_CUR_SYMBOLS.get(sym, "EUR")
        context = jd_text[max(0, m.start() - 5): m.end() + 25].lower()
        is_monthly = any(kw in context for kw in _LI_MONTHLY_KEYWORDS) and "meses)" not in context
        # unlabeled figures under ~4,000 are implausible as an annual professional
        # salary in EUR/GBP -- treat as monthly (common in NL/PT/IT/DE postings)
        if not is_monthly and currency in ("EUR", "GBP") and lower < 4000:
            is_monthly = True
        if is_monthly:
            lower *= 12
            upper *= 12
        if lower > 600_000 or lower < 1000:
            continue
        is_annual = any(kw in context for kw in _LI_ANNUAL_KEYWORDS)
        score = (2 if has_context else 0) + (1 if is_monthly or is_annual else 0)
        candidates.append((score, -m.start(), round(lower), round(upper), currency))

    if not candidates:
        for m in _LI_SINGLE_RE.finditer(jd_text):
            if not _li_has_salary_context(jd_text, m.start(), m.end()):
                continue
            val = _li_parse_number(m.group("num"), m.group("k"))
            if val is None or val < 1000:
                continue
            sym = m.group("sym_pre") or m.group("sym_post")
            currency = _LI_CUR_SYMBOLS.get(sym, "EUR")
            context = jd_text[max(0, m.start() - 5): m.end() + 25].lower()
            is_monthly = any(kw in context for kw in _LI_MONTHLY_KEYWORDS)
            if not is_monthly and currency in ("EUR", "GBP") and val < 4000:
                is_monthly = True
            if is_monthly:
                val *= 12
            if val > 600_000:
                continue
            candidates.append((1, -m.start(), round(val), None, currency))

    if not candidates:
        return None, None, None

    # highest score wins; ties broken by earliest position in the text
    candidates.sort(reverse=True)
    _, _, lower, upper, currency = candidates[0]
    rate = RATES_TO_EUR.get(currency, 1.0)
    lower_eur = round(lower * rate) if lower is not None else None
    upper_eur = round(upper * rate) if upper is not None else None
    return lower_eur, upper_eur, currency