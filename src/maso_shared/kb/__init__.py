"""
Knowledge Base utilities for MASO applications

Provides:
- KnowledgeService: Unified facade for search and context building (main entry point)
- KBDiffService: Compare KB content and generate structured diffs
- KBSearchEngine: Stateless search engine for KB content  
- LLMContextBuilder: Build context strings for LLM prompts
- QueryAnalyzer: Analyze queries for signals and categories
- Context Modules: Pluggable modules for context building
"""

# Main unified service (primary entry point)
from .service import KnowledgeService, create_knowledge_service

# Query analysis
from .query_analyzer import (
    QueryAnalyzer, 
    analyze_query, 
    detect_categories,
    DEFAULT_ACTIVITY_SYNONYMS,
)

# Re-export as ACTIVITY_SYNONYMS for backward compatibility
ACTIVITY_SYNONYMS = DEFAULT_ACTIVITY_SYNONYMS

# Context modules (for customization)
from .modules import (
    ContextModule,
    OrganisationModule,
    OpeningHoursModule,
    ArrangementsModule,
    FavoriteArrangementsModule,
    FAQModule,
    SearchResultsModule,
    KidsModule,
    BedrijfModule,
    ActivityPricingModule,
    get_default_modules,
)

# Search engine
from .search import KBSearchEngine, get_search_engine, extract_relevant_excerpt

# Context builder (legacy, use KnowledgeService instead)
from .context import LLMContextBuilder, get_context_builder

# Diff service
from .diff_service import KBDiffService, get_diff_service

# Types
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

# Constants
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
    # Main service (primary entry point)
    "KnowledgeService",
    "create_knowledge_service",
    
    # Query analysis
    "QueryAnalyzer",
    "analyze_query",
    "detect_categories",
    
    # Context modules
    "ContextModule",
    "OrganisationModule",
    "OpeningHoursModule",
    "ArrangementsModule",
    "FavoriteArrangementsModule",
    "FAQModule",
    "SearchResultsModule",
    "KidsModule",
    "BedrijfModule",
    "ActivityPricingModule",
    "get_default_modules",
    
    # Search
    "KBSearchEngine",
    "get_search_engine",
    "extract_relevant_excerpt",
    
    # Context builder (legacy)
    "LLMContextBuilder",
    "get_context_builder",
    
    # Diff service
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
    
    # Stopwords
    "STOPWORDS",
    "STOPWORDS_EXTENDED",
    
    # Synonym maps
    "SYNONYM_MAP",
    "EXCERPT_SYNONYMS",
    "QUERY_EXPANSIONS",
    "ACTIVITY_SYNONYMS",
    
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
