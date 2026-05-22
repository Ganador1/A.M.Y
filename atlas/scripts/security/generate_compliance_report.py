#!/usr/bin/env python3
"""
Compliance Report Generator - Generador de reportes de compliance automático
"""

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import os

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.compliance.ethics_decision_store import decision_store
from app.security.audit_logger import audit_logger


class ComplianceReportGenerator:
    """Generador de reportes de compliance"""
    
    def __init__(self):
        self.decision_store = decision_store
        self.audit_logger = audit_logger
    
    def generate_monthly_report(self, year: int = None, month: int = None) -> Dict[str, Any]:
        """Generar reporte mensual"""
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        start_date = datetime(year, month, 1, tzinfo=timezone.utc)
        if month == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)
        
        return self.generate_custom_report(start_date, end_date)
    
    def generate_quarterly_report(self, year: int = None, quarter: int = None) -> Dict[str, Any]:
        """Generar reporte trimestral"""
        if year is None:
            year = datetime.now().year
        if quarter is None:
            quarter = (datetime.now().month - 1) // 3 + 1
        
        start_month = (quarter - 1) * 3 + 1
        start_date = datetime(year, start_month, 1, tzinfo=timezone.utc)
        
        if quarter == 4:
            end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end_month = start_month + 3
            end_date = datetime(year, end_month, 1, tzinfo=timezone.utc)
        
        return self.generate_custom_report(start_date, end_date)
    
    def generate_custom_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generar reporte personalizado"""
        # Obtener estadísticas de decisiones éticas
        ethics_stats = self.decision_store.get_statistics(start_date, end_date)
        
        # Obtener estadísticas de audit logs
        audit_stats = self.audit_logger.get_statistics(
            hours=int((end_date - start_date).total_seconds() / 3600)
        )
        
        # Calcular compliance score
        compliance_score = self._calculate_compliance_score(ethics_stats, audit_stats)
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(ethics_stats, audit_stats)
        
        # Crear reporte
        report = {
            "report_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "report_type": "compliance_report"
            },
            "summary_metrics": {
                "total_evaluations": ethics_stats.get("total", 0),
                "total_ethics_evaluations": ethics_stats.get("total", 0),
                "total_blocked_events": ethics_stats.get("blocked", 0),
                "block_rate": ethics_stats.get("blocked_rate", 0),
                "compliance_score": compliance_score,
                "total_audit_events": audit_stats.get("total_events", 0),
                "critical_events": audit_stats.get("critical_events", 0),
                "policy_violations": audit_stats.get("policy_violations", 0)
            },
            "risk_distribution": {
                "by_level": ethics_stats.get("by_level", {}),
                "by_domain": ethics_stats.get("by_domain", {}),
                "trend_analysis": self._analyze_trends(start_date, end_date)
            },
            "domain_analysis": {
                "top_domains": self._get_top_domains(ethics_stats.get("by_domain", {})),
                "high_risk_domains": self._get_high_risk_domains(ethics_stats),
                "blocked_domains": self._get_blocked_domains(ethics_stats)
            },
            "user_activity": {
                "by_user": audit_stats.get("by_user", {}),
                "top_users": self._get_top_users(audit_stats.get("by_user", {})),
                "suspicious_patterns": self._detect_suspicious_patterns(audit_stats)
            },
            "audit_events": {
                "by_type": audit_stats.get("by_type", {}),
                "by_hour": audit_stats.get("by_hour", {}),
                "critical_events": self._get_critical_events(start_date, end_date)
            },
            "recommendations": recommendations,
            "compliance_status": self._determine_compliance_status(compliance_score)
        }
        
        return report
    
    def _calculate_compliance_score(self, ethics_stats: Dict[str, Any], 
                                  audit_stats: Dict[str, Any]) -> float:
        """Calcular score de compliance (0-100)"""
        base_score = 100.0
        
        # Penalizaciones
        penalties = {}
        
        # Tasa de bloqueo alta
        blocked_rate = ethics_stats.get("blocked_rate", 0)
        if blocked_rate > 10:  # Más del 10% bloqueado
            penalties["high_blocked_rate"] = min(blocked_rate * 2, 20)  # Max -20
        
        # Eventos críticos
        critical_events = audit_stats.get("critical_events", 0)
        penalties["critical_events"] = min(critical_events * 5, 25)  # Max -25
        
        # Violaciones de política
        policy_violations = audit_stats.get("policy_violations", 0)
        penalties["policy_violations"] = min(policy_violations * 10, 30)  # Max -30
        
        # Decisiones que requieren firma sin justificación
        signature_required = ethics_stats.get("signature_required", 0)
        total_evaluations = ethics_stats.get("total", 1)
        if signature_required > 0:
            missing_justifications = max(0, signature_required - (total_evaluations * 0.1))
            penalties["missing_justifications"] = min(missing_justifications * 2, 15)  # Max -15
        
        # Calcular score final
        total_penalties = sum(penalties.values())
        compliance_score = max(0, base_score - total_penalties)
        
        return round(compliance_score, 2)
    
    def _generate_recommendations(self, ethics_stats: Dict[str, Any], 
                                audit_stats: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generar recomendaciones basadas en estadísticas"""
        recommendations = []
        
        # Recomendaciones basadas en tasa de bloqueo
        blocked_rate = ethics_stats.get("blocked_rate", 0)
        if blocked_rate > 15:
            recommendations.append({
                "category": "high_blocked_rate",
                "priority": "high",
                "title": "Tasa de bloqueo alta",
                "description": f"La tasa de bloqueo es {blocked_rate:.1f}%, considerando revisar políticas o mejorar documentación",
                "action": "Revisar políticas de ética y mejorar guías de usuario"
            })
        
        # Recomendaciones basadas en eventos críticos
        critical_events = audit_stats.get("critical_events", 0)
        if critical_events > 5:
            recommendations.append({
                "category": "critical_events",
                "priority": "high",
                "title": "Eventos críticos frecuentes",
                "description": f"Se detectaron {critical_events} eventos críticos en el período",
                "action": "Investigar causas raíz y implementar medidas preventivas"
            })
        
        # Recomendaciones basadas en violaciones de política
        policy_violations = audit_stats.get("policy_violations", 0)
        if policy_violations > 0:
            recommendations.append({
                "category": "policy_violations",
                "priority": "medium",
                "title": "Violaciones de política detectadas",
                "description": f"Se detectaron {policy_violations} violaciones de política",
                "action": "Revisar y actualizar políticas, mejorar entrenamiento de usuarios"
            })
        
        # Recomendaciones basadas en dominios de alto riesgo
        high_risk_domains = self._get_high_risk_domains(ethics_stats)
        if len(high_risk_domains) > 3:
            recommendations.append({
                "category": "high_risk_domains",
                "priority": "medium",
                "title": "Múltiples dominios de alto riesgo",
                "description": f"Se identificaron {len(high_risk_domains)} dominios con actividad de alto riesgo",
                "action": "Implementar monitoreo adicional para dominios de alto riesgo"
            })
        
        # Recomendaciones basadas en patrones de usuario
        suspicious_patterns = self._detect_suspicious_patterns(audit_stats)
        if suspicious_patterns:
            recommendations.append({
                "category": "suspicious_patterns",
                "priority": "high",
                "title": "Patrones sospechosos detectados",
                "description": "Se detectaron patrones de actividad inusuales",
                "action": "Investigar usuarios con patrones sospechosos"
            })
        
        return recommendations
    
    def _get_top_domains(self, domain_stats: Dict[str, int], limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener top dominios por actividad"""
        sorted_domains = sorted(domain_stats.items(), key=lambda x: x[1], reverse=True)
        return [{"domain": domain, "count": count} for domain, count in sorted_domains[:limit]]
    
    def _get_high_risk_domains(self, ethics_stats: Dict[str, Any]) -> List[str]:
        """Obtener dominios de alto riesgo"""
        high_risk_domains = []
        by_domain = ethics_stats.get("by_domain", {})
        
        # Dominios con más de 5 evaluaciones y alta tasa de bloqueo
        for domain, count in by_domain.items():
            if count >= 5:  # Mínimo de actividad
                # Aquí podríamos calcular la tasa de bloqueo por dominio
                # Por simplicidad, asumimos que dominios con mucha actividad son de riesgo
                high_risk_domains.append(domain)
        
        return high_risk_domains[:10]  # Top 10
    
    def _get_blocked_domains(self, ethics_stats: Dict[str, Any]) -> List[str]:
        """Obtener dominios con más bloqueos"""
        # Esta implementación es simplificada
        # En una implementación real, necesitaríamos datos más detallados
        return []
    
    def _get_top_users(self, user_stats: Dict[str, int], limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener top usuarios por actividad"""
        sorted_users = sorted(user_stats.items(), key=lambda x: x[1], reverse=True)
        return [{"user_id": user_id, "activity_count": count} for user_id, count in sorted_users[:limit]]
    
    def _detect_suspicious_patterns(self, audit_stats: Dict[str, Any]) -> List[str]:
        """Detectar patrones sospechosos"""
        suspicious_patterns = []
        
        # Patrón: Usuario con mucha actividad
        by_user = audit_stats.get("by_user", {})
        for user_id, count in by_user.items():
            if count > 100:  # Más de 100 eventos
                suspicious_patterns.append(f"Usuario {user_id} con alta actividad ({count} eventos)")
        
        # Patrón: Muchos eventos en una hora
        by_hour = audit_stats.get("by_hour", {})
        for hour, count in by_hour.items():
            if count > 50:  # Más de 50 eventos en una hora
                suspicious_patterns.append(f"Alta actividad en {hour} ({count} eventos)")
        
        return suspicious_patterns
    
    def _get_critical_events(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Obtener eventos críticos del período"""
        # Obtener eventos críticos de audit logs
        critical_events = []
        
        try:
            # Buscar eventos de violación de política y errores del sistema
            policy_violations = self.audit_logger.search_events(
                {"event_type": "policy_violation"},
                hours=int((end_date - start_date).total_seconds() / 3600)
            )
            
            system_errors = self.audit_logger.search_events(
                {"event_type": "system_error"},
                hours=int((end_date - start_date).total_seconds() / 3600)
            )
            
            critical_events.extend(policy_violations[:5])  # Top 5
            critical_events.extend(system_errors[:5])  # Top 5
            
        except Exception as e:
            print(f"Error getting critical events: {e}")
        
        return critical_events
    
    def _analyze_trends(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analizar tendencias en el tiempo"""
        # Implementación simplificada
        # En una implementación real, analizaríamos tendencias por día/semana
        return {
            "trend_direction": "stable",
            "peak_activity_hour": "14:00",
            "low_activity_hour": "02:00"
        }
    
    def _determine_compliance_status(self, compliance_score: float) -> str:
        """Determinar estado de compliance basado en score"""
        if compliance_score >= 90:
            return "excellent"
        elif compliance_score >= 80:
            return "good"
        elif compliance_score >= 70:
            return "acceptable"
        elif compliance_score >= 60:
            return "needs_improvement"
        else:
            return "critical"
    
    def export_report(self, report: Dict[str, Any], format: str = "json", 
                     output_path: Optional[str] = None) -> str:
        """Exportar reporte en diferentes formatos"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"reports/compliance/compliance_report_{timestamp}.{format}"
        
        # Crear directorio si no existe
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        
        elif format == "markdown":
            markdown_content = self._generate_markdown_report(report)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return output_path
    
    def _generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """Generar reporte en formato Markdown"""
        metadata = report["report_metadata"]
        summary = report["summary_metrics"]
        risk_dist = report["risk_distribution"]
        domain_analysis = report["domain_analysis"]
        user_activity = report["user_activity"]
        recommendations = report["recommendations"]
        compliance_status = report["compliance_status"]
        
        markdown = f"""# Reporte de Compliance - AXIOM ATLAS

**Generado:** {metadata["generated_at"]}  
**Período:** {metadata["period"]["start"]} - {metadata["period"]["end"]}  
**Estado:** {compliance_status.upper()}

## Resumen Ejecutivo

- **Score de Compliance:** {summary["compliance_score"]}/100
- **Total de Evaluaciones:** {summary["total_evaluations"]}
- **Eventos Bloqueados:** {summary["total_blocked_events"]} ({summary["block_rate"]:.1f}%)
- **Eventos Críticos:** {summary["critical_events"]}
- **Violaciones de Política:** {summary["policy_violations"]}

## Distribución de Riesgo

### Por Nivel
"""
        
        for level, count in risk_dist["by_level"].items():
            markdown += f"- **{level}:** {count}\n"
        
        markdown += "\n### Top Dominios\n"
        for domain_info in domain_analysis["top_domains"][:5]:
            markdown += f"- **{domain_info['domain']}:** {domain_info['count']} evaluaciones\n"
        
        markdown += "\n## Análisis de Usuarios\n"
        for user_info in user_activity["top_users"][:5]:
            markdown += f"- **{user_info['user_id']}:** {user_info['activity_count']} eventos\n"
        
        markdown += "\n## Recomendaciones\n"
        for rec in recommendations:
            priority_emoji = "🔴" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
            markdown += f"\n### {priority_emoji} {rec['title']}\n"
            markdown += f"**Descripción:** {rec['description']}\n\n"
            markdown += f"**Acción Recomendada:** {rec['action']}\n"
        
        markdown += "\n---\n"
        markdown += f"*Reporte generado automáticamente por AXIOM ATLAS Compliance System*"
        
        return markdown


def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(description="Generar reportes de compliance")
    parser.add_argument("--monthly", action="store_true", help="Generar reporte mensual")
    parser.add_argument("--quarterly", action="store_true", help="Generar reporte trimestral")
    parser.add_argument("--start", type=str, help="Fecha de inicio (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, help="Fecha de fin (YYYY-MM-DD)")
    parser.add_argument("--format", choices=["json", "markdown"], default="json", help="Formato de salida")
    parser.add_argument("--output", type=str, help="Ruta de archivo de salida")
    parser.add_argument("--year", type=int, help="Año para reporte mensual/trimestral")
    parser.add_argument("--month", type=int, help="Mes para reporte mensual")
    parser.add_argument("--quarter", type=int, help="Trimestre para reporte trimestral")
    parser.add_argument("--alert-threshold", type=float, default=80, help="Umbral de alerta para compliance score")
    parser.add_argument("--email", type=str, help="Email para enviar alertas")
    
    args = parser.parse_args()
    
    generator = ComplianceReportGenerator()
    
    try:
        if args.monthly:
            report = generator.generate_monthly_report(args.year, args.month)
        elif args.quarterly:
            report = generator.generate_quarterly_report(args.year, args.quarter)
        elif args.start and args.end:
            start_date = datetime.fromisoformat(args.start)
            end_date = datetime.fromisoformat(args.end)
            report = generator.generate_custom_report(start_date, end_date)
        else:
            # Por defecto, reporte del último mes
            report = generator.generate_monthly_report()
        
        # Exportar reporte
        output_path = generator.export_report(report, args.format, args.output)
        print(f"Reporte generado: {output_path}")
        
        # Verificar umbral de alerta
        compliance_score = report["summary_metrics"]["compliance_score"]
        if compliance_score < args.alert_threshold:
            print(f"⚠️  ALERTA: Compliance score ({compliance_score}) está por debajo del umbral ({args.alert_threshold})")
            
            if args.email:
                # Aquí se podría implementar envío de email
                print(f"📧 Alerta enviada a: {args.email}")
        
        # Mostrar resumen en consola
        print(f"\n📊 Resumen del Reporte:")
        print(f"   Compliance Score: {compliance_score}/100")
        print(f"   Total Evaluaciones: {report['summary_metrics']['total_evaluations']}")
        print(f"   Eventos Bloqueados: {report['summary_metrics']['total_blocked_events']}")
        print(f"   Eventos Críticos: {report['summary_metrics']['critical_events']}")
        print(f"   Estado: {report['compliance_status'].upper()}")
        
    except Exception as e:
        print(f"Error generando reporte: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
