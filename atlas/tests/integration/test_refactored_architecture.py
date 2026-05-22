"""Smoke coverage for the refactored application architecture."""

from __future__ import annotations

import importlib


def test_main_refactored_exports_the_current_application():
    """`main_refactored` should remain a stable alias for the FastAPI app."""

    main_module = importlib.import_module("main")
    refactored_module = importlib.import_module("main_refactored")

    assert refactored_module.app is main_module.app
    assert refactored_module.app.title == "AXIOM ATLAS"
    assert hasattr(refactored_module.app, "router")


def test_main_refactored_exposes_core_system_routes():
    """The compatibility entrypoint should keep the base health endpoints."""

    app = importlib.import_module("main_refactored").app
    routes = {route.path for route in app.routes}

    assert {"/", "/health", "/status", "/metrics"}.issubset(routes)


def test_router_registry_metadata_is_coherent():
    """Registry metadata should reflect the configured routers accurately."""

    from app.routers.router_registry import ROUTER_CONFIG, get_router_info

    info = get_router_info()
    expected_domains = {"mathematics", "scientific", "infrastructure", "medical"}
    required_router_fields = {"name", "module", "router_var", "prefix", "tags", "lazy_load"}

    assert info["total_routers"] == sum(len(routers) for routers in ROUTER_CONFIG.values())
    assert expected_domains.issubset(set(info["domains"]))
    assert expected_domains.issubset(set(info["routers_by_domain"]))
    assert all(info["routers_by_domain"][domain] > 0 for domain in expected_domains)

    for routers in ROUTER_CONFIG.values():
        for router in routers:
            assert required_router_fields.issubset(router)


def test_router_registry_uses_lazy_loading_for_all_configured_routers():
    """The generated registry should keep lazy loading enabled across the board."""

    from app.routers.router_registry import ROUTER_CONFIG

    assert ROUTER_CONFIG
    assert all(router.get("lazy_load") is True for routers in ROUTER_CONFIG.values() for router in routers)


def test_modular_orchestration_components_import_cleanly():
    """The refactored orchestration modules should remain importable together."""

    from app.services.orchestration.execution import PipelineExecutor
    from app.services.orchestration.models import PipelineStatus, ResearchPipeline, TaskPriority
    from app.services.orchestration.templates import TEMPLATE_REGISTRY

    assert ResearchPipeline is not None
    assert PipelineExecutor is not None
    assert PipelineStatus.PENDING.value == "pending"
    assert TaskPriority.HIGH.value == 3
    assert "comprehensive_research" in TEMPLATE_REGISTRY
    assert callable(TEMPLATE_REGISTRY["comprehensive_research"])
