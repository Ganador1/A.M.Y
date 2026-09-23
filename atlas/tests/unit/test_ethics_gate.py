"""
Tests completos para Ethics Gate - Implementación real
"""

import pytest
import tempfile
import os
from datetime import datetime, timezone
from app.compliance.ethics_gate import EthicsGate, ExperimentRequest, EthicsDecision
from app.compliance.ethics_policy import EthicsPolicyManager
from app.compliance.ethics_decision_store import EthicsDecisionStore


class TestEthicsGate:
    """Tests para la implementación completa del Ethics Gate"""

    def setup_method(self):
        """Setup para cada test"""
        self.gate = EthicsGate()
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()

    def teardown_method(self):
        """Cleanup después de cada test"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_low_risk_experiment_allowed(self):
        """Test: Experimento de bajo riesgo debe ser aprobado"""
        req = ExperimentRequest(
            domain="algebra",
            description="Operación simbólica básica",
            data_sensitivity="none",
            declared_intent="research"
        )
        
        decision = self.gate.evaluate(req)
        
        assert decision.allowed is True
        assert decision.level == "LOW"
        assert decision.risk_score <= 3
        assert decision.requires_signature is False
        assert decision.decision_id != ""
        assert decision.timestamp is not None

    def test_high_risk_domain_blocked(self):
        """Test: Dominio de alto riesgo debe ser bloqueado"""
        req = ExperimentRequest(
            domain="synthetic_biology",
            description="Diseño de organismo sintético",
            data_sensitivity="none",
            declared_intent="research"
        )
        
        decision = self.gate.evaluate(req)
        
        assert decision.allowed is False
        assert decision.level in ["HIGH", "CRITICAL"]
        assert decision.risk_score >= 9
        assert decision.requires_signature is True
        assert len(decision.escalation_reasons) > 0
        assert len(decision.recommended_actions) > 0

    def test_blocked_keywords_rejection(self):
        """Test: Keywords bloqueadas deben causar rechazo automático"""
        req = ExperimentRequest(
            domain="algebra",
            description="Diseño de bioweapon para ataque",
            data_sensitivity="none",
            declared_intent="research"
        )
        
        decision = self.gate.evaluate(req)
        
        assert decision.allowed is False
        assert decision.level == "CRITICAL"
        assert decision.risk_score == 20
        assert "Blocked keywords detected" in decision.reason
        assert any("bioweapon" in reason for reason in decision.escalation_reasons)

    def test_sensitive_keywords_escalation(self):
        """Test: Keywords sensibles deben incrementar el score"""
        req = ExperimentRequest(
            domain="computational_biology",
            description="Análisis de virus patógeno con datos de pacientes",
            data_sensitivity="high",
            declared_intent="research",
            keywords=["virus", "pathogen", "patient"]
        )
        
        decision = self.gate.evaluate(req)
        
        assert decision.risk_score >= 7  # Base domain + data + keywords
        assert len(decision.escalation_reasons) > 0
        assert any("Sensitive keywords detected" in reason for reason in decision.escalation_reasons)

    def test_data_sensitivity_scoring(self):
        """Test: Sensibilidad de datos debe afectar el score"""
        # Test con datos críticos
        req_critical = ExperimentRequest(
            domain="algebra",
            description="Operación básica",
            data_sensitivity="critical",
            declared_intent="research"
        )
        
        decision_critical = self.gate.evaluate(req_critical)
        
        # Test con datos normales
        req_normal = ExperimentRequest(
            domain="algebra",
            description="Operación básica",
            data_sensitivity="none",
            declared_intent="research"
        )
        
        decision_normal = self.gate.evaluate(req_normal)
        
        assert decision_critical.risk_score > decision_normal.risk_score
        assert decision_critical.risk_score >= 8  # critical data weight

    def test_intent_scoring(self):
        """Test: Intención declarada debe afectar el score"""
        # Test con intención dual-use
        req_dual_use = ExperimentRequest(
            domain="computational_chemistry",
            description="Análisis químico",
            data_sensitivity="none",
            declared_intent="dual_use"
        )
        
        decision_dual_use = self.gate.evaluate(req_dual_use)
        
        # Test con intención de investigación
        req_research = ExperimentRequest(
            domain="computational_chemistry",
            description="Análisis químico",
            data_sensitivity="none",
            declared_intent="research"
        )
        
        decision_research = self.gate.evaluate(req_research)
        
        assert decision_dual_use.risk_score > decision_research.risk_score
        assert decision_dual_use.risk_score >= 5  # dual_use intent weight

    def test_signature_requirements(self):
        """Test: Niveles HIGH y CRITICAL deben requerir firma"""
        # Test HIGH level
        req_high = ExperimentRequest(
            domain="genomics",
            description="Análisis genómico",
            data_sensitivity="high",
            declared_intent="research"
        )
        
        decision_high = self.gate.evaluate(req_high)
        
        if decision_high.level == "HIGH":
            assert decision_high.requires_signature is True
        
        # Test CRITICAL level
        req_critical = ExperimentRequest(
            domain="synthetic_biology",
            description="Diseño de organismo",
            data_sensitivity="critical",
            declared_intent="dual_use"
        )
        
        decision_critical = self.gate.evaluate(req_critical)
        
        if decision_critical.level == "CRITICAL":
            assert decision_critical.requires_signature is True

    def test_decision_storage(self):
        """Test: Decisiones deben almacenarse en base de datos"""
        req = ExperimentRequest(
            domain="algebra",
            description="Test decision storage",
            data_sensitivity="none",
            declared_intent="research"
        )
        
        decision = self.gate.evaluate(req)
        
        # Verificar que la decisión se almacenó
        stored_decision = self.gate.decision_store.get_decision(decision.decision_id)
        assert stored_decision is not None
        assert stored_decision.decision_id == decision.decision_id
        assert stored_decision.domain == req.domain
        assert stored_decision.allowed == decision.allowed

    def test_decision_history(self):
        """Test: Historial de decisiones debe ser recuperable"""
        # Crear varias decisiones
        domains = ["algebra", "computational_biology", "synthetic_biology"]
        decisions = []
        
        for domain in domains:
            req = ExperimentRequest(
                domain=domain,
                description=f"Test for {domain}",
                data_sensitivity="none",
                declared_intent="research"
            )
            decision = self.gate.evaluate(req)
            decisions.append(decision)
        
        # Recuperar historial
        history = self.gate.get_decision_history(limit=10)
        assert len(history) >= len(decisions)
        
        # Verificar que nuestras decisiones están en el historial
        decision_ids = {d.decision_id for d in decisions}
        history_ids = {h.decision_id for h in history}
        assert decision_ids.issubset(history_ids)

    def test_statistics_generation(self):
        """Test: Estadísticas deben generarse correctamente"""
        # Crear decisiones de diferentes niveles
        test_cases = [
            ("algebra", "none", "research", "LOW"),
            ("genomics", "high", "research", "HIGH"),
            ("synthetic_biology", "critical", "dual_use", "CRITICAL")
        ]
        
        for domain, sensitivity, intent, expected_level in test_cases:
            req = ExperimentRequest(
                domain=domain,
                description=f"Test statistics for {domain}",
                data_sensitivity=sensitivity,
                declared_intent=intent
            )
            self.gate.evaluate(req)
        
        # Obtener estadísticas
        stats = self.gate.get_statistics()
        
        assert "total" in stats
        assert "blocked" in stats
        assert "blocked_rate" in stats
        assert "by_level" in stats
        assert "by_domain" in stats
        assert stats["total"] >= len(test_cases)

    def test_error_handling(self):
        """Test: Manejo de errores debe ser robusto"""
        # Test con request inválido
        req = ExperimentRequest(
            domain="",  # Dominio vacío
            description="",
            data_sensitivity="invalid",  # Sensibilidad inválida
            declared_intent="invalid"  # Intención inválida
        )
        
        decision = self.gate.evaluate(req)
        
        # Debe retornar una decisión válida (probablemente conservadora)
        assert isinstance(decision, EthicsDecision)
        assert decision.decision_id != ""
        assert decision.timestamp is not None

    def test_concurrent_evaluations(self):
        """Test: Evaluaciones concurrentes deben funcionar"""
        import threading
        import time
        
        results = []
        
        def evaluate_experiment(domain, description):
            req = ExperimentRequest(
                domain=domain,
                description=description,
                data_sensitivity="none",
                declared_intent="research"
            )
            decision = self.gate.evaluate(req)
            results.append(decision)
        
        # Crear múltiples threads
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=evaluate_experiment,
                args=(f"domain_{i}", f"Test concurrent {i}")
            )
            threads.append(thread)
        
        # Ejecutar concurrentemente
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verificar que todas las evaluaciones se completaron
        assert len(results) == 5
        for result in results:
            assert isinstance(result, EthicsDecision)
            assert result.decision_id != ""

    def test_policy_validation(self):
        """Test: Validación de política debe funcionar"""
        policy_manager = EthicsPolicyManager()
        errors = policy_manager.validate_policy()
        
        # La política por defecto debe ser válida
        assert len(errors) == 0

    def test_domain_weight_retrieval(self):
        """Test: Pesos de dominio deben recuperarse correctamente"""
        policy_manager = EthicsPolicyManager()
        
        # Test dominios conocidos
        assert policy_manager.get_domain_weight("algebra") == 0
        assert policy_manager.get_domain_weight("synthetic_biology") == 9
        assert policy_manager.get_domain_weight("biosecurity_assessment") == 10
        
        # Test dominio desconocido (debe retornar peso por defecto)
        assert policy_manager.get_domain_weight("unknown_domain") == 1

    def test_keyword_detection(self):
        """Test: Detección de keywords debe funcionar"""
        policy_manager = EthicsPolicyManager()
        
        # Test keywords bloqueadas
        blocked_keywords = policy_manager.get_blocked_keywords()
        assert "bioweapon" in blocked_keywords
        assert "dual-use weaponization" in blocked_keywords
        
        # Test keywords sensibles
        sensitive_keywords = policy_manager.get_sensitive_keywords()
        assert "biology" in sensitive_keywords
        assert "pathogen" in sensitive_keywords["biology"]
        assert "chemistry" in sensitive_keywords
        assert "toxic" in sensitive_keywords["chemistry"]

    def test_threshold_retrieval(self):
        """Test: Umbrales deben recuperarse correctamente"""
        policy_manager = EthicsPolicyManager()
        thresholds = policy_manager.get_thresholds()
        
        assert thresholds.low == 3
        assert thresholds.medium == 7
        assert thresholds.high == 11
        assert thresholds.critical == 15
        assert thresholds.low < thresholds.medium < thresholds.high < thresholds.critical


class TestEthicsDecisionStore:
    """Tests para el almacén de decisiones éticas"""

    def setup_method(self):
        """Setup para cada test"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.store = EthicsDecisionStore(self.temp_db.name)

    def teardown_method(self):
        """Cleanup después de cada test"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_decision_storage_and_retrieval(self):
        """Test: Almacenamiento y recuperación de decisiones"""
        from app.compliance.ethics_decision_store import EthicsDecisionRecord
        
        record = EthicsDecisionRecord(
            decision_id="test-123",
            timestamp=datetime.now(timezone.utc),
            domain="test_domain",
            description="Test decision",
            decision="LOW",
            risk_score=2,
            allowed=True,
            requires_signature=False,
            escalation_reasons=["Test reason"],
            recommended_actions=["Test action"]
        )
        
        # Almacenar
        self.store.store_decision(record)
        
        # Recuperar
        retrieved = self.store.get_decision("test-123")
        assert retrieved is not None
        assert retrieved.decision_id == "test-123"
        assert retrieved.domain == "test_domain"
        assert retrieved.allowed is True

    def test_statistics_generation(self):
        """Test: Generación de estadísticas"""
        from app.compliance.ethics_decision_store import EthicsDecisionRecord
        
        # Crear varias decisiones
        decisions = [
            ("test-1", "LOW", True),
            ("test-2", "MEDIUM", True),
            ("test-3", "HIGH", False),
            ("test-4", "CRITICAL", False)
        ]
        
        for decision_id, level, allowed in decisions:
            record = EthicsDecisionRecord(
                decision_id=decision_id,
                timestamp=datetime.now(timezone.utc),
                domain="test_domain",
                description=f"Test {decision_id}",
                decision=level,
                risk_score=5,
                allowed=allowed,
                requires_signature=level in ["HIGH", "CRITICAL"],
                escalation_reasons=[],
                recommended_actions=[]
            )
            self.store.store_decision(record)
        
        # Obtener estadísticas
        stats = self.store.get_statistics()
        
        assert stats["total"] == 4
        assert stats["blocked"] == 2
        assert stats["blocked_rate"] == 50.0
        assert "LOW" in stats["by_level"]
        assert "CRITICAL" in stats["by_level"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
