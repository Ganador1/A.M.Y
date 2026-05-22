"""Validation Matrix Persistence (MVP)

Snapshots históricos para tracking de tendencias:
- Almacenamiento de scores temporales
- Análisis de tendencias y degradación
- Configuración de intervalos y retención
- API para consultas históricas
"""
from __future__ import annotations
import time
import json
import sqlite3
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import asyncio

from app.validation.cross_validation_matrix import CrossValidationMatrix
from app.config import settings


class ValidationSnapshot:
    """Single snapshot of validation matrix state"""
    
    def __init__(
        self, 
        timestamp: float, 
        total_score: float, 
        integrity_score: float,
        services_count: int, 
        lineage_quality: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.timestamp = timestamp
        self.total_score = total_score
        self.integrity_score = integrity_score
        self.services_count = services_count
        self.lineage_quality = lineage_quality
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "total_score": self.total_score,
            "integrity_score": self.integrity_score,
            "services_count": self.services_count,
            "lineage_quality": self.lineage_quality,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationSnapshot":
        return cls(
            timestamp=data["timestamp"],
            total_score=data["total_score"],
            integrity_score=data["integrity_score"],
            services_count=data["services_count"],
            lineage_quality=data["lineage_quality"],
            metadata=data.get("metadata", {}),
        )


class ValidationMatrixPersistence:
    """Persistence layer for validation matrix snapshots"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.getenv(
            "VALIDATION_MATRIX_DB", 
            "data/validation_matrix.db"
        )
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_db()
        
        # Configuration with safe fallbacks: settings → env → defaults
        self.retention_days = int(os.getenv("VALIDATION_RETENTION_DAYS", getattr(settings, "validation_retention_days", "30")))
        self.snapshot_interval = int(os.getenv("VALIDATION_SNAPSHOT_INTERVAL", getattr(settings, "validation_snapshot_interval", "300")))  # 5 min
    
    def _init_db(self) -> None:
        """Initialize SQLite database"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS validation_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    total_score REAL NOT NULL,
                    integrity_score REAL NOT NULL,
                    services_count INTEGER NOT NULL,
                    lineage_quality REAL NOT NULL,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON validation_snapshots(timestamp)")
            conn.commit()
            conn.close()
    
    def save_snapshot(self, snapshot: ValidationSnapshot) -> bool:
        """Save a validation snapshot"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                conn.execute("""
                    INSERT INTO validation_snapshots 
                    (timestamp, total_score, integrity_score, services_count, lineage_quality, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    snapshot.timestamp,
                    snapshot.total_score,
                    snapshot.integrity_score,
                    snapshot.services_count,
                    snapshot.lineage_quality,
                    json.dumps(snapshot.metadata)
                ))
                conn.commit()
                conn.close()
                return True
        except Exception:  # pragma: no cover
            return False
    
    def get_snapshots(
        self, 
        hours_back: int = 24, 
        limit: int = 100
    ) -> List[ValidationSnapshot]:
        """Get recent snapshots"""
        cutoff = time.time() - (hours_back * 3600)
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT timestamp, total_score, integrity_score, services_count, lineage_quality, metadata
                FROM validation_snapshots 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (cutoff, limit))
            
            snapshots = []
            for row in cursor:
                metadata = json.loads(row["metadata"]) if row["metadata"] else {}
                snapshots.append(ValidationSnapshot(
                    timestamp=row["timestamp"],
                    total_score=row["total_score"],
                    integrity_score=row["integrity_score"],
                    services_count=row["services_count"],
                    lineage_quality=row["lineage_quality"],
                    metadata=metadata
                ))
            
            conn.close()
            return snapshots
    
    def get_trend_analysis(self, hours_back: int = 24) -> Dict[str, Any]:
        """Analyze trends in recent snapshots"""
        snapshots = self.get_snapshots(hours_back)
        
        if len(snapshots) < 2:
            return {
                "trend": "insufficient_data",
                "snapshots_count": len(snapshots),
                "hours_analyzed": hours_back,
            }
        
        # Sort by timestamp (oldest first for trend calculation)
        snapshots.sort(key=lambda s: s.timestamp)
        
        # Calculate trends
        first, last = snapshots[0], snapshots[-1]
        time_diff = last.timestamp - first.timestamp
        
        if time_diff == 0:
            return {"trend": "no_time_difference", "snapshots_count": len(snapshots)}
        
        total_score_trend = (last.total_score - first.total_score) / time_diff
        integrity_trend = (last.integrity_score - first.integrity_score) / time_diff
        
        # Categorize trends
        def trend_category(value: float) -> str:
            if value > 0.002:  # Más sensible para detectar mejoras
                return "improving"
            elif value < -0.002:  # Más sensible para detectar degradación
                return "degrading"
            else:
                return "stable"
        
        return {
            "trend": "analyzed",
            "snapshots_count": len(snapshots),
            "hours_analyzed": hours_back,
            "time_span_hours": time_diff / 3600,
            "total_score": {
                "first": first.total_score,
                "last": last.total_score,
                "trend": trend_category(total_score_trend),
                "rate_per_hour": total_score_trend * 3600,
            },
            "integrity_score": {
                "first": first.integrity_score,
                "last": last.integrity_score,
                "trend": trend_category(integrity_trend),
                "rate_per_hour": integrity_trend * 3600,
            },
            "services_count": {
                "first": first.services_count,
                "last": last.services_count,
                "change": last.services_count - first.services_count,
            },
        }
    
    def cleanup_old_snapshots(self) -> int:
        """Remove snapshots older than retention period"""
        cutoff = time.time() - (self.retention_days * 24 * 3600)
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                "DELETE FROM validation_snapshots WHERE timestamp < ?", 
                (cutoff,)
            )
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            return deleted
    
    def get_stats(self) -> Dict[str, Any]:
        """Get persistence statistics"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            # Count total snapshots
            total = conn.execute("SELECT COUNT(*) as count FROM validation_snapshots").fetchone()["count"]
            
            # Get oldest and newest
            oldest = conn.execute(
                "SELECT MIN(timestamp) as ts FROM validation_snapshots"
            ).fetchone()["ts"]
            newest = conn.execute(
                "SELECT MAX(timestamp) as ts FROM validation_snapshots"
            ).fetchone()["ts"]
            
            conn.close()
            
            return {
                "total_snapshots": total,
                "oldest_timestamp": oldest,
                "newest_timestamp": newest,
                "retention_days": self.retention_days,
                "snapshot_interval": self.snapshot_interval,
                "db_path": self.db_path,
            }


class ValidationMatrixRecorder:
    """Automatic recorder for validation matrix snapshots"""
    
    def __init__(self, persistence: ValidationMatrixPersistence):
        self.persistence = persistence
        self.matrix = CrossValidationMatrix()
        self._last_snapshot = 0.0
    
    def should_record(self) -> bool:
        """Check if enough time has passed for next snapshot"""
        return (time.time() - self._last_snapshot) >= self.persistence.snapshot_interval
    
    def record_current_state(self, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Record current validation matrix state"""
        if not self.should_record():
            return False
        
        try:
            # Try to build the matrix; if it fails, fall back to minimal defaults
            try:
                result = self.matrix.build_matrix()
            except Exception:
                result = {
                    "score": 0.0,
                    "service_count": 0,
                    "flags": []
                }
            
            snapshot = ValidationSnapshot(
                timestamp=time.time(),
                total_score=result.get("score", 0.0),
                integrity_score=result.get("score", 0.0),  # Use total score as proxy
                services_count=result.get("service_count", 0),
                lineage_quality=max(0, 100 - len(result.get("flags", [])) * 10),  # Rough estimate
                metadata=metadata or {"flags": result.get("flags", [])}
            )
            
            success = self.persistence.save_snapshot(snapshot)
            if success:
                self._last_snapshot = time.time()
            return success
            
        except Exception:  # pragma: no cover
            return False


# Global instances
_persistence = ValidationMatrixPersistence()
_recorder = ValidationMatrixRecorder(_persistence)

def get_validation_persistence() -> ValidationMatrixPersistence:
    return _persistence

def get_validation_recorder() -> ValidationMatrixRecorder:
    return _recorder
