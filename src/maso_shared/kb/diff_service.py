"""
Knowledge Base Diff Service

Compares current content with scraped content and generates structured changes.
This is a stateless service - no database dependencies.

Used by both Voice AI and Main App for:
- Detecting changes between current and newly scraped KB content
- Generating structured diff reports for review UI
- Applying selected changes to KB content
"""

import difflib
import hashlib
import json
import logging
from typing import Dict, Any, List, Tuple, Optional, Set

from .types import KBContent, DiffChange, DiffSummary, DiffResult

logger = logging.getLogger(__name__)


class KBDiffService:
    """Service for generating diffs between current and scraped knowledge base content"""
    
    def __init__(self):
        pass
    
    def generate_changes(
        self, 
        current_content: KBContent, 
        scraped_content: KBContent
    ) -> DiffResult:
        """
        Generate structured diff between current and scraped content
        
        Args:
            current_content: Current KB content from database
            scraped_content: Newly scraped content
            
        Returns:
            DiffResult with summary and list of changes
        """
        # Check content fingerprint first
        current_fingerprint = current_content.get('_metadata', {}).get('content_fingerprint')
        scraped_fingerprint = scraped_content.get('_metadata', {}).get('content_fingerprint')
        
        if current_fingerprint and scraped_fingerprint:
            if current_fingerprint == scraped_fingerprint:
                logger.info("🔒 Content fingerprints match - NO REAL CHANGES DETECTED")
                return {
                    'summary': {
                        'total': 0,
                        'by_type': {},
                        'by_action': {'ADDED': 0, 'MODIFIED': 0, 'REMOVED': 0},
                        'fingerprint_match': True
                    },
                    'changes': []
                }
            else:
                logger.info(f"🔓 Fingerprints differ: {current_fingerprint[:16]}... → {scraped_fingerprint[:16]}...")
        
        changes: List[DiffChange] = []
        
        # Compare FAQs
        faq_changes = self._diff_faqs(
            current_content.get('faqs', []),
            scraped_content.get('faqs', [])
        )
        changes.extend(faq_changes)
        
        # Compare sections (excluding PDFs - those are handled separately)
        current_sections = [s for s in current_content.get('content_sections', []) if s.get('type') != 'pdf']
        scraped_sections = [s for s in scraped_content.get('content_sections', []) if s.get('type') != 'pdf']
        section_changes = self._diff_sections(current_sections, scraped_sections)
        changes.extend(section_changes)
        
        # Compare PDF documents
        pdf_changes = self._diff_documents(
            current_content.get('pdf_documents', []),
            scraped_content.get('pdf_documents', [])
        )
        changes.extend(pdf_changes)
        
        # Compare arrangements
        arrangement_changes = self._diff_arrangements(
            current_content.get('arrangements', []),
            scraped_content.get('arrangements', [])
        )
        changes.extend(arrangement_changes)
        
        # Compare business info
        business_changes = self._diff_business_info(
            current_content.get('business_info', {}),
            scraped_content.get('business_info', {})
        )
        changes.extend(business_changes)
        
        # Generate summary
        summary = self._generate_summary(changes)
        
        logger.info(f"📊 Generated {len(changes)} changes: {summary}")
        
        return {
            'summary': summary,
            'changes': changes
        }
    
    def apply_changes(
        self,
        current_content: KBContent,
        changes_to_apply: List[str],
        all_changes: List[DiffChange]
    ) -> KBContent:
        """
        Apply selected changes to current content
        
        Args:
            current_content: Current KB content
            changes_to_apply: List of change_ids to apply
            all_changes: Full list of changes from generate_changes()
            
        Returns:
            Updated content dict
        """
        # Create change lookup
        change_lookup = {c['change_id']: c for c in all_changes}
        
        # Deep copy current content
        new_content = json.loads(json.dumps(current_content))
        
        # Track indices that need adjustment after removals
        # Process in order: MODIFIED first, then ADDED, then REMOVED (to keep indices stable)
        changes_by_action = {'MODIFIED': [], 'ADDED': [], 'REMOVED': []}
        
        for change_id in changes_to_apply:
            if change_id not in change_lookup:
                logger.warning(f"Change ID not found: {change_id}")
                continue
            change = change_lookup[change_id]
            changes_by_action[change['action']].append(change)
        
        # Apply in safe order
        for action in ['MODIFIED', 'ADDED', 'REMOVED']:
            for change in changes_by_action[action]:
                change_type = change['type']
                
                if change_type == 'faq':
                    self._apply_faq_change(new_content, change, action)
                elif change_type == 'section':
                    self._apply_section_change(new_content, change, action)
                elif change_type == 'document':
                    self._apply_document_change(new_content, change, action)
                elif change_type == 'arrangement':
                    self._apply_arrangement_change(new_content, change, action)
                elif change_type == 'business_info':
                    self._apply_business_info_change(new_content, change, action)
        
        return new_content
    
    # =========================================================================
    # DIFF METHODS
    # =========================================================================
    
    def _diff_faqs(self, current: List[Dict], scraped: List[Dict]) -> List[DiffChange]:
        """Compare FAQ lists and generate changes"""
        changes = []
        
        # Try exact matching first, then similarity
        matched_pairs, added, removed = self._match_items_by_exact_then_similarity(
            current, scraped, 
            key_field='question',
            threshold=0.90
        )
        
        # Check for modifications in matched pairs
        for curr_item, new_item, curr_idx, new_idx in matched_pairs:
            modifications = []
            
            if curr_item.get('question') != new_item.get('question'):
                modifications.append({
                    'field': 'question',
                    'old_value': curr_item.get('question'),
                    'new_value': new_item.get('question')
                })
            
            if curr_item.get('answer') != new_item.get('answer'):
                diff_html = self._generate_text_diff(
                    curr_item.get('answer', ''),
                    new_item.get('answer', '')
                )
                modifications.append({
                    'field': 'answer',
                    'old_value': curr_item.get('answer'),
                    'new_value': new_item.get('answer'),
                    'diff_html': diff_html
                })
            
            if curr_item.get('category') != new_item.get('category'):
                modifications.append({
                    'field': 'category',
                    'old_value': curr_item.get('category'),
                    'new_value': new_item.get('category')
                })
            
            if modifications:
                changes.append({
                    'change_id': self._generate_change_id('faq', 'MODIFIED', new_item),
                    'type': 'faq',
                    'action': 'MODIFIED',
                    'current_index': curr_idx,
                    'data': new_item,
                    'modifications': modifications
                })
        
        # Add new FAQs
        for item, idx in added:
            changes.append({
                'change_id': self._generate_change_id('faq', 'ADDED', item),
                'type': 'faq',
                'action': 'ADDED',
                'data': item
            })
        
        # Removed FAQs
        for item, idx in removed:
            changes.append({
                'change_id': self._generate_change_id('faq', 'REMOVED', item),
                'type': 'faq',
                'action': 'REMOVED',
                'current_index': idx,
                'data': item
            })
        
        return changes
    
    def _diff_sections(self, current: List[Dict], scraped: List[Dict]) -> List[DiffChange]:
        """Compare content sections"""
        changes = []
        
        # Match sections by URL
        matched_pairs, added, removed = self._match_items_by_field(
            current, scraped, 
            key_field='url'
        )
        
        # Check modifications
        for curr_item, new_item, curr_idx, new_idx in matched_pairs:
            modifications = []
            
            if curr_item.get('title') != new_item.get('title'):
                modifications.append({
                    'field': 'title',
                    'old_value': curr_item.get('title'),
                    'new_value': new_item.get('title')
                })
            
            if curr_item.get('content') != new_item.get('content'):
                diff_html = self._generate_text_diff(
                    curr_item.get('content', '')[:500],
                    new_item.get('content', '')[:500]
                )
                modifications.append({
                    'field': 'content',
                    'old_value': curr_item.get('content', '')[:200] + '...',
                    'new_value': new_item.get('content', '')[:200] + '...',
                    'diff_html': diff_html
                })
            
            if modifications:
                changes.append({
                    'change_id': self._generate_change_id('section', 'MODIFIED', new_item),
                    'type': 'section',
                    'action': 'MODIFIED',
                    'current_index': curr_idx,
                    'data': new_item,
                    'modifications': modifications
                })
        
        # Added sections
        for item, idx in added:
            changes.append({
                'change_id': self._generate_change_id('section', 'ADDED', item),
                'type': 'section',
                'action': 'ADDED',
                'data': item
            })
        
        # Removed sections
        for item, idx in removed:
            changes.append({
                'change_id': self._generate_change_id('section', 'REMOVED', item),
                'type': 'section',
                'action': 'REMOVED',
                'current_index': idx,
                'data': item
            })
        
        return changes
    
    def _diff_documents(self, current: List[Dict], scraped: List[Dict]) -> List[DiffChange]:
        """Compare PDF documents"""
        changes = []
        
        if not current and not scraped:
            return changes
        
        # Match documents by URL
        matched_pairs, added, removed = self._match_items_by_field(
            current or [], scraped or [], 
            key_field='url'
        )
        
        # Check modifications
        for curr_item, new_item, curr_idx, new_idx in matched_pairs:
            modifications = []
            
            if curr_item.get('filename') != new_item.get('filename'):
                modifications.append({
                    'field': 'filename',
                    'old_value': curr_item.get('filename'),
                    'new_value': new_item.get('filename')
                })
            
            # Check if content changed (compare first 500 chars)
            curr_content = curr_item.get('content', '')[:500]
            new_content = new_item.get('content', '')[:500]
            if curr_content != new_content:
                modifications.append({
                    'field': 'content',
                    'old_value': curr_content[:200] + '...',
                    'new_value': new_content[:200] + '...'
                })
            
            if modifications:
                changes.append({
                    'change_id': self._generate_change_id('document', 'MODIFIED', new_item),
                    'type': 'document',
                    'action': 'MODIFIED',
                    'current_index': curr_idx,
                    'data': new_item,
                    'modifications': modifications
                })
        
        # Added documents
        for item, idx in added:
            changes.append({
                'change_id': self._generate_change_id('document', 'ADDED', item),
                'type': 'document',
                'action': 'ADDED',
                'data': item
            })
        
        # Removed documents
        for item, idx in removed:
            changes.append({
                'change_id': self._generate_change_id('document', 'REMOVED', item),
                'type': 'document',
                'action': 'REMOVED',
                'current_index': idx,
                'data': item
            })
        
        return changes
    
    def _diff_arrangements(self, current: List[Dict], scraped: List[Dict]) -> List[DiffChange]:
        """Compare arrangements"""
        changes = []
        
        # Use exact + similarity matching
        matched_pairs, added, removed = self._match_items_by_exact_then_similarity(
            current, scraped,
            key_field='name',
            threshold=0.92
        )
        
        # Check modifications
        for curr_item, new_item, curr_idx, new_idx in matched_pairs:
            modifications = []
            
            for field in ['name', 'description', 'duration', 'category', 'age_restriction', 'group_size']:
                if curr_item.get(field) != new_item.get(field):
                    modifications.append({
                        'field': field,
                        'old_value': curr_item.get(field),
                        'new_value': new_item.get(field)
                    })
            
            # Compare price arrays
            curr_prices = curr_item.get('price', [])
            new_prices = new_item.get('price', [])
            if sorted(curr_prices) != sorted(new_prices):
                modifications.append({
                    'field': 'price',
                    'old_value': ', '.join(curr_prices) if curr_prices else 'None',
                    'new_value': ', '.join(new_prices) if new_prices else 'None'
                })
            
            if modifications:
                changes.append({
                    'change_id': self._generate_change_id('arrangement', 'MODIFIED', new_item),
                    'type': 'arrangement',
                    'action': 'MODIFIED',
                    'current_index': curr_idx,
                    'data': new_item,
                    'modifications': modifications
                })
        
        # Added arrangements
        for item, idx in added:
            changes.append({
                'change_id': self._generate_change_id('arrangement', 'ADDED', item),
                'type': 'arrangement',
                'action': 'ADDED',
                'data': item
            })
        
        # Removed arrangements
        for item, idx in removed:
            changes.append({
                'change_id': self._generate_change_id('arrangement', 'REMOVED', item),
                'type': 'arrangement',
                'action': 'REMOVED',
                'current_index': idx,
                'data': item
            })
        
        return changes
    
    def _diff_business_info(self, current: Dict, scraped: Dict) -> List[DiffChange]:
        """Compare business info"""
        changes = []
        
        for field in ['name', 'url', 'type', 'description']:
            if current.get(field) != scraped.get(field):
                changes.append({
                    'change_id': self._generate_change_id('business_info', 'MODIFIED', {'field': field}),
                    'type': 'business_info',
                    'action': 'MODIFIED',
                    'field': field,
                    'old_value': current.get(field),
                    'new_value': scraped.get(field)
                })
        
        # Check opening hours
        curr_hours = current.get('opening_hours', {})
        new_hours = scraped.get('opening_hours', {})
        
        if curr_hours != new_hours:
            changes.append({
                'change_id': self._generate_change_id('business_info', 'MODIFIED', {'field': 'opening_hours'}),
                'type': 'business_info',
                'action': 'MODIFIED',
                'field': 'opening_hours',
                'old_value': curr_hours,
                'new_value': new_hours
            })
        
        return changes
    
    # =========================================================================
    # MATCHING HELPERS
    # =========================================================================
    
    def _match_items_by_field(
        self, 
        current: List[Dict], 
        scraped: List[Dict],
        key_field: str
    ) -> Tuple[List, List, List]:
        """Match items by exact field value"""
        matched_pairs = []
        added = []
        removed = []
        
        current_map = {item.get(key_field): (item, idx) for idx, item in enumerate(current) if item.get(key_field)}
        scraped_map = {item.get(key_field): (item, idx) for idx, item in enumerate(scraped) if item.get(key_field)}
        
        for key, (scraped_item, scraped_idx) in scraped_map.items():
            if key in current_map:
                current_item, current_idx = current_map[key]
                matched_pairs.append((current_item, scraped_item, current_idx, scraped_idx))
            else:
                added.append((scraped_item, scraped_idx))
        
        for key, (current_item, current_idx) in current_map.items():
            if key not in scraped_map:
                removed.append((current_item, current_idx))
        
        return matched_pairs, added, removed
    
    def _match_items_by_exact_then_similarity(
        self,
        current: List[Dict],
        scraped: List[Dict],
        key_field: str,
        threshold: float = 0.85
    ) -> Tuple[List, List, List]:
        """
        Match items by EXACT match first, then similarity for unmatched
        """
        matched_pairs = []
        added = []
        removed = []
        
        # PHASE 1: Exact matching (normalized)
        scraped_remaining = list(enumerate(scraped))
        current_remaining = list(enumerate(current))
        
        scraped_normalized: Dict[str, Tuple[Dict, int]] = {}
        for idx, item in scraped_remaining:
            key = ' '.join(item.get(key_field, '').lower().split())
            if key:
                scraped_normalized[key] = (item, idx)
        
        current_exact_matched: Set[int] = set()
        for curr_idx, curr_item in list(current_remaining):
            key = ' '.join(curr_item.get(key_field, '').lower().split())
            if key and key in scraped_normalized:
                scraped_item, scraped_idx = scraped_normalized[key]
                matched_pairs.append((curr_item, scraped_item, curr_idx, scraped_idx))
                current_exact_matched.add(curr_idx)
                scraped_remaining = [(i, item) for i, item in scraped_remaining if i != scraped_idx]
        
        current_remaining = [(idx, item) for idx, item in current_remaining if idx not in current_exact_matched]
        
        # PHASE 2: Similarity matching for unmatched items
        for curr_idx, curr_item in current_remaining:
            curr_text = curr_item.get(key_field, '')
            if not curr_text:
                removed.append((curr_item, curr_idx))
                continue
            
            best_match = None
            best_score = 0.0
            best_idx = None
            
            for scraped_idx, scraped_item in scraped_remaining:
                scraped_text = scraped_item.get(key_field, '')
                if not scraped_text:
                    continue
                
                score = difflib.SequenceMatcher(None, curr_text.lower(), scraped_text.lower()).ratio()
                if score > best_score:
                    best_score = score
                    best_match = scraped_item
                    best_idx = scraped_idx
            
            if best_score >= threshold and best_match is not None:
                matched_pairs.append((curr_item, best_match, curr_idx, best_idx))
                scraped_remaining = [(i, item) for i, item in scraped_remaining if i != best_idx]
            else:
                removed.append((curr_item, curr_idx))
        
        # All remaining scraped items are new
        for idx, item in scraped_remaining:
            added.append((item, idx))
        
        logger.debug(f"Matching {key_field}: {len(matched_pairs)} matched, {len(added)} added, {len(removed)} removed")
        
        return matched_pairs, added, removed
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def _generate_text_diff(self, old_text: str, new_text: str) -> str:
        """Generate HTML diff for text fields"""
        try:
            differ = difflib.HtmlDiff()
            html = differ.make_table(
                old_text.splitlines(),
                new_text.splitlines(),
                fromdesc='Current',
                todesc='Scraped',
                context=True,
                numlines=2
            )
            return html
        except Exception as e:
            logger.error(f"Error generating diff: {e}")
            return ""
    
    def _generate_summary(self, changes: List[DiffChange]) -> DiffSummary:
        """Generate summary statistics for changes"""
        summary: DiffSummary = {
            'total': len(changes),
            'by_type': {},
            'by_action': {
                'ADDED': 0,
                'MODIFIED': 0,
                'REMOVED': 0
            }
        }
        
        for change in changes:
            change_type = change['type']
            if change_type not in summary['by_type']:
                summary['by_type'][change_type] = {
                    'ADDED': 0,
                    'MODIFIED': 0,
                    'REMOVED': 0
                }
            
            action = change['action']
            summary['by_type'][change_type][action] += 1
            summary['by_action'][action] += 1
        
        return summary
    
    def _generate_change_id(self, change_type: str, action: str, data: Dict) -> str:
        """
        Generate deterministic change ID based on content
        """
        if change_type == 'faq':
            key = data.get('question', '')
        elif change_type == 'section':
            key = data.get('url', '') or data.get('title', '')
        elif change_type == 'document':
            key = data.get('url', '') or data.get('filename', '')
        elif change_type == 'arrangement':
            key = data.get('name', '')
        elif change_type == 'business_info':
            key = data.get('field', '')
        else:
            key = str(data)
        
        hash_input = f"{change_type}:{action}:{key}"
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()[:12]
        return f"{change_type}_{action}_{hash_value}"
    
    # =========================================================================
    # APPLY CHANGE METHODS
    # =========================================================================
    
    def _apply_faq_change(self, content: Dict, change: DiffChange, action: str):
        """Apply FAQ change"""
        faqs = content.setdefault('faqs', [])
        
        if action == 'ADDED':
            faqs.append(change['data'])
        elif action == 'MODIFIED':
            idx = change.get('current_index')
            if idx is not None and idx < len(faqs):
                faqs[idx] = change['data']
        elif action == 'REMOVED':
            idx = change.get('current_index')
            if idx is not None and idx < len(faqs):
                faqs.pop(idx)
    
    def _apply_section_change(self, content: Dict, change: DiffChange, action: str):
        """Apply section change"""
        sections = content.setdefault('content_sections', [])
        
        if action == 'ADDED':
            sections.append(change['data'])
        elif action == 'MODIFIED':
            idx = change.get('current_index')
            if idx is not None and idx < len(sections):
                sections[idx] = change['data']
        elif action == 'REMOVED':
            idx = change.get('current_index')
            if idx is not None and idx < len(sections):
                sections.pop(idx)
    
    def _apply_document_change(self, content: Dict, change: DiffChange, action: str):
        """Apply PDF document change"""
        documents = content.setdefault('pdf_documents', [])
        
        if action == 'ADDED':
            documents.append(change['data'])
        elif action == 'MODIFIED':
            idx = change.get('current_index')
            if idx is not None and idx < len(documents):
                documents[idx] = change['data']
        elif action == 'REMOVED':
            idx = change.get('current_index')
            if idx is not None and idx < len(documents):
                documents.pop(idx)
    
    def _apply_arrangement_change(self, content: Dict, change: DiffChange, action: str):
        """Apply arrangement change"""
        arrangements = content.setdefault('arrangements', [])
        
        if action == 'ADDED':
            arrangements.append(change['data'])
        elif action == 'MODIFIED':
            idx = change.get('current_index')
            if idx is not None and idx < len(arrangements):
                arrangements[idx] = change['data']
        elif action == 'REMOVED':
            idx = change.get('current_index')
            if idx is not None and idx < len(arrangements):
                arrangements.pop(idx)
    
    def _apply_business_info_change(self, content: Dict, change: DiffChange, action: str):
        """Apply business info change"""
        business_info = content.setdefault('business_info', {})
        
        if action == 'MODIFIED':
            field = change.get('field')
            if field:
                business_info[field] = change.get('new_value')


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_diff_service_instance: Optional[KBDiffService] = None


def get_diff_service() -> KBDiffService:
    """Get or create diff service instance"""
    global _diff_service_instance
    if _diff_service_instance is None:
        _diff_service_instance = KBDiffService()
    return _diff_service_instance
