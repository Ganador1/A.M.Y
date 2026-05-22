#!/usr/bin/env python3
import os
import ast
import json
import argparse
from typing import List, Dict, Any

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOMAINS_DIR = os.path.join(ROOT, "app", "domains")


def find_python_files(base_dir: str) -> List[str]:
    files = []
    for dirpath, _, filenames in os.walk(base_dir):
        for f in filenames:
            if f.endswith(".py") and not f.startswith("__"):
                files.append(os.path.join(dirpath, f))
    return files


def analyze_file(file_path: str) -> Dict[str, Any]:
    result = {"file": file_path, "missing": []}
    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            source = fh.read()
        tree = ast.parse(source, filename=file_path)
    except Exception as e:
        result["error"] = str(e)
        return result

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node)
            if not doc:
                result["missing"].append({
                    "type": "function",
                    "name": node.name,
                    "lineno": getattr(node, "lineno", None)
                })
        elif isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node)
            if not doc:
                result["missing"].append({
                    "type": "class",
                    "name": node.name,
                    "lineno": getattr(node, "lineno", None)
                })

    # Module docstring
    module_doc = ast.get_docstring(tree)
    if not module_doc:
        result["missing"].insert(0, {"type": "module", "name": os.path.basename(file_path), "lineno": 1})

    return result


def filter_domain(files: List[str], domain: str) -> List[str]:
    if not domain or domain == "all":
        return files
    domain_path = os.path.join(DOMAINS_DIR, domain)
    return [f for f in files if f.startswith(domain_path)]


def main():
    parser = argparse.ArgumentParser(description="Audit docstrings in AXIOM domains")
    parser.add_argument("--domain", default="all", help="Domain to audit (e.g., biology). Default: all")
    parser.add_argument("--report", default=None, help="Path to write JSON report")
    args = parser.parse_args()

    py_files = find_python_files(DOMAINS_DIR)
    py_files = filter_domain(py_files, args.domain)

    report = []
    for f in py_files:
        report.append(analyze_file(f))

    summary = {
        "total_files": len(py_files),
        "files_with_missing": sum(1 for r in report if r.get("missing")),
        "total_missing_items": sum(len(r.get("missing", [])) for r in report),
    }

    output = {"summary": summary, "results": report}

    if args.report:
        os.makedirs(os.path.dirname(args.report), exist_ok=True)
        with open(args.report, "w", encoding="utf-8") as fh:
            json.dump(output, fh, indent=2)
        print(f"Report written to {args.report}")
    else:
        print(json.dumps(output["summary"], indent=2))


if __name__ == "__main__":
    main()