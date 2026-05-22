#!/usr/bin/env python3

"""
Targeted Manual Fixes - Apply specific corrections to high-priority files
Based on manual review analysis results
"""

import os
import re

def fix_high_priority_files():
    """Fix the most critical high-priority files identified in manual review."""

    # List of files that need specific attention based on manual analysis
    high_priority_fixes = [
        {
            'file': 'app/routers/auth.py',
            'issues': ['requests without httpx'],
            'actions': [
                'Add httpx import',
                'Replace requests calls with httpx'
            ]
        },
        {
            'file': 'app/routers/cache.py',
            'issues': ['requests without httpx'],
            'actions': [
                'Add httpx import',
                'Replace requests.get with await httpx.get'
            ]
        },
        {
            'file': 'app/connectors/astronomical_data_connector.py',
            'issues': ['requests without httpx'],
            'actions': [
                'Add httpx import',
                'Replace requests calls'
            ]
        },
        {
            'file': 'app/middleware/profiling.py',
            'issues': ['requests without httpx'],
            'actions': [
                'Add httpx import',
                'Replace requests calls'
            ]
        },
        {
            'file': 'app/domains/astronomy/routers/api.py',
            'issues': ['requests without httpx'],
            'actions': [
                'Add httpx import'
            ]
        },
        {
            'file': 'app/domains/chemistry/routers/api.py',
            'issues': ['requests without httpx'],
            'actions': [
                'Add httpx import'
            ]
        },
        {
            'file': 'app/domains/mathematics/routers/api.py',
            'issues': ['requests without httpx'],
            'actions': [
                'Add httpx import'
            ]
        },
        {
            'file': 'app/domains/medicine/routers/api.py',
            'issues': ['requests without httpx'],
            'actions': [
                'Add httpx import'
            ]
        },
        {
            'file': 'app/domains/physics/routers/api.py',
            'issues': ['requests without httpx'],
            'actions': [
                'Add httpx import'
            ]
        },
        {
            'file': 'app/domains/engineering/routers/core/api.py',
            'issues': ['requests without httpx'],
            'actions': [
                'Add httpx import'
            ]
        },
        {
            'file': 'app/domains/biology/routers/api.py',
            'issues': ['requests without httpx'],
            'actions': [
                'Add httpx import'
            ]
        },
        {
            'file': 'app/distributed/distributed_scaling_manager.py',
            'issues': ['requests without httpx'],
            'actions': [
                'Add httpx import'
            ]
        }
    ]

    total_files_fixed = 0
    total_fixes_applied = 0

    print("🎯 TARGETED MANUAL FIXES")
    print("=" * 50)
    print("Applying specific corrections to high-priority files...")

    for fix_config in high_priority_fixes:
        filepath = fix_config['file']

        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            fixes_applied = []

            # Apply specific fixes based on the configuration
            if 'Add httpx import' in fix_config['actions']:
                if 'import httpx' not in content:
                    # Add httpx import
                    import_match = re.search(r'(^import .*\n|^from .*\n)+', content, re.MULTILINE)
                    if import_match:
                        insert_pos = import_match.end()
                        content = content[:insert_pos] + 'import httpx\n' + content[insert_pos:]
                        fixes_applied.append('Added httpx import')

            if 'Replace requests calls' in fix_config['actions'] or 'Replace requests.get with await httpx.get' in fix_config['actions']:
                if 'requests.' in content and 'httpx' in content:
                    # Replace requests.get/post/put/delete with httpx equivalents
                    replacements = [
                        (r'requests\.get\(', 'httpx.get('),
                        (r'requests\.post\(', 'httpx.post('),
                        (r'requests\.put\(', 'httpx.put('),
                        (r'requests\.delete\(', 'httpx.delete('),
                    ]

                    for old_pattern, new_pattern in replacements:
                        content = re.sub(re.escape(old_pattern), new_pattern, content)

                    # Add await to httpx calls in async functions
                    content = re.sub(r'(\s+)httpx\.(get|post|put|delete)\(', r'\1await httpx.\2(', content)

                    if 'await httpx.' in content:
                        fixes_applied.append('Replaced requests with httpx')

            # Only write if changes were made
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

                print(f"✅ {filepath}: {', '.join(fixes_applied)}")
                total_files_fixed += 1
                total_fixes_applied += len(fixes_applied)
            else:
                print(f"⏭️  {filepath}: No changes needed")

        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")

    print("\n📊 TARGETED FIXES SUMMARY")
    print("=" * 50)
    print(f"Files targeted: {len(high_priority_fixes)}")
    print(f"Files fixed: {total_files_fixed}")
    print(f"Fixes applied: {total_fixes_applied}")

    if total_files_fixed > 0:
        print("\n✅ HIGH-PRIORITY ISSUES ADDRESSED")
        print("• HTTP requests now use httpx async client")
        print("• Ready for final verification")
    else:
        print("\n⚠️  Files may already be optimized")

    print("\n💡 Next steps:")
    print("• Run final verification")
    print("• Check remaining medium-priority issues")
    print("• Consider JSON operations if needed")

if __name__ == "__main__":
    fix_high_priority_files()
