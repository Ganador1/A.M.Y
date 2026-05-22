from app.services.orchestration.management.multi_agent_coordinator import MultiAgentCoordinator


def test_audit_publication_claims_flags_unsupported_quantitative_results():
    coordinator = MultiAgentCoordinator.__new__(MultiAgentCoordinator)
    grounded_results = "\n".join(
        [
            "Resultados grounded de herramientas ejecutadas:",
            "- support_score real: 0.117",
            "- real_coverage: 0.333",
            "- QuantumComputingService/run_vqe estimó eigenvalue=0.408487",
        ]
    )
    draft = """
# Informe
## Resultados
El ansatz simétrico fue 42% mejor con p < 0.01 tras 30 réplicas.
## Conclusiones
La mejora quedó estadísticamente demostrada.
"""

    audit = coordinator._audit_publication_claims(draft, grounded_results)

    assert audit["suspect_sentence_count"] == 1
    assert "42%" in audit["suspect_sentences"][0]
