"""Native startup journal isolation with no inference and no global writes."""
import json
from types import SimpleNamespace
import pytest
from core import provenance
from core.execution_evidence import EvidenceRun, verify_run
from core.provenance_epoch import provenance_epoch
from amy import AMY


@pytest.fixture
def historical(tmp_path, monkeypatch):
    manager = provenance.ProvenanceManager(tmp_path / 'historical')
    manager.journal_path.write_text('deliberately corrupted historical fixture\n')
    monkeypatch.setattr(provenance, '_provenance', manager)
    return manager


def test_default_preserves_runner_override(historical):
    with provenance_epoch({'evidence': {}}) as manager:
        assert manager is historical
        assert provenance.get_provenance_manager() is historical


@pytest.mark.asyncio
async def test_native_startup_isolates_and_retains_historical_link(tmp_path, historical):
    run = EvidenceRun(tmp_path / 'run', metadata={'origin': 'test fixture'})
    old_bytes = historical.journal_path.read_bytes()
    async def body():
        manager = provenance.get_provenance_manager()
        assert manager.base_dir == run.path / 'experiments'
        manager.record_execution('fixture', 'input', 'output', True, 0, experiment_id='new_fixture')
        assert manager.verify_journal()['integrity_verified'] is True
    amy = SimpleNamespace(config={'evidence': {'provenance_per_run': True}}, _start_impl=body)
    with run.activate():
        await AMY._start_with_provenance(amy)
    assert provenance.get_provenance_manager() is historical
    assert historical.journal_path.read_bytes() == old_bytes
    summary = json.loads((run.path / 'experiments' / 'epoch.json').read_text())
    assert summary['historical_journal']['integrity_verified'] is None
    assert summary['historical_journal']['inherited_as_verified_evidence'] is False
    assert verify_run(run.path, expected_root=run.seal()['root_sha256'])['integrity_verified']


def test_explicit_root_and_exception_restore_manager(tmp_path, historical):
    target = tmp_path / 'explicit'
    with pytest.raises(RuntimeError):
        with provenance_epoch({'evidence': {'provenance_root': str(target)}}):
            assert provenance.get_provenance_manager().base_dir == target
            raise RuntimeError('intentional fixture interruption')
    assert provenance.get_provenance_manager() is historical
    with pytest.raises(FileExistsError):
        with provenance_epoch({'evidence': {'provenance_root': str(target)}}):
            pass


def test_per_run_requires_evidence_and_rejects_historical_root(historical):
    with pytest.raises(ValueError, match='active execution evidence'):
        with provenance_epoch({'evidence': {'provenance_per_run': True}}):
            pass
    with pytest.raises(ValueError, match='historical directory'):
        with provenance_epoch({'evidence': {'provenance_root': str(historical.base_dir)}}):
            pass


@pytest.mark.asyncio
async def test_public_start_with_active_evidence_preserves_explicit_runner_manager(tmp_path, historical):
    from types import MethodType
    run = EvidenceRun(tmp_path / 'external-run', metadata={'origin': 'test fixture'})
    calls = []
    async def body():
        calls.append(provenance.get_provenance_manager())
    amy = SimpleNamespace(config={'evidence': {'enabled': True}}, _start_impl=body)
    amy._start_with_provenance = MethodType(AMY._start_with_provenance, amy)
    with run.activate():
        await AMY.start(amy)
    assert calls == [historical]
    assert not (run.path / 'experiments').exists()
