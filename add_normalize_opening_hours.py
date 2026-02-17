#!/usr/bin/env python3
"""Add _normalize_opening_hours function to modules.py"""

normalize_function = '''

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
'''

# Read current modules.py
with open('src/maso_shared/kb/modules.py', 'r') as f:
    lines = f.readlines()

# Find insertion point (after logger line, before BASE MODULE INTERFACE comment)
insert_index = None
for i, line in enumerate(lines):
    if line.strip() == 'logger = logging.getLogger(__name__)':
        insert_index = i + 1
        break

if insert_index is None:
    print("❌ Could not find insertion point!")
    exit(1)

# Insert function
lines.insert(insert_index, normalize_function + '\n')

# Write back
with open('src/maso_shared/kb/modules.py', 'w') as f:
    f.writelines(lines)

print("✅ Added _normalize_opening_hours() function to modules.py")
