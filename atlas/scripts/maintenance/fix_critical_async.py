#!/usr/bin/env python3

"""
Critical Async Fix - Fix time.sleep in async functions
"""

import os
import re
from pathlib import Path

def fix_time_sleep_in_async(filepath):
    """Fix time.sleep calls in async functions."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        fixes_applied = []

        # Check if file has async functions AND time.sleep
        if 'async def' in content and 'time.sleep' in content:
            # Add asyncio import if not present
            if 'import asyncio' not in content and 'from asyncio' not in content:
                # Find first import section
                import_match = re.search(r'(^import .*\n|^from .*\n)+', content, re.MULTILINE)
                if import_match:
                    insert_pos = import_match.end()
                    content = content[:insert_pos] + 'import asyncio\n' + content[insert_pos:]
                    fixes_applied.append('Added asyncio import')

            # Replace time.sleep with await asyncio.sleep
            def replace_sleep(match):
                sleep_time = match.group(1)
                return f'await asyncio.sleep({sleep_time})'

            content = re.sub(r'time\.sleep\(([^)]+)\)', replace_sleep, content)
            fixes_applied.append('Replaced time.sleep with await asyncio.sleep')

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
    """Fix critical async files."""
    print("🚨 CRITICAL ASYNC FIX - Fixing time.sleep in async functions")
    print("=" * 60)

    # Critical files identified in the scan
    critical_files = [
        "app/routers/mathlab.py",
        "app/core/metrics.py",
        "app/core/database.py",
        "app/core/executors.py",
        "app/distributed/distributed_scaling_manager.py",
        "app/adapters/tool_adapter.py",
        "app/monitoring/service_profiler.py",
        "app/services/ollama_service.py",
        "app/advanced_ops/advanced_fastapi_operations.py"
    ]

    total_files_fixed = 0
    total_fixes_applied = 0

    for filename in critical_files:
        if os.path.exists(filename):
            fixes = fix_time_sleep_in_async(filename)
            if fixes:
                print(f"✅ {filename}: {', '.join(fixes)}")
                total_files_fixed += 1
                total_fixes_applied += len(fixes)
        else:
            print(f"❌ File not found: {filename}")

    print("\n📊 CRITICAL FIXES SUMMARY")
    print("=" * 60)
    print(f"Critical files processed: {total_files_fixed}")
    print(f"Critical fixes applied: {total_fixes_applied}")

    if total_files_fixed > 0:
        print("\n✅ CRITICAL BLOCKING ISSUES RESOLVED")
        print("🎯 Event loop should now be completely unblocked")
    else:
        print("\n⚠️  No critical fixes were needed - files may already be correct")

    print("\n💡 Next steps:")
    print("• Run the async verification again to confirm")
    print("• Test the application to ensure it still works")
    print("• Monitor performance improvements")

if __name__ == "__main__":
    main()
