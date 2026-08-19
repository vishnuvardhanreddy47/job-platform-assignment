"""Parse RSS XML and supported public job APIs into source-agnostic dictionaries."""

import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, List


def _text(item: ET.Element, name: str) -> str:
    value = item.findtext(name)
    return (value or "").strip()


def parse_rss(xml_text: str) -> List[Dict[str, str]]:
    root = ET.fromstring(xml_text)

    jobs: List[Dict[str, str]] = []

    for item in root.findall(".//item"):
        jobs.append(
            {
                "title": _text(item, "title"),
                "company": (
                    _text(item, "{https://example.com/jobs}company")
                    or _text(item, "company")
                ),
                "location": (
                    _text(item, "{https://example.com/jobs}location")
                    or _text(item, "location")
                ),
                "description": _text(item, "description"),
                "url": _text(item, "link"),
                "published": _text(item, "pubDate"),
            }
        )

    return jobs


def parse_job_api(payload: Any) -> List[Dict[str, str]]:
    """Parse Arbeitnow's public JSON job-board format.

    The API exposes jobs under a top-level ``data`` array and does not
    require an API key.
    """
    if isinstance(payload, str):
        payload = json.loads(payload)

    if not isinstance(payload, dict):
        raise ValueError("Job API response must be a JSON object")

    records = payload.get("data")
    if not isinstance(records, list):
        raise ValueError("Job API response is missing a data array")

    jobs: List[Dict[str, str]] = []

    for record in records:
        if not isinstance(record, dict):
            continue

        created_at = record.get("created_at")
        published = ""
        if isinstance(created_at, (int, float)):
            published = datetime.fromtimestamp(
                created_at, tz=timezone.utc
            ).isoformat()

        jobs.append(
            {
                "title": str(record.get("title") or ""),
                "company": str(record.get("company_name") or ""),
                "location": str(record.get("location") or ""),
                "description": str(record.get("description") or ""),
                "url": str(record.get("url") or ""),
                "published": published,
            }
        )

    return jobs
