#!/usr/bin/env python3
import sys
import re

def check_file(filepath):
    with open(filepath, encoding="utf-8", errors="ignore") as f:
        content = f.read()

    errors = []
    for match in re.finditer(r"(?m)^\s*raise\s+Exception\s*\(", content):
        line_num = content[:match.start()].count("\n") + 1
        errors.append(f"{filepath}:{line_num}: raise Exception detected")
    return errors

def main():
    all_errors = []
    for filepath in sys.argv[1:]:
        all_errors.extend(check_file(filepath))

    if all_errors:
        print("\n".join(all_errors))
        sys.exit(1)

if __name__ == "__main__":
    main()