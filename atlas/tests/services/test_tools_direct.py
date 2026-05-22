"""Test directo del ToolEvidenceOrchestrator para diagnosticar qué herramientas funcionan"""
import asyncio
import json
from app.services.tool_evidence_orchestrator import ToolEvidenceOrchestratorService

async def test_tools():
    print("🔬 Diagnóstico de herramientas disponibles")
    print("=" * 50)
    
    orchestrator = ToolEvidenceOrchestratorService()
    
    # Test goal específico
    goal = "neural tissue regeneration using functionalized nanoparticles with growth factors"
    domain = "neuroscience"
    
    print(f"📋 Test Goal: {goal}")
    print(f"🔬 Domain: {domain}")
    print()
    
    try:
        print("🔍 Construyendo request...")
        request_data = {
            "action": "corroborate",
            "hypothesis": {
                "title": "Neural Tissue Regeneration with Functionalized Nanoparticles",
                "description": goal,
                "variables": ["nanoparticle concentration", "growth factor type", "neural cell survival"],
                "expected_outcome": "increased neural tissue regeneration",
                "assumptions": ["nanoparticles effectively deliver growth factors"],
                "domain": domain
            }
        }
        print(f"✅ Request construido: {len(str(request_data))} chars")
        
        print("🚀 Ejecutando corroboración...")
        result = await orchestrator.process_request(request_data)
        print(f"✅ Resultado recibido: success={result.get('success')}")
        
        if result.get('success'):
            print("📊 Analizando resultado...")
            evidence_items = result.get("evidence_items", [])
            print(f"   Evidence items encontrados: {len(evidence_items)}")
            
            if evidence_items:
                successful_items = [e for e in evidence_items if e.get('success')]
                failed_items = [e for e in evidence_items if not e.get('success')]
                
                print(f"   ✅ Exitosas: {len(successful_items)}")
                print(f"   ❌ Fallidas: {len(failed_items)}")
                
                # Mostrar las primeras exitosas
                if successful_items:
                    print("\n🟢 HERRAMIENTAS EXITOSAS:")
                    for i, item in enumerate(successful_items[:3], 1):
                        source = item.get('source', 'unknown')
                        operation = item.get('operation', 'unknown')
                        print(f"   {i}. {source}: {operation}")
                
                # Mostrar las primeras fallidas con detalles
                if failed_items:
                    print("\n🔴 HERRAMIENTAS FALLIDAS:")
                    for i, item in enumerate(failed_items[:3], 1):
                        source = item.get('source', 'unknown')
                        operation = item.get('operation', 'unknown') 
                        error = item.get('error', 'Unknown error')
                        print(f"   {i}. {source}: {operation}")
                        print(f"      Error: {error}")
            else:
                print("⚠️ No se encontraron evidence items")
                
            # Mostrar métricas agregadas
            aggregate = result.get('aggregate', {})
            print(f"\n📊 MÉTRICAS AGREGADAS:")
            for key, value in aggregate.items():
                print(f"   {key}: {value}")
                
        else:
            error = result.get('error', 'Unknown error')
            print(f"❌ Error en corroboración: {error}")
        
        print("✅ Resultado de herramientas:")
        print(f"   Success: {result.get('success')}")
        
        if result.get('success'):
            tools_data = result.get('tools', [])
            successful_tools = [t for t in tools_data if t.get('success')]
            failed_tools = [t for t in tools_data if not t.get('success')]
            
            print(f"   Total herramientas: {len(tools_data)}")
            print(f"   Exitosas: {len(successful_tools)}")
            print(f"   Fallidas: {len(failed_tools)}")
            
            if successful_tools:
                print("\n🟢 HERRAMIENTAS EXITOSAS:")
                for tool in successful_tools[:5]:  # Top 5
                    print(f"   - {tool.get('name', 'unknown')}: {tool.get('evidence_type', 'N/A')}")
            
            if failed_tools:
                print("\n🔴 HERRAMIENTAS FALLIDAS:")
                for tool in failed_tools[:5]:  # Top 5
                    error = tool.get('error', 'Unknown error')
                    print(f"   - {tool.get('name', 'unknown')}: {error}")
            
            # Mostrar métricas agregadas
            aggregate = result.get('aggregate', {})
            if aggregate:
                print(f"\n📊 MÉTRICAS AGREGADAS:")
                print(f"   Support Score: {aggregate.get('support_score', 'N/A')}")
                print(f"   Coverage: {aggregate.get('coverage', 'N/A')}")
                print(f"   Diversity: {aggregate.get('diversity', 'N/A')}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Excepción: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_tools())
