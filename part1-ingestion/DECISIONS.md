# Decisions

## 1. Why this ingestion strategy?

I chose an authorized public job API/RSS adapter instead of browser scraping. The obvious alternative was automating job-board pages with a headless browser, but that creates a larger detection surface, is more fragile when markup changes, and can cross authentication, CAPTCHA, robots, rate-limit, or terms-of-service boundaries. The demo therefore uses Arbeitnow's documented public Job Board API, which requires no API key, and keeps the fetcher generic enough to support an authorized RSS source. If the primary source fails or returns an empty first response, a controlled local RSS fixture keeps the service demonstrable without pretending the fallback is live data.

The fetcher uses a conservative request cadence, timeout, retries, exponential backoff, and explicit identification as a demo client. It does not attempt to evade bot detection or access controls.

## 2. Time-limit trade-off

I used an in-memory store instead of a database. This keeps the assignment small and makes URL-based deduplication easy to demonstrate, but jobs disappear when the process restarts and multiple instances do not share data. With a full week, I would add Postgres or SQLite with a unique URL constraint, retention rules, source-level metrics, scheduled ingestion, and contract/integration tests against documented authorized fixtures.

## 3. AI assistance and verification

AI assistance was used to scaffold the module layout, draft FastAPI routes, suggest retry/fallback structure, and help prepare tests and documentation. I personally verified the source contract, inspected the implementation, tested the service locally, fixed the fetcher indentation issue, ran the test suite, checked repeated-ingestion deduplication, and verified that a blocked source falls back to the controlled fixture. I kept the design free of scraping or access-control bypasses and made sure the implementation remains small enough to explain line by line.
