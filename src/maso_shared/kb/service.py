"""
Knowledge Service - Unified facade for KB search and context building

This is the main entry point for knowledge operations. It combines:
- Query analysis
- KB search
- LLM context building

Apps should use this class instead of the individual components directly.

Usage:
    from maso_shared.kb import KnowledgeService
    
    # Create service
    service = KnowledgeService(kb_content=my_kb_content)
    
    # Get context for LLM
    context = service.get_context_for_llm(query="kinderfeestje prijzen")
    
    # Or with products from DB
    context = service.get_context_for_llm(
        query="kinderfeestje prijzen",
        products=kids_products,
    )
"""

import logging
from typing import List, Dict, Any, Optional, Callable

from .types import KBContent, SearchResult, QuerySignals
from .search import KBSearchEngine, extract_relevant_excerpt
from .query_analyzer import QueryAnalyzer, analyze_query
from .modules import (
    ContextModule,
    get_default_modules,
    OrganisationModule,
    OpeningHoursModule,
    ArrangementsModule,
    FAQModule,
    SearchResultsModule,
    KidsModule,
    BedrijfModule,
    ActivityPricingModule,
)

logger = logging.getLogger(__name__)


class KnowledgeService:
    """
    Unified service for knowledge base operations.
    
    This is the main entry point that combines:
    - Query analysis (signals, categories)
    - KB search (with configurable boosters)
    - LLM context building (with pluggable modules)
    
    Both voice_agent and boulesclub should use this class.
    
    Args:
        kb_content: The knowledge base content
        search_engine: Optional custom search engine (creates default if not provided)
        query_analyzer: Optional custom query analyzer
        modules: Optional list of context modules (uses defaults if not provided)
        tenant_id: Optional tenant identifier for multi-tenant scenarios
    """
    
    def __init__(
        self,
        kb_content: KBContent = None,
        search_engine: KBSearchEngine = None,
        query_analyzer: QueryAnalyzer = None,
        modules: List[ContextModule] = None,
        tenant_id: str = None,
    ):
        self.kb_content = kb_content or {}
        self.tenant_id = tenant_id
        
        # Initialize components
        self._search_engine = search_engine or KBSearchEngine(self.kb_content)
        self._query_analyzer = query_analyzer or QueryAnalyzer()
        self._modules = modules or get_default_modules()
        
        # Module lookup by name
        self._module_map = {m.name: m for m in self._modules}
        
        logger.info(
            f"KnowledgeService initialized with {len(self._modules)} modules"
            + (f" for tenant {tenant_id}" if tenant_id else "")
        )
    
    def update_kb_content(self, kb_content: KBContent):
        """
        Update the knowledge base content.
        
        Call this when the KB is refreshed from the database.
        """
        self.kb_content = kb_content
        self._search_engine = KBSearchEngine(kb_content)
        logger.info("KB content updated")
    
    def register_module(self, module: ContextModule):
        """
        Register a custom module.
        
        Args:
            module: The module to add
        """
        self._modules.append(module)
        self._module_map[module.name] = module
        logger.info(f"Module registered: {module.name}")
    
    def replace_module(self, name: str, module: ContextModule):
        """
        Replace an existing module by name.
        
        Args:
            name: Name of the module to replace
            module: The new module
        """
        # Remove old module if exists
        self._modules = [m for m in self._modules if m.name != name]
        
        # Add new module
        self._modules.append(module)
        self._module_map[module.name] = module
        logger.info(f"Module replaced: {name}")
    
    def analyze_query(self, query: str) -> QuerySignals:
        """
        Analyze a query to extract signals.
        
        Args:
            query: The user query
            
        Returns:
            Query signals dictionary
        """
        return self._query_analyzer.analyze(query)
    
    def search(
        self,
        query: str,
        max_results: int = 10,
        min_score: float = 0.1,
    ) -> List[SearchResult]:
        """
        Search the knowledge base.
        
        Args:
            query: The search query
            max_results: Maximum results to return
            min_score: Minimum relevance score
            
        Returns:
            List of search results
        """
        return self._search_engine.search(
            query=query,
            max_results=max_results,
            min_score=min_score,
        )
    
    def get_context_for_llm(
        self,
        query: str,
        products: List[Dict] = None,
        conversation_history: List[Dict] = None,
        custom_context: Dict[str, Any] = None,
        max_context_length: int = 8000,
        include_modules: List[str] = None,
        exclude_modules: List[str] = None,
    ) -> str:
        """
        Get complete context for LLM based on query.
        
        This is the main method that combines analysis, search, and context building.
        
        Args:
            query: The user query
            products: Optional products from database (for activity pricing)
            conversation_history: Optional conversation history
            custom_context: Optional custom context to pass to modules
            max_context_length: Maximum context length in characters
            include_modules: Optional list of module names to include (all if None)
            exclude_modules: Optional list of module names to exclude
            
        Returns:
            Formatted context string for LLM
        """
        # Analyze query
        signals = self._query_analyzer.analyze(query)
        logger.info(f"Query signals: {signals}")
        
        # Search KB
        search_results = self._search_engine.search(query, max_results=10)
        logger.info(f"Search returned {len(search_results)} results")
        
        # Build context using modules
        context_parts = []
        
        # Add conversation history if provided
        if conversation_history:
            history_context = self._format_conversation_history(conversation_history)
            if history_context:
                context_parts.append(history_context)
        
        # Prepare module context
        module_context = {
            'products': products or [],
            'activity_name': signals.get('detected_activity'),
            'query': query,  # Pass query for smart excerpt extraction
            **(custom_context or {})
        }
        
        # Determine which modules to include
        active_modules = self._modules
        if include_modules:
            active_modules = [m for m in self._modules if m.name in include_modules]
        if exclude_modules:
            active_modules = [m for m in active_modules if m.name not in exclude_modules]
        
        # Render each module
        for module in active_modules:
            try:
                if module.should_include(signals, search_results=search_results, **module_context):
                    content = module.render(
                        self.kb_content,
                        search_results,
                        signals,
                        **module_context
                    )
                    if content and content.strip():
                        context_parts.append(content)
            except Exception as e:
                logger.error(f"Module {module.name} failed: {e}", exc_info=True)
        
        # Combine and truncate if needed
        full_context = "\n".join(context_parts)
        
        if len(full_context) > max_context_length:
            logger.warning(f"Context truncated from {len(full_context)} to {max_context_length}")
            full_context = full_context[:max_context_length] + "\n\n[Context truncated...]"
        
        return full_context
    
    def get_relevant_excerpt(
        self,
        content: str,
        query: str,
        max_length: int = 800,
    ) -> str:
        """
        Extract a relevant excerpt from content based on query.
        
        Args:
            content: Full content text
            query: Search query
            max_length: Maximum excerpt length
            
        Returns:
            Relevant excerpt
        """
        return extract_relevant_excerpt(content, query, max_length)
    
    def _format_conversation_history(
        self,
        history: List[Dict],
        max_turns: int = 3,
    ) -> str:
        """Format conversation history for context."""
        if not history:
            return ""
        
        recent = history[-max_turns:]
        
        parts = ["📝 GESPREKSGESCHIEDENIS:\n"]
        for turn in recent:
            role = turn.get('role', 'user')
            content = turn.get('content', '')
            
            if role == 'user':
                parts.append(f"👤 Klant: {content}\n")
            elif role == 'assistant':
                parts.append(f"🤖 Assistent: {content}\n")
        
        parts.append("\n")
        return "".join(parts)
    
    def get_faq_answer(self, query: str) -> Optional[str]:
        """
        Try to find a direct FAQ answer for the query.
        
        Args:
            query: The user query
            
        Returns:
            FAQ answer if found, None otherwise
        """
        results = self._search_engine.search(query, max_results=3, min_score=0.5)
        
        # Look for high-confidence FAQ match
        for result in results:
            if result.get('is_faq') and result.get('score', 0) > 0.7:
                answer = result.get('answer', '')
                if answer:
                    return answer
                
                # Try to extract from content
                content = result.get('content', '')
                if 'ANTWOORD:' in content:
                    return content.split('ANTWOORD:')[1].strip()
                
                return content
        
        return None
    
    def get_arrangement_info(self, arrangement_name: str) -> Optional[Dict]:
        """
        Get information about a specific arrangement.
        
        Args:
            arrangement_name: Name of the arrangement
            
        Returns:
            Arrangement dict if found, None otherwise
        """
        arrangements = self.kb_content.get('arrangements', [])
        name_lower = arrangement_name.lower()
        
        for arr in arrangements:
            if arr.get('name', '').lower() == name_lower:
                return arr
            # Also check partial match
            if name_lower in arr.get('name', '').lower():
                return arr
        
        return None
    
    def get_activity_pricing(self, activity_name: str) -> Optional[Dict]:
        """
        Get pricing information for an activity.
        
        Args:
            activity_name: Name of the activity
            
        Returns:
            Pricing dict if found in KB, None otherwise
        """
        # Search for activity in sections
        results = self._search_engine.search(
            f"{activity_name} prijs kosten",
            max_results=3,
        )
        
        for result in results:
            if result.get('score', 0) > 0.5:
                # Extract pricing from content
                content = result.get('content', '')
                if '€' in content or 'euro' in content.lower() or 'prijs' in content.lower():
                    return {
                        'activity': activity_name,
                        'content': content,
                        'source': result.get('title', 'KB'),
                    }
        
        return None


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_knowledge_service(
    kb_content: KBContent,
    custom_modules: List[ContextModule] = None,
    tenant_id: str = None,
) -> KnowledgeService:
    """
    Create a KnowledgeService with optional customization.
    
    This is the recommended way to create a service instance.
    
    Args:
        kb_content: Knowledge base content
        custom_modules: Optional additional modules
        tenant_id: Optional tenant identifier
        
    Returns:
        Configured KnowledgeService instance
    """
    modules = get_default_modules()
    if custom_modules:
        modules.extend(custom_modules)
    
    return KnowledgeService(
        kb_content=kb_content,
        modules=modules,
        tenant_id=tenant_id,
    )
