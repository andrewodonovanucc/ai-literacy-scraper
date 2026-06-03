# AI Literacy Scraper

A Python tool for scraping and analysing academic job postings on [jobs.ac.uk](https://www.jobs.ac.uk) to investigate the prevalence of AI literacy requirements in higher education roles. Built as part of a PhD research project examining how institutions are responding to generative AI.

## What it does

The tool runs as a pipeline with four stages, each of which can be executed independently or all together:

| Stage | What it does |
|-------|-------------|
| 1. **Scrape** | Searches jobs.ac.uk for academic roles (Lecturer, Professor, Instructional Designer, etc.) across configured locations and collects job listings across all result pages. Deduplicates by URL and saves to JSON. |
| 2. **Job Details** | Fetches the full text and structured criteria (salary, hours, contract type, dates, location) for each job posting by following the individual listing URLs. |
| 3. **Filter** | Scans job descriptions for AI-related terminology (e.g. `ai literacy`, `large language model`, `generative ai`, `chatgpt`) using regex matching, and records the matching sentences per job. |
| 4. **Analyse** | Loads the filtered dataset into a pandas DataFrame for downstream analysis. |


## Setup

**Requirements:** Python 3.10+

```bash
git clone https://github.com/andrewodonovanucc/ai-literacy-scraper.git
cd ai-literacy-scraper
pip install -r requirements.txt
```

## Usage

### CLI pipeline

```bash
python main.py
```

You'll be prompted with a menu:

```
1. Run Scraper
2. Get Job Details
3. Filter
4. Analyse
5. All
6. Archive old files
7. Exit
```

Select `5` to run the full pipeline end-to-end, or run individual stages as needed.

Combo options are also supported:

| Option | Stages run |
|--------|-----------|
| `12`   | Scrape + Job Details |
| `123`  | Scrape + Job Details + Filter |
| `126`  | Scrape + Job Details + Archive |
| `1236` | Scrape + Job Details + Filter + Archive |
| `1246` | Scrape + Job Details + Analyse + Archive |
| `24`   | Job Details + Analyse |
| `246`  | Job Details + Analyse + Archive |
| `26`   | Job Details + Archive |
| `46`   | Analyse + Archive |

### Streamlit dashboard

A basic dashboard is also available for browsing the latest filtered dataset:

```bash
streamlit run app.py
```

This loads the most recent file from `data/criteria/` and displays it as an interactive table.

## Configuration

All search parameters are in `config.py`:

```python
# Job roles to search for
SEARCH_TERMS = [
    "Lecturer",
    "Professor",
    "Instructional Designer",
    "Educational Developer",
    "Academic Developer",
    "Faculty Position",
]

# Locations to search (country code: display name)
LOCATIONS = {
    "GB": "United Kingdom",
    "IE": "Ireland",
}

# AI-related terms to match in job descriptions
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

REQUEST_DELAY = 1.5  # seconds between requests
```

Modify `SEARCH_TERMS`, `LOCATIONS`, or `AI_TERMS` to adjust the scope of the scrape or the filter criteria. Add or remove entries from `LOCATIONS` to target different countries supported by jobs.ac.uk.

## Project structure

```
ai-literacy-scraper/
├── data/
│   ├── criteria/   # Jobs with salary, hours, contract type, dates, and location added (timestamped JSON)
│   ├── filters/    # Jobs with AI match count and matched sentences added (timestamped JSON)
│   ├── jd/         # Jobs with full job description text added (timestamped JSON)
│   ├── jobs/       # Raw deduplicated job listings from the scraper (timestamped JSON)
│   └── runs/       # Log file for each run (timestamped .log)
├── main.py          # Entry point and menu
├── app.py           # Streamlit dashboard
├── scraper.py       # Fetches job listings from jobs.ac.uk
├── job_details.py   # Fetches full job text and structured criteria per listing
├── ai_filter.py     # Filters postings by AI terminology using regex
├── analyse.py       # Loads filtered data into pandas for analysis
├── config.py        # Search terms, locations, AI terms, currency rates, request config
├── file_handling.py # JSON read/write helpers and file archiving
├── log_setup.py     # Logging configuration
├── parse_salary.py  # Salary string parsing and currency normalisation
└── requirements.txt
```

## Data pipeline

Each stage reads from the most recent file in the relevant input folder and writes a new timestamped file to its output folder. The full chain is:

```
jobs/ → jd/ → criteria/ → filters/
```

The `archive_old_files()` function (option 6) moves all but the most recent file in each folder to `../ai-literacy-scraper-data-backup/`.

## Notes

- The scraper uses a persistent `requests.Session` with cache-busting query parameters to avoid stale CloudFront cached responses from jobs.ac.uk.
- A configurable delay between requests (`REQUEST_DELAY` in `config.py`) is included to avoid hammering the server.
- Salary figures are parsed and normalised to GBP where possible via `parse_salary.py`, with fallback exchange rates defined in `config.py` under `RATES_TO_EUR`.
- Multiple currency formats are supported (£, €, $, NZ$, AU$, CA$, ¥) with longest-match parsing to avoid ambiguity.
- Each job posting captures location (e.g. `UK`, `IE`) extracted from the listing page.
- Progress is shown via `rich` progress bars during scraping and filtering.
- All output is logged to `data/runs/` and written to JSON files for downstream analysis.
- This tool is intended for academic research purposes only. Please respect jobs.ac.uk's terms of service.

## Dependencies

Key packages: `beautifulsoup4`, `requests`, `rich`, `pandas`, `streamlit`, `lxml`, `CurrencyConverter`. Full list in `requirements.txt`.

## Author

Andrew O'Donovan — PhD Researcher, University College Cork  
[github.com/andrewodonovanucc](https://github.com/andrewodonovanucc)

[LinkedIn](https://ie.linkedin.com/in/andrew-o-donovan)