"""pedrad_ai: tools for measuring the growth and landscape of radiology AI,
with a focus on pediatric radiology.

The package provides small, dependency-light collectors that query public APIs
(PubMed, PatentsView, Crossref, Semantic Scholar, GitHub, OpenReview) and a set
of analysis helpers that turn the raw pulls into time series and landscape
tables. Results are written to ``data/`` and figures/reports are generated from
there.
"""

from __future__ import annotations

__version__ = "0.1.0"

from . import config, utils  # noqa: F401

__all__ = ["config", "utils", "__version__"]
