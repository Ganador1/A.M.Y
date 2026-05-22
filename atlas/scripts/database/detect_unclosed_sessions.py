#!/usr/bin/env python3

import re
from pathlib import Path

def check_session_management(filepath):
    """Check for unclosed database sessions in a Python file."""
    with open(filepath) as f:
        content = f.read()

    issues = []

    # Pattern 1: Session() without with statement
    sessions = re.finditer(r'(\w+)\s*=\s*SessionLocal\(\)', content)
    for match in sessions:
        var_name = match.group(1)
        # Check if used in 'with' statement
        with_pattern = rf'with\s+SessionLocal\(\)\s+as\s+{var_name}'
        if not re.search(with_pattern, content):
            line = content[:match.start()].count('\n') + 1
            issues.append({
                'file': str(filepath),
                'line': line,
                'issue': f'Session {var_name} not used in context manager',
                'severity': 'HIGH'
            })

    # Pattern 2: Direct Session() instantiation without proper cleanup
    direct_sessions = re.finditer(r'Session\(\)', content)
    for match in direct_sessions:
        line = content[:match.start()].count('\n') + 1
        issues.append({
            'file': str(filepath),
            'line': line,
            'issue': 'Direct Session() instantiation without context manager',
            'severity': 'HIGH'
        })

    # Pattern 3: get_db_session() without proper cleanup
    db_sessions = re.finditer(r'(\w+)\s*=\s*get_db_session\(\)', content)
    for match in db_sessions:
        var_name = match.group(1)
        # Check if session.close() is called
        close_pattern = rf'{var_name}\.close\(\)'
        if not re.search(close_pattern, content):
            line = content[:match.start()].count('\n') + 1
            issues.append({
                'file': str(filepath),
                'line': line,
                'issue': f'get_db_session() {var_name} without explicit close()',
                'severity': 'MEDIUM'
            })

    return issues

def main():
    """Scan all service files for session management issues."""
    print("🔍 Scanning for database session management issues...")
    print("=" * 60)

    total_issues = []
    scan_dirs = [
        Path('app/services'),
        Path('app/routers'),
        Path('app/core'),
        Path('app/api')
    ]

    for scan_dir in scan_dirs:
        if scan_dir.exists():
            print(f"\n📁 Scanning {scan_dir}/")
            for service in scan_dir.glob('*.py'):
                issues = check_session_management(service)
                for issue in issues:
                    total_issues.append(issue)
                    print(f"⚠️  {issue['file']}:{issue['line']} - {issue['issue']}")

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total issues found: {len(total_issues)}")

    high_severity = len([i for i in total_issues if i['severity'] == 'HIGH'])
    medium_severity = len([i for i in total_issues if i['severity'] == 'MEDIUM'])

    print(f"🔴 High severity issues: {high_severity}")
    print(f"🟡 Medium severity issues: {medium_severity}")

    if total_issues:
        print("
💡 RECOMMENDATIONS:"        print("- Use 'with SessionLocal() as session:' instead of manual session management")
        print("- Use FastAPI dependency injection with 'get_db' for endpoints")
        print("- Always call session.close() in finally blocks if using manual management")
        print("- Consider using context managers for all database operations")

    return len(total_issues)

if __name__ == "__main__":
    exit(main())
