"""
Tests for KBSearchEngine
"""

import pytest
from maso_shared.kb import KBSearchEngine


@pytest.fixture
def search_engine():
    return KBSearchEngine()


@pytest.fixture
def sample_kb_content():
    return {
        'faqs': [
            {
                'question': 'Wat zijn de openingstijden?',
                'answer': 'We zijn open van 10:00 tot 22:00 op doordeweekse dagen.',
                'category': 'algemeen'
            },
            {
                'question': 'Vanaf welke leeftijd mag je simracen?',
                'answer': 'Je moet minimaal 1,40 meter lang zijn en 6 jaar oud.',
                'category': 'simracen'
            },
            {
                'question': 'Kan ik een kinderfeestje organiseren?',
                'answer': 'Ja! We hebben speciale kids party arrangementen.',
                'category': 'kids'
            },
        ],
        'arrangements': [
            {
                'name': 'Kids Party Basic',
                'description': 'Leuk kinderfeestje met 1 activiteit',
                'price': ['€25,00 p.p.'],
                'duration': '2 uur',
                'category': 'kids',
                'is_favorite': True
            },
            {
                'name': 'Bedrijfsuitje Compleet',
                'description': 'Teambuilding met meerdere activiteiten',
                'price': ['€55,00 p.p.'],
                'duration': '4 uur',
                'category': 'bedrijf',
                'is_favorite': True
            },
            {
                'name': 'Race Experience',
                'description': '30 minuten racen op echte F1 circuits',
                'price': ['€35,00 p.p.'],
                'duration': '1 uur',
                'category': 'simracen'
            },
        ],
        'content_sections': [
            {
                'title': 'Home',
                'url': 'https://example.com/',
                'content': 'Welkom bij ons entertainmentcentrum! Wij bieden simracen, jeu de boules en meer.'
            },
            {
                'title': 'Arrangementen',
                'url': 'https://example.com/arrangementen',
                'content': 'Bekijk onze arrangementen voor kids, bedrijven en meer.'
            },
        ],
        'business_info': {
            'name': 'Test Entertainment',
            'description': 'Het leukste uitgaanscentrum',
            'opening_hours': {
                'monday': '10:00 - 22:00',
                'tuesday': '10:00 - 22:00',
                'saturday': '10:00 - 23:00',
                'sunday': 'Gesloten'
            }
        }
    }


class TestSearch:
    def test_search_returns_results(self, search_engine, sample_kb_content):
        results = search_engine.search(sample_kb_content, "openingstijden")
        
        assert len(results) > 0
    
    def test_faq_ranked_high_for_exact_match(self, search_engine, sample_kb_content):
        results = search_engine.search(sample_kb_content, "openingstijden")
        
        # FAQ about openingstijden should be in top results
        top_result = results[0]
        assert top_result.get('is_faq') or 'openingstijd' in top_result.get('title', '').lower()
    
    def test_arrangement_query_boosts_arrangements(self, search_engine, sample_kb_content):
        results = search_engine.search(sample_kb_content, "welke arrangementen hebben jullie?")
        
        # Should have arrangement results
        arrangement_results = [r for r in results if r.get('is_arrangement')]
        assert len(arrangement_results) > 0
    
    def test_kids_query_boosts_kids_content(self, search_engine, sample_kb_content):
        results = search_engine.search(sample_kb_content, "kinderfeestje")
        
        # Should find kids-related content
        found_kids = False
        for r in results:
            content = (r.get('title', '') + r.get('content', '')).lower()
            if 'kids' in content or 'kinder' in content:
                found_kids = True
                break
        
        assert found_kids
    
    def test_simracen_query_finds_racing_content(self, search_engine, sample_kb_content):
        results = search_engine.search(sample_kb_content, "simracen leeftijd")
        
        # Should find FAQ about simracen leeftijd
        found_simracen = False
        for r in results:
            if r.get('is_faq') and 'simracen' in r.get('title', '').lower():
                found_simracen = True
                break
        
        assert found_simracen
    
    def test_max_sections_limits_results(self, search_engine, sample_kb_content):
        results = search_engine.search(sample_kb_content, "test", max_sections=2)
        
        assert len(results) <= 2


class TestQuerySignals:
    def test_detects_kids_signal(self, search_engine):
        signals = search_engine.analyze_query_signals("kinderfeestje prijzen")
        
        assert signals['kids'] == True
        assert signals['pricing'] == True
    
    def test_detects_bedrijf_signal(self, search_engine):
        signals = search_engine.analyze_query_signals("bedrijfsuitje teambuilding")
        
        assert signals['bedrijf'] == True
    
    def test_detects_arrangement_signal(self, search_engine):
        signals = search_engine.analyze_query_signals("welke arrangementen hebben jullie")
        
        assert signals['arrangement'] == True
    
    def test_detects_opening_hours_signal(self, search_engine):
        signals = search_engine.analyze_query_signals("wanneer zijn jullie open")
        
        assert signals['opening_hours'] == True
    
    def test_detects_multiple_signals(self, search_engine):
        signals = search_engine.analyze_query_signals("wat kost een kinderfeestje arrangement")
        
        assert signals['kids'] == True
        assert signals['pricing'] == True
        assert signals['arrangement'] == True


class TestQueryExpansion:
    def test_expands_synonyms(self, search_engine):
        expanded = search_engine._expand_query("wat is de prijs")
        
        # Should include synonyms for 'prijs'
        assert 'kosten' in expanded or 'tarief' in expanded
    
    def test_expands_query_patterns(self, search_engine):
        expanded = search_engine._expand_query("hoeveel simulators")
        
        # Should expand with related terms
        assert 'personen' in expanded or 'racen' in expanded


class TestExcerptExtraction:
    def test_extracts_relevant_excerpt(self, search_engine):
        content = "Dit is wat voorafgaande tekst. De openingstijden zijn van 10:00 tot 22:00. Dit is wat tekst erna."
        
        excerpt = search_engine.extract_relevant_excerpt(content, "openingstijden", context_chars=100)
        
        assert "openingstijden" in excerpt.lower()
    
    def test_adds_ellipsis_when_truncated(self, search_engine):
        content = "A" * 1000
        
        excerpt = search_engine.extract_relevant_excerpt(content, "test", context_chars=100)
        
        assert "..." in excerpt
