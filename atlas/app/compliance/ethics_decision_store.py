"""
Ethics Decision Store - Almacenamiento persistente de decisiones éticas
"""

import sqlite3
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class EthicsDecisionRecord:
    """Registro de decisión ética para almacenamiento"""
    decision_id: str
    timestamp: datetime
    domain: str
    description: str
    decision: str  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score: int
    allowed: bool
    requires_signature: bool
    escalation_reasons: List[str]
    recommended_actions: List[str]
    user_id: Optional[str] = None
    organization: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class EthicsDecisionStore:
    """Almacén de decisiones éticas con SQLite"""
    
    def __init__(self, db_path: str = "data/ethics_decisions.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self) -> None:
        """Inicializar base de datos y tablas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS ethics_decisions (
                        decision_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        domain TEXT NOT NULL,
                        description TEXT NOT NULL,
                        decision TEXT NOT NULL,
                        risk_score INTEGER NOT NULL,
                        allowed BOOLEAN NOT NULL,
                        requires_signature BOOLEAN NOT NULL,
                        escalation_reasons TEXT NOT NULL,
                        recommended_actions TEXT NOT NULL,
                        user_id TEXT,
                        organization TEXT,
                        metadata TEXT
                    )
                """)
                
                # Índices para consultas eficientes
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON ethics_decisions(timestamp)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_domain 
                    ON ethics_decisions(domain)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_decision 
                    ON ethics_decisions(decision)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_user_id 
                    ON ethics_decisions(user_id)
                """)
                
                conn.commit()
                logger.info(f"Ethics decision store initialized at {self.db_path}")
                
        except Exception as e:
            logger.error(f"Error initializing ethics decision store: {e}")
            raise
    
    def store_decision(self, record: EthicsDecisionRecord) -> None:
        """Almacenar decisión ética"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO ethics_decisions 
                    (decision_id, timestamp, domain, description, decision, risk_score, 
                     allowed, requires_signature, escalation_reasons, recommended_actions,
                     user_id, organization, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.decision_id,
                    record.timestamp.isoformat(),
                    record.domain,
                    record.description,
                    record.decision,
                    record.risk_score,
                    record.allowed,
                    record.requires_signature,
                    json.dumps(record.escalation_reasons),
                    json.dumps(record.recommended_actions),
                    record.user_id,
                    record.organization,
                    json.dumps(record.metadata) if record.metadata else None
                ))
                conn.commit()
                logger.debug(f"Stored ethics decision: {record.decision_id}")
                
        except Exception as e:
            logger.error(f"Error storing ethics decision: {e}")
            raise
    
    def get_decision(self, decision_id: str) -> Optional[EthicsDecisionRecord]:
        """Obtener decisión por ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM ethics_decisions WHERE decision_id = ?
                """, (decision_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_record(row)
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving decision {decision_id}: {e}")
            return None
    
    def get_decisions_by_domain(self, domain: str, limit: int = 100) -> List[EthicsDecisionRecord]:
        """Obtener decisiones por dominio"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM ethics_decisions 
                    WHERE domain = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (domain, limit))
                
                return [self._row_to_record(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error retrieving decisions for domain {domain}: {e}")
            return []
    
    def get_decisions_by_level(self, level: str, limit: int = 100) -> List[EthicsDecisionRecord]:
        """Obtener decisiones por nivel de riesgo"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM ethics_decisions 
                    WHERE decision = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (level, limit))
                
                return [self._row_to_record(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error retrieving decisions for level {level}: {e}")
            return []
    
    def get_recent_decisions(self, hours: int = 24, limit: int = 100) -> List[EthicsDecisionRecord]:
        """Obtener decisiones recientes"""
        try:
            cutoff_time = datetime.now(timezone.utc).timestamp() - (hours * 3600)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM ethics_decisions 
                    WHERE timestamp >= ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (datetime.fromtimestamp(cutoff_time).isoformat(), limit))
                
                return [self._row_to_record(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error retrieving recent decisions: {e}")
            return []
    
    def get_statistics(self, start_date: Optional[datetime] = None, 
                      end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Obtener estadísticas de decisiones"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Filtros de fecha
                date_filter = ""
                params = []
                if start_date:
                    date_filter += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                if end_date:
                    date_filter += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                # Total de decisiones - FIXED: Use parameterized query
                base_query = "SELECT COUNT(*) as total FROM ethics_decisions WHERE 1=1"
                if date_filter:
                    base_query += date_filter
                cursor = conn.execute(base_query, params)
                total = cursor.fetchone()['total']
                
                # Por nivel de decisión - FIXED: Use parameterized query
                query_by_level = """
                    SELECT decision, COUNT(*) as count 
                    FROM ethics_decisions 
                    WHERE 1=1
                """
                if date_filter:
                    query_by_level += date_filter
                query_by_level += " GROUP BY decision"
                cursor = conn.execute(query_by_level, params)
                by_level = {row['decision']: row['count'] for row in cursor.fetchall()}
                
                # Por dominio - FIXED: Use parameterized query
                query_by_domain = """
                    SELECT domain, COUNT(*) as count 
                    FROM ethics_decisions 
                    WHERE 1=1
                """
                if date_filter:
                    query_by_domain += date_filter
                query_by_domain += " GROUP BY domain ORDER BY count DESC LIMIT 10"
                cursor = conn.execute(query_by_domain, params)
                by_domain = {row['domain']: row['count'] for row in cursor.fetchall()}
                
                # Decisiones bloqueadas - FIXED: Use parameterized query
                query_blocked = "SELECT COUNT(*) as blocked FROM ethics_decisions WHERE allowed = 0"
                if date_filter:
                    query_blocked += date_filter
                cursor = conn.execute(query_blocked, params)
                blocked = cursor.fetchone()['blocked']
                
                # Decisiones que requieren firma - FIXED: Use parameterized query
                query_signature = "SELECT COUNT(*) as signature_required FROM ethics_decisions WHERE requires_signature = 1"
                if date_filter:
                    query_signature += date_filter
                cursor = conn.execute(query_signature, params)
                signature_required = cursor.fetchone()['signature_required']
                
                return {
                    'total': total,
                    'blocked': blocked,
                    'blocked_rate': (blocked / total * 100) if total > 0 else 0,
                    'signature_required': signature_required,
                    'by_level': by_level,
                    'by_domain': by_domain
                }
                
        except Exception as e:
            logger.error(f"Error retrieving statistics: {e}")
            return {}
    
    def export_decisions(self, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Exportar decisiones como lista de diccionarios"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Filtros de fecha
                date_filter = ""
                params = []
                if start_date:
                    date_filter += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                if end_date:
                    date_filter += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                # FIXED: Use parameterized query
                query_export = "SELECT * FROM ethics_decisions WHERE 1=1"
                if date_filter:
                    query_export += date_filter
                query_export += " ORDER BY timestamp DESC"
                cursor = conn.execute(query_export, params)
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error exporting decisions: {e}")
            return []
    
    def cleanup_old_decisions(self, days: int = 90) -> int:
        """Limpiar decisiones antiguas (retention policy)"""
        try:
            cutoff_time = datetime.now(timezone.utc).timestamp() - (days * 24 * 3600)
            cutoff_date = datetime.fromtimestamp(cutoff_time).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM ethics_decisions 
                    WHERE timestamp < ?
                """, (cutoff_date,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_count} old ethics decisions")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error cleaning up old decisions: {e}")
            return 0
    
    def _row_to_record(self, row: sqlite3.Row) -> EthicsDecisionRecord:
        """Convertir fila de DB a EthicsDecisionRecord"""
        return EthicsDecisionRecord(
            decision_id=row['decision_id'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            domain=row['domain'],
            description=row['description'],
            decision=row['decision'],
            risk_score=row['risk_score'],
            allowed=bool(row['allowed']),
            requires_signature=bool(row['requires_signature']),
            escalation_reasons=json.loads(row['escalation_reasons']),
            recommended_actions=json.loads(row['recommended_actions']),
            user_id=row['user_id'],
            organization=row['organization'],
            metadata=json.loads(row['metadata']) if row['metadata'] else None
        )


# Instancia global
decision_store = EthicsDecisionStore()
