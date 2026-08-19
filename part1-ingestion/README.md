# Job Ingestion Service

A small FastAPI ingestion service that reads job listings from an authorized public job API/RSS source, validates and normalizes them, and stores them in memory.

## Source

The demo defaults to the public **Arbeitnow Job Board API**:

`https://www.arbeitnow.com/api/job-board-api`

Arbeitnow documents this API as a free job search API that requires no API key. The service can also be pointed at another authorized RSS/API source with `JOB_FEED_URL`.

If the configured source fails, the service falls back to a controlled local RSS fixture. The response explicitly reports `used_fallback: true`, so fallback data is never presented as live source data.

## Architecture

`POST /ingest` fetches the configured source with timeout, retries, exponential backoff, and pacing. The payload is parsed by the source adapter, normalized and validated by `normalizer.py` and `models.py`, then deduplicated by URL in `storage.py`.

See `docs/ARCHITECTURE.md` and `DECISIONS.md`.

## Local setup

```powershell
cd part1-ingestion
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Verify

```powershell
python -m pytest
Invoke-RestMethod -Method Post http://127.0.0.1:8000/ingest
Invoke-RestMethod http://127.0.0.1:8000/jobs
Invoke-RestMethod -Method Post http://127.0.0.1:8000/ingest
```

The second ingestion should normally add `0` new jobs because the store deduplicates by normalized URL.

## Deployment

The included `render.yaml` is configured for a Render Python web service with:

- Root directory: `part1-ingestion`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- `JOB_FEED_URL`: Arbeitnow public API

The service uses in-memory storage, so data resets after a restart. A production version would add durable storage and source-specific observability.
