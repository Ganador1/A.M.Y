#!/usr/bin/env python3

"""
Automatic Async I/O Migration - Fix common blocking patterns in async functions
"""

import os
import re
from pathlib import Path

def fix_blocking_io_in_file(filepath):
    """Fix blocking I/O operations in async functions."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        fixes_applied = []

        # Fix 1: Add aiofiles import for file operations
        if 'open(' in content and 'async def' in content:
            if 'import aiofiles' not in content and 'from aiofiles' not in content:
                # Add aiofiles import after existing imports
                import_match = re.search(r'(^import .*\n|^from .*\n)+', content, re.MULTILINE)
                if import_match:
                    insert_pos = import_match.end()
                    content = content[:insert_pos] + 'import aiofiles\n' + content[insert_pos:]
                    fixes_applied.append('Added aiofiles import')

        # Fix 2: Replace blocking file operations with aiofiles
        if 'open(' in content and 'aiofiles' in content:
            # Replace open() with aiofiles.open() in async functions
            def replace_open(match):
                context = match.group(0)
                if 'async def' in context[:context.find('open(')]:
                    return 'aiofiles.open(' + match.group(1)
                return match.group(0)

            content = re.sub(r'open\(([^)]+)\)', replace_open, content)
            fixes_applied.append('Replaced open() with aiofiles.open()')

        # Fix 3: Add httpx import for HTTP requests
        if 'requests.' in content and 'async def' in content:
            if 'import httpx' not in content and 'from httpx' not in content:
                # Add httpx import
                import_match = re.search(r'(^import .*\n|^from .*\n)+', content, re.MULTILINE)
                if import_match:
                    insert_pos = import_match.end()
                    content = content[:insert_pos] + 'import httpx\n' + content[insert_pos:]
                    fixes_applied.append('Added httpx import')

        # Fix 4: Replace requests with httpx async client
        if 'requests.' in content and 'httpx' in content:
            # Replace requests.get/post/put/delete with httpx
            def replace_requests(match):
                method = match.group(1)
                url = match.group(2)
                if 'async def' in match.string[max(0, match.start() - 200):match.start()]:
                    return f'await httpx.{method}({url})'
                return match.group(0)

            content = re.sub(r'requests\.(\w+)\(([^)]+)\)', replace_requests, content)
            fixes_applied.append('Replaced requests with httpx')

        # Fix 5: Add asyncio for JSON operations
        if ('json.load' in content or 'json.dump' in content) and 'async def' in content:
            if 'import asyncio' not in content:
                import_match = re.search(r'(^import .*\n|^from .*\n)+', content, re.MULTILINE)
                if import_match:
                    insert_pos = import_match.end()
                    content = content[:insert_pos] + 'import asyncio\n' + content[insert_pos:]
                    fixes_applied.append('Added asyncio import')

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
    """Main migration function."""
    print("🔧 AUTOMATIC ASYNC I/O MIGRATION")
    print("=" * 50)

    # Target directories
    target_dirs = [
        "app/services",
        "app/routers",
        "app/domains",
        "app/core",
        "app/monitoring"
    ]

    total_files_fixed = 0
    total_fixes_applied = 0

    for target_dir in target_dirs:
        if os.path.exists(target_dir):
            print(f"\n📁 Processing {target_dir}/")

            for root, dirs, files in os.walk(target_dir):
                for file in files:
                    if file.endswith(".py"):
                        filepath = os.path.join(root, file)

                        fixes = fix_blocking_io_in_file(filepath)
                        if fixes:
                            print(f"✅ {filepath}: {', '.join(fixes)}")
                            total_files_fixed += 1
                            total_fixes_applied += len(fixes)

    print("\n📊 MIGRATION SUMMARY")
    print("=" * 50)
    print(f"Files processed: {total_files_fixed}")
    print(f"Fixes applied: {total_fixes_applied}")
    print("\n💡 Next steps:")
    print("• Run tests to ensure changes work correctly")
    print("• Consider manual review of complex files")
    print("• Update any remaining blocking operations manually")

if __name__ == "__main__":
    main()
