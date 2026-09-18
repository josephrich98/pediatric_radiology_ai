"""The refresh policy, checked against the URLs the collectors actually build.

A rule that drifts away from its collector fails silently — the refresh just
stops re-fetching that source — so these tests construct each URL the same way
``utils.http_get`` does (``urlencode`` of the collector's own params) rather
than hand-writing a URL that the collector may no longer request.
"""

from __future__ import annotations

import urllib.parse

import pytest

from pedrad_ai import arxiv, cache, config, medrxiv, openalex, pubmed


def _url(base: str, params: dict) -> str:
    return base + "?" + urllib.parse.urlencode(params, doseq=True)


@pytest.fixture(autouse=True)
def _refresh_on():
    cache.enable(window_years=2, export_env=False)
    yield
    cache.disable()


def _verdict(url: str, body: bytes | None = None) -> bool:
    rule, reason = cache.classify(url, body)
    return cache._is_volatile(rule, reason)


# --------------------------------------------------------------------------- #
# PubMed
# --------------------------------------------------------------------------- #
def _esearch_url(term: str) -> str:
    params = pubmed._base_params()
    params.update({"term": term, "retmax": 0, "rettype": "count", "retmode": "json"})
    return _url(pubmed.ESEARCH, params)


def test_pubmed_settled_year_is_kept():
    assert not _verdict(_esearch_url(f"({config.PAPER_DB_QUERY}) AND 2015[pdat]"))


def test_pubmed_current_year_is_refetched():
    assert _verdict(_esearch_url(f"(x) AND {config.END_YEAR}[pdat]"))


def test_pubmed_previous_year_is_refetched():
    assert _verdict(_esearch_url(f"(x) AND {config.END_YEAR - 1}[pdat]"))


def test_pubmed_span_reaching_current_year_is_refetched():
    """The crosstab and era queries use a start:end span, not a single year."""
    assert _verdict(_esearch_url(f"(x) AND {config.START_YEAR}:{config.END_YEAR}[pdat]"))


def test_pubmed_settled_span_is_kept():
    assert not _verdict(_esearch_url("(x) AND 2008:2022[pdat]"))


def test_pubmed_efetch_record_is_kept():
    params = pubmed._base_params()
    params.update({"id": "12345678", "retmode": "xml"})
    assert not _verdict(_url(pubmed.EFETCH, params))


def test_pubmed_doi_lookup_is_kept():
    assert not _verdict(_esearch_url('"10.1148/radiol.2021203957"[doi]'))


# --------------------------------------------------------------------------- #
# Preprints
# --------------------------------------------------------------------------- #
def _arxiv_url(start: int, end: int) -> str:
    params = {
        "search_query": f"(all:pediatric) AND submittedDate:[{start}01010000 TO {end}12312359]",
        "start": 0,
        "max_results": 1,
    }
    return _url(arxiv.API, params)


def test_arxiv_settled_year_is_kept():
    assert not _verdict(_arxiv_url(2015, 2015))


def test_arxiv_current_year_is_refetched():
    assert _verdict(_arxiv_url(config.END_YEAR, config.END_YEAR))


def _epmc_url(start: int, end: int) -> str:
    q = f'{medrxiv._SOURCE_FILTER} AND (TITLE:"x") AND PUB_YEAR:[{start} TO {end}]'
    return _url(medrxiv.API, {"query": q, "format": "json", "pageSize": 1})


def test_medrxiv_settled_year_is_kept():
    assert not _verdict(_epmc_url(2015, 2015))


def test_medrxiv_current_year_is_refetched():
    assert _verdict(_epmc_url(config.END_YEAR, config.END_YEAR))


def test_europepmc_doi_lookup_is_kept():
    """newsletters.resolve_paper hits the same host without a PUB_YEAR filter."""
    url = _url(medrxiv.API, {"query": 'DOI:"10.1038/s41467-024-00000-0"', "format": "json"})
    assert not _verdict(url)


# --------------------------------------------------------------------------- #
# OpenAlex
# --------------------------------------------------------------------------- #
def test_openalex_settled_search_is_kept():
    url = _url(openalex.WORKS, {"filter": "title_and_abstract.search:x,type:preprint,"
                                          "from_publication_date:2015-01-01,to_publication_date:2015-12-31"})
    assert not _verdict(url)


def test_openalex_current_search_is_refetched():
    url = _url(openalex.WORKS, {"filter": f"title_and_abstract.search:x,type:preprint,"
                                          f"from_publication_date:{config.END_YEAR}-01-01,"
                                          f"to_publication_date:{config.END_YEAR}-12-31"})
    assert _verdict(url)


def test_openalex_doi_batch_is_metrics_and_off_by_default():
    url = _url(openalex.WORKS, {"filter": "doi:10.1/a|10.1/b"})
    assert not _verdict(url)
    cache.enable(window_years=2, scopes={"metrics"}, export_env=False)
    assert _verdict(url)


def test_icite_is_metrics_and_off_by_default():
    url = _url("https://icite.od.nih.gov/api/pubs", {"pmids": "1,2,3"})
    assert not _verdict(url)
    cache.enable(window_years=2, scopes={"metrics"}, export_env=False)
    assert _verdict(url)


# --------------------------------------------------------------------------- #
# Newsletters
# --------------------------------------------------------------------------- #
def test_wordpress_listing_is_refetched_but_content_is_kept():
    base = config.NEWSLETTER_SOURCES["The Imaging Wire"]["base"]
    listing = _url(f"{base}/wp-json/wp/v2/posts",
                   {"per_page": 100, "page": 1, "orderby": "date", "order": "asc", "_fields": "id"})
    content = _url(f"{base}/wp-json/wp/v2/posts",
                   {"include": "1,2,3", "per_page": 3, "orderby": "include",
                    "_fields": "id,date,link,title,content"})
    assert _verdict(listing)
    assert not _verdict(content)


def test_rsna_archive_is_refetched_but_articles_are_kept():
    assert _verdict(config.NEWSLETTER_SOURCES["RSNA News"]["archive"])
    assert not _verdict("https://www.rsna.org/news/2026/january/some-story")


def test_tldr_dated_page_is_kept():
    """A new weekday is a new URL, so it already misses the cache."""
    assert not _verdict("https://tldr.tech/ai/2026-09-17")


# --------------------------------------------------------------------------- #
# Conferences / patents
# --------------------------------------------------------------------------- #
def test_venue_accepted_list_is_refetched():
    assert _verdict(f"https://neurips.cc/static/virtual/data/neurips-{config.END_YEAR}-orals-posters.json")


def test_dblp_is_opt_in():
    url = _url("https://dblp.org/search/publ/api", {"q": "venue:CVPR: segmentation", "format": "json"})
    assert not _verdict(url)
    cache.enable(window_years=2, scopes={"dblp"}, export_env=False)
    assert _verdict(url)


# --------------------------------------------------------------------------- #
# Safety properties
# --------------------------------------------------------------------------- #
def test_unmatched_urls_are_kept():
    """A refresh may only re-fetch what a rule names."""
    assert not _verdict("https://example.org/something/we/never/thought/about")


def test_nothing_is_volatile_when_refresh_is_off():
    cache.disable()
    hot = _esearch_url(f"(x) AND {config.END_YEAR}[pdat]")
    assert not cache.should_refetch(hot, __import__("pathlib").Path("/nonexistent"))


def test_window_can_be_widened():
    url = _esearch_url("(x) AND 2023[pdat]")
    assert not _verdict(url)
    cache.enable(window_years=config.END_YEAR - 2023 + 1, export_env=False)
    assert _verdict(url)


# --------------------------------------------------------------------------- #
# Soft errors: HTTP 200 with a failure body (NCBI does this under load)
# --------------------------------------------------------------------------- #
_SOFT = '{"header":{"type":"esearch"},"esearchresult":{"ERROR":"Search Backend failed: 502"}}'
_GOOD = '{"header":{"type":"esearch"},"esearchresult":{"count":"42"}}'


class _FakeResponse:
    def __init__(self, text: str):
        self._text = text

    def read(self):
        return self._text.encode()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _stub_urlopen(monkeypatch, texts):
    """Serve ``texts`` in order; record how many calls were made."""
    from pedrad_ai import utils
    calls = {"n": 0}

    def fake(req, timeout=None):
        i = min(calls["n"], len(texts) - 1)
        calls["n"] += 1
        return _FakeResponse(texts[i])

    monkeypatch.setattr(utils.urllib.request, "urlopen", fake)
    monkeypatch.setattr(utils.time, "sleep", lambda *_a, **_k: None)
    return calls


def test_soft_error_detection():
    from pedrad_ai import utils
    assert utils.is_soft_error(_SOFT)
    assert not utils.is_soft_error(_GOOD)
    # A field literally named ERROR in some other payload is not an NCBI failure.
    assert not utils.is_soft_error('{"message":{"ERROR":"nope"}}')


def test_soft_error_is_never_written_to_the_cache(monkeypatch, tmp_path):
    from pedrad_ai import utils
    monkeypatch.setattr(utils, "CACHE_DIR", tmp_path)
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?term=x"
    _stub_urlopen(monkeypatch, [_SOFT, _SOFT, _GOOD])
    assert utils.http_get(url, max_retries=3, pause=0.0) == _GOOD
    assert utils._cache_path(url, None).read_text() == _GOOD


def test_soft_error_never_overwrites_a_good_cached_value(monkeypatch, tmp_path):
    """The failure that started this: a refresh must not poison a working entry."""
    from pedrad_ai import utils
    monkeypatch.setattr(utils, "CACHE_DIR", tmp_path)
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
           f"?term=(x)+AND+{config.END_YEAR}%5Bpdat%5D")
    utils._cache_path(url, None).write_text(_GOOD)
    _stub_urlopen(monkeypatch, [_SOFT])            # every retry fails softly
    assert utils.http_get(url, max_retries=2, pause=0.0) == _GOOD   # stale fallback
    assert utils._cache_path(url, None).read_text() == _GOOD        # cache intact


def test_poisoned_cache_entry_heals_on_next_request(monkeypatch, tmp_path):
    """A poisoned entry from an earlier run is re-fetched even with refresh off."""
    from pedrad_ai import utils
    cache.disable()
    monkeypatch.setattr(utils, "CACHE_DIR", tmp_path)
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?term=y"
    utils._cache_path(url, None).write_text(_SOFT)
    _stub_urlopen(monkeypatch, [_GOOD])
    assert utils.http_get(url, max_retries=2, pause=0.0) == _GOOD
    assert utils._cache_path(url, None).read_text() == _GOOD


def test_refresh_falls_back_to_cache_when_the_network_is_down(monkeypatch, tmp_path):
    """One unreachable service must not take a refresh down."""
    from pedrad_ai import utils
    monkeypatch.setattr(utils, "CACHE_DIR", tmp_path)
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
           f"?term=(x)+AND+{config.END_YEAR}%5Bpdat%5D")
    utils._cache_path(url, None).write_text(_GOOD)

    def boom(req, timeout=None):
        raise utils.urllib.error.URLError("no network")

    monkeypatch.setattr(utils.urllib.request, "urlopen", boom)
    monkeypatch.setattr(utils.time, "sleep", lambda *_a, **_k: None)
    assert utils.http_get(url, max_retries=2, pause=0.0) == _GOOD


def test_settled_year_makes_no_request_at_all(monkeypatch, tmp_path):
    """The point of the live window: a 2015 count is served from disk."""
    from pedrad_ai import utils
    monkeypatch.setattr(utils, "CACHE_DIR", tmp_path)
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
           "?term=(x)+AND+2015%5Bpdat%5D")
    utils._cache_path(url, None).write_text(_GOOD)
    calls = _stub_urlopen(monkeypatch, [_GOOD])
    assert utils.http_get(url, pause=0.0) == _GOOD
    assert calls["n"] == 0


def test_bare_pub_year_does_not_crash_the_classifier():
    """Europe PMC accepts PUB_YEAR:2026 as well as PUB_YEAR:[a TO b]."""
    settled = _url(medrxiv.API, {"query": f'{medrxiv._SOURCE_FILTER} AND (x) AND PUB_YEAR:2015'})
    live = _url(medrxiv.API, {"query": f'{medrxiv._SOURCE_FILTER} AND (x) AND PUB_YEAR:{config.END_YEAR}'})
    assert not _verdict(settled)
    assert _verdict(live)


def test_settled_venue_list_is_kept_but_live_one_is_refetched():
    assert not _verdict("https://neurips.cc/static/virtual/data/neurips-2019-orals-posters.json")
    assert _verdict(f"https://openaccess.thecvf.com/CVPR{config.END_YEAR}?day=all")


def test_a_broken_year_extractor_cannot_break_a_request(monkeypatch):
    """The policy fails closed: on error the cached response is still served."""
    monkeypatch.setattr(cache, "_pubmed_years", lambda u: 1 / 0)
    bad = cache.Rule("boom", cache.WINDOW, lambda u: "esearch.fcgi" in u,
                     years=lambda u: 1 / 0)
    monkeypatch.setattr(cache, "_RULES", [bad] + list(cache._RULES))
    # A WINDOW rule whose extractor raises is treated as "no year" -> re-fetched,
    # never as an exception escaping into the collector.
    assert _verdict(_esearch_url("(x) AND 2015[pdat]")) is True


def test_refresh_mode_is_inherited_by_subprocesses():
    """refresh.py exports the settings; run_step's children must pick them up."""
    import subprocess
    import sys

    cache.enable(window_years=4, scopes={"metrics"})   # export_env defaults to True
    try:
        out = subprocess.run(
            [sys.executable, "-c",
             "from pedrad_ai import cache; "
             "print(cache.is_enabled(), cache.live_window(), sorted(cache._state.scopes))"],
            capture_output=True, text=True, check=True,
        ).stdout.strip().splitlines()[0]
    finally:
        cache.disable()
    assert out == f"True ({config.END_YEAR - 3}, {config.END_YEAR}) ['metrics']", out


def test_disable_clears_the_exported_environment():
    import os
    cache.enable(window_years=2)
    assert os.environ.get(cache.ENV_ENABLED) == "1"
    cache.disable()
    assert cache.ENV_ENABLED not in os.environ
