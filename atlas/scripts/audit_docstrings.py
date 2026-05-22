import ast
import os
from typing import List, Tuple

def find_missing_docstrings(root_dir: str) -> List[Tuple[str, str, str]]:
    missing = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(subdir, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                        if not ast.get_docstring(node):
                            missing.append((file_path, node.name, 'function' if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else 'class'))
    return missing

if __name__ == '__main__':
    root = './app'
    missing = find_missing_docstrings(root)
    output_file = './scripts/missing_docstrings.txt'
    with open(output_file, 'w') as f:
        if missing:
            f.write("Missing docstrings:\n")
            for path, name, typ in missing:
                f.write(f"{path}: {typ} {name}\n")
        else:
            f.write("All functions and classes have docstrings.\n")
    print(f"Output written to {output_file}")