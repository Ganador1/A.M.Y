#!/usr/bin/env python3
"""
AXIOM - Ciclo de Investigación Autónoma FINAL
=============================================

Script corregido con el payload correcto para los endpoints reales.
"""

import http.client
import json
from datetime import datetime
from typing import Dict, Any, Optional

def log_action(action: str, details: str = ""):
    """Registra las acciones con timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {action}")
    if details:
        print(f"           {details}")

def make_request(method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Realiza peticiones HTTP al servidor con manejo de errores"""
    try:
        conn = http.client.HTTPConnection("localhost", 8002, timeout=30)
        
        headers = {"Content-Type": "application/json"}
        body = json.dumps(data) if data else None
        
        log_action(f"🌐 {method}", f"{endpoint}")
        
        conn.request(method, endpoint, body, headers)
        response = conn.getresponse()
        
        response_data = response.read().decode('utf-8')
        status = response.status
        
        conn.close()
        
        # Intentar parsear como JSON
        try:
            parsed_data = json.loads(response_data)
            return {"status": status, "data": parsed_data}
        except json.JSONDecodeError:
            return {"status": status, "data": response_data}
            
    except Exception as e:
        return {"status": 500, "error": str(e)}

def execute_final_autonomous_cycle():
    """Ejecuta un ciclo de investigación autónoma final con payload correcto"""
    
    print("🔬 AXIOM - Ciclo de Investigación Autónoma FINAL")
    print("=" * 60)
    
    # 1. Verificar que el servidor esté funcionando
    log_action("🔍 VERIFICACIÓN INICIAL", "Checkeando estado del sistema...")
    
    health_response = make_request("GET", "/health")
    if health_response["status"] != 200:
        log_action("❌ ERROR", "Servidor no disponible")
        return False
    
    log_action("✅ Servidor operativo", f"Status: {health_response['status']}")
    
    # 2. Verificar stats del sistema
    stats_response = make_request("GET", "/api/scientific-hypothesis/stats")
    if stats_response["status"] == 200:
        stats = stats_response["data"]
        log_action("📊 Stats del sistema", 
                  f"Hipótesis: {stats.get('total_hypotheses', 0)}, "
                  f"Dominios: {len(stats.get('supported_domains', []))}")
    
    # 3. Generar hipótesis usando payload corregido
    log_action("🧠 GENERACIÓN DE HIPÓTESIS", "Domain: materials_science")
    
    hypothesis_data = {
        "research_question": "¿Cómo puede validarse la capacidad autónoma de investigación en sistemas de ciencia de materiales mediante ciclos integrados de generación, análisis y refinamiento de hipótesis?",
        "domain": "materials_science",
        "focus_area": "autonomous_research_validation", 
        "description": "Validación de capacidades autónomas de investigación en sistemas de ciencia de materiales",
        "initial_confidence": 0.75
    }
    
    hyp_response = make_request("POST", "/api/scientific-hypothesis/generate-hypothesis", hypothesis_data)
    
    if hyp_response["status"] != 200:
        log_action("❌ ERROR", f"Generación falló: {hyp_response}")
        # Intentar con payload mínimo
        log_action("🔄 REINTENTO", "Probando con payload mínimo...")
        minimal_data = {
            "research_question": "Autonomous research validation in materials science",
            "domain": "materials_science"
        }
        hyp_response = make_request("POST", "/api/scientific-hypothesis/generate-hypothesis", minimal_data)
        
        if hyp_response["status"] != 200:
            log_action("❌ ERROR FINAL", f"Segundo intento falló: {hyp_response}")
            return False
    
    hypothesis_id = hyp_response["data"]["id"]
    hypothesis_title = hyp_response["data"].get("title", "Sin título")
    log_action("✅ Hipótesis generada", f"ID: {hypothesis_id}")
    log_action("📄 Título", hypothesis_title)
    
    # 4. Iniciar ciclo de investigación
    log_action("🔄 INICIO DE CICLO", "Iniciando ciclo de investigación...")
    
    cycle_data = {
        "hypothesis_id": hypothesis_id,
        "research_parameters": {
            "evidence_types": ["experimental", "theoretical", "computational"],
            "validation_criteria": ["reproducibility", "statistical_significance"],
            "duration_weeks": 4
        }
    }
    
    cycle_response = make_request("POST", "/api/scientific-hypothesis/start-research-cycle", cycle_data)
    
    if cycle_response["status"] != 200:
        log_action("❌ ERROR", f"Inicio de ciclo falló: {cycle_response}")
        return False
    
    cycle_id = cycle_response["data"]["cycle_id"]
    log_action("✅ Ciclo iniciado", f"Cycle ID: {cycle_id}")
    
    # 5. Analizar evidencia
    log_action("🔍 ANÁLISIS DE EVIDENCIA", "Procesando evidencia disponible...")
    
    evidence_data = {
        "cycle_id": cycle_id,
        "analysis_depth": "comprehensive",
        "include_meta_analysis": True
    }
    
    evidence_response = make_request("POST", "/api/scientific-hypothesis/analyze-evidence", evidence_data)
    
    if evidence_response["status"] != 200:
        log_action("❌ ERROR", f"Análisis de evidencia falló: {evidence_response}")
        return False
    
    evidence_strength = evidence_response["data"]["evidence_strength"]
    evidence_count = evidence_response["data"]["total_evidence"]
    log_action("✅ Evidencia analizada", f"Fuerza: {evidence_strength}, Total: {evidence_count}")
    
    # 6. Refinar hipótesis
    log_action("🧪 REFINAMIENTO", "Refinando hipótesis basado en evidencia...")
    
    refinement_data = {
        "hypothesis_id": hypothesis_id,
        "evidence_data": evidence_response["data"],
        "refinement_approach": "bayesian_update"
    }
    
    refinement_response = make_request("POST", "/api/scientific-hypothesis/refine-hypothesis", refinement_data)
    
    if refinement_response["status"] != 200:
        log_action("❌ ERROR", f"Refinamiento falló: {refinement_response}")
        return False
    
    new_confidence = refinement_response["data"]["updated_confidence"]
    log_action("✅ Hipótesis refinada", f"Nueva confianza: {new_confidence}")
    
    # 7. Obtener información final de la hipótesis
    log_action("📋 INFORMACIÓN FINAL", "Obteniendo detalles de la hipótesis...")
    
    final_hyp_response = make_request("GET", f"/api/scientific-hypothesis/hypothesis/{hypothesis_id}")
    
    if final_hyp_response["status"] == 200:
        final_hyp = final_hyp_response["data"]
        log_action("✅ Hipótesis recuperada", f"Estado: {final_hyp.get('status', 'N/A')}")
    
    # 8. Listar todas las hipótesis
    log_action("📄 LISTADO DE HIPÓTESIS", "Obteniendo lista completa...")
    
    list_response = make_request("GET", "/api/scientific-hypothesis/list-hypotheses")
    
    if list_response["status"] == 200:
        hypotheses_list = list_response["data"]
        total_hyp = len(hypotheses_list.get("hypotheses", []))
        log_action("✅ Lista obtenida", f"Total hipótesis en sistema: {total_hyp}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL CICLO AUTÓNOMO FINAL")
    print("=" * 60)
    
    print(f"🆔 Hipótesis ID: {hypothesis_id}")
    print(f"📄 Título: {hypothesis_title}")
    print(f"🔄 Ciclo ID: {cycle_id}")
    print(f"📈 Confianza inicial: {hypothesis_data.get('initial_confidence', 'N/A')}")
    print(f"📈 Confianza final: {new_confidence}")
    print(f"💪 Fuerza evidencia: {evidence_strength}")
    print(f"📊 Total evidencia: {evidence_count}")
    
    if stats_response["status"] == 200:
        stats = stats_response["data"]
        print("\n🎯 Métricas del Sistema:")
        print(f"   Dominios soportados: {', '.join(stats.get('supported_domains', []))}")
        print(f"   Total hipótesis: {stats.get('total_hypotheses', 'N/A')}")
        print(f"   Ciclos activos: {stats.get('active_cycles', 'N/A')}")
    
    print("\n🏆 RESULTADO: CICLO AUTÓNOMO FINAL COMPLETADO EXITOSAMENTE")
    print("✅ Hipótesis generada y procesada")
    print("✅ Ciclo de investigación iniciado")
    print("✅ Evidencia analizada y refinamiento aplicado")
    print("✅ Sistema respondiendo con datos reales")
    print("✅ Investigación autónoma funcional")
    
    return True

if __name__ == "__main__":
    try:
        success = execute_final_autonomous_cycle()
        if success:
            print("\n🎉 ÉXITO: Ciclo autónomo final completado")
            print("🚀 Sistema AXIOM funcionando con capacidades autónomas completas")
        else:
            print("\n❌ FALLO: El ciclo no pudo completarse")
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()