# Job Ingestion Service

A beginner-friendly FastAPI service that reads job listings from an authorized public RSS/API source, validates and normalizes them, and stores them in memory. The default source is a controlled local mock RSS feed, so the demo works without scraping or depending on a third-party site.

## Architecture

`POST /ingest` calls `ingestion/fetcher.py` for an authorized HTTP feed, parses RSS in `parser.py`, normalizes and validates records in `normalizer.py` and `models.py`, then deduplicates them in `storage.py`. A failed or empty initial source falls back to the local mock feed. Existing jobs are preserved when a previously populated source suddenly returns zero jobs.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the detailed design and Mermaid diagram.

## Installation

Use Python 3.11 or newer:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Local Setup

The service defaults to `mock://local/jobs`. To use a real source, set `JOB_FEED_URL` to an RSS URL that you are authorized to access and that permits automated requests:

```powershell
$env:JOB_FEED_URL = "https://your-authorized-source.example/jobs.xml"
```

Do not use this project to scrape LinkedIn, Indeed, Naukri, Wellfound, or any protected website. Do not bypass authentication, CAPTCHA, bot detection, robots restrictions, rate limits, or IP bans.

## Running the API

```powershell
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive OpenAPI documentation.

## Testing

```powershell
pytest -q
```

Tests cover RSS parsing, normalization, URL-based deduplication, and fallback behavior.

## API Endpoints

- `GET /` returns service status.
- `GET /health` returns health and the current in-memory job count.
- `GET /jobs` returns normalized jobs.
- `POST /ingest` fetches, parses, validates, deduplicates, and stores jobs.

Example:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/ingest
Invoke-RestMethod http://127.0.0.1:8000/jobs
```

## Deployment on Render

`render.yaml` contains a minimal Render web-service definition. Connect the repository in Render, or create a Python web service with:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Optional environment variable: `JOB_FEED_URL`

This version uses in-memory storage, so jobs reset when the service restarts. A production version would add a durable database after the source contract and retention policy are known.
