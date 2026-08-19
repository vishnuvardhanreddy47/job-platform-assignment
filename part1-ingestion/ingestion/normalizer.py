"""Turn source-specific fields into validated Job objects."""

import hashlib
import re
from html import unescape
from typing import Dict

from .models import Job


def _clean(value: str) -> str:
    return re.sub(r"\\s+", " ", unescape(value or "")).strip()


def normalize_job(raw: Dict[str, str], source: str) -> Job:
    return Job(
        title=_clean(raw.get("title", "")),
        company=_clean(raw.get("company", "Unknown company")),
        location=_clean(raw.get("location", "Unknown location")),
        description=_clean(raw.get("description", "")),
        url=raw.get("url", ""),
        published=_clean(raw.get("published", "")) or None,
        source=source,
    )


def job_id(job: Job) -> str:
    """Stable identifier: the normalized URL, hashed for compact storage."""
    return hashlib.sha256(str(job.url).encode("utf-8")).hexdigest()
