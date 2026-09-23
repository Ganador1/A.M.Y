#!/usr/bin/env python3
"""
Security Report Generator - Generador de reportes de seguridad
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import os

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.security.audit_logger import audit_logger


class SecurityReportGenerator:
    """Generador de reportes de seguridad"""
    
    def __init__(self):
        self.audit_logger = audit_logger
    
    def generate_security_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generar reporte de seguridad"""
        # Obtener estadísticas de audit logs
        audit_stats = self.audit_logger.get_statistics(hours)
        
        # Obtener eventos recientes
        recent_events = self.audit_logger.get_recent_events(hours)
        
        # Analizar eventos críticos
        critical_events = self._analyze_critical_events(recent_events)
        
        # Detectar patrones sospechosos
        suspicious_patterns = self._detect_suspicious_patterns(recent_events)
        
        # Generar recomendaciones
        recommendations = self._generate_security_recommendations(audit_stats, critical_events, suspicious_patterns)
        
        # Crear reporte
        report = {
            "report_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "period_hours": hours,
                "report_type": "security_report"
            },
            "summary": {
                "total_events": audit_stats.get("total_events", 0),
                "critical_events": audit_stats.get("critical_events", 0),
                "policy_violations": audit_stats.get("policy_violations", 0),
                "suspicious_patterns": len(suspicious_patterns)
            },
            "event_analysis": {
                "by_type": audit_stats.get("by_type", {}),
                "by_user": audit_stats.get("by_user", {}),
                "by_hour": audit_stats.get("by_hour", {})
            },
            "critical_events": critical_events,
            "suspicious_patterns": suspicious_patterns,
            "recommendations": recommendations,
            "security_status": self._determine_security_status(audit_stats, critical_events, suspicious_patterns)
        }
        
        return report
    
    def _analyze_critical_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analizar eventos críticos"""
        critical_events = []
        
        for event in events:
            event_type = event.get("event_type", "")
            details = event.get("details", {})
            
            # Eventos de violación de política
            if event_type == "policy_violation":
                severity = details.get("severity", "medium")
                if severity in ["high", "critical"]:
                    critical_events.append({
                        "type": "policy_violation",
                        "severity": severity,
                        "description": details.get("description", ""),
                        "policy_name": details.get("policy_name", ""),
                        "timestamp": event.get("timestamp", ""),
                        "user_id": event.get("user_id", "unknown")
                    })
            
            # Eventos de error del sistema
            elif event_type == "system_error":
                severity = details.get("severity", "medium")
                if severity in ["high", "critical"]:
                    critical_events.append({
                        "type": "system_error",
                        "severity": severity,
                        "description": details.get("error_message", ""),
                        "component": details.get("component", ""),
                        "timestamp": event.get("timestamp", ""),
                        "error_type": details.get("error_type", "")
                    })
            
            # Evaluaciones éticas de alto riesgo
            elif event_type == "ethics_evaluation":
                decision = details.get("decision", "")
                if decision in ["HIGH", "CRITICAL"]:
                    critical_events.append({
                        "type": "high_risk_ethics",
                        "severity": "high" if decision == "HIGH" else "critical",
                        "description": f"High-risk ethics evaluation: {details.get('domain', '')}",
                        "domain": details.get("domain", ""),
                        "risk_score": details.get("risk_score", 0),
                        "timestamp": event.get("timestamp", ""),
                        "user_id": event.get("user_id", "unknown")
                    })
        
        return critical_events
    
    def _detect_suspicious_patterns(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detectar patrones sospechosos"""
        suspicious_patterns = []
        
        # Agrupar eventos por usuario
        user_events = {}
        for event in events:
            user_id = event.get("user_id", "anonymous")
            if user_id not in user_events:
                user_events[user_id] = []
            user_events[user_id].append(event)
        
        # Detectar patrones por usuario
        for user_id, user_event_list in user_events.items():
            if len(user_event_list) > 50:  # Mucha actividad
                suspicious_patterns.append({
                    "pattern_type": "high_activity",
                    "description": f"Usuario {user_id} con alta actividad ({len(user_event_list)} eventos)",
                    "user_id": user_id,
                    "event_count": len(user_event_list),
                    "severity": "medium"
                })
            
            # Detectar múltiples violaciones de política
            policy_violations = [e for e in user_event_list if e.get("event_type") == "policy_violation"]
            if len(policy_violations) > 3:
                suspicious_patterns.append({
                    "pattern_type": "multiple_policy_violations",
                    "description": f"Usuario {user_id} con múltiples violaciones de política ({len(policy_violations)})",
                    "user_id": user_id,
                    "violation_count": len(policy_violations),
                    "severity": "high"
                })
        
        return suspicious_patterns
    
    def _generate_security_recommendations(self, audit_stats: Dict[str, Any], 
                                         critical_events: List[Dict[str, Any]], 
                                         suspicious_patterns: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generar recomendaciones de seguridad"""
        recommendations = []
        
        # Recomendaciones basadas en eventos críticos
        if critical_events:
            critical_count = len([e for e in critical_events if e.get("severity") == "critical"])
            high_count = len([e for e in critical_events if e.get("severity") == "high"])
            
            if critical_count > 0:
                recommendations.append({
                    "category": "critical_events",
                    "priority": "critical",
                    "title": "Eventos críticos detectados",
                    "description": f"Se detectaron {critical_count} eventos críticos que requieren atención inmediata",
                    "action": "Investigar y resolver eventos críticos inmediatamente"
                })
            
            if high_count > 0:
                recommendations.append({
                    "category": "high_events",
                    "priority": "high",
                    "title": "Eventos de alto riesgo",
                    "description": f"Se detectaron {high_count} eventos de alto riesgo",
                    "action": "Priorizar la investigación de eventos de alto riesgo"
                })
        
        # Recomendaciones basadas en patrones sospechosos
        if suspicious_patterns:
            high_severity_patterns = [p for p in suspicious_patterns if p.get("severity") == "high"]
            if high_severity_patterns:
                recommendations.append({
                    "category": "suspicious_patterns",
                    "priority": "high",
                    "title": "Patrones sospechosos detectados",
                    "description": f"Se detectaron {len(high_severity_patterns)} patrones de alta severidad",
                    "action": "Investigar usuarios con patrones sospechosos y considerar restricciones"
                })
        
        return recommendations
    
    def _determine_security_status(self, audit_stats: Dict[str, Any], 
                                 critical_events: List[Dict[str, Any]], 
                                 suspicious_patterns: List[Dict[str, Any]]) -> str:
        """Determinar estado de seguridad"""
        critical_count = len([e for e in critical_events if e.get("severity") == "critical"])
        high_count = len([e for e in critical_events if e.get("severity") == "high"])
        high_severity_patterns = len([p for p in suspicious_patterns if p.get("severity") == "high"])
        
        if critical_count > 0:
            return "critical"
        elif high_count > 2 or high_severity_patterns > 1:
            return "high_risk"
        elif high_count > 0 or high_severity_patterns > 0:
            return "medium_risk"
        else:
            return "secure"


def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(description="Generar reportes de seguridad")
    parser.add_argument("--hours", type=int, default=24, help="Horas a analizar (default: 24)")
    parser.add_argument("--format", choices=["json", "markdown"], default="json", help="Formato de salida")
    parser.add_argument("--output", type=str, help="Ruta de archivo de salida")
    
    args = parser.parse_args()
    
    generator = SecurityReportGenerator()
    
    try:
        # Generar reporte
        report = generator.generate_security_report(args.hours)
        
        # Exportar reporte
        if args.format == "json":
            if args.output:
                output_path = args.output
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"reports/security/security_report_{timestamp}.json"
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"Reporte de seguridad generado: {output_path}")
        
        # Mostrar resumen en consola
        summary = report["summary"]
        security_status = report["security_status"]
        
        print(f"\n🔒 Resumen del Reporte de Seguridad:")
        print(f"   Estado: {security_status.upper()}")
        print(f"   Total Eventos: {summary['total_events']}")
        print(f"   Eventos Críticos: {summary['critical_events']}")
        print(f"   Violaciones de Política: {summary['policy_violations']}")
        print(f"   Patrones Sospechosos: {summary['suspicious_patterns']}")
        
        # Mostrar alertas si hay eventos críticos
        if summary['critical_events'] > 0:
            print(f"\n🚨 ALERTA: Se detectaron {summary['critical_events']} eventos críticos")
        
        if summary['suspicious_patterns'] > 0:
            print(f"⚠️ ALERTA: Se detectaron {summary['suspicious_patterns']} patrones sospechosos")
        
    except Exception as e:
        print(f"Error generando reporte de seguridad: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
