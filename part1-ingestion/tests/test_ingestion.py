import app as app_module
from ingestion.models import Job
from ingestion.normalizer import job_id, normalize_job
from ingestion.parser import parse_rss
from ingestion.storage import JobStore


RSS = """<rss><channel><item><title>  API Developer  </title><company>Acme</company><location>Remote</location><description>Hello &amp; welcome</description><link>https://example.com/jobs/1</link><pubDate>Today</pubDate></item></channel></rss>"""


def test_parser_reads_rss_fields():
    result = parse_rss(RSS)
    assert result[0]["title"] == "API Developer"
    assert result[0]["url"] == "https://example.com/jobs/1"


def test_normalization_cleans_text_and_validates():
    job = normalize_job(parse_rss(RSS)[0], "mock://test")
    assert isinstance(job, Job)
    assert job.description == "Hello & welcome"
    assert job.source == "mock://test"


def test_store_deduplicates_by_url():
    job = normalize_job(parse_rss(RSS)[0], "mock://test")
    store = JobStore()
    assert store.add_many([job, job]) == 1
    assert job_id(store.all()[0]) == job_id(job)


def test_ingest_uses_fallback_when_source_fails(monkeypatch):
    monkeypatch.setattr(app_module, "SOURCE_URL", "https://authorized.example/jobs.xml")
    monkeypatch.setattr(app_module.fetcher, "fetch", lambda url: (_ for _ in ()).throw(RuntimeError("offline")))
    monkeypatch.setattr(app_module, "store", JobStore())
    result = app_module.ingest_from_source()
    assert result.used_fallback is True
    assert result.jobs_added == 2
