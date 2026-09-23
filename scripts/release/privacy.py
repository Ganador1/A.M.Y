"""Privacy checks for publication derivatives; never print matched values."""
from __future__ import annotations
import json
from pathlib import Path
import re

SECRET = re.compile(r'(?<![A-Za-z0-9])(?:sk-[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{24,}|github_pat_[A-Za-z0-9_]{24,}|AIza[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,})')
HOME_PATH = re.compile(r'[/](?:Users|home)[/][^/\s<>"\'`]+')
VOLUME_PATH = re.compile(r'[/]Volumes[/][^/\n"\'`<>]+')
EMAIL = re.compile(r'[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')


def load_identifiers(path):
    return json.loads(Path(path).read_text()) if path else []


def sanitize(text, identifiers):
    changes = {}
    for value in sorted(set(identifiers), key=len, reverse=True):
        if not value:
            continue
        text, n = re.subn(re.escape(value), 'Ganador1', text, flags=re.I)
        if n:
            changes['private_identifier'] = changes.get('private_identifier', 0) + n
    text, n = HOME_PATH.subn('/home/amy', text)
    if n: changes['personal_home_path'] = n
    text, n = VOLUME_PATH.subn('/workspace', text)
    if n: changes['local_volume_path'] = n
    # A recognized credential never goes to a model or publication derivative.
    text, n = SECRET.subn('[REDACTED_CREDENTIAL]', text)
    if n: changes['credential_pattern'] = n
    return text, changes


def findings(text, identifiers):
    result=[]
    if any(v and re.search(re.escape(v),text,re.I) for v in identifiers):result.append('private_identifier')
    if SECRET.search(text):result.append('credential_pattern')
    if re.search(r'[/](?:Users|Volumes)[/][^/\s\"\'`<>]+',text):result.append('personal_machine_path')
    return result
