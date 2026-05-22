from __future__ import annotations
import subprocess
import sys
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
import asyncio
from typing import Dict, Any, List, Optional, Tuple

# Intentamos importar el servicio de versionado; si falla, seguimos sin bloquear el pipeline
try:
    from app.services.data_versioning import DataVersioningService
except Exception:
    DataVersioningService = None  # type: ignore

# Rutas de artefactos conocidas del pipeline v4
ENRICHED = Path('data/plausibility_training_v4_enriched.jsonl')
ENRICHED_WITH_YEAR = Path('data/plausibility_training_v4_enriched_with_year.jsonl')
EMBEDDINGS = Path('data/plausibility_training_v4_embeddings.parquet')
WEAK = Path('data/plausibility_training_v4_weak_labels.parquet')
ENSEMBLE_WEAK = Path('data/plausibility_training_v4_weak_labels_ensemble.parquet')
MODEL = Path('models/plausibility_v4_rf.pkl')
CV_JSON = Path('models/plausibility_v4_cv_metrics.json')
HEURISTICS = Path('data/heuristics_tuned_v4.json')
META_JSON = Path('models/pipeline_metadata_v4.json')
PLATT = Path('models/calibrated/platt_calibrator.pkl')
ISO = Path('models/calibrated/isotonic_calibrator.pkl')
ARTIFACT_MAP = Path('models/artifact_map.json')
# Targets críticos con enforcement de DVC
CRITICAL_ARTIFACTS = {ENRICHED, EMBEDDINGS, WEAK, ENSEMBLE_WEAK}

PROV_OUT = Path('data/provenance_report.json')
DAG_OUT = Path('data/pipeline_dag_v4.json')
LOOP_OUT = Path('reports/scientific_loop_report.json')


def sha256_file(path: Path) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


class ProvenanceBuilder:
    def __init__(self, agent_name: str = 'AXIOM Pipeline', agent_id: Optional[str] = None):
        self.agent_id = agent_id or f"agent:{agent_name.lower().replace(' ', '_')}"
        self.agent = {
            self.agent_id: {
                'type': 'prov:Agent',
                'name': agent_name
            }
        }
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.activities: Dict[str, Dict[str, Any]] = {}
        self.relations: Dict[str, List[Dict[str, Any]]] = {
            'wasGeneratedBy': [],
            'used': [],
            'wasAssociatedWith': []
        }
        self._ent_counter = 0
        self._act_counter = 0

    def _new_entity_id(self, name: str) -> str:
        self._ent_counter += 1
        return f"entity:{name}:{self._ent_counter}"

    def _new_activity_id(self, name: str) -> str:
        self._act_counter += 1
        return f"activity:{name}:{self._act_counter}"

    def add_entity(self, path: Path, attrs: Optional[Dict[str, Any]] = None) -> str:
        name = path.name
        eid = self._new_entity_id(name)
        self.entities[eid] = {
            'type': 'prov:Entity',
            'name': name,
            'path': str(path),
            'exists': path.exists(),
            'sha256': sha256_file(path),
        }
        if attrs:
            self.entities[eid].update(attrs)
        return eid

    def add_activity(self, name: str, start: datetime, end: datetime, attrs: Optional[Dict[str, Any]] = None) -> str:
        aid = self._new_activity_id(name)
        self.activities[aid] = {
            'type': 'prov:Activity',
            'name': name,
            'startedAtTime': start.isoformat() + 'Z',
            'endedAtTime': end.isoformat() + 'Z'
        }
        if attrs:
            self.activities[aid].update(attrs)
        # Association to pipeline agent
        self.relations['wasAssociatedWith'].append({'activity': aid, 'agent': self.agent_id})
        return aid

    def link_used(self, activity_id: str, entity_id: str):
        self.relations['used'].append({'activity': activity_id, 'entity': entity_id})

    def link_generated_by(self, entity_id: str, activity_id: str):
        self.relations['wasGeneratedBy'].append({'entity': entity_id, 'activity': activity_id})

    def to_prov_json(self) -> Dict[str, Any]:
        prov = {
            'agent': self.agent,
            'entity': self.entities,
            'activity': self.activities,
            'wasGeneratedBy': self.relations['wasGeneratedBy'],
            'used': self.relations['used'],
            'wasAssociatedWith': self.relations['wasAssociatedWith'],
            'prefix': {
                'prov': 'http://www.w3.org/ns/prov#'
            }
        }
        # graph hash for checkpointing
        graph_bytes = json.dumps(prov, sort_keys=True).encode('utf-8')
        prov['graph_sha256'] = hashlib.sha256(graph_bytes).hexdigest()
        prov['generatedAt'] = datetime.utcnow().isoformat() + 'Z'
        return prov


BASE_STEPS = [
    ['python', 'update_dataset.py', '--rows', '50', '--max-batches', '1', '--semantic-limit', '10', '--semantic-batches', '1'],
    ['python', 'enrich_dataset_v4.py'],
]

POST_FETCH_STEPS = [
    ['python', 'generate_embeddings_v4.py'],
    ['python', 'build_faiss_index_v4.py'],
    ['python', 'cluster_embeddings_v4.py', '--k', '20'],
    ['python', 'weak_label_v4.py'],
    ['python', 'weak_label_alt_v4.py'],
    ['python', 'weak_label_ensemble_v4.py'],
    ['python', 'train_plausibility_model_v4.py'],
    ['python', 'pipeline_metadata_v4.py'],
]

def build_steps():
    steps = list(BASE_STEPS)
    if os.environ.get('FETCH_PUBLICATION_YEARS') == '1':
        # Ejecutar fetch externo de años antes de embeddings para que futuros features temporal-aware sean posibles
        steps.append(['python', 'fetch_publication_years_v1.py'])
        # Si se generó enriched con años, opcionalmente sustituir archivo original (no lo borramos, sólo informamos)
    steps.extend(POST_FETCH_STEPS)
    return steps


async def _version_if_exists(svc: Any, path: Path, tags: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    if not path.exists() or DataVersioningService is None or svc is None:
        return None
    req = {
        'data_path': str(path),
        'metadata': {
            'pipeline': 'v4',
            'component': 'orchestrator',
        },
        'tags': tags or [],
        'allow_external_path': True
    }
    try:
        result = await svc.version_data(req)  # type: ignore
        return result if isinstance(result, dict) else None
    except Exception:
        return None


def _candidate_artifacts() -> List[Path]:
    cands = [ENRICHED, ENRICHED_WITH_YEAR, EMBEDDINGS, WEAK, ENSEMBLE_WEAK, MODEL, CV_JSON, HEURISTICS, META_JSON, ARTIFACT_MAP, PLATT, ISO]
    return [p for p in cands]


def run_steps():
    steps = build_steps()

    # Inicializar PROV y DAG
    prov = ProvenanceBuilder('AXIOM Scientific Pipeline')
    dag_nodes: List[Dict[str, Any]] = []
    dag_edges: List[Tuple[str, str]] = []

    # Instanciar servicio de versionado si disponible
    svc = None
    if DataVersioningService is not None:
        try:
            svc = DataVersioningService()
        except Exception:
            svc = None

    for cmd in steps:
        name = cmd[1] if len(cmd) > 1 else 'unknown'
        node_id = f"node:{name}:{len(dag_nodes)+1}"
        print(f"\n=== Ejecutando: {' '.join(cmd)} ===")
        start = datetime.utcnow()
        r = subprocess.run(cmd, text=True, check=False)
        end = datetime.utcnow()

        status = 'success' if r.returncode == 0 else 'failure'
        dag_nodes.append({'id': node_id, 'name': name, 'cmd': cmd, 'status': status, 'started_at': start.isoformat()+'Z', 'ended_at': end.isoformat()+'Z'})
        if len(dag_nodes) > 1:
            dag_edges.append((dag_nodes[-2]['id'], node_id))

        # Registrar actividad en PROV
        act = prov.add_activity(name=name, start=start, end=end, attrs={'returncode': r.returncode})

        # Escanear artefactos candidatos y vincular
        produced_entities: List[str] = []
        for p in _candidate_artifacts():
            if p.exists():
                eid = prov.add_entity(p)
                prov.link_generated_by(eid, act)
                produced_entities.append(eid)
                # Versionar si es posible
                if svc is not None:
                    res_ok = False
                    try:
                        res = asyncio.run(_version_if_exists(svc, p, tags=[name]))
                        if isinstance(res, dict) and res.get('success'):
                            # Añadir info de versión al entity
                            self_entity = prov.entities.get(eid, {})
                            self_entity['version_id'] = res.get('version_id')
                            res_ok = True
                    except Exception:
                        res_ok = False
                    # Enforcement para targets críticos: si el snapshot falla, abortar
                    if p in CRITICAL_ARTIFACTS and not res_ok:
                        print(f"❌ DVC enforcement falló para {p}. Abortando pipeline.")
                        _persist_prov_and_dag(prov, dag_nodes, dag_edges)
                        sys.exit(1)

        # Marcar usos básicos (heurística: actividad usa entidades previas inmediatas)
        if len(dag_nodes) > 1:
            # Vincular a todas las entidades producidas por el paso anterior
            prev_node_idx = len(dag_nodes) - 2
            prev_acts = list(prov.activities.keys())
            if prev_acts:
                # Tomamos la última actividad como anterior
                prev_act_id = prev_acts[-2] if len(prev_acts) >= 2 else prev_acts[0]
                # Todas las entidades actuales se consideran usadas por el siguiente paso
                for eid in produced_entities:
                    prov.link_used(act, eid)

        if r.returncode != 0:
            print(f"Fallo en paso: {' '.join(cmd)}")
            # Persistimos lo recolectado antes de salir
            _persist_prov_and_dag(prov, dag_nodes, dag_edges)
            sys.exit(r.returncode)

    # Persistir PROV y DAG tras completar
    _persist_prov_and_dag(prov, dag_nodes, dag_edges)

    # Generar reporte de loop científico
    _generate_scientific_loop_report(prov)


def _persist_prov_and_dag(prov: ProvenanceBuilder, dag_nodes: List[Dict[str, Any]], dag_edges: List[Tuple[str, str]]):
    PROV_OUT.parent.mkdir(parents=True, exist_ok=True)
    DAG_OUT.parent.mkdir(parents=True, exist_ok=True)

    prov_json = prov.to_prov_json()
    PROV_OUT.write_text(json.dumps(prov_json, ensure_ascii=False, indent=2), encoding='utf-8')

    dag = {
        'nodes': dag_nodes,
        'edges': [{'from': a, 'to': b} for a, b in dag_edges],
        'generatedAt': datetime.utcnow().isoformat() + 'Z'
    }
    DAG_OUT.write_text(json.dumps(dag, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"🧬 PROV-JSON guardado en {PROV_OUT}")
    print(f"🗺️  DAG guardado en {DAG_OUT}")


def _load_json_if_exists(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def _generate_scientific_loop_report(prov: ProvenanceBuilder):
    LOOP_OUT.parent.mkdir(parents=True, exist_ok=True)

    metadata = _load_json_if_exists(META_JSON) or {}
    cv_metrics = _load_json_if_exists(CV_JSON) or {}

    # Observaciones básicas de calibración si existen dentro de metadata
    calibration_metrics = metadata.get('calibration_metrics') if isinstance(metadata, dict) else None

    loop = {
        'loop_id': f"loop_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        'hypothesis': {
            'description': 'Mejorar la plausibilidad y calibración del clasificador v4 mediante enriquecimiento y señales débiles',
            'inputs': {
                'enriched_exists': ENRICHED.exists() or ENRICHED_WITH_YEAR.exists(),
                'weak_labels_exists': WEAK.exists(),
                'embeddings_exists': EMBEDDINGS.exists()
            }
        },
        'experiment': {
            'activities_count': len(prov.activities),
            'artifacts_count': len(prov.entities)
        },
        'observations': {
            'cv_metrics': cv_metrics,
            'calibration_metrics': calibration_metrics
        },
        'adjustment': {
            'proposal': 'Aplicar calibración isotónica si reduce ECE vs base; ajustar umbral de decisión si Brier > objetivo.'
        },
        'provenance': {
            'graph_sha256': prov.to_prov_json().get('graph_sha256')
        },
        'generatedAt': datetime.utcnow().isoformat() + 'Z'
    }

    # Calcular hash del reporte
    loop_bytes = json.dumps(loop, sort_keys=True).encode('utf-8')
    loop['report_sha256'] = hashlib.sha256(loop_bytes).hexdigest()

    LOOP_OUT.write_text(json.dumps(loop, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"🔁 Scientific loop report guardado en {LOOP_OUT}")


if __name__ == '__main__':
    run_steps()
