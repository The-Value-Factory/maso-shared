"""
Query Analyzer - Analyze queries for signals, categories, and intent

This module provides query analysis functionality that both apps can use.
It detects:
- Query signals (arrangement, kids, opening_hours, etc.)
- Relevant categories for search
- Special intents (pricing, reservation, etc.)

Usage:
    from maso_shared.kb.query_analyzer import QueryAnalyzer
    
    analyzer = QueryAnalyzer()
    signals = analyzer.analyze("kinderfeestje prijzen")
    # Returns: {"kids": True, "pricing": True, "arrangement": True, ...}
"""

import logging
import re
from typing import List, Dict, Set, Optional, Any, Callable

from .types import QuerySignals
from .constants import (
    DRINK_KEYWORDS,
    ALLERGY_QUERY_KEYWORDS,
)

# Default activity synonyms - can be overridden in constructor
DEFAULT_ACTIVITY_SYNONYMS = {
    'biljart': ['biljart', 'pool', 'snooker', 'poolbiljart', 'billiard'],
    'bowlen': ['bowl', 'bowlen', 'bowling', 'baan', 'kegelen'],
    'darten': ['dart', 'darten', 'pijl', 'pijltje', 'darts'],
    'shuffleboard': ['shuffle', 'shuffleboard', 'sjoelen'],
    'jeu_de_boules': ['boule', 'boules', 'petanque', 'jeu de boules', 'boulen', 'jeu'],
    'karaoke': ['karaoke', 'zing', 'zang', 'microfoon', 'zingen'],
    'quiz': ['quiz', 'pubquiz', 'trivia', 'vraag', 'vragen', 'quizzen'],
    'escape_room': ['escape', 'escaperoom', 'ontsnappen', 'puzzle'],
    'lasergamen': ['laser', 'lasergame', 'lasergamen', 'lasertag'],
    'klimmen': ['klimmen', 'klim', 'klimwand', 'boulderen'],
    'trampolinespringen': ['trampoline', 'springen', 'trampolinepark'],
}

logger = logging.getLogger(__name__)


# ============================================================================
# DEFAULT CATEGORY DEFINITIONS
# ============================================================================

# Standard Dutch category patterns
DEFAULT_CATEGORY_PATTERNS = {
    # General categories
    'algemeen': ['algemeen', 'general', 'over', 'about', 'wat is', 'welkom', 'hallo'],
    'openingstijden': ['open', 'geopend', 'sluit', 'dicht', 'wanneer', 'uur', 'tijd', 'openingstijd', 'ma', 'di', 'wo', 'do', 'vr', 'za', 'zo', 'maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag', 'weekend'],
    'locatie': ['adres', 'waar', 'locatie', 'route', 'parkeren', 'parkeerplaats', 'bereikbaar', 'rijden', 'navigeer', 'vind'],
    'contact': ['telefoon', 'bel', 'mail', 'email', 'contact', 'bereik', 'nummer', 'app', 'whatsapp'],
    
    # Arrangement categories
    'arrangementen': ['arrangement', 'pakket', 'formule', 'deal', 'aanbieding', 'actie', 'aanbod'],
    'kinderfeestje': ['kind', 'kinder', 'kids', 'kinderen', 'feest', 'party', 'verjaardag', 'jarig'],
    'bedrijfsuitje': ['bedrijf', 'team', 'teamuitje', 'teambuilding', 'corporate', 'zakelijk', 'uitje', 'personeels', 'collega'],
    'vrijgezellenfeest': ['vrijgezel', 'bachelor', 'bachelorette', 'vrijgezellenfeest', 'trouw'],
    
    # Activity categories
    'biljart': ['biljart', 'pool', 'snooker', 'poolbiljart'],
    'bowlen': ['bowl', 'bowlen', 'bowling', 'baan', 'kegelen'],
    'darten': ['dart', 'darten', 'pijl', 'pijltje'],
    'shuffleboard': ['shuffle', 'shuffleboard', 'sjoelen'],
    'jeu_de_boules': ['boule', 'petanque', 'jeu de boules', 'boulen'],
    'karaoke': ['karaoke', 'zing', 'zang', 'microfoon'],
    'quiz': ['quiz', 'pubquiz', 'trivia', 'vraag', 'vragen'],
    
    # Service categories
    'eten': ['eten', 'maaltijd', 'diner', 'lunch', 'ontbijt', 'hapje', 'snack', 'burger', 'pizza', 'menu', 'kaart', 'gerecht'],
    'drinken': ['drink', 'drank', 'bier', 'wijn', 'cocktail', 'drankje', 'bar', 'tap', 'frisdrank'],
    'reserveren': ['reserv', 'boek', 'boeking', 'beschikbaar', 'beschikbaarheid', 'plek', 'plekje'],
    'prijs': ['prijs', 'kost', 'kosten', 'euro', '€', 'tarief', 'betaal', 'geld', 'budget', 'goedkoop', 'duur'],
    'groep': ['groep', 'grote', 'groot', 'personen', 'persoon', 'mensen', 'gezelschap', 'feest'],
    
    # Special categories
    'allergie': ['allergi', 'intolerant', 'gluten', 'lactose', 'noten', 'vegan', 'vegetar'],
    'toegankelijkheid': ['rolstoel', 'toegankelijk', 'handicap', 'invalide', 'lift', 'trap'],
}


# ============================================================================
# QUERY ANALYZER CLASS
# ============================================================================

class QueryAnalyzer:
    """
    Analyzes queries to extract signals, categories, and intent.
    
    This is a configurable analyzer that apps can extend with custom
    categories and signal detectors.
    
    Usage:
        analyzer = QueryAnalyzer()
        
        # Analyze query
        signals = analyzer.analyze("kinderfeestje prijzen")
        
        # Or with custom detectors
        analyzer.register_detector('my_signal', my_detector_func)
    """
    
    def __init__(
        self,
        category_patterns: Dict[str, List[str]] = None,
        activity_synonyms: Dict[str, List[str]] = None,
        extra_detectors: Dict[str, Callable[[str], bool]] = None,
    ):
        """
        Initialize the analyzer.
        
        Args:
            category_patterns: Custom category patterns (or use defaults)
            activity_synonyms: Activity name synonyms (or use defaults from constants)
            extra_detectors: Additional signal detectors to register
        """
        self.category_patterns = category_patterns or DEFAULT_CATEGORY_PATTERNS.copy()
        self.activity_synonyms = activity_synonyms or DEFAULT_ACTIVITY_SYNONYMS.copy()
        
        # Signal detectors - functions that take query and return bool
        self._detectors: Dict[str, Callable[[str], bool]] = {}
        self._register_default_detectors()
        
        # Register extra detectors
        if extra_detectors:
            for name, detector in extra_detectors.items():
                self.register_detector(name, detector)
    
    def _register_default_detectors(self):
        """Register the default signal detectors."""
        
        # General query
        self.register_detector('general', lambda q: any(
            w in q.lower() for w in ['hallo', 'hoi', 'welkom', 'wat kun', 'wat kan', 'help']
        ))
        
        # Opening hours
        self.register_detector('opening_hours', lambda q: any(
            w in q.lower() for w in ['open', 'geopend', 'sluit', 'dicht', 'openingstijd', 'uur']
        ) or any(d in q.lower() for d in ['maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag', 'weekend']))
        
        # Location
        self.register_detector('location', lambda q: any(
            w in q.lower() for w in ['adres', 'waar', 'locatie', 'route', 'parkeren', 'navigeer', 'rijden']
        ))
        
        # Arrangements
        self.register_detector('arrangement', lambda q: any(
            w in q.lower() for w in ['arrangement', 'pakket', 'formule', 'deal', 'feest', 'party', 'uitje']
        ))
        
        # Kids
        self.register_detector('kids', lambda q: any(
            w in q.lower() for w in ['kind', 'kinder', 'kids', 'kinderen', 'kinderfeest', 'kinderparty']
        ))
        
        # Business
        self.register_detector('bedrijf', lambda q: any(
            w in q.lower() for w in ['bedrijf', 'team', 'teamuitje', 'teambuilding', 'corporate', 'zakelijk', 'collega']
        ))
        
        # Pricing
        self.register_detector('pricing', lambda q: any(
            w in q.lower() for w in ['prijs', 'kost', 'kosten', 'euro', '€', 'tarief', 'goedkoop', 'duur', 'budget']
        ))
        
        # Reservation
        self.register_detector('reservation', lambda q: any(
            w in q.lower() for w in ['reserv', 'boek', 'boeking', 'afspraak', 'beschikbaar']
        ))
        
        # Food
        self.register_detector('food', lambda q: any(
            w in q.lower() for w in ['eten', 'maaltijd', 'diner', 'lunch', 'hapje', 'menu', 'gerecht', 'burger', 'pizza']
        ))
        
        # Drinks
        self.register_detector('drinks', lambda q: any(
            w in q.lower() for w in DRINK_KEYWORDS
        ))
        
        # Allergies
        self.register_detector('allergy', lambda q: any(
            w in q.lower() for w in ALLERGY_QUERY_KEYWORDS
        ))
        
        # Groups
        self.register_detector('group', lambda q: any(
            w in q.lower() for w in ['groep', 'grote', 'personen', 'mensen', 'gezelschap']
        ) or re.search(r'\b\d+\s*(personen|mensen|persoon)\b', q.lower()))
        
        # Activity (generic - specific activity detected separately)
        self.register_detector('activity', lambda q: self._detect_activity(q) is not None)
    
    def _detect_activity(self, query: str) -> Optional[str]:
        """
        Detect which activity the query is about.
        
        Returns the normalized activity name or None.
        """
        query_lower = query.lower()
        
        for activity, synonyms in self.activity_synonyms.items():
            for synonym in synonyms:
                if synonym.lower() in query_lower:
                    return activity
        
        return None
    
    def register_detector(self, name: str, detector: Callable[[str], bool]):
        """
        Register a custom signal detector.
        
        Args:
            name: Signal name
            detector: Function that takes query string and returns bool
        """
        self._detectors[name] = detector
    
    def analyze(self, query: str) -> QuerySignals:
        """
        Analyze a query and return signals.
        
        Args:
            query: The query to analyze
            
        Returns:
            Dictionary of signal names to boolean values
        """
        signals: QuerySignals = {}
        
        # Run all detectors
        for name, detector in self._detectors.items():
            try:
                signals[name] = detector(query)
            except Exception as e:
                logger.warning(f"Detector {name} failed: {e}")
                signals[name] = False
        
        # Add detected activity name if present
        activity = self._detect_activity(query)
        if activity:
            signals['detected_activity'] = activity  # type: ignore
        
        logger.debug(f"Query signals: {signals}")
        return signals
    
    def detect_categories(self, query: str, max_categories: int = 5) -> List[str]:
        """
        Detect relevant categories for a query.
        
        Args:
            query: The query to analyze
            max_categories: Maximum categories to return
            
        Returns:
            List of category names, ordered by relevance
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        category_scores: Dict[str, int] = {}
        
        for category, patterns in self.category_patterns.items():
            score = 0
            
            for pattern in patterns:
                # Exact word match
                if pattern in query_words:
                    score += 2
                # Substring match
                elif pattern in query_lower:
                    score += 1
            
            if score > 0:
                category_scores[category] = score
        
        # Sort by score and return top categories
        sorted_cats = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        return [cat for cat, _ in sorted_cats[:max_categories]]
    
    def extract_group_size(self, query: str) -> Optional[int]:
        """
        Extract group size from query if mentioned.
        
        Args:
            query: The query to analyze
            
        Returns:
            Group size as integer, or None if not found
        """
        patterns = [
            r'(\d+)\s*(personen|mensen|persoon|pers)',
            r'groep\s*van\s*(\d+)',
            r'met\s*(\d+)\s*(mensen|personen)',
            r'(\d+)\s*man\b',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def detect_language(self, query: str) -> str:
        """
        Detect the language of the query.
        
        Returns:
            'nl' for Dutch, 'en' for English, 'nl' as default
        """
        # Simple heuristic based on common words
        dutch_indicators = {'en', 'van', 'het', 'de', 'een', 'wat', 'is', 'zijn', 'voor', 'met', 'op', 'aan', 'bij', 'naar'}
        english_indicators = {'the', 'a', 'an', 'is', 'are', 'what', 'how', 'do', 'does', 'can', 'could', 'with', 'for', 'at', 'to'}
        
        words = set(query.lower().split())
        
        dutch_score = len(words & dutch_indicators)
        english_score = len(words & english_indicators)
        
        if english_score > dutch_score and english_score >= 2:
            return 'en'
        return 'nl'
    
    def get_search_weights(self, signals: QuerySignals) -> Dict[str, float]:
        """
        Get search weight adjustments based on signals.
        
        Returns:
            Dictionary of content type to weight multiplier
        """
        weights = {
            'faq': 1.0,
            'section': 1.0,
            'arrangement': 1.0,
        }
        
        if signals.get('arrangement') or signals.get('kids') or signals.get('bedrijf'):
            weights['arrangement'] = 1.5
            weights['faq'] = 0.8
        
        if signals.get('pricing'):
            weights['arrangement'] = 1.3
            weights['faq'] = 1.2  # FAQs often contain pricing info
        
        if signals.get('opening_hours') or signals.get('location'):
            weights['section'] = 1.5
            weights['faq'] = 1.3
        
        return weights


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_default_analyzer: Optional[QueryAnalyzer] = None


def get_default_analyzer() -> QueryAnalyzer:
    """Get or create the default query analyzer."""
    global _default_analyzer
    if _default_analyzer is None:
        _default_analyzer = QueryAnalyzer()
    return _default_analyzer


def analyze_query(query: str) -> QuerySignals:
    """
    Analyze a query using the default analyzer.
    
    This is a convenience function for simple use cases.
    """
    return get_default_analyzer().analyze(query)


def detect_categories(query: str, max_categories: int = 5) -> List[str]:
    """
    Detect categories using the default analyzer.
    
    This is a convenience function for simple use cases.
    """
    return get_default_analyzer().detect_categories(query, max_categories)
