#!/usr/bin/env python3
"""
Usar los scrapers existentes para expandir dataset masivamente con papers reales.
Usa update_dataset.py con múltiples configuraciones para obtener diversidad.
"""

import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

class SmartDatasetExpander:
    """Expande dataset usando los scrapers existentes con configuraciones diversas."""
    
    def __init__(self):
        self.start_time = time.time()
        
    def run_crossref_batches(self, total_batches: int = 20, rows_per_batch: int = 500) -> int:
        """Execute multiple Crossref batches to get diverse papers."""
        print(f"🔍 Descargando {total_batches} batches de Crossref ({rows_per_batch} papers/batch)")
        
        total_added = 0
        
        # Run update_dataset.py multiple times with different configurations
        for i in range(total_batches):
            print(f"Batch {i+1}/{total_batches}...", end=" ")
            
            cmd = [
                "python", "update_dataset.py",
                "--rows", str(rows_per_batch),
                "--max-batches", "1",
                "--delay", "1.0"
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    # Parse output to get added papers count
                    output_lines = result.stdout.strip().split('\n')
                    for line in output_lines:
                        if "Nuevos registros añadidos tras deduplicar:" in line:
                            added = int(line.split(':')[1].strip())
                            total_added += added
                            print(f"✅ +{added} papers")
                            break
                    else:
                        print("✅ Completado")
                else:
                    print(f"❌ Error: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print("⏰ Timeout")
            except Exception as e:
                print(f"❌ {str(e)}")
                
            # Small delay between batches
            time.sleep(2)
        
        return total_added
        
    def run_semantic_scholar_queries(self, queries: List[str], limit_per_query: int = 100) -> int:
        """Execute Semantic Scholar searches with diverse queries."""
        print(f"🧠 Ejecutando {len(queries)} queries en Semantic Scholar")
        
        total_added = 0
        
        for i, query in enumerate(queries):
            print(f"Query {i+1}/{len(queries)}: '{query}'...", end=" ")
            
            cmd = [
                "python", "update_dataset.py",
                "--rows", "0",  # Skip Crossref
                "--semantic-limit", str(limit_per_query),
                "--semantic-batches", "3",
                "--semantic-query", query,
                "--delay", "1.5"
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    # Parse output for Semantic Scholar results
                    output_lines = result.stdout.strip().split('\n')
                    for line in output_lines:
                        if "SemanticScholar:" in line and "Crossref:" in line:
                            # Extract semantic scholar count
                            parts = line.split('|')
                            for part in parts:
                                if "SemanticScholar:" in part:
                                    added = int(part.split(':')[1].strip())
                                    total_added += added
                                    print(f"✅ +{added} papers")
                                    break
                            break
                    else:
                        print("✅ Completado")
                else:
                    print(f"❌ Error: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print("⏰ Timeout")
            except Exception as e:
                print(f"❌ {str(e)}")
                
            # Delay between queries to be polite
            time.sleep(3)
            
        return total_added
    
    def get_diverse_semantic_queries(self) -> List[str]:
        """Get diverse semantic scholar queries for different domains and quality levels."""
        return [
            # High quality scientific domains
            "materials science graphene carbon nanotube",
            "quantum physics superconductor",
            "machine learning deep learning neural network",
            "cancer immunotherapy treatment clinical trial",
            "neuroscience brain imaging fMRI",
            "renewable energy solar cell efficiency", 
            "chemistry organic synthesis catalysis",
            "biology molecular genetics CRISPR",
            "artificial intelligence computer vision",
            "nanotechnology nanoparticle biomedical",
            
            # Medium quality / interdisciplinary
            "climate change environmental science",
            "psychology cognitive science behavior",
            "biotechnology genetic engineering",
            "robotics automation manufacturing",
            "biomedical engineering medical device",
            "computational biology bioinformatics",
            "materials engineering composite",
            "pharmaceutical drug discovery",
            "medical imaging diagnosis",
            "sustainable technology innovation",
            
            # Areas that might have lower quality papers
            "alternative medicine complementary therapy",
            "homeopathy alternative treatment",
            "consciousness quantum brain theory",
            "pseudoscience scientific misconduct",
            "paranormal research parapsychology",
            "conspiracy theory misinformation",
            "cold fusion energy device",
            "free energy perpetual motion",
            "crystal healing therapy wellness",
            "astrology personality psychology",
            
            # Borderline scientific areas
            "blockchain technology application",
            "virtual reality metaverse",
            "cryptocurrency digital currency",
            "social media psychology behavior",
            "nutrition supplement health",
            "exercise physiology performance",
            "mindfulness meditation brain",
            "acupuncture pain management",
            "herbal medicine traditional",
            "stem cell therapy regenerative"
        ]
    
    def analyze_final_dataset(self) -> Dict[str, Any]:
        """Analyze the final expanded dataset."""
        
        dataset_file = Path("data/plausibility_training_v4_candidates.jsonl")
        
        if not dataset_file.exists():
            return {"error": "Dataset file not found"}
        
        papers = []
        with open(dataset_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    papers.append(json.loads(line))
        
        # Basic statistics
        total_papers = len(papers)
        sources = {}
        years = {}
        has_abstract = 0
        has_citations = 0
        
        for paper in papers:
            source = paper.get('source', 'unknown')
            year = paper.get('year', 'unknown')
            
            sources[source] = sources.get(source, 0) + 1
            years[str(year)] = years.get(str(year), 0) + 1
            
            if paper.get('abstract'):
                has_abstract += 1
            if paper.get('citation_count') is not None:
                has_citations += 1
        
        analysis = {
            'total_papers': total_papers,
            'sources': sources,
            'year_distribution': dict(sorted(years.items())),
            'quality_metrics': {
                'papers_with_abstract': has_abstract,
                'papers_with_citations': has_citations,
                'abstract_coverage': has_abstract / total_papers if total_papers > 0 else 0,
                'citation_coverage': has_citations / total_papers if total_papers > 0 else 0
            },
            'estimated_classification_time_hours': total_papers * 12 / 3600,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return analysis
    
    def run_massive_expansion(self, max_crossref_batches: int = 15, semantic_queries_limit: int = 30) -> str:
        """Run massive dataset expansion."""
        
        print("🚀 EXPANSIÓN MASIVA DE DATASET")
        print("=" * 60)
        print(f"📊 Configuración:")
        print(f"   - Crossref batches: {max_crossref_batches}")
        print(f"   - Semantic Scholar queries: {semantic_queries_limit}")
        print(f"   - Tiempo estimado: {(max_crossref_batches * 2 + semantic_queries_limit * 3) / 60:.1f} minutos")
        print()
        
        total_papers_added = 0
        
        # Phase 1: Crossref bulk download
        print("📚 FASE 1: Descarga masiva Crossref")
        crossref_added = self.run_crossref_batches(max_crossref_batches, 500)
        total_papers_added += crossref_added
        print(f"✅ Crossref completado: +{crossref_added} papers")
        print()
        
        # Phase 2: Semantic Scholar diverse queries
        print("🧠 FASE 2: Queries diversas Semantic Scholar")
        queries = self.get_diverse_semantic_queries()[:semantic_queries_limit]
        semantic_added = self.run_semantic_scholar_queries(queries, 100)
        total_papers_added += semantic_added
        print(f"✅ Semantic Scholar completado: +{semantic_added} papers")
        print()
        
        # Phase 3: Analysis
        print("📊 FASE 3: Análisis del dataset final")
        analysis = self.analyze_final_dataset()
        
        # Save analysis
        analysis_file = Path("data/massive_expansion_analysis.json")
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        elapsed_time = time.time() - self.start_time
        
        print()
        print("🎉 EXPANSIÓN COMPLETADA")
        print("=" * 60)
        print(f"⏰ Tiempo total: {elapsed_time/60:.1f} minutos")
        print(f"📊 Estadísticas finales:")
        print(f"   Papers en dataset: {analysis.get('total_papers', 0)}")
        print(f"   Papers añadidos: {total_papers_added}")
        print(f"   Fuentes: {', '.join(analysis.get('sources', {}).keys())}")
        print(f"   Coverage abstracts: {analysis.get('quality_metrics', {}).get('abstract_coverage', 0):.1%}")
        print(f"   Coverage citas: {analysis.get('quality_metrics', {}).get('citation_coverage', 0):.1%}")
        print(f"📁 Análisis guardado: {analysis_file}")
        print(f"📁 Dataset expandido: data/plausibility_training_v4_candidates.jsonl")
        print(f"🤖 Tiempo estimado clasificación: {analysis.get('estimated_classification_time_hours', 0):.1f} horas")
        
        return str(analysis_file)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart massive dataset expansion")
    parser.add_argument('--crossref-batches', type=int, default=15,
                       help='Number of Crossref batches to fetch')
    parser.add_argument('--semantic-queries', type=int, default=30,
                       help='Number of Semantic Scholar queries to run')
    
    args = parser.parse_args()
    
    expander = SmartDatasetExpander()
    result_file = expander.run_massive_expansion(
        max_crossref_batches=args.crossref_batches,
        semantic_queries_limit=args.semantic_queries
    )
    
    print(f"\n🔥 Expansión masiva completada!")
    print(f"📊 Análisis disponible en: {result_file}")

if __name__ == '__main__':
    main()
