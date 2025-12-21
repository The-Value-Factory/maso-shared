"""
maso-shared - Shared utilities for MASO applications

This package provides shared functionality for:
- Knowledge Base search and context generation
- Tenant configuration
- Common utilities
"""

from .kb import (
    # Search
    KBSearchEngine,
    get_search_engine,
    
    # Service facade
    KnowledgeService,
    create_knowledge_service,
    
    # Query analysis
    QueryAnalyzer,
    analyze_query,
    detect_categories,
    
    # Context modules
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
    
    # Types
    QuerySignals,
    SearchResult,
)

from .config import (
    BaseTenantConfig,
    TenantConfigStatic,
)

__version__ = "0.2.0"
__all__ = [
    # KB
    "KBSearchEngine",
    "get_search_engine",
    "KnowledgeService",
    "create_knowledge_service",
    "QueryAnalyzer",
    "analyze_query",
    "detect_categories",
    # Modules
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
    # Types
    "QuerySignals",
    "SearchResult",
    # Config
    "BaseTenantConfig",
    "TenantConfigStatic",
]
