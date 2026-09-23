"""Debug para revisar qué dominios están disponibles en ToolEvidenceOrchestrator"""
from app.services.tool_evidence_orchestrator import ToolEvidenceOrchestratorService

def debug_domains():
    print("🔍 Diagnóstico de dominios disponibles")
    print("=" * 50)
    
    orchestrator = ToolEvidenceOrchestratorService()
    
    print("📋 Dominios configurados:")
    domains = list(orchestrator.domain_routes.keys())
    for i, domain in enumerate(sorted(domains), 1):
        route_count = len(orchestrator.domain_routes[domain])
        print(f"   {i:2d}. {domain}: {route_count} herramientas")
    
    print(f"\n📊 Total dominios: {len(domains)}")
    
    # Verificar dominio neuroscience específicamente
    if "neuroscience" in domains:
        routes = orchestrator.domain_routes["neuroscience"]
        print(f"\n🧠 Detalle dominio NEUROSCIENCE ({len(routes)} herramientas):")
        for i, spec in enumerate(routes, 1):
            print(f"   {i}. {spec.description} (peso: {spec.weight})")
    else:
        print("\n❌ Dominio 'neuroscience' NO ENCONTRADO")
    
    return domains

if __name__ == "__main__":
    debug_domains()
