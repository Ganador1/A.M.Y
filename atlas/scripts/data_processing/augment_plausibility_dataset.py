"""Genera un dataset ampliado (v3) para el modelo de plausibility.

Modos:
    --mode synthetic (default) : Usa plantillas internas (versión anterior).
    --mode external            : Intenta obtener registros reales de OpenAlex, arXiv y PubMed (títulos+abstracts).

Fuentes externas (simplificadas):
    * OpenAlex: API REST pública (ratelimit friendly). Sólo recuperación básica de works en dominios keywords.
    * arXiv: RSS / query interface vía feedparser.
    * PubMed: E-utilities (solo título/abstract). Aquí se deja placeholder para evitar dependencias extra.

Etiquetado weak external:
    - Se aplica `weak_label` sobre título/abstract.
    - Se interpreta como label=1 si score heurístico >=2.
    - No se fuerza balance perfecto; se hace post-trimming para acercarse a pos_ratio.

Requisitos adicionales para modo external (añadir a requirements si no están):
    requests, feedparser, tenacity, ratelimit

Advertencia: Este script no implementa paginación exhaustiva ni manejo completo de límites.
Está pensado como bootstrap rápido.
"""
from __future__ import annotations
import json
import random
import hashlib
import math
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any
import argparse

try:
    import requests  # type: ignore
    import time
    import xml.etree.ElementTree as ET
except ImportError:  # pragma: no cover
    requests = None
    time = None
    ET = None

try:
    import feedparser  # type: ignore
except ImportError:  # pragma: no cover
    feedparser = None


BASE_V2 = Path("data/plausibility_training_v2.jsonl")
OUT_V3 = Path("data/plausibility_training_v3.jsonl")
RNG = random.Random(42)

def read_jsonl(p: Path) -> List[Dict[str, Any]]:
    if not p.exists():
        return []
    return [json.loads(ln) for ln in p.read_text(encoding='utf-8').strip().splitlines() if ln.strip()]

def write_jsonl(p: Path, rows: List[Dict[str, Any]]):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

DOMAINS = [
    "materials_science", "energy_storage", "drug_discovery", "neuroscience", "ai_research",
    "medical_imaging", "quantum_physics"
]

POS_TEMPLATES = [
    "Investigate whether {focus} improves {metric} in {domain}",
    "Assess impact of {modifier} {focus} on {metric} within {domain}",
    "Determine if optimizing {focus} can enhance {metric} for {domain} applications",
]
NEG_TEMPLATES = [
    "Random speculation about {focus} without measurable outcome in {domain}",
    "Vague idea that {focus} maybe changes something somewhere",
    "Hyperbolic claim that {focus} will revolutionize everything instantly",
]
FOCUS = ["nanoparticle dispersion", "graph neural networks", "CRISPR efficiency", "catalyst surface area", "membrane porosity", "quantum coherence", "signal denoising"]
METRICS = ["thermal conductivity", "energy efficiency", "reaction yield", "classification accuracy", "battery cycle life", "drug binding affinity", "synaptic plasticity"]
MODIFIERS = ["adaptive", "multi-scale", "bio-inspired", "hybrid", "automated"]

@dataclass
class GeneratedExample:
    title: str
    abstract: str
    domain: str
    label: int
    source: str
    generation_ops: List[str]

# Heurística simple para weak label.
def weak_label(title: str, abstract: str, positive_hint: bool) -> int:
    score = 0
    quantitative = any(x in abstract.lower() for x in ["%", "increase", "decrease", "improve", "enhance"])
    measurable = any(m in abstract.lower() for m in ["conductivity", "efficiency", "yield", "accuracy", "affinity", "plasticity"])    
    if quantitative:
        score += 1
    if measurable:
        score += 1
    if positive_hint:
        score += 1
    hype = any(h in abstract.lower() for h in ["revolutionize", "breakthrough", "instantly"])
    if hype:
        score -= 1
    return 1 if score >= 2 else 0

def synthesize(domain: str, n_pos: int, n_neg: int) -> List[GeneratedExample]:
    out: List[GeneratedExample] = []
    for _ in range(n_pos):
        focus = RNG.choice(FOCUS)
        metric = RNG.choice(METRICS)
        modifier = RNG.choice(MODIFIERS)
        t = RNG.choice(POS_TEMPLATES).format(focus=focus, metric=metric, domain=domain, modifier=modifier)
        abstract = f"We test whether {modifier} {focus} can improve {metric} in {domain} by 10-20% using controlled experiments."  # simple
        label = weak_label(t, abstract, True)
        out.append(GeneratedExample(title=t, abstract=abstract, domain=domain, label=label, source="synthetic_template", generation_ops=["template_pos"]))
    for _ in range(n_neg):
        focus = RNG.choice(FOCUS)
        metric = RNG.choice(METRICS)
        t = RNG.choice(NEG_TEMPLATES).format(focus=focus, metric=metric, domain=domain)
        abstract = f"This idea asserts {focus} totally changes {metric} forever without data in {domain}."  # vague
        label = weak_label(t, abstract, False)
        out.append(GeneratedExample(title=t, abstract=abstract, domain=domain, label=label, source="synthetic_template", generation_ops=["template_neg"]))
    return out

def to_record(g: GeneratedExample) -> Dict[str, Any]:
    # features básicos vacíos (se rellenarán en entrenamiento v3 extrayendo de nuevo)
    return {
        "paper_id": hashlib.sha256((g.title+g.abstract).encode()).hexdigest(),
        "title": g.title,
        "abstract": g.abstract,
        "label": g.label,
        "domain": g.domain,
        "source": g.source,
        "generation_ops": g.generation_ops,
    }

def fetch_openalex(sample_size: int = 300, query: str = "materials") -> List[Dict[str, Any]]:
    """Fetch real papers from OpenAlex API"""
    if requests is None:
        print("⚠️ requests no disponible - devolviendo lista vacía")
        return []
    
    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per-page": min(sample_size, 200),
        "filter": "has_abstract:true,language:en"
    }
    
    try:
        print(f"📡 Obteniendo datos de OpenAlex para '{query}'...")
        response = requests.get(url, params=params, timeout=30)
        if response.status_code != 200:
            print(f"❌ OpenAlex error: {response.status_code}")
            return []
        
        data = response.json().get("results", [])
        out = []
        
        for work in data:
            title = work.get("title", "").strip()
            if not title:
                continue
                
            # OpenAlex a veces tiene abstracts en formato invertido
            abstract_raw = work.get("abstract_inverted_index")
            if isinstance(abstract_raw, dict) and abstract_raw:
                # Reconstruir abstract desde índice invertido
                max_pos = max([max(positions) for positions in abstract_raw.values()]) if abstract_raw else 0
                tokens = [""] * (max_pos + 1)
                for word, positions in abstract_raw.items():
                    for pos in positions:
                        if pos < len(tokens):
                            tokens[pos] = word
                abstract = " ".join(token for token in tokens if token).strip()
            else:
                abstract = str(work.get("abstract", "")).strip()
            
            if len(abstract) < 50:  # Skip if abstract too short
                continue
                
            out.append({
                "title": title,
                "abstract": abstract,
                "domain": query.replace(" ", "_").lower(),
                "source": "openalex",
                "url": work.get("id", "")
            })
        
        print(f"✅ OpenAlex: obtenidos {len(out)} registros")
        return out
        
    except Exception as e:
        print(f"❌ Error OpenAlex: {e}")
        return []

def fetch_arxiv(sample_size: int = 300, query: str = "materials") -> List[Dict[str, Any]]:
    """Fetch real papers from arXiv"""
    if feedparser is None:
        print("⚠️ feedparser no disponible - devolviendo lista vacía")
        return []
    
    try:
        print(f"📡 Obteniendo datos de arXiv para '{query}'...")
        
        # arXiv API URL with proper encoding
        base_url = "http://export.arxiv.org/api/query"
        # Replace spaces with + for arXiv query format
        search_query = query.replace(" ", "+")
        params = {
            "search_query": f"all:{search_query}",
            "start": 0,
            "max_results": min(sample_size, 100)  # arXiv recommends max 100
        }
        
        # Build URL manually to avoid encoding issues
        param_str = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{base_url}?{param_str}"
        
        feed = feedparser.parse(url)
        if feed.bozo:
            print(f"❌ arXiv feed error: {getattr(feed, 'bozo_exception', 'Unknown')}")
            return []
        
        out = []
        for entry in feed.entries:
            title = getattr(entry, 'title', '').strip()
            abstract = getattr(entry, 'summary', '').strip()
            
            if not title or len(abstract) < 50:
                continue
                
            out.append({
                "title": title,
                "abstract": abstract,
                "domain": query.replace(" ", "_").lower(),
                "source": "arxiv",
                "url": getattr(entry, 'id', '')
            })
        
        print(f"✅ arXiv: obtenidos {len(out)} registros")
        return out
        
    except Exception as e:
        print(f"❌ Error arXiv: {e}")
        return []

def fetch_pubmed(sample_size: int = 200, query: str = "cancer") -> List[Dict[str, Any]]:
    """Fetch real papers from PubMed using E-utilities"""
    if requests is None:
        print("⚠️ requests no disponible - devolviendo lista vacía")
        return []
    
    try:
        print(f"📡 Obteniendo datos de PubMed para '{query}'...")
        
        # Step 1: Search for IDs
        esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": min(sample_size, 100),
            "retmode": "json"
        }
        
        search_response = requests.get(esearch_url, params=search_params, timeout=30)
        if search_response.status_code != 200:
            print(f"❌ PubMed search error: {search_response.status_code}")
            return []
        
        search_data = search_response.json()
        id_list = search_data.get("esearchresult", {}).get("idlist", [])
        
        if not id_list:
            print("❌ PubMed: no se encontraron IDs")
            return []
        
        # Step 2: Fetch abstracts
        efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(id_list[:50]),  # Limit to 50 to avoid timeout
            "retmode": "xml"
        }
        
        fetch_response = requests.get(efetch_url, params=fetch_params, timeout=45)
        if fetch_response.status_code != 200:
            print(f"❌ PubMed fetch error: {fetch_response.status_code}")
            return []
        
        # Parse XML
        if ET is None:
            print("⚠️ xml.etree no disponible")
            return []
            
        root = ET.fromstring(fetch_response.content)
        out = []
        
        for article in root.findall(".//PubmedArticle"):
            # Extract title
            title_elem = article.find(".//ArticleTitle")
            title = title_elem.text if title_elem is not None else ""
            
            # Extract abstract
            abstract_elem = article.find(".//Abstract/AbstractText")
            abstract = abstract_elem.text if abstract_elem is not None else ""
            
            if not title or not abstract or len(abstract) < 50:
                continue
                
            # Get PMID for URL
            pmid_elem = article.find(".//PMID")
            pmid = pmid_elem.text if pmid_elem is not None else ""
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
            
            out.append({
                "title": title.strip(),
                "abstract": abstract.strip(),
                "domain": query.replace(" ", "_").lower(),
                "source": "pubmed",
                "url": url
            })
        
        print(f"✅ PubMed: obtenidos {len(out)} registros")
        return out
        
    except Exception as e:
        print(f"❌ Error PubMed: {e}")
        return []

def external_corpus(domains: List[str], per_domain: int = 300) -> List[Dict[str, Any]]:
    """Fetch external data from multiple sources with domain-specific queries"""
    collected: List[Dict[str, Any]] = []
    
    # Define better queries per domain
    domain_queries = {
        "materials_science": ["materials science", "materials engineering", "nanomaterials"],
        "energy_storage": ["battery", "energy storage", "lithium ion"],
        "quantum_physics": ["quantum", "quantum mechanics", "quantum computing"],
        "drug_discovery": ["drug discovery", "pharmaceutical", "medicinal chemistry"],
        "medical_imaging": ["medical imaging", "radiology", "MRI"],
        "neuroscience": ["neuroscience", "brain", "neural networks"],
        "ai_research": ["artificial intelligence", "machine learning", "deep learning"]
    }
    
    for domain in domains:
        print(f"\n🔍 Procesando dominio: {domain}")
        queries = domain_queries.get(domain, [domain.replace('_', ' ')])
        
        domain_data = []
        
        for query in queries:
            # Add small delay between requests to be respectful
            if time:
                time.sleep(1)
            
            # Choose sources based on domain
            if domain in ("materials_science", "energy_storage", "quantum_physics"):
                # Science/physics domains: OpenAlex + arXiv
                domain_data.extend(fetch_openalex(per_domain // len(queries), query))
                if time:
                    time.sleep(1)
                domain_data.extend(fetch_arxiv(per_domain // (2 * len(queries)), query))
                
            elif domain in ("drug_discovery", "medical_imaging", "neuroscience"):
                # Medical domains: OpenAlex + PubMed
                domain_data.extend(fetch_openalex(per_domain // len(queries), query))
                if time:
                    time.sleep(1)
                domain_data.extend(fetch_pubmed(per_domain // (2 * len(queries)), query))
                
            else:
                # General domains: OpenAlex + arXiv
                domain_data.extend(fetch_openalex(per_domain // len(queries), query))
                if time:
                    time.sleep(1)
                domain_data.extend(fetch_arxiv(per_domain // (2 * len(queries)), query))
        
        # Deduplicate by title
        seen_titles = set()
        unique_data = []
        for item in domain_data:
            title_lower = item["title"].lower()
            if title_lower not in seen_titles and len(title_lower) > 10:
                seen_titles.add(title_lower)
                item["domain"] = domain  # Ensure consistent domain name
                unique_data.append(item)
        
        collected.extend(unique_data)
        print(f"✅ {domain}: {len(unique_data)} registros únicos obtenidos")
    
    print(f"\n📊 Total recopilado: {len(collected)} registros de {len(domains)} dominios")
    return collected

def build_from_external(domains: List[str], target_size: int, pos_ratio: float) -> List[Dict[str, Any]]:
    raw = external_corpus(domains, per_domain=max(150, target_size // (len(domains)*2)))
    # aplicar weak label
    processed: List[Dict[str, Any]] = []
    for r in raw:
        title = r.get("title", "")
        abstract = r.get("abstract", "")
        domain = r.get("domain", "unknown")
        label = weak_label(title, abstract, True)  # usamos positive_hint=True para favorecer recall
        processed.append({
            "paper_id": hashlib.sha256((title+abstract).encode()).hexdigest(),
            "title": title,
            "abstract": abstract,
            "label": label,
            "domain": domain,
            "source": r.get("source", "external"),
            "generation_ops": ["external_fetch"]
        })
    # Ajuste simple de balance (subsample si excede)
    pos = [x for x in processed if x['label']==1]
    neg = [x for x in processed if x['label']==0]
    desired_pos = int(pos_ratio * target_size)
    desired_neg = target_size - desired_pos
    RNG.shuffle(pos)
    RNG.shuffle(neg)
    balanced = pos[:desired_pos] + neg[:desired_neg]
    RNG.shuffle(balanced)
    return balanced

def main(target_size: int = 2000, pos_ratio: float = 0.5, min_per_domain: int = 200, mode: str = "synthetic"):
    base = read_jsonl(BASE_V2)
    # Filtramos campos esenciales, ignoramos features antiguos (se reconstruyen)
    base_clean = []
    for r in base:
        base_clean.append({
            "paper_id": r.get("paper_id"),
            "title": r.get("title"),
            "abstract": r.get("abstract"),
            "label": r.get("label"),
            "domain": r.get("domain", "unknown"),
            "source": "base_v2",
            "generation_ops": []
        })
    existing = base_clean
    # Conteo inicial por dominio
    counts = {}
    for r in existing:
        d = r["domain"]
        counts[d] = counts.get(d, 0) + 1
    if mode == "external":
        external_rows = build_from_external(DOMAINS, target_size - len(existing) if target_size>len(existing) else target_size, pos_ratio)
        all_rows = existing + external_rows
    else:
        # Generamos sintéticos hasta target
        needed = max(0, target_size - len(existing))
        domains_cycle = DOMAINS.copy()
        idx = 0
        synthetic: List[Dict[str, Any]] = []
        while needed > 0 and idx < target_size * 10:  # safety
            d = domains_cycle[idx % len(domains_cycle)]
            current_d = sum(1 for x in existing if x["domain"] == d) + sum(1 for x in synthetic if x["domain"] == d)
            if current_d < min_per_domain or (len(existing) + len(synthetic)) < target_size:
                batch_pos = max(1, int( (pos_ratio) * 4))
                batch_neg = max(1, 4 - batch_pos)
                gen = synthesize(d, batch_pos, batch_neg)
                for g in gen:
                    synthetic.append(to_record(g))
                    needed -= 1
                    if needed <= 0:
                        break
            idx += 1
        all_rows = existing + synthetic
    write_jsonl(OUT_V3, all_rows)
    # Stats
    domain_counts = {}
    pos, neg = 0, 0
    for r in all_rows:
        domain_counts[r['domain']] = domain_counts.get(r['domain'], 0) + 1
        if r['label'] == 1:
            pos += 1
        else:
            neg += 1
    entropy = 0.0
    total = len(all_rows)
    for c in domain_counts.values():
        p = c / total
        entropy -= p * math.log(p + 1e-12, 2)
    max_entropy = math.log(len(domain_counts)+1e-12, 2)
    print(f"[DATASET V3] size={total} pos={pos} neg={neg} pos_ratio={pos/total:.3f} domains={domain_counts} entropy_norm={entropy/max_entropy if max_entropy>0 else 0:.3f}")
    print(f"Escrito: {OUT_V3}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-size", type=int, default=2000)
    parser.add_argument("--pos-ratio", type=float, default=0.5)
    parser.add_argument("--min-per-domain", type=int, default=200)
    parser.add_argument("--mode", choices=["synthetic", "external"], default="synthetic")
    args = parser.parse_args()
    main(target_size=args.target_size, pos_ratio=args.pos_ratio, min_per_domain=args.min_per_domain, mode=args.mode)
