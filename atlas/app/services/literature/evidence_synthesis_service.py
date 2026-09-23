"""
Advanced Evidence Synthesis Service for ATLAS Autonomous Laboratory

This service combines multiple sources of scientific evidence to create
coherent summaries and insights, resolving conflicts and identifying
cross-domain connections.

Author: ATLAS Autonomous Laboratory System
Date: September 11, 2025
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timezone as tz
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Set, Tuple
from enum import Enum
import numpy as np
from collections import defaultdict, Counter
import re
from app.exceptions.domain.biology import BiologyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UTC = tz.utc

class EvidenceType(Enum):
    """Types of scientific evidence"""
    EXPERIMENTAL = "experimental"
    THEORETICAL = "theoretical"  
    OBSERVATIONAL = "observational"
    COMPUTATIONAL = "computational"
    LITERATURE_REVIEW = "literature_review"
    META_ANALYSIS = "meta_analysis"
    CASE_STUDY = "case_study"
    CLINICAL_TRIAL = "clinical_trial"

class ConfidenceLevel(Enum):
    """Confidence levels for evidence"""
    VERY_HIGH = "very_high"    # >0.90
    HIGH = "high"              # 0.75-0.90
    MEDIUM = "medium"          # 0.50-0.75
    LOW = "low"                # 0.25-0.50
    VERY_LOW = "very_low"      # <0.25

class ConflictResolution(Enum):
    """Methods for resolving evidence conflicts"""
    WEIGHTED_AVERAGE = "weighted_average"
    HIGHEST_CONFIDENCE = "highest_confidence"
    MOST_RECENT = "most_recent"
    EXPERT_CONSENSUS = "expert_consensus"
    META_ANALYSIS = "meta_analysis"

@dataclass
class EvidenceSource:
    """Individual piece of scientific evidence"""
    id: str
    title: str
    content: str
    evidence_type: EvidenceType
    confidence_score: float
    reliability_score: float
    publication_date: datetime
    domain: str
    authors: List[str]
    doi: Optional[str] = None
    citations: int = 0
    peer_reviewed: bool = True
    methodology_score: float = 0.0
    sample_size: Optional[int] = None
    statistical_power: Optional[float] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass  
class EvidenceCluster:
    """Group of related evidence sources"""
    id: str
    topic: str
    evidence_sources: List[EvidenceSource]
    consensus_level: float
    conflict_level: float
    main_findings: List[str]
    conflicting_points: List[str]
    confidence_distribution: Dict[str, float]
    
@dataclass
class SynthesisResult:
    """Result of evidence synthesis"""
    id: str
    query: str
    timestamp: datetime
    evidence_clusters: List[EvidenceCluster]
    overall_confidence: float
    main_conclusions: List[str]
    limitations: List[str]
    future_research_directions: List[str]
    cross_domain_connections: List[Dict[str, Any]]
    conflict_resolutions: List[Dict[str, Any]]
    evidence_gaps: List[str]
    methodology_assessment: Dict[str, float]

class AdvancedEvidenceSynthesisService:
    """
    Advanced service for synthesizing scientific evidence from multiple sources
    """
    
    def __init__(self, cache_size: int = 1000):
        """Initialize the evidence synthesis service"""
        self.cache_size = cache_size
        self.synthesis_cache: Dict[str, SynthesisResult] = {}
        self.domain_expertise = self._initialize_domain_expertise()
        self.conflict_resolution_strategies = self._initialize_conflict_strategies()
        logger.info("✅ AdvancedEvidenceSynthesisService initialized")
    
    def _initialize_domain_expertise(self) -> Dict[str, Dict[str, float]]:
        """Initialize domain-specific expertise weights"""
        return {
            "medicine": {
                "clinical_trial": 0.95,
                "meta_analysis": 0.90,
                "observational": 0.75,
                "case_study": 0.60,
                "theoretical": 0.50
            },
            "physics": {
                "experimental": 0.90,
                "theoretical": 0.85,
                "computational": 0.80,
                "observational": 0.75,
                "literature_review": 0.60
            },
            "biology": {
                "experimental": 0.90,
                "observational": 0.80,
                "meta_analysis": 0.85,
                "computational": 0.75,
                "literature_review": 0.65
            },
            "chemistry": {
                "experimental": 0.95,
                "computational": 0.80,
                "theoretical": 0.75,
                "literature_review": 0.60,
                "case_study": 0.50
            },
            "materials_science": {
                "experimental": 0.90,
                "computational": 0.85,
                "theoretical": 0.75,
                "observational": 0.70,
                "literature_review": 0.60
            },
            "neuroscience": {
                "experimental": 0.85,
                "observational": 0.80,
                "clinical_trial": 0.90,
                "computational": 0.75,
                "case_study": 0.65
            }
        }
    
    def _initialize_conflict_strategies(self) -> Dict[ConflictResolution, callable]:
        """Initialize conflict resolution strategies"""
        return {
            ConflictResolution.WEIGHTED_AVERAGE: self._weighted_average_resolution,
            ConflictResolution.HIGHEST_CONFIDENCE: self._highest_confidence_resolution,
            ConflictResolution.MOST_RECENT: self._most_recent_resolution,
            ConflictResolution.EXPERT_CONSENSUS: self._expert_consensus_resolution,
            ConflictResolution.META_ANALYSIS: self._meta_analysis_resolution
        }
    
    async def synthesize_evidence(
        self,
        evidence_sources: List[EvidenceSource],
        query: str,
        synthesis_parameters: Optional[Dict[str, Any]] = None
    ) -> SynthesisResult:
        """
        Main method to synthesize multiple evidence sources
        
        Args:
            evidence_sources: List of evidence to synthesize
            query: Research question or topic
            synthesis_parameters: Optional parameters for synthesis
            
        Returns:
            SynthesisResult with comprehensive analysis
        """
        try:
            # Generate synthesis ID
            synthesis_id = hashlib.sha256(
                f"{query}_{len(evidence_sources)}_{datetime.now(UTC).isoformat()}".encode()
            ).hexdigest()[:12]
            
            # Check cache
            cache_key = f"{query}_{len(evidence_sources)}"
            if cache_key in self.synthesis_cache:
                logger.info(f"✅ Retrieved synthesis from cache: {synthesis_id}")
                return self.synthesis_cache[cache_key]
            
            # Initialize synthesis parameters
            params = synthesis_parameters or {}
            min_confidence = params.get('min_confidence', 0.3)
            cluster_threshold = params.get('cluster_threshold', 0.7)
            max_clusters = params.get('max_clusters', 10)
            
            # Filter evidence by minimum confidence
            filtered_evidence = [
                ev for ev in evidence_sources 
                if ev.confidence_score >= min_confidence
            ]
            
            logger.info(f"🔍 Synthesizing {len(filtered_evidence)} evidence sources (filtered from {len(evidence_sources)})")
            
            # Step 1: Cluster related evidence
            evidence_clusters = await self._cluster_evidence(
                filtered_evidence, 
                cluster_threshold, 
                max_clusters
            )
            
            # Step 2: Analyze each cluster
            analyzed_clusters = []
            for cluster in evidence_clusters:
                analyzed_cluster = await self._analyze_evidence_cluster(cluster)
                analyzed_clusters.append(analyzed_cluster)
            
            # Step 3: Generate cross-domain connections
            cross_domain_connections = await self._identify_cross_domain_connections(
                analyzed_clusters
            )
            
            # Step 4: Resolve conflicts
            conflict_resolutions = await self._resolve_evidence_conflicts(
                analyzed_clusters
            )
            
            # Step 5: Generate main conclusions
            main_conclusions = await self._generate_main_conclusions(
                analyzed_clusters, 
                cross_domain_connections
            )
            
            # Step 6: Identify limitations and gaps
            limitations = await self._identify_limitations(analyzed_clusters)
            evidence_gaps = await self._identify_evidence_gaps(query, analyzed_clusters)
            
            # Step 7: Suggest future research directions
            future_research = await self._suggest_future_research(
                analyzed_clusters, 
                evidence_gaps
            )
            
            # Step 8: Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(analyzed_clusters)
            
            # Step 9: Assess methodology quality
            methodology_assessment = self._assess_methodology_quality(filtered_evidence)
            
            # Create synthesis result
            result = SynthesisResult(
                id=synthesis_id,
                query=query,
                timestamp=datetime.now(UTC),
                evidence_clusters=analyzed_clusters,
                overall_confidence=overall_confidence,
                main_conclusions=main_conclusions,
                limitations=limitations,
                future_research_directions=future_research,
                cross_domain_connections=cross_domain_connections,
                conflict_resolutions=conflict_resolutions,
                evidence_gaps=evidence_gaps,
                methodology_assessment=methodology_assessment
            )
            
            # Cache result
            if len(self.synthesis_cache) >= self.cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self.synthesis_cache))
                del self.synthesis_cache[oldest_key]
            
            self.synthesis_cache[cache_key] = result
            
            logger.info(f"✅ Evidence synthesis completed: {synthesis_id}")
            return result
            
        except BiologyError as e:
            logger.error(f"Failed to synthesize evidence: {e}")
            raise
    
    async def _cluster_evidence(
        self, 
        evidence_sources: List[EvidenceSource],
        threshold: float = 0.7,
        max_clusters: int = 10
    ) -> List[EvidenceCluster]:
        """Cluster related evidence sources using semantic similarity"""
        
        if not evidence_sources:
            return []
        
        # For now, use simple keyword-based clustering
        # In production, this would use advanced NLP models
        clusters = []
        unclustered = evidence_sources.copy()
        
        cluster_id = 0
        while unclustered and len(clusters) < max_clusters:
            # Take first evidence as cluster seed
            seed = unclustered[0]
            cluster_evidence = [seed]
            unclustered.remove(seed)
            
            # Find similar evidence
            to_remove = []
            for evidence in unclustered:
                similarity = self._calculate_semantic_similarity(seed, evidence)
                if similarity >= threshold:
                    cluster_evidence.append(evidence)
                    to_remove.append(evidence)
            
            # Remove clustered evidence
            for evidence in to_remove:
                unclustered.remove(evidence)
            
            # Create cluster
            cluster = EvidenceCluster(
                id=f"cluster_{cluster_id}",
                topic=self._extract_cluster_topic(cluster_evidence),
                evidence_sources=cluster_evidence,
                consensus_level=0.0,  # Will be calculated in analysis
                conflict_level=0.0,   # Will be calculated in analysis
                main_findings=[],     # Will be filled in analysis
                conflicting_points=[], # Will be filled in analysis
                confidence_distribution={}  # Will be calculated in analysis
            )
            
            clusters.append(cluster)
            cluster_id += 1
        
        # Add remaining evidence as individual clusters
        for evidence in unclustered:
            if len(clusters) >= max_clusters:
                break
            
            cluster = EvidenceCluster(
                id=f"cluster_{cluster_id}",
                topic=evidence.title[:50] + "...",
                evidence_sources=[evidence],
                consensus_level=1.0,
                conflict_level=0.0,
                main_findings=[evidence.content[:200] + "..."],
                conflicting_points=[],
                confidence_distribution={
                    self._get_confidence_level(evidence.confidence_score).value: 1.0
                }
            )
            
            clusters.append(cluster)
            cluster_id += 1
        
        logger.info(f"✅ Created {len(clusters)} evidence clusters")
        return clusters
    
    def _calculate_semantic_similarity(
        self, 
        evidence1: EvidenceSource, 
        evidence2: EvidenceSource
    ) -> float:
        """Calculate semantic similarity between two evidence sources"""
        
        # Simple keyword-based similarity (would use embeddings in production)
        text1 = (evidence1.title + " " + evidence1.content).lower()
        text2 = (evidence2.title + " " + evidence2.content).lower()
        
        # Extract keywords
        words1 = set(re.findall(r'\b\w+\b', text1))
        words2 = set(re.findall(r'\b\w+\b', text2))
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0.0
        
        jaccard_sim = intersection / union
        
        # Boost similarity for same domain
        domain_bonus = 0.2 if evidence1.domain == evidence2.domain else 0.0
        
        # Boost similarity for same evidence type
        type_bonus = 0.1 if evidence1.evidence_type == evidence2.evidence_type else 0.0
        
        return min(1.0, jaccard_sim + domain_bonus + type_bonus)
    
    def _extract_cluster_topic(self, evidence_sources: List[EvidenceSource]) -> str:
        """Extract main topic from a cluster of evidence"""
        
        # Extract all words from titles and content
        all_text = " ".join([
            ev.title + " " + ev.content for ev in evidence_sources
        ]).lower()
        
        # Find most common meaningful words
        words = re.findall(r'\b\w{4,}\b', all_text)  # Words with 4+ chars
        
        # Filter common words
        stop_words = {
            'that', 'this', 'with', 'from', 'they', 'were', 'been', 'have',
            'their', 'said', 'each', 'which', 'them', 'than', 'more', 'very',
            'what', 'know', 'just', 'first', 'time', 'over', 'think', 'also',
            'back', 'after', 'use', 'two', 'how', 'our', 'work', 'life',
            'only', 'new', 'years', 'way', 'well', 'before', 'here', 'all'
        }
        
        filtered_words = [w for w in words if w not in stop_words]
        
        if not filtered_words:
            return f"Evidence cluster ({len(evidence_sources)} sources)"
        
        # Get most common words
        word_counts = Counter(filtered_words)
        top_words = word_counts.most_common(3)
        
        topic = " ".join([word for word, _ in top_words])
        return topic.title()
    
    async def _analyze_evidence_cluster(self, cluster: EvidenceCluster) -> EvidenceCluster:
        """Analyze a cluster of evidence to extract insights and conflicts"""
        
        evidence_list = cluster.evidence_sources
        
        # Calculate consensus level
        confidence_scores = [ev.confidence_score for ev in evidence_list]
        consensus_level = np.std(confidence_scores) / (np.mean(confidence_scores) + 0.001)
        consensus_level = max(0.0, 1.0 - consensus_level)  # Convert to consensus (higher = more consensus)
        
        # Calculate conflict level
        conflict_level = 1.0 - consensus_level
        
        # Extract main findings
        main_findings = []
        for evidence in evidence_list[:3]:  # Top 3 by confidence
            finding = evidence.content[:150] + "..."
            main_findings.append(finding)
        
        # Identify conflicting points (simplified)
        conflicting_points = []
        if conflict_level > 0.3:
            conflicting_points.append(
                f"Confidence scores vary significantly (σ={np.std(confidence_scores):.3f})"
            )
            if len(set(ev.evidence_type for ev in evidence_list)) > 1:
                conflicting_points.append("Multiple evidence types present")
        
        # Calculate confidence distribution
        confidence_distribution = {}
        for evidence in evidence_list:
            level = self._get_confidence_level(evidence.confidence_score)
            if level.value not in confidence_distribution:
                confidence_distribution[level.value] = 0
            confidence_distribution[level.value] += 1
        
        # Normalize to percentages
        total = sum(confidence_distribution.values())
        confidence_distribution = {
            k: v/total for k, v in confidence_distribution.items()
        }
        
        # Update cluster
        cluster.consensus_level = consensus_level
        cluster.conflict_level = conflict_level
        cluster.main_findings = main_findings
        cluster.conflicting_points = conflicting_points
        cluster.confidence_distribution = confidence_distribution
        
        return cluster
    
    def _get_confidence_level(self, score: float) -> ConfidenceLevel:
        """Convert numeric confidence score to confidence level"""
        if score >= 0.90:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 0.75:
            return ConfidenceLevel.HIGH
        elif score >= 0.50:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.25:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    async def _identify_cross_domain_connections(
        self, 
        clusters: List[EvidenceCluster]
    ) -> List[Dict[str, Any]]:
        """Identify connections between different domains"""
        
        connections = []
        
        # Get domains from all evidence
        domain_clusters = defaultdict(list)
        for cluster in clusters:
            for evidence in cluster.evidence_sources:
                domain_clusters[evidence.domain].append((cluster, evidence))
        
        # Find cross-domain connections
        domains = list(domain_clusters.keys())
        for i, domain1 in enumerate(domains):
            for domain2 in domains[i+1:]:
                
                # Calculate connection strength (simplified)
                cluster1_topics = [c.topic for c, _ in domain_clusters[domain1]]
                cluster2_topics = [c.topic for c, _ in domain_clusters[domain2]]
                
                # Find topic overlap
                words1 = set()
                for topic in cluster1_topics:
                    words1.update(topic.lower().split())
                
                words2 = set()  
                for topic in cluster2_topics:
                    words2.update(topic.lower().split())
                
                overlap = len(words1.intersection(words2))
                if overlap > 0:
                    connection_strength = overlap / len(words1.union(words2))
                    
                    if connection_strength > 0.1:  # Minimum threshold
                        connections.append({
                            "domain1": domain1,
                            "domain2": domain2,
                            "connection_strength": connection_strength,
                            "shared_concepts": list(words1.intersection(words2)),
                            "description": f"Interdisciplinary connection between {domain1} and {domain2}",
                            "potential_applications": [
                                f"Combined {domain1}-{domain2} research",
                                f"Cross-domain validation of findings"
                            ]
                        })
        
        logger.info(f"✅ Identified {len(connections)} cross-domain connections")
        return connections
    
    async def _resolve_evidence_conflicts(
        self, 
        clusters: List[EvidenceCluster]
    ) -> List[Dict[str, Any]]:
        """Resolve conflicts within and between evidence clusters"""
        
        resolutions = []
        
        for cluster in clusters:
            if cluster.conflict_level > 0.3:  # Significant conflict
                
                # Identify conflict type
                evidence_list = cluster.evidence_sources
                confidence_scores = [ev.confidence_score for ev in evidence_list]
                
                conflict_info = {
                    "cluster_id": cluster.id,
                    "conflict_type": "confidence_variation",
                    "conflict_level": cluster.conflict_level,
                    "resolution_method": ConflictResolution.WEIGHTED_AVERAGE.value,
                    "resolved_value": np.average(
                        confidence_scores,
                        weights=[ev.reliability_score for ev in evidence_list]
                    ),
                    "confidence_in_resolution": 1.0 - cluster.conflict_level,
                    "explanation": f"Resolved confidence conflict using weighted average of {len(evidence_list)} sources"
                }
                
                resolutions.append(conflict_info)
        
        logger.info(f"✅ Resolved {len(resolutions)} evidence conflicts")
        return resolutions
    
    async def _generate_main_conclusions(
        self, 
        clusters: List[EvidenceCluster],
        cross_domain_connections: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate main conclusions from synthesized evidence"""
        
        conclusions = []
        
        # High-confidence cluster conclusions
        high_confidence_clusters = [
            c for c in clusters 
            if c.consensus_level > 0.7 and len(c.evidence_sources) >= 2
        ]
        
        for cluster in high_confidence_clusters:
            avg_confidence = np.mean([
                ev.confidence_score for ev in cluster.evidence_sources
            ])
            
            conclusion = (
                f"Strong evidence supports {cluster.topic.lower()} "
                f"(confidence: {avg_confidence:.2f}, consensus: {cluster.consensus_level:.2f})"
            )
            conclusions.append(conclusion)
        
        # Cross-domain insights
        strong_connections = [
            conn for conn in cross_domain_connections 
            if conn["connection_strength"] > 0.2
        ]
        
        for connection in strong_connections:
            conclusion = (
                f"Significant interdisciplinary connection identified between "
                f"{connection['domain1']} and {connection['domain2']} "
                f"(strength: {connection['connection_strength']:.2f})"
            )
            conclusions.append(conclusion)
        
        # Overall synthesis conclusion
        if len(clusters) > 1:
            total_evidence = sum(len(c.evidence_sources) for c in clusters)
            avg_consensus = np.mean([c.consensus_level for c in clusters])
            
            overall_conclusion = (
                f"Synthesis of {total_evidence} evidence sources across {len(clusters)} "
                f"topic areas reveals average consensus level of {avg_consensus:.2f}"
            )
            conclusions.append(overall_conclusion)
        
        return conclusions[:10]  # Limit to top 10 conclusions
    
    async def _identify_limitations(self, clusters: List[EvidenceCluster]) -> List[str]:
        """Identify limitations in the evidence synthesis"""
        
        limitations = []
        
        # Check for low-confidence clusters
        low_confidence_clusters = [c for c in clusters if c.consensus_level < 0.5]
        if low_confidence_clusters:
            limitations.append(
                f"{len(low_confidence_clusters)} evidence clusters show low consensus, "
                "indicating conflicting or uncertain findings"
            )
        
        # Check for evidence type diversity
        all_evidence_types = set()
        for cluster in clusters:
            for evidence in cluster.evidence_sources:
                all_evidence_types.add(evidence.evidence_type.value)
        
        if len(all_evidence_types) < 3:
            limitations.append(
                f"Limited evidence type diversity ({len(all_evidence_types)} types), "
                "may bias conclusions toward specific methodological approaches"
            )
        
        # Check for recent evidence
        total_evidence = sum(len(c.evidence_sources) for c in clusters)
        recent_evidence = 0
        for cluster in clusters:
            for evidence in cluster.evidence_sources:
                age_years = (datetime.now(UTC) - evidence.publication_date).days / 365.25
                if age_years < 5:  # Published within 5 years
                    recent_evidence += 1
        
        if recent_evidence / total_evidence < 0.5:
            limitations.append(
                f"Only {recent_evidence}/{total_evidence} ({recent_evidence/total_evidence:.1%}) "
                "evidence sources are recent (< 5 years old)"
            )
        
        # Check for domain coverage
        domains = set()
        for cluster in clusters:
            for evidence in cluster.evidence_sources:
                domains.add(evidence.domain)
        
        if len(domains) == 1:
            limitations.append(
                "Evidence limited to single domain, may miss interdisciplinary perspectives"
            )
        
        return limitations
    
    async def _identify_evidence_gaps(
        self, 
        query: str, 
        clusters: List[EvidenceCluster]
    ) -> List[str]:
        """Identify gaps in the evidence base"""
        
        gaps = []
        
        # Check for missing evidence types
        present_types = set()
        for cluster in clusters:
            for evidence in cluster.evidence_sources:
                present_types.add(evidence.evidence_type.value)
        
        important_types = {
            EvidenceType.EXPERIMENTAL.value,
            EvidenceType.META_ANALYSIS.value,
            EvidenceType.LITERATURE_REVIEW.value
        }
        
        missing_types = important_types - present_types
        if missing_types:
            gaps.append(f"Missing evidence types: {', '.join(missing_types)}")
        
        # Check for methodological gaps
        has_quantitative = False
        has_qualitative = False
        
        for cluster in clusters:
            for evidence in cluster.evidence_sources:
                if evidence.statistical_power is not None and evidence.statistical_power > 0.8:
                    has_quantitative = True
                if evidence.evidence_type in [EvidenceType.CASE_STUDY, EvidenceType.OBSERVATIONAL]:
                    has_qualitative = True
        
        if not has_quantitative:
            gaps.append("Lack of high-powered quantitative studies")
        if not has_qualitative:
            gaps.append("Lack of qualitative/observational evidence")
        
        # Sample size analysis
        sample_sizes = []
        for cluster in clusters:
            for evidence in cluster.evidence_sources:
                if evidence.sample_size:
                    sample_sizes.append(evidence.sample_size)
        
        if sample_sizes:
            avg_sample_size = np.mean(sample_sizes)
            if avg_sample_size < 100:
                gaps.append(f"Small average sample size ({avg_sample_size:.0f})")
        else:
            gaps.append("Sample size information not available")
        
        return gaps
    
    async def _suggest_future_research(
        self, 
        clusters: List[EvidenceCluster],
        evidence_gaps: List[str]
    ) -> List[str]:
        """Suggest future research directions"""
        
        suggestions = []
        
        # Address evidence gaps
        for gap in evidence_gaps:
            if "Missing evidence types" in gap:
                suggestions.append(f"Conduct studies to address {gap.lower()}")
            elif "sample size" in gap.lower():
                suggestions.append("Design larger-scale studies with increased statistical power")
        
        # High-conflict areas need more research
        high_conflict_clusters = [c for c in clusters if c.conflict_level > 0.5]
        for cluster in high_conflict_clusters:
            suggestions.append(
                f"Resolve conflicts in {cluster.topic} through targeted research "
                f"or systematic reviews"
            )
        
        # Cross-domain opportunities
        domains = set()
        for cluster in clusters:
            for evidence in cluster.evidence_sources:
                domains.add(evidence.domain)
        
        if len(domains) > 1:
            domain_list = list(domains)
            for i in range(len(domain_list)):
                for j in range(i+1, len(domain_list)):
                    suggestions.append(
                        f"Explore interdisciplinary research combining "
                        f"{domain_list[i]} and {domain_list[j]} approaches"
                    )
        
        # Methodological improvements
        avg_method_score = 0
        method_count = 0
        for cluster in clusters:
            for evidence in cluster.evidence_sources:
                if evidence.methodology_score > 0:
                    avg_method_score += evidence.methodology_score
                    method_count += 1
        
        if method_count > 0 and avg_method_score / method_count < 0.7:
            suggestions.append("Improve methodological rigor in future studies")
        
        return suggestions[:8]  # Limit to top 8 suggestions
    
    def _calculate_overall_confidence(self, clusters: List[EvidenceCluster]) -> float:
        """Calculate overall confidence in the synthesis"""
        
        if not clusters:
            return 0.0
        
        # Weight by cluster size and consensus
        weighted_confidence = 0
        total_weight = 0
        
        for cluster in clusters:
            cluster_size = len(cluster.evidence_sources)
            weight = cluster_size * cluster.consensus_level
            
            # Average confidence in cluster
            cluster_confidence = np.mean([
                ev.confidence_score for ev in cluster.evidence_sources
            ])
            
            weighted_confidence += weight * cluster_confidence
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_confidence / total_weight
    
    def _assess_methodology_quality(self, evidence_sources: List[EvidenceSource]) -> Dict[str, float]:
        """Assess overall methodology quality"""
        
        assessment = {
            "overall_score": 0.0,
            "peer_review_rate": 0.0,
            "average_citations": 0.0,
            "methodology_score": 0.0,
            "sample_size_adequacy": 0.0,
            "statistical_power": 0.0
        }
        
        if not evidence_sources:
            return assessment
        
        # Peer review rate
        peer_reviewed = sum(1 for ev in evidence_sources if ev.peer_reviewed)
        assessment["peer_review_rate"] = peer_reviewed / len(evidence_sources)
        
        # Average citations
        citations = [ev.citations for ev in evidence_sources if ev.citations > 0]
        assessment["average_citations"] = np.mean(citations) if citations else 0.0
        
        # Methodology scores
        method_scores = [ev.methodology_score for ev in evidence_sources if ev.methodology_score > 0]
        assessment["methodology_score"] = np.mean(method_scores) if method_scores else 0.0
        
        # Sample size adequacy (simplified)
        adequate_samples = sum(
            1 for ev in evidence_sources 
            if ev.sample_size and ev.sample_size >= 30
        )
        total_with_samples = sum(
            1 for ev in evidence_sources 
            if ev.sample_size is not None
        )
        assessment["sample_size_adequacy"] = (
            adequate_samples / total_with_samples if total_with_samples > 0 else 0.0
        )
        
        # Statistical power
        power_scores = [ev.statistical_power for ev in evidence_sources if ev.statistical_power]
        assessment["statistical_power"] = np.mean(power_scores) if power_scores else 0.0
        
        # Overall score (weighted average)
        weights = [0.25, 0.15, 0.25, 0.15, 0.20]  # Respective weights
        scores = [
            assessment["peer_review_rate"],
            min(assessment["average_citations"] / 50, 1.0),  # Normalize citations
            assessment["methodology_score"],
            assessment["sample_size_adequacy"],
            assessment["statistical_power"]
        ]
        
        assessment["overall_score"] = sum(w * s for w, s in zip(weights, scores))
        
        return assessment
    
    # Conflict resolution methods
    def _weighted_average_resolution(self, conflicting_values: List[Tuple[float, float]]) -> float:
        """Resolve conflict using weighted average"""
        values, weights = zip(*conflicting_values)
        return np.average(values, weights=weights)
    
    def _highest_confidence_resolution(self, conflicting_values: List[Tuple[float, float]]) -> float:
        """Resolve conflict by taking highest confidence value"""
        return max(conflicting_values, key=lambda x: x[1])[0]
    
    def _most_recent_resolution(self, conflicting_evidence: List[EvidenceSource]) -> float:
        """Resolve conflict by taking most recent evidence"""
        most_recent = max(conflicting_evidence, key=lambda x: x.publication_date)
        return most_recent.confidence_score
    
    def _expert_consensus_resolution(self, conflicting_values: List[Tuple[float, float]]) -> float:
        """Resolve conflict using expert consensus (simplified)"""
        # In practice, this would involve expert judgment
        return self._weighted_average_resolution(conflicting_values)
    
    def _meta_analysis_resolution(self, conflicting_values: List[Tuple[float, float]]) -> float:
        """Resolve conflict using meta-analysis approach"""
        # Simplified meta-analysis (would use proper statistical methods in practice)
        values, weights = zip(*conflicting_values)
        return np.average(values, weights=weights)
    
    async def get_synthesis_health_status(self) -> Dict[str, Any]:
        """Get health status of the evidence synthesis service"""
        return {
            "service_name": "AdvancedEvidenceSynthesisService",
            "status": "healthy",
            "cache_size": len(self.synthesis_cache),
            "max_cache_size": self.cache_size,
            "supported_evidence_types": [et.value for et in EvidenceType],
            "supported_domains": list(self.domain_expertise.keys()),
            "conflict_resolution_methods": [cr.value for cr in ConflictResolution],
            "version": "1.0.0",
            "last_check": datetime.now(UTC).isoformat()
        }

# Backwards compatibility alias
EvidenceSynthesisService = AdvancedEvidenceSynthesisService
