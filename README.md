# AI Literacy Scraper

A Python tool for scraping and analysing academic job postings on [jobs.ac.uk](https://www.jobs.ac.uk) to investigate the prevalence of AI literacy requirements in higher education roles. Built as part of a PhD research project examining how institutions are responding to generative AI.

## What it does

The tool runs as a pipeline with four stages, each of which can be executed independently or all together:

| Stage | What it does |
|-------|-------------|
| 1. **Scrape** | Searches jobs.ac.uk for academic roles (Lecturer, Professor, Instructional Designer, etc.) and collects job listings across all result pages. Deduplicates by URL and saves to JSON. |
| 2. **Job Details** | Fetches the full text and structured criteria (salary, hours, contract type) for each job posting by following the individual listing URLs. |
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
| `26`   | Job Details + Archive |

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

# AI-related terms to match in job descriptions
AI_TERMS = [
    "artificial intelligence",
    "ai literacy",
    "large language model",
    "generative ai",
    "llm",
    "chatgpt",
    # ... and more
]

REQUEST_DELAY = 1  # seconds between requests
```

Modify `SEARCH_TERMS` or `AI_TERMS` to adjust the scope of the scrape or the filter criteria.

## Project structure

```
ai-literacy-scraper/
├── data/
│   ├── criteria/   # Jobs with salary, hours, and contract type added (timestamped JSON)
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
├── config.py        # Search terms, AI terms, request config
├── file_handling.py # JSON read/write helpers and file archiving
├── log_setup.py     # Logging configuration
└── requirements.txt
```

## Data pipeline

Each stage reads from the most recent file in the relevant input folder and writes a new timestamped file to its output folder. The full chain is:

```
jobs/ → jd/ → criteria/ → filters/
```

The `archive_old_files()` function (option 6) moves all but the most recent file in each folder to `../ai-literacy-scraper-data-backup/`.

## Notes

- The scraper includes a configurable delay between requests (`REQUEST_DELAY` in `config.py`) to avoid hammering the server.
- Progress is shown via `rich` progress bars during scraping and filtering.
- All output is logged to `data/runs/` and written to JSON files for downstream analysis.
- This tool is intended for academic research purposes only. Please respect jobs.ac.uk's terms of service.

## Dependencies

Key packages: `beautifulsoup4`, `requests`, `rich`, `pandas`, `streamlit`, `lxml`. Full list in `requirements.txt`.

## Author

Andrew O'Donovan — PhD Researcher, University College Cork  
[github.com/andrewodonovanucc](https://github.com/andrewodonovanucc)

[LinkedIn](https://ie.linkedin.com/in/andrew-o-donovan)