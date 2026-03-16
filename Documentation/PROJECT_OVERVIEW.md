# Mass-Arb: Mass Arbitration & Class Action Monitor

## What It Does

Mass-Arb is an automated monitoring system that tracks **13 law firm websites** for newly published mass arbitration and class action lawsuit pages. It runs daily, discovers new case URLs, stores them in a local database, and emails a digest report to the team.

**In short:** It answers the question *"What new cases did law firms announce today?"* — automatically, every morning.

---

## How It Works (High-Level Flow)

```
Daily Cron Job (e.g., 4:39 AM)
        |
        v
  main.py launches ScraperOrchestrator
        |
        v
  Runs 13 scrapers sequentially
  (each scraper targets a specific law firm website)
        |
        v
  Each scraper:
    1. Fetches the target web page(s) or sitemap
    2. Extracts case/investigation URLs
    3. Filters by date (only keeps items from Jan 1, 2026 onward)
    4. Deduplicates against the local JSON database
    5. Saves any genuinely new URLs to disk
        |
        v
  Orchestrator collects results from all 13 scrapers
        |
        v
  Sends a styled HTML email digest
  (subject: "Daily Mass Arbitration Links")
  to configured recipients via Gmail SMTP
```

---

## Monitored Law Firm Sources (13 Total)

| # | Source | Website | Scraping Method |
|---|--------|---------|-----------------|
| 1 | Class Action Legal Help | classactionlegalhelp.co | HTML page |
| 2 | Gutride Safier | gutridesafier.com | HTML (2 pages) |
| 3 | Find Class Action / ClassAction.org | findclassaction.jotform.com, classaction.org | HTML (2 domains) |
| 4 | Shamis & Gentile | shamisgentile.com | HTML page |
| 5 | Toppe Law Firm | toppefirm.com | XML Sitemap |
| 6 | Consumers Protection Law | consumersprotectionlaw.com | HTML page |
| 7 | Consumer Legal Action | consumerlegalaction.com | HTML page |
| 8 | Crosner Legal | crosnerlegal.com | XML Sitemap index |
| 9 | Edelson PC | edelson.com | HTML page |
| 10 | Stop Consumer Harm | stopconsumerharm.com | XML Sitemap |
| 11 | EKSM | eksm.com | HTML page |
| 12 | FMFPC | fmfpc.com | Hybrid (3 sitemaps + 1 HTML) |
| 13 | Lantern Labaton | lantern.labaton.com | Paginated HTML (up to 50 pages) |

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.8+ | Core runtime |
| HTTP Client | `requests` | Fetches web pages |
| HTML Parser | `BeautifulSoup4` + `lxml` | Extracts URLs and dates from HTML/XML |
| Data Storage | JSON files (local) | Persists discovered URLs with deduplication |
| Email | `smtplib` (SMTP/TLS) | Sends daily digest via Gmail |
| Secrets | `python-dotenv` | Loads credentials from external file |
| Scheduling | OS-level cron (Linux/Mac) or Task Scheduler (Windows) | Triggers daily runs |

No external databases, cloud services, or paid APIs are required.

---

## Project Structure

```
Mass-Arb/
├── main.py                  # Entry point - runs all scrapers and sends email
├── setup.py                 # One-time setup/installation helper
├── run_examples.py          # Interactive menu for running scrapers individually
├── requirements.txt         # Python dependencies (pinned versions)
│
├── config/
│   └── settings.py          # All configuration: URLs, email, scraping parameters
│
├── scrapers/
│   ├── base_scraper.py      # Shared logic (HTTP, parsing, date filtering, retries)
│   └── [13 scraper files]   # One file per law firm, each ~50-150 lines
│
├── utils/
│   ├── storage.py           # JSON-based URL database with deduplication
│   ├── email_sender.py      # HTML email construction and SMTP delivery
│   └── logger.py            # Logging to file + console
│
├── data/                    # JSON database files (one per source)
├── logs/                    # Rotating log file (scraper.log)
└── Documentation/           # Project documentation
```

---

## Key Design Decisions

### 1. Incremental Scraping with Deduplication
Each run only adds **genuinely new URLs**. Previously seen URLs are skipped via O(1) set-based lookup. This makes repeated runs safe and efficient.

### 2. Graceful Error Handling
If one scraper fails (e.g., a website is down or returns 403), the remaining 12 scrapers continue running. Failures are logged and included in the email report so the team is aware.

### 3. Date-Based Filtering
URLs are filtered to only include content published on or after **January 1, 2026**. If a date cannot be determined from the page, the URL is still kept (conservative approach to avoid missing new cases).

### 4. Retry Logic
HTTP requests automatically retry up to 3 times with exponential backoff, handling transient network issues without manual intervention.

### 5. Credential Security
SMTP credentials are stored in a separate secrets file **outside the repository**, never committed to version control.

---

## Data Storage Format

Each source has a JSON file in `data/` (e.g., `toppefirm_urls.json`):

```json
{
  "source": "Toppe Law Firm",
  "last_updated": "2026-03-13T04:39:16.016677",
  "total_entries": 3,
  "cutoff_date": "2026-01-01",
  "entries": [
    {
      "url": "https://www.toppefirm.com/example-case",
      "date": "2026-01-15T00:00:00",
      "scraped_at": "2026-01-20T02:04:11.942511"
    }
  ]
}
```

Each entry records: the case URL, the publication date (if found), and when it was first discovered.

---

## Email Report

The daily email includes:
- **Summary block**: total sources scraped, successes/failures, new URLs found
- **Per-source sections**: status indicator, count of new URLs, clickable links to each new case page
- **Error details**: for any scrapers that failed, the error message is included

Recipients are configured via environment variables (currently delivers to two team members).

---

## Running the System

**Daily automated run** (already configured via cron):
```bash
python main.py
```

**One-time setup** (for new environments):
```bash
python setup.py
```

**Interactive testing** (run individual scrapers):
```bash
python run_examples.py
```

---

## Architecture Diagram

```
                    ┌──────────────┐
                    │   Cron Job   │
                    │  (daily)     │
                    └──────┬───────┘
                           │
                           v
                    ┌──────────────┐
                    │   main.py    │
                    │ Orchestrator │
                    └──────┬───────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            v              v              v
     ┌────────────┐ ┌────────────┐ ┌────────────┐
     │ Scraper #1 │ │ Scraper #2 │ │   ... #13  │
     │ (inherits  │ │ (inherits  │ │ (inherits  │
     │  BaseScrpr)│ │  BaseScrpr)│ │  BaseScrpr)│
     └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
           │               │              │
           v               v              v
     ┌────────────┐ ┌────────────┐ ┌────────────┐
     │  Law Firm  │ │  Law Firm  │ │  Law Firm  │
     │  Website   │ │  Website   │ │  Website   │
     └────────────┘ └────────────┘ └────────────┘
           │               │              │
           └───────────┬───┘──────────────┘
                       │
                       v
              ┌────────────────┐
              │  URLStorage    │
              │  (JSON files)  │
              │  Deduplication │
              └────────┬───────┘
                       │
                       v
              ┌────────────────┐
              │  EmailSender   │
              │  (HTML digest  │
              │   via Gmail)   │
              └────────┬───────┘
                       │
                       v
              ┌────────────────┐
              │  Team Inbox    │
              └────────────────┘
```

---

## Current Status (as of March 13, 2026)

- **11 of 13 scrapers** functioning correctly
- **2 scrapers** intermittently fail due to 403 responses (classactionlegalhelp, edelson) — these sites may have added bot detection
- **~850 total URLs** stored across all sources
- System has been running daily since **January 20, 2026**

---

## Deployment

The system runs on:
- **macOS** (local development, Python 3.14 via Homebrew)
- **Linux/Ubuntu** (production, scheduled via cron)

No Docker, cloud infrastructure, or external services beyond Gmail SMTP are needed.
