"""
Sistema de Navegación Inteligente para Dominios Científicos
Permite búsqueda, descubrimiento y navegación eficiente por dominios
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import re
from pathlib import Path
import importlib
from app.domains.registry import domain_registry, DomainCategory


class SearchScope(Enum):
    """Alcance de búsqueda"""
    ALL = "all"
    DOMAIN = "domain"
    SUBDOMAIN = "subdomain"
    SERVICE = "service"
    ROUTER = "router"
    MODEL = "model"


@dataclass
class SearchResult:
    """Resultado de búsqueda en dominios"""
    domain: str
    subdomain: Optional[str]
    component_type: str  # service, router, model, etc.
    component_name: str
    path: str
    description: Optional[str]
    score: float  # Relevancia del resultado


class DomainNavigator:
    """Navegador inteligente para dominios científicos"""
    
    def __init__(self):
        self.registry = domain_registry
        self._search_index = self._build_search_index()
        
        # Sinónimos científicos para mejorar búsqueda
        self.synonyms = {
            # Matemáticas
            "math": ["mathematics", "mathematical", "computation", "numerical"],
            "algebra": ["algebraic", "linear", "abstract"],
            "calculus": ["differential", "integral", "derivative"],
            "statistics": ["statistical", "probability", "stochastic"],
            "topology": ["topological", "geometric", "manifold"],
            
            # Física
            "physics": ["physical", "mechanical", "thermal"],
            "quantum": ["qm", "quantum_mechanics", "schrodinger"],
            "plasma": ["ionized", "electromagnetic"],
            
            # Química  
            "chemistry": ["chemical", "molecular", "atomic"],
            "materials": ["material_science", "crystalline", "polymer"],
            
            # Biología
            "biology": ["biological", "biochemical", "molecular_biology"],
            "genomics": ["genome", "dna", "genetic", "sequence"],
            "protein": ["proteomics", "amino_acid", "folding"],
            
            # Medicina
            "medicine": ["medical", "clinical", "healthcare"],
            "imaging": ["mri", "ct", "ultrasound", "radiology"],
            "diagnosis": ["diagnostic", "pathology", "screening"],
            
            # Otros
            "ai": ["artificial_intelligence", "machine_learning", "ml"],
            "simulation": ["modeling", "computational", "numerical"]
        }
    
    def _build_search_index(self) -> Dict[str, List[SearchResult]]:
        """Construye índice de búsqueda de todos los componentes"""
        index = {}
        
        for domain_name, domain_info in self.registry.get_all_domains().items():
            if not domain_info.enabled:
                continue
            
            # Indexar dominio
            self._add_to_index(index, domain_name, SearchResult(
                domain=domain_name,
                subdomain=None,
                component_type="domain",
                component_name=domain_name,
                path=f"domains/{domain_name}",
                description=domain_info.description,
                score=1.0
            ))
            
            # Indexar subdominios
            for subdomain in domain_info.subdomains:
                self._add_to_index(index, subdomain, SearchResult(
                    domain=domain_name,
                    subdomain=subdomain,
                    component_type="subdomain", 
                    component_name=subdomain,
                    path=f"domains/{domain_name}/{subdomain}",
                    description=f"{subdomain} in {domain_name}",
                    score=0.8
                ))
            
            # Indexar servicios
            for service in domain_info.services:
                self._add_to_index(index, service, SearchResult(
                    domain=domain_name,
                    subdomain=None,
                    component_type="service",
                    component_name=service,
                    path=f"domains/{domain_name}/services/{service}",
                    description=f"{service} service in {domain_name}",
                    score=0.9
                ))
            
            # Indexar routers
            for router in domain_info.routers:
                self._add_to_index(index, router, SearchResult(
                    domain=domain_name,
                    subdomain=None,
                    component_type="router",
                    component_name=router,
                    path=f"domains/{domain_name}/routers/{router}",
                    description=f"{router} API in {domain_name}",
                    score=0.9
                ))
        
        return index
    
    def _add_to_index(self, index: Dict[str, List[SearchResult]], 
                     key: str, result: SearchResult):
        """Añade resultado al índice de búsqueda"""
        key = key.lower()
        if key not in index:
            index[key] = []
        index[key].append(result)
    
    def search(self, query: str, scope: SearchScope = SearchScope.ALL, 
              limit: int = 10) -> List[SearchResult]:
        """Búsqueda inteligente en dominios"""
        query = query.lower().strip()
        results = []
        
        # Búsqueda exacta
        exact_matches = self._search_exact(query, scope)
        results.extend(exact_matches)
        
        # Búsqueda con sinónimos
        synonym_matches = self._search_synonyms(query, scope)
        results.extend(synonym_matches)
        
        # Búsqueda parcial
        partial_matches = self._search_partial(query, scope)
        results.extend(partial_matches)
        
        # Eliminar duplicados y ordenar por score
        seen = set()
        unique_results = []
        
        for result in results:
            key = (result.domain, result.component_name, result.component_type)
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        # Ordenar por score descendente
        unique_results.sort(key=lambda x: x.score, reverse=True)
        
        return unique_results[:limit]
    
    def _search_exact(self, query: str, scope: SearchScope) -> List[SearchResult]:
        """Búsqueda exacta en el índice"""
        results = []
        
        if query in self._search_index:
            for result in self._search_index[query]:
                if self._match_scope(result, scope):
                    results.append(result)
        
        return results
    
    def _search_synonyms(self, query: str, scope: SearchScope) -> List[SearchResult]:
        """Búsqueda usando sinónimos"""
        results = []
        
        # Buscar sinónimos de la query
        query_synonyms = set([query])
        for base_term, synonyms in self.synonyms.items():
            if query in synonyms or query == base_term:
                query_synonyms.update(synonyms)
                query_synonyms.add(base_term)
        
        # Buscar cada sinónimo
        for synonym in query_synonyms:
            if synonym in self._search_index:
                for result in self._search_index[synonym]:
                    if self._match_scope(result, scope):
                        # Reducir score para matches de sinónimos
                        result.score *= 0.8
                        results.append(result)
        
        return results
    
    def _search_partial(self, query: str, scope: SearchScope) -> List[SearchResult]:
        """Búsqueda parcial (contains)"""
        results = []
        
        for key, search_results in self._search_index.items():
            if query in key or key in query:
                for result in search_results:
                    if self._match_scope(result, scope):
                        # Reducir score para matches parciales
                        result.score *= 0.6
                        results.append(result)
        
        return results
    
    def _match_scope(self, result: SearchResult, scope: SearchScope) -> bool:
        """Verifica si el resultado coincide con el scope"""
        if scope == SearchScope.ALL:
            return True
        elif scope == SearchScope.DOMAIN:
            return result.component_type == "domain"
        elif scope == SearchScope.SUBDOMAIN:
            return result.component_type == "subdomain"
        elif scope == SearchScope.SERVICE:
            return result.component_type == "service"
        elif scope == SearchScope.ROUTER:
            return result.component_type == "router"
        elif scope == SearchScope.MODEL:
            return result.component_type == "model"
        
        return False
    
    def get_domain_tree(self) -> Dict[str, Any]:
        """Obtiene árbol completo de dominios para navegación"""
        tree = {}
        
        for category in DomainCategory:
            domains = self.registry.get_domains_by_category(category)
            if domains:
                tree[category.value] = {}
                
                for domain in domains:
                    tree[category.value][domain.name] = {
                        "description": domain.description,
                        "subdomains": {
                            subdomain: {
                                "path": f"domains/{domain.name}/{subdomain}",
                                "components": self._get_subdomain_components(domain.name, subdomain)
                            }
                            for subdomain in domain.subdomains
                        },
                        "services": [
                            {
                                "name": service,
                                "path": f"domains/{domain.name}/services/{service}",
                                "type": "service"
                            }
                            for service in domain.services
                        ],
                        "routers": [
                            {
                                "name": router,
                                "path": f"domains/{domain.name}/routers/{router}",
                                "type": "router"
                            }
                            for router in domain.routers
                        ]
                    }
        
        return tree
    
    def _get_subdomain_components(self, domain: str, subdomain: str) -> List[Dict]:
        """Obtiene componentes de un subdominio"""
        # Esto sería implementado para escanear archivos reales
        