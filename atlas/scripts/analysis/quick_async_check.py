#!/usr/bin/env python3

"""
Quick Async Verification - Simple check for critical async issues
"""

import os
from pathlib import Path
import subprocess

def check_time_sleep_in_async():
    """Check for time.sleep in async functions across the codebase."""
    print("🔍 Checking for time.sleep in async functions...")

    critical_files = []

    for root, dirs, files in os.walk("app"):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Check if file has async functions
                    if 'async def' in content:
                        # Check if file has time.sleep
                        if 'time.sleep' in content:
                            critical_files.append(filepath)
                            print(f"🚨 CRITICAL: {filepath}")
                            # Show the problematic lines
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if 'time.sleep' in line and 'async def' in ''.join(lines[max(0, i-5):i+5]):
                                    print(f"    Line {i}: {line.strip()}")

                except Exception as e:
                    pass  # Skip files that can't be read

    return critical_files

def check_blocking_io_in_async():
    """Check for blocking I/O operations in async functions."""
    print("\n🔍 Checking for blocking I/O in async functions...")

    blocking_patterns = ['requests.', 'urllib', 'open(', 'json.load', 'json.dump']
    blocking_files = []

    for root, dirs, files in os.walk("app"):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if 'async def' in content:
                        for pattern in blocking_patterns:
                            if pattern in content:
                                blocking_files.append((filepath, pattern))
                                print(f"⚠️  BLOCKING I/O: {filepath} - {pattern}")
                                break

                except Exception as e:
                    pass

    return blocking_files

def check_async_compliance():
    """Quick check of async compliance."""
    print("\n📊 ASYNC COMPLIANCE SUMMARY")
    print("=" * 50)

    # Count async vs sync functions
    async_count = 0
    sync_count = 0

    for root, dirs, files in os.walk("app"):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    async_count += content.count('async def')
                    sync_count += content.count('def ') - content.count('async def')

                except Exception as e:
                    pass

    total_functions = async_count + sync_count
    async_ratio = async_count / total_functions if total_functions > 0 else 0

    print(f"Total functions: {total_functions}")
    print(f"Async functions: {async_count}")
    print(f"Sync functions: {sync_count}")
    print(f"Async ratio: {async_ratio:.1%}")

    if async_ratio > 0.7:
        print("🎉 EXCELLENT: High async adoption")
    elif async_ratio > 0.5:
        print("✅ GOOD: Moderate async adoption")
    elif async_ratio > 0.3:
        print("⚠️  MODERATE: Some async adoption")
    else:
        print("❌ LOW: Limited async adoption")

    return async_ratio

def main():
    """Main verification function."""
    print("🚀 COMPREHENSIVE ASYNC VERIFICATION")
    print("=" * 60)

    # Check critical issues
    critical_files = check_time_sleep_in_async()
    blocking_files = check_blocking_io_in_async()

    # Overall compliance
    async_ratio = check_async_compliance()

    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS")
    print("=" * 60)

    if not critical_files and not blocking_files and async_ratio > 0.5:
        print("✅ ASYNC IMPLEMENTATION IS COMPREHENSIVE")
        print("✅ No critical blocking issues found")
        print("✅ Good async adoption ratio")
        return 0
    else:
        print("⚠️  ASYNC IMPLEMENTATION NEEDS ATTENTION")
        if critical_files:
            print(f"🚨 {len(critical_files)} files with time.sleep in async functions")
        if blocking_files:
            print(f"⚠️  {len(blocking_files)} files with blocking I/O in async functions")
        if async_ratio <= 0.5:
            print("📈 Consider migrating more functions to async")
        return 1

if __name__ == "__main__":
    exit(main())
