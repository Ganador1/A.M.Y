"""
Literature Service: búsqueda y verificación de hipótesis con fuentes abiertas
Acciones: search_papers, verify_hypothesis (ligero, heurístico),
          search_arxiv, search_patents, search_materials, search_chembl,
          verify_hypothesis_plus (multi-fuente, razones y fuentes clave)
"""
from __future__ import annotations

from typing import Any, Dict, List

from app.services.base_service import BaseService
from app.integrations.literature_clients import LiteratureFacade
from app.exceptions.domain.biology import BiologyError
from app.services.external_science_service import external_science_service


class LiteratureService(BaseService):
    def __init__(self):
        super().__init__("LiteratureService")
        self.facade = LiteratureFacade()

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            action = request_data.get("action", "")
            if action == "search_papers":
                q = request_data.get("query", "")
                k = int(request_data.get("k", 10))
                if not q:
                    return {"success": False, "error": "query required"}
                return self.facade.unified_search(q, k)
            elif action == "search_arxiv":
                q = request_data.get("query", "")
                k = int(request_data.get("k", 10))
                if not q:
                    return {"success": False, "error": "query required"}
                return self.facade.arxiv.search(q, k)
            elif action == "search_patents":
                q = request_data.get("query", "")
                k = int(request_data.get("k", 5))
                if not q:
                    return {"success": False, "error": "query required"}
                return self.facade.search_patents(q, k)
            elif action == "search_materials":
                formula = request_data.get("formula", "")
                k = int(request_data.get("k", 5))
                if not formula:
                    return {"success": False, "error": "formula required"}
                # Filtros opcionales
                emax = request_data.get("e_above_hull_max")
                bmin = request_data.get("band_gap_min")
                return self.facade.search_materials(formula, k) if (emax is None and bmin is None) else self.facade.materials.search(formula, k, emax, bmin)
            elif action == "search_materials_by_chemsys":
                chemsys = request_data.get("chemsys", "")
                k = int(request_data.get("k", 5))
                if not chemsys:
                    return {"success": False, "error": "chemsys required"}
                emax = request_data.get("e_above_hull_max")
                bmin = request_data.get("band_gap_min")
                fields = request_data.get("fields")
                return self.facade.materials.search_by_chemsys(chemsys, k, emax, bmin, fields)
            elif action == "search_chembl":
                q = request_data.get("query", "")
                k = int(request_data.get("k", 5))
                if not q:
                    return {"success": False, "error": "query required"}
                return self.facade.search_chembl(q, k)
            elif action == "search_proteins":
                q = request_data.get("query", "")
                k = int(request_data.get("k", 10))
                if not q:
                    return {"success": False, "error": "query required"}
                return self.facade.search_proteins(q, k)
            elif action == "get_alphafold":
                acc = request_data.get("accession", "")
                if not acc:
                    return {"success": False, "error": "accession required"}
                return self.facade.get_alphafold(acc)
            elif action == "verify_hypothesis":
                hyp = request_data.get("hypothesis", {})
                topic = hyp.get("title") or request_data.get("topic") or ""
                if not topic:
                    return {"success": False, "error": "hypothesis.title or topic required"}
                # Asegura que haya título para el scoring
                if not hyp or not hyp.get("title"):
                    hyp = {**(hyp or {}), "title": topic}
                k = int(request_data.get("k", 10))
                papers = self.facade.unified_search(topic, k).get("results", [])
                score = self._score_support(hyp, papers)
                return {"success": True, "support_score": score, "papers": papers}
            elif action == "verify_hypothesis_plus":
                hyp = request_data.get("hypothesis", {})
                topic = hyp.get("title") or request_data.get("topic") or ""
                domain = (hyp.get("domain") or request_data.get("domain") or "").strip().lower()
                if not topic:
                    return {"success": False, "error": "hypothesis.title or topic required"}
                # Asegura que haya título para el scoring
                if not hyp or not hyp.get("title"):
                    hyp = {**(hyp or {}), "title": topic}
                k = int(request_data.get("k", 12))
                # Consultar múltiples fuentes
                papers = self.facade.unified_search(topic, k).get("results", [])
                arx = self.facade.arxiv.search(topic, min(8, k)).get("results", [])
                patents = self.facade.search_patents(topic, 5).get("results", [])
                # Para dominios materiales/químicos, sólo sumamos si el topic parece fórmula simple
                materials = []
                if any(c.isdigit() for c in topic) and any(ch.isupper() for ch in topic):
                    materials = self.facade.search_materials(topic, 5).get("results", [])

                topic_l = topic.lower()
                # ChEMBL es caro e irrelevante para la mayoría de dominios (p.ej. matemáticas).
                # Activarlo sólo cuando haya señales claras de química/biomedicina.
                chembl = []
                chem_keywords = (
                    "drug", "compound", "ligand", "inhibitor", "agonist", "antagonist",
                    "ic50", "ec50", "ki", "affinity", "binding", "enzyme", "receptor",
                    "smiles", "inchi", "molecule", "pharmac", "tox", "adme"
                )
                chemistry_like = (
                    domain in {"chemistry", "materials", "materials_science", "biology", "medicine", "medical"}
                    or any(w in topic_l for w in chem_keywords)
                    or (any(c.isdigit() for c in topic) and any(ch.isupper() for ch in topic))
                )
                if chemistry_like and len(topic) > 2:
                    chembl = self.facade.search_chembl(topic, 5).get("results", [])

                trials = []
                if any(w in topic_l for w in ("clinical", "trial", "phase", "patient", "randomized", "placebo", "treatment", "therapy", "drug", "disease")):
                    trials = self.facade.search_clinical_trials(topic, min(6, k)).get("results", [])

                pdb = []
                if any(w in topic_l for w in ("protein", "enzyme", "receptor", "antibody", "kinase", "structure", "crystal", "cryo", "alphafold", "mutation", "binding")):
                    pdb = self.facade.search_pdb(topic, min(6, k)).get("results", [])

                proteins = []
                if any(w in topic_l for w in ("protein", "enzyme", "receptor", "antibody", "kinase", "mutation", "binding")):
                    proteins = self.facade.search_proteins(topic, min(6, k)).get("results", [])

                exoplanets = []
                if any(w in topic_l for w in ("exoplanet", "kepler", "tess", "transit", "radial", "planet", "stellar", "orbit", "orbital")):
                    exoplanets = self.facade.search_exoplanets(topic, min(6, k)).get("results", [])

                opentargets = []
                if any(w in topic_l for w in ("target", "disease", "gene", "drug", "association", "phenotype", "mechanism", "inhibitor")):
                    opentargets = self.facade.search_open_targets(topic, min(6, k)).get("results", [])

                gwas = []
                if any(w in topic_l for w in ("gwas", "variant", "snp", "trait", "association", "polymorphism", "risk", "locus", "genotype")):
                    gwas = self.facade.search_gwas(topic, min(6, k)).get("results", [])

                combined = papers + arx + patents + materials + chembl + trials + pdb + proteins + exoplanets + opentargets + gwas
                score = self._score_support(hyp, combined)
                # razones simples
                reasons = []
                if arx:
                    reasons.append("arXiv contiene trabajos relevantes al tópico")
                if patents:
                    reasons.append("Existen patentes relacionadas, indicando aplicabilidad")
                if materials:
                    reasons.append("Datos de Materials Project sugieren materiales afines")
                if chembl:
                    reasons.append("ChEMBL lista compuestos o dianas asociadas")
                if trials:
                    reasons.append("ClinicalTrials.gov contiene ensayos relacionados al tópico")
                if pdb:
                    reasons.append("RCSB PDB contiene estructuras potencialmente relevantes")
                if proteins:
                    reasons.append("UniProt contiene entradas de proteínas relacionadas")
                if exoplanets:
                    reasons.append("NASA Exoplanet Archive contiene entradas relacionadas")
                if opentargets:
                    reasons.append("Open Targets Platform contiene asociaciones diana-enfermedad relevantes")
                if gwas:
                    reasons.append("GWAS Catalog contiene estudios de asociación relevantes")
                key_sources = {
                    "papers": papers[:5],
                    "arxiv": arx[:5],
                    "patents": patents[:5],
                    "materials": materials[:5],
                    "chembl": chembl[:5],
                    "clinical_trials": trials[:5],
                    "pdb": pdb[:5],
                    "proteins": proteins[:5],
                    "exoplanets": exoplanets[:5],
                    "open_targets": opentargets[:5],
                    "gwas_catalog": gwas[:5],
                }

                try:
                    external_ev = await external_science_service.process_request(
                        {
                            "action": "paperqa2_verify_claim",
                            "claim": topic,
                            "domain": domain or "general",
                            "max_results": min(8, max(4, k)),
                        }
                    )
                except Exception:
                    external_ev = {"success": False}

                if external_ev.get("success"):
                    paperqa_support = external_ev.get("support_score")
                    if isinstance(paperqa_support, (int, float)):
                        score = round((score + float(paperqa_support)) / 2.0, 3)
                    reasons.extend(external_ev.get("reasons", [])[:3] if isinstance(external_ev.get("reasons"), list) else [])
                    key_sources["paperqa2"] = external_ev.get("citations", [])[:5]

                return {"success": True, "support_score": score, "reasons": reasons, "sources": key_sources}
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        except BiologyError as e:
            return self.handle_error(e, "process_request")

    def _score_support(self, hypothesis: Dict[str, Any], papers: List[Dict[str, Any]]) -> float:
        """Heurística simple: coincidencias por palabras clave del título/variables.
        - Extrae palabras clave (>3 letras) del título
        - Por paper: +1 si hay >=2 coincidencias; +0.5 si hay 1 coincidencia
        - Variables suman +0.5 si aparece cualquiera
        """
        title = (hypothesis or {}).get("title", "")
        variables = [v.lower() for v in (hypothesis or {}).get("variables", [])]
        if not papers:
            return 0.0
        import re
        stop = {
            "the","and","for","with","from","under","over","into","onto","via","using",
            "of","to","in","on","by","a","an","is","are","be","being","been","this","that",
        }
        tokens = [t for t in re.split(r"[^a-zA-Z0-9]+", title.lower()) if len(t) > 3 and t not in stop]
        if not tokens and title:
            # fallback: usa fragmento del título antes de ':'
            frag = title.split(":")[0].strip().lower()
            if frag:
                tokens = [frag]
        total = 0.0
        for p in papers:
            text = " ".join([
                str(p.get("title", "")),
                str(p.get("abstract", "")),
            ]).lower()
            t_hits = sum(1 for t in tokens if t and t in text)
            inc = 0.0
            if t_hits >= 2:
                inc += 1.0
            elif t_hits == 1:
                inc += 0.5
            if variables and any(v in text for v in variables):
                inc += 0.5
            total += inc
        score = min(1.0, total / max(1, len(papers)))
        return float(score)
