"""
Context Modules - Pluggable modules for LLM context building

Each module knows how to render a specific type of content for the LLM context.
Apps can use the default modules or create custom ones.

Usage:
    # Use default modules
    from maso_shared.kb.modules import OrganisationModule, FAQModule
    
    # Create custom module
    class MyCustomModule(ContextModule):
        def render(self, kb_content, search_results, signals, **kwargs) -> str:
            return "My custom content"
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable

from .search import extract_relevant_excerpt
from .types import KBContent, SearchResult, QuerySignals
from .constants import DAY_NAMES_EN_TO_NL, DAYS_ORDER

logger = logging.getLogger(__name__)


# ============================================================================
# HELPER: Transform English day names to Dutch (backward compatibility)
# ============================================================================

def _normalize_opening_hours(opening_hours: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform opening hours from English day names to Dutch format.
    
    Handles both formats:
    - English keys: {"monday": {"open": "12:00", "close": "17:00"}}
    - Dutch keys: {"maandag": "12.00 - 17.00"}
    
    Always returns Dutch keys with string format for DAYS_ORDER compatibility.
    
    Args:
        opening_hours: Dict with day names as keys
        
    Returns:
        Dict with Dutch day names as keys
    """
    if not opening_hours:
        return opening_hours
    
    # Check if already Dutch (has any Dutch day name from DAYS_ORDER)
    if any(day in opening_hours for day in DAYS_ORDER):
        return opening_hours
    
    # Check if English (has any English day name)
    english_keys = list(DAY_NAMES_EN_TO_NL.keys())
    has_english = any(day.lower() in english_keys for day in opening_hours.keys())
    
    if not has_english:
        return opening_hours
    
    # Transform EN → NL
    logger.debug("🔄 Transforming opening hours from English to Dutch day names")
    normalized = {}
    
    for eng_day, hours_data in opening_hours.items():
        # Get Dutch day name
        nl_day = DAY_NAMES_EN_TO_NL.get(eng_day.lower())
        if not nl_day:
            logger.warning(f"Unknown day name: {eng_day}, skipping")
            continue
        
        # Convert format: dict → string
        if isinstance(hours_data, dict):
            if hours_data.get('closed', False) or not hours_data.get('open'):
                normalized[nl_day] = "gesloten"
            else:
                open_time = str(hours_data.get('open', '')).replace(':', '.')
                close_time = str(hours_data.get('close', '')).replace(':', '.')
                normalized[nl_day] = f"{open_time} - {close_time}"
        elif isinstance(hours_data, str):
            # Already string format, just use Dutch key
            normalized[nl_day] = hours_data
        else:
            logger.warning(f"Unknown hours_data type for {eng_day}: {type(hours_data)}")
    
    return normalized



# ============================================================================
# BASE MODULE INTERFACE
# ============================================================================

class ContextModule(ABC):
    """
    Base class for context modules.
    
    Each module is responsible for rendering a specific type of content
    for the LLM context (e.g., organisation info, FAQs, arrangements).
    
    Apps can subclass this to create custom modules.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Module name for logging."""
        pass
    
    @abstractmethod
    def should_include(self, signals: QuerySignals, **kwargs) -> bool:
        """
        Determine if this module should be included based on query signals.
        
        Args:
            signals: Query signals from analyzer
            **kwargs: Additional context (e.g., search_results)
            
        Returns:
            True if module should be included
        """
        pass
    
    @abstractmethod
    def render(
        self, 
        kb_content: KBContent, 
        search_results: List[SearchResult],
        signals: QuerySignals,
        **kwargs
    ) -> str:
        """
        Render the module content.
        
        Args:
            kb_content: Knowledge base content
            search_results: Search results
            signals: Query signals
            **kwargs: Additional context
            
        Returns:
            Formatted string for LLM context
        """
        pass


# ============================================================================
# CORE MODULES
# ============================================================================

class OrganisationModule(ContextModule):
    """Module for organisation description and opening hours."""
    
    @property
    def name(self) -> str:
        return "organisation"
    
    def should_include(self, signals: QuerySignals, **kwargs) -> bool:
        return signals.get('general', False) or signals.get('opening_hours', False) or signals.get('location', False)
    
    def render(
        self, 
        kb_content: KBContent, 
        search_results: List[SearchResult],
        signals: QuerySignals,
        **kwargs
    ) -> str:
        parts = []
        
        business_info = kb_content.get('business_info', {})
        business_name = business_info.get('name', 'De organisatie')
        
        # Add description
        if business_info.get('description'):
            parts.append(f"🏢 OVER {business_name}:\n")
            parts.append(business_info['description'])
            parts.append("\n\n")
        
        # Add opening hours if relevant
        if signals.get('opening_hours', False):
            opening_hours = _normalize_opening_hours(business_info.get('opening_hours', {}))
            if opening_hours:
                parts.append("🕐 OPENINGSTIJDEN:\n")
                for day in DAYS_ORDER:
                    if day in opening_hours:
                        day_nl = DAY_NAMES_EN_TO_NL.get(day, day.capitalize())
                        hours = opening_hours[day]
                        parts.append(f"  • {day_nl}: {hours}\n")
                parts.append("\n")
        
        result = "".join(parts)
        if result:
            logger.info(f"✅ {self.name} module: {len(result)} chars")
        return result


class OpeningHoursModule(ContextModule):
    """Dedicated module for opening hours (when specifically asked)."""
    
    @property
    def name(self) -> str:
        return "opening_hours"
    
    def should_include(self, signals: QuerySignals, **kwargs) -> bool:
        return signals.get('opening_hours', False)
    
    def render(
        self, 
        kb_content: KBContent, 
        search_results: List[SearchResult],
        signals: QuerySignals,
        **kwargs
    ) -> str:
        business_info = kb_content.get('business_info', {})
        opening_hours = business_info.get('opening_hours', {})
        
        if not opening_hours:
            return ""
        
        parts = ["🕐 OPENINGSTIJDEN:\n"]
        
        for day in DAYS_ORDER:
            if day in opening_hours:
                day_nl = DAY_NAMES_EN_TO_NL.get(day, day.capitalize())
                hours = opening_hours[day]
                parts.append(f"  • {day_nl}: {hours}\n")
        
        # Add spoken format if available
        spoken_hours = business_info.get('opening_hours_spoken', {})
        if spoken_hours:
            parts.append("\n📢 UITSPREKEN ALS:\n")
            for day in DAYS_ORDER:
                if day in spoken_hours:
                    day_nl = DAY_NAMES_EN_TO_NL.get(day, day.capitalize())
                    spoken = spoken_hours[day]
                    parts.append(f"  • {day_nl}: {spoken}\n")
        
        parts.append("\n")
        return "".join(parts)


class ArrangementsModule(ContextModule):
    """Module for arrangements overview."""
    
    def __init__(self, show_all: bool = True, max_items: int = 10):
        """
        Args:
            show_all: Whether to show all arrangements or just top ones
            max_items: Maximum items to show
        """
        self.show_all = show_all
        self.max_items = max_items
    
    @property
    def name(self) -> str:
        return "arrangements"
    
    def should_include(self, signals: QuerySignals, **kwargs) -> bool:
        return signals.get('arrangement', False)
    
    def render(
        self, 
        kb_content: KBContent, 
        search_results: List[SearchResult],
        signals: QuerySignals,
        **kwargs
    ) -> str:
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
        
        # Show remaining
        if self.show_all:
            other = sorted_arrangements[3:self.max_items]
            if other:
                parts.append(f"\n📦 OVERIGE ARRANGEMENTEN ({len(other)} opties):\n\n")
                for arr in other:
                    parts.append(self._format_arrangement_short(arr))
        
        parts.append("\n💡 Voor maatwerk of grote groepen, vraag naar een offerte!\n\n")
        
        logger.info(f"✅ {self.name} module: {len(unique_arrangements)} items")
        return "".join(parts)
    
    def _format_arrangement(self, arr: Dict[str, Any], numbered: int = None) -> str:
        parts = []
        name = arr.get('name', 'Onbekend')
        prices = arr.get('price', [])
        description = arr.get('description', '')
        duration = arr.get('duration', '')
        
        if isinstance(prices, list) and prices:
            price_str = ', '.join(prices)
        elif prices:
            price_str = str(prices)
        else:
            price_str = "Prijs op aanvraag"
        
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
        name = arr.get('name', 'Onbekend')
        prices = arr.get('price', [])
        
        if isinstance(prices, list) and prices:
            price_str = ', '.join(prices)
        elif prices:
            price_str = str(prices)
        else:
            price_str = ""
        
        line = f"• {name}"
        if price_str:
            line += f" - {price_str}"
        return line + "\n"


class FavoriteArrangementsModule(ContextModule):
    """Module for favorite arrangements (non-arrangement queries)."""
    
    def __init__(self, max_items: int = 5):
        self.max_items = max_items
    
    @property
    def name(self) -> str:
        return "favorite_arrangements"
    
    def should_include(self, signals: QuerySignals, **kwargs) -> bool:
        # Include when NOT an arrangement query but we want to show popular options
        return not signals.get('arrangement', False) and not signals.get('general', False)
    
    def render(
        self, 
        kb_content: KBContent, 
        search_results: List[SearchResult],
        signals: QuerySignals,
        **kwargs
    ) -> str:
        arrangements = kb_content.get('arrangements', [])
        if not arrangements:
            return ""
        
        favorites = [arr for arr in arrangements if arr.get('is_featured')]
        if not favorites:
            return ""
        
        # Deduplicate
        seen = {}
        for arr in favorites:
            name = arr.get('name', '').strip().lower()
            if name and name not in seen:
                seen[name] = arr
        
        unique_favorites = list(seen.values())[:self.max_items]
        
        parts = ["⭐ POPULAIRE ARRANGEMENTEN:\n\n"]
        for arr in unique_favorites:
            name = arr.get('name', 'Onbekend')
            prices = arr.get('price', [])
            price_str = ', '.join(prices) if isinstance(prices, list) else str(prices) if prices else ""
            
            line = f"• {name}"
            if price_str:
                line += f" - {price_str}"
            parts.append(line + "\n")
        
        parts.append("\n")
        logger.info(f"✅ {self.name} module: {len(unique_favorites)} items")
        return "".join(parts)


class FAQModule(ContextModule):
    """Module for FAQ results."""
    
    def __init__(self, max_items: int = 5):
        self.max_items = max_items
    
    @property
    def name(self) -> str:
        return "faqs"
    
    def should_include(self, signals: QuerySignals, search_results: List[SearchResult] = None, **kwargs) -> bool:
        # Include if there are FAQ results
        if not search_results:
            return False
        return any(r.get('is_faq') for r in search_results)
    
    def render(
        self, 
        kb_content: KBContent, 
        search_results: List[SearchResult],
        signals: QuerySignals,
        **kwargs
    ) -> str:
        relevant_faqs = [r for r in search_results if r.get('is_faq')]
        if not relevant_faqs:
            return ""
        
        parts = ["❓ VEELGESTELDE VRAGEN:\n\n"]
        
        for faq in relevant_faqs[:self.max_items]:
            question = faq.get('question', faq.get('title', '').replace('FAQ: ', ''))
            answer = faq.get('answer', '')
            
            if not answer and 'ANTWOORD:' in faq.get('content', ''):
                answer = faq['content'].split('ANTWOORD:')[1].strip()
            elif not answer:
                answer = faq.get('content', '')
            
            parts.append(f"• {question}\n")
            parts.append(f"  → {answer}\n\n")
        
        logger.info(f"✅ {self.name} module: {len(relevant_faqs[:self.max_items])} FAQs")
        return "".join(parts)


class SearchResultsModule(ContextModule):
    """Module for additional search results."""
    
    def __init__(self, max_items: int = 3, excerpt_length: int = 2000):
        self.max_items = max_items
        self.excerpt_length = excerpt_length
    
    @property
    def name(self) -> str:
        return "search_results"
    
    def should_include(self, signals: QuerySignals, search_results: List[SearchResult] = None, **kwargs) -> bool:
        if not search_results:
            return False
        # Include if there are non-FAQ, non-arrangement results
        return any(not r.get('is_faq') and not r.get('is_arrangement') for r in search_results)
    
    def render(
        self, 
        kb_content: KBContent, 
        search_results: List[SearchResult],
        signals: QuerySignals,
        **kwargs
    ) -> str:
        other_results = [
            r for r in search_results 
            if not r.get('is_faq') and not r.get('is_arrangement')
        ]
        
        if not other_results:
            return ""
        
        parts = ["📋 EXTRA INFORMATIE:\n\n"]
        
        # Use ORIGINAL query from kwargs (not expanded search_query!)
        # The expanded search_query contains synonyms that may match wrong section
        original_query = kwargs.get('query', '')

        for result in other_results[:self.max_items]:
            title = result.get('title', 'Onbekend')
            content = result.get('content', '')
            
            parts.append(f"PAGINA: {title}\n")
            
            # Use smart excerpt extraction that finds relevant content around search terms
            if original_query and len(content) > self.excerpt_length:
                excerpt = extract_relevant_excerpt(
                    content=content,
                    query=original_query,
                    context_chars=self.excerpt_length,
                    before_chars=200
                )
            else:
                excerpt = content[:self.excerpt_length]
                if len(content) > self.excerpt_length:
                    excerpt += "..."
            parts.append(f"{excerpt}\n\n")
        
        logger.info(f"✅ {self.name} module: {len(other_results[:self.max_items])} results")
        return "".join(parts)


class KidsModule(ContextModule):
    """Module for kids arrangements/products."""
    
    def __init__(self, max_items: int = 5):
        self.max_items = max_items
    
    @property
    def name(self) -> str:
        return "kids"
    
    def should_include(self, signals: QuerySignals, **kwargs) -> bool:
        return signals.get('kids', False)
    
    def render(
        self, 
        kb_content: KBContent, 
        search_results: List[SearchResult],
        signals: QuerySignals,
        products: List[Dict] = None,  # Optional: products from DB
        **kwargs
    ) -> str:
        parts = []
        
        # If products provided from DB, use those
        if products:
            parts.append("🎈 KINDERARRANGEMENTEN:\n\n")
            for product in products[:self.max_items]:
                name = product.get('product_name', product.get('name', 'Onbekend'))
                price = product.get('product_price', product.get('price', 0))
                description = product.get('product_description', product.get('description', ''))
                
                if isinstance(price, (int, float)):
                    price_str = f"€{price:.2f}".replace('.', ',')
                else:
                    price_str = str(price) if price else ""
                
                parts.append(f"⭐ {name}\n")
                if price_str:
                    parts.append(f"💰 {price_str} per persoon\n")
                if description:
                    parts.append(f"📋 {description}\n")
                parts.append("\n")
        else:
            # Fall back to KB arrangements
            arrangements = kb_content.get('arrangements', [])
            kids_arrangements = [
                arr for arr in arrangements
                if any(word in (arr.get('name', '') + arr.get('category', '')).lower()
                       for word in ['kids', 'kinder', 'party', 'feest'])
            ]
            
            if kids_arrangements:
                parts.append("🎈 KINDERARRANGEMENTEN:\n\n")
                for arr in kids_arrangements[:self.max_items]:
                    name = arr.get('name', 'Onbekend')
                    prices = arr.get('price', [])
                    description = arr.get('description', '')
                    
                    price_str = ', '.join(prices) if isinstance(prices, list) else str(prices) if prices else ""
                    
                    parts.append(f"⭐ {name}\n")
                    if price_str:
                        parts.append(f"💰 {price_str}\n")
                    if description:
                        parts.append(f"📋 {description}\n")
                    parts.append("\n")
        
        if parts:
            parts.append("💡 INSTRUCTIE: Noem altijd de exacte prijzen en beschrijvingen!\n\n")
            logger.info(f"✅ {self.name} module rendered")
        
        return "".join(parts)


class BedrijfModule(ContextModule):
    """Module for business arrangements/products."""
    
    def __init__(self, max_items: int = 5):
        self.max_items = max_items
    
    @property
    def name(self) -> str:
        return "bedrijf"
    
    def should_include(self, signals: QuerySignals, **kwargs) -> bool:
        return signals.get('bedrijf', False)
    
    def render(
        self, 
        kb_content: KBContent, 
        search_results: List[SearchResult],
        signals: QuerySignals,
        products: List[Dict] = None,
        **kwargs
    ) -> str:
        parts = []
        
        if products:
            parts.append("🏢 BEDRIJFSARRANGEMENTEN:\n\n")
            for product in products[:self.max_items]:
                name = product.get('product_name', product.get('name', 'Onbekend'))
                price = product.get('product_price', product.get('price', 0))
                description = product.get('product_description', product.get('description', ''))
                
                if isinstance(price, (int, float)):
                    price_str = f"€{price:.2f}".replace('.', ',')
                else:
                    price_str = str(price) if price else ""
                
                parts.append(f"⭐ {name}\n")
                if price_str:
                    parts.append(f"💰 {price_str} per persoon\n")
                if description:
                    parts.append(f"📋 {description}\n")
                parts.append("\n")
        else:
            arrangements = kb_content.get('arrangements', [])
            bedrijf_arrangements = [
                arr for arr in arrangements
                if any(word in (arr.get('name', '') + arr.get('category', '')).lower()
                       for word in ['bedrijf', 'zakelijk', 'team', 'corporate', 'uitje'])
            ]
            
            if bedrijf_arrangements:
                parts.append("🏢 BEDRIJFSARRANGEMENTEN:\n\n")
                for arr in bedrijf_arrangements[:self.max_items]:
                    name = arr.get('name', 'Onbekend')
                    prices = arr.get('price', [])
                    description = arr.get('description', '')
                    
                    price_str = ', '.join(prices) if isinstance(prices, list) else str(prices) if prices else ""
                    
                    parts.append(f"⭐ {name}\n")
                    if price_str:
                        parts.append(f"💰 {price_str}\n")
                    if description:
                        parts.append(f"📋 {description}\n")
                    parts.append("\n")
        
        if parts:
            logger.info(f"✅ {self.name} module rendered")
        
        return "".join(parts)


class ActivityPricingModule(ContextModule):
    """Module for activity-specific pricing."""
    
    def __init__(self):
        pass
    
    @property
    def name(self) -> str:
        return "activity_pricing"
    
    def should_include(self, signals: QuerySignals, **kwargs) -> bool:
        return signals.get('pricing', False) and signals.get('activity', False)
    
    def render(
        self, 
        kb_content: KBContent, 
        search_results: List[SearchResult],
        signals: QuerySignals,
        products: List[Dict] = None,
        activity_name: str = None,
        **kwargs
    ) -> str:
        if not products:
            return ""
        
        parts = []
        
        if activity_name:
            parts.append(f"💰 PRIJZEN {activity_name.upper()}:\n\n")
        else:
            parts.append("💰 PRIJZEN:\n\n")
        
        for product in products:
            name = product.get('product_name', product.get('name', 'Onbekend'))
            price = product.get('product_price', product.get('price', 0))
            description = product.get('product_description', product.get('description', ''))
            
            if isinstance(price, (int, float)):
                price_str = f"€{price:.2f}".replace('.', ',')
            else:
                price_str = str(price) if price else "Prijs op aanvraag"
            
            parts.append(f"• {name}: {price_str}\n")
            if description:
                parts.append(f"  {description}\n")
        
        parts.append("\n")
        logger.info(f"✅ {self.name} module: {len(products)} items")
        return "".join(parts)


# ============================================================================
# DEFAULT MODULE SET
# ============================================================================

def get_default_modules() -> List[ContextModule]:
    """
    Get the default set of modules for context building.
    
    Apps can modify this list or create their own.
    """
    return [
        OrganisationModule(),
        OpeningHoursModule(),
        ArrangementsModule(),
        FavoriteArrangementsModule(),
        KidsModule(),
        BedrijfModule(),
        ActivityPricingModule(),
        FAQModule(),
        SearchResultsModule(),
    ]
