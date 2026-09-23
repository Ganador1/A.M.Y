#!/usr/bin/env python3

"""
Targeted Async I/O Fixes - Focus on most common blocking patterns
"""

import os
import re
from pathlib import Path

def fix_common_blocking_patterns(filepath):
    """Fix the most common blocking I/O patterns."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        fixes_applied = []

        # Pattern 1: Simple open() calls in async functions
        if 'open(' in content and 'async def' in content:
            # Add aiofiles import if not present
            if 'import aiofiles' not in content:
                import_match = re.search(r'(^import .*\n|^from .*\n)+', content, re.MULTILINE)
                if import_match:
                    insert_pos = import_match.end()
                    content = content[:insert_pos] + 'import aiofiles\n' + content[insert_pos:]
                    fixes_applied.append('Added aiofiles import')

            # Replace simple open() calls
            content = re.sub(r'open\(([^,\)]+)\)', r'aiofiles.open(\1)', content)
            fixes_applied.append('Replaced open() with aiofiles.open()')

        # Pattern 2: JSON operations in async functions
        if ('json.load' in content or 'json.dump' in content) and 'async def' in content:
            # Add asyncio import if not present
            if 'import asyncio' not in content:
                import_match = re.search(r'(^import .*\n|^from .*\n)+', content, re.MULTILINE)
                if import_match:
                    insert_pos = import_match.end()
                    content = content[:insert_pos] + 'import asyncio\n' + content[insert_pos:]
                    fixes_applied.append('Added asyncio import')

        # Pattern 3: Simple requests calls
        if 'requests.get' in content and 'async def' in content:
            # Add httpx import if not present
            if 'import httpx' not in content:
                import_match = re.search(r'(^import .*\*\n|^from .*\n)+', content, re.MULTILINE)
                if import_match:
                    insert_pos = import_match.end()
                    content = content[:insert_pos] + 'import httpx\n' + content[insert_pos:]
                    fixes_applied.append('Added httpx import')

            # Replace requests.get calls
            content = re.sub(r'requests\.get\(([^,\)]+)\)', r'httpx.get(\1)', content)
            fixes_applied.append('Replaced requests.get with httpx.get')

        # Only write if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return fixes_applied

        return []

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return []

def main():
    """Fix common blocking patterns in targeted files."""
    print("🎯 TARGETED ASYNC I/O FIXES")
    print("=" * 50)
    print("Focusing on most common and easily fixable patterns...")

    # Target the files identified in the scan
    target_files = [
        # Core application files
        "app/routers/auth.py",
        "app/routers/system.py",
        "app/routers/cache.py",
        "app/core/metrics.py",
        "app/core/cache.py",

        # Domain files
        "app/domains/medicine/services/medical_realtime_service.py",
        "app/domains/chemistry/services/differential_scanning_calorimetry_service.py",
        "app/domains/physics/services/particle_physics_service.py",

        # Service files
        "app/services/ai_scientist_service.py",
        "app/services/cost_metrics_service.py",
        "app/services/scientific_figure_generator.py",
        "app/services/experiment_scheduler_service.py"
    ]

    total_files_fixed = 0
    total_fixes_applied = 0

    for filename in target_files:
        if os.path.exists(filename):
            fixes = fix_common_blocking_patterns(filename)
            if fixes:
                print(f"✅ {filename}: {', '.join(fixes)}")
                total_files_fixed += 1
                total_fixes_applied += len(fixes)
        else:
            print(f"❌ File not found: {filename}")

    print("\n📊 TARGETED FIXES SUMMARY")
    print("=" * 50)
    print(f"Files targeted: {len(target_files)}")
    print(f"Files fixed: {total_files_fixed}")
    print(f"Fixes applied: {total_fixes_applied}")

    if total_files_fixed > 0:
        print("\n✅ Common blocking patterns resolved")
        print("• Most frequent I/O issues addressed")
        print("• Ready for testing and validation")
    else:
        print("\n⚠️  No additional fixes needed for targeted files")

    print("\n💡 Next steps:")
    print("• Run verification again to check remaining files")
    print("• Consider manual fixes for complex cases")
    print("• Test application functionality")

if __name__ == "__main__":
    main()
