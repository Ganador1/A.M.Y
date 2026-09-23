from unittest.mock import Mock

from app.agents.contracts.conjecture_contracts import (
    ConjecturePayload,
    build_normalization_result,
    build_verification_result,
    NormalizationStatus,
    VerificationStatus,
)
from app.agents.bridges.agent1_agent2_bridge import Agent1Agent2Bridge
from app.services.theorem_proving.z3_smt_service import Z3SMTService
from app.mathlab.persistence.conjecture_persistence import ConjecturePersistenceService


def test_builders_default_status_mapping():
    n = build_normalization_result({})
    assert n.status == NormalizationStatus.ERROR
    v = build_verification_result({})
    assert v.status == VerificationStatus.UNKNOWN


def test_process_conjecture_flow():
    smt_service = Z3SMTService()
    persistence_service_mock = Mock(spec=ConjecturePersistenceService)
    bridge = Agent1Agent2Bridge(smt_service, persistence_service_mock)
    payload = ConjecturePayload(id="c1", statement="x > 0", domain={})
    result = bridge.process_conjecture(payload)
    assert result.conjecture.id == "c1"
    assert result.normalization.status in {NormalizationStatus.OK, NormalizationStatus.UNAVAILABLE, NormalizationStatus.ERROR}
    assert result.elapsed_ms >= 0

    # If normalization succeeded, verification status should be in expected set
    if result.normalization.status == NormalizationStatus.OK:
        assert result.verification.status in {VerificationStatus.PROVEN, VerificationStatus.REFUTED, VerificationStatus.UNKNOWN}
    else:
        assert result.verification.status in {VerificationStatus.NORMALIZATION_FAILED, VerificationStatus.Z3_UNAVAILABLE, VerificationStatus.ERROR, VerificationStatus.UNKNOWN}

    # Verify that persistence was called
    persistence_service_mock.update_conjecture_with_verification.assert_called_once_with(
        conjecture_id="c1",
        verification_result=result.model_dump()
    )
