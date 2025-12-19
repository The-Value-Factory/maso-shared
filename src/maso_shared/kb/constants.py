"""
Shared constants for Knowledge Base search and context building

These constants are used by both Voice AI and Main App for:
- Query expansion and synonym matching
- Signal detection (kids, bedrijf, pricing, etc.)
- Stopword filtering
"""

# ============================================================================
# STOPWORDS - Dutch filler words to filter out during search
# ============================================================================

STOPWORDS = {
    # Articles & determiners
    'de', 'het', 'een', 'en', 'van', 'in', 'op', 'te', 'is', 'voor', 'dat', 'die',
    'aan', 'met', 'als', 'of', 'er', 'zijn', 'was', 'heeft', 'bij', 'naar', 'om',
    
    # Modal verbs
    'kan', 'kunnen', 'wil', 'willen', 'moet', 'moeten', 'zou', 'zouden', 'mag', 'mogen',
    
    # Adverbs & conjunctions
    'ook', 'wel', 'nog', 'maar', 'want', 'dan', 'deze', 'dit', 'die', 'daar',
    
    # Pronouns
    'je', 'jullie', 'ik', 'we', 'ze', 'hij', 'zij', 'hun', 'uw', 'mijn', 'jouw',
    
    # Common filler words
    'me', 'meer', 'over', 'graag', 'even', 'gewoon', 'hier', 'daar', 'waar',
    'hoe', 'wat', 'wie', 'welke', 'welk', 'waarom', 'wanneer',
}


# ============================================================================
# SYNONYM MAP - Expand queries with related terms
# ============================================================================

SYNONYM_MAP = {
    'leeftijd': ['jaar', 'oud', 'jong', 'oudheid', 'age', 'minimumleeftijd', 'lengte', 'minimumlengte'],
    'lengte': ['lang', 'groot', 'meter', 'cm', 'centimeter', 'height', 'hoog', 'minimumlengte'],
    'kind': ['kinderen', 'kids', 'jeugd', 'peuter', 'tiener', 'jong'],
    'prijs': ['kosten', 'kost', 'betalen', 'tarief', 'tarieven', 'euro', 'bedrag'],
    'open': ['openingstijd', 'openingstijden', 'geopend', 'gesloten', 'tijden'],
    'reserveren': ['boeken', 'reservering', 'afspraak', 'boeking'],
    'mag': ['kunnen', 'toegestaan', 'mogelijk', 'welkom', 'mogen'],
    'simracen': ['racen', 'race', 'simrace', 'simracing', 'racing', 'racer', 'simulator'],
    'duur': ['duurt', 'lang', 'tijd', 'tijdsduur'],
    'minimum': ['minimaal', 'minimale', 'min', 'vanaf'],
    'menu': ['menukaart', 'kaart', 'eten', 'drinken', 'gerechten'],
    'dranken': ['drinken', 'drankje', 'drinks', 'drankenkaart'],
    'bier': ['biertje', 'pils', 'pilsener', 'speciaalbier'],
    'cocktail': ['cocktails', 'mix', 'mixdrink'],
    'eten': ['hapjes', 'bites', 'snacks', 'gerecht', 'maaltijd'],
}


# ============================================================================
# QUERY EXPANSIONS - Expand specific queries with related phrases
# ============================================================================

QUERY_EXPANSIONS = {
    'simulators': ['personen racen', 'tegelijk racen', 'race plekken', 'racen bij ons'],
    'simulator': ['personen racen', 'tegelijk racen', 'race plekken'],
    'hoeveel simulators': ['hoeveel personen', 'aantal personen racen', 'tegelijk racen'],
    'aantal simulators': ['hoeveel personen', 'aantal personen racen', 'tegelijk racen'],
    'circuits': ['verschillende circuits', 'formule 1'],
    'f1': ['formule 1', 'race', 'simulators', 'elke zondag'],
}


# ============================================================================
# SIGNAL DETECTION KEYWORDS
# ============================================================================

# Kids/children related queries
KIDS_KEYWORDS = [
    'kids', 'kinder', 'kinderen', 'kinderfeest', 'kinderfeestje',
    'kinderparty', 'party', 'feest', 'feestje', 'verjaardag',
    'birthday', 'peuter', 'tiener', 'jeugd'
]

# Business/corporate related queries
BEDRIJF_KEYWORDS = [
    'bedrijf', 'bedrijven', 'bedrijfsuitje', 'bedrijfsuitjes',
    'teamuitje', 'teambuilding', 'zakelijk', 'zakelijke',
    'collega', 'collega\'s', 'werk', 'kantoor', 'afdeling',
    'personeelsuitje', 'personeelsfeest'
]

# Pricing related queries
PRICING_KEYWORDS = [
    'wat kost', 'hoeveel kost', 'kosten', 'prijs', 'prijzen',
    'tarief', 'tarieven', 'euro', 'betalen', 'bedrag',
    'per persoon', 'p.p.', 'pp'
]

# Arrangement/package related queries
ARRANGEMENT_KEYWORDS = [
    'arrangement', 'arrangementen', 'pakket', 'pakketten',
    'deal', 'deals', 'aanbod', 'aanbieding', 'aanbiedingen',
    'product', 'producten', 'welke', 'wat hebben jullie',
    'wat bieden jullie', 'wat voor', 'welke mogelijkheden',
    'opties', 'keuzes', 'nog meer arrangement', 'andere arrangementen'
]

# Opening hours related queries
OPENING_HOURS_KEYWORDS = [
    'open', 'gesloten', 'dicht', 'openingstijd', 'openingstijden',
    'tijd', 'tijden', 'morgen', 'vandaag', 'overmorgen',
    'maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag',
    'weekdag', 'weekend', 'wanneer open', 'hoe laat', 'tot hoe laat',
    'sluitingstijd', 'sluitingstijden'
]

# General information queries
GENERAL_KEYWORDS = [
    'vertel', 'over jullie', 'over ons', 'wie zijn jullie',
    'locatie', 'waar', 'adres', 'route', 'bereikbaar',
    'info', 'informatie', 'weten'
]

# Location related queries
LOCATION_KEYWORDS = [
    'locatie', 'waar', 'adres', 'vinden', 'zitten',
    'route', 'rijden', 'parkeren', 'parkeerplaats',
    'ov', 'openbaar vervoer', 'bus', 'trein'
]

# Menu/food related queries
MENU_KEYWORDS = [
    'menu', 'menukaart', 'dranken', 'drankenkaart', 'eten', 'drinken',
    'bier', 'cocktail', 'cocktails', 'wijn', 'pizza', 'koffie', 'thee', 'fris',
    'op het menu', 'wat serveren', 'gerechten', 'drankjes', 'hapjes'
]


# ============================================================================
# DAY NAME TRANSLATIONS
# ============================================================================

DAY_NAMES_EN_TO_NL = {
    'monday': 'Maandag',
    'tuesday': 'Dinsdag',
    'wednesday': 'Woensdag',
    'thursday': 'Donderdag',
    'friday': 'Vrijdag',
    'saturday': 'Zaterdag',
    'sunday': 'Zondag'
}

DAYS_ORDER = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']


# ============================================================================
# IMPORTANT SEARCH TERMS - Get extra weight in search
# ============================================================================

IMPORTANT_SEARCH_TERMS = [
    'reservering', 'prijzen', 'openingstijden', 'contact', 'activiteiten',
    'jeu de boules', 'simracen', 'arrangement', 'kids party', 'kinderfeest',
    'leeftijd', 'lengte', '140', 'meter'
]
