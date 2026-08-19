import logging
import os
from typing import List

from fastapi import FastAPI, HTTPException

from ingestion.fetcher import FeedFetcher
from ingestion.models import IngestResponse, Job
from ingestion.normalizer import normalize_job
from ingestion.parser import parse_job_api, parse_rss
from ingestion.storage import JobStore

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(title="Job Ingestion Service", version="1.1.0")

store = JobStore()
fetcher = FeedFetcher()

SOURCE_URL = os.getenv(
    "JOB_FEED_URL",
    "https://www.arbeitnow.com/api/job-board-api",
)

MOCK_RSS = """<?xml version="1.0"?>
<rss version="2.0" xmlns:jobs="https://example.com/jobs">
<channel>
<title>Controlled local job feed</title>
<item>
<title>Python Backend Engineer</title>
<jobs:company>Example Labs</jobs:company>
<jobs:location>Remote</jobs:location>
<description>Build reliable APIs with Python and FastAPI.</description>
<link>https://example.com/jobs/python-backend-engineer</link>
<pubDate>2026-08-18</pubDate>
</item>
<item>
<title>Data Platform Engineer</title>
<jobs:company>Northwind Analytics</jobs:company>
<jobs:location>New York, NY</jobs:location>
<description>Improve pipelines and data quality for a growing platform.</description>
<link>https://example.com/jobs/data-platform-engineer</link>
<pubDate>2026-08-17</pubDate>
</item>
</channel>
</rss>"""


def read_source(url: str):
    if url.startswith("mock://"):
        return "rss", MOCK_RSS

    if "arbeitnow.com/api/job-board-api" in url:
        return "json", fetcher.fetch_json(url)

    return "rss", fetcher.fetch(url)


def ingest_from_source() -> IngestResponse:
    used_fallback = False
    source = SOURCE_URL

    try:
        source_type, payload = read_source(SOURCE_URL)

        if source_type == "json":
            raw_jobs = parse_job_api(payload)
        else:
            raw_jobs = parse_rss(payload)

        if not raw_jobs:
            if store.count():
                logger.warning(
                    "Source returned zero jobs; preserving %s existing jobs",
                    store.count(),
                )
                return IngestResponse(
                    source=source,
                    jobs_seen=0,
                    jobs_added=0,
                    used_fallback=False,
                    message="Empty response ignored",
                )

            raise ValueError("Source returned zero jobs")

    except Exception as error:
        logger.warning(
            "Source unavailable (%s); using controlled mock feed",
            error,
        )
        source = "mock://local/jobs"
        used_fallback = True
        raw_jobs = parse_rss(MOCK_RSS)

    jobs: List[Job] = []

    for raw_job in raw_jobs:
        try:
            jobs.append(normalize_job(raw_job, source))
        except Exception:
            logger.exception("Skipping invalid job record")

    added = store.add_many(jobs)

    logger.info(
        "Ingested %s jobs, added %s new jobs",
        len(jobs),
        added,
    )

    return IngestResponse(
        source=source,
        jobs_seen=len(jobs),
        jobs_added=added,
        used_fallback=used_fallback,
        message="Ingestion completed",
    )


@app.get("/")
def root() -> dict:
    return {"service": "job-ingestion", "status": "running"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "jobs": store.count()}


@app.get("/jobs", response_model=List[Job])
def jobs() -> List[Job]:
    return store.all()


@app.post("/ingest", response_model=IngestResponse)
def ingest() -> IngestResponse:
    try:
        return ingest_from_source()
    except Exception as error:
        logger.exception("Ingestion failed unexpectedly")
        raise HTTPException(status_code=500, detail=str(error))
