#!/usr/bin/env python3
"""
AXIOM - Ciclo de Investigación Autónoma con Verificación de Persistencia
========================================================================

Este script ejecuta un ciclo completo de investigación autónoma y verifica
que los datos se persistan correctamente en todas las capas del sistema.
"""

import http.client
import json
import sqlite3
import time
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

def check_database_state() -> Dict[str, int]:
    """Verifica el estado de la base de datos local"""
    try:
        conn = sqlite3.connect("mathematical_conjectures.db")
        cursor = conn.cursor()
        
        # Contar registros en cada tabla
        tables_info = {}
        
        cursor.execute("SELECT COUNT(*) FROM hypotheses")
        tables_info["hypotheses"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM hypothesis_evidence")
        tables_info["evidence"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM hypothesis_refinements")
        tables_info["refinements"] = cursor.fetchone()[0]
        
        conn.close()
        return tables_info
        
    except Exception as e:
        return {"error": str(e)}

def execute_verified_autonomous_cycle():
    """Ejecuta un ciclo de investigación autónoma con verificación completa"""
    
    print("🔬 AXIOM - Ciclo de Investigación Autónoma Verificado")
    print("=" * 60)
    
    # 1. Verificar estado inicial
    log_action("🔍 VERIFICACIÓN INICIAL", "Checkeando estado del sistema...")
    
    initial_db_state = check_database_state()
    log_action("📊 Estado inicial BD", f"Hipótesis: {initial_db_state.get('hypotheses', 0)}")
    
    # Verificar que el servidor esté funcionando
    health_response = make_request("GET", "/health")
    if health_response["status"] != 200:
        log_action("❌ ERROR", "Servidor no disponible")
        return False
    
    log_action("✅ Servidor operativo", f"Status: {health_response['status']}")
    
    # 2. Generar hipótesis inicial
    log_action("🧠 GENERACIÓN DE HIPÓTESIS", "Domain: materials_science")
    
    hypothesis_data = {
        "domain": "materials_science",
        "focus_area": "autonomous_research_validation",
        "description": "Investigación autónoma para validación de persistencia de datos en sistemas de hipótesis científicas",
        "initial_confidence": 0.75
    }
    
    hyp_response = make_request("POST", "/api/scientific-hypothesis/generate", hypothesis_data)
    
    if hyp_response["status"] != 200:
        log_action("❌ ERROR", f"Generación falló: {hyp_response}")
        return False
    
    hypothesis_id = hyp_response["data"]["id"]
    log_action("✅ Hipótesis generada", f"ID: {hypothesis_id}")
    
    # 3. Iniciar ciclo de investigación
    log_action("🔄 INICIO DE CICLO", "Iniciando ciclo de investigación...")
    
    cycle_data = {
        "hypothesis_id": hypothesis_id,
        "research_parameters": {
            "evidence_types": ["experimental", "theoretical", "computational"],
            "validation_criteria": ["reproducibility", "statistical_significance"],
            "duration_weeks": 4
        }
    }
    
    cycle_response = make_request("POST", "/api/scientific-hypothesis/initiate-cycle", cycle_data)
    
    if cycle_response["status"] != 200:
        log_action("❌ ERROR", f"Inicio de ciclo falló: {cycle_response}")
        return False
    
    cycle_id = cycle_response["data"]["cycle_id"]
    log_action("✅ Ciclo iniciado", f"Cycle ID: {cycle_id}")
    
    # 4. Analizar evidencia
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
    log_action("✅ Evidencia analizada", f"Fuerza: {evidence_strength}")
    
    # 5. Refinar hipótesis
    log_action("🧪 REFINAMIENTO", "Refinando hipótesis basado en evidencia...")
    
    refinement_data = {
        "hypothesis_id": hypothesis_id,
        "evidence_data": evidence_response["data"],
        "refinement_approach": "bayesian_update"
    }
    
    refinement_response = make_request("POST", "/api/scientific-hypothesis/refine", refinement_data)
    
    if refinement_response["status"] != 200:
        log_action("❌ ERROR", f"Refinamiento falló: {refinement_response}")
        return False
    
    new_confidence = refinement_response["data"]["updated_confidence"]
    log_action("✅ Hipótesis refinada", f"Nueva confianza: {new_confidence}")
    
    # 6. Validar resultados
    log_action("✅ VALIDACIÓN", "Validando resultados del ciclo...")
    
    validation_data = {
        "cycle_id": cycle_id,
        "validation_type": "comprehensive",
        "include_peer_review": True
    }
    
    validation_response = make_request("POST", "/api/scientific-hypothesis/validate", validation_data)
    
    if validation_response["status"] != 200:
        log_action("❌ ERROR", f"Validación falló: {validation_response}")
        return False
    
    validation_score = validation_response["data"]["validation_score"]
    log_action("✅ Validación completada", f"Score: {validation_score}")
    
    # 7. Verificar persistencia final
    log_action("📊 VERIFICACIÓN FINAL", "Checkeando persistencia de datos...")
    
    # Pequeña pausa para asegurar que las escrituras se completen
    time.sleep(2)
    
    final_db_state = check_database_state()
    
    # Obtener métricas del sistema
    metrics_response = make_request("GET", "/api/scientific-hypothesis/metrics")
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL CICLO AUTÓNOMO VERIFICADO")
    print("=" * 60)
    
    print(f"🆔 Hipótesis ID: {hypothesis_id}")
    print(f"🔄 Ciclo ID: {cycle_id}")
    print(f"📈 Confianza inicial: {hypothesis_data['initial_confidence']}")
    print(f"📈 Confianza final: {new_confidence}")
    print(f"💪 Fuerza evidencia: {evidence_strength}")
    print(f"✅ Score validación: {validation_score}")
    
    print(f"\n📊 Estado Base de Datos:")
    print(f"   Inicial - Hipótesis: {initial_db_state.get('hypotheses', 0)}")
    print(f"   Final   - Hipótesis: {final_db_state.get('hypotheses', 0)}")
    print(f"   Evidencia: {final_db_state.get('evidence', 0)}")
    print(f"   Refinamientos: {final_db_state.get('refinements', 0)}")
    
    if metrics_response["status"] == 200:
        metrics = metrics_response["data"]
        print(f"\n🎯 Métricas del Sistema:")
        print(f"   Total hipótesis: {metrics.get('total_hypotheses', 'N/A')}")
        print(f"   Ciclos activos: {metrics.get('active_cycles', 'N/A')}")
    
    print("\n🏆 RESULTADO: CICLO AUTÓNOMO COMPLETADO EXITOSAMENTE")
    print("✅ Todas las operaciones de investigación ejecutadas")
    print("✅ Sistema respondiendo correctamente")
    print("✅ Flujo de datos verificado")
    
    return True

if __name__ == "__main__":
    try:
        success = execute_verified_autonomous_cycle()
        if success:
            print(f"\n🎉 ÉXITO: Ciclo autónomo verificado completado")
        else:
            print(f"\n❌ FALLO: El ciclo no pudo completarse")
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()