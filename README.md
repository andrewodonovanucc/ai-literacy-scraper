# AI LITERACY SCRAPER

A Python tool for scraping and analysing academic job postings on [jobs.ac.uk](https://www.jobs.ac.uk) to investigate the prevalence of AI literacy requirements in higher education roles. Built as part of a PhD research project examining how institutions are responding to generative AI.

## What it does

The tool runs as a pipeline with four stages, each of which can be executed independently or all together:

1. **Scrape** - Searches jobs.ac.uk for academic roles (Lecturer, Professor, Instructional Designer, etc.) and collects job listings across all result pages. Deduplicates by URL and saves to JSON.
2. **Job Details** - Fetches the full text of each job posting by following the individual listing URLs.
3. **Filter** - Scans job descriptions for AI-related terminology (e.g. `ai literacy`, `large language model`, `generative ai`, `chatgpt`) to identify postings that reference AI.
4. **Analyse** - Runs analysis across the filtered dataset to surface patterns and findings.


## Setup

**Requirements:** Python 3.10+

```bash
git clone https://github.com/andrewodonovanucc/ai-literacy-scraper.git
cd ai-literacy-scraper
pip install -r requirements.txt
```

## Usage

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
6. Exit
```

Select `5` to run the full pipeline end-to-end, or run individual stages as needed. 

*Combo options `12` (scrape and details) and `123` (scrape + details + filter, no analysis) are also supported.*

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
├── data
├──     criteria/     # Storage for scraped jobs in a timestamped JSON format - criteria added.
├──     filters/      # Storage for scraped jobs in a timestamped JSON format - AI Matches count added.
├──     jd/           # Storage for scraped job descriptions in a timestamped JSON format
├──     jobs/         # Storage for scraped jobs in a timestamped JSON format
├──     runs/         # Storage for the output of each individual run in a timestamped JSON format
├── main.py           # Entry point and menu
├── scraper.py        # Fetches job listings from jobs.ac.uk
├── job_details.py    # Fetches full text of each job posting
├── ai_filter.py      # Filters postings by AI terminology
├── analyse.py        # Analysis and reporting
├── config.py         # Search terms, AI terms, request config
├── file_handling.py  # JSON read/write helpers
├── log_setup.py      # Logging configuration
└── requirements.txt
```

## Notes

- The scraper includes a configurable delay between requests (`REQUEST_DELAY` in `config.py`) to avoid hammering the server.
- Progress is shown via `rich` progress bars during scraping.
- All output is logged and written to JSON files for downstream analysis.
- This tool is intended for academic research purposes only. Please respect jobs.ac.uk's terms of service.

## Dependencies

Key packages: `beautifulsoup4`, `requests`, `rich`, `pandas`, `matplotlib`, `lxml`. Full list in `requirements.txt`.

## Author

Andrew O'Donovan — PhD Researcher, University College Cork  
[github.com/andrewodonovanucc](https://github.com/andrewodonovanucc)