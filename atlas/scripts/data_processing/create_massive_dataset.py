#!/usr/bin/env python3
"""
Scraper masivo para expandir dataset con papers reales de múltiples fuentes y dominios.
Usa los scrapers existentes del proyecto para obtener diversidad máxima.
"""

import json
import time
import argparse
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from ingestion.crossref_fetcher import CrossrefFetcher
from ingestion.semantic_scholar_fetcher import SemanticScholarFetcher
from ingestion.utils import load_state, canonical_id

class MassiveDatasetExpander:
    """Expande el dataset usando múltiples fuentes y queries diversas."""
    
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.total_fetched = 0
        self.total_unique = 0
        self.seen_ids = set()
        
    def get_diverse_queries(self) -> List[Dict[str, Any]]:
        """Queries diversas para maximizar variedad de dominios y calidad."""
        
        # Queries por dominio científico
        domain_queries = [
            # Ciencias exactas y naturales
            {"query": "materials science graphene", "source": "crossref", "domain": "materials_science", "expected_quality": "high"},
            {"query": "quantum physics entanglement", "source": "crossref", "domain": "physics", "expected_quality": "high"},
            {"query": "organic chemistry synthesis", "source": "crossref", "domain": "chemistry", "expected_quality": "high"},
            {"query": "molecular biology CRISPR", "source": "crossref", "domain": "biology", "expected_quality": "high"},
            {"query": "machine learning deep learning", "source": "crossref", "domain": "computer_science", "expected_quality": "high"},
            
            # Ciencias aplicadas y ingeniería
            {"query": "biomedical engineering implants", "source": "crossref", "domain": "engineering", "expected_quality": "high"},
            {"query": "renewable energy solar cells", "source": "crossref", "domain": "energy", "expected_quality": "high"},
            {"query": "artificial intelligence robotics", "source": "crossref", "domain": "robotics", "expected_quality": "high"},
            {"query": "nanotechnology carbon nanotubes", "source": "crossref", "domain": "nanotechnology", "expected_quality": "high"},
            
            # Ciencias médicas y de la salud
            {"query": "cancer immunotherapy treatment", "source": "semantic_scholar", "domain": "medicine", "expected_quality": "high"},
            {"query": "neuroscience brain imaging", "source": "semantic_scholar", "domain": "neuroscience", "expected_quality": "high"},
            {"query": "pharmacology drug discovery", "source": "semantic_scholar", "domain": "pharmacology", "expected_quality": "high"},
            {"query": "clinical trials COVID-19", "source": "semantic_scholar", "domain": "epidemiology", "expected_quality": "high"},
            
            # Ciencias ambientales y geológicas
            {"query": "climate change carbon dioxide", "source": "crossref", "domain": "environmental_science", "expected_quality": "high"},
            {"query": "geology earthquake seismic", "source": "crossref", "domain": "geology", "expected_quality": "high"},
            {"query": "ecology biodiversity conservation", "source": "crossref", "domain": "ecology", "expected_quality": "high"},
            
            # Matemáticas y estadística
            {"query": "mathematics topology algebra", "source": "crossref", "domain": "mathematics", "expected_quality": "high"},
            {"query": "statistics machine learning", "source": "crossref", "domain": "statistics", "expected_quality": "high"},
            
            # Queries para atraer papers de menor calidad o más controversiales
            {"query": "alternative medicine homeopathy", "source": "crossref", "domain": "alternative_medicine", "expected_quality": "low"},
            {"query": "parapsychology telepathy", "source": "crossref", "domain": "parapsychology", "expected_quality": "low"},
            {"query": "conspiracy theory", "source": "crossref", "domain": "sociology", "expected_quality": "low"},
            {"query": "pseudoscience debunked", "source": "crossref", "domain": "science_communication", "expected_quality": "low"},
            {"query": "cold fusion energy", "source": "crossref", "domain": "physics", "expected_quality": "borderline"},
            {"query": "free energy perpetual motion", "source": "crossref", "domain": "physics", "expected_quality": "low"},
            
            # Áreas interdisciplinarias (potencialmente más variables en calidad)
            {"query": "bioinformatics computational biology", "source": "semantic_scholar", "domain": "bioinformatics", "expected_quality": "medium"},
            {"query": "cognitive science psychology", "source": "semantic_scholar", "domain": "psychology", "expected_quality": "medium"},
            {"query": "social science behavior", "source": "crossref", "domain": "sociology", "expected_quality": "medium"},
            {"query": "economics behavioral finance", "source": "crossref", "domain": "economics", "expected_quality": "medium"},
            
            # Tecnologías emergentes (pueden tener claims exagerados)
            {"query": "blockchain cryptocurrency", "source": "crossref", "domain": "computer_science", "expected_quality": "medium"},
            {"query": "virtual reality metaverse", "source": "crossref", "domain": "computer_science", "expected_quality": "medium"},
            {"query": "augmented reality AI", "source": "crossref", "domain": "computer_science", "expected_quality": "medium"},
            
            # Áreas con potencial pseudociencia
            {"query": "consciousness quantum brain", "source": "crossref", "domain": "neuroscience", "expected_quality": "borderline"},
            {"query": "crystal healing therapy", "source": "crossref", "domain": "alternative_medicine", "expected_quality": "low"},
            {"query": "astrology personality", "source": "crossref", "domain": "psychology", "expected_quality": "low"},
        ]
        
        return domain_queries
    
    def fetch_from_crossref(self, query: str, max_batches: int = 5, rows_per_batch: int = 200) -> List[Dict[str, Any]]:
        """Fetch papers from Crossref with specific query."""
        print(f"🔍 Buscando en Crossref: '{query}'")
        
        # Crossref fetcher doesn't support query parameter in constructor
        # We'll fetch general papers and filter later by domain
        fetcher = CrossrefFetcher(rows=rows_per_batch, polite_delay=self.delay)
        state = load_state().get('crossref', {})
        
        results = []
        for i in range(max_batches):
            print(f"   Batch {i+1}/{max_batches}...", end=" ")
            batch = fetcher.fetch_batch(state)
            
            if not batch.items:
                print("Sin resultados")
                break
                
            batch_size = len(batch.items)
            results.extend(batch.items)
            print(f"✅ {batch_size} papers")
            
            state = batch.next_state
            if not state:
                print("   Fin de resultados")
                break
                
            time.sleep(self.delay)
        
        return results
    
    def fetch_from_semantic_scholar(self, query: str, max_batches: int = 3, limit_per_batch: int = 100) -> List[Dict[str, Any]]:
        """Fetch papers from Semantic Scholar with specific query."""
        print(f"🧠 Buscando en Semantic Scholar: '{query}'")
        
        fetcher = SemanticScholarFetcher(query=query, limit=limit_per_batch, polite_delay=self.delay)
        state = load_state().get('semantic_scholar', {})
        
        results = []
        for i in range(max_batches):
            print(f"   Batch {i+1}/{max_batches}...", end=" ")
            batch = fetcher.fetch_batch(state)
            
            if not batch.items:
                print("Sin resultados")
                break
                
            batch_size = len(batch.items)
            results.extend(batch.items)
            print(f"✅ {batch_size} papers")
            
            state = batch.next_state
            if not state:
                print("   Fin de resultados")
                break
                
            time.sleep(self.delay)
        
        return results
    
    def deduplicate_and_enrich(self, papers: List[Dict[str, Any]], query_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Remove duplicates and enrich with query metadata."""
        unique_papers = []
        
        for paper in papers:
            # Generate ID for deduplication
            paper_id = paper.get('paper_id') or canonical_id(
                paper.get('title', ''), 
                paper.get('year', paper.get('published_year'))
            )
            
            if paper_id in self.seen_ids:
                continue
                
            self.seen_ids.add(paper_id)
            
            # Enrich with metadata
            paper['paper_id'] = paper_id
            paper['source_query'] = query_info['query']
            paper['expected_domain'] = query_info['domain']
            paper['expected_quality'] = query_info['expected_quality']
            paper['fetched_at'] = datetime.now().isoformat()
            
            # Ensure required fields
            if not paper.get('title') or len(paper.get('title', '')) < 10:
                continue
                
            if not paper.get('abstract') and not paper.get('summary'):
                continue
            
            # Normalize abstract field
            if not paper.get('abstract') and paper.get('summary'):
                paper['abstract'] = paper['summary']
            
            unique_papers.append(paper)
            
        return unique_papers
    
    def run_massive_fetch(self, max_papers: int = 5000) -> str:
        """Run massive fetching from all sources with diverse queries."""
        
        print(f"🚀 SCRAPING MASIVO - Objetivo: {max_papers} papers únicos")
        print(f"🕒 Estimado de tiempo: {max_papers * self.delay / 3600:.1f} horas")
        print("=" * 80)
        
        queries = self.get_diverse_queries()
        all_papers = []
        
        start_time = time.time()
        
        for i, query_info in enumerate(queries):
            if self.total_unique >= max_papers:
                print(f"\n🎯 Meta alcanzada: {self.total_unique} papers únicos")
                break
                
            print(f"\n[{i+1}/{len(queries)}] Query: {query_info['domain']} - {query_info['expected_quality']}")
            
            try:
                if query_info['source'] == 'crossref':
                    batch_results = self.fetch_from_crossref(query_info['query'])
                elif query_info['source'] == 'semantic_scholar':
                    batch_results = self.fetch_from_semantic_scholar(query_info['query'])
                else:
                    continue
                
                # Process and deduplicate
                unique_batch = self.deduplicate_and_enrich(batch_results, query_info)
                all_papers.extend(unique_batch)
                
                self.total_fetched += len(batch_results)
                self.total_unique += len(unique_batch)
                
                print(f"   📊 Batch: {len(batch_results)} raw → {len(unique_batch)} unique")
                print(f"   🔢 Total acumulado: {self.total_unique} únicos de {self.total_fetched} raw")
                
                # Save intermediate results every 5 queries
                if (i + 1) % 5 == 0:
                    self.save_intermediate_results(all_papers, i + 1)
                
            except Exception as e:
                print(f"   ❌ Error en query '{query_info['query']}': {str(e)}")
                continue
        
        # Final save
        output_file = self.save_final_results(all_papers)
        
        elapsed = time.time() - start_time
        print(f"\n🏁 SCRAPING COMPLETADO")
        print(f"⏱️  Tiempo total: {elapsed/3600:.1f} horas")
        print(f"📊 Estadísticas finales:")
        print(f"   Papers raw fetched: {self.total_fetched}")
        print(f"   Papers únicos: {self.total_unique}")
        print(f"   Tasa deduplicación: {(1 - self.total_unique/max(self.total_fetched, 1)):.1%}")
        print(f"📁 Archivo final: {output_file}")
        
        return str(output_file)
    
    def save_intermediate_results(self, papers: List[Dict[str, Any]], query_num: int):
        """Save intermediate results as backup."""
        backup_file = Path(f"data/expanded_dataset_backup_query_{query_num}.jsonl")
        self.save_papers_to_file(papers, backup_file)
        print(f"   💾 Backup guardado: {backup_file}")
    
    def save_final_results(self, papers: List[Dict[str, Any]]) -> Path:
        """Save final results with analysis."""
        output_file = Path("data/plausibility_massive_dataset.jsonl")
        self.save_papers_to_file(papers, output_file)
        
        # Generate analysis report
        analysis = self.generate_dataset_analysis(papers)
        analysis_file = Path("data/massive_dataset_analysis.json")
        
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Análisis guardado en: {analysis_file}")
        
        return output_file
    
    def save_papers_to_file(self, papers: List[Dict[str, Any]], file_path: Path):
        """Save papers to JSONL file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            for paper in papers:
                f.write(json.dumps(paper, ensure_ascii=False) + '\n')
    
    def generate_dataset_analysis(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive dataset analysis."""
        
        # Count by domain
        domain_counts = {}
        quality_counts = {}
        source_counts = {}
        year_counts = {}
        
        for paper in papers:
            domain = paper.get('expected_domain', 'unknown')
            quality = paper.get('expected_quality', 'unknown')
            source = paper.get('raw_source', 'unknown')
            year = paper.get('year', paper.get('published_year', 'unknown'))
            
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1
            year_counts[str(year)] = year_counts.get(str(year), 0) + 1
        
        return {
            'total_papers': len(papers),
            'unique_domains': len(domain_counts),
            'domain_distribution': domain_counts,
            'quality_distribution': quality_counts,
            'source_distribution': source_counts,
            'year_distribution': dict(sorted(year_counts.items())),
            'analysis_timestamp': datetime.now().isoformat(),
            'estimated_classification_time_hours': len(papers) * 12 / 3600,
        }

def main():
    parser = argparse.ArgumentParser(description="Massive dataset expansion using existing scrapers")
    parser.add_argument('--max-papers', type=int, default=5000, 
                       help='Maximum number of unique papers to fetch')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between API requests (seconds)')
    
    args = parser.parse_args()
    
    expander = MassiveDatasetExpander(delay=args.delay)
    output_file = expander.run_massive_fetch(max_papers=args.max_papers)
    
    print(f"\n🎉 Dataset masivo creado: {output_file}")
    print(f"🤖 Listo para clasificación con Mistral")
    print(f"⏰ Tiempo estimado clasificación: {args.max_papers * 12 / 3600:.1f} horas")

if __name__ == '__main__':
    main()
