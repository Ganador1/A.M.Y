"""
Reproducibility Database - AXIOM META 4
Database system for tracking reproducibility experiments and analyzing failure patterns.
"""

from __future__ import annotations

import json
import sqlite3
import pandas as pd
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.bootstrap_logging import logger
from app.services.base_service import BaseService
from app.exceptions.infrastructure.database import DatabaseError
from app.types.reproducibility_database_types import (
    ProcessRequestResult,
    RecordAttemptResult,
    GetAttemptResult,
    ListAttemptsResult,
    AnalyzeFailurePatternsResult,
    GenerateRecommendationsResult,
    GetStatisticsResult,
    SearchSimilarExperimentsResult,
    CalculateStatisticsResult,
)


@dataclass
class ReproducibilityAttempt:
    """Record of a reproducibility attempt"""
    attempt_id: str
    paper_id: str
    paper_title: str
    experiment_type: str
    parameters: Dict[str, Any]
    success: bool
    reproducibility_score: float
    execution_time: float
    error_message: Optional[str] = None
    variations_count: int = 1
    confidence_level: float = 0.95
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class FailurePattern:
    """Pattern identified in reproducibility failures"""
    pattern_id: str
    pattern_type: str  # 'parameter', 'method', 'equipment', 'environment'
    description: str
    frequency: int
    affected_experiments: List[str]
    common_factors: Dict[str, Any]
    recommendations: List[str]
    confidence: float
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ReproducibilityRecommendation:
    """Recommendation for improving reproducibility"""
    recommendation_id: str
    experiment_type: str
    recommendation_type: str  # 'parameter_control', 'method_improvement', 'equipment_upgrade', 'protocol_change'
    title: str
    description: str
    priority: str  # 'high', 'medium', 'low'
    expected_improvement: float
    implementation_effort: str  # 'low', 'medium', 'high'
    evidence_count: int
    created_at: datetime = field(default_factory=datetime.now)


class ReproducibilityDatabase(BaseService):
    """Database system for tracking and analyzing reproducibility experiments"""
    
    def __init__(self, db_path: str = "reproducibility.db"):
        super().__init__("ReproducibilityDatabase")
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._initialize_database()
        
        # Initialize thread pool for database operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info("✅ ReproducibilityDatabase initialized")
    
    def _initialize_database(self):
        """Initialize SQLite database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create reproducibility_attempts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS reproducibility_attempts (
                        attempt_id TEXT PRIMARY KEY,
                        paper_id TEXT NOT NULL,
                        paper_title TEXT NOT NULL,
                        experiment_type TEXT NOT NULL,
                        parameters TEXT NOT NULL,
                        success BOOLEAN NOT NULL,
                        reproducibility_score REAL NOT NULL,
                        execution_time REAL NOT NULL,
                        error_message TEXT,
                        variations_count INTEGER DEFAULT 1,
                        confidence_level REAL DEFAULT 0.95,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP
                    )
                """)
                
                # Create failure_patterns table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS failure_patterns (
                        pattern_id TEXT PRIMARY KEY,
                        pattern_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        frequency INTEGER NOT NULL,
                        affected_experiments TEXT NOT NULL,
                        common_factors TEXT NOT NULL,
                        recommendations TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create recommendations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS reproducibility_recommendations (
                        recommendation_id TEXT PRIMARY KEY,
                        experiment_type TEXT NOT NULL,
                        recommendation_type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        expected_improvement REAL NOT NULL,
                        implementation_effort TEXT NOT NULL,
                        evidence_count INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_attempts_paper_id ON reproducibility_attempts(paper_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_attempts_success ON reproducibility_attempts(success)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_attempts_experiment_type ON reproducibility_attempts(experiment_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_patterns_type ON failure_patterns(pattern_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_recommendations_type ON reproducibility_recommendations(experiment_type)")
                
                conn.commit()
                
        except DatabaseError as e:
            logger.error(f"❌ Error initializing database: {e}")
            raise
    
    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process reproducibility database requests"""
        try:
            action = request_data.get("action", "")
            
            if action == "record_attempt":
                return await self.record_attempt(request_data)
            elif action == "get_attempt":
                return await self.get_attempt(request_data)
            elif action == "list_attempts":
                return await self.list_attempts(request_data)
            elif action == "analyze_failure_patterns":
                return await self.analyze_failure_patterns(request_data)
            elif action == "generate_recommendations":
                return await self.generate_recommendations(request_data)
            elif action == "get_statistics":
                return await self.get_statistics(request_data)
            elif action == "search_similar_experiments":
                return await self.search_similar_experiments(request_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "record_attempt", "get_attempt", "list_attempts",
                        "analyze_failure_patterns", "generate_recommendations",
                        "get_statistics", "search_similar_experiments"
                    ]
                }
                
        except DatabaseError as e:
            return self.handle_error(e, "process_request")
    
    async def record_attempt(self, request_data: RecordAttemptResult) -> RecordAttemptResult:
        """Record a reproducibility attempt"""
        try:
            attempt_data = request_data.get("attempt_data", {})
            
            # Create ReproducibilityAttempt object
            attempt = ReproducibilityAttempt(
                attempt_id=attempt_data["attempt_id"],
                paper_id=attempt_data["paper_id"],
                paper_title=attempt_data["paper_title"],
                experiment_type=attempt_data["experiment_type"],
                parameters=attempt_data["parameters"],
                success=attempt_data["success"],
                reproducibility_score=attempt_data["reproducibility_score"],
                execution_time=attempt_data["execution_time"],
                error_message=attempt_data.get("error_message"),
                variations_count=attempt_data.get("variations_count", 1),
                confidence_level=attempt_data.get("confidence_level", 0.95),
                completed_at=datetime.now() if attempt_data["success"] else None
            )
            
            # Insert into database
            await self._insert_attempt(attempt)
            
            logger.info(f"✅ Recorded reproducibility attempt: {attempt.attempt_id}")
            
            return {
                "success": True,
                "attempt_id": attempt.attempt_id,
                "recorded_at": attempt.created_at.isoformat()
            }
            
        except DatabaseError as e:
            return self.handle_error(e, "record_attempt")
    
    async def get_attempt(self, request_data: GetAttemptResult) -> GetAttemptResult:
        """Get details of a specific reproducibility attempt"""
        try:
            attempt_id = request_data.get("attempt_id")
            
            if not attempt_id:
                return {
                    "success": False,
                    "error": "attempt_id is required"
                }
            
            attempt = await self._get_attempt_by_id(attempt_id)
            
            if attempt:
                return {
                    "success": True,
                    "attempt": attempt.__dict__
                }
            else:
                return {
                    "success": False,
                    "error": f"Attempt {attempt_id} not found"
                }
                
        except DatabaseError as e:
            return self.handle_error(e, "get_attempt")
    
    async def list_attempts(self, request_data: ListAttemptsResult) -> ListAttemptsResult:
        """List reproducibility attempts with filtering"""
        try:
            filters = request_data.get("filters", {})
            limit = request_data.get("limit", 100)
            offset = request_data.get("offset", 0)
            
            attempts = await self._list_attempts_with_filters(filters, limit, offset)
            
            return {
                "success": True,
                "attempts": [attempt.__dict__ for attempt in attempts],
                "count": len(attempts),
                "limit": limit,
                "offset": offset
            }
            
        except DatabaseError as e:
            return self.handle_error(e, "list_attempts")
    
    async def analyze_failure_patterns(self, request_data: AnalyzeFailurePatternsResult) -> AnalyzeFailurePatternsResult:
        """Analyze patterns in reproducibility failures"""
        try:
            experiment_type = request_data.get("experiment_type")
            min_frequency = request_data.get("min_frequency", 2)
            
            # Get failed attempts
            failed_attempts = await self._get_failed_attempts(experiment_type)
            
            if not failed_attempts:
                return {
                    "success": True,
                    "patterns": [],
                    "message": "No failed attempts found for analysis"
                }
            
            # Analyze patterns
            patterns = await self._analyze_patterns(failed_attempts, min_frequency)
            
            # Store patterns in database
            for pattern in patterns:
                await self._insert_failure_pattern(pattern)
            
            logger.info(f"✅ Analyzed failure patterns: {len(patterns)} patterns identified")
            
            return {
                "success": True,
                "patterns": [pattern.__dict__ for pattern in patterns],
                "total_patterns": len(patterns),
                "analyzed_attempts": len(failed_attempts)
            }
            
        except DatabaseError as e:
            return self.handle_error(e, "analyze_failure_patterns")
    
    async def generate_recommendations(self, request_data: GenerateRecommendationsResult) -> GenerateRecommendationsResult:
        """Generate recommendations for improving reproducibility"""
        try:
            experiment_type = request_data.get("experiment_type")
            priority_threshold = request_data.get("priority_threshold", "medium")
            
            # Get failure patterns
            patterns = await self._get_failure_patterns(experiment_type)
            
            # Generate recommendations based on patterns
            recommendations = await self._generate_recommendations_from_patterns(patterns, priority_threshold)
            
            # Store recommendations in database
            for recommendation in recommendations:
                await self._insert_recommendation(recommendation)
            
            logger.info(f"✅ Generated recommendations: {len(recommendations)} recommendations")
            
            return {
                "success": True,
                "recommendations": [rec.__dict__ for rec in recommendations],
                "total_recommendations": len(recommendations),
                "high_priority_count": len([r for r in recommendations if r.priority == "high"])
            }
            
        except DatabaseError as e:
            return self.handle_error(e, "generate_recommendations")
    
    async def get_statistics(self, request_data: GetStatisticsResult) -> GetStatisticsResult:
        """Get reproducibility statistics"""
        try:
            experiment_type = request_data.get("experiment_type")
            time_range = request_data.get("time_range", 30)  # days
            
            stats = await self._calculate_statistics(experiment_type, time_range)
            
            return {
                "success": True,
                "statistics": stats,
                "time_range_days": time_range
            }
            
        except DatabaseError as e:
            return self.handle_error(e, "get_statistics")
    
    async def search_similar_experiments(self, request_data: SearchSimilarExperimentsResult) -> SearchSimilarExperimentsResult:
        """Search for similar experiments based on parameters"""
        try:
            parameters = request_data.get("parameters", {})
            similarity_threshold = request_data.get("similarity_threshold", 0.7)
            limit = request_data.get("limit", 10)
            
            similar_experiments = await self._find_similar_experiments(parameters, similarity_threshold, limit)
            
            return {
                "success": True,
                "similar_experiments": [exp.__dict__ for exp in similar_experiments],
                "count": len(similar_experiments),
                "similarity_threshold": similarity_threshold
            }
            
        except DatabaseError as e:
            return self.handle_error(e, "search_similar_experiments")
    
    async def _insert_attempt(self, attempt: ReproducibilityAttempt):
        """Insert attempt into database"""
        def _insert():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO reproducibility_attempts 
                    (attempt_id, paper_id, paper_title, experiment_type, parameters, 
                     success, reproducibility_score, execution_time, error_message, 
                     variations_count, confidence_level, created_at, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    attempt.attempt_id,
                    attempt.paper_id,
                    attempt.paper_title,
                    attempt.experiment_type,
                    json.dumps(attempt.parameters),
                    attempt.success,
                    attempt.reproducibility_score,
                    attempt.execution_time,
                    attempt.error_message,
                    attempt.variations_count,
                    attempt.confidence_level,
                    attempt.created_at.isoformat(),
                    attempt.completed_at.isoformat() if attempt.completed_at else None
                ))
                conn.commit()
        
        await asyncio.get_event_loop().run_in_executor(self.executor, _insert)
    
    async def _get_attempt_by_id(self, attempt_id: str) -> Optional[ReproducibilityAttempt]:
        """Get attempt by ID"""
        def _get():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM reproducibility_attempts WHERE attempt_id = ?", (attempt_id,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_attempt(row)
                return None
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, _get)
    
    async def _list_attempts_with_filters(self, filters: Dict[str, Any], limit: int, offset: int) -> List[ReproducibilityAttempt]:
        """List attempts with filters"""
        def _list():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query with filters
                query = "SELECT * FROM reproducibility_attempts WHERE 1=1"
                params = []
                
                if filters.get("experiment_type"):
                    query += " AND experiment_type = ?"
                    params.append(filters["experiment_type"])
                
                if filters.get("success") is not None:
                    query += " AND success = ?"
                    params.append(filters["success"])
                
                if filters.get("paper_id"):
                    query += " AND paper_id = ?"
                    params.append(filters["paper_id"])
                
                query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [self._row_to_attempt(row) for row in rows]
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, _list)
    
    async def _get_failed_attempts(self, experiment_type: Optional[str] = None) -> List[ReproducibilityAttempt]:
        """Get failed attempts for analysis"""
        filters = {"success": False}
        if experiment_type:
            filters["experiment_type"] = experiment_type
        
        return await self._list_attempts_with_filters(filters, 1000, 0)
    
    async def _analyze_patterns(self, failed_attempts: List[ReproducibilityAttempt], min_frequency: int) -> List[FailurePattern]:
        """Analyze patterns in failed attempts"""
        patterns = []
        
        # Group by experiment type
        by_type = {}
        for attempt in failed_attempts:
            if attempt.experiment_type not in by_type:
                by_type[attempt.experiment_type] = []
            by_type[attempt.experiment_type].append(attempt)
        
        # Analyze each type
        for exp_type, attempts in by_type.items():
            if len(attempts) >= min_frequency:
                # Analyze parameter patterns
                param_patterns = self._analyze_parameter_patterns(attempts)
                patterns.extend(param_patterns)
                
                # Analyze error patterns
                error_patterns = self._analyze_error_patterns(attempts)
                patterns.extend(error_patterns)
        
        return patterns
    
    def _analyze_parameter_patterns(self, attempts: List[ReproducibilityAttempt]) -> List[FailurePattern]:
        """Analyze parameter-related failure patterns"""
        patterns = []
        
        # Analyze common parameter values in failures
        param_frequencies = {}
        for attempt in attempts:
            for param_name, param_value in attempt.parameters.items():
                key = f"{param_name}:{param_value}"
                param_frequencies[key] = param_frequencies.get(key, 0) + 1
        
        # Find frequent parameter combinations
        for param_key, frequency in param_frequencies.items():
            if frequency >= 2:  # At least 2 occurrences
                param_name, param_value = param_key.split(":", 1)
                
                pattern = FailurePattern(
                    pattern_id=f"param_pattern_{len(patterns)}",
                    pattern_type="parameter",
                    description=f"Parameter '{param_name}' with value '{param_value}' frequently associated with failures",
                    frequency=frequency,
                    affected_experiments=[attempt.attempt_id for attempt in attempts if attempt.parameters.get(param_name) == param_value],
                    common_factors={"parameter": param_name, "value": param_value},
                    recommendations=[
                        f"Review parameter '{param_name}' settings",
                        f"Consider alternative values for '{param_name}'",
                        "Implement parameter validation"
                    ],
                    confidence=min(frequency / len(attempts), 1.0)
                )
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_error_patterns(self, attempts: List[ReproducibilityAttempt]) -> List[FailurePattern]:
        """Analyze error-related failure patterns"""
        patterns = []
        
        # Analyze error messages
        error_frequencies = {}
        for attempt in attempts:
            if attempt.error_message:
                error_frequencies[attempt.error_message] = error_frequencies.get(attempt.error_message, 0) + 1
        
        # Find frequent error patterns
        for error_msg, frequency in error_frequencies.items():
            if frequency >= 2:  # At least 2 occurrences
                pattern = FailurePattern(
                    pattern_id=f"error_pattern_{len(patterns)}",
                    pattern_type="method",
                    description=f"Common error: {error_msg}",
                    frequency=frequency,
                    affected_experiments=[attempt.attempt_id for attempt in attempts if attempt.error_message == error_msg],
                    common_factors={"error_message": error_msg},
                    recommendations=[
                        "Review experimental protocol",
                        "Check equipment calibration",
                        "Verify parameter ranges"
                    ],
                    confidence=min(frequency / len(attempts), 1.0)
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _insert_failure_pattern(self, pattern: FailurePattern):
        """Insert failure pattern into database"""
        def _insert():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO failure_patterns 
                    (pattern_id, pattern_type, description, frequency, affected_experiments, 
                     common_factors, recommendations, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern.pattern_id,
                    pattern.pattern_type,
                    pattern.description,
                    pattern.frequency,
                    json.dumps(pattern.affected_experiments),
                    json.dumps(pattern.common_factors),
                    json.dumps(pattern.recommendations),
                    pattern.confidence,
                    pattern.created_at.isoformat()
                ))
                conn.commit()
        
        await asyncio.get_event_loop().run_in_executor(self.executor, _insert)
    
    async def _get_failure_patterns(self, experiment_type: Optional[str] = None) -> List[FailurePattern]:
        """Get failure patterns from database"""
        def _get():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if experiment_type:
                    cursor.execute("SELECT * FROM failure_patterns WHERE pattern_type = ?", (experiment_type,))
                else:
                    cursor.execute("SELECT * FROM failure_patterns")
                
                rows = cursor.fetchall()
                return [self._row_to_pattern(row) for row in rows]
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, _get)
    
    async def _generate_recommendations_from_patterns(self, patterns: List[FailurePattern], priority_threshold: str) -> List[ReproducibilityRecommendation]:
        """Generate recommendations from failure patterns"""
        recommendations = []
        
        for pattern in patterns:
            # Determine priority based on frequency and confidence
            if pattern.frequency >= 5 and pattern.confidence >= 0.8:
                priority = "high"
            elif pattern.frequency >= 3 and pattern.confidence >= 0.6:
                priority = "medium"
            else:
                priority = "low"
            
            if priority_threshold == "high" and priority != "high":
                continue
            elif priority_threshold == "medium" and priority == "low":
                continue
            
            recommendation = ReproducibilityRecommendation(
                recommendation_id=f"rec_{len(recommendations)}",
                experiment_type=pattern.pattern_type,
                recommendation_type=self._get_recommendation_type(pattern),
                title=f"Improve {pattern.pattern_type} for {pattern.description}",
                description=f"Based on {pattern.frequency} failed attempts: {pattern.description}",
                priority=priority,
                expected_improvement=min(pattern.confidence * 0.3, 0.5),
                implementation_effort=self._assess_implementation_effort(pattern),
                evidence_count=pattern.frequency
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _get_recommendation_type(self, pattern: FailurePattern) -> str:
        """Get recommendation type based on pattern"""
        if pattern.pattern_type == "parameter":
            return "parameter_control"
        elif pattern.pattern_type == "method":
            return "method_improvement"
        elif pattern.pattern_type == "equipment":
            return "equipment_upgrade"
        else:
            return "protocol_change"
    
    def _assess_implementation_effort(self, pattern: FailurePattern) -> str:
        """Assess implementation effort for recommendation"""
        if pattern.pattern_type == "parameter":
            return "low"
        elif pattern.pattern_type == "method":
            return "medium"
        else:
            return "high"
    
    async def _insert_recommendation(self, recommendation: ReproducibilityRecommendation):
        """Insert recommendation into database"""
        def _insert():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO reproducibility_recommendations 
                    (recommendation_id, experiment_type, recommendation_type, title, description, 
                     priority, expected_improvement, implementation_effort, evidence_count, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    recommendation.recommendation_id,
                    recommendation.experiment_type,
                    recommendation.recommendation_type,
                    recommendation.title,
                    recommendation.description,
                    recommendation.priority,
                    recommendation.expected_improvement,
                    recommendation.implementation_effort,
                    recommendation.evidence_count,
                    recommendation.created_at.isoformat()
                ))
                conn.commit()
        
        await asyncio.get_event_loop().run_in_executor(self.executor, _insert)
    
    async def _calculate_statistics(self, experiment_type: Optional[str], time_range: int) -> CalculateStatisticsResult:
        """Calculate reproducibility statistics"""
        def _calculate():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Base query
                base_query = "SELECT * FROM reproducibility_attempts"
                params = []
                
                if experiment_type:
                    base_query += " WHERE experiment_type = ?"
                    params.append(experiment_type)
                
                # Get all attempts
                cursor.execute(base_query, params)
                all_attempts = cursor.fetchall()
                
                if not all_attempts:
                    return {
                        "total_attempts": 0,
                        "success_rate": 0,
                        "average_reproducibility_score": 0,
                        "average_execution_time": 0,
                        "failure_rate": 0
                    }
                
                # Calculate statistics
                total_attempts = len(all_attempts)
                successful_attempts = sum(1 for row in all_attempts if row[5])  # success column
                success_rate = successful_attempts / total_attempts
                
                reproducibility_scores = [row[6] for row in all_attempts if row[5]]  # reproducibility_score column
                avg_reproducibility = sum(reproducibility_scores) / len(reproducibility_scores) if reproducibility_scores else 0
                
                execution_times = [row[7] for row in all_attempts]  # execution_time column
                avg_execution_time = sum(execution_times) / len(execution_times)
                
                return {
                    "total_attempts": total_attempts,
                    "successful_attempts": successful_attempts,
                    "failed_attempts": total_attempts - successful_attempts,
                    "success_rate": success_rate,
                    "failure_rate": 1 - success_rate,
                    "average_reproducibility_score": avg_reproducibility,
                    "average_execution_time": avg_execution_time,
                    "experiment_types": list(set(row[3] for row in all_attempts))  # experiment_type column
                }
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, _calculate)
    
    async def _find_similar_experiments(self, parameters: Dict[str, Any], similarity_threshold: float, limit: int) -> List[ReproducibilityAttempt]:
        """Find similar experiments based on parameters"""
        def _find():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM reproducibility_attempts")
                all_attempts = cursor.fetchall()
                
                similar_attempts = []
                for row in all_attempts:
                    attempt = self._row_to_attempt(row)
                    similarity = self._calculate_parameter_similarity(parameters, attempt.parameters)
                    
                    if similarity >= similarity_threshold:
                        similar_attempts.append((attempt, similarity))
                
                # Sort by similarity and return top results
                similar_attempts.sort(key=lambda x: x[1], reverse=True)
                return [attempt for attempt, _ in similar_attempts[:limit]]
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, _find)
    
    def _calculate_parameter_similarity(self, params1: Dict[str, Any], params2: Dict[str, Any]) -> float:
        """Calculate similarity between parameter sets"""
        if not params1 or not params2:
            return 0.0
        
        # Find common parameters
        common_params = set(params1.keys()) & set(params2.keys())
        if not common_params:
            return 0.0
        
        # Calculate similarity for common parameters
        similarities = []
        for param in common_params:
            val1 = params1[param]
            val2 = params2[param]
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numerical similarity
                if val1 == 0 and val2 == 0:
                    similarity = 1.0
                else:
                    similarity = 1 - abs(val1 - val2) / max(abs(val1), abs(val2), 1)
            else:
                # String similarity
                similarity = 1.0 if str(val1) == str(val2) else 0.0
            
            similarities.append(similarity)
        
        return sum(similarities) / len(similarities)
    
    def _row_to_attempt(self, row) -> ReproducibilityAttempt:
        """Convert database row to ReproducibilityAttempt object"""
        return ReproducibilityAttempt(
            attempt_id=row[0],
            paper_id=row[1],
            paper_title=row[2],
            experiment_type=row[3],
            parameters=json.loads(row[4]),
            success=bool(row[5]),
            reproducibility_score=row[6],
            execution_time=row[7],
            error_message=row[8],
            variations_count=row[9],
            confidence_level=row[10],
            created_at=datetime.fromisoformat(row[11]),
            completed_at=datetime.fromisoformat(row[12]) if row[12] else None
        )
    
    def _row_to_pattern(self, row) -> FailurePattern:
        """Convert database row to FailurePattern object"""
        return FailurePattern(
            pattern_id=row[0],
            pattern_type=row[1],
            description=row[2],
            frequency=row[3],
            affected_experiments=json.loads(row[4]),
            common_factors=json.loads(row[5]),
            recommendations=json.loads(row[6]),
            confidence=row[7],
            created_at=datetime.fromisoformat(row[8])
        )
