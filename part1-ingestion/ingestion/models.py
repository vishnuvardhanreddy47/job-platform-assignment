from typing import Optional

from pydantic import BaseModel, HttpUrl


class Job(BaseModel):
    title: str
    company: str
    location: str
    description: str
    url: HttpUrl
    published: Optional[str] = None
    source: str


class IngestResponse(BaseModel):
    source: str
    jobs_seen: int
    jobs_added: int
    used_fallback: bool
    message: str
