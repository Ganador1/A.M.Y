"""
Provenance Service
Construye grafos de reproducibilidad unificando:
- Experimentos (MLflow via ExperimentTrackingService)
- Artefactos por experimento
- Versiones de datos (DataVersioningService)

Entrega:
- JSON con nodos y aristas
- (Opcional) HTML interactivo con pyvis en static/graphs
"""

from __future__ import annotations

from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import hashlib
import os
import networkx as nx
from pyvis.network import Network

from app.services.base_service import BaseService
from app.services.experiment_tracking import ExperimentTrackingService
from app.services.data_versioning import DataVersioningService
from app.exceptions.domain.physics import QuantumError
from app.types.provenance_types import (
    ProcessRequestResult,
    ListExperimentsResult,
    GetExperimentResult,
)
# logger optional for future; keep service lean for now


@dataclass
class Node:
    id: str
    label: str
    type: str
    meta: Dict[str, Any]


class ProvenanceService(BaseService):
    def __init__(self):
        super().__init__("Provenance")
        self.output_dir = Path("static/graphs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Procesa acciones del servicio de procedencia.
        Acciones soportadas:
        - graph_all: construir grafo de todos los experimentos
        - graph_experiment: construir grafo de un experimento específico
        """
        try:
            action = request_data.get("action")
            render_html = bool(request_data.get("render_html", True))

            if action == "graph_all":
                exp_service = request_data.get("exp_service") or ExperimentTrackingService()
                data_service = request_data.get("data_service") or DataVersioningService()
                return self.build_all_experiments_graph(
                    exp_service=exp_service,
                    data_service=data_service,
                    render_html=render_html,
                )
            elif action == "graph_experiment":
                experiment_id = request_data.get("experiment_id")
                if not experiment_id:
                    return {"success": False, "error": "experiment_id is required"}
                exp_service = request_data.get("exp_service") or ExperimentTrackingService()
                data_service = request_data.get("data_service") or DataVersioningService()
                return self.build_experiment_graph(
                    exp_service=exp_service,
                    experiment_id=experiment_id,
                    data_service=data_service,
                    render_html=render_html,
                )
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        except QuantumError as e:
            return self.handle_error(e, "process_request")

    def _add_node(self, G: nx.Graph, node: Node):
        if not G.has_node(node.id):
            G.add_node(node.id, label=node.label, type=node.type, **node.meta)

    def _add_edge(self, G: nx.Graph, src: str, dst: str, label: str):
        if not G.has_edge(src, dst):
            G.add_edge(src, dst, label=label)

    def _attach_workflow_nodes(self, G: nx.Graph, exp_node_id: str, params: Dict[str, Any], tags: Dict[str, Any]):
        """Adjunta nodos de pasos de workflow cuando hay metadatos de pipeline.
        Soporta formatos flexibles:
        - params["workflow_dag"]: {nodes: [{id,label,...}], edges: [{from,to,label}]}
        - params["workflow_steps"]: [str | {id?, name, after?}]
        (También se aceptan en tags).
        """
        wf_dag = (params or {}).get("workflow_dag") or (tags or {}).get("workflow_dag")
        wf_steps = (params or {}).get("workflow_steps") or (tags or {}).get("workflow_steps")

        if wf_dag and isinstance(wf_dag, dict):
            nodes = wf_dag.get("nodes", [])
            edges = wf_dag.get("edges", [])
            for n in nodes:
                nid = f"wf:{n.get('id') or n.get('name') or hashlib.sha256(str(n).encode()).hexdigest()[:6]}"
                label = n.get("label") or n.get("name") or nid
                self._add_node(G, Node(id=nid, label=label, type="workflow_step", meta={k: v for k, v in n.items() if k not in ("id", "label", "name")}))
                self._add_edge(G, exp_node_id, nid, "has_step")
            for e in edges:
                frm = f"wf:{e.get('from')}"
                to = f"wf:{e.get('to')}"
                if G.has_node(frm) and G.has_node(to):
                    self._add_edge(G, frm, to, e.get("label") or "depends_on")

        elif wf_steps and isinstance(wf_steps, list):
            prev_id: Optional[str] = None
            for i, s in enumerate(wf_steps):
                if isinstance(s, dict):
                    sid = s.get("id") or s.get("name") or f"s{i}"
                    nid = f"wf:{sid}"
                    label = s.get("name") or sid
                    self._add_node(G, Node(id=nid, label=label, type="workflow_step", meta={k: v for k, v in s.items() if k not in ("id", "name", "after")}))
                    self._add_edge(G, exp_node_id, nid, "has_step")
                    after = s.get("after")
                    if after:
                        dep = f"wf:{after}"
                        if G.has_node(dep):
                            self._add_edge(G, dep, nid, "depends_on")
                    prev_id = nid
                else:
                    # Assume string
                    nid = f"wf:{i}:{hashlib.sha256(str(s).encode()).hexdigest()[:6]}"
                    self._add_node(G, Node(id=nid, label=str(s), type="workflow_step", meta={}))
                    self._add_edge(G, exp_node_id, nid, "has_step")
                    if prev_id:
                        self._add_edge(G, prev_id, nid, "depends_on")
                    prev_id = nid

    def _render_html(self, G: nx.Graph, name_seed: str) -> str:
        net = Network(
            notebook=False,
            height="800px",
            width="100%",
            bgcolor="#ffffff",
        )
        net.from_nx(G)

        # Style nodes by type
        type_styles = {
            "experiment": {"color": "#1f77b4", "shape": "dot", "size": 20},
            "run": {"color": "#2ca02c", "shape": "diamond", "size": 16},
            "artifact": {"color": "#ff7f0e", "shape": "box", "size": 14},
            "data_version": {"color": "#9467bd", "shape": "ellipse", "size": 14},
        }
        for n in net.nodes:
            t = (n.get("type") or G.nodes[n["id"]].get("type") or "").lower()
            style = type_styles.get(t, {"color": "#7f7f7f", "shape": "dot", "size": 12})
            n.update(style)

        net.set_options(
            """
            var options = {
              "physics": {"enabled": true, "stabilization": {"enabled": true, "iterations": 100}},
              "interaction": {"hover": true},
              "edges": {"smooth": {"type": "dynamic"}}
            }
            """
        )

        content_hash = hashlib.sha256(name_seed.encode()).hexdigest()[:8]
        file_name = f"provenance_{content_hash}.html"
        full_path = self.output_dir / file_name
        net.save_graph(str(full_path))
        return f"/static/graphs/{file_name}"

    def build_all_experiments_graph(
        self,
        exp_service: ExperimentTrackingService,
        data_service: Optional[DataVersioningService] = None,
        render_html: bool = True,
    ) -> Dict[str, Any]:
        """Construye el grafo de todos los experimentos en memoria y sus artefactos/versiones de datos."""
        data_service = data_service or DataVersioningService()

        G = nx.DiGraph()
    # nodes list not required; build directly on graph

        experiments = exp_service.list_experiments().get("experiments", [])

        # Index versiones por data_path para vincular artefactos → versión
        versions_index: Dict[str, Dict[str, Any]] = {}
        for v in data_service.data_versions.values():
            versions_index[v.data_path] = {
                "version_id": v.version_id,
                "checksum": v.checksum,
                "size_bytes": v.size_bytes,
            }

        for e in experiments:
            exp_id = e["experiment_id"]
            # Obtener detalles para métricas/artefactos
            exp_detail = exp_service.get_experiment({"experiment_id": exp_id})
            if not exp_detail.get("success"):
                continue
            exp = exp_detail["experiment"]

            exp_node = Node(id=f"exp:{exp_id}", label=exp["name"], type="experiment", meta={"status": exp["status"]})
            self._add_node(G, exp_node)

            run_id = exp.get("run_id") or ""
            if run_id:
                run_node = Node(id=f"run:{run_id}", label=f"run:{run_id[:8]}", type="run", meta={})
                self._add_node(G, run_node)
                self._add_edge(G, exp_node.id, run_node.id, "has_run")

            # Parámetros y métricas como metadatos del nodo experimento
            G.nodes[exp_node.id]["parameters"] = exp.get("parameters", {})
            G.nodes[exp_node.id]["metrics"] = exp.get("metrics", {})

            # Adjuntar workflow si existe
            self._attach_workflow_nodes(G, exp_node.id, exp.get("parameters", {}), exp.get("tags", {}))

            # Artefactos → posibles versiones de datos
            for art in exp.get("artifacts", []) or []:
                art_id = f"artifact:{os.path.basename(str(art))}:{hashlib.sha256(str(art).encode()).hexdigest()[:6]}"
                art_node = Node(id=art_id, label=os.path.basename(str(art)), type="artifact", meta={"path": art})
                self._add_node(G, art_node)
                self._add_edge(G, exp_node.id, art_node.id, "produces")

                ver = versions_index.get(str(art))
                if ver:
                    dv_id = f"dvc:{ver['version_id']}"
                    dv_node = Node(id=dv_id, label=ver["version_id"], type="data_version", meta={"checksum": ver["checksum"], "size": ver["size_bytes"]})
                    self._add_node(G, dv_node)
                    self._add_edge(G, art_node.id, dv_node.id, "versioned_as")

        # Serializar JSON
        nodes_json = [
            {"id": n, "label": G.nodes[n].get("label"), "type": G.nodes[n].get("type"), **{k: v for k, v in G.nodes[n].items() if k not in ("label", "type")}}
            for n in G.nodes
        ]
        edges_json = [
            {"from": u, "to": v, "label": G.edges[u, v].get("label")}
            for u, v in G.edges
        ]

        html_url = self._render_html(G, name_seed=f"all:{len(nodes_json)}:{len(edges_json)}") if render_html else None

        return {
            "success": True,
            "graph": {"nodes": nodes_json, "edges": edges_json},
            "html": html_url,
            "counts": {"nodes": len(nodes_json), "edges": len(edges_json)},
        }

    def build_experiment_graph(
        self,
        exp_service: ExperimentTrackingService,
        experiment_id: str,
        data_service: Optional[DataVersioningService] = None,
        render_html: bool = True,
    ) -> Dict[str, Any]:
        data_service = data_service or DataVersioningService()

        # Reutiliza el builder global filtrando por ID
        class _Shim(ExperimentTrackingService):
            def __init__(self, base: ExperimentTrackingService, target: str):
                self._base = base
                self._target = target

            def list_experiments(self) -> ListExperimentsResult:  # type: ignore[override]
                base = self._base.list_experiments()
                base["experiments"] = [e for e in base.get("experiments", []) if e.get("experiment_id") == self._target]
                return base

            def get_experiment(self, request_data: GetExperimentResult) -> GetExperimentResult:  # passthrough for details
                return self._base.get_experiment(request_data)

        shim = _Shim(exp_service, experiment_id)
        return self.build_all_experiments_graph(shim, data_service, render_html)
