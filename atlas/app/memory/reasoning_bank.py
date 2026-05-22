"""
ReasoningBank - Memory-Driven Framework for LLM Agent Evolution

Based on arXiv 2025 ReasoningBank framework:
- Stores successful and failed research experiences
- Abstracts high-level strategies from patterns
- Enables continuous learning without retraining
- Retrieves relevant past experiences for new problems

Author: AXIOM Team
"""

from __future__ import annotations

import json
import os
import hashlib
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Try to import ChromaDB, fall back to JSON storage
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from app.core.bootstrap_logging import logger


@dataclass
class Experience:
    """A research experience (success or failure) stored in memory."""
    experience_id: str
    domain: str
    topic: str
    hypothesis: str
    outcome: str  # "success" or "failure"
    score: float
    rejection_reason: Optional[str] = None
    tools_used: List[str] = field(default_factory=list)
    key_insights: List[str] = field(default_factory=list)
    peer_review_feedback: Optional[str] = None
    iterations_needed: int = 1
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Experience":
        return cls(**data)


@dataclass
class Strategy:
    """A high-level strategy abstracted from experience patterns."""
    strategy_id: str
    domain: str
    name: str
    description: str
    success_rate: float
    times_used: int = 0
    derived_from_experiences: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Strategy":
        return cls(**data)


class ReasoningBank:
    """
    Memory-driven framework for continuous agent evolution.
    
    Key capabilities:
    - Store successful hypotheses with context
    - Store failures with rejection reasons
    - Abstract strategies from patterns
    - Retrieve similar past experiences
    """
    
    def __init__(self, storage_path: str = "artifacts/reasoning_bank"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.experiences_file = self.storage_path / "experiences.json"
        self.strategies_file = self.storage_path / "strategies.json"
        
        self._experiences: Dict[str, Experience] = {}
        self._strategies: Dict[str, Strategy] = {}
        
        # ChromaDB for semantic search (optional)
        self._collection = None
        if CHROMADB_AVAILABLE:
            try:
                self._client = chromadb.Client(Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory=str(self.storage_path / "chroma"),
                    anonymized_telemetry=False
                ))
                self._collection = self._client.get_or_create_collection(
                    name="reasoning_bank",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("✅ ReasoningBank: ChromaDB initialized for semantic search")
            except Exception as e:
                logger.warning(f"ChromaDB init failed, using JSON fallback: {e}")
                self._collection = None
        else:
            logger.info("ℹ️ ReasoningBank: Using JSON storage (ChromaDB not available)")
        
        self._load()
        logger.info(f"✅ ReasoningBank initialized with {len(self._experiences)} experiences, {len(self._strategies)} strategies")
    
    def _load(self):
        """Load experiences and strategies from disk."""
        if self.experiences_file.exists():
            try:
                with open(self.experiences_file, "r") as f:
                    data = json.load(f)
                    self._experiences = {
                        k: Experience.from_dict(v) for k, v in data.items()
                    }
            except Exception as e:
                logger.warning(f"Failed to load experiences: {e}")
        
        if self.strategies_file.exists():
            try:
                with open(self.strategies_file, "r") as f:
                    data = json.load(f)
                    self._strategies = {
                        k: Strategy.from_dict(v) for k, v in data.items()
                    }
            except Exception as e:
                logger.warning(f"Failed to load strategies: {e}")
    
    def _save(self):
        """Persist experiences and strategies to disk."""
        with open(self.experiences_file, "w") as f:
            json.dump({k: v.to_dict() for k, v in self._experiences.items()}, f, indent=2)
        
        with open(self.strategies_file, "w") as f:
            json.dump({k: v.to_dict() for k, v in self._strategies.items()}, f, indent=2)
    
    def _generate_id(self, content: str) -> str:
        """Generate unique ID from content hash."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def store_success(
        self,
        hypothesis: str,
        score: float,
        domain: str,
        topic: str,
        tools_used: List[str] = None,
        key_insights: List[str] = None,
        iterations_needed: int = 1
    ) -> str:
        """
        Store a successful research experience.
        
        Returns the experience ID.
        """
        exp_id = self._generate_id(f"{domain}:{topic}:{hypothesis[:100]}")
        
        experience = Experience(
            experience_id=exp_id,
            domain=domain,
            topic=topic,
            hypothesis=hypothesis[:2000],  # Truncate for storage
            outcome="success",
            score=score,
            tools_used=tools_used or [],
            key_insights=key_insights or [],
            iterations_needed=iterations_needed
        )
        
        self._experiences[exp_id] = experience
        
        # Add to ChromaDB if available
        if self._collection is not None:
            try:
                self._collection.upsert(
                    ids=[exp_id],
                    documents=[f"{domain} {topic} {hypothesis[:500]}"],
                    metadatas=[{
                        "domain": domain,
                        "outcome": "success",
                        "score": score
                    }]
                )
            except Exception as e:
                logger.warning(f"ChromaDB upsert failed: {e}")
        
        self._save()
        logger.info(f"📗 ReasoningBank: Stored success experience {exp_id} (score: {score})")
        
        # Check if we can abstract a new strategy
        self._maybe_abstract_strategy(domain)
        
        return exp_id
    
    def store_failure(
        self,
        hypothesis: str,
        rejection_reason: str,
        domain: str,
        topic: str,
        score: float = 0.0,
        peer_review_feedback: str = None
    ) -> str:
        """
        Store a failed research experience for learning.
        
        Returns the experience ID.
        """
        exp_id = self._generate_id(f"{domain}:{topic}:fail:{hypothesis[:100]}")
        
        experience = Experience(
            experience_id=exp_id,
            domain=domain,
            topic=topic,
            hypothesis=hypothesis[:2000],
            outcome="failure",
            score=score,
            rejection_reason=rejection_reason,
            peer_review_feedback=peer_review_feedback
        )
        
        self._experiences[exp_id] = experience
        
        # Add to ChromaDB if available
        if self._collection is not None:
            try:
                self._collection.upsert(
                    ids=[exp_id],
                    documents=[f"{domain} {topic} FAILED: {rejection_reason}"],
                    metadatas=[{
                        "domain": domain,
                        "outcome": "failure",
                        "score": score
                    }]
                )
            except Exception as e:
                logger.warning(f"ChromaDB upsert failed: {e}")
        
        self._save()
        logger.info(f"📕 ReasoningBank: Stored failure experience {exp_id}")
        
        return exp_id
    
    def retrieve_similar(
        self,
        query: str,
        domain: str = None,
        k: int = 5,
        include_failures: bool = True
    ) -> List[Experience]:
        """
        Retrieve similar past experiences using semantic search.
        
        Falls back to keyword matching if ChromaDB is not available.
        """
        if self._collection is not None:
            try:
                where_filter = {}
                if domain:
                    where_filter["domain"] = domain
                if not include_failures:
                    where_filter["outcome"] = "success"
                
                results = self._collection.query(
                    query_texts=[query],
                    n_results=k,
                    where=where_filter if where_filter else None
                )
                
                experience_ids = results.get("ids", [[]])[0]
                return [
                    self._experiences[eid] 
                    for eid in experience_ids 
                    if eid in self._experiences
                ]
            except Exception as e:
                logger.warning(f"ChromaDB query failed, using fallback: {e}")
        
        # Fallback: Simple keyword matching
        query_lower = query.lower()
        scored = []
        
        for exp in self._experiences.values():
            if domain and exp.domain != domain:
                continue
            if not include_failures and exp.outcome == "failure":
                continue
            
            # Simple relevance scoring
            score = 0
            text = f"{exp.topic} {exp.hypothesis}".lower()
            for word in query_lower.split():
                if word in text:
                    score += 1
            
            if score > 0:
                scored.append((score, exp))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [exp for _, exp in scored[:k]]
    
    def get_strategies(self, domain: str = None) -> List[Strategy]:
        """Get abstracted strategies, optionally filtered by domain."""
        if domain:
            return [s for s in self._strategies.values() if s.domain == domain]
        return list(self._strategies.values())
    
    def _maybe_abstract_strategy(self, domain: str):
        """
        Check if we have enough experiences to abstract a new strategy.
        
        Strategies are abstracted when:
        - We have 3+ successful experiences in a domain
        - There's a pattern in tools used or approach
        """
        domain_successes = [
            e for e in self._experiences.values()
            if e.domain == domain and e.outcome == "success"
        ]
        
        if len(domain_successes) < 3:
            return
        
        # Analyze tool usage patterns
        tool_counts: Dict[str, int] = {}
        for exp in domain_successes:
            for tool in exp.tools_used:
                tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        # Find tools used in >50% of successes
        common_tools = [
            tool for tool, count in tool_counts.items()
            if count >= len(domain_successes) * 0.5
        ]
        
        if common_tools:
            strategy_id = self._generate_id(f"strategy:{domain}:{','.join(common_tools)}")
            
            if strategy_id not in self._strategies:
                avg_score = sum(e.score for e in domain_successes) / len(domain_successes)
                
                strategy = Strategy(
                    strategy_id=strategy_id,
                    domain=domain,
                    name=f"Effective {domain.title()} Strategy",
                    description=f"Use tools: {', '.join(common_tools)}. Based on {len(domain_successes)} successful experiments with avg score {avg_score:.1f}.",
                    success_rate=1.0,  # All derived from successes
                    times_used=len(domain_successes),
                    derived_from_experiences=[e.experience_id for e in domain_successes]
                )
                
                self._strategies[strategy_id] = strategy
                self._save()
                logger.info(f"🧠 ReasoningBank: Abstracted new strategy '{strategy.name}'")
    
    def get_context_for_hypothesis(
        self,
        topic: str,
        domain: str,
        max_examples: int = 3
    ) -> str:
        """
        Generate context from past experiences for hypothesis generation.
        
        Returns formatted text to include in LLM prompt.
        """
        # Get similar successes
        successes = self.retrieve_similar(
            topic, domain=domain, k=max_examples, include_failures=False
        )
        
        # Get domain strategies
        strategies = self.get_strategies(domain)
        
        context_parts = []
        
        if strategies:
            context_parts.append("**Proven Strategies:**")
            for s in strategies[:2]:
                context_parts.append(f"- {s.description}")
        
        if successes:
            context_parts.append("\n**Similar Successful Research:**")
            for exp in successes:
                context_parts.append(
                    f"- Topic: {exp.topic[:100]}\n"
                    f"  Score: {exp.score}/10\n"
                    f"  Tools: {', '.join(exp.tools_used[:5])}"
                )
        
        # Get recent failures to avoid
        failures = [
            e for e in self._experiences.values()
            if e.domain == domain and e.outcome == "failure"
        ][-3:]
        
        if failures:
            context_parts.append("\n**Avoid These Issues (from past failures):**")
            for exp in failures:
                if exp.rejection_reason:
                    context_parts.append(f"- {exp.rejection_reason[:150]}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the reasoning bank."""
        successes = [e for e in self._experiences.values() if e.outcome == "success"]
        failures = [e for e in self._experiences.values() if e.outcome == "failure"]
        
        domains = set(e.domain for e in self._experiences.values())
        
        return {
            "total_experiences": len(self._experiences),
            "successes": len(successes),
            "failures": len(failures),
            "success_rate": len(successes) / max(1, len(self._experiences)),
            "avg_success_score": sum(e.score for e in successes) / max(1, len(successes)),
            "total_strategies": len(self._strategies),
            "domains": list(domains),
            "chromadb_enabled": self._collection is not None
        }


# Global singleton instance
_reasoning_bank: Optional[ReasoningBank] = None


def get_reasoning_bank() -> ReasoningBank:
    """Get or create the global ReasoningBank instance."""
    global _reasoning_bank
    if _reasoning_bank is None:
        _reasoning_bank = ReasoningBank()
    return _reasoning_bank


__all__ = ["ReasoningBank", "Experience", "Strategy", "get_reasoning_bank"]
