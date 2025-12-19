"""
Knowledge Base utilities for MASO applications

Provides:
- KBDiffService: Compare KB content and generate structured diffs
- KBSearchEngine: Stateless search engine for KB content
- LLMContextBuilder: Build context strings for LLM prompts
"""

from .diff_service import KBDiffService, get_diff_service
from .search import KBSearchEngine, get_search_engine
from .context import LLMContextBuilder, get_context_builder
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
    LOCATION_KEYWORDS,
    MENU_KEYWORDS,
    DAY_NAMES_EN_TO_NL,
    DAYS_ORDER,
    IMPORTANT_SEARCH_TERMS,
)

__all__ = [
    # Services
    "KBDiffService",
    "get_diff_service",
    "KBSearchEngine",
    "get_search_engine",
    "LLMContextBuilder",
    "get_context_builder",
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
    "LOCATION_KEYWORDS",
    "MENU_KEYWORDS",
    "DAY_NAMES_EN_TO_NL",
    "DAYS_ORDER",
    "IMPORTANT_SEARCH_TERMS",
]
