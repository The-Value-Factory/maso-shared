"""
Tests for LLMContextBuilder
"""

import pytest
from maso_shared.kb import LLMContextBuilder, KBSearchEngine


@pytest.fixture
def context_builder():
    return LLMContextBuilder()


@pytest.fixture
def search_engine():
    return KBSearchEngine()


@pytest.fixture
def sample_kb_content():
    return {
        'faqs': [
            {
                'question': 'Wat zijn de openingstijden?',
                'answer': 'We zijn open van 10:00 tot 22:00.',
                'category': 'algemeen'
            },
        ],
        'arrangements': [
            {
                'name': 'Kids Party',
                'description': 'Leuk kinderfeestje',
                'price': ['€25,00 p.p.'],
                'duration': '2 uur',
                'is_favorite': True
            },
            {
                'name': 'Bedrijfsuitje',
                'description': 'Teambuilding activiteit',
                'price': ['€55,00 p.p.'],
                'duration': '4 uur',
                'is_favorite': True
            },
            {
                'name': 'Race Experience',
                'description': 'Simracen voor beginners',
                'price': ['€35,00 p.p.'],
                'duration': '1 uur',
                'is_favorite': False
            },
        ],
        'content_sections': [],
        'business_info': {
            'name': 'Test Entertainment',
            'description': 'Het leukste uitgaanscentrum van Nederland',
            'opening_hours': {
                'monday': '10:00 - 22:00',
                'tuesday': '10:00 - 22:00',
                'wednesday': '10:00 - 22:00',
                'thursday': '10:00 - 22:00',
                'friday': '10:00 - 23:00',
                'saturday': '10:00 - 23:00',
                'sunday': 'Gesloten'
            }
        }
    }


class TestBuildContext:
    def test_builds_context_for_general_query(self, context_builder, sample_kb_content):
        signals = {'general': True, 'opening_hours': False, 'arrangement': False}
        
        context = context_builder.build_context(sample_kb_content, [], signals)
        
        assert 'Test Entertainment' in context
    
    def test_includes_opening_hours_for_opening_query(self, context_builder, sample_kb_content):
        signals = {'general': False, 'opening_hours': True, 'arrangement': False}
        
        context = context_builder.build_context(sample_kb_content, [], signals)
        
        assert 'OPENINGSTIJDEN' in context
        assert 'Maandag' in context
    
    def test_includes_arrangements_for_arrangement_query(self, context_builder, sample_kb_content):
        signals = {'general': False, 'opening_hours': False, 'arrangement': True}
        
        context = context_builder.build_context(sample_kb_content, [], signals)
        
        assert 'Kids Party' in context
        assert 'Bedrijfsuitje' in context


class TestOrganisationModule:
    def test_includes_business_name(self, context_builder, sample_kb_content):
        module = context_builder.build_organisation_module(sample_kb_content)
        
        assert 'Test Entertainment' in module
    
    def test_includes_description(self, context_builder, sample_kb_content):
        module = context_builder.build_organisation_module(sample_kb_content)
        
        assert 'leukste uitgaanscentrum' in module
    
    def test_includes_opening_hours(self, context_builder, sample_kb_content):
        module = context_builder.build_organisation_module(sample_kb_content)
        
        assert 'Maandag' in module
        assert '10:00 - 22:00' in module
    
    def test_days_in_correct_order(self, context_builder, sample_kb_content):
        module = context_builder.build_organisation_module(sample_kb_content)
        
        # Maandag should come before Dinsdag
        maandag_pos = module.find('Maandag')
        dinsdag_pos = module.find('Dinsdag')
        
        assert maandag_pos < dinsdag_pos


class TestArrangementsModule:
    def test_shows_all_arrangements(self, context_builder, sample_kb_content):
        module = context_builder.build_arrangements_module(sample_kb_content)
        
        assert 'Kids Party' in module
        assert 'Bedrijfsuitje' in module
        assert 'Race Experience' in module
    
    def test_includes_prices(self, context_builder, sample_kb_content):
        module = context_builder.build_arrangements_module(sample_kb_content)
        
        assert '€25,00' in module
    
    def test_deduplicates_arrangements(self, context_builder):
        kb_with_dupes = {
            'arrangements': [
                {'name': 'Kids Party', 'price': ['€25,00']},
                {'name': 'kids party', 'price': ['€25,00']},  # Duplicate (different case)
                {'name': 'Kids Party', 'price': ['€30,00']},  # Duplicate
            ]
        }
        
        module = context_builder.build_arrangements_module(kb_with_dupes)
        
        # Should only appear once
        assert module.count('Kids Party') == 1 or module.count('kids party') == 1


class TestFavoriteArrangementsModule:
    def test_shows_only_favorites(self, context_builder, sample_kb_content):
        module = context_builder.build_favorite_arrangements_module(sample_kb_content)
        
        assert 'Kids Party' in module
        assert 'Bedrijfsuitje' in module
        assert 'Race Experience' not in module  # Not a favorite
    
    def test_returns_empty_if_no_favorites(self, context_builder):
        kb_no_favorites = {
            'arrangements': [
                {'name': 'Test', 'price': ['€10,00'], 'is_favorite': False}
            ]
        }
        
        module = context_builder.build_favorite_arrangements_module(kb_no_favorites)
        
        assert module == ""


class TestFaqsModule:
    def test_formats_faqs_from_search_results(self, context_builder):
        search_results = [
            {
                'is_faq': True,
                'title': 'FAQ: Test vraag?',
                'content': 'VRAAG: Test vraag?\n\nANTWOORD: Test antwoord.'
            }
        ]
        
        module = context_builder.build_faqs_module(search_results)
        
        assert 'Test vraag' in module
        assert 'Test antwoord' in module
    
    def test_limits_to_5_faqs(self, context_builder):
        search_results = [
            {'is_faq': True, 'title': f'FAQ: Vraag {i}?', 'content': f'Antwoord {i}'}
            for i in range(10)
        ]
        
        module = context_builder.build_faqs_module(search_results)
        
        # Should only have 5 FAQs
        assert module.count('Vraag') == 5


class TestContextLength:
    def test_respects_max_length(self, context_builder):
        # Create KB with lots of content
        large_kb = {
            'arrangements': [
                {'name': f'Arrangement {i}', 'description': 'A' * 500, 'price': ['€10,00']}
                for i in range(50)
            ],
            'business_info': {'name': 'Test', 'description': 'B' * 1000}
        }
        
        signals = {'arrangement': True}
        context = context_builder.build_context(large_kb, [], signals, max_length=2000)
        
        assert len(context) <= 2100  # Allow small buffer for truncation
