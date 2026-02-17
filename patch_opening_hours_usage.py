#!/usr/bin/env python3
"""
Add _normalize_opening_hours() calls in OrganisationModule and OpeningHoursModule
"""

# Read modules.py
with open('src/maso_shared/kb/modules.py', 'r') as f:
    content = f.read()

# Patch 1: OrganisationModule line ~183
old_org = '''        # Add opening hours if relevant
        if signals.get('opening_hours', False):
            opening_hours = business_info.get('opening_hours', {})
            if opening_hours:'''

new_org = '''        # Add opening hours if relevant
        if signals.get('opening_hours', False):
            opening_hours = _normalize_opening_hours(business_info.get('opening_hours', {}))
            if opening_hours:'''

# Patch 2: OpeningHoursModule line ~221
old_hours = '''        business_info = kb_content.get('business_info', {})
        opening_hours = business_info.get('opening_hours', {})

        if not opening_hours:'''

new_hours = '''        business_info = kb_content.get('business_info', {})
        opening_hours = _normalize_opening_hours(business_info.get('opening_hours', {}))

        if not opening_hours:'''

# Apply patches
if old_org in content:
    content = content.replace(old_org, new_org)
    print("✅ Patched OrganisationModule")
else:
    print("⚠️  OrganisationModule pattern not found")

if old_hours in content:
    content = content.replace(old_hours, new_hours)
    print("✅ Patched OpeningHoursModule")
else:
    print("⚠️  OpeningHoursModule pattern not found")

# Write back
with open('src/maso_shared/kb/modules.py', 'w') as f:
    f.write(content)

print("\n✅ Done! Both modules now use _normalize_opening_hours()")
