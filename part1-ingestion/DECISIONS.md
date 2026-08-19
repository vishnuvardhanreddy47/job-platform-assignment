# Decisions

## 1. Why this ingestion strategy?

I chose an authorized RSS/API adapter with a controlled local mock fallback. The obvious alternative was scraping job-board web pages with browser automation. That alternative is more fragile, harder to test, and can violate terms or encounter authentication, CAPTCHA, robots, bot-detection, and rate-limit controls. RSS/API data is structured, easier to parse, and appropriate for a transparent demo. The mock source keeps the application runnable when a reliable authorized public feed is unavailable.

## 2. Time-limit trade-off

I used an in-memory store instead of a database. This keeps the assignment small and makes URL deduplication easy to explain, but jobs disappear when the process restarts and multiple instances do not share data. With a full week, I would add SQLite or Postgres with a unique URL constraint, migrations, retention rules, source-level metrics, and integration tests against a documented authorized fixture.

## 3. AI assistance and verification

AI assistance was used to scaffold the module layout, draft the FastAPI routes, suggest retry/fallback structure, and prepare test cases and documentation. I personally verified the files, kept the design free of scraping or access-control bypasses, installed the pinned dependencies in the project virtual environment, and ran the test suite. The tests cover parsing, normalization, URL deduplication, and fallback behavior; the implementation remains intentionally small enough to inspect and explain line by line.
