"""Build a fresh privacy-reviewed source snapshot without Git or private run data."""
from __future__ import annotations
import argparse,hashlib,json,re,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.release.privacy import findings,load_identifiers,sanitize
from scripts.release.check_release import unsafe_member

ROOT_FILES={'amy.py','pyproject.toml','uv.lock','requirements.txt','LICENSE','CITATION.cff','README.md','README_PUBLIC.md','SCIENCE_MANIFESTO.md','ATLAS_TOOL_GUIDE.md','RESEARCH.md','RELEASE_CHECKLIST.md','CONTRIBUTING.md','ENVIRONMENT.md','SECURITY.md','USE_POLICY.md','CHANGELOG.md','MANIFEST.in','pytest.ini','conftest.py','.env.example','config.release.yaml','.gitignore'}
PACKAGES=('core','cognition','memory','senses','skills','communication','evolution','sandbox','tests','benchmarks','scripts/release')
LABS=('experiments/multimodel_recovery_20260919','experiments/recovery_campaign_20260919')
EXCLUDED={'__pycache__','.git','.venv','node_modules','output','data','runs','studies'}

def candidates():
    selected={ROOT/n for n in ROOT_FILES if (ROOT/n).is_file()}
    for rel in PACKAGES+LABS+('atlas/app',):
        for p in (ROOT/rel).rglob('*'):
            if p.is_file() and not p.is_symlink() and p.suffix in {'.py','.md','.json','.yaml','.yml','.txt'} and not any(x in EXCLUDED for x in p.relative_to(ROOT/rel).parts):selected.add(p)
    for rel in ('docs/releases','docs/publication','docs/en','release_evidence'):
        for p in (ROOT/rel).rglob('*'):
            if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts:selected.add(p)
    for rel in ('docs/PROJECT_MAP.md','docs/ENGLISH_MANUALS.md','docs/DETECTOR_CHARACTERIZATION.md','atlas/README.md','atlas/LICENSE','atlas/pyproject.toml','sandbox/Dockerfile','.github/workflows/release-hygiene.yml','.github/workflows/public-candidate.yml','atlas/kubernetes/secret.example.yml','scripts/run/run_receipt_memory_validation.py','scripts/run/run_native_science_benchmark.py','scripts/verify/package_native_science.py','scripts/verify/score_scientific_assessments.py','scripts/verify/summarize_native_benchmark.py','scripts/verify/verify_native_science_run.py','scripts/diagnostics/verify_secret_hygiene.py','scripts/diagnostics/verify_atlas_tools.py'):
        p=ROOT/rel
        if p.is_file():selected.add(p)
    for pat in ('*.py','requirements*.txt'):
        selected.update(p for p in (ROOT/'atlas').glob(pat) if p.is_file())
    # Local policy files required by the Atlas laboratory; environment credentials excluded.
    for rel in ('atlas/config/ethics_policy.yaml','atlas/config/compliance_policy.yaml'):
        p=ROOT/rel
        if p.is_file():selected.add(p)
    test_names={'test_sandbox_isolation.py','test_release_http.py','test_model_broker.py','test_science_gates.py','test_runtime_recovery.py','test_goal_focus.py','test_native_session_finish.py','test_experiment_receipt_memory.py','test_execution_evidence.py','test_provenance_epoch.py','test_merkle_tree.py','test_decision_schema.py','test_sandbox_cancellation.py','test_learning_wired.py','test_consolidation_wired.py','test_heartbeat_paper_pipeline.py','test_release_atlas_syntax.py','test_release_privacy.py','test_public_release_hygiene.py','test_cli_config.py','test_installed_atlas_worker.py','test_multimodel_recovery_campaign.py','test_multimodel_recovery_labs.py','test_multimodel_worker_subset.py','conftest.py'}
    selected = {p for p in selected if not unsafe_member(str(p.relative_to(ROOT)))}
    return sorted(p for p in selected if p.relative_to(ROOT).parts[0]!='tests' or p.name in test_names or 'fixtures' in p.relative_to(ROOT).parts)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--private-identifiers',type=Path,required=True);args=parser.parse_args()
    out=args.output.resolve()
    if out.exists():raise SystemExit('output must be a new directory')
    ids=load_identifiers(args.private_identifiers)
    credentials=[]
    for p in (ROOT/'.env',ROOT/'atlas/.env'):
        if not p.exists():continue
        for line in p.read_text().splitlines():
            if '=' not in line or line.lstrip().startswith('#'):continue
            key,value=line.split('=',1);value=value.strip().strip('\"\'')
            if re.search(r'key|secret|token|password',key,re.I) and len(value)>=12 and not re.search(r'example|your_|placeholder|changeme',value,re.I):credentials.append(value)
    out.mkdir(parents=True)
    records=[]
    for p in candidates():
        rel=p.relative_to(ROOT)
        if any(part.startswith('.env') and part!='.env.example' for part in rel.parts) or p.suffix in {'.key','.pem','.enc'}:raise ValueError('sensitive candidate filename')
        try:original=p.read_text()
        except UnicodeError:raise ValueError('unexpected binary source member: '+str(rel))
        text,changes=sanitize(original,ids)
        for value in credentials:
            if value in text:text=text.replace(value,'[REDACTED_CREDENTIAL]');changes['known_credential']=changes.get('known_credential',0)+1
        text,n=re.subn(r'[\w.+-]+@(?:gmail|hotmail|outlook|yahoo|icloud|protonmail|proton)\.[A-Za-z.]+','contact@example.invalid',text,flags=re.I)
        if n:changes['personal_email']=n
        if findings(text,ids):raise ValueError('privacy finding in '+str(rel))
        target=out/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
        records.append({'path':str(rel),'sha256':hashlib.sha256(text.encode()).hexdigest(),'privacy_substitutions':changes})
    shutil.copy2(out/'config.release.yaml',out/'config.yaml')
    records.append({'path':'config.yaml','sha256':hashlib.sha256((out/'config.yaml').read_bytes()).hexdigest(),'privacy_substitutions':{'portable_default':1}})
    # Source bytes may change during privacy substitutions: recompute derivative manifests.
    for rel in ('release_evidence/autocorrelation','release_evidence/runtime'):
        base=out/rel
        files=[p for p in base.rglob('*') if p.is_file() and p.name!='MANIFEST.json']
        (base/'MANIFEST.json').write_text(json.dumps({'scope':'Public derivative integrity; no external signatures','sha256':{str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}},indent=2)+'\n')
    for record in records:record['sha256']=hashlib.sha256((out/record['path']).read_bytes()).hexdigest()
    (out/'PUBLIC_SOURCE_MANIFEST.json').write_text(json.dumps({'scope':'Curated privacy-reviewed snapshot, no Git history or private native trajectories. May contain historical comments and literal examples in their original language.','files':records},indent=2)+'\n')
    print(json.dumps({'files':len(records),'changed_for_privacy':sum(bool(x['privacy_substitutions']) for x in records),'output_name':out.name}))
if __name__=='__main__':main()
