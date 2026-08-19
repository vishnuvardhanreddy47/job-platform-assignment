from typing import Dict, Iterable, List

from .models import Job
from .normalizer import job_id


class JobStore:
    """Simple in-memory store suitable for this assignment's single process."""

    def __init__(self) -> None:
        self._jobs: Dict[str, Job] = {}

    def add_many(self, jobs: Iterable[Job]) -> int:
        added = 0
        for job in jobs:
            identifier = job_id(job)
            if identifier not in self._jobs:
                self._jobs[identifier] = job
                added += 1
        return added

    def all(self) -> List[Job]:
        return list(self._jobs.values())

    def count(self) -> int:
        return len(self._jobs)
