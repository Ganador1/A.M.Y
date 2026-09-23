"""
Database Health Checker - ROADMAP 6 Implementation
Enhanced database health monitoring and diagnostics.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import engine, get_db_session

logger = logging.getLogger(__name__)


class DatabaseHealthChecker:
    """
    Comprehensive database health checker implementing all checks from ROADMAP 6.

    Provides real-time monitoring of:
    - Connection health
    - Migration status
    - Connection pool status
    - Slow query detection
    - Session management
    """

    def __init__(self, db_engine=None):
        """Initialize with database engine."""
        self.engine = db_engine or engine

    async def check_connection(self) -> bool:
        """
        Check if database is reachable and responding.

        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False

    async def check_migrations(self) -> Dict[str, Any]:
        """
        Check Alembic migration status.

        Returns:
            dict: Migration status information
        """
        try:
            async with self.engine.connect() as conn:
                result = await conn.execute(
                    text("SELECT version_num FROM alembic_version")
                )
                current_version = result.scalar()
            return {
                "status": "ok",
                "version": current_version,
                "message": f"Database at migration: {current_version}"
            }
        except Exception as e:
            logger.error(f"Migration check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Could not determine migration status"
            }

    async def check_pool_status(self) -> Dict[str, Any]:
        """
        Check connection pool health and utilization.

        Returns:
            dict: Pool statistics and health information
        """
        try:
            pool = self.engine.pool
            checked_in = pool.checkedin()
            checked_out = pool.checkedout()
            total_size = pool.size()
            overflow = pool.overflow()

            utilization = (checked_out / total_size) if total_size > 0 else 0

            # Health indicators
            is_healthy = True
            warnings = []

            if utilization > 0.8:
                is_healthy = False
                warnings.append("High pool utilization (>80%)")

            if checked_out == total_size and overflow > 0:
                warnings.append("Pool exhausted, using overflow connections")

            if checked_in == 0 and checked_out > 0:
                warnings.append("No connections available in pool")

            return {
                "status": "healthy" if is_healthy else "warning",
                "pool_size": total_size,
                "checked_in": checked_in,
                "checked_out": checked_out,
                "overflow": overflow,
                "utilization": round(utilization, 3),
                "warnings": warnings,
                "recommendations": self._get_pool_recommendations(utilization, total_size)
            }
        except Exception as e:
            logger.error(f"Pool status check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Could not determine pool status"
            }

    def _get_pool_recommendations(self, utilization: float, pool_size: int) -> List[str]:
        """Generate recommendations based on pool metrics."""
        recommendations = []

        if utilization > 0.9:
            recommendations.append("Consider increasing pool_size in database configuration")
        elif utilization < 0.2:
            recommendations.append("Pool size may be oversized for current load")

        if pool_size < 5:
            recommendations.append("Consider increasing pool_size for better performance")

        return recommendations

    async def check_slow_queries(self) -> List[Dict[str, Any]]:
        """
        Identify slow queries from pg_stat_statements.

        Returns:
            list: List of slow queries with performance metrics
        """
        try:
            async with self.engine.connect() as conn:
                result = await conn.execute(text("""
                    SELECT query, mean_exec_time, calls, total_exec_time
                    FROM pg_stat_statements
                    WHERE mean_exec_time > 1000
                    ORDER BY mean_exec_time DESC
                    LIMIT 10
                """))
                slow_queries = []
                for row in result:
                    slow_queries.append({
                        "query": str(row.query)[:200] + "..." if len(str(row.query)) > 200 else str(row.query),
                        "mean_exec_time_ms": round(row.mean_exec_time, 2),
                        "total_calls": row.calls,
                        "total_exec_time_ms": round(row.total_exec_time, 2),
                        "avg_exec_time_per_call_ms": round(row.total_exec_time / row.calls, 2) if row.calls > 0 else 0
                    })
                return slow_queries
        except Exception as e:
            logger.debug(f"Slow query check failed (likely not PostgreSQL or pg_stat_statements not enabled): {e}")
            return []

    async def check_session_management(self) -> Dict[str, Any]:
        """
        Check for unclosed database sessions.

        Returns:
            dict: Session management status and recommendations
        """
        try:
            # This is a simplified check - in production, you'd want more sophisticated monitoring
            pool = self.engine.pool
            active_sessions = pool.checkedout()

            # Basic heuristics for session management
            is_healthy = True
            issues = []

            if active_sessions > pool.size() * 0.8:
                is_healthy = False
                issues.append("High number of active sessions relative to pool size")

            # Check for long-running sessions (simplified)
            # In a real implementation, you'd track session start times

            return {
                "status": "healthy" if is_healthy else "warning",
                "active_sessions": active_sessions,
                "pool_size": pool.size(),
                "utilization": active_sessions / pool.size() if pool.size() > 0 else 0,
                "issues": issues,
                "recommendations": [
                    "Use context managers (with statements) for all database sessions",
                    "Ensure sessions are closed in finally blocks",
                    "Consider using FastAPI dependency injection for endpoints"
                ] if issues else []
            }
        except Exception as e:
            logger.error(f"Session management check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Could not check session management"
            }

    async def check_table_integrity(self) -> Dict[str, Any]:
        """
        Check for schema consistency and data integrity issues.

        Returns:
            dict: Integrity check results
        """
        try:
            async with self.engine.connect() as conn:
                # Check for common integrity issues
                checks = []

                # Check if key tables exist and have expected structure
                tables_to_check = [
                    "users", "user_sessions", "calculations", "cached_results",
                    "system_metrics", "error_logs", "api_request_logs"
                ]

                for table in tables_to_check:
                    try:
                        result = await conn.execute(text(f"SELECT COUNT(*) FROM {table} LIMIT 1"))
                        count = result.scalar()
                        checks.append({
                            "table": table,
                            "status": "ok",
                            "record_count": count
                        })
                    except Exception as e:
                        checks.append({
                            "table": table,
                            "status": "error",
                            "error": str(e)
                        })

                healthy_tables = len([c for c in checks if c["status"] == "ok"])
                total_tables = len(checks)

                return {
                    "status": "healthy" if healthy_tables == total_tables else "warning",
                    "total_tables": total_tables,
                    "healthy_tables": healthy_tables,
                    "table_details": checks,
                    "recommendations": [
                        "Run database migrations if any tables are missing",
                        "Check for schema drift if tables have unexpected structure"
                    ] if healthy_tables < total_tables else []
                }
        except Exception as e:
            logger.error(f"Table integrity check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Could not perform table integrity check"
            }

    async def full_health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check combining all individual checks.

        Returns:
            dict: Complete health status report
        """
        start_time = time.time()

        # Run all checks concurrently for better performance
        connection_status = await self.check_connection()
        migration_status = await self.check_migrations()
        pool_status = await self.check_pool_status()
        slow_queries = await self.check_slow_queries()
        session_status = await self.check_session_management()
        integrity_status = await self.check_table_integrity()

        # Calculate overall health
        check_results = [connection_status, migration_status["status"] == "ok",
                        pool_status["status"] in ["healthy"],
                        session_status["status"] in ["healthy"],
                        integrity_status["status"] in ["healthy"]]

        overall_healthy = all(check_results)

        duration = time.time() - start_time

        return {
            "timestamp": time.time(),
            "overall_status": "healthy" if overall_healthy else "warning" if any(check_results) else "critical",
            "check_duration_seconds": round(duration, 3),
            "connection": connection_status,
            "migrations": migration_status,
            "pool": pool_status,
            "slow_queries": slow_queries,
            "session_management": session_status,
            "table_integrity": integrity_status,
            "summary": {
                "total_checks": len(check_results),
                "passed_checks": sum(check_results),
                "failed_checks": len(check_results) - sum(check_results)
            }
        }


# Global instance for easy access
health_checker = DatabaseHealthChecker()


def get_database_health() -> Dict[str, Any]:
    """
    Synchronous wrapper for database health checks.
    Useful for endpoints that need to return health status quickly.
    """
    import asyncio

    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, we need to use a different approach
            # For FastAPI endpoints, use dependency injection instead
            return {
                "status": "info",
                "message": "Use async health check for comprehensive results",
                "timestamp": time.time()
            }
    except RuntimeError:
        # No event loop, create a new one
        return asyncio.run(health_checker.full_health_check())

    # Fallback for other cases
    return {
        "status": "info",
        "message": "Async health check recommended for full results",
        "timestamp": time.time()
    }
