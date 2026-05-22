"""
Hypothesis Generator for Autonomous Research Loops
==================================================

Wrapper around ScientificHypothesisAgent for autonomous loop integration.
Provides simplified interface for generating hypotheses in production loops.
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from app.services.scientific_hypothesis_agent import ScientificHypothesisAgent
from app.core.bootstrap_logging import logger


def validate_biological_plausibility(hypothesis: Dict[str, Any]) -> Tuple[bool, str]:
    """
    FIX #2: Validate biological plausibility of hypothesis.
    
    Detects impossible combinations like:
    - PTMs + transcriptomics (PTMs require proteomics)
    - Protein structure + genomics (requires structural biology methods)
    - Metabolomics + RNA-seq (requires mass spectrometry)
    
    Args:
        hypothesis: Hypothesis dict with title + description
    
    Returns:
        Tuple of (is_plausible, reason_if_not)
    """
    title = hypothesis.get('title', '').lower()
    description = hypothesis.get('description', '').lower()
    full_text = f"{title} {description}"
    
    # Rule 1: PTMs require proteomics, not transcriptomics
    has_ptm = any(term in full_text for term in [
        'ptm', 'post-translational', 'phosphorylation', 
        'ubiquitination', 'acetylation', 'methylation'
    ])
    has_transcriptomics = any(term in full_text for term in [
        'transcriptom', 'rna-seq', 'rna seq', 'mrna', 'gene expression'
    ])
    
    if has_ptm and has_transcriptomics:
        return False, (
            "Biological implausibility: PTMs (post-translational modifications) "
            "occur at protein level and cannot be directly measured with "
            "transcriptomics (RNA-seq). Requires proteomics (mass spectrometry)."
        )
    
    # Rule 2: Protein structure requires structural methods, not genomics alone
    has_structure = any(term in full_text for term in [
        'protein structure', 'folding', '3d structure', 'structural'
    ])
    has_genomics_only = 'genomic' in full_text and not any(term in full_text for term in [
        'proteom', 'x-ray', 'cryo-em', 'nmr', 'alphafold'
    ])
    
    if has_structure and has_genomics_only:
        return False, (
            "Biological implausibility: Protein structure prediction/determination "
            "requires structural biology methods (X-ray, cryo-EM, NMR) or "
            "computational prediction (AlphaFold), not genomics alone."
        )
    
    # Rule 3: Metabolomics requires mass spectrometry, not RNA-seq
    has_metabolomics = any(term in full_text for term in [
        'metabolom', 'metabolite', 'small molecule'
    ])
    
    if has_metabolomics and has_transcriptomics:
        return False, (
            "Biological implausibility: Metabolomics (small molecule profiling) "
            "requires mass spectrometry, not transcriptomics. RNA levels don't "
            "directly correlate with metabolite abundance."
        )
    
    # All checks passed
    return True, "Hypothesis is biologically plausible"


class HypothesisGenerator:
    """
    Hypothesis Generator for autonomous research loops.
    
    Wraps ScientificHypothesisAgent to provide simplified interface
    for production loop hypothesis generation.
    """
    
    def __init__(self):
        """Initialize with ScientificHypothesisAgent"""
        self.agent = ScientificHypothesisAgent()
        logger.info("🧠 HypothesisGenerator initialized")
    
    async def generate_hypothesis(
        self,
        domain: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a scientific hypothesis for the given domain.
        
        Args:
            domain: Scientific domain (e.g., 'quantum_physics', 'biology', 'materials_science')
            context: Optional context including mode, thresholds, etc.
                - enable_literature_search: bool (default True) - Enable pre-hypothesis literatura search
                - literature_year: int (default 2024) - Minimum publication year for literatura
                - literature_limit: int (default 20) - Max papers to fetch
                - peer_review_feedback: Dict (optional) - Previous peer review feedback to incorporate
                    - issues: List of validation issues from rejected hypothesis
                    - recommendations: List of improvement suggestions
                    - scores: Dict with scientific_validity, methodological_rigor, novelty_contribution
                - failed_hypotheses: List[Dict] (optional) - Previously rejected hypotheses to avoid
                - iteration: int (optional) - Current iteration number for refinement
            
        Returns:
            Dict containing:
                - title: Hypothesis title
                - description: Detailed description
                - novelty_score: Estimated novelty (0-1)
                - confidence_score: Confidence in hypothesis (0-1)
                - variables: Relevant variables
                - assumptions: Key assumptions
                - expected_outcome: Expected result
                - literature_context: (if enabled) Dict with papers, gaps, saturated keywords
                - validated_novelty: (if enabled) Novelty score validated against literature
                - addresses_feedback: (if peer_review_feedback provided) How this hypothesis addresses previous issues
        """
        try:
            # Extract context parameters
            context = context or {}
            # mode = context.get('mode', 'production')  # Reserved for future use
            novelty_threshold = context.get('novelty_threshold', 0.7)
            enable_literature_search = context.get('enable_literature_search', True)
            literature_year = context.get('literature_year', 2024)
            literature_limit = context.get('literature_limit', 20)
            
            # === PEER REVIEW FEEDBACK INTEGRATION ===
            peer_review_feedback = context.get('peer_review_feedback')
            failed_hypotheses = context.get('failed_hypotheses', [])
            iteration = context.get('iteration', 1)
            
            if peer_review_feedback:
                logger.info(f"📝 Incorporating peer review feedback from iteration {iteration - 1}")
                logger.info(f"   Issues to address: {len(peer_review_feedback.get('issues', []))}")
                logger.info(f"   Recommendations: {len(peer_review_feedback.get('recommendations', []))}")
            
            if failed_hypotheses:
                logger.info(f"⚠️ Avoiding {len(failed_hypotheses)} previously failed hypotheses")
            
            # ========================================
            # STEP 1: PRE-HYPOTHESIS LITERATURA SEARCH
            # ========================================
            literature_context = context.get('literature_context')
            literature_papers = []
            
            if enable_literature_search and literature_context is None:
                logger.info("📚 Executing pre-hypothesis literatura search...")
                
                try:
                    from app.services.literature_analyzer import LiteratureAnalyzer
                    
                    analyzer = LiteratureAnalyzer()
                    
                    # FIX #1: Extract research_question from context for targeted queries
                    research_question = context.get('research_question')
                    
                    lit_analysis = await analyzer.analyze_domain(
                        domain,
                        year=literature_year,
                        limit=literature_limit,
                        research_question=research_question  # ← TARGETED QUERY
                    )
                    
                    # Build literatura context for prompt
                    literature_context = {
                        'papers_summary': lit_analysis['papers_summary'],
                        'studied_topics': lit_analysis['studied_topics'][:15],
                        'identified_gaps': lit_analysis['identified_gaps'][:5],
                        'saturated_keywords': lit_analysis['saturated_keywords'][:10]
                    }
                    
                    literature_papers = lit_analysis['papers']
                    
                    logger.info(f"   ✅ Literatura analysis complete:")
                    logger.info(f"      Papers: {len(literature_papers)}")
                    logger.info(f"      Gaps: {len(literature_context['identified_gaps'])}")
                    logger.info(f"      Saturated: {len(literature_context['saturated_keywords'])}")
                    
                except Exception as lit_error:
                    logger.warning(f"⚠️ Literatura search failed: {lit_error}, continuing without")
                    literature_context = None
            
            # Build research question based on domain
            research_questions = {
                'quantum_physics': "What novel quantum phenomena can be explored using computational methods?",
                'biology': "What biological mechanisms can be discovered through autonomous data analysis?",
                'chemistry': "What chemical reactions or compounds show promising properties?",
                'mathematics': "What mathematical patterns or conjectures warrant investigation?",
                'neuroscience': "What neural mechanisms underlie cognitive functions?",
                'materials_science': "What material compositions yield superior properties?",
                'climate_science': "What climate patterns or feedback mechanisms need investigation?",
                'engineering': "What engineering solutions optimize performance and efficiency?",
                'medicine': "What medical interventions or biomarkers improve patient outcomes?",
                'astronomy': "What astronomical phenomena require further observation and modeling?",
                'general': "What scientific phenomena warrant systematic investigation?"
            }
            
            research_question = research_questions.get(domain, research_questions['general'])
            
            # ========================================
            # STEP 2: GENERATE HYPOTHESIS WITH LITERATURA CONTEXT
            # ========================================
            logger.info(f"🔬 Generating hypothesis for domain: {domain}")
            
            # Build request with literatura context and peer review feedback
            context_with_literature = context.copy()
            if literature_context:
                context_with_literature['literature_context'] = literature_context
            
            # Add peer review feedback to context for iterative improvement
            if peer_review_feedback:
                context_with_literature['peer_review_feedback'] = {
                    'issues': peer_review_feedback.get('issues', [])[:5],  # Limit to top 5
                    'recommendations': peer_review_feedback.get('recommendations', [])[:5],
                    'scores': peer_review_feedback.get('scores', {}),
                    'rejected_reason': peer_review_feedback.get('rejected_reason', '')
                }
            
            # Add failed hypotheses to avoid repetition
            if failed_hypotheses:
                context_with_literature['failed_hypotheses'] = [
                    {
                        'title': h.get('title', ''),
                        'rejection_reason': h.get('rejection_reason', 'Not specified')
                    }
                    for h in failed_hypotheses[-3:]  # Only last 3 to avoid prompt bloat
                ]
            
            # Add iteration number for adaptive prompting
            context_with_literature['iteration'] = iteration
            
            request_data = {
                'action': 'generate_hypothesis',
                'domain': domain,
                'research_question': research_question,
                'context_data': context_with_literature
            }
            
            result = await self.agent.process_request(request_data)
            
            if not result.get('success'):
                logger.warning(f"⚠️ Hypothesis generation failed: {result.get('error')}")
                # Return fallback hypothesis
                return self._generate_fallback_hypothesis(domain, novelty_threshold)
            
            # Extract hypothesis data
            hypothesis = result.get('hypothesis', {})
            
            # Format response
            formatted_hypothesis = {
                'title': hypothesis.get('title', f'Autonomous exploration in {domain}'),
                'description': hypothesis.get('description', ''),
                'novelty_score': hypothesis.get('novelty_score', novelty_threshold),
                'confidence_score': hypothesis.get('confidence_score', 0.5),
                'variables': hypothesis.get('variables', []),
                'assumptions': hypothesis.get('assumptions', []),
                'expected_outcome': hypothesis.get('expected_outcome', 'Novel insights'),
                'domain': domain,
                'hypothesis_id': result.get('hypothesis_id', 'unknown')
            }
            
            # ========================================
            # FIX #2: BIOLOGICAL PLAUSIBILITY VALIDATION
            # ========================================
            if domain == 'biology':
                is_plausible, reason = validate_biological_plausibility(formatted_hypothesis)
                
                if not is_plausible:
                    logger.warning(f"⚠️ IMPLAUSIBLE HYPOTHESIS DETECTED")
                    logger.warning(f"   Reason: {reason}")
                    logger.warning(f"   Title: {formatted_hypothesis['title'][:80]}...")
                    
                    # Mark as implausible - peer review will catch this
                    formatted_hypothesis['plausibility_check'] = {
                        'is_plausible': False,
                        'reason': reason,
                        'checked_at': datetime.now().isoformat()
                    }
                    
                    # Lower confidence score for implausible hypotheses
                    formatted_hypothesis['confidence_score'] = max(
                        0.1, 
                        formatted_hypothesis['confidence_score'] * 0.3
                    )
                else:
                    logger.info(f"✅ Plausibility check passed: {reason}")
                    formatted_hypothesis['plausibility_check'] = {
                        'is_plausible': True,
                        'reason': reason,
                        'checked_at': datetime.now().isoformat()
                    }
            
            # ========================================
            # STEP 3: POST-GENERATION NOVELTY VALIDATION
            # ========================================
            if enable_literature_search and literature_papers:
                logger.info("📈 Validating novelty against literatura...")
                
                try:
                    from app.services.literature_analyzer import LiteratureAnalyzer
                    
                    analyzer = LiteratureAnalyzer()
                    validated_novelty = analyzer.validate_novelty(
                        formatted_hypothesis,
                        literature_papers
                    )
                    
                    formatted_hypothesis['validated_novelty'] = validated_novelty
                    formatted_hypothesis['literature_context'] = literature_context
                    formatted_hypothesis['literature_papers_count'] = len(literature_papers)
                    
                    logger.info(f"   ✅ Novelty validated: {validated_novelty:.3f}")
                    logger.info(f"   📊 Self-reported: {formatted_hypothesis['novelty_score']:.3f}")
                    logger.info(f"   📈 Delta: {validated_novelty - formatted_hypothesis['novelty_score']:+.3f}")
                    
                except Exception as val_error:
                    logger.warning(f"⚠️ Novelty validation failed: {val_error}")
            
            logger.info(f"✅ Hypothesis generated: {formatted_hypothesis['title'][:60]}...")
            logger.info(f"   Novelty: {formatted_hypothesis.get('validated_novelty', formatted_hypothesis['novelty_score']):.3f}")
            
            return formatted_hypothesis
            
        except Exception as e:
            logger.error(f"❌ Error in generate_hypothesis: {e}")
            return self._generate_fallback_hypothesis(domain, 0.5)
    
    def _generate_fallback_hypothesis(self, domain: str, novelty_score: float = 0.5) -> Dict[str, Any]:
        """
        Generate a fallback hypothesis when agent fails.
        
        Args:
            domain: Scientific domain
            novelty_score: Target novelty score
            
        Returns:
            Basic hypothesis structure
        """
        fallback_templates = {
            'quantum_physics': {
                'title': 'Exploration of quantum entanglement in mesoscale systems',
                'description': 'Investigate quantum coherence and entanglement dynamics in intermediate-scale quantum systems',
                'variables': ['system_size', 'decoherence_rate', 'entanglement_measure'],
                'expected_outcome': 'Novel entanglement scaling behavior'
            },
            'biology': {
                'title': 'Analysis of gene regulatory network dynamics',
                'description': 'Characterize temporal dynamics of gene expression regulatory networks',
                'variables': ['gene_expression', 'regulatory_factors', 'network_topology'],
                'expected_outcome': 'Identification of key regulatory motifs'
            },
            'chemistry': {
                'title': 'Discovery of novel catalytic materials',
                'description': 'Systematic exploration of material compositions for catalytic applications',
                'variables': ['composition', 'structure', 'catalytic_activity'],
                'expected_outcome': 'High-performance catalyst candidates'
            },
            'materials_science': {
                'title': 'Optimization of material properties through composition tuning',
                'description': 'Investigate relationship between composition and functional properties',
                'variables': ['composition', 'processing_conditions', 'material_properties'],
                'expected_outcome': 'Superior property combinations'
            },
            'mathematics': {
                'title': 'Investigation of number-theoretic patterns',
                'description': 'Explore patterns and structure in mathematical sequences',
                'variables': ['sequence_type', 'pattern_metrics', 'distribution'],
                'expected_outcome': 'Novel mathematical relationships'
            }
        }
        
        template = fallback_templates.get(
            domain,
            {
                'title': f'Autonomous exploration in {domain}',
                'description': f'Systematic investigation of phenomena in {domain}',
                'variables': ['independent_var', 'dependent_var'],
                'expected_outcome': 'Novel scientific insights'
            }
        )
        
        return {
            'title': template['title'],
            'description': template['description'],
            'novelty_score': novelty_score,
            'confidence_score': 0.5,
            'variables': template['variables'],
            'assumptions': ['Standard domain assumptions'],
            'expected_outcome': template['expected_outcome'],
            'domain': domain,
            'hypothesis_id': 'fallback'
        }
    
    async def generate(self, research_question: str) -> Dict[str, Any]:
        """
        Alternative interface matching test mock signature.
        
        Args:
            research_question: Research question to address
            
        Returns:
            Hypothesis dict matching test format
        """
        # Extract domain from research question (simple heuristic)
        domain = 'general'
        
        domain_keywords = {
            'quantum': 'quantum_physics',
            'biology': 'biology',
            'gene': 'biology',
            'protein': 'biology',
            'chemistry': 'chemistry',
            'molecule': 'chemistry',
            'material': 'materials_science',
            'mathematics': 'mathematics',
            'neural': 'neuroscience',
            'climate': 'climate_science',
            'engineering': 'engineering',
            'medicine': 'medicine',
            'medical': 'medicine',
            'astronomy': 'astronomy',
            'stellar': 'astronomy'
        }
        
        question_lower = research_question.lower()
        for keyword, detected_domain in domain_keywords.items():
            if keyword in question_lower:
                domain = detected_domain
                break
        
        # Generate hypothesis using main method
        hypothesis = await self.generate_hypothesis(domain, {
            'research_question': research_question
        })
        
        # Format to match test interface
        return {
            'id': hypothesis.get('hypothesis_id', 'unknown'),
            'research_question': research_question,
            'hypothesis': hypothesis.get('description', ''),
            'null_hypothesis': f"No significant relationship in {research_question.lower()}",
            'variables': {
                'independent': hypothesis.get('variables', [])[:2],
                'dependent': hypothesis.get('variables', [])[2:4] if len(hypothesis.get('variables', [])) > 2 else ['outcome'],
                'controlled': ['standard_conditions']
            },
            'predictions': [hypothesis.get('expected_outcome', 'Measurable effect')],
            'methodology': 'computational',
            'confidence': hypothesis.get('confidence_score', 0.5),
            'status': 'generated',
            'timestamp': str(datetime.now())
        }


__all__ = ['HypothesisGenerator']
