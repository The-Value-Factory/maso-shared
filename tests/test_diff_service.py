"""
Tests for KBDiffService
"""

import pytest
from maso_shared.kb import KBDiffService


@pytest.fixture
def diff_service():
    return KBDiffService()


@pytest.fixture
def sample_current_content():
    return {
        "faqs": [
            {
                "question": "Wat zijn de openingstijden?",
                "answer": "We zijn open van 10:00 tot 22:00",
                "category": "algemeen",
            },
            {"question": "Kan ik reserveren?", "answer": "Ja, via onze website", "category": "reserveren"},
        ],
        "arrangements": [
            {"name": "Kids Party", "price": ["€25,00 p.p."], "duration": "2 uur"},
            {"name": "Bedrijfsuitje", "price": ["€45,00 p.p."], "duration": "3 uur"},
        ],
        "content_sections": [
            {"title": "Home", "url": "https://example.com/", "content": "Welkom bij ons!"},
        ],
        "business_info": {
            "name": "Test Bedrijf",
            "description": "Een leuk uitgaanscentrum",
        },
    }


@pytest.fixture
def sample_scraped_content():
    return {
        "faqs": [
            {
                "question": "Wat zijn de openingstijden?",
                "answer": "We zijn open van 10:00 tot 23:00",
                "category": "algemeen",
            },  # Modified
            {"question": "Kan ik reserveren?", "answer": "Ja, via onze website", "category": "reserveren"},  # Unchanged
            {
                "question": "Waar kan ik parkeren?",
                "answer": "Gratis parkeren voor de deur",
                "category": "locatie",
            },  # Added
        ],
        "arrangements": [
            {"name": "Kids Party", "price": ["€27,50 p.p."], "duration": "2 uur"},  # Modified price
            # Bedrijfsuitje removed
            {"name": "VIP Arrangement", "price": ["€75,00 p.p."], "duration": "4 uur"},  # Added
        ],
        "content_sections": [
            {"title": "Home", "url": "https://example.com/", "content": "Welkom bij ons!"},
        ],
        "business_info": {
            "name": "Test Bedrijf",
            "description": "Het leukste uitgaanscentrum van Nederland",  # Modified
        },
    }


class TestGenerateChanges:
    def test_detects_faq_modification(self, diff_service, sample_current_content, sample_scraped_content):
        result = diff_service.generate_changes(sample_current_content, sample_scraped_content)

        faq_changes = [c for c in result["changes"] if c["type"] == "faq"]
        modified_faqs = [c for c in faq_changes if c["action"] == "MODIFIED"]

        assert len(modified_faqs) == 1
        assert "openingstijden" in modified_faqs[0]["data"]["question"].lower()

    def test_detects_faq_addition(self, diff_service, sample_current_content, sample_scraped_content):
        result = diff_service.generate_changes(sample_current_content, sample_scraped_content)

        faq_changes = [c for c in result["changes"] if c["type"] == "faq"]
        added_faqs = [c for c in faq_changes if c["action"] == "ADDED"]

        assert len(added_faqs) == 1
        assert "parkeren" in added_faqs[0]["data"]["question"].lower()

    def test_detects_arrangement_modification(self, diff_service, sample_current_content, sample_scraped_content):
        result = diff_service.generate_changes(sample_current_content, sample_scraped_content)

        arr_changes = [c for c in result["changes"] if c["type"] == "arrangement"]
        modified_arr = [c for c in arr_changes if c["action"] == "MODIFIED"]

        assert len(modified_arr) == 1
        assert "Kids Party" in modified_arr[0]["data"]["name"]

    def test_detects_arrangement_removal(self, diff_service, sample_current_content, sample_scraped_content):
        result = diff_service.generate_changes(sample_current_content, sample_scraped_content)

        arr_changes = [c for c in result["changes"] if c["type"] == "arrangement"]
        removed_arr = [c for c in arr_changes if c["action"] == "REMOVED"]

        assert len(removed_arr) == 1
        assert "Bedrijfsuitje" in removed_arr[0]["data"]["name"]

    def test_detects_arrangement_addition(self, diff_service, sample_current_content, sample_scraped_content):
        result = diff_service.generate_changes(sample_current_content, sample_scraped_content)

        arr_changes = [c for c in result["changes"] if c["type"] == "arrangement"]
        added_arr = [c for c in arr_changes if c["action"] == "ADDED"]

        assert len(added_arr) == 1
        assert "VIP" in added_arr[0]["data"]["name"]

    def test_detects_business_info_modification(self, diff_service, sample_current_content, sample_scraped_content):
        result = diff_service.generate_changes(sample_current_content, sample_scraped_content)

        biz_changes = [c for c in result["changes"] if c["type"] == "business_info"]

        assert len(biz_changes) == 1
        assert biz_changes[0]["field"] == "description"

    def test_summary_counts_correct(self, diff_service, sample_current_content, sample_scraped_content):
        result = diff_service.generate_changes(sample_current_content, sample_scraped_content)

        summary = result["summary"]

        assert summary["by_action"]["ADDED"] == 2  # 1 FAQ + 1 arrangement
        assert summary["by_action"]["MODIFIED"] == 3  # 1 FAQ + 1 arrangement + 1 business_info
        assert summary["by_action"]["REMOVED"] == 1  # 1 arrangement

    def test_fingerprint_match_returns_no_changes(self, diff_service):
        content = {"_metadata": {"content_fingerprint": "abc123"}, "faqs": [{"question": "Test?", "answer": "Yes"}]}

        result = diff_service.generate_changes(content, content)

        assert result["summary"]["total"] == 0
        assert result["summary"].get("fingerprint_match") == True


class TestApplyChanges:
    def test_apply_faq_addition(self, diff_service, sample_current_content, sample_scraped_content):
        result = diff_service.generate_changes(sample_current_content, sample_scraped_content)

        # Find the added FAQ change
        added_faq = next(c for c in result["changes"] if c["type"] == "faq" and c["action"] == "ADDED")

        # Apply just this change
        new_content = diff_service.apply_changes(sample_current_content, [added_faq["change_id"]], result["changes"])

        assert len(new_content["faqs"]) == 3
        assert any("parkeren" in faq["question"].lower() for faq in new_content["faqs"])

    def test_apply_arrangement_removal(self, diff_service, sample_current_content, sample_scraped_content):
        result = diff_service.generate_changes(sample_current_content, sample_scraped_content)

        # Find the removed arrangement change
        removed_arr = next(c for c in result["changes"] if c["type"] == "arrangement" and c["action"] == "REMOVED")

        # Apply just this change
        new_content = diff_service.apply_changes(sample_current_content, [removed_arr["change_id"]], result["changes"])

        assert len(new_content["arrangements"]) == 1
        assert not any("Bedrijfsuitje" in arr["name"] for arr in new_content["arrangements"])


class TestChangeIdGeneration:
    def test_change_ids_are_deterministic(self, diff_service, sample_current_content, sample_scraped_content):
        result1 = diff_service.generate_changes(sample_current_content, sample_scraped_content)
        result2 = diff_service.generate_changes(sample_current_content, sample_scraped_content)

        ids1 = sorted([c["change_id"] for c in result1["changes"]])
        ids2 = sorted([c["change_id"] for c in result2["changes"]])

        assert ids1 == ids2

    def test_change_ids_are_unique(self, diff_service, sample_current_content, sample_scraped_content):
        result = diff_service.generate_changes(sample_current_content, sample_scraped_content)

        ids = [c["change_id"] for c in result["changes"]]

        assert len(ids) == len(set(ids))  # All unique


class TestApplyIndexStability:
    """Regression tests: apply_changes must hit the item the diff pointed at."""

    def test_section_index_survives_pdf_sections_in_list(self, diff_service):
        # A PDF section sits *before* the page sections. The diff skips PDFs,
        # so without remapping index 0 would point at the PDF, not at /over-ons.
        current = {
            "content_sections": [
                {"title": "PDF: menu.pdf", "url": "https://x.nl/menu.pdf", "content": "menu", "type": "pdf"},
                {"title": "Over ons", "url": "https://x.nl/over-ons", "content": "oud", "type": "page"},
                {"title": "Contact", "url": "https://x.nl/contact", "content": "bel ons", "type": "page"},
            ],
        }
        scraped = {
            "content_sections": [
                {"title": "PDF: menu.pdf", "url": "https://x.nl/menu.pdf", "content": "menu", "type": "pdf"},
                {"title": "Over ons", "url": "https://x.nl/over-ons", "content": "nieuw", "type": "page"},
            ],
        }
        result = diff_service.generate_changes(current, scraped)
        section_changes = [c for c in result["changes"] if c["type"] == "section"]
        modified = next(c for c in section_changes if c["action"] == "MODIFIED")
        removed = next(c for c in section_changes if c["action"] == "REMOVED")
        assert modified["current_index"] == 1
        assert removed["current_index"] == 2

        new_content = diff_service.apply_changes(current, [modified["change_id"]], result["changes"])
        assert new_content["content_sections"][0]["type"] == "pdf"
        assert new_content["content_sections"][1]["content"] == "nieuw"
        assert len(new_content["content_sections"]) == 3

        new_content = diff_service.apply_changes(current, [removed["change_id"]], result["changes"])
        assert [s["url"] for s in new_content["content_sections"]] == [
            "https://x.nl/menu.pdf",
            "https://x.nl/over-ons",
        ]

    def test_multiple_removals_do_not_shift(self, diff_service):
        current = {
            "faqs": [
                {"question": "A?", "answer": "a"},
                {"question": "B?", "answer": "b"},
                {"question": "C?", "answer": "c"},
                {"question": "D?", "answer": "d"},
            ],
        }
        scraped = {"faqs": [{"question": "D?", "answer": "d"}]}
        result = diff_service.generate_changes(current, scraped)
        removed = [c for c in result["changes"] if c["type"] == "faq" and c["action"] == "REMOVED"]
        assert len(removed) == 3

        # Pass the ids in ascending index order, the worst case for pop()
        ids = [c["change_id"] for c in sorted(removed, key=lambda c: c["current_index"])]
        new_content = diff_service.apply_changes(current, ids, result["changes"])
        assert [f["question"] for f in new_content["faqs"]] == ["D?"]
