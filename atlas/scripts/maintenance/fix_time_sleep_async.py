#!/usr/bin/env python3
"""
Fix time.sleep() calls in async functions to use await asyncio.sleep().

This script automatically replaces blocking time.sleep() calls with non-blocking
asyncio.sleep() in async functions to prevent event loop blocking.
"""

import re
from pathlib import Path
import sys
import ast
from typing import List, Tuple, Dict, Any


def analyze_file_for_time_sleep(filepath: Path) -> Dict[str, Any]:
    """Analyze a file for time.sleep usage and async functions."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"error": str(e), "filepath": str(filepath)}
    
    # Parse AST to understand structure
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return {"error": f"Syntax error: {e}", "filepath": str(filepath)}
    
    analysis = {
        "filepath": str(filepath),
        "has_async_functions": False,
        "has_time_sleep": False,
        "time_sleep_calls": [],
        "async_functions": [],
        "sync_functions": [],
        "needs_fix": False,
        "has_asyncio_import": False,
    }
    
    # Check for asyncio import
    analysis["has_asyncio_import"] = bool(re.search(r'^import asyncio', content, re.MULTILINE))
    
    # Find time.sleep calls
    time_sleep_matches = list(re.finditer(r'time\.sleep\(([^)]+)\)', content))
    if time_sleep_matches:
        analysis["has_time_sleep"] = True
        for match in time_sleep_matches:
            analysis["time_sleep_calls"].append({
                "line": content[:match.start()].count('\n') + 1,
                "match": match.group(0),
                "arg": match.group(1)
            })
    
    # Analyze functions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_info = {
                "name": node.name,
                "line": node.lineno,
                "is_async": False
            }
            analysis["sync_functions"].append(func_info)
            
        elif isinstance(node, ast.AsyncFunctionDef):
            func_info = {
                "name": node.name,
                "line": node.lineno,
                "is_async": True
            }
            analysis["async_functions"].append(func_info)
            analysis["has_async_functions"] = True
    
    # Determine if fix is needed
    analysis["needs_fix"] = (
        analysis["has_async_functions"] and 
        analysis["has_time_sleep"] and
        not analysis["has_asyncio_import"]
    )
    
    return analysis


def fix_time_sleep_in_file(filepath: Path) -> Tuple[bool, str]:
    """Replace time.sleep with await asyncio.sleep in async functions."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"Error reading file: {e}"
    
    # Check if file has async functions
    if 'async def' not in content:
        return False, "No async functions found"
    
    # Check if already has asyncio import
    has_asyncio_import = bool(re.search(r'^import asyncio', content, re.MULTILINE))
    
    # Replace time.sleep with await asyncio.sleep
    new_content, replacements = re.subn(
        r'time\.sleep\(([^)]+)\)',
        r'await asyncio.sleep(\1)',
        content
    )
    
    if replacements == 0:
        return False, "No time.sleep() calls found"
    
    # Add asyncio import if not present
    if not has_asyncio_import:
        # Find first import or beginning of file
        import_match = re.search(r'^(import |from )', new_content, re.MULTILINE)
        if import_match:
            insert_pos = import_match.start()
            new_content = (
                new_content[:insert_pos] +
                "import asyncio\n" +
                new_content[insert_pos:]
            )
        else:
            new_content = "import asyncio\n\n" + new_content
    
    # Remove time import if no longer used
    if 'time.' not in new_content.replace('await asyncio.sleep', ''):
        new_content = re.sub(r'^import time\s*$', '', new_content, flags=re.MULTILINE)
        new_content = re.sub(r'^from time import.*$', '', new_content, flags=re.MULTILINE)
    
    # Write back
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, f"Fixed {replacements} time.sleep() calls"
    except Exception as e:
        return False, f"Error writing file: {e}"


def find_files_with_time_sleep() -> List[Path]:
    """Find all Python files that contain time.sleep calls."""
    project_root = Path(__file__).parent.parent.parent
    files_with_time_sleep = []
    
    # Search in app directory
    for py_file in project_root.glob("app/**/*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'time.sleep(' in content:
                    files_with_time_sleep.append(py_file)
        except Exception:
            continue
    
    return files_with_time_sleep


def main():
    """Main entry point for the time.sleep fixer."""
    print("🔧 Fixing time.sleep() calls in async functions...")
    print("=" * 60)
    
    # Find all files with time.sleep
    files_with_time_sleep = find_files_with_time_sleep()
    
    if not files_with_time_sleep:
        print("✅ No files with time.sleep() found!")
        return 0
    
    print(f"📁 Found {len(files_with_time_sleep)} files with time.sleep() calls:")
    for file_path in files_with_time_sleep:
        print(f"  - {file_path}")
    print()
    
    # Analyze each file
    files_to_fix = []
    for file_path in files_with_time_sleep:
        analysis = analyze_file_for_time_sleep(file_path)
        
        if "error" in analysis:
            print(f"❌ Error analyzing {file_path}: {analysis['error']}")
            continue
        
        print(f"📊 {file_path}:")
        print(f"  - Async functions: {len(analysis['async_functions'])}")
        print(f"  - Sync functions: {len(analysis['sync_functions'])}")
        print(f"  - time.sleep calls: {len(analysis['time_sleep_calls'])}")
        print(f"  - Has asyncio import: {analysis['has_asyncio_import']}")
        print(f"  - Needs fix: {analysis['needs_fix']}")
        
        if analysis['time_sleep_calls']:
            print("  - time.sleep locations:")
            for call in analysis['time_sleep_calls']:
                print(f"    Line {call['line']}: {call['match']}")
        
        if analysis['needs_fix']:
            files_to_fix.append(file_path)
        
        print()
    
    if not files_to_fix:
        print("✅ No files need fixing!")
        return 0
    
    print(f"🔧 Files that need fixing: {len(files_to_fix)}")
    print()
    
    # Fix files
    fixed_count = 0
    for file_path in files_to_fix:
        print(f"🔧 Fixing {file_path}...")
        success, message = fix_time_sleep_in_file(file_path)
        
        if success:
            print(f"✅ {message}")
            fixed_count += 1
        else:
            print(f"❌ {message}")
        print()
    
    print("=" * 60)
    print(f"🎉 Fixed {fixed_count} files")
    
    if fixed_count > 0:
        print("\n⚠️  Next steps:")
        print("1. Run tests: pytest tests/ -v")
        print("2. Check for any remaining time.sleep calls:")
        print("   grep -r 'time\\.sleep' app --include='*.py' | grep -v '#'")
        print("3. Test async functionality manually")
        print("4. Commit changes")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
