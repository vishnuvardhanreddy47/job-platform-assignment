"""Parse RSS XML into small, source-agnostic dictionaries."""

import xml.etree.ElementTree as ET
from typing import Dict, List


def _text(item: ET.Element, name: str) -> str:
    value = item.findtext(name)
    return (value or "").strip()


def parse_rss(xml_text: str) -> List[Dict[str, str]]:
    root = ET.fromstring(xml_text)
    jobs = []
    for item in root.findall(".//item"):
        jobs.append(
            {
                "title": _text(item, "title"),
                "company": _text(item, "{https://example.com/jobs}company") or _text(item, "company"),
                "location": _text(item, "{https://example.com/jobs}location") or _text(item, "location"),
                "description": _text(item, "description"),
                "url": _text(item, "link"),
                "published": _text(item, "pubDate"),
            }
        )
    return jobs
