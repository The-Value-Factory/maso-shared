"""
Shared type definitions for Knowledge Base data structures

These TypedDicts define the expected structure of KB data,
ensuring consistency between Voice AI and Main App.
"""

from typing import TypedDict, List, Optional, Dict, Any


class FAQItem(TypedDict, total=False):
    """A single FAQ entry in the knowledge base"""
    question: str
    answer: str
    category: Optional[str]
    source_url: Optional[str]
    sms_template: Optional[str]


class ArrangementItem(TypedDict, total=False):
    """A single arrangement/package in the knowledge base"""
    name: str
    description: Optional[str]
    price: List[str]  # Can have multiple price points
    duration: Optional[str]
    category: Optional[str]
    source_url: Optional[str]
    age_restriction: Optional[str]
    group_size: Optional[str]
    activities: Optional[List[str]]
    is_favorite: Optional[bool]


class ContentSection(TypedDict, total=False):
    """A content section scraped from a webpage"""
    title: str
    content: str
    url: str
    type: Optional[str]  # e.g., 'pdf', 'page'
    metadata: Optional[Dict[str, Any]]


class PDFDocument(TypedDict, total=False):
    """A PDF document in the knowledge base"""
    filename: str
    url: str
    content: str  # Extracted text content
    page_count: Optional[int]


class OpeningHours(TypedDict, total=False):
    """Opening hours for each day of the week"""
    monday: Optional[str]
    tuesday: Optional[str]
    wednesday: Optional[str]
    thursday: Optional[str]
    friday: Optional[str]
    saturday: Optional[str]
    sunday: Optional[str]


class BusinessInfo(TypedDict, total=False):
    """Business information from the knowledge base"""
    name: str
    url: Optional[str]
    type: Optional[str]
    description: Optional[str]
    opening_hours: Optional[OpeningHours]
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]


class KBMetadata(TypedDict, total=False):
    """Metadata about the knowledge base content"""
    content_fingerprint: Optional[str]
    scraped_at: Optional[str]
    source_url: Optional[str]


class KBContent(TypedDict, total=False):
    """
    The complete knowledge base content structure
    
    This is what gets stored in the `content` JSONB field of the knowledge_bases table.
    """
    faqs: List[FAQItem]
    content_sections: List[ContentSection]
    arrangements: List[ArrangementItem]
    business_info: BusinessInfo
    pdf_documents: Optional[List[PDFDocument]]
    searchable_content: Optional[Dict[str, List[int]]]  # Term -> section indices
    _metadata: Optional[KBMetadata]


# ============================================================================
# Search & Context Types
# ============================================================================

class SearchResult(TypedDict, total=False):
    """A single search result"""
    type: str  # 'faq', 'section', 'arrangement'
    title: str
    content: str
    url: Optional[str]
    score: float
    is_faq: Optional[bool]
    is_arrangement: Optional[bool]
    question: Optional[str]  # For FAQs
    answer: Optional[str]    # For FAQs
    metadata: Optional[Dict[str, Any]]
    search_query: Optional[str]


class QuerySignals(TypedDict, total=False):
    """Detected signals from user query analysis"""
    kids: bool
    bedrijf: bool
    pricing: bool
    activity: bool
    arrangement: bool
    general: bool
    location: bool
    opening_hours: bool


# ============================================================================
# Diff Types
# ============================================================================

class FieldModification(TypedDict, total=False):
    """A single field modification in a diff"""
    field: str
    old_value: Any
    new_value: Any
    diff_html: Optional[str]


class DiffChange(TypedDict, total=False):
    """A single change detected by the diff service"""
    change_id: str
    type: str  # 'faq', 'section', 'arrangement', 'business_info', 'document'
    action: str  # 'ADDED', 'MODIFIED', 'REMOVED'
    current_index: Optional[int]
    data: Dict[str, Any]
    modifications: Optional[List[FieldModification]]
    field: Optional[str]  # For business_info changes
    old_value: Optional[Any]
    new_value: Optional[Any]


class DiffSummaryByType(TypedDict):
    """Summary counts for a single content type"""
    ADDED: int
    MODIFIED: int
    REMOVED: int


class DiffSummary(TypedDict, total=False):
    """Summary of all changes in a diff"""
    total: int
    by_type: Dict[str, DiffSummaryByType]
    by_action: DiffSummaryByType
    fingerprint_match: Optional[bool]


class DiffResult(TypedDict):
    """Complete result from generate_changes()"""
    summary: DiffSummary
    changes: List[DiffChange]
