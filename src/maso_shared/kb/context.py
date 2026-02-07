"""
LLM Context Builder

Builds context strings for LLM prompts from knowledge base content and search results.
This is completely stateless - all data is passed in as parameters.

Used by both Voice AI and Main App for:
- Building modular context from KB content
- Formatting arrangements, FAQs, business info for LLM
- Opening hours formatting
"""

import logging
from typing import List, Dict, Any, Optional

from .types import KBContent, SearchResult, QuerySignals
from .constants import DAY_NAMES_EN_TO_NL, DAYS_ORDER

logger = logging.getLogger(__name__)


class LLMContextBuilder:
    """
    Builds context strings for LLM prompts.
    
    All data is passed in as parameters - no internal state or database calls.
    
    Usage:
        builder = LLMContextBuilder()
        context = builder.build_context(kb_content, search_results, signals)
    """
    
    def __init__(self):
        pass
    
    def build_context(
        self,
        kb_content: KBContent,
        search_results: List[SearchResult],
        signals: QuerySignals,
        max_length: int = 5000
    ) -> str:
        """
        Build complete LLM context from KB content and search results.
        
        Args:
            kb_content: Knowledge base content
            search_results: Results from search engine
            signals: Query signals for module selection
            max_length: Maximum context length in characters
            
        Returns:
            Context string for LLM prompt
        """
        context_parts = []
        modules_used = []
        
        # Always include organisation info for general questions or opening hours
        if signals.get('general') or signals.get('opening_hours') or signals.get('location'):
            org_module = self.build_organisation_module(kb_content)
            if org_module:
                context_parts.append(org_module)
                modules_used.append('organisation')
        
        # Add arrangements for arrangement queries
        if signals.get('arrangement'):
            arr_module = self.build_arrangements_module(kb_content, search_results)
            if arr_module:
                context_parts.append(arr_module)
                modules_used.append('arrangements')
        elif not signals.get('general'):
            # Add favorite arrangements as fallback
            fav_module = self.build_favorite_arrangements_module(kb_content)
            if fav_module:
                context_parts.append(fav_module)
                modules_used.append('favorite_arrangements')
        
        # Add relevant FAQs
        faqs_module = self.build_faqs_module(search_results)
        if faqs_module:
            context_parts.append(faqs_module)
            modules_used.append('faqs')
        
        # Add search results as additional context
        search_module = self.build_search_results_module(search_results, exclude_faqs=True)
        if search_module:
            context_parts.append(search_module)
            modules_used.append('search_results')
        
        full_context = "\n".join(context_parts)
        
        logger.info(f"✅ Context built with modules: {', '.join(modules_used)}")
        logger.info(f"📏 Total context length: {len(full_context)} chars")
        
        # Trim if too long
        if len(full_context) > max_length:
            logger.warning(f"⚠️ Context too long ({len(full_context)} chars), trimming")
            # Remove search results module first
            if search_module and search_module in full_context:
                full_context = full_context.replace(search_module, "")
            # If still too long, hard truncate
            if len(full_context) > max_length:
                full_context = full_context[:max_length] + "..."
        
        return full_context if full_context else "Geen specifieke informatie gevonden."
    
    def build_organisation_module(self, kb_content: KBContent) -> str:
        """
        Build organisation description module with opening hours.
        
        Args:
            kb_content: Knowledge base content
            
        Returns:
            Formatted organisation info string
        """
        parts = []
        
        business_info = kb_content.get('business_info', {})
        business_name = business_info.get('name', 'De organisatie')
        
        # Add description
        if business_info.get('description'):
            parts.append(f"🏢 OVER {business_name}:")
            parts.append(business_info['description'])
            parts.append("\n")
        
        # Add opening hours
        opening_hours = business_info.get('opening_hours', {})
        
        if opening_hours:
            parts.append("\n🕐 OPENINGSTIJDEN:\n")
            
            for day in DAYS_ORDER:
                if day in opening_hours:
                    day_nl = DAY_NAMES_EN_TO_NL.get(day, day.capitalize())
                    hours = opening_hours[day]
                    parts.append(f"  • {day_nl}: {hours}\n")
            
            parts.append("\n")
            logger.info(f"✅ Added opening hours to context: {len(opening_hours)} days")
        
        return "".join(parts) if parts else ""
    
    def build_arrangements_module(
        self,
        kb_content: KBContent,
        search_results: List[SearchResult] = None
    ) -> str:
        """
        Build arrangements module for arrangement queries.
        
        Shows all arrangements when user asks for overview.
        
        Args:
            kb_content: Knowledge base content
            search_results: Optional search results for relevance sorting
            
        Returns:
            Formatted arrangements string
        """
        arrangements = kb_content.get('arrangements', [])
        
        if not arrangements:
            return ""
        
        # Deduplicate by name
        seen = {}
        for arr in arrangements:
            name = arr.get('name', '').strip().lower()
            if name and name not in seen:
                seen[name] = arr
        
        unique_arrangements = list(seen.values())
        
        # Sort: favorites first, then by name
        def sort_key(arr):
            is_fav = arr.get('is_featured', False)
            return (0 if is_fav else 1, arr.get('name', ''))
        
        sorted_arrangements = sorted(unique_arrangements, key=sort_key)
        
        parts = []
        
        # Show top 3 as highlights
        top_arrangements = sorted_arrangements[:3]
        if top_arrangements:
            parts.append(f"🎯 TOP {len(top_arrangements)} MEEST GEKOZEN ARRANGEMENTEN:\n\n")
            
            for i, arr in enumerate(top_arrangements, 1):
                parts.append(self._format_arrangement(arr, numbered=i))
        
        # Show remaining as list
        other_arrangements = sorted_arrangements[3:]
        if other_arrangements:
            parts.append(f"\n📦 OVERIGE ARRANGEMENTEN ({len(other_arrangements)} opties):\n\n")
            
            for arr in other_arrangements:
                parts.append(self._format_arrangement_short(arr))
        
        parts.append("\n💡 Voor maatwerk of grote groepen, vraag naar een offerte!\n\n")
        
        logger.info(f"✅ Arrangements module: {len(unique_arrangements)} items")
        return "".join(parts)
    
    def build_favorite_arrangements_module(self, kb_content: KBContent) -> str:
        """
        Build favorite arrangements module (for non-arrangement queries).
        
        Only shows arrangements marked as is_featured=true.
        
        Args:
            kb_content: Knowledge base content
            
        Returns:
            Formatted favorite arrangements string
        """
        arrangements = kb_content.get('arrangements', [])
        
        if not arrangements:
            return ""
        
        # Filter for favorites only
        favorite_arrangements = [arr for arr in arrangements if arr.get('is_featured')]
        
        if not favorite_arrangements:
            return ""
        
        # Deduplicate by name
        seen = {}
        for arr in favorite_arrangements:
            name = arr.get('name', '').strip().lower()
            if name and name not in seen:
                seen[name] = arr
        
        unique_favorites = list(seen.values())
        
        parts = ["⭐ POPULAIRE ARRANGEMENTEN:\n\n"]
        
        for arr in unique_favorites[:5]:  # Max 5
            parts.append(self._format_arrangement_short(arr))
        
        parts.append("\n")
        logger.info(f"✅ Favorite arrangements module: {len(unique_favorites)} items")
        return "".join(parts)
    
    def build_faqs_module(self, search_results: List[SearchResult]) -> str:
        """
        Build FAQs module from search results.
        
        Args:
            search_results: Search results (FAQs are already ranked)
            
        Returns:
            Formatted FAQs string
        """
        relevant_faqs = [r for r in search_results if r.get('is_faq')]
        
        if not relevant_faqs:
            return ""
        
        parts = ["❓ VEELGESTELDE VRAGEN:\n\n"]
        
        for faq in relevant_faqs[:5]:  # Max 5 FAQs
            faq_title = faq.get('title', '').replace('FAQ: ', '')
            parts.append(f"• {faq_title}\n")
            
            content = faq.get('content', '')
            if 'ANTWOORD:' in content:
                answer = content.split('ANTWOORD:')[1].strip()
                parts.append(f"  → {answer}\n\n")
            else:
                parts.append(f"  → {content}\n\n")
        
        logger.info(f"✅ FAQs module: {len(relevant_faqs)} FAQs")
        return "".join(parts)
    
    def build_search_results_module(
        self,
        search_results: List[SearchResult],
        exclude_faqs: bool = True,
        max_results: int = 3
    ) -> str:
        """
        Build search results module as additional context.
        
        Args:
            search_results: Search results
            exclude_faqs: Whether to exclude FAQ results
            max_results: Maximum results to include
            
        Returns:
            Formatted search results string
        """
        other_results = []
        
        for r in search_results:
            if exclude_faqs and r.get('is_faq'):
                continue
            if r.get('is_arrangement'):
                continue  # Arrangements handled separately
            other_results.append(r)
        
        if not other_results:
            return ""
        
        parts = ["📋 EXTRA INFORMATIE:\n\n"]
        
        for result in other_results[:max_results]:
            title = result.get('title', 'Onbekend')
            content = result.get('content', '')
            
            parts.append(f"PAGINA: {title}\n")
            
            # Add excerpt
            excerpt = content[:800] + "..." if len(content) > 800 else content
            parts.append(f"{excerpt}\n\n")
        
        logger.info(f"✅ Search results module: {len(other_results[:max_results])} results")
        return "".join(parts)
    
    def build_kids_module(self, kb_content: KBContent) -> str:
        """
        Build kids arrangements module.
        
        Args:
            kb_content: Knowledge base content
            
        Returns:
            Formatted kids arrangements string
        """
        arrangements = kb_content.get('arrangements', [])
        
        kids_arrangements = [
            arr for arr in arrangements
            if any(word in (arr.get('name', '') + arr.get('category', '')).lower() 
                   for word in ['kids', 'kinder', 'party', 'feest'])
        ]
        
        if not kids_arrangements:
            return ""
        
        parts = ["🎈 KINDERARRANGEMENTEN:\n\n"]
        
        for arr in kids_arrangements[:5]:
            parts.append(self._format_arrangement(arr))
        
        logger.info(f"✅ Kids module: {len(kids_arrangements)} arrangements")
        return "".join(parts)
    
    def build_bedrijf_module(self, kb_content: KBContent) -> str:
        """
        Build business arrangements module.
        
        Args:
            kb_content: Knowledge base content
            
        Returns:
            Formatted business arrangements string
        """
        arrangements = kb_content.get('arrangements', [])
        
        bedrijf_arrangements = [
            arr for arr in arrangements
            if any(word in (arr.get('name', '') + arr.get('category', '')).lower() 
                   for word in ['bedrijf', 'zakelijk', 'team', 'corporate'])
        ]
        
        if not bedrijf_arrangements:
            return ""
        
        parts = ["🏢 BEDRIJFSARRANGEMENTEN:\n\n"]
        
        for arr in bedrijf_arrangements[:5]:
            parts.append(self._format_arrangement(arr))
        
        logger.info(f"✅ Bedrijf module: {len(bedrijf_arrangements)} arrangements")
        return "".join(parts)
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _format_arrangement(self, arr: Dict[str, Any], numbered: int = None) -> str:
        """Format a single arrangement with full details."""
        parts = []
        
        name = arr.get('name', 'Onbekend')
        prices = arr.get('price', [])
        description = arr.get('description', '')
        duration = arr.get('duration', '')
        
        # Format prices
        if isinstance(prices, list) and prices:
            price_str = ', '.join(prices)
        elif prices:
            price_str = str(prices)
        else:
            price_str = "Prijs op aanvraag"
        
        # Build output
        if numbered:
            parts.append(f"⭐ {numbered}. {name}\n")
        else:
            parts.append(f"⭐ {name}\n")
        
        if price_str != "Prijs op aanvraag":
            parts.append(f"💰 {price_str}\n")
        
        if duration:
            parts.append(f"⏱️ {duration}\n")
        
        if description:
            parts.append(f"📋 {description}\n")
        
        parts.append("\n")
        return "".join(parts)
    
    def _format_arrangement_short(self, arr: Dict[str, Any]) -> str:
        """Format a single arrangement as a short one-liner."""
        name = arr.get('name', 'Onbekend')
        prices = arr.get('price', [])
        
        # Format prices
        if isinstance(prices, list) and prices:
            price_str = ', '.join(prices)
        elif prices:
            price_str = str(prices)
        else:
            price_str = ""
        
        line = f"• {name}"
        if price_str:
            line += f" - {price_str}"
        line += "\n"
        
        return line


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_context_builder_instance: Optional[LLMContextBuilder] = None


def get_context_builder() -> LLMContextBuilder:
    """Get or create a global context builder instance."""
    global _context_builder_instance
    if _context_builder_instance is None:
        _context_builder_instance = LLMContextBuilder()
    return _context_builder_instance
