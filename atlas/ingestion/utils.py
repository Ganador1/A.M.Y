from __future__ import annotations
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Iterable
from time import sleep
from contextlib import suppress

def retry_call(fn, *, retries: int = 3, base_backoff: float = 1.0, factor: float = 2.0, exceptions: tuple[type[Exception], ...] = (Exception,), before_retry=None):
    """Retry genérico para funciones sincrónicas.
    fn: callable sin argumentos o con closure.
    before_retry: hook(op_attempt, exc, backoff_secs)
    """
    attempt = 0
    while True:
        try:
            return fn()
        except exceptions as exc:  # noqa: PERF203 (controlado)
            attempt += 1
            if attempt > retries:
                raise
            backoff = base_backoff * (factor ** (attempt - 1))
            if before_retry:
                with suppress(Exception):
                    before_retry(attempt, exc, backoff)
            sleep(backoff)

CACHE_DIR = Path("cache/RAW")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

STATE_FILE = Path("data/ingestion_state.json")
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

def normalize_text(t: str) -> str:
    t = t.replace('\n', ' ').strip()
    return ' '.join(t.split())

def canonical_id(title: str, year: int | None) -> str:
    key = (title.lower().strip() + (str(year) if year else "")).encode()
    return hashlib.sha1(key).hexdigest()

def write_cache(source: str, page_tag: str, data: Dict[str, Any]):
    day = datetime.utcnow().strftime('%Y%m%d')
    out_dir = CACHE_DIR / source / day
    out_dir.mkdir(parents=True, exist_ok=True)
    f = out_dir / f"{page_tag}.json"
    f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

class JsonlWriter:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
    def append_many(self, rows: Iterable[Dict[str, Any]]):
        with self.path.open('a', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')

def load_state() -> Dict[str, Any]:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    except (ValueError, json.JSONDecodeError):
        return {}

def save_state(state: Dict[str, Any]):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')

def log_event(source: str, event: str, **kwargs: Any):
    day = datetime.utcnow().strftime('%Y%m%d')
    lf = LOG_DIR / f"ingestion_{day}.log"
    record = {"ts": datetime.utcnow().isoformat(), "source": source, "event": event}
    record.update(kwargs)
    with lf.open('a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
