# AI Literacy Scraper

A Python tool for scraping and analysing job postings from [jobs.ac.uk](https://www.jobs.ac.uk) and LinkedIn to investigate the prevalence of AI literacy requirements in academic and industry roles. Built as part of a PhD research project examining how institutions and employers are responding to generative AI.

## What it does

The tool runs two parallel scraping tracks (jobs.ac.uk and LinkedIn) that feed into a shared filter, analyse, and dashboard pipeline. Each stage can be run independently, in combination, or all together via the menu.

| Stage | What it does |
|-------|-------------|
| 1. **Scrape (jobs.ac.uk)** | Searches jobs.ac.uk for academic roles and PhD studentships (`JOB_SEARCH_TERMS` / `PHD_SEARCH_TERMS` / `COMBINED_SEARCH_TERMS`) across configured locations. Collects listings across all result pages and deduplicates by URL. |
| 2. **Job Details (jobs.ac.uk)** | Fetches full job description text and structured criteria (salary, hours, contract type, dates, location, discipline) for each listing. Filters out non-Academic/Research postings. Splits output into `criteria_academic` and `criteria_phd`. |
| 3. **Filter** | Scans job descriptions for AI-related terminology using word-boundary regex matching, and records the matching sentences per job. |
| 4. **Analyse** | Computes salary and AI-match breakdowns by discipline and logs summary tables to the console. |
| 5. **All** | Runs the full jobs.ac.uk pipeline (scrape → details → filter → analyse) and archives old files. |
| 6. **Archive old files** | Moves outdated data files to backup. |
| 7. **Run App** | Launches the Streamlit dashboard. |
| 8. **Scrape (LinkedIn)** | Scrapes LinkedIn for industry roles (`INDUSTRY_SEARCH_TERMS`) via `linkedin-jobs-scraper`. |
| 9. **Job Details (LinkedIn)** | Deduplicates LinkedIn postings by URL and extracts salary from the scraped job description text. |
| 0. **Exit** | |

## Setup

**Requirements:** Python 3.10+

```bash
git clone https://github.com/andrewodonovanucc/ai-literacy-scraper.git
cd ai-literacy-scraper
pip install -r requirements.txt
```

### LinkedIn scraping setup

The LinkedIn track uses `linkedin-jobs-scraper`, which drives a real Chrome browser via Selenium. You'll need a `.env` file in the project root with:

```
CHROME_DR=/path/to/chromedriver
CHROME_BIN=/path/to/chrome
LI_AT_COOKIE=your_li_at_session_cookie
```

`LI_AT_COOKIE` is your LinkedIn session cookie, used by the underlying library for authentication. Treat it as a credential: don't commit `.env`, and rotate the cookie if it's ever exposed (e.g. shared in a chat, ticket, or log).

## Usage

### CLI pipeline

```bash
python main.py
```

Run with no arguments to get the interactive menu, or pass positional args directly:

```bash
python main.py <option> <scrape_type> <analyse_type>
```

- `option` — main menu choice (`1`–`9`, `0`, or a combo like `123`)
- `scrape_type` — jobs.ac.uk scraper sub-choice (`1`=Academic, `2`=PhD, `3`=Both) — only used by options that scrape jobs.ac.uk
- `analyse_type` — analyse sub-choice (`1`=Academic, `2`=PhD, `3`=LinkedIn, `4`=All) — only used by options that run Analyse

Any argument left out falls back to an interactive prompt for that stage.

Combo options:

| Option | Stages run |
|--------|-----------|
| `12`   | Scrape (jobs.ac.uk) + Job Details |
| `123`  | Scrape + Job Details + Filter |
| `126`  | Scrape + Job Details + Archive |
| `1236` | Scrape + Job Details + Filter + Archive |
| `1246` | Scrape + Job Details + Analyse + Archive |
| `24`   | Job Details + Analyse |
| `246`  | Job Details + Analyse + Archive |
| `26`   | Job Details + Archive |
| `46`   | Analyse + Archive |
| `89`   | Scrape (LinkedIn) + Job Details (LinkedIn) |
| `893`  | Scrape (LinkedIn) + Job Details (LinkedIn) + Filter |
| `8934` | Scrape (LinkedIn) + Job Details (LinkedIn) + Filter + Analyse |
| `86`   | Scrape (LinkedIn) + Archive |
| `896`  | Scrape (LinkedIn) + Job Details (LinkedIn) + Archive |
| `8936` | Scrape (LinkedIn) + Job Details (LinkedIn) + Filter + Archive |
| `89346`| Scrape (LinkedIn) + Job Details (LinkedIn) + Filter + Analyse + Archive |
| `96`   | Job Details (LinkedIn) + Archive |
| `936`  | Job Details (LinkedIn) + Filter + Archive |
| `9346` | Job Details (LinkedIn) + Filter + Analyse + Archive |

### Scraper sub-menu (jobs.ac.uk)

When option 1 (or a combo starting with it) runs, you'll be prompted to choose which roles to search for:

```
1. JUST ACADEMIC JOBS
2. JUST PHD STUDENTSHIPS
3. BOTH
```

Option 1 uses `JOB_SEARCH_TERMS`, option 2 uses `PHD_SEARCH_TERMS`, option 3 uses `COMBINED_SEARCH_TERMS` (see `config.py`).

### Analyse sub-menu

When Analyse runs without an `analyse_type` passed in, you'll be prompted:

```
1. JUST ACADEMIC JOBS (jobs.ac.uk)
2. JUST PHD STUDENTSHIPS (jobs.ac.uk)
3. LINKEDIN JOBS
4. ALL
```

### Streamlit dashboard

```bash
streamlit run app.py
```

Loads the most recent filtered dataset and displays it as tabbed views with bar charts and Plotly pie charts, covering salary and AI-match breakdowns by discipline.

## Configuration

All search parameters are in `config.py`:

```python
# Academic roles (jobs.ac.uk)
JOB_SEARCH_TERMS = [
    "Lecturer", "Professor", "Teaching Fellow", "Teaching Associate",
    "Stipendiary", "Dean", "Head of Department", "Chair", "Reader",
]

# PhD studentship roles (jobs.ac.uk)
PHD_SEARCH_TERMS = [
    "Research Associate", "Research Fellow", "Postdoctoral",
]

# Industry roles (LinkedIn)
INDUSTRY_SEARCH_TERMS = [
    "Business Analyst", "ERP Consultant", "Data Analyst", "Project Coordinator",
    "IT Risk Analyst", "Technical Support Engineer", "IT Support Engineer",
    "Audit Associate", "Tax Associate", "Software Developer",
]

# Locations to search on jobs.ac.uk (country code: display name)
LOCATIONS = {
    "GB": "United Kingdom",
    "IE": "Ireland",
}

# AI-related terms matched against job description text (word-boundary regex)
AI_TERMS = [
    "artificial intelligence", "machine learning", "deep learning", "neural network",
    "reinforcement learning", "natural language processing", "nlp", "computer vision",
    "generative ai", "gen ai", "genai", "large language model", "llm", "foundation model",
    "chatgpt", "gpt-4", "gpt4", "gpt-4o", "gpt-5", "openai", "anthropic", "github copilot",
    "ai literacy", "ai fluency", "ai tool", "ai-powered", "ai-enabled",
    "ai in education", "ai in teaching", "ai in learning", "ai policy", "ai ethics",
    "ai governance", "responsible ai", "prompt engineering",
    "prescriptive analysis", "prescriptive analytics", "predictive model", "ai",
]

REQUEST_DELAY = 1.5  # seconds between requests (jobs.ac.uk)
```

Modify `JOB_SEARCH_TERMS`, `PHD_SEARCH_TERMS`, `INDUSTRY_SEARCH_TERMS`, `LOCATIONS`, or `AI_TERMS` to adjust the scope of the scrape or the filter criteria.

## Project structure

```
ai-literacy-scraper/
├── data/
│   ├── jobs/                # Raw deduplicated job listings from jobs.ac.uk scraper (timestamped JSON)
│   ├── jobs_linkedin/       # Raw deduplicated LinkedIn listings (timestamped JSON)
│   ├── jd/                  # jobs.ac.uk jobs with full description text added (timestamped JSON)
│   ├── criteria/            # jobs.ac.uk jobs with salary, hours, contract, dates, location, discipline (timestamped JSON)
│   ├── criteria_academic/   # Subset of criteria: non-PhD roles only (timestamped JSON)
│   ├── criteria_phd/        # Subset of criteria: PhD studentships only (timestamped JSON)
│   ├── criteria_linkedin/   # LinkedIn jobs with salary extracted from jd_text (timestamped JSON)
│   ├── filters/             # Jobs with AI match count and matched sentences added (timestamped JSON)
│   ├── analyse/             # Jobs prepared for the Streamlit dashboard (timestamped JSON)
│   └── runs/                # Log file for each run (timestamped .log)
├── main.py                  # Entry point and menu
├── app.py                   # Streamlit dashboard
├── scraper.py                # Fetches job listings from jobs.ac.uk
├── scraper_linkedin.py        # Fetches job listings from LinkedIn
├── job_details.py             # Fetches full job text and structured criteria per jobs.ac.uk listing
├── job_details_linkedin.py    # Deduplicates and extracts salary for LinkedIn listings
├── ai_filter.py                # Filters postings by AI terminology using regex
├── analyse.py                  # Salary and AI-match breakdowns by discipline
├── parse_salary.py             # Salary string parsing and currency normalisation (jobs.ac.uk + LinkedIn)
├── config.py                   # Search terms, locations, AI terms, currency rates, request config
├── file_handling.py            # JSON read/write helpers and file archiving
├── helper.py                    # Shared request/retry helpers
├── log_setup.py                 # Logging configuration
└── requirements.txt
```

## Data pipeline

```
jobs/ ──────────────► jd/ ──► criteria/ ┬─► criteria_academic/
                                          └─► criteria_phd/
jobs_linkedin/ ─────────────────────────────► criteria_linkedin/
                                                      │
                                    (merged for Filter + Analyse)
                                                      ▼
                                                  filters/ ──► analyse/
```

The `archive_old_files()` function (menu option 6) moves all but the most recent file in each folder to `../ai-literacy-scraper-data-backup/`.

## Notes

- The jobs.ac.uk scraper uses a persistent `requests.Session` with cache-busting query parameters to avoid stale CloudFront cached responses.
- A configurable delay between requests (`REQUEST_DELAY` in `config.py`) is included to avoid hammering jobs.ac.uk.
- Salary figures are parsed and normalised to EUR via `parse_salary.py`, with live rate lookups (falling back to `RATES_TO_EUR` in `config.py` if the lookup fails). PhD studentships without a salary field fall back to extracting a stipend figure from the job description text.
- LinkedIn salary parsing handles multiple currency symbols, monthly vs annual figures, and several European number formats.
- Multiple currency formats are supported (£, €, $, NZ$, AU$, CA$, ¥) with longest-match parsing to avoid ambiguity.
- Each jobs.ac.uk posting captures location (`UK`/`IE`) and discipline extracted from the listing page.
- PhD role detection (`is_phd`) checks the job title and, where available, the full job description text.
- Progress is shown via `rich` progress bars during scraping and filtering.
- All output is logged to `data/runs/` and written to JSON files for downstream analysis.
- This tool is intended for academic research purposes only. Please respect the terms of service of jobs.ac.uk and LinkedIn.

## Dependencies

Key packages: `beautifulsoup4`, `requests`, `rich`, `streamlit`, `plotly`, `lxml`, `CurrencyConverter`, `linkedin-jobs-scraper`, `selenium`, `playwright`, `python-dotenv`. Full list in `requirements.txt`.

## Author

Andrew O'Donovan — PhD Researcher, University College Cork
[github.com/andrewodonovanucc](https://github.com/andrewodonovanucc)

[LinkedIn](https://ie.linkedin.com/in/andrew-o-donovan)