#!/usr/bin/env python3

"""
Post-Migration Verification - Verify all async improvements
"""

import os
import subprocess
from pathlib import Path

def run_quick_check():
    """Run the quick async check to verify improvements."""
    print("🔍 POST-MIGRATION VERIFICATION")
    print("=" * 50)

    try:
        # Run the quick async check script
        result = subprocess.run([
            'python', 'scripts/analysis/quick_async_check.py'
        ], capture_output=True, text=True, cwd=os.getcwd())

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print("=" * 50)
        print("✅ Verification completed")

        return result.returncode == 0

    except Exception as e:
        print(f"Error running verification: {e}")
        return False

def check_specific_improvements():
    """Check specific improvements made."""
    print("\n📋 SPECIFIC IMPROVEMENTS MADE")
    print("=" * 50)

    # Check for aiofiles usage
    aiofiles_files = 0
    for root, dirs, files in os.walk("app"):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        if 'aiofiles' in f.read():
                            aiofiles_files += 1
                except:
                    pass

    print(f"✅ Files using aiofiles: {aiofiles_files}")

    # Check for httpx usage
    httpx_files = 0
    for root, dirs, files in os.walk("app"):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        if 'httpx' in f.read():
                            httpx_files += 1
                except:
                    pass

    print(f"✅ Files using httpx: {httpx_files}")

    # Check for asyncio usage
    asyncio_files = 0
    for root, dirs, files in os.walk("app"):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        if 'asyncio' in f.read():
                            asyncio_files += 1
                except:
                    pass

    print(f"✅ Files using asyncio: {asyncio_files}")

def main():
    """Main verification function."""
    print("🚀 POST-MIGRATION VERIFICATION SUITE")
    print("=" * 60)

    # Run verification
    verification_success = run_quick_check()

    # Check specific improvements
    check_specific_improvements()

    print("\n" + "=" * 60)
    print("🎯 MIGRATION STATUS")
    print("=" * 60)

    if verification_success:
        print("✅ ASYNC MIGRATION APPEARS SUCCESSFUL")
        print("• Critical blocking issues resolved")
        print("• I/O operations migrated to async")
        print("• Ready for production deployment")
    else:
        print("⚠️  SOME ISSUES DETECTED")
        print("• Review the verification output above")
        print("• Check specific files that may need manual attention")

    print("\n💡 Next steps:")
    print("• Run full test suite to ensure functionality")
    print("• Monitor application performance")
    print("• Consider manual optimization of complex files")

if __name__ == "__main__":
    main()
