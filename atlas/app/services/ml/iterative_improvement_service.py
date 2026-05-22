"""
Iterative Improvement Pipeline Service for ATLAS

This service implements a continuous learning system that improves the quality
of scientific analysis through feedback loops, performance metrics, and adaptive
optimization strategies.

Key Features:
- Feedback collection from analysis results
- Performance tracking and metrics calculation
- Adaptive parameter optimization
- Model performance evaluation
- Automated quality improvement recommendations
- Learning from historical data
"""

import logging
import asyncio
import json
import numpy as np
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import statistics
import aiofiles
from app.exceptions.domain.biology import BiologyError
from app.types.iterative_improvement_service_types import (
    GetLearningInsightsResult,
    GetServiceHealthResult,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of feedback for the improvement pipeline"""
    USER_RATING = "user_rating"
    ACCURACY_SCORE = "accuracy_score"
    COMPLETION_TIME = "completion_time"
    ERROR_RATE = "error_rate"
    COHERENCE_SCORE = "coherence_score"
    RELEVANCE_SCORE = "relevance_score"
    SCIENTIFIC_VALIDITY = "scientific_validity"


class AnalysisType(Enum):
    """Types of analysis that can be improved"""
    LITERATURE_SEARCH = "literature_search"
    EVIDENCE_SYNTHESIS = "evidence_synthesis"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    MODEL_PREDICTION = "model_prediction"
    EXPERIMENTAL_DESIGN = "experimental_design"
    PEER_REVIEW = "peer_review"
    TOOL_ORCHESTRATION = "tool_orchestration"


@dataclass
class FeedbackEntry:
    """Individual feedback entry"""
    id: str
    analysis_type: AnalysisType
    feedback_type: FeedbackType
    value: float
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    timestamp: datetime
    source: str
    

@dataclass
class PerformanceMetrics:
    """Performance metrics for analysis"""
    accuracy_mean: float
    accuracy_std: float
    completion_time_mean: float
    completion_time_std: float
    error_rate: float
    coherence_mean: float
    relevance_mean: float
    scientific_validity_mean: float
    total_analyses: int
    improvement_trend: float  # Positive = improving


@dataclass
class OptimizationRecommendation:
    """Recommendation for improving analysis"""
    parameter: str
    current_value: Any
    recommended_value: Any
    expected_improvement: float
    confidence: float
    rationale: str


class IterativeImprovementPipeline:
    """
    Main service for continuous improvement of scientific analysis
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the improvement pipeline"""
        
        self.data_dir = data_dir or Path("data/improvement_pipeline")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Storage files
        self.feedback_file = self.data_dir / "feedback_history.jsonl"
        self.metrics_file = self.data_dir / "performance_metrics.json"
        self.recommendations_file = self.data_dir / "optimization_recommendations.json"
        
        # In-memory storage
        self.feedback_history: List[FeedbackEntry] = []
        self.current_metrics: Dict[AnalysisType, PerformanceMetrics] = {}
        self.optimization_recommendations: Dict[AnalysisType, List[OptimizationRecommendation]] = {}
        
        # Configuration
        self.feedback_window_days = 30  # Consider feedback from last 30 days
        self.min_samples_for_optimization = 10  # Minimum samples before optimization
        self.improvement_threshold = 0.05  # 5% improvement threshold
        
        # Load existing data
        self._load_historical_data()
        
        logger.info("✅ IterativeImprovementPipeline initialized")
    
    def _load_historical_data(self):
        """Load historical feedback and metrics"""
        try:
            # Load feedback history
            if self.feedback_file.exists():
                with open(self.feedback_file, 'r') as f:
                    for line in f:
                        data = json.loads(line)
                        feedback = FeedbackEntry(
                            id=data['id'],
                            analysis_type=AnalysisType(data['analysis_type']),
                            feedback_type=FeedbackType(data['feedback_type']),
                            value=data['value'],
                            parameters=data['parameters'],
                            context=data['context'],
                            timestamp=datetime.fromisoformat(data['timestamp']),
                            source=data['source']
                        )
                        self.feedback_history.append(feedback)
            
            # Load current metrics
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    metrics_data = json.load(f)
                    for analysis_type, metrics in metrics_data.items():
                        self.current_metrics[AnalysisType(analysis_type)] = PerformanceMetrics(**metrics)
            
            # Load recommendations
            if self.recommendations_file.exists():
                with open(self.recommendations_file, 'r') as f:
                    rec_data = json.load(f)
                    for analysis_type, recommendations in rec_data.items():
                        self.optimization_recommendations[AnalysisType(analysis_type)] = [
                            OptimizationRecommendation(**rec) for rec in recommendations
                        ]
            
            logger.info(f"Loaded {len(self.feedback_history)} feedback entries and metrics for {len(self.current_metrics)} analysis types")
            
        except BiologyError as e:
            logger.error(f"Failed to load historical data: {e}")
    
    def _save_feedback(self, feedback: FeedbackEntry):
        """Save feedback entry to disk"""
        try:
            with open(self.feedback_file, 'a') as f:
                data = asdict(feedback)
                data['analysis_type'] = feedback.analysis_type.value
                data['feedback_type'] = feedback.feedback_type.value
                data['timestamp'] = feedback.timestamp.isoformat()
                f.write(json.dumps(data) + '\n')
        except BiologyError as e:
            logger.error(f"Failed to save feedback: {e}")
    
    def _save_metrics(self):
        """Save current metrics to disk"""
        try:
            metrics_data = {}
            for analysis_type, metrics in self.current_metrics.items():
                metrics_data[analysis_type.value] = asdict(metrics)
            
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
        except BiologyError as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def _save_recommendations(self):
        """Save optimization recommendations to disk"""
        try:
            rec_data = {}
            for analysis_type, recommendations in self.optimization_recommendations.items():
                rec_data[analysis_type.value] = [asdict(rec) for rec in recommendations]
            
            with open(self.recommendations_file, 'w') as f:
                json.dump(rec_data, f, indent=2)
        except BiologyError as e:
            logger.error(f"Failed to save recommendations: {e}")
    
    async def record_feedback(
        self,
        analysis_type: AnalysisType,
        feedback_type: FeedbackType,
        value: float,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        source: str = "system"
    ) -> str:
        """
        Record feedback for a specific analysis
        
        Args:
            analysis_type: Type of analysis being evaluated
            feedback_type: Type of feedback (rating, accuracy, etc.)
            value: Feedback value (normalized 0-1 or actual metric)
            parameters: Parameters used in the analysis
            context: Additional context information
            source: Source of feedback (user, system, etc.)
            
        Returns:
            Feedback ID
        """
        try:
            # Generate feedback ID
            feedback_id = hashlib.sha256(
                f"{analysis_type.value}_{feedback_type.value}_{datetime.now(UTC).isoformat()}_{source}".encode()
            ).hexdigest()[:12]
            
            # Create feedback entry
            feedback = FeedbackEntry(
                id=feedback_id,
                analysis_type=analysis_type,
                feedback_type=feedback_type,
                value=value,
                parameters=parameters,
                context=context or {},
                timestamp=datetime.now(UTC),
                source=source
            )
            
            # Store feedback
            self.feedback_history.append(feedback)
            self._save_feedback(feedback)
            
            # Trigger metrics update
            await self._update_metrics(analysis_type)
            
            logger.info(f"✅ Recorded feedback {feedback_id} for {analysis_type.value}")
            return feedback_id
            
        except BiologyError as e:
            logger.error(f"Failed to record feedback: {e}")
            raise
    
    async def _update_metrics(self, analysis_type: AnalysisType):
        """Update performance metrics for a specific analysis type"""
        try:
            # Get recent feedback for this analysis type
            cutoff_date = datetime.now(UTC) - timedelta(days=self.feedback_window_days)
            recent_feedback = [
                fb for fb in self.feedback_history
                if fb.analysis_type == analysis_type and fb.timestamp >= cutoff_date
            ]
            
            if len(recent_feedback) < 5:  # Not enough data
                return
            
            # Calculate metrics by feedback type
            accuracy_values = [fb.value for fb in recent_feedback if fb.feedback_type == FeedbackType.ACCURACY_SCORE]
            completion_times = [fb.value for fb in recent_feedback if fb.feedback_type == FeedbackType.COMPLETION_TIME]
            error_rates = [fb.value for fb in recent_feedback if fb.feedback_type == FeedbackType.ERROR_RATE]
            coherence_scores = [fb.value for fb in recent_feedback if fb.feedback_type == FeedbackType.COHERENCE_SCORE]
            relevance_scores = [fb.value for fb in recent_feedback if fb.feedback_type == FeedbackType.RELEVANCE_SCORE]
            validity_scores = [fb.value for fb in recent_feedback if fb.feedback_type == FeedbackType.SCIENTIFIC_VALIDITY]
            
            # Calculate improvement trend (compare recent vs older performance)
            older_cutoff = cutoff_date - timedelta(days=self.feedback_window_days)
            older_feedback = [
                fb for fb in self.feedback_history
                if fb.analysis_type == analysis_type 
                and fb.timestamp >= older_cutoff 
                and fb.timestamp < cutoff_date
                and fb.feedback_type == FeedbackType.ACCURACY_SCORE
            ]
            
            improvement_trend = 0.0
            if older_feedback and accuracy_values:
                recent_mean = statistics.mean(accuracy_values)
                older_mean = statistics.mean([fb.value for fb in older_feedback])
                improvement_trend = (recent_mean - older_mean) / older_mean if older_mean > 0 else 0.0
            
            # Create performance metrics
            metrics = PerformanceMetrics(
                accuracy_mean=statistics.mean(accuracy_values) if accuracy_values else 0.0,
                accuracy_std=statistics.stdev(accuracy_values) if len(accuracy_values) > 1 else 0.0,
                completion_time_mean=statistics.mean(completion_times) if completion_times else 0.0,
                completion_time_std=statistics.stdev(completion_times) if len(completion_times) > 1 else 0.0,
                error_rate=statistics.mean(error_rates) if error_rates else 0.0,
                coherence_mean=statistics.mean(coherence_scores) if coherence_scores else 0.0,
                relevance_mean=statistics.mean(relevance_scores) if relevance_scores else 0.0,
                scientific_validity_mean=statistics.mean(validity_scores) if validity_scores else 0.0,
                total_analyses=len(recent_feedback),
                improvement_trend=improvement_trend
            )
            
            self.current_metrics[analysis_type] = metrics
            self._save_metrics()
            
            # Trigger optimization if we have enough data
            if len(recent_feedback) >= self.min_samples_for_optimization:
                await self._generate_optimization_recommendations(analysis_type, recent_feedback)
            
            logger.info(f"✅ Updated metrics for {analysis_type.value}: accuracy={metrics.accuracy_mean:.3f}, trend={improvement_trend:.3f}")
            
        except BiologyError as e:
            logger.error(f"Failed to update metrics for {analysis_type.value}: {e}")
    
    async def _generate_optimization_recommendations(
        self,
        analysis_type: AnalysisType,
        feedback_data: List[FeedbackEntry]
    ):
        """Generate optimization recommendations based on feedback data"""
        try:
            recommendations = []
            
            # Analyze parameter patterns for high-performing analyses
            high_performance = [fb for fb in feedback_data if fb.value >= 0.8]  # Top 20%
            low_performance = [fb for fb in feedback_data if fb.value <= 0.5]   # Bottom 50%
            
            if len(high_performance) < 3 or len(low_performance) < 3:
                return  # Not enough data for meaningful recommendations
            
            # Extract common parameters
            all_params = set()
            for fb in feedback_data:
                all_params.update(fb.parameters.keys())
            
            # Analyze each parameter
            for param in all_params:
                try:
                    # Get parameter values for high/low performance
                    high_values = []
                    low_values = []
                    
                    for fb in high_performance:
                        if param in fb.parameters and fb.parameters[param] is not None:
                            val = fb.parameters[param]
                            if isinstance(val, (int, float)):
                                high_values.append(val)
                    
                    for fb in low_performance:
                        if param in fb.parameters and fb.parameters[param] is not None:
                            val = fb.parameters[param]
                            if isinstance(val, (int, float)):
                                low_values.append(val)
                    
                    if len(high_values) >= 3 and len(low_values) >= 3:
                        high_mean = statistics.mean(high_values)
                        low_mean = statistics.mean(low_values)
                        
                        # Check if there's a significant difference
                        if abs(high_mean - low_mean) / max(abs(high_mean), abs(low_mean), 1e-6) > 0.1:
                            # Calculate confidence based on sample sizes and variance
                            high_std = statistics.stdev(high_values) if len(high_values) > 1 else 0
                            low_std = statistics.stdev(low_values) if len(low_values) > 1 else 0
                            
                            confidence = min(0.95, len(high_values) * len(low_values) / 100)
                            expected_improvement = abs(high_mean - low_mean) / max(abs(low_mean), 1e-6)
                            
                            # Get current typical value
                            all_values = [fb.parameters.get(param) for fb in feedback_data[-10:] 
                                        if param in fb.parameters and isinstance(fb.parameters[param], (int, float))]
                            current_value = statistics.mean(all_values) if all_values else low_mean
                            
                            recommendation = OptimizationRecommendation(
                                parameter=param,
                                current_value=current_value,
                                recommended_value=high_mean,
                                expected_improvement=expected_improvement,
                                confidence=confidence,
                                rationale=f"High-performing analyses use {param}={high_mean:.3f} vs {low_mean:.3f} in low-performing ones"
                            )
                            recommendations.append(recommendation)
                
                except BiologyError as e:
                    logger.warning(f"Failed to analyze parameter {param}: {e}")
            
            # Sort by expected improvement
            recommendations.sort(key=lambda r: r.expected_improvement * r.confidence, reverse=True)
            
            # Keep top 5 recommendations
            self.optimization_recommendations[analysis_type] = recommendations[:5]
            self._save_recommendations()
            
            logger.info(f"✅ Generated {len(recommendations)} optimization recommendations for {analysis_type.value}")
            
        except BiologyError as e:
            logger.error(f"Failed to generate optimization recommendations: {e}")
    
    async def get_performance_metrics(
        self,
        analysis_type: Optional[AnalysisType] = None
    ) -> Dict[str, Any]:
        """
        Get current performance metrics
        
        Args:
            analysis_type: Specific analysis type, or None for all
            
        Returns:
            Dictionary with performance metrics
        """
        try:
            if analysis_type:
                metrics = self.current_metrics.get(analysis_type)
                if metrics:
                    metrics_dict = asdict(metrics)
                    # Ensure improvement_trend is included (alias for trend)
                    metrics_dict['improvement_trend'] = metrics_dict.get('trend', 0.0)
                    
                    return {
                        'success': True,
                        'data': {
                            'analysis_type': analysis_type.value,
                            'metrics': {
                                **metrics_dict,
                                'total_analyses': len([fb for fb in self.feedback_history if fb.analysis_type == analysis_type])
                            },
                            'last_updated': datetime.now(UTC).isoformat(),
                            'data_points': len([fb for fb in self.feedback_history if fb.analysis_type == analysis_type])
                        }
                    }
                else:
                    return {
                        'success': False,
                        'data': {
                            'analysis_type': analysis_type.value, 
                            'metrics': None, 
                            'message': 'No data available'
                        }
                    }
            else:
                all_metrics = {}
                for at, metrics in self.current_metrics.items():
                    metrics_dict = asdict(metrics)
                    # Ensure improvement_trend is included
                    metrics_dict['improvement_trend'] = metrics_dict.get('trend', 0.0)
                    all_metrics[at.value] = metrics_dict
                
                return {
                    'success': True,
                    'all_metrics': all_metrics,
                    'total_feedback_entries': len(self.feedback_history),
                    'analysis_types_tracked': len(all_metrics),
                    'last_updated': datetime.now(UTC).isoformat()
                }
        
        except BiologyError as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {'error': str(e)}
    
    async def get_optimization_recommendations(
        self,
        analysis_type: AnalysisType
    ) -> Dict[str, Any]:
        """
        Get optimization recommendations for specific analysis type
        
        Args:
            analysis_type: Analysis type to get recommendations for
            
        Returns:
            Dictionary with recommendations
        """
        try:
            recommendations = self.optimization_recommendations.get(analysis_type, [])
            
            return {
                'analysis_type': analysis_type.value,
                'recommendations': [asdict(rec) for rec in recommendations],
                'total_recommendations': len(recommendations),
                'last_updated': datetime.now(UTC).isoformat(),
                'based_on_samples': len([fb for fb in self.feedback_history if fb.analysis_type == analysis_type])
            }
        
        except BiologyError as e:
            logger.error(f"Failed to get optimization recommendations: {e}")
            return {'error': str(e)}
    
    async def simulate_improvement_impact(
        self,
        analysis_type: AnalysisType,
        parameter_changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate the potential impact of parameter changes
        
        Args:
            analysis_type: Analysis type to simulate
            parameter_changes: Dictionary of parameter changes to simulate
            
        Returns:
            Simulation results
        """
        try:
            # Get recent feedback for this analysis type
            cutoff_date = datetime.now(UTC) - timedelta(days=self.feedback_window_days)
            recent_feedback = [
                fb for fb in self.feedback_history
                if fb.analysis_type == analysis_type and fb.timestamp >= cutoff_date
            ]
            
            if len(recent_feedback) < 5:
                return {'error': 'Not enough historical data for simulation'}
            
            # Calculate current performance baseline
            current_performance = statistics.mean([
                fb.value for fb in recent_feedback 
                if fb.feedback_type == FeedbackType.ACCURACY_SCORE
            ])
            
            # Find similar parameter configurations in history
            similar_configs = []
            for fb in recent_feedback:
                similarity_score = 0
                total_params = 0
                
                for param, new_value in parameter_changes.items():
                    if param in fb.parameters:
                        old_value = fb.parameters[param]
                        if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
                            # Calculate similarity (inverse of relative difference)
                            diff = abs(new_value - old_value) / max(abs(old_value), 1e-6)
                            similarity_score += max(0, 1 - diff)
                            total_params += 1
                
                if total_params > 0:
                    avg_similarity = similarity_score / total_params
                    if avg_similarity > 0.8:  # 80% similarity threshold
                        similar_configs.append((fb, avg_similarity))
            
            # Estimate performance with similar configurations
            if similar_configs:
                similar_configs.sort(key=lambda x: x[1], reverse=True)
                similar_performance = statistics.mean([
                    fb.value for fb, _ in similar_configs[:5]  # Top 5 most similar
                    if fb.feedback_type == FeedbackType.ACCURACY_SCORE
                ])
                
                estimated_improvement = similar_performance - current_performance
                confidence = min(0.9, len(similar_configs) / 10)
            else:
                # Use recommendations to estimate improvement
                recommendations = self.optimization_recommendations.get(analysis_type, [])
                relevant_recs = [
                    rec for rec in recommendations 
                    if rec.parameter in parameter_changes
                ]
                
                if relevant_recs:
                    estimated_improvement = sum(rec.expected_improvement * rec.confidence for rec in relevant_recs) / len(relevant_recs)
                    confidence = statistics.mean([rec.confidence for rec in relevant_recs])
                else:
                    estimated_improvement = 0.0
                    confidence = 0.0
            
            return {
                'analysis_type': analysis_type.value,
                'parameter_changes': parameter_changes,
                'current_performance': current_performance,
                'estimated_new_performance': current_performance + estimated_improvement,
                'estimated_improvement': estimated_improvement,
                'confidence': confidence,
                'similar_configurations_found': len(similar_configs),
                'simulation_timestamp': datetime.now(UTC).isoformat()
            }
        
        except BiologyError as e:
            logger.error(f"Failed to simulate improvement impact: {e}")
            return {'error': str(e)}
    
    async def get_learning_insights(self) -> GetLearningInsightsResult:
        """
        Get insights about what the system has learned
        
        Returns:
            Dictionary with learning insights
        """
        try:
            insights = {
                'total_feedback_entries': len(self.feedback_history),
                'analysis_types_tracked': len(self.current_metrics),
                'learning_period_days': self.feedback_window_days,
                'insights_by_type': {},
                'overall_trends': {},
                'generated_timestamp': datetime.now(UTC).isoformat()
            }
            
            # Analyze each analysis type
            for analysis_type, metrics in self.current_metrics.items():
                type_insights = {
                    'performance_trend': 'improving' if metrics.improvement_trend > 0.05 
                                      else 'declining' if metrics.improvement_trend < -0.05 
                                      else 'stable',
                    'improvement_rate': metrics.improvement_trend,
                    'current_accuracy': metrics.accuracy_mean,
                    'reliability': 1 - metrics.accuracy_std if metrics.accuracy_std < 1 else 0,
                    'total_analyses': metrics.total_analyses,
                    'optimization_recommendations': len(self.optimization_recommendations.get(analysis_type, []))
                }
                insights['insights_by_type'][analysis_type.value] = type_insights
            
            # Overall trends
            if self.current_metrics:
                all_improvements = [m.improvement_trend for m in self.current_metrics.values()]
                all_accuracies = [m.accuracy_mean for m in self.current_metrics.values()]
                
                insights['overall_trends'] = {
                    'average_improvement_trend': statistics.mean(all_improvements),
                    'average_accuracy': statistics.mean(all_accuracies),
                    'most_improved_analysis': max(self.current_metrics.items(), 
                                                key=lambda x: x[1].improvement_trend)[0].value,
                    'most_accurate_analysis': max(self.current_metrics.items(), 
                                                key=lambda x: x[1].accuracy_mean)[0].value,
                    'total_recommendations_generated': sum(len(recs) for recs in self.optimization_recommendations.values())
                }
            
            return insights
        
        except BiologyError as e:
            logger.error(f"Failed to get learning insights: {e}")
            return {'error': str(e)}
    
    async def get_service_health(self) -> GetServiceHealthResult:
        """Get service health status"""
        return {
            'service': 'IterativeImprovementPipeline',
            'status': 'healthy',
            'feedback_entries': len(self.feedback_history),
            'analysis_types_tracked': len(self.current_metrics),
            'data_directory': str(self.data_dir),
            'feedback_window_days': self.feedback_window_days,
            'min_samples_for_optimization': self.min_samples_for_optimization
        }


# Global service instance
_improvement_pipeline = None

def get_improvement_pipeline() -> IterativeImprovementPipeline:
    """Get singleton improvement pipeline instance"""
    global _improvement_pipeline
    if _improvement_pipeline is None:
        _improvement_pipeline = IterativeImprovementPipeline()
    return _improvement_pipeline
