import ast, os
from pathlib import Path

broken = []
for root, dirs, files in os.walk('.'):
    if 'atlas' in root or '__pycache__' in root or '.venv' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            p = Path(root) / f
            try:
                tree = ast.parse(p.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        mod = node.module
                        if mod.startswith(('core.', 'cognition.', 'memory.', 'skills.', 'communication.', 'senses.', 'evolution.', 'sandbox.')):
                            parts = mod.split('.')
                            target = Path(parts[0]) / (parts[1] + '.py')
                            if not target.exists():
                                broken.append((str(p), mod))
            except Exception as e:
                broken.append((str(p), f'PARSE_ERROR: {e}'))

for b in broken:
    print(f'{b[0]} -> {b[1]}')
