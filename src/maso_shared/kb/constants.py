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

    # Question words (for excerpt extraction)
    'ja', 'nee', 'hebben', 'weten', 'zien', 'kijken', 'komen', 'gaan', 'doen', 'maken',
    'iets', 'alles', 'niets', 'veel', 'weinig', 'beetje', 'details', 'informatie', 'info',
}

# Extended stopwords for excerpt extraction (includes English)
STOPWORDS_EXTENDED = STOPWORDS | {
    # English stopwords (for multilingual)
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'can', 'could', 'may', 'might', 'shall', 'should', 'must',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your',
    'what', 'which', 'who', 'where', 'when', 'why', 'how',
    'this', 'that', 'these', 'those', 'some', 'any', 'all',
}


# ============================================================================
# SYNONYM MAP - Expand queries with related terms
# ============================================================================

SYNONYM_MAP = {
    'leeftijd': ['jaar', 'oud', 'jong', 'oudheid', 'age', 'minimumleeftijd', 'lengte', 'minimumlengte'],
    'lengte': ['lang', 'groot', 'meter', 'cm', 'centimeter', 'height', 'hoog', 'minimumlengte'],
    'kind': ['kinderen', 'kids', 'jeugd', 'peuter', 'tiener', 'jong'],
    'kinderen': ['kids', 'kind', 'kindermenu', 'kinderkaart', 'voor de kids', 'kindereten'],
    'prijs': ['kosten', 'kost', 'betalen', 'tarief', 'tarieven', 'euro', 'bedrag'],
    'open': ['openingstijd', 'openingstijden', 'geopend', 'gesloten', 'tijden'],
    'reserveren': ['boeken', 'reservering', 'afspraak', 'boeking'],
    'mag': ['kunnen', 'toegestaan', 'mogelijk', 'welkom', 'mogen'],
    'simracen': ['racen', 'race', 'simrace', 'simracing', 'racing', 'racer', 'simulator'],
    'duur': ['duurt', 'lang', 'tijd', 'tijdsduur'],
    'minimum': ['minimaal', 'minimale', 'min', 'vanaf'],
    'menu': ['menukaart', 'kaart', 'eten', 'drinken', 'gerechten'],
    'kindermenu': ['kinderkaart', 'kindereten', 'kids menu', 'voor de kids', 'kinderen eten'],
    'kids': ['kinderen', 'kindermenu', 'kinderkaart', 'voor de kids'],
    'dranken': ['drinken', 'drankje', 'drinks', 'drankenkaart', 'bier', 'wijn', 'cocktail'],
    'bier': ['biertje', 'pils', 'pilsje', 'pilsener', 'speciaalbier', 'tapbier', 'fust'],
    'wijn': ['wijntje', 'rode wijn', 'witte wijn', 'rose', 'prosecco', 'champagne'],
    'cocktail': ['cocktails', 'mix', 'mixdrink', 'mojito', 'martini', 'spritz'],
    'eten': ['hapjes', 'bites', 'snacks', 'gerecht', 'maaltijd'],
    'allergie': ['allergieen', 'allergisch', 'glutenvrij', 'lactosevrij', 'vegan', 'vegetarisch', 'intolerantie'],
}

# Synonym expansions for excerpt extraction (bidirectional)
EXCERPT_SYNONYMS = {
    'bier': ['pils', 'tapbier', 'speciaalbier', 'biertje', 'biertjes'],
    'wijn': ['rood', 'wit', 'rose', 'wijntje', 'huiswijn'],
    'drank': ['drankjes', 'drinken', 'borrel'],
    'eten': ['gerechten', 'menu', 'kaart', 'menukaart'],
    'prijs': ['kost', 'euro', 'prijzen', 'tarief'],
    'kost': ['prijs', 'euro', 'prijzen', 'tarief'],
    'kinderen': ['kindermenu', 'kinderkaart', 'kids', 'kinder', 'kleintjes', 'kindermenus'],
    'kindermenu': ['kinderen', 'kinderkaart', 'kids', 'kinder', 'kleintjes'],
    'kids': ['kinderen', 'kindermenu', 'kinderkaart', 'kinder'],
    'kinder': ['kinderen', 'kindermenu', 'kinderkaart', 'kids', 'kleintjes'],
    'lunch': ['lunchkaart', 'lunchgerecht', 'middageten'],
    'ontbijt': ['breakfast', 'ochtend'],
    'diner': ['avondeten', 'dineren', 'dinerkaart'],
    'borrel': ['borrelhapjes', 'borrelkaart', 'hapjes'],
    'menu': ['menukaart', 'kaart', 'gerechten'],
}


# ============================================================================
# QUERY EXPANSIONS - Common misspellings and variations
# ============================================================================

QUERY_EXPANSIONS = {
    'reserveren': ['boeken', 'reservering', 'boeking'],
    'prijs': ['kosten', 'tarief', 'euro', 'betalen'],
    'menu': ['kaart', 'menukaart', 'eten', 'drinken'],
    'open': ['openingstijd', 'openingstijden', 'geopend'],
    'kind': ['kinderen', 'kids', 'peuter'],
}


# ============================================================================
# SIGNAL DETECTION KEYWORDS - For query analysis
# ============================================================================

# Kids/children related queries
KIDS_QUERY_KEYWORDS = {'kind', 'kinderen', 'kids', 'kleintjes', 'peuter', 'peuters', 'kleuter',
                       'kleuters', 'baby', 'babies', 'tiener', 'tieners', 'jeugd', 'jong',
                       'gezin', 'familie', 'ouders', 'kindermenu', 'kinderkaart'}

KIDS_CONTENT_KEYWORDS = {'kind', 'kinderen', 'kids', 'kleintjes', 'peuter', 'kleuter', 'baby',
                         'minimumleeftijd', 'leeftijd', 'jaar oud', 'vanaf jaar', 'toegestaan vanaf'}

# Business/corporate related queries
BEDRIJF_QUERY_KEYWORDS = {'bedrijf', 'zakelijk', 'zakelijke', 'bedrijven', 'teambuilding',
                          'team', 'teams', 'teamuitje', 'bedrijfsuitje', 'personeelsuitje',
                          'vergadering', 'meeting', 'conferentie', 'corporate', 'b2b',
                          'kantoor', 'collega', 'collegas', 'werk', 'afdeling', 'organisatie',
                          'evenement', 'event', 'groep', 'groepen', 'gezelschap'}

BEDRIJF_CONTENT_KEYWORDS = {'bedrijf', 'zakelijk', 'bedrijven', 'teambuilding', 'team',
                            'teamuitje', 'bedrijfsuitje', 'corporate', 'b2b', 'vergadering',
                            'evenement', 'groepen', 'groepsarrangement', 'offerte'}

# Pricing related queries
PRICING_QUERY_KEYWORDS = {'prijs', 'prijzen', 'kosten', 'kost', 'tarief', 'tarieven', 'euro',
                          'geld', 'betalen', 'goedkoop', 'duur', 'budget', 'inclusief',
                          'inbegrepen', 'extra', 'toeslag', 'korting', 'aanbieding',
                          'actie', 'deal', 'gratis', 'pp', 'per persoon'}

PRICING_CONTENT_KEYWORDS = {'€', 'euro', 'prijs', 'tarief', 'kost', 'per persoon', 'p.p.',
                            'inclusief', 'inbegrepen', 'vanaf', 'korting'}


# ============================================================================
# DRINK-SPECIFIC KEYWORDS - For boosting drink sections
# ============================================================================

# Drink query detection - which words in user queries indicate drink questions
DRINK_KEYWORDS = {
    'bier': ['bier', 'biertje', 'biertjes', 'pils', 'pilsje', 'speciaal', 'speciaalbier', 'tap', 'tapbier', 'fust', 'ipa', 'witbier', 'blond', 'tripel', 'dubbel'],
    'wijn': ['wijn', 'wijntje', 'wijnen', 'rood', 'rode', 'wit', 'witte', 'rose', 'rosé', 'prosecco', 'champagne', 'cava', 'bubbels', 'glas wijn'],
    'cocktail': ['cocktail', 'cocktails', 'mix', 'mixdrank', 'mojito', 'martini', 'spritz', 'aperol', 'gin tonic', 'gin-tonic', 'margarita', 'cosmopolitan', 'long drink'],
    'frisdrank': ['frisdrank', 'fris', 'cola', 'sinas', 'spa', 'water', 'mineraalwater', 'ice tea', 'icetea', 'tonic', 'bitter lemon', 'cassis', 'appelsap', 'jus', 'juice'],
    'koffie': ['koffie', 'espresso', 'cappuccino', 'latte', 'americano', 'flat white', 'koffiemenu'],
    'thee': ['thee', 'tea', 'theemenu', 'earl grey', 'groene thee', 'muntthee'],
    'alcohol': ['alcohol', 'drank', 'drankje', 'dranken', 'alcoholvrij', 'sterke drank', 'shot', 'shots', 'borrel', 'borrelen'],
}

# All drink keywords flattened for quick lookup
ALL_DRINK_KEYWORDS = set()
for keywords in DRINK_KEYWORDS.values():
    ALL_DRINK_KEYWORDS.update(keywords)

# Content patterns that indicate a drink section
DRINK_CONTENT_PATTERNS = ['bier', 'wijn', 'cocktail', 'drankkaart', 'dranken', 'menu', 'tap', 'fles', 'glas', '€']


# ============================================================================
# ALLERGY/DIET KEYWORDS - For boosting allergy-related sections
# ============================================================================

# Allergy query detection
ALLERGY_QUERY_KEYWORDS = {
    'allergie', 'allergieen', 'allergieën', 'allergisch', 'intolerantie', 'intoleranties',
    'glutenvrij', 'gluten', 'lactosevrij', 'lactose', 'melkvrij', 'zuivelvrij',
    'notenvrij', 'noten', 'pinda', 'pindas', 'pindavrij',
    'vegan', 'veganistisch', 'vegetarisch', 'plantaardig',
    'halal', 'kosher', 'koosjer',
    'voedingsallergie', 'voedselallergie', 'dieet', 'dieetwensen',
    'ei-vrij', 'eivrij', 'eieren', 'schaaldieren', 'schelpdieren', 'vis',
    'soja', 'sojavrij', 'sesamvrij', 'sesam', 'mosterd',
    'kan eten', 'mag eten', 'verdragen', 'niet tegen',
}

# Content patterns that indicate allergy/diet info
ALLERGY_CONTENT_KEYWORDS = {
    'allergie', 'allergenen', 'allergisch', 'intolerantie',
    'glutenvrij', 'lactosevrij', 'melkvrij', 'zuivelvrij', 'notenvrij',
    'vegan', 'veganistisch', 'vegetarisch', 'plantaardig',
    'halal', 'kosher', 'dieet', 'dieetwensen',
    'kan aangepast', 'op verzoek', 'personeel vragen', 'keuken informeren',
    'ingredienten', 'ingrediënten', 'bevat', 'zonder',
}


# ============================================================================
# RESERVATION SIGNAL KEYWORDS
# ============================================================================

RESERVATION_QUERY_KEYWORDS = {'reserveren', 'reservering', 'boeken', 'boeking', 'afspraak',
                              'reservatie', 'vastleggen', 'inplannen', 'beschikbaar',
                              'beschikbaarheid', 'tafel', 'plek', 'plaats'}


# ============================================================================
# OPENING HOURS KEYWORDS
# ============================================================================

OPENING_HOURS_KEYWORDS = {'open', 'dicht', 'gesloten', 'openingstijd', 'openingstijden',
                          'sluitingstijd', 'openingsuren', 'wanneer open', 'hoe laat',
                          'maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag',
                          'zaterdag', 'zondag', 'weekend', 'doordeweeks', 'feestdag'}


# ============================================================================
# LOCATION KEYWORDS
# ============================================================================

LOCATION_KEYWORDS = {'adres', 'locatie', 'waar', 'route', 'bereikbaar', 'bereikbaarheid',
                     'parkeren', 'parkeerplaats', 'ov', 'openbaar vervoer', 'bus', 'tram',
                     'trein', 'metro', 'fiets', 'auto', 'navigatie', 'straat', 'stad',
                     'postcode', 'plaats', 'gemeente'}


# ============================================================================
# BACKWARD COMPATIBILITY - Aliases for old constant names
# ============================================================================

# For backward compatibility with code that uses the old names
KIDS_KEYWORDS = KIDS_QUERY_KEYWORDS
BEDRIJF_KEYWORDS = BEDRIJF_QUERY_KEYWORDS
PRICING_KEYWORDS = PRICING_QUERY_KEYWORDS


# ============================================================================
# ARRANGEMENT KEYWORDS
# ============================================================================

ARRANGEMENT_KEYWORDS = {
    'arrangement', 'arrangementen', 'pakket', 'pakketten', 'deal', 'deals',
    'aanbieding', 'aanbiedingen', 'groepsarrangement', 'feest', 'feestje',
    'verjaardag', 'vrijgezellenfeest', 'bedrijfsuitje', 'teamuitje',
}


# ============================================================================
# GENERAL KEYWORDS
# ============================================================================

GENERAL_KEYWORDS = {
    'wat', 'hoe', 'waarom', 'wanneer', 'wie', 'welke', 'kunnen', 'mogen',
    'mag', 'kan', 'moet', 'willen', 'graag', 'informatie', 'info', 'vraag',
    'vragen', 'weten', 'vertellen', 'uitleggen',
}


# ============================================================================
# MENU KEYWORDS
# ============================================================================

MENU_KEYWORDS = {
    'menu', 'menukaart', 'kaart', 'eten', 'drinken', 'gerechten', 'hapjes',
    'snacks', 'bites', 'lunch', 'diner', 'ontbijt', 'brunch', 'borrel',
    'borrelhapjes', 'voorgerecht', 'hoofdgerecht', 'nagerecht', 'dessert',
}


# ============================================================================
# DAY/DATE CONSTANTS
# ============================================================================

DAY_NAMES_EN_TO_NL = {
    'monday': 'maandag',
    'tuesday': 'dinsdag',
    'wednesday': 'woensdag',
    'thursday': 'donderdag',
    'friday': 'vrijdag',
    'saturday': 'zaterdag',
    'sunday': 'zondag',
}

DAYS_ORDER = ['maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag']


# ============================================================================
# IMPORTANT SEARCH TERMS - For relevance boosting
# ============================================================================

IMPORTANT_SEARCH_TERMS = {
    'prijs', 'kosten', 'tarief', 'euro', 'reserveren', 'boeken', 'open',
    'gesloten', 'adres', 'locatie', 'parkeren', 'kinderen', 'kind', 'kids',
    'menu', 'eten', 'drinken', 'allergie', 'vegan', 'vegetarisch',
    'bedrijf', 'zakelijk', 'groep', 'groepen', 'arrangement',
}
