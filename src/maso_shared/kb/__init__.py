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
    # Stopwords
    STOPWORDS,
    STOPWORDS_EXTENDED,
    # Synonym maps
    SYNONYM_MAP,
    EXCERPT_SYNONYMS,
    QUERY_EXPANSIONS,
    # Signal detection keywords
    KIDS_QUERY_KEYWORDS,
    KIDS_CONTENT_KEYWORDS,
    KIDS_KEYWORDS,  # Backward compat
    BEDRIJF_QUERY_KEYWORDS,
    BEDRIJF_CONTENT_KEYWORDS,
    BEDRIJF_KEYWORDS,  # Backward compat
    PRICING_QUERY_KEYWORDS,
    PRICING_CONTENT_KEYWORDS,
    PRICING_KEYWORDS,  # Backward compat
    # Drink keywords
    DRINK_KEYWORDS,
    ALL_DRINK_KEYWORDS,
    DRINK_CONTENT_PATTERNS,
    # Allergy keywords
    ALLERGY_QUERY_KEYWORDS,
    ALLERGY_CONTENT_KEYWORDS,
    # Other signal keywords
    RESERVATION_QUERY_KEYWORDS,
    OPENING_HOURS_KEYWORDS,
    LOCATION_KEYWORDS,
    ARRANGEMENT_KEYWORDS,
    GENERAL_KEYWORDS,
    MENU_KEYWORDS,
    # Date/day constants
    DAY_NAMES_EN_TO_NL,
    DAYS_ORDER,
    # Search relevance
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
    # Stopwords
    "STOPWORDS",
    "STOPWORDS_EXTENDED",
    # Synonym maps
    "SYNONYM_MAP",
    "EXCERPT_SYNONYMS",
    "QUERY_EXPANSIONS",
    # Signal detection keywords
    "KIDS_QUERY_KEYWORDS",
    "KIDS_CONTENT_KEYWORDS",
    "KIDS_KEYWORDS",
    "BEDRIJF_QUERY_KEYWORDS",
    "BEDRIJF_CONTENT_KEYWORDS",
    "BEDRIJF_KEYWORDS",
    "PRICING_QUERY_KEYWORDS",
    "PRICING_CONTENT_KEYWORDS",
    "PRICING_KEYWORDS",
    # Drink keywords
    "DRINK_KEYWORDS",
    "ALL_DRINK_KEYWORDS",
    "DRINK_CONTENT_PATTERNS",
    # Allergy keywords
    "ALLERGY_QUERY_KEYWORDS",
    "ALLERGY_CONTENT_KEYWORDS",
    # Other signal keywords
    "RESERVATION_QUERY_KEYWORDS",
    "OPENING_HOURS_KEYWORDS",
    "LOCATION_KEYWORDS",
    "ARRANGEMENT_KEYWORDS",
    "GENERAL_KEYWORDS",
    "MENU_KEYWORDS",
    # Date/day constants
    "DAY_NAMES_EN_TO_NL",
    "DAYS_ORDER",
    # Search relevance
    "IMPORTANT_SEARCH_TERMS",
]
