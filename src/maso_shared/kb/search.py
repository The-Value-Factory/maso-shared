"""
Stateless Knowledge Base Search Engine

This module provides search functionality for knowledge base content.
It is completely stateless - all data is passed in as parameters.

Used by both Voice AI and Main App for:
- Searching FAQs, sections, and arrangements
- Scoring and ranking results
- Query expansion with synonyms
- Signal detection (kids, bedrijf, pricing, etc.)
"""

import re
import logging
from typing import List, Dict, Any, Set, Optional
from functools import lru_cache

from .types import KBContent, SearchResult, QuerySignals
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
    IMPORTANT_SEARCH_TERMS,
    # New drink/allergy constants
    ALL_DRINK_KEYWORDS,
    DRINK_CONTENT_PATTERNS,
    ALLERGY_QUERY_KEYWORDS,
    ALLERGY_CONTENT_KEYWORDS,
    # Excerpt helper constants
    STOPWORDS_EXTENDED,
    EXCERPT_SYNONYMS,
)

logger = logging.getLogger(__name__)


class KBSearchEngine:
    """
    Stateless search engine for knowledge base content.
    
    All data is passed in as parameters - no internal state or database calls.
    
    Usage:
        engine = KBSearchEngine()
        results = engine.search(kb_content, "welke arrangementen hebben jullie?")
        signals = engine.analyze_query_signals("kinderfeestje prijzen")
    """
    
    def __init__(
        self,
        kb_content: KBContent = None,
        stopwords: Set[str] = None,
        synonyms: Dict[str, List[str]] = None,
        query_expansions: Dict[str, List[str]] = None
    ):
        """
        Initialize search engine with optional custom configuration.
        
        Args:
            stopwords: Custom stopwords set (defaults to STOPWORDS)
            synonyms: Custom synonym map (defaults to SYNONYM_MAP)
            query_expansions: Custom query expansions (defaults to QUERY_EXPANSIONS)
        """
        self.kb_content = kb_content or {}
        self.stopwords = stopwords or STOPWORDS
        self.synonyms = synonyms or SYNONYM_MAP
        self.query_expansions = query_expansions or QUERY_EXPANSIONS
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """
        Search knowledge base content for relevant results.

        Args:
            query: User's search query
            max_results: Maximum number of results to return
            min_score: Minimum score threshold (optional)

        Returns:
            List of SearchResult dicts sorted by relevance score
        """
        if not self.kb_content:
            logger.warning("⚠️ Empty knowledge base content")
            return []

        query_lower = query.lower()

        # Detect query types for boosting
        signals = self.analyze_query_signals(query_lower)

        is_arrangement_query = signals.get('arrangement', False)
        is_menu_query = any(keyword in query_lower for keyword in MENU_KEYWORDS)

        if is_arrangement_query:
            logger.info("🎯 Arrangement query detected - boosting arrangement pages")
        if is_menu_query:
            logger.info("🍕 Menu query detected - boosting menu content")

        results = self._search(
            self.kb_content,
            query,
            max_results,
            is_arrangement_query,
            is_menu_query
        )

        # Filter by min_score if specified
        if min_score > 0:
            results = [r for r in results if r.get('score', 0) >= min_score]

        return results
    def _search(
        self,
        kb_content: KBContent,
        query: str,
        max_sections: int = 5,
        is_arrangement_query: bool = False,
        is_menu_query: bool = False
    ) -> List[SearchResult]:
        """Internal search implementation with all scoring logic."""
        query_lower = query.lower()
        
        # Expand query with synonyms and expansions
        expanded_query = self._expand_query(query_lower)
        
        # Get content from KB
        sections = kb_content.get('content_sections', [])
        searchable = kb_content.get('searchable_content', {})
        arrangements = kb_content.get('arrangements', [])
        faqs = kb_content.get('faqs', [])
        
        logger.debug(f"🔍 SEARCH - sections: {len(sections)}, faqs: {len(faqs)}, arrangements: {len(arrangements)}")
        
        scored_sections: List[tuple] = []
        
        # Process FAQs
        for faq in faqs:
            score = self._score_faq(faq, query_lower, expanded_query)
            
            if score > 0:
                faq_section: SearchResult = {
                    "type": "faq",
                    "title": f"FAQ: {faq.get('question', 'Onbekend')}",
                    "content": f"VRAAG: {faq.get('question', '')}\n\nANTWOORD: {faq.get('answer', '')}",
                    "question": faq.get('question', ''),
                    "answer": faq.get('answer', ''),
                    "url": faq.get('source_url', ''),
                    "is_faq": True,
                    "score": score
                }
                scored_sections.append((score, faq_section))
        
        # Process content sections
        for i, section in enumerate(sections):
            score = self._score_section(
                section, 
                query_lower, 
                expanded_query, 
                searchable, 
                i,
                is_arrangement_query,
                is_menu_query
            )
            
            if score > 0:
                section_copy = dict(section)
                section_copy['score'] = score
                section_copy['search_query'] = expanded_query
                scored_sections.append((score, section_copy))
        
        # Process arrangements
        for arr in arrangements:
            score = self._score_arrangement(
                arr, 
                query_lower, 
                expanded_query,
                is_arrangement_query
            )
            
            if score > 0:
                # ✅ FIX: Handle multiple price formats (int, float, str, list)
                price_raw = arr.get('price', [])
                if isinstance(price_raw, (int, float)):
                    # Number → format with currency
                    price_str = f"€{price_raw:.2f}".replace('.', ',')
                elif isinstance(price_raw, str):
                    # String → use directly
                    price_str = price_raw
                elif isinstance(price_raw, list) and price_raw:
                    # List → join elements
                    price_str = ', '.join(str(p) for p in price_raw)
                else:
                    # Empty or None → fallback
                    price_str = "Prijs op aanvraag"
                
                arr_section: SearchResult = {
                    "type": "arrangement",
                    "title": f"Arrangement: {arr.get('name', 'Onbekend')}",
                    "content": f"{arr.get('name', '')} - {arr.get('description', '')} - Prijs: {price_str} - Duur: {arr.get('duration', '')}",
                    "url": arr.get('source_url', ''),
                    "metadata": {
                        "prices": arr.get('price', []),
                        "duration": arr.get('duration', ''),
                        "activities": arr.get('activities', [])
                    },
                    "is_arrangement": True,
                    "score": score
                }
                scored_sections.append((score, arr_section))
        
        # Sort by score and return top sections
        scored_sections.sort(reverse=True, key=lambda x: x[0])
        return [section for score, section in scored_sections[:max_sections]]
    
    def _score_faq(
        self,
        faq: Dict[str, Any],
        query_lower: str,
        expanded_query: str
    ) -> float:
        """Score a FAQ item based on query relevance."""
        score = 0.0
        question = faq.get('question', '').lower()
        answer = faq.get('answer', '').lower()
        category = faq.get('category', '')
        
        # Detect query characteristics
        is_height_query = any(word in query_lower for word in ['lang', 'groot', 'lengte', 'meter', 'cm'])
        is_racing_query = any(word in query_lower for word in ['simracen', 'racen', 'race', 'simrace', 'racer'])
        is_duration_query = any(word in query_lower for word in ['duurt', 'duren', 'tijd'])
        is_age_query = any(word in query_lower for word in ['leeftijd', 'jaar', 'oud', 'minimumleeftijd'])
        is_minimum_query = any(word in query_lower for word in ['minimum', 'minimaal', 'minimale', 'min'])
        
        is_simulator_count_query = any(phrase in query_lower for phrase in [
            'hoeveel simulator', 'aantal simulator', 'hoeveel race',
            'hoeveel personen racen', 'hoeveel kunnen racen'
        ])
        
        # Specific query type scoring
        if is_simulator_count_query:
            if any(phrase in question for phrase in ['hoeveel personen', 'tegelijk racen', 'tegen elkaar racen']):
                score += 40
            if any(phrase in answer for phrase in ['20 personen', 'twintig personen', '20 mensen']):
                score += 35
        
        if 'hoe lang' in query_lower and is_racing_query:
            if 'lengte' in question or 'leeftijd' in question or '140' in answer or 'meter' in answer:
                score += 30
            elif 'duurt' in question or 'duur' in question:
                score -= 15
        
        if is_minimum_query and is_racing_query and (is_age_query or is_height_query):
            if any(word in question for word in ['leeftijd', 'lengte', 'minimum']):
                score += 35
            if any(word in answer for word in ['140', '1,40', 'meter', '6 jaar', '6 tot']):
                score += 30
        
        if is_duration_query and not is_racing_query:
            if 'duurt' in question or 'duur' in question:
                score += 25
        
        # Exact match bonus
        if query_lower in question or question in query_lower:
            score += 50
        
        # Category relevance
        if is_racing_query and category == 'simracen':
            score += 20
        elif is_racing_query and category != 'simracen':
            score -= 10
        
        # Word matching
        for word in expanded_query.split():
            if len(word) > 2 and word not in self.stopwords:
                if word in question:
                    score += 15
                if word in answer:
                    score += 8
        
        # Numeric queries
        if any(word in query_lower for word in ['hoeveel', 'aantal', 'hoe veel']):
            numbers_in_answer = re.findall(r'\d+', answer)
            if numbers_in_answer:
                score += 15
        
        # Height/age indicator matching
        height_indicators = ['lengte', 'lang', 'groot', 'meter', 'cm', '140', '1,40', 'height']
        age_indicators = ['leeftijd', 'jaar', 'oud', 'jong', 'age']
        
        if any(ind in query_lower for ind in height_indicators):
            if any(ind in answer for ind in ['140', '1,40', '1.40', 'meter']):
                score += 25
            if any(ind in question for ind in height_indicators):
                score += 15
        
        if any(ind in query_lower for ind in age_indicators):
            if any(ind in answer for ind in ['jaar', 'oud', 'jong', 'leeftijd']):
                score += 20
            if any(ind in question for ind in age_indicators):
                score += 15
        
        # FAQ-style keyword matching
        faq_keywords = ['mag', 'kunnen', 'vanaf', 'wanneer', 'hoe', 'wat']
        for keyword in faq_keywords:
            if keyword in query_lower and keyword in question:
                score += 5
        
        return score
    
    def _score_section(
        self,
        section: Dict[str, Any],
        query_lower: str,
        expanded_query: str,
        searchable: Dict[str, List[int]],
        section_index: int,
        is_arrangement_query: bool = False,
        is_menu_query: bool = False
    ) -> float:
        """Score a content section based on query relevance."""
        score = 0.0
        content = section.get('content', '').lower()
        title = section.get('title', '').lower()
        url = section.get('url', '').lower()
        
        # Boost arrangement pages for arrangement queries
        if is_arrangement_query:
            if 'arrangementen' in title or 'deals' in title or 'arrangement' in url:
                score += 100
                logger.debug(f"🎯 Arrangement page boost: '{title}' +100 points")
        
        # Boost PDF menus for menu queries
        is_pdf_menu = 'pdf:' in title and any(word in content for word in ['menu', 'koffie', 'bier', 'pizza', 'cocktail'])
        if is_menu_query and is_pdf_menu:
            score += 50
            logger.debug(f"🍕 PDF Menu boost: '{title}' +50 points for menu query")
        
        # Racing content boost
        is_racing_query = any(word in query_lower for word in ['simracen', 'racen', 'race', 'simrace', 'racer'])
        if is_racing_query and 'simracen' in title:
            score += 15
        

        # DRINK-SPECIFIC BOOST
        # When user asks about drinks (bier, wijn, etc.), boost sections containing drink info
        query_words = set(query_lower.split())
        is_drink_query = bool(query_words & ALL_DRINK_KEYWORDS)
        if is_drink_query:
            has_drink_content = any(pattern in content or pattern in title for pattern in DRINK_CONTENT_PATTERNS)
            if has_drink_content:
                score += 30
                # Extra boost if title contains drink word
                if any(drink in title for drink in ['bier', 'wijn', 'cocktail', 'drank', 'menu']):
                    score += 15

        # ALLERGY/DIET BOOST
        # When user asks about allergies, boost sections with allergy info
        is_allergy_query = bool(query_words & ALLERGY_QUERY_KEYWORDS)
        if is_allergy_query:
            has_allergy_content = any(kw in content for kw in ALLERGY_CONTENT_KEYWORDS)
            if has_allergy_content:
                score += 35
                # Extra boost for sections specifically about allergies/diets
                if any(kw in title for kw in ['allergie', 'dieet', 'vegan', 'vegetarisch', 'glutenvrij']):
                    score += 20

        # Searchable index matching
        for term, section_indices in searchable.items():
            if term in expanded_query and section_index in section_indices:
                score += 10
        
        # Title word matching
        if any(word in title for word in expanded_query.split() if word not in self.stopwords):
            score += 8
        
        # Content word matching
        for word in expanded_query.split():
            if len(word) > 2 and word not in self.stopwords:
                score += content.count(word) * 2
        
        # Important term matching
        for term in IMPORTANT_SEARCH_TERMS:
            if term in expanded_query:
                if term in title:
                    score += 12
                elif term in content:
                    score += 6
        
        return score
    
    def _score_arrangement(
        self,
        arr: Dict[str, Any],
        query_lower: str,
        expanded_query: str,
        is_arrangement_query: bool = False
    ) -> float:
        """Score an arrangement based on query relevance."""
        score = 0.0
        arr_name = arr.get('name', '').lower()
        arr_desc = arr.get('description', '').lower()
        arr_category = arr.get('category', '').lower()
        
        # Huge boost for arrangement queries
        if is_arrangement_query:
            score += 80
            logger.debug(f"🎯 Arrangement query boost: '{arr_name}' +80 points")
        
        # Kids arrangement boost
        if any(word in query_lower for word in ['kinderfeest', 'kinderparty', 'kids', 'kinder', 'verjaardag', 'birthday']):
            if any(word in arr_name + arr_desc + arr_category for word in ['kids', 'kinder', 'party']):
                score += 60
                logger.debug(f"🎈 Kids arrangement boost: '{arr_name}' +60 points")
        
        # Name word matching
        if any(word in arr_name for word in expanded_query.split() if word not in self.stopwords):
            score += 15
        
        # Content word matching
        for word in expanded_query.split():
            if len(word) > 2 and word not in self.stopwords:
                count = (arr_name + arr_desc).count(word)
                if count > 0:
                    score += count * 3
        
        # Arrangement keyword matching
        arrangement_keywords = ['arrangement', 'kids', 'party', 'kinderfeest', 'verjaardag', 'deal']
        for keyword in arrangement_keywords:
            if keyword in expanded_query and keyword in arr_desc:
                score += 8
        
        return score
    
    def _expand_query(self, query: str) -> str:
        """
        Expand query with synonyms and query expansions.
        
        Args:
            query: Original query (lowercase)
            
        Returns:
            Expanded query string with additional terms
        """
        expanded_query = query
        
        # Apply query expansions
        for key, expansions in self.query_expansions.items():
            if key in query:
                expanded_query += ' ' + ' '.join(expansions)
        
        # Expand with synonyms
        expanded_words = set(expanded_query.split())
        for base_word, synonyms in self.synonyms.items():
            if base_word in query:
                expanded_words.update(synonyms)
            for synonym in synonyms:
                if synonym in query:
                    expanded_words.update([base_word] + [s for s in synonyms if s != synonym])
        
        return ' '.join(expanded_words)
    
    def analyze_query_signals(self, query: str) -> QuerySignals:
        """
        Analyze query to detect relevant signals.
        
        Args:
            query: User's query (will be lowercased)
            
        Returns:
            QuerySignals dict with boolean flags for each signal type
        """
        query_lower = query.lower()
        
        signals: QuerySignals = {
            'kids': False,
            'bedrijf': False,
            'pricing': False,
            'activity': False,
            'arrangement': False,
            'general': False,
            'location': False,
            'opening_hours': False,
        }
        
        # Kids signals
        signals['kids'] = any(keyword in query_lower for keyword in KIDS_KEYWORDS)
        
        # Bedrijf signals
        signals['bedrijf'] = any(keyword in query_lower for keyword in BEDRIJF_KEYWORDS)
        
        # Pricing signals
        signals['pricing'] = any(keyword in query_lower for keyword in PRICING_KEYWORDS)
        
        # Arrangement signals
        signals['arrangement'] = any(keyword in query_lower for keyword in ARRANGEMENT_KEYWORDS)
        
        # Opening hours signals
        signals['opening_hours'] = any(keyword in query_lower for keyword in OPENING_HOURS_KEYWORDS)
        
        # General signals
        signals['general'] = any(keyword in query_lower for keyword in GENERAL_KEYWORDS)
        
        # Location signals
        signals['location'] = any(keyword in query_lower for keyword in LOCATION_KEYWORDS)
        
        return signals
    
    def extract_relevant_excerpt(
        self,
        content: str,
        search_query: str,
        context_chars: int = 1000,
        before_chars: int = 300
    ) -> str:
        """
        Extract relevant excerpt from content around search terms.
        
        Enhanced with Dutch word stem handling and synonym expansion:
        - biertje -> bier
        - wijntje -> wijn
        - drankje -> drank
        
        Args:
            content: Full content text
            search_query: Query to find relevant section
            context_chars: Characters to include after match
            before_chars: Characters to include before match

        Returns:
            Relevant excerpt with ellipsis
        """
        content_lower = content.lower()
        query_lower = search_query.lower()
        
        # Build expanded search terms with stems and synonyms (EXCLUDING stopwords)
        search_terms = []
        for word in query_lower.split():
            if len(word) > 2 and word not in STOPWORDS_EXTENDED:
                search_terms.append(word)
                # Add Dutch word stems (remove common diminutive suffixes)
                if word.endswith('tje'):
                    search_terms.append(word[:-3])  # biertje -> bier
                elif word.endswith('je'):
                    search_terms.append(word[:-2])  # wijntje -> wijn
                elif word.endswith('tjes'):
                    search_terms.append(word[:-4])  # biertjes -> bier
                elif word.endswith('jes'):
                    search_terms.append(word[:-3])  # wijntjes -> wijn
        
        # Add synonyms for common drink/food terms
        expanded_terms = list(search_terms)
        for term in search_terms:
            if term in EXCERPT_SYNONYMS:
                expanded_terms.extend(EXCERPT_SYNONYMS[term])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for t in expanded_terms:
            if t not in seen:
                seen.add(t)
                unique_terms.append(t)
        
        # Find best match position using expanded terms
        best_pos = -1
        best_score = 0
        
        for word in unique_terms:
            pos = content_lower.find(word)
            if pos >= 0:
                # Score based on word importance and position
                score = len(word) * 2  # Longer words = better match
                # Bonus for original query terms (not synonyms)
                if word in search_terms:
                    score += 5
                # Extra bonus for longer, more specific terms
                if len(word) >= 6:
                    score += 3
                if score > best_score:
                    best_score = score
                    best_pos = pos

        if best_pos < 0:
            return content[:context_chars] + "..."

        # Extract context around match
        start = max(0, best_pos - before_chars)
        end = min(len(content), best_pos + context_chars)

        # Expand to sentence boundaries
        while start > 0 and content[start] not in '.!?\n':
            start -= 1
            if best_pos - start > before_chars + 100:
                break

        while end < len(content) and content[end] not in '.!?\n':
            end += 1
            if end - best_pos > context_chars + 100:
                break

        excerpt = content[start:end].strip()

        if start > 0:
            excerpt = "..." + excerpt
        if end < len(content):
            excerpt = excerpt + "..."

        return excerpt



# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

# Global search engine instance
_search_engine_instance: Optional[KBSearchEngine] = None


def get_search_engine() -> KBSearchEngine:
    """Get or create a global search engine instance."""
    global _search_engine_instance
    if _search_engine_instance is None:
        _search_engine_instance = KBSearchEngine()
    return _search_engine_instance


def extract_relevant_excerpt(
    content: str,
    query: str,
    max_length: int = 800,
    context_chars: int = 400,
    before_chars: int = 100,
) -> str:
    """
    Standalone function to extract relevant excerpt from content.
    
    This is a convenience wrapper around the KBSearchEngine method.
    
    Args:
        content: Full content text
        query: Search query  
        max_length: Maximum excerpt length (default 800)
        context_chars: Characters to include after match
        before_chars: Characters to include before match
        
    Returns:
        Relevant excerpt from content
    """
    engine = get_search_engine()
    return engine.extract_relevant_excerpt(
        content=content,
        search_query=query,
        context_chars=context_chars,
        before_chars=before_chars,
    )
