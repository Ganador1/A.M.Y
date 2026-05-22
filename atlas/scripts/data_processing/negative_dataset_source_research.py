"""
🔍 ATLAS - Investigación de Fuentes de Dataset Negativo
=========================================================

Este script busca y documenta fuentes de papers problemáticos/retractados
para crear un dataset negativo balanceado para nuestro filtro de calidad.

Problema identificado:
- Nuestro dataset actual: 99.8% papers plausibles (495) vs 0.2% implausibles (1)
- El modelo ML aprueba pseudociencia obvía como de alta calidad
- Necesitamos ejemplos negativos para balancear el entrenamiento

Fuentes identificadas hasta ahora:
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Any

class NegativeDatasetSourceResearcher:
    def __init__(self):
        self.sources = {}
        self.findings = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def document_source(self, name: str, url: str, description: str, 
                       access_method: str, estimated_size: str, quality_level: str):
        """Documenta una fuente de papers problemáticos"""
        self.sources[name] = {
            'url': url,
            'description': description,
            'access_method': access_method,
            'estimated_size': estimated_size,
            'quality_level': quality_level,  # high, medium, low
            'discovered_at': self.timestamp
        }
        
        print(f"✅ Documentada fuente: {name}")
        print(f"   URL: {url}")
        print(f"   Descripción: {description}")
        print(f"   Método de acceso: {access_method}")
        print(f"   Tamaño estimado: {estimated_size}")
        print(f"   Nivel de calidad: {quality_level}")
        print()
        
    def add_finding(self, category: str, description: str, actionability: str):
        """Añade un hallazgo de la investigación"""
        finding = {
            'category': category,
            'description': description,
            'actionability': actionability,
            'timestamp': self.timestamp
        }
        self.findings.append(finding)
        
        print(f"💡 Hallazgo [{category}]: {description}")
        print(f"   Accionabilidad: {actionability}")
        print()

def main():
    """Función principal de investigación"""
    
    print("🔍 ATLAS - Investigación de Fuentes de Dataset Negativo")
    print("=" * 60)
    print()
    
    researcher = NegativeDatasetSourceResearcher()
    
    # === FUENTES PRINCIPALES ===
    print("📊 FUENTES PRINCIPALES IDENTIFICADAS:")
    print("-" * 40)
    
    # 1. Retraction Watch Database
    researcher.document_source(
        name="Retraction Watch Database",
        url="https://retractionwatch.com/ + https://api.labs.crossref.org/data/retractionwatch",
        description="Base de datos más completa de papers retractados. Crossref adquirió los datos en 2023 y los hizo públicos. Contiene ~60,000+ retractados con metadatos detallados sobre razones de retractación.",
        access_method="API gratuita de Crossref Labs + CSV descargable + web scraping del blog",
        estimated_size="60,000+ papers retractados",
        quality_level="high"
    )
    
    # 2. COPE (Committee on Publication Ethics)
    researcher.document_source(
        name="COPE Database",
        url="https://publicationethics.org/",
        description="Casos de estudio y guidelines sobre ética en publicación. Incluye casos reales de misconduct, paper mills, authorship issues, etc.",
        access_method="Casos públicos en web + guidelines + forums",
        estimated_size="Cientos de casos documentados",
        quality_level="high"
    )
    
    # 3. PubPeer
    researcher.document_source(
        name="PubPeer",
        url="https://pubpeer.com/",
        description="Plataforma de post-publication peer review donde se discuten problemas en papers publicados. Muchos papers posteriormente retractados tienen discusiones aquí primero.",
        access_method="Web scraping + API si disponible",
        estimated_size="Miles de papers con problemas identificados",
        quality_level="medium"
    )
    
    # 4. Beall's List (archivada)
    researcher.document_source(
        name="Beall's List (Archive)",
        url="https://web.archive.org/web/20170111172309/https://scholarlyoa.com/publishers/ + mirrors",
        description="Lista históricamente importante de predatory journals. Aunque desactualizada, contiene journals que publicaron contenido de baja calidad sistemáticamente.",
        access_method="Web Archive + mirrors mantenidos por comunidad",
        estimated_size="Cientos de journals predatory identificados",
        quality_level="medium"
    )
    
    # === FUENTES ESPECIALIZADAS ===
    print("🎯 FUENTES ESPECIALIZADAS:")
    print("-" * 30)
    
    # 5. Paper Mills detectados
    researcher.document_source(
        name="Paper Mill Watch",
        url="https://papermill.pub/ + reports on Retraction Watch",
        description="Sitio especializado en detectar paper mills - organizaciones que producen papers falsos sistemáticamente. Muchos de estos papers terminan siendo retractados.",
        access_method="Web scraping + análisis de reportes",
        estimated_size="Cientos de papers de paper mills",
        quality_level="high"
    )
    
    # 6. Elisabeth Bik's Science Integrity Digest
    researcher.document_source(
        name="Science Integrity Digest",
        url="https://scienceintegritydigest.com/",
        description="Blog de Elisabeth Bik, experta en image manipulation y scientific misconduct. Documenta casos específicos con evidencia detallada.",
        access_method="Web scraping de posts + Twitter analysis",
        estimated_size="Cientos de casos bien documentados",
        quality_level="high"
    )
    
    # === ENFOQUES SINTÉTICOS ===
    print("🧪 ENFOQUES SINTÉTICOS:")
    print("-" * 25)
    
    # 7. Generación de pseudociencia controlada
    researcher.document_source(
        name="Synthetic Pseudoscience Generation",
        url="N/A - Generación propia",
        description="Generar sintéticamente papers que violan principios científicos básicos usando templates de pseudociencia conocida (perpetual motion, crystal healing, etc.)",
        access_method="Generación algorítmica con LLM + templates",
        estimated_size="Ilimitado - podemos generar cientos/miles",
        quality_level="medium"
    )
    
    # === HALLAZGOS CLAVE ===
    print("💡 HALLAZGOS CLAVE DE LA INVESTIGACIÓN:")
    print("-" * 40)
    
    researcher.add_finding(
        category="Recurso Principal",
        description="Retraction Watch Database via Crossref es la fuente más prometedora - 60,000+ papers retractados con metadatos estructurados y API gratuita",
        actionability="ALTA - Implementar descarga y parsing automático inmediatamente"
    )
    
    researcher.add_finding(
        category="Diversidad de Problemas",
        description="Las fuentes cubren diferentes tipos de problemas: misconduct real (Retraction Watch), problemas metodológicos (PubPeer), journals predatory (Beall's List), paper mills (Paper Mill Watch)",
        actionability="ALTA - Usar múltiples fuentes para dataset más robusto"
    )
    
    researcher.add_finding(
        category="Escalabilidad",
        description="Algunas fuentes (Retraction Watch, PubPeer) tienen miles de ejemplos, mientras que otras (COPE cases) tienen cientos pero muy bien documentados",
        actionability="MEDIA - Priorizar fuentes grandes primero, luego añadir casos de alta calidad"
    )
    
    researcher.add_finding(
        category="Automatización",
        description="Varias fuentes tienen APIs o son scrapeable, permitiendo automatización de la recolección de datos",
        actionability="ALTA - Crear pipeline automatizado de recolección"
    )
    
    researcher.add_finding(
        category="Complementariedad",
        description="Podemos combinar papers retractados reales con pseudociencia sintética para crear dataset negativo más completo y balanceado",
        actionability="ALTA - Estrategia híbrida: real + sintético"
    )
    
    # === PLAN DE ACCIÓN RECOMENDADO ===
    print("🎯 PLAN DE ACCIÓN RECOMENDADO:")
    print("-" * 35)
    
    action_plan = [
        "1. INMEDIATO: Descargar Retraction Watch Database (60,000+ ejemplos)",
        "2. CORTO PLAZO: Scraper para PubPeer papers con problemas identificados", 
        "3. MEDIO PLAZO: Generar pseudociencia sintética usando templates conocidos",
        "4. LARGO PLAZO: Integrar COPE cases y Science Integrity Digest reports",
        "5. VALIDACIÓN: Testear filtro recalibrado con dataset balanceado"
    ]
    
    for action in action_plan:
        print(f"   {action}")
    
    print()
    print("=" * 60)
    print(f"📄 Investigación completada: {researcher.timestamp}")
    
    # Guardar resultados
    results = {
        'sources': researcher.sources,
        'findings': researcher.findings,
        'timestamp': researcher.timestamp,
        'summary': {
            'total_sources': len(researcher.sources),
            'high_quality_sources': len([s for s in researcher.sources.values() if s['quality_level'] == 'high']),
            'recommended_primary': "Retraction Watch Database via Crossref Labs API",
            'estimated_negative_examples': "60,000+ from Retraction Watch alone"
        }
    }
    
    output_file = f"negative_dataset_research_results_{researcher.timestamp}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Resultados guardados en: {output_file}")
    
if __name__ == "__main__":
    main()
