"""Public source must contain runnable defaults and omit working notes/caches."""
from pathlib import Path
import json
import tomllib
import yaml
from scripts.release.export_public_source import candidates, ROOT
from scripts.release.check_release import nonpublic_member


def test_archive_content_filter_preserves_evidence_and_rejects_working_files():
    for path in ('amy/RELEASE_CHECKLIST.md', 'amy/docs/releases/VALIDATION.md',
                 'amy/docs/publication/PUBLICATION_PLAN.md',
                 'amy/docs/en/atlas/docs/guides/paper_failed.md',
                 'amy/sandbox/scripts/.cache/model/config.json',
                 'amy/atlas/brian2.py', 'amy/atlas/rdkit_shadow_bak.py'):
        assert nonpublic_member(path), path
    for path in ('amy/release_evidence/runtime/verify.py',
                 'amy/scripts/release/public_content.json',
                 'amy/docs/REPRODUCIBILITY.md', 'amy/atlas/app/core/config.py'):
        assert not nonpublic_member(path), path


def test_export_contains_runtime_assets_and_no_internal_work_products():
    paths={str(p.relative_to(ROOT)) for p in candidates()}
    assert {'atlas/config/agents.yaml','atlas/config/models.yaml',
            'atlas/config/external_science.yaml','atlas/config/prompts/hypothesis_agent.yaml',
            'atlas/config/policy_engine_config.yaml','docs/REPRODUCIBILITY.md',
            'atlas/improvements/real_scientific_databases.py',
            'atlas/alembic/env.py','atlas/app/static/scientific_ui.html',
            'atlas/tests/unit/orchestration/test_tool_evidence_external_science.py',
            'tests/test_grounding_repair.py','scripts/examples/run_math_example.py',
            'atlas/.dockerignore'} <= paths
    assert 'RELEASE_CHECKLIST.md' not in paths
    for path in paths:
        assert not path.startswith(('docs/releases/','docs/publication/','sandbox/scripts/'))
        assert '/guides/archive/' not in path and '/guides/paper_' not in path
    for name in ('brian2.py','libsbml.py','seaborn.py','rdkit_shadow_bak.py'):
        assert 'atlas/'+name not in paths


def test_atlas_metadata_is_valid_and_matches_license():
    project=tomllib.loads((ROOT/'atlas/pyproject.toml').read_text())['project']
    assert project['authors']==[{'name':'Ganador1'}]
    assert project['license']['text']=='Apache-2.0'
    assert 'Apache License' in (ROOT/'atlas/LICENSE').read_text()


def test_documented_public_commands_have_their_inputs():
    for name in ('tests/test_installed_atlas_worker.py','tests/test_decision_envelope.py',
                 'experiments/multimodel_recovery_20260919/campaign.py',
                 'release_evidence/runtime/cloud-model-catalog.json'):
        assert (ROOT/name).is_file(),name
    for name in ('agents.yaml','models.yaml','policy_engine_config.yaml','external_science.yaml'):
        assert isinstance(yaml.safe_load((ROOT/'atlas/config'/name).read_text()),dict)
