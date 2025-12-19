"""
Knowledge Base utilities for MASO applications

Provides:
- KBDiffService: Compare KB content and generate structured diffs
- KBSearchEngine: Stateless search engine for KB content
- LLMContextBuilder: Build context strings for LLM prompts
"""

from .diff_service import KBDiffService, get_diff_service
from .types import (
    FAQItem,
    ArrangementItem,
    ContentSection,
    BusinessInfo,
    KBContent,
    SearchResult,
    QuerySignals,
    DiffChange,
    DiffSummary,
)
from .constants import (
    STOPWORDS,
    SYNONYM_MAP,
    QUERY_EXPANSIONS,
    KIDS_KEYWORDS,
    BEDRIJF_KEYWORDS,
    PRICING_KEYWORDS,
    ARRANGEMENT_KEYWORDS,
    OPENING_HOURS_KEYWORDS,
    GENERAL_KEYWORDS,
)

__all__ = [
    # Services
    "KBDiffService",
    "get_diff_service",
    # Types
    "FAQItem",
    "ArrangementItem",
    "ContentSection",
    "BusinessInfo",
    "KBContent",
    "SearchResult",
    "QuerySignals",
    "DiffChange",
    "DiffSummary",
    # Constants
    "STOPWORDS",
    "SYNONYM_MAP",
    "QUERY_EXPANSIONS",
    "KIDS_KEYWORDS",
    "BEDRIJF_KEYWORDS",
    "PRICING_KEYWORDS",
    "ARRANGEMENT_KEYWORDS",
    "OPENING_HOURS_KEYWORDS",
    "GENERAL_KEYWORDS",
]
