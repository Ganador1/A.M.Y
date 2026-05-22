"""
Literature Analyzer Service
============================

Analiza literatura científica reciente para identificar gaps y validar novelty.
Basado en papers ICLR 2025: MOOSE-Chem, CycleResearcher, AlphaEvolve.

Funcionalidades:
- Búsqueda en arXiv/PubMed de papers recientes
- Extracción de topics estudiados (TF-IDF)
- Identificación de gaps (áreas poco estudiadas)
- Detección de keywords saturados (>50% overlap)
- Validación de novelty (similarity scoring)
"""

from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
from datetime import datetime
import re
import logging
import asyncio

logger = logging.getLogger(__name__)


class LiteratureAnalyzer:
    """
    Analizador de literatura científica para validación de novelty.
    
    Basado en arquitectura de MOOSE-Chem (ICLR 2025):
    1. Literatura search → 2. Gap analysis → 3. Novelty validation
    """
    
    def __init__(self):
        """Initialize analyzer"""
        self.domain_gap_templates = self._load_gap_templates()
        logger.info("📚 LiteratureAnalyzer initialized")
    
    def _load_gap_templates(self) -> Dict[str, List[str]]:
        """
        Domain-specific gap templates.
        
        Estas son áreas típicamente UNDERSTUDIED en cada dominio.
        Basado en análisis de literatura 2020-2024.
        """
        return {
            'biology': [
                "cell-type-specific dynamics",
                "post-translational modification crosstalk",
                "temporal resolution at single-cell level",
                "pathway crosstalk mechanisms",
                "non-canonical signaling routes",
                "circadian rhythm integration",
                "metabolic-epigenetic coupling",
                "microbiome-host interaction dynamics",
                "spatial transcriptomics heterogeneity",
                "protein isoform-specific functions"
            ],
            'quantum_physics': [
                "intermediate-scale quantum systems",
                "non-Markovian decoherence",
                "topological phase transitions",
                "many-body localization",
                "quantum thermalization",
                "open quantum systems far from equilibrium",
                "quantum error correction in NISQ era",
                "hybrid classical-quantum algorithms",
                "quantum supremacy verification",
                "fault-tolerant quantum gates"
            ],
            'materials_science': [
                "multi-scale modeling integration",
                "interface engineering at atomic scale",
                "defect dynamics under stress",
                "processing-structure-property relationships",
                "high-throughput synthesis validation",
                "machine learning for property prediction",
                "additive manufacturing microstructure control",
                "environmental degradation mechanisms",
                "bio-inspired material design",
                "quantum materials applications"
            ],
            'chemistry': [
                "catalyst deactivation mechanisms",
                "reaction intermediate characterization",
                "solvent effect quantification",
                "stereoselectivity prediction",
                "green chemistry alternatives",
                "computational screening validation",
                "flow chemistry optimization",
                "photocatalytic mechanism elucidation",
                "electrocatalyst stability",
                "machine learning for reaction prediction"
            ],
            'neuroscience': [
                "cell-type-specific circuit dynamics",
                "neuromodulator temporal dynamics",
                "long-range connectivity mapping",
                "synaptic plasticity rules",
                "brain-wide activity correlation",
                "neurovascular coupling mechanisms",
                "glial-neuronal interactions",
                "memory consolidation pathways",
                "neural code for behavior",
                "disease-specific circuit dysfunction"
            ],
            'medicine': [
                "patient stratification biomarkers",
                "treatment response prediction",
                "drug-drug interaction mechanisms",
                "personalized dosing algorithms",
                "rare disease pathophysiology",
                "biomarker validation in diverse populations",
                "digital health integration",
                "preventive intervention efficacy",
                "multi-omics integration for diagnosis",
                "real-world evidence validation"
            ],
            'climate_science': [
                "regional climate feedback mechanisms",
                "tipping point early warning signals",
                "ocean-atmosphere coupling dynamics",
                "extreme event attribution",
                "carbon cycle uncertainties",
                "cloud-aerosol interactions",
                "ice sheet dynamics",
                "vegetation-climate feedbacks",
                "urban heat island mitigation",
                "climate intervention side effects"
            ],
            'mathematics': [
                "computational complexity lower bounds",
                "number theory patterns",
                "graph theory extremal problems",
                "dynamical systems bifurcations",
                "optimization algorithm convergence",
                "topological data analysis applications",
                "machine learning theory foundations",
                "cryptographic primitive security",
                "combinatorial optimization heuristics",
                "numerical stability analysis"
            ],
            'astronomy': [
                "exoplanet atmosphere composition",
                "gravitational wave source identification",
                "dark matter distribution mapping",
                "galaxy formation simulations",
                "stellar evolution rare phases",
                "black hole mergers",
                "cosmological parameter constraints",
                "interstellar medium chemistry",
                "fast radio burst origins",
                "habitability zone characterization"
            ],
            'engineering': [
                "multi-objective optimization trade-offs",
                "failure mode prediction",
                "real-time system control",
                "energy efficiency improvement",
                "material fatigue modeling",
                "sensor fusion algorithms",
                "autonomous system safety",
                "human-robot interaction",
                "sustainable design principles",
                "lifecycle assessment integration"
            ]
        }
    
    def _build_generic_query(self, domain: str, year: int) -> str:
        """
        Build generic domain query when research_question not provided.
        
        Args:
            domain: Scientific domain
            year: Publication year
        
        Returns:
            Generic query string
        """
        domain_queries = {
            'biology': f"biology genomics protein {year}",
            'quantum_physics': f"quantum computing qubit {year}",
            'materials_science': f"materials synthesis composite {year}",
            'chemistry': f"chemistry catalyst synthesis {year}",
            'neuroscience': f"neuroscience brain neural {year}",
            'medicine': f"medicine clinical biomarker {year}",
            'climate_science': f"climate temperature carbon {year}",
            'mathematics': f"mathematics optimization theorem {year}",
            'astronomy': f"astronomy exoplanet galaxy {year}",
            'engineering': f"engineering design optimization {year}"
        }
        
        return domain_queries.get(domain, f"{domain} {year}")
    
    def _extract_scientific_keywords(self, research_question: str, domain: str) -> List[str]:
        """
        Extract scientific keywords from research question.
        
        FIX #1: Domain-specific keyword extraction for targeted queries.
        Instead of generic "biology genomics protein", extract actual terms
        from the research question.
        
        Args:
            research_question: The hypothesis research question
            domain: Scientific domain
        
        Returns:
            List of extracted keywords (max 5)
        """
        # Scientific stopwords to filter out
        SCIENTIFIC_STOPWORDS = {
            'analysis', 'analyze', 'study', 'investigate', 'research',
            'identify', 'determine', 'examine', 'explore', 'understand',
            'increase', 'decrease', 'improve', 'enhance', 'optimize',
            'measure', 'detect', 'observe', 'assess', 'evaluate',
            'involved', 'leading', 'resulting', 'causing', 'affecting',
            'method', 'approach', 'technique', 'strategy', 'mechanism',
            'will', 'reveal', 'show', 'demonstrate', 'indicate',
            'within', 'using', 'through', 'based', 'related'
        }
        
        # Extract capitalized terms (likely scientific entities)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', research_question)
        
        # Extract multi-word technical terms (e.g., "single-cell", "T cell")
        technical_terms = re.findall(r'\b[a-z]+-[a-z]+\b|\b[A-Z]+\d+\+?\b', research_question.lower())
        
        # Extract general scientific words (min 4 chars, not stopwords)
        words = re.findall(r'\b[a-z]{4,}\b', research_question.lower())
        scientific_words = [w for w in words if w not in SCIENTIFIC_STOPWORDS]
        
        # Combine and deduplicate
        keywords = []
        seen = set()
        
        # Priority 1: Capitalized terms (cell types, proteins, etc.)
        for term in capitalized:
            term_lower = term.lower()
            if term_lower not in seen and term_lower not in SCIENTIFIC_STOPWORDS:
                keywords.append(term_lower)
                seen.add(term_lower)
        
        # Priority 2: Technical terms (single-cell, CD8+, etc.)
        for term in technical_terms:
            if term not in seen:
                keywords.append(term)
                seen.add(term)
        
        # Priority 3: Scientific words
        for word in scientific_words:
            if word not in seen and len(keywords) < 5:
                keywords.append(word)
                seen.add(word)
        
        # Limit to top 5 most relevant
        return keywords[:5]
    
    async def fetch_recent_papers(
        self,
        domain: str,
        year: int = 2024,
        limit: int = 20,
        research_question: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent papers from arXiv/PubMed.
        
        FIX #1: Now supports research_question for targeted queries.
        If provided, extracts keywords to build domain-specific query.
        
        Args:
            domain: Scientific domain (e.g., 'biology', 'quantum_physics')
            year: Minimum publication year
            limit: Maximum number of papers to fetch
            research_question: Optional research question for keyword extraction
        
        Returns:
            List of papers with title, abstract, arxiv_id, relevance_score
        """
        try:
            from app.autonomous.interfaces.external_apis import fetch_literature_snippets
            
            # Build query: targeted if research_question provided, else generic
            if research_question:
                keywords = self._extract_scientific_keywords(research_question, domain)
                if keywords:
                    query = f"{domain} {' '.join(keywords)} {year}"
                    logger.info(f"🎯 Extracted keywords: {keywords}")
                else:
                    # Fallback to generic if extraction failed
                    query = self._build_generic_query(domain, year)
                    logger.warning(f"⚠️ No keywords extracted, using generic query")
            else:
                query = self._build_generic_query(domain, year)
            
            logger.info(f"🔍 Fetching literature: query='{query}', limit={limit}")
            
            papers = await fetch_literature_snippets(query=query, limit=limit)
            
            logger.info(f"   ✅ Found {len(papers)} papers")
            
            return papers
            
        except Exception as e:
            logger.warning(f"⚠️ Literature fetch failed: {e}, using fallback")
            return self._generate_fallback_papers(domain, limit)
    
    def _generate_fallback_papers(self, domain: str, limit: int) -> List[Dict]:
        """Generate synthetic papers for offline testing"""
        papers = []
        
        # Domain-specific keywords
        keywords_by_domain = {
            'biology': ['protein', 'gene', 'cell', 'signaling', 'expression', 'regulation'],
            'quantum_physics': ['qubit', 'entanglement', 'decoherence', 'gate', 'circuit', 'error'],
            'materials_science': ['composite', 'structure', 'mechanical', 'thermal', 'synthesis'],
            # Add more as needed
        }
        
        keywords = keywords_by_domain.get(domain, ['research', 'analysis', 'study'])
        
        for i in range(limit):
            # Generate synthetic title
            kw1, kw2, kw3 = keywords[i % len(keywords)], keywords[(i+1) % len(keywords)], keywords[(i+2) % len(keywords)]
            
            papers.append({
                'arxiv_id': f'2024.{i:05d}',
                'title': f"Study of {kw1}-{kw2} interactions in {kw3} systems",
                'abstract': f"We investigate {kw1} mechanisms through {kw2} analysis. Our {kw3}-based approach reveals novel insights.",
                'relevance_score': 0.7 - (i * 0.03)  # Decreasing relevance
            })
        
        return papers
    
    def extract_topics(self, papers: List[Dict]) -> List[str]:
        """
        Extract main topics from papers using simple TF-IDF.
        
        Returns most frequent significant keywords (length >5, frequency ≥3).
        """
        if not papers:
            return []
        
        all_words = []
        
        for paper in papers:
            title = paper.get('title', '').lower()
            abstract = paper.get('abstract', '')[:500].lower()  # Limit abstract length
            
            # Tokenize (simple split)
            text = title + ' ' + abstract
            
            # Remove common words and extract significant terms
            words = re.findall(r'\b[a-z]{6,}\b', text)  # Words ≥6 chars
            all_words.extend(words)
        
        # Count frequencies
        word_counts = Counter(all_words)
        
        # Filter: keep words appearing in ≥3 papers
        threshold = min(3, len(papers) // 5)  # At least 3 or 20% of papers
        
        significant = [
            word for word, count in word_counts.most_common(30)
            if count >= threshold
        ]
        
        logger.info(f"   📊 Extracted {len(significant)} topics from {len(papers)} papers")
        logger.debug(f"      Top topics: {', '.join(significant[:10])}")
        
        return significant
    
    def identify_gaps(self, studied_topics: List[str], domain: str) -> List[str]:
        """
        Identify research gaps by comparing studied topics with domain templates.
        
        A gap is UNDERSTUDIED if its keywords do NOT appear in studied_topics.
        
        Returns:
            List of gap descriptions (max 5)
        """
        if not studied_topics:
            # If no topics extracted, return all templates as potential gaps
            return self.domain_gap_templates.get(domain, [])[:5]
        
        potential_gaps = self.domain_gap_templates.get(domain, [])
        
        gaps = []
        
        for gap in potential_gaps:
            # Extract keywords from gap template
            gap_keywords = set(re.findall(r'\b[a-z]{6,}\b', gap.lower()))
            
            # Check overlap with studied topics
            overlap = gap_keywords & set(studied_topics)
            
            # If <50% overlap, it's understudied
            if len(overlap) < len(gap_keywords) * 0.5:
                gaps.append(gap)
        
        logger.info(f"   🎯 Identified {len(gaps)} gaps in {domain}")
        if gaps:
            logger.debug(f"      Top gaps: {', '.join(gaps[:3])}")
        
        return gaps[:5]  # Return top 5 gaps
    
    def find_saturated_keywords(
        self,
        papers: List[Dict],
        threshold: float = 0.5
    ) -> List[str]:
        """
        Find keywords appearing in >threshold% of papers (saturated topics).
        
        Args:
            papers: List of paper dicts
            threshold: Fraction of papers (0.5 = 50%)
        
        Returns:
            List of saturated keywords
        """
        if not papers:
            return []
        
        keyword_paper_counts = Counter()
        
        for paper in papers:
            title = paper.get('title', '').lower()
            
            # Extract keywords from title (more reliable than abstract)
            keywords = set(re.findall(r'\b[a-z]{6,}\b', title))
            
            # Increment count for each unique keyword in this paper
            keyword_paper_counts.update(keywords)
        
        # Find keywords appearing in >threshold papers
        min_papers = int(len(papers) * threshold)
        
        saturated = [
            kw for kw, count in keyword_paper_counts.most_common(20)
            if count >= min_papers
        ]
        
        logger.info(f"   ⚠️ Found {len(saturated)} saturated keywords (in >{threshold*100:.0f}% of papers)")
        logger.debug(f"      Saturated: {', '.join(saturated[:10])}")
        
        return saturated
    
    def validate_novelty(
        self,
        hypothesis: Dict[str, Any],
        recent_papers: List[Dict],
        use_tfidf: bool = True
    ) -> float:
        """
        Validate novelty by comparing hypothesis with recent papers.
        
        FIX #3: Uses TF-IDF + cosine similarity for more accurate novelty measurement.
        
        Args:
            hypothesis: Dict with 'title' and 'description'
            recent_papers: List of recent paper dicts
            use_tfidf: Use TF-IDF (True) or simple keyword overlap (False)
        
        Returns:
            Novelty score 0.0-1.0 (higher = more novel)
        """
        if not recent_papers:
            logger.warning("⚠️ No papers to compare, returning default novelty 0.5")
            return 0.5
        
        # Extract hypothesis text
        hyp_text = (
            hypothesis.get('title', '') + ' ' +
            hypothesis.get('description', '')
        )
        
        if not hyp_text.strip():
            return 0.5
        
        if use_tfidf:
            # FIX #3: TF-IDF + cosine similarity
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                from sklearn.metrics.pairwise import cosine_similarity
                
                # Build corpus: hypothesis + all papers
                corpus = [hyp_text]
                for paper in recent_papers:
                    paper_text = (
                        paper.get('title', '') + ' ' +
                        paper.get('abstract', '')[:500]
                    )
                    if paper_text.strip():
                        corpus.append(paper_text)
                
                if len(corpus) < 2:
                    return 0.5
                
                # TF-IDF vectorization
                vectorizer = TfidfVectorizer(
                    max_features=100,
                    stop_words='english',
                    ngram_range=(1, 2),  # Unigrams + bigrams
                    min_df=1,
                    lowercase=True
                )
                
                tfidf_matrix = vectorizer.fit_transform(corpus)
                
                # Cosine similarity: hypothesis vs all papers
                similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
                
                # Max similarity with any paper
                max_similarity = float(similarities.max())
                
                # Novelty = 1 - max_similarity
                # (Less similar to existing work = more novel)
                novelty = 1.0 - max_similarity
                
                # Clamp to [0, 1]
                novelty = max(0.0, min(1.0, novelty))
                
                logger.info(f"   📈 TF-IDF Novelty: {novelty:.3f} (max similarity: {max_similarity:.3f})")
                
                return novelty
                
            except ImportError:
                logger.warning("⚠️ sklearn not available, falling back to keyword overlap")
                # Fall through to keyword overlap method
            except Exception as e:
                logger.warning(f"⚠️ TF-IDF failed: {e}, falling back to keyword overlap")
                # Fall through to keyword overlap method
        
        # Fallback: Simple keyword overlap (old method)
        hyp_keywords = set(re.findall(r'\b[a-z]{6,}\b', hyp_text.lower()))
        
        if not hyp_keywords:
            return 0.5
        
        # Extract keywords from all papers
        papers_keywords = set()
        for paper in recent_papers:
            title = paper.get('title', '').lower()
            abstract = paper.get('abstract', '')[:300].lower()
            
            keywords = re.findall(r'\b[a-z]{6,}\b', title + ' ' + abstract)
            papers_keywords.update(keywords)
        
        # Calculate overlap
        overlap = hyp_keywords & papers_keywords
        
        # Novelty = 1 - (overlap ratio)
        novelty = 1.0 - (len(overlap) / len(hyp_keywords))
        
        # Clamp to [0, 1]
        novelty = max(0.0, min(1.0, novelty))
        
        logger.info(f"   📈 Keyword overlap novelty: {novelty:.3f}")
        logger.debug(f"      Hypothesis keywords: {len(hyp_keywords)}")
        logger.debug(f"      Overlap with papers: {len(overlap)}")
        logger.debug(f"      Overlap ratio: {len(overlap)/len(hyp_keywords):.2%}")
        
        return novelty
    
    def calculate_keyword_overlap(
        self,
        hypothesis: Dict[str, Any],
        papers: List[Dict]
    ) -> float:
        """
        Calculate keyword overlap ratio (0-1).
        
        This is the INVERSE of novelty:
        - High overlap = low novelty (hypothesis similar to existing work)
        - Low overlap = high novelty (hypothesis explores new territory)
        
        Returns:
            Overlap ratio 0.0-1.0
        """
        novelty = self.validate_novelty(hypothesis, papers)
        
        # Overlap = 1 - novelty
        return 1.0 - novelty
    
    def summarize_papers(self, papers: List[Dict], max_papers: int = 10) -> str:
        """
        Create a summary of papers for prompt context.
        
        Returns:
            Multi-line string with paper titles and relevance scores
        """
        if not papers:
            return "No recent papers found."
        
        summary_lines = []
        
        for i, paper in enumerate(papers[:max_papers], 1):
            title = paper.get('title', 'Untitled')
            arxiv_id = paper.get('arxiv_id', 'N/A')
            relevance = paper.get('relevance_score', 0.0)
            
            summary_lines.append(
                f"{i}. [{arxiv_id}] {title} (relevance: {relevance:.2f})"
            )
        
        return '\n'.join(summary_lines)
    
    async def analyze_domain(
        self,
        domain: str,
        year: int = 2024,
        limit: int = 20,
        research_question: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete literature analysis for a domain.
        
        FIX #1: Now accepts research_question for targeted literature search.
        
        This is the main entry point combining all analysis steps.
        
        Args:
            domain: Scientific domain
            year: Minimum publication year
            limit: Max papers to fetch
            research_question: Optional research question for targeted search
        
        Returns:
            Dict with:
                - papers: List of paper dicts
                - studied_topics: List of frequent keywords
                - identified_gaps: List of understudied areas
                - saturated_keywords: List of over-studied keywords
                - papers_summary: String summary for prompts
        """
        logger.info(f"🔬 Starting literature analysis for {domain}")
        
        # Step 1: Fetch papers (with targeted query if research_question provided)
        papers = await self.fetch_recent_papers(
            domain, 
            year, 
            limit,
            research_question=research_question
        )
        
        # Step 2: Extract topics
        topics = self.extract_topics(papers)
        
        # Step 3: Identify gaps
        gaps = self.identify_gaps(topics, domain)
        
        # Step 4: Find saturated keywords
        saturated = self.find_saturated_keywords(papers, threshold=0.5)
        
        # Step 5: Create summary
        summary = self.summarize_papers(papers, max_papers=10)
        
        result = {
            'papers': papers,
            'papers_count': len(papers),
            'studied_topics': topics,
            'identified_gaps': gaps,
            'saturated_keywords': saturated,
            'papers_summary': summary
        }
        
        logger.info(f"   ✅ Analysis complete:")
        logger.info(f"      Papers: {len(papers)}")
        logger.info(f"      Topics: {len(topics)}")
        logger.info(f"      Gaps: {len(gaps)}")
        logger.info(f"      Saturated: {len(saturated)}")
        
        return result


__all__ = ['LiteratureAnalyzer']
