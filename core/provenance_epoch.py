"""Opt-in, isolated experiment journals for native runs.

The historical journal is referenced, never repaired or promoted into evidence.
One native run per process is required (as for the global provenance manager).
"""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path

from core import provenance
from core.execution_evidence import current_evidence, record_event


@contextmanager
def provenance_epoch(config):
    settings = config.get('evidence', {})
    explicit_root = settings.get('provenance_root')
    if not explicit_root and not settings.get('provenance_per_run', False):
        yield provenance.get_provenance_manager()
        return
    run = current_evidence()
    if not explicit_root and run is None:
        raise ValueError('provenance_per_run requires active execution evidence')
    root = Path(explicit_root) if explicit_root else run.path / 'experiments'
    previous = provenance.get_provenance_manager()
    if root.resolve() == previous.base_dir.resolve():
        raise ValueError('new provenance epoch cannot reuse the historical directory')
    # Exclusive creation prevents accidentally appending to a prior/parallel run.
    root.mkdir(parents=True, exist_ok=False)
    journal = previous.journal_path
    historical = {'path': str(journal.resolve()), 'exists': journal.is_file(),
                  'integrity_verified': None, 'verification_status': 'not_assessed',
                  'truth_verified': False, 'inherited_as_verified_evidence': False}
    if historical['exists']:
        raw = journal.read_bytes()
        historical.update(sha256=hashlib.sha256(raw).hexdigest(), byte_count=len(raw))
    summary = {'schema': 'amy.provenance_epoch.v1', 'root': str(root.resolve()),
               'historical_journal': historical,
               'scope': 'Independent new journal; historical validity is not asserted'}
    (root / 'epoch.json').write_text(json.dumps(summary, indent=2) + '\n')
    manager = provenance.ProvenanceManager(root)
    record_event('provenance.epoch', summary)
    provenance._provenance = manager
    try:
        yield manager
    finally:
        provenance._provenance = previous
