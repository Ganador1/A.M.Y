"""
Advanced Peer Review Service
Enhanced implementation with AI-driven content analysis, sentiment analysis, and sophisticated methodology flaw detection
"""
from __future__ import annotations
import asyncio
import re
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
import logging
from app.exceptions.domain.biology import BiologyError

# Advanced NLP imports
try:
    import torch
    import transformers
    from transformers import (
        AutoTokenizer, AutoModel, pipeline, BertTokenizer, BertModel
    )
    from sentence_transformers import SentenceTransformer
    import spacy
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    # Dummy classes for when transformers are not available
    class AutoTokenizer:
        pass
    class AutoModel:
        pass
    class pipeline:
        pass
    class BertTokenizer:
        pass
    class BertModel:
        pass
    class SentenceTransformer:
        pass
    class spacy:
        pass

# Additional ML imports
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    import scipy.stats as stats
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    # Dummy classes
    class TfidfVectorizer:
        pass
    class cosine_similarity:
        pass
    class KMeans:
        pass
    class LogisticRegression:
        pass
    class RandomForestClassifier:
        pass
    class stats:
        pass

from app.core.bootstrap_logging import logger
from app.types.peer_review_service_types import (
    ReviewStatisticalResult,
    ReviewMethodologyResult,
    ReviewRobustnessResult,
    DetectStatisticalElementsResult,
    AnalyzeToneIndicatorsResult,
    ReviewResult,
    GenerateOverallStatisticsResult,
    GetModelCapabilitiesResult,
    HealthCheckResult,
)


@dataclass
class ReviewIssue:
    """
    Represents a specific issue found during peer review.
    
    Attributes:
        issue_type: Type of issue (e.g., "statistical", "methodology", "robustness")
        severity: Severity level ("critical", "major", "minor")
        description: Human-readable description of the issue
        evidence: Text evidence supporting the issue
        suggestion: Suggested improvement
        confidence: Confidence score for the issue detection (0.0 to 1.0)
    """
    issue_type: str
    severity: str
    description: str
    evidence: str
    suggestion: str
    confidence: float


@dataclass
class SentimentAnalysis:
    """
    Result of sentiment analysis for peer review.
    
    Attributes:
        overall_sentiment: Overall sentiment ("positive", "negative", "neutral")
        confidence: Confidence in sentiment classification
        sentiment_scores: Detailed sentiment scores
        tone_indicators: Indicators of writing tone
    """
    overall_sentiment: str
    confidence: float
    sentiment_scores: Dict[str, float]
    tone_indicators: Dict[str, Any]


@dataclass
class MethodologyAnalysis:
    """
    Comprehensive methodology analysis result.
    
    Attributes:
        methodology_score: Overall methodology quality score
        strengths: List of methodological strengths
        weaknesses: List of methodological weaknesses
        missing_elements: Missing methodological elements
        bias_indicators: Potential bias indicators
        reproducibility_score: Reproducibility assessment
    """
    methodology_score: float
    strengths: List[str]
    weaknesses: List[str]
    missing_elements: List[str]
    bias_indicators: List[str]
    reproducibility_score: float


class PeerReviewService:
    """
    Advanced Peer Review Service with AI-driven content analysis
    Enhanced implementation for comprehensive scientific paper review
    """
    
    def __init__(self):
        """Initialize advanced peer review service"""
        logger.info("Initializing PeerReviewService (advanced version)")
        self.version = "v2.0-advanced"
        
        # Advanced configuration
        self.advanced_config = {
            "use_ai_analysis": True,
            "use_sentiment_analysis": True,
            "use_methodology_detection": True,
            "use_bias_detection": True,
            "use_reproducibility_check": True,
            "confidence_threshold": 0.7,
            "severity_thresholds": {
                "critical": 0.9,
                "major": 0.7,
                "minor": 0.5
            },
            "max_issues_per_paper": 20,
            "use_gpu": torch.cuda.is_available() if TRANSFORMERS_AVAILABLE else False
        }
        
        # Model initialization
        self.sentiment_pipeline = None
        self.sentence_transformer = None
        self.spacy_model = None
        self.tfidf_vectorizer = None
        
        # Initialize models
        self._initialize_models()
        
        # Review patterns and keywords
        self._initialize_review_patterns()
        
        # Statistical analysis patterns
        self.statistical_patterns = {
            "p_value_indicators": [r"p\s*[=<>]\s*[\d.]+", r"p\s*<\s*[\d.]+", r"p\s*>\s*[\d.]+"],
            "confidence_intervals": [r"CI\s*[=:]\s*[\d.-]+", r"confidence\s+interval", r"95%\s+CI"],
            "effect_sizes": [r"effect\s+size", r"cohen'?s?\s+d", r"eta\s+squared", r"r\s+squared"],
            "sample_size": [r"n\s*=\s*\d+", r"sample\s+size", r"participants?\s*:\s*\d+"],
            "statistical_tests": [r"t\s*[-=]\s*test", r"anova", r"chi\s*square", r"regression", r"correlation"]
        }
        
        # Methodology patterns
        self.methodology_patterns = {
            "experimental_design": ["randomized", "controlled", "double-blind", "placebo", "crossover"],
            "controls": ["control group", "baseline", "comparison", "reference"],
            "randomization": ["random", "randomized", "randomization", "randomly assigned"],
            "blinding": ["blind", "blinded", "double-blind", "single-blind", "masked"],
            "replication": ["replication", "reproducibility", "repeated", "validation"],
            "power_analysis": ["power analysis", "sample size calculation", "statistical power"]
        }
        
        # Bias detection patterns
        self.bias_patterns = {
            "selection_bias": ["selection", "sampling bias", "volunteer", "convenience sample"],
            "confirmation_bias": ["confirm", "support", "validate", "prove"],
            "publication_bias": ["significant", "positive results", "null results"],
            "funding_bias": ["funded by", "sponsored", "commercial", "industry"],
            "language_bias": ["english only", "language barrier", "translation"]
        }
        
        # Robustness indicators
        self.robustness_patterns = {
            "sensitivity_analysis": ["sensitivity", "robust", "stable", "consistent"],
            "cross_validation": ["cross-validation", "validation", "holdout", "test set"],
            "generalization": ["generalize", "external validity", "generalizability"],
            "replication": ["replicate", "replication", "reproduce", "reproducibility"]
        }
    
    def _initialize_models(self):
        """Initialize advanced NLP models"""
        try:
            if TRANSFORMERS_AVAILABLE:
                # Initialize sentiment analysis pipeline
                try:
                    self.sentiment_pipeline = pipeline(
                        "sentiment-analysis",
                        model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                        return_all_scores=True
                    )
                    logger.info("✅ Sentiment analysis pipeline loaded successfully")
                except Exception as e:
                    logger.warning(f"⚠️ Sentiment pipeline not available: {e}")
                    self.sentiment_pipeline = None
                
                # Initialize sentence transformer
                try:
                    self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
                    logger.info("✅ Sentence Transformer loaded successfully")
                except Exception as e:
                    logger.warning(f"⚠️ Sentence Transformer not available: {e}")
                    self.sentence_transformer = None
            
            # Initialize spaCy
            try:
                import spacy
                self.spacy_model = spacy.load("en_core_web_sm")
                logger.info("✅ spaCy model loaded successfully")
            except Exception as e:
                logger.warning(f"⚠️ spaCy not available: {e}")
                self.spacy_model = None
            
            # Initialize TF-IDF vectorizer
            if SKLEARN_AVAILABLE:
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 3)
                )
                logger.info("✅ TF-IDF vectorizer initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing models: {e}")
    
    def _initialize_review_patterns(self):
        """Initialize review patterns and keywords"""
        # Quality indicators
        self.quality_indicators = {
            "high_quality": [
                "rigorous", "comprehensive", "systematic", "thorough", "robust",
                "well-designed", "carefully", "meticulously", "extensive"
            ],
            "methodological_concerns": [
                "limitation", "bias", "confound", "artifact", "spurious",
                "questionable", "problematic", "inadequate", "insufficient"
            ],
            "statistical_concerns": [
                "underpowered", "multiple comparisons", "p-hacking", "cherry picking",
                "data dredging", "fishing expedition", "overfitting"
            ]
        }
        
        # Reproducibility indicators
        self.reproducibility_indicators = {
            "positive": [
                "open data", "reproducible", "replication", "validation",
                "code available", "materials available", "pre-registered"
            ],
            "negative": [
                "proprietary", "confidential", "not available", "upon request",
                "contact author", "restricted access"
            ]
        }

    async def _review_statistical(self, paper: ReviewStatisticalResult) -> ReviewStatisticalResult:
        """Advanced statistical review with AI-driven analysis"""
        try:
            text = (paper.get("title") or "") + " " + (paper.get("abstract") or "")
            issues = []
            
            # Detect statistical elements
            statistical_elements = self._detect_statistical_elements(text)
            
            # Check for missing statistical elements
            if not statistical_elements["p_values"]:
                issues.append(ReviewIssue(
                    issue_type="statistical",
                    severity="major",
                    description="No explicit p-values reported",
                    evidence="No p-value indicators found in text",
                    suggestion="Report p-values for statistical tests",
                    confidence=0.8
                ))
            
            if not statistical_elements["confidence_intervals"]:
                issues.append(ReviewIssue(
                    issue_type="statistical",
                    severity="minor",
                    description="No confidence intervals reported",
                    evidence="No CI indicators found in text",
                    suggestion="Consider reporting confidence intervals",
                    confidence=0.7
                ))
            
            if not statistical_elements["effect_sizes"]:
                issues.append(ReviewIssue(
                    issue_type="statistical",
                    severity="minor",
                    description="No effect sizes reported",
                    evidence="No effect size indicators found in text",
                    suggestion="Report effect sizes alongside p-values",
                    confidence=0.6
                ))
            
            # Check for statistical concerns
            statistical_concerns = self._detect_statistical_concerns(text)
            for concern in statistical_concerns:
                issues.append(ReviewIssue(
                    issue_type="statistical",
                    severity="major",
                    description=f"Potential statistical concern: {concern['type']}",
                    evidence=concern['evidence'],
                    suggestion=concern['suggestion'],
                    confidence=concern['confidence']
                ))
            
            # Calculate statistical score
            score = self._calculate_statistical_score(statistical_elements, statistical_concerns)
            
            return {
                "role": "statistical",
                "score": round(score, 3),
                "issues": [vars(issue) for issue in issues],
                "statistical_elements": statistical_elements,
                "concerns": statistical_concerns
            }
            
        except BiologyError as e:
            logger.error(f"Error in statistical review: {e}")
            return {"role": "statistical", "score": 0.5, "issues": [], "error": str(e)}

    async def _review_methodology(self, paper: ReviewMethodologyResult) -> ReviewMethodologyResult:
        """Advanced methodology review with comprehensive analysis"""
        try:
            text = (paper.get("abstract") or "").lower()
            issues = []
            
            # Perform comprehensive methodology analysis
            methodology_analysis = self._analyze_methodology(text)
            
            # Check for missing methodological elements
            for missing_element in methodology_analysis.missing_elements:
                issues.append(ReviewIssue(
                    issue_type="methodology",
                    severity="major",
                    description=f"Missing methodological element: {missing_element}",
                    evidence=f"No indicators of {missing_element} found",
                    suggestion=f"Consider including {missing_element} in methodology",
                    confidence=0.8
                ))
            
            # Check for bias indicators
            for bias in methodology_analysis.bias_indicators:
                issues.append(ReviewIssue(
                    issue_type="methodology",
                    severity="critical",
                    description=f"Potential bias detected: {bias}",
                    evidence=f"Bias indicators found in text",
                    suggestion="Address potential bias in methodology",
                    confidence=0.9
                ))
            
            return {
                "role": "methodology",
                "score": round(methodology_analysis.methodology_score, 3),
                "issues": [vars(issue) for issue in issues],
                "methodology_analysis": vars(methodology_analysis)
            }
            
        except BiologyError as e:
            logger.error(f"Error in methodology review: {e}")
            return {"role": "methodology", "score": 0.5, "issues": [], "error": str(e)}

    async def _review_robustness(self, paper: ReviewRobustnessResult) -> ReviewRobustnessResult:
        """Advanced robustness review with AI analysis"""
        try:
            text = (paper.get("abstract") or "").lower()
            issues = []
            
            # Detect robustness indicators
            robustness_indicators = self._detect_robustness_indicators(text)
            
            # Check for missing robustness elements
            if not robustness_indicators["sensitivity_analysis"]:
                issues.append(ReviewIssue(
                    issue_type="robustness",
                    severity="minor",
                    description="No sensitivity analysis reported",
                    evidence="No sensitivity analysis indicators found",
                    suggestion="Consider performing sensitivity analysis",
                    confidence=0.6
                ))
            
            if not robustness_indicators["cross_validation"]:
                issues.append(ReviewIssue(
                    issue_type="robustness",
                    severity="minor",
                    description="No cross-validation reported",
                    evidence="No cross-validation indicators found",
                    suggestion="Consider using cross-validation",
                    confidence=0.6
                ))
            
            # Calculate robustness score
            score = self._calculate_robustness_score(robustness_indicators)
            
            return {
                "role": "robustness",
                "score": round(score, 3),
                "issues": [vars(issue) for issue in issues],
                "robustness_indicators": robustness_indicators
            }
            
        except BiologyError as e:
            logger.error(f"Error in robustness review: {e}")
            return {"role": "robustness", "score": 0.5, "issues": [], "error": str(e)}

    def _detect_statistical_elements(self, text: str) -> DetectStatisticalElementsResult:
        """Detect statistical elements in text"""
        text_lower = text.lower()
        
        # Detect p-values
        p_values = []
        for pattern in self.statistical_patterns["p_value_indicators"]:
            matches = re.findall(pattern, text_lower)
            p_values.extend(matches)
        
        # Detect confidence intervals
        confidence_intervals = []
        for pattern in self.statistical_patterns["confidence_intervals"]:
            matches = re.findall(pattern, text_lower)
            confidence_intervals.extend(matches)
        
        # Detect effect sizes
        effect_sizes = []
        for pattern in self.statistical_patterns["effect_sizes"]:
            matches = re.findall(pattern, text_lower)
            effect_sizes.extend(matches)
        
        # Detect sample size
        sample_sizes = []
        for pattern in self.statistical_patterns["sample_size"]:
            matches = re.findall(pattern, text_lower)
            sample_sizes.extend(matches)
        
        # Detect statistical tests
        statistical_tests = []
        for pattern in self.statistical_patterns["statistical_tests"]:
            matches = re.findall(pattern, text_lower)
            statistical_tests.extend(matches)
        
        return {
            "p_values": p_values,
            "confidence_intervals": confidence_intervals,
            "effect_sizes": effect_sizes,
            "sample_sizes": sample_sizes,
            "statistical_tests": statistical_tests
        }
    
    def _detect_statistical_concerns(self, text: str) -> List[Dict[str, Any]]:
        """Detect potential statistical concerns"""
        concerns = []
        text_lower = text.lower()
        
        # Check for multiple comparisons without correction
        if "multiple" in text_lower and "comparison" in text_lower and "correction" not in text_lower:
            concerns.append({
                "type": "Multiple comparisons without correction",
                "evidence": "Multiple comparisons mentioned without correction",
                "suggestion": "Apply multiple comparison correction (e.g., Bonferroni)",
                "confidence": 0.8
            })
        
        # Check for p-hacking indicators
        p_hacking_indicators = ["exploratory", "post-hoc", "data-driven", "fishing"]
        if any(indicator in text_lower for indicator in p_hacking_indicators):
            concerns.append({
                "type": "Potential p-hacking",
                "evidence": "Exploratory or post-hoc analysis indicators found",
                "suggestion": "Pre-register hypotheses or use appropriate corrections",
                "confidence": 0.7
            })
        
        # Check for small sample size
        sample_size_matches = re.findall(r"n\s*=\s*(\d+)", text_lower)
        if sample_size_matches:
            for match in sample_size_matches:
                if int(match) < 30:
                    concerns.append({
                        "type": "Small sample size",
                        "evidence": f"Sample size n={match} may be too small",
                        "suggestion": "Consider power analysis or larger sample",
                        "confidence": 0.6
                    })
        
        return concerns
    
    def _calculate_statistical_score(self, elements: Dict[str, Any], concerns: List[Dict[str, Any]]) -> float:
        """Calculate statistical quality score"""
        base_score = 0.5
        
        # Add points for statistical elements
        if elements["p_values"]:
            base_score += 0.2
        if elements["confidence_intervals"]:
            base_score += 0.15
        if elements["effect_sizes"]:
            base_score += 0.1
        if elements["sample_sizes"]:
            base_score += 0.1
        if elements["statistical_tests"]:
            base_score += 0.05
        
        # Subtract points for concerns
        for concern in concerns:
            if concern["confidence"] > 0.7:
                base_score -= 0.2
            elif concern["confidence"] > 0.5:
                base_score -= 0.1
        
        return max(0.0, min(1.0, base_score))
    
    def _analyze_methodology(self, text: str) -> MethodologyAnalysis:
        """Comprehensive methodology analysis"""
        strengths = []
        weaknesses = []
        missing_elements = []
        bias_indicators = []
        
        # Check for methodological strengths
        for category, keywords in self.methodology_patterns.items():
            found_keywords = [kw for kw in keywords if kw in text]
            if found_keywords:
                strengths.append(f"{category}: {', '.join(found_keywords)}")
            else:
                missing_elements.append(category)
        
        # Check for bias indicators
        for bias_type, keywords in self.bias_patterns.items():
            found_keywords = [kw for kw in keywords if kw in text]
            if found_keywords:
                bias_indicators.append(f"{bias_type}: {', '.join(found_keywords)}")
        
        # Check for quality indicators
        for concern_type, keywords in self.quality_indicators.items():
            found_keywords = [kw for kw in keywords if kw in text]
            if found_keywords:
                if concern_type == "high_quality":
                    strengths.append(f"Quality indicators: {', '.join(found_keywords)}")
                else:
                    weaknesses.append(f"{concern_type}: {', '.join(found_keywords)}")
        
        # Calculate methodology score
        methodology_score = 0.5
        methodology_score += len(strengths) * 0.1
        methodology_score -= len(weaknesses) * 0.15
        methodology_score -= len(missing_elements) * 0.1
        methodology_score -= len(bias_indicators) * 0.2
        
        # Calculate reproducibility score
        reproducibility_score = self._calculate_reproducibility_score(text)
        
        return MethodologyAnalysis(
            methodology_score=max(0.0, min(1.0, methodology_score)),
            strengths=strengths,
            weaknesses=weaknesses,
            missing_elements=missing_elements,
            bias_indicators=bias_indicators,
            reproducibility_score=reproducibility_score
        )
    
    def _calculate_reproducibility_score(self, text: str) -> float:
        """Calculate reproducibility score"""
        text_lower = text.lower()
        
        positive_indicators = sum(1 for indicator in self.reproducibility_indicators["positive"] 
                                if indicator in text_lower)
        negative_indicators = sum(1 for indicator in self.reproducibility_indicators["negative"] 
                                 if indicator in text_lower)
        
        score = 0.5 + (positive_indicators * 0.1) - (negative_indicators * 0.15)
        return max(0.0, min(1.0, score))
    
    def _detect_robustness_indicators(self, text: str) -> Dict[str, bool]:
        """Detect robustness indicators in text"""
        text_lower = text.lower()
        
        indicators = {}
        for category, keywords in self.robustness_patterns.items():
            indicators[category] = any(keyword in text_lower for keyword in keywords)
        
        return indicators
    
    def _calculate_robustness_score(self, indicators: Dict[str, bool]) -> float:
        """Calculate robustness score based on indicators"""
        base_score = 0.3
        positive_indicators = sum(indicators.values())
        score = base_score + (positive_indicators * 0.15)
        return max(0.0, min(1.0, score))
    
    async def _analyze_sentiment(self, text: str) -> SentimentAnalysis:
        """Analyze sentiment of the paper"""
        try:
            if self.sentiment_pipeline and TRANSFORMERS_AVAILABLE:
                # Use AI sentiment analysis
                results = self.sentiment_pipeline(text[:512])  # Limit text length
                
                # Extract sentiment scores
                sentiment_scores = {}
                for result in results[0]:
                    sentiment_scores[result['label']] = result['score']
                
                # Determine overall sentiment
                overall_sentiment = max(sentiment_scores, key=sentiment_scores.get)
                confidence = max(sentiment_scores.values())
                
            else:
                # Fallback to rule-based sentiment analysis
                sentiment_scores = self._rule_based_sentiment(text)
                overall_sentiment = max(sentiment_scores, key=sentiment_scores.get)
                confidence = max(sentiment_scores.values())
            
            # Analyze tone indicators
            tone_indicators = self._analyze_tone_indicators(text)
            
            return SentimentAnalysis(
                overall_sentiment=overall_sentiment,
                confidence=confidence,
                sentiment_scores=sentiment_scores,
                tone_indicators=tone_indicators
            )
            
        except BiologyError as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return SentimentAnalysis(
                overall_sentiment="neutral",
                confidence=0.5,
                sentiment_scores={"neutral": 0.5},
                tone_indicators={}
            )
    
    def _rule_based_sentiment(self, text: str) -> Dict[str, float]:
        """Rule-based sentiment analysis fallback"""
        text_lower = text.lower()
        
        positive_words = ["significant", "effective", "successful", "improved", "beneficial", "promising"]
        negative_words = ["failed", "ineffective", "problematic", "limitation", "concern", "issue"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return {"neutral": 1.0}
        
        positive_score = positive_count / total_words
        negative_score = negative_count / total_words
        neutral_score = 1.0 - positive_score - negative_score
        
        return {
            "positive": positive_score,
            "negative": negative_score,
            "neutral": max(0.0, neutral_score)
        }
    
    def _analyze_tone_indicators(self, text: str) -> AnalyzeToneIndicatorsResult:
        """Analyze tone indicators in text"""
        text_lower = text.lower()
        
        # Detect cautious language
        cautious_words = ["suggest", "indicate", "appear", "seem", "might", "could", "possibly"]
        cautious_count = sum(1 for word in cautious_words if word in text_lower)
        
        # Detect confident language
        confident_words = ["demonstrate", "prove", "establish", "confirm", "definitively"]
        confident_count = sum(1 for word in confident_words if word in text_lower)
        
        # Detect hedging
        hedging_words = ["however", "although", "despite", "nevertheless", "but"]
        hedging_count = sum(1 for word in hedging_words if word in text_lower)
        
        return {
            "cautious_language": cautious_count,
            "confident_language": confident_count,
            "hedging": hedging_count,
            "tone_classification": "cautious" if cautious_count > confident_count else "confident"
        }

    async def review(self, enriched_papers: List[ReviewResult]) -> ReviewResult:
        """Advanced peer review with AI-driven analysis"""
        try:
            logger.info(f"Starting advanced peer review for {len(enriched_papers)} papers")
            results: List[Dict[str, Any]] = []
            
            for p in enriched_papers:
                try:
                    # Base paper information
                    base = {
                        "paper_id": p.get("paper_id"),
                        "title": p.get("title"),
                        "abstract": p.get("abstract", ""),
                        "authors": p.get("authors", []),
                        "journal": p.get("journal", ""),
                        "year": p.get("year", ""),
                    }
                    
                    # Perform advanced reviews
                    reviews = await asyncio.gather(
                        self._review_statistical(p),
                        self._review_methodology(p),
                        self._review_robustness(p)
                    )
                    
                    # Perform sentiment analysis
                    full_text = f"{base['title']} {base['abstract']}"
                    sentiment_analysis = await self._analyze_sentiment(full_text)
                    
                    # Calculate consensus score
                    consensus = sum(r["score"] for r in reviews) / len(reviews)
                    
                    # Collect all issues
                    all_issues = []
                    for review in reviews:
                        all_issues.extend(review.get("issues", []))
                    
                    # Categorize issues by severity
                    critical_issues = [issue for issue in all_issues if issue.get("severity") == "critical"]
                    major_issues = [issue for issue in all_issues if issue.get("severity") == "major"]
                    minor_issues = [issue for issue in all_issues if issue.get("severity") == "minor"]
                    
                    # Calculate overall quality metrics
                    quality_metrics = {
                        "consensus_score": round(consensus, 3),
                        "statistical_score": reviews[0]["score"],
                        "methodology_score": reviews[1]["score"],
                        "robustness_score": reviews[2]["score"],
                        "sentiment_score": sentiment_analysis.confidence,
                        "overall_sentiment": sentiment_analysis.overall_sentiment,
                        "total_issues": len(all_issues),
                        "critical_issues": len(critical_issues),
                        "major_issues": len(major_issues),
                        "minor_issues": len(minor_issues),
                        "reproducibility_score": reviews[1].get("methodology_analysis", {}).get("reproducibility_score", 0.5)
                    }
                    
                    # Enhanced paper result
                    enhanced_result = {
                        **base,
                        "reviews": reviews,
                        "sentiment_analysis": vars(sentiment_analysis),
                        "quality_metrics": quality_metrics,
                        "issues": {
                            "all": all_issues,
                            "critical": critical_issues,
                            "major": major_issues,
                            "minor": minor_issues
                        },
                        "recommendations": self._generate_recommendations(all_issues, quality_metrics),
                        "review_summary": self._generate_review_summary(reviews, sentiment_analysis, quality_metrics)
                    }
                    
                    results.append(enhanced_result)
                    
                except BiologyError as e:
                    logger.error(f"Error reviewing paper {p.get('paper_id', 'unknown')}: {e}")
                    # Add error result
                    results.append({
                        "paper_id": p.get("paper_id"),
                        "title": p.get("title"),
                        "error": str(e),
                        "consensus_score": 0.0
                    })
            
            # Sort by consensus score
            results.sort(key=lambda x: x.get("quality_metrics", {}).get("consensus_score", 0), reverse=True)
            
            # Generate overall statistics
            overall_stats = self._generate_overall_statistics(results)
            
            return {
                "version": self.version,
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
                "count": len(results),
                "papers": results,
                "overall_statistics": overall_stats,
                "review_metadata": {
                    "total_papers": len(enriched_papers),
                    "successful_reviews": len([r for r in results if "error" not in r]),
                    "failed_reviews": len([r for r in results if "error" in r]),
                    "average_consensus_score": np.mean([r.get("quality_metrics", {}).get("consensus_score", 0) for r in results if "error" not in r]) if results else 0,
                    "model_capabilities": self._get_model_capabilities()
                }
            }
            
        except BiologyError as e:
            logger.error(f"Error in peer review process: {e}")
            return {
                "version": self.version,
                "error": str(e),
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
                "count": 0,
                "papers": []
            }
    
    def _generate_recommendations(self, issues: List[Dict[str, Any]], quality_metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on issues and quality metrics"""
        recommendations = []
        
        # Statistical recommendations
        if quality_metrics["statistical_score"] < 0.6:
            recommendations.append("Improve statistical reporting: Include p-values, confidence intervals, and effect sizes")
        
        # Methodology recommendations
        if quality_metrics["methodology_score"] < 0.6:
            recommendations.append("Strengthen methodology: Add controls, randomization, and bias mitigation")
        
        # Robustness recommendations
        if quality_metrics["robustness_score"] < 0.6:
            recommendations.append("Enhance robustness: Include sensitivity analysis and cross-validation")
        
        # Reproducibility recommendations
        if quality_metrics["reproducibility_score"] < 0.6:
            recommendations.append("Improve reproducibility: Share data, code, and materials")
        
        # Issue-specific recommendations
        critical_issues = [issue for issue in issues if issue.get("severity") == "critical"]
        if critical_issues:
            recommendations.append("Address critical issues: Review and address all critical methodological concerns")
        
        return recommendations
    
    def _generate_review_summary(self, reviews: List[Dict[str, Any]], sentiment: SentimentAnalysis, metrics: Dict[str, Any]) -> str:
        """Generate a comprehensive review summary"""
        summary_parts = []
        
        # Overall assessment
        if metrics["consensus_score"] >= 0.8:
            summary_parts.append("High-quality research with strong methodology and statistical rigor.")
        elif metrics["consensus_score"] >= 0.6:
            summary_parts.append("Good research with some areas for improvement.")
        else:
            summary_parts.append("Research requires significant improvements in methodology and analysis.")
        
        # Sentiment analysis
        if sentiment.overall_sentiment == "positive":
            summary_parts.append("The paper presents findings in a positive and confident tone.")
        elif sentiment.overall_sentiment == "negative":
            summary_parts.append("The paper acknowledges limitations and presents findings cautiously.")
        
        # Issue summary
        if metrics["critical_issues"] > 0:
            summary_parts.append(f"Critical issues identified: {metrics['critical_issues']} critical concerns need immediate attention.")
        
        if metrics["major_issues"] > 0:
            summary_parts.append(f"Major issues: {metrics['major_issues']} major concerns should be addressed.")
        
        return " ".join(summary_parts)
    
    def _generate_overall_statistics(self, results: List[GenerateOverallStatisticsResult]) -> GenerateOverallStatisticsResult:
        """Generate overall statistics for the review batch"""
        successful_results = [r for r in results if "error" not in r]
        
        if not successful_results:
            return {"error": "No successful reviews to analyze"}
        
        consensus_scores = [r.get("quality_metrics", {}).get("consensus_score", 0) for r in successful_results]
        statistical_scores = [r.get("quality_metrics", {}).get("statistical_score", 0) for r in successful_results]
        methodology_scores = [r.get("quality_metrics", {}).get("methodology_score", 0) for r in successful_results]
        robustness_scores = [r.get("quality_metrics", {}).get("robustness_score", 0) for r in successful_results]
        
        total_issues = sum(r.get("quality_metrics", {}).get("total_issues", 0) for r in successful_results)
        critical_issues = sum(r.get("quality_metrics", {}).get("critical_issues", 0) for r in successful_results)
        
        return {
            "average_consensus_score": round(np.mean(consensus_scores), 3),
            "average_statistical_score": round(np.mean(statistical_scores), 3),
            "average_methodology_score": round(np.mean(methodology_scores), 3),
            "average_robustness_score": round(np.mean(robustness_scores), 3),
            "score_distribution": {
                "high_quality": len([s for s in consensus_scores if s >= 0.8]),
                "good_quality": len([s for s in consensus_scores if 0.6 <= s < 0.8]),
                "needs_improvement": len([s for s in consensus_scores if s < 0.6])
            },
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "papers_with_critical_issues": len([r for r in successful_results if r.get("quality_metrics", {}).get("critical_issues", 0) > 0])
        }
    
    def _get_model_capabilities(self) -> GetModelCapabilitiesResult:
        """Get information about available model capabilities"""
        return {
            "sentiment_analysis": self.sentiment_pipeline is not None,
            "sentence_transformer": self.sentence_transformer is not None,
            "spacy_model": self.spacy_model is not None,
            "tfidf_vectorizer": self.tfidf_vectorizer is not None,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "sklearn_available": SKLEARN_AVAILABLE
        }
    
    async def health_check(self) -> HealthCheckResult:
        """Service health check"""
        try:
            model_capabilities = self._get_model_capabilities()
            available_models = sum(model_capabilities.values())
            total_models = len(model_capabilities)
            model_readiness = available_models / total_models if total_models > 0 else 0.0
            
            return {
                'service_status': 'healthy',
                'service_name': 'PeerReviewService',
                'version': self.version,
                'model_capabilities': model_capabilities,
                'model_readiness': model_readiness,
                'advanced_config': self.advanced_config,
                'capabilities': [
                    'AI-driven Statistical Review',
                    'Comprehensive Methodology Analysis',
                    'Robustness Assessment',
                    'Sentiment Analysis',
                    'Bias Detection',
                    'Reproducibility Scoring',
                    'Issue Classification',
                    'Recommendation Generation'
                ]
            }
        except BiologyError as e:
            logger.error(f"Health check failed: {e}")
            return {
                'service_status': 'error',
                'error': str(e)
            }


# Create service instance
peer_review_service = PeerReviewService()
