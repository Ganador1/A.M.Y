"""Offline release checks; reports paths and errors, never credential values."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
import tomllib
import zipfile
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DOCS = [
    'README.md', 'README_PUBLIC.md', 'RESEARCH.md', 'SCIENCE_MANIFESTO.md',
    'CONTRIBUTING.md', 'ENVIRONMENT.md',
    'docs/PROJECT_MAP.md', 'docs/REPRODUCIBILITY.md', 'docs/MIGRATION.md',
    'docs/RESULTS.md', 'docs/EVIDENCE.md', 'docs/research/AUTOCORRELATION.md',
    'docs/ENGLISH_MANUALS.md', 'atlas/README.md',
    'release_evidence/autocorrelation/README.md', 'release_evidence/runtime/README.md',
]


def unsafe_member(name):
    p = PurePosixPath(name)
    return (p.is_absolute() or '..' in p.parts or
            any(x in {'.git', '.venv', '__pycache__', 'output', 'zenodo_deposits'} for x in p.parts) or
            p.name in {'.env', '.api_keys.enc', '.secrets.key', 'secret.yml', 'secret.yaml'} or
            p.name.startswith('.secrets.') or
            (p.name.startswith('secrets_') and p.suffix == '.json') or
            p.name.endswith('.secret.json') or
            p.suffix in {'.key', '.pem', '.enc', '.pyc', '.db', '.sqlite', '.jsonl'} or
            (p.name.startswith('.env.') and p.name != '.env.example'))


def nonpublic_member(name):
    """Reject working notes, generated state and library-shadowing test stubs."""
    p = PurePosixPath(name)
    normalized = '/' + str(p).lstrip('/')
    return (p.name == 'RELEASE_CHECKLIST.md' or
            any(part in {'.cache', '.pytest_cache', '.amy_artifact_store',
                         'amx_receipts', 'amy_workspace'} for part in p.parts) or
            any(prefix in normalized for prefix in (
                '/docs/releases/', '/docs/publication/', '/sandbox/scripts/',
                '/guides/archive/', '/guides/paper_')) or
            (p.parent.name == 'atlas' and
             (p.name in {'brian2.py', 'libsbml.py', 'seaborn.py'} or
              p.name.endswith('_shadow_bak.py'))))


def check(root=ROOT, dist=None):
    errors = []
    source_manifest = root / 'PUBLIC_SOURCE_MANIFEST.json'
    if source_manifest.exists():
        for row in json.loads(source_manifest.read_text())['files']:
            if unsafe_member(row['path']) or nonpublic_member(row['path']):
                errors.append('nonpublic source member: ' + row['path'])
    metadata = tomllib.loads((root / 'pyproject.toml').read_text())['project']
    version = metadata['version']
    runtime = next(n.value.value for n in ast.parse((root / 'amy.py').read_text()).body
                   if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '__version__' for t in n.targets))
    citation = (root / 'CITATION.cff').read_text()
    if runtime != version or f'version: {version}\n' not in citation:
        errors.append('runtime/package/citation versions differ')
    if '10.5281/zenodo.1234567' in citation:
        errors.append('placeholder DOI')
    lock = tomllib.loads((root / 'uv.lock').read_text())
    if next(x['version'] for x in lock['package'] if x['name'] == 'amy') != version:
        errors.append('lockfile version differs')
    for name in PUBLIC_DOCS:
        path = root / name
        if not path.exists():
            errors.append('missing public document: ' + name)
            continue
        text = path.read_text()
        if '/Volumes/' in text or '/Users/' in text:
            errors.append('machine-specific public link: ' + name)
        for target in re.findall(r'\]\(([^\s)]+)\)', text):
            if target.startswith(('http:', 'https:', '#', 'mailto:')):
                continue
            target = unquote(target.split('#')[0])
            if target and not (path.parent / target).exists():
                errors.append(f'broken local link: {name}: {target}')
    evidence = root / 'release_evidence/autocorrelation'
    manifest = json.loads((evidence / 'MANIFEST.json').read_text())
    for name, digest in manifest['sha256'].items():
        path = evidence / name
        if path.parent != evidence or path.is_symlink() or not path.is_file():
            errors.append('invalid evidence member: ' + name)
        elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            errors.append('evidence hash mismatch: ' + name)
    artifacts = []
    if dist:
        for path in sorted(Path(dist).iterdir()):
            if path.suffix == '.whl':
                with zipfile.ZipFile(path) as z:
                    names = z.namelist()
                    if 'amy.py' not in names or 'core/runtime_receipts.py' not in names:
                        errors.append('runtime missing from wheel')
                    meta = [n for n in names if n.endswith('.dist-info/METADATA')]
                    if len(meta) != 1 or f'Version: {version}\n' not in z.read(meta[0]).decode():
                        errors.append('wheel metadata version differs')
            elif path.name.endswith('.tar.gz'):
                with tarfile.open(path) as t:
                    members = t.getmembers()
                    names = [m.name for m in members]
                    if any(m.issym() or m.islnk() for m in members):
                        errors.append('links in source distribution')
                    if not any(n.endswith('/release_evidence/autocorrelation/verify.py') for n in names):
                        errors.append('source distribution missing witness verifier')
            else:
                continue
            for name in names:
                if unsafe_member(name) or nonpublic_member(name):
                    errors.append('unsafe distribution member: ' + name)
            artifacts.append({'name': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'members': len(names)})
        if not any(a['name'].endswith('.whl') for a in artifacts) or not any(a['name'].endswith('.tar.gz') for a in artifacts):
            errors.append('both wheel and source distribution required')
    return {'version': version, 'passed': not errors, 'errors': errors, 'artifacts': artifacts,
            'scope': 'Local metadata, links, package paths and evidence hashes; not external attestation or comprehensive security audit.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist', type=Path)
    args = parser.parse_args()
    report = check(dist=args.dist)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['passed'] else 1)
