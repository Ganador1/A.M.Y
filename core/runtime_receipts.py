"""Persistent operational receipts. Process success never certifies a hypothesis."""
from __future__ import annotations
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import uuid
from core.execution_evidence import canonical, current_evidence, record_event


def action_succeeded(action):
    if not isinstance(action, dict):
        return False
    if type(action.get('success')) is bool:
        return action['success']
    result = action.get('result')
    return isinstance(result, dict) and result.get('success') is True


class ReceiptStore:
    """Append-only local chain; no external authentication or scientific authority."""
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else None
        self.index = {}
        self.tip = ''
        if self.path and self.path.exists():
            for line in self.path.read_bytes().splitlines():
                entry = json.loads(line)
                sha = entry.pop('sha256')
                if entry.get('previous_sha256') != self.tip or hashlib.sha256(canonical(entry)).hexdigest() != sha:
                    raise ValueError('runtime receipt journal integrity failed')
                receipt = entry['receipt']
                if not isinstance(receipt.get('experiment_id'), str) or receipt['experiment_id'] in self.index:
                    raise ValueError('invalid or duplicate runtime receipt ID')
                # Replayed summaries are not re-certified from a local cache.
                restored = copy.deepcopy(receipt)
                if restored.get('certificate_verified') is True:
                    restored['certificate_verified'] = False
                    restored.pop('verified_summary', None)
                    restored['verification_required_after_restart'] = True
                self.index[receipt['experiment_id']] = restored
                self.tip = sha

    def add(self, receipt):
        receipt = copy.deepcopy(receipt)
        identifier = receipt['experiment_id']
        if identifier in self.index:
            if self.index[identifier] != receipt:
                raise ValueError('runtime receipt ID reused with different content')
            return
        entry = {'previous_sha256': self.tip, 'receipt': receipt}
        sha = hashlib.sha256(canonical(entry)).hexdigest()
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open('ab') as f:
                f.write(canonical({**entry, 'sha256': sha}) + b'\n')
                f.flush()
                os.fsync(f.fileno())
        self.index[identifier] = receipt
        self.tip = sha
        record_event('memory.receipt_registered', {'receipt': receipt, 'local_journal_tip': sha})


def sandbox_receipt(result, code, *, action_type):
    """Index retained output, including failures, without inventing numerical truth."""
    run = current_evidence()
    identifier = result.get('experiment_id') or f'script_{uuid.uuid4().hex}'
    stdout, stderr = str(result.get('stdout', '')), str(result.get('stderr', ''))
    def text_view(text, limit):
        raw = text.encode()
        return {'text': text if len(raw) <= limit else None,
                'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
                'omitted_reason': None if len(raw) <= limit else 'exceeds_byte_limit'}
    evidence = copy.deepcopy(result.get('execution_evidence') or {})
    ref = evidence.get('stdout')
    return {'experiment_id': identifier, 'tool_name': 'sandbox_' + action_type,
            'execution_success': result.get('success') is True,
            'certificate_verified': False, 'interpretation_verified': False,
            'scientific_truth_verified': False, 'return_code': result.get('return_code'),
            'raw_output_sha256': ref['sha256'] if isinstance(ref, dict) else hashlib.sha256(stdout.encode()).hexdigest(),
            'original_input': text_view(code, 2048),
            'operational_observation': {'output': text_view(stdout, 4096), 'stderr': text_view(stderr, 2048),
                'scientific_truth_verified': False, 'scope': 'Recorded sandbox output; execution success does not verify the hypothesis.'},
            'nonfinite_output_requires_review': bool(re.search(r'\b(?:nan|inf)\b', stdout, re.I)),
            'retained_execution': evidence,
            'origin_run': str(run.path) if run else None,
            'provenance_path': result.get('provenance_path')}
