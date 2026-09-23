"""
Improved Agent Prompt Templates with Quantitative Requirements

Este módulo contiene prompts mejorados con requisitos estrictos de calidad
para cada tipo de agente en el sistema multi-agente de AXIOM Atlas.

Basado en el análisis de calidad que mostró promedio de 5.6/10:
- Bio Hypothesis: Falta especificidad y cuantificación (3/10 en algunos casos)
- PhysChem Coder: No genera código real (5.5/10)
- Reviewer: Demasiado benevolente (6.5/10)
- Orchestrator: Muy genérico, sin timeline (6.0/10)

Mejoras implementadas:
1. Requisitos cuantitativos explícitos
2. Formato JSON estructurado
3. Ejemplos de salidas de alta calidad
4. Validaciones post-procesamiento
5. Temperaturas optimizadas por agente
"""

import logging
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)


# ============================================================================
# LITERATURA CONTEXT FORMATTING
# ============================================================================

def format_literature_context(literature_context: Optional[Dict[str, Any]] = None) -> str:
    """
    Formatea el contexto de literatura para incluir en prompts de LLM.
    
    Args:
        literature_context: Dict con:
            - papers: List[Dict] - Papers recientes de ArXiv
            - studied_topics: List[str] - Temas bien estudiados
            - identified_gaps: List[str] - Gaps de investigación
            - saturated_keywords: List[str] - Keywords saturados (>50% papers)
    
    Returns:
        str: Sección formateada para insertar en prompt, o string vacío si no hay context
    """
    if not literature_context:
        return ""
    
    papers = literature_context.get('papers', [])
    topics = literature_context.get('studied_topics', [])
    gaps = literature_context.get('identified_gaps', [])
    saturated = literature_context.get('saturated_keywords', [])
    
    if not papers and not gaps:
        return ""  # No hay datos útiles
    
    section = "\n## 📚 RECENT LITERATURE ANALYSIS\n\n"
    
    # Papers reviewed
    if papers:
        section += f"**Papers reviewed:** {len(papers)} recent publications from ArXiv\n\n"
    
    # Well-studied topics (avoid these unless combining with novelty)
    if topics:
        section += "**Well-studied topics** (use only if combining with novel aspects):\n"
        section += ", ".join(topics[:10])  # Limit to 10
        section += "\n\n"
    
    # Saturated keywords (AVOID these)
    if saturated:
        section += "**⚠️ SATURATED KEYWORDS - AVOID THESE:**\n"
        for kw in saturated[:8]:  # Top 8 most saturated
            section += f"- `{kw}` (appears in >50% of recent papers)\n"
        section += "\n"
    
    # Research gaps (TARGET these!)
    if gaps:
        section += "**🎯 IDENTIFIED RESEARCH GAPS - TARGET THESE:**\n\n"
        for i, gap in enumerate(gaps[:5], 1):  # Top 5 gaps
            section += f"{i}. **{gap}**\n"
        section += "\n"
        
        # Strategy guidance
        section += "**NOVELTY STRATEGY:**\n"
        section += "- Combine established mechanisms with gap areas above\n"
        section += "- Example: 'Cell-type-specific [known pathway] dynamics' targets gap #1\n"
        section += "- Example: 'Temporal resolution of [known process] at single-cell level' targets gap #3\n"
        section += "- Focus on HOW/WHEN/WHERE rather than just WHAT\n\n"
    
    return section


# ============================================================================
# CONFIGURACIÓN DE PARÁMETROS POR AGENTE
# ============================================================================

AGENT_PARAMETERS = {
    "orchestrator": {
        "temperature": 0.3,  # Baja temperatura para planificación estructurada
        "max_new_tokens": 1200,  # Aumentado de 800 para planes detallados completos
        "top_p": 0.9
    },
    "bio_hypothesis": {
        "temperature": 0.8,  # Alta para creatividad en hipótesis
        "max_new_tokens": 1000,  # Aumentado de 700 para JSON completo sin truncar
        "top_p": 0.95
    },
    "physchem_coder": {
        "temperature": 0.2,  # Muy baja para código preciso
        "max_new_tokens": 1800,  # Aumentado de 1000 para código ejecutable completo
        "top_p": 0.85
    },
    "reviewer": {
        "temperature": 0.4,  # Media-baja para crítica consistente
        "max_new_tokens": 1000,  # Aumentado de 800 para análisis crítico detallado
        "top_p": 0.9
    },
    "publisher": {
        "temperature": 0.5,  # Media para escritura balanceada
        "max_new_tokens": 1200,  # Aumentado de 1000 para informes completos
        "top_p": 0.92
    },
    "scientific_reasoner": {
        "temperature": 0.3,  # Baja para razonamiento preciso
        "max_new_tokens": 900,  # Aumentado de 700 para razonamiento completo
        "top_p": 0.9
    }
}


# ============================================================================
# DOMAIN-SPECIFIC TERMINOLOGY
# ============================================================================

DOMAIN_KEYWORDS = {
    "neuroscience": [
        "neuronal", "neural", "brain", "neuron", "neurons",
        "synapse", "synaptic", "hippocampus", "hippocampal",
        "plasticity", "long-term potentiation", "LTP", "LTD",
        "dendrite", "axon", "NMDA", "AMPA", "glutamate",
        "GABA", "dopamine", "serotonin", "acetylcholine",
        "action potential", "membrane potential", "ion channel",
        "neurotransmitter", "receptor", "postsynaptic", "presynaptic",
        "cognition", "memory", "learning", "consolidation",
        "prefrontal cortex", "amygdala", "striatum", "cerebellum",
        "neural network", "neural circuit", "connectivity"
    ],
    "biology": [
        "gene", "protein", "DNA", "RNA", "genome", "genomic",
        "CRISPR", "mutation", "allele", "chromosome",
        "transcription", "translation", "expression",
        "cellular", "cell", "mitochondria", "nucleus",
        "metabolism", "metabolic", "pathway", "enzyme",
        "microbiome", "bacteria", "species", "strain"
    ],
    "chemistry": [
        "molecule", "molecular", "compound", "synthesis",
        "reaction", "catalyst", "bond", "structure",
        "spectroscopy", "chromatography", "mass spectrometry",
        "pH", "concentration", "molarity", "solvent"
    ],
    "physics": [
        "quantum", "particle", "energy", "force",
        "field", "wave", "frequency", "amplitude",
        "momentum", "spin", "entanglement", "coherence"
    ],
    "quantum_computing": [
        "qubit", "logical qubit", "surface code", "stabilizer code",
        "syndrome extraction", "topological order", "error correction",
        "depolarizing noise", "fault-tolerant", "threshold", "logical error rate",
        "code distance", "stabilizer measurement", "Z error", "X error", "Y error",
        "lattice surgery", "minimum weight perfect matching", "VQE", "QAOA",
        "quantum circuit", "superconducting qubits", "coherence time", "T1", "T2"
    ],
    "mathematics": [
        "prime gap", "Chebyshev function", "Riemann zeta function",
        "Hardy-Littlewood conjecture", "Montgomery-Odlyzko law",
        "random matrix theory", "GUE statistics", "explicit formula",
        "zero density estimate", "logarithmic integral", "sieve method",
        "Dirichlet character", "L-function", "spectral analysis",
        "Gaussian fluctuations", "large deviations", "variance bound",
        "elliptic curve", "modular form", "Langlands program"
    ]
}

# ============================================================================
# PROMPT TEMPLATE: MATH HYPOTHESIS
# ============================================================================

MATH_HYPOTHESIS_PROMPT_TEMPLATE = """You are an expert mathematician and researcher for AXIOM ATLAS.

CRITICAL REQUIREMENTS - Your hypothesis MUST include:
1. **FORMAL STATEMENT**: Use LaTeX formatting for mathematical expressions.
2. **CONJECTURE CLASS**: Specify if it is an existential, universal, or probabilistic conjecture.
3. **RELATIONSHIP TO KNOWN RESULTS**: cite relevant theorems (e.g., "Generalizes the Hardy-Littlewood k-tuple conjecture").
4. **NOVELTY**: Clearly state what is new (e.g., "Provides a tighter error term O(x^(1/2+epsilon))").
5. **VERIFICATION STRATEGY**: Propose a computational method to verify it (e.g., "Check consistency for n < 10^12").
6. **DOMAIN TERMINOLOGY**: Use precise mathematical constants and functions.

FORMAT - Return ONLY valid JSON:
{{
    "title": "Short descriptive title",
    "statement": "Formal mathematical statement in LaTeX",
    "domain": "Number Theory (or other)",
    "novelty": "Description of why this is new",
    "verification_strategy": "Description of computational check",
    "confidence_score": 0.0-1.0
}}
"""

# ============================================================================
# PROMPT TEMPLATE: BIO HYPOTHESIS (Mejorado)
# ============================================================================

BIO_HYPOTHESIS_PROMPT_TEMPLATE = """You are an expert biological hypothesis generator for AXIOM ATLAS research platform.

CRITICAL REQUIREMENTS - Your hypothesis MUST include:
1. **QUANTITATIVE PREDICTIONS**: Specific numbers (e.g., "50±10% increase", "≥2-fold change")
2. **SPECIFIC ENTITIES**: Exact species, genes, proteins, metabolites (not "bacteria" but "Faecalibacterium prausnitzii")
3. **MECHANISTIC DETAIL**: Step-by-step molecular pathway with concentrations/timescales
4. **NOVELTY**: What's new compared to published literature
5. **STATISTICAL DESIGN**: Sample size, power (≥80%), alpha (0.05), effect size
6. **DOMAIN TERMINOLOGY**: Use technical terms specific to the domain (see required keywords below)

FORMAT - Return ONLY valid JSON (no markdown, no extra text):
{{
  "hypothesis": "Single sentence prediction with NUMBERS and SPECIFIC entities",
  "novelty": "Why this is novel vs existing literature (cite if possible)",
  "mechanism": {{
    "step_1": "Detailed molecular event with concentrations",
    "step_2": "Next event with timescales",
    "step_3": "Final outcome with quantification"
  }},
  "quantitative_predictions": [
    {{
      "outcome": "What will be measured",
      "expected_change": "50±10%",
      "metric": "Units and measurement method",
      "timeframe": "When this occurs",
      "baseline": "Current/control value"
    }}
  ],
  "statistical_design": {{
    "n_per_group": 15,
    "power": 0.8,
    "alpha": 0.05,
    "effect_size": "Cohen's d=0.8 or similar",
    "primary_endpoint": "What you're measuring",
    "correction": "Multiple testing correction method"
  }},
  "experiments": [
    {{
      "method": "Specific technique (e.g., RNA-seq, Western blot)",
      "n_samples": 15,
      "controls": ["Negative control", "Positive control"],
      "measurements": ["Measurement 1", "Measurement 2"],
      "duration": "Experiment timeline"
    }}
  ],
  "validation": {{
    "independent_cohort": "Yes/No and details",
    "reproducibility_check": "How to verify",
    "off_target_analysis": "For CRISPR or similar"
  }}
}}

EXAMPLE - High quality hypothesis:
{{
  "hypothesis": "Increasing Faecalibacterium prausnitzii abundance by ≥3-fold in the gut microbiome will reduce plasma Aβ42 levels by 40±12% and slow cognitive decline by 50% in early-stage Alzheimer's patients within 6 months, via enhanced short-chain fatty acid (SCFA) production (≥200% increase in butyrate).",
  "novelty": "First to quantify F. prausnitzii-specific effects on Aβ clearance with mechanistic SCFA measurements. Previous studies (Zhang 2023) showed correlation but not causation or quantification.",
  "mechanism": {{
    "step_1": "Probiotic increases F. prausnitzii from baseline 2% to 6% relative abundance (qPCR) at week 4",
    "step_2": "Butyrate production increases from 12mM to 36mM (GC-MS) by week 8, strengthening blood-brain barrier tight junctions (claudin-5 ↑60%)",
    "step_3": "Enhanced BBB integrity increases Aβ clearance by 40% (measured by CSF Aβ42/Aβ40 ratio), measurable at month 3"
  }},
  "quantitative_predictions": [
    {{"outcome": "Plasma Aβ42 reduction", "expected_change": "40±12%", "metric": "pg/mL via ELISA", "timeframe": "6 months", "baseline": "25.3±4.2 pg/mL"}},
    {{"outcome": "MMSE score improvement", "expected_change": "3.5±1.2 points", "metric": "Mini-Mental State Exam", "timeframe": "6 months", "baseline": "22.1±2.8"}},
    {{"outcome": "F. prausnitzii abundance", "expected_change": "200±50%", "metric": "16S rRNA qPCR", "timeframe": "4 weeks", "baseline": "2.1±0.7%"}}
  ],
  "statistical_design": {{
    "n_per_group": 30,
    "power": 0.85,
    "alpha": 0.05,
    "effect_size": "Cohen's d=0.9 for primary endpoint",
    "primary_endpoint": "Plasma Aβ42 at 6 months",
    "correction": "Bonferroni for 3 primary endpoints"
  }},
  "experiments": [
    {{"method": "16S rRNA sequencing + qPCR", "n_samples": 30, "controls": ["Placebo probiotic", "No intervention"], "measurements": ["Microbiome composition", "F. prausnitzii abundance"], "duration": "6 months"}},
    {{"method": "SCFA quantification (GC-MS)", "n_samples": 30, "controls": ["Baseline", "Placebo"], "measurements": ["Butyrate", "Acetate", "Propionate"], "duration": "Monthly for 6 months"}},
    {{"method": "Plasma biomarkers (ELISA)", "n_samples": 30, "controls": ["Baseline", "Age-matched healthy"], "measurements": ["Aβ42", "Aβ40", "tau", "p-tau"], "duration": "Baseline, 3mo, 6mo"}}
  ],
  "validation": {{
    "independent_cohort": "Yes - replicate in n=50 patients from different geographic region",
    "reproducibility_check": "Mouse model (APP/PS1) with same probiotic dose",
    "off_target_analysis": "Monitor 100 other gut species to rule out confounders"
  }}
}}

BAD EXAMPLE - What NOT to do:
{{
  "hypothesis": "The gut microbiome influences Alzheimer's disease through inflammation."
}}
PROBLEMS: No quantification, no specific entities, no mechanism, not testable, already known!

{literature_context_section}

USER REQUEST: {user_prompt}

GENERATE HYPOTHESIS (JSON only, no markdown):"""


# ============================================================================
# PROMPT TEMPLATE: PHYSCHEM CODER (Mejorado - Simplified)
# ============================================================================

PHYSCHEM_CODER_PROMPT_SIMPLE = """You are an expert computational scientist. Write COMPLETE, EXECUTABLE Python code.

USER REQUEST: {user_prompt}

Write Python code that:
1. Includes ALL imports at the top
2. Defines functions with docstrings
3. Includes statistical analysis (t-tests, effect sizes, p-values)
4. Creates publication-quality plots with matplotlib
5. Has a main() function that runs the analysis
6. Includes error handling and validation

Return ONLY Python code (no JSON, no markdown, just executable .py file content):

```python
# [Your complete code here]
```
"""

PHYSCHEM_CODER_PROMPT_TEMPLATE = """You are an expert computational scientist writing EXECUTABLE CODE for AXIOM ATLAS experiments.

CRITICAL REQUIREMENTS - You MUST provide:
1. **COMPLETE WORKING CODE**: Not descriptions, not pseudocode - ACTUAL Python code
2. **STATISTICAL ANALYSIS**: Power analysis, effect size calculations, multiple testing corrections
3. **VISUALIZATION**: Publication-quality plots with error bars, p-values, confidence intervals
4. **VALIDATION**: Unit tests, edge case handling, reproducibility checks
5. **COMPUTATIONAL DETAILS**: Exact parameters, algorithms, convergence criteria

FORMAT - Return ONLY valid JSON:
{{
  "experiment_design": {{
    "objective": "What you're computing",
    "method": "Specific algorithm/technique",
    "parameters": {{"param1": "value with units", "param2": "value"}},
    "expected_runtime": "Estimated time",
    "computational_resources": "CPU/GPU/memory requirements"
  }},
  "code": {{
    "imports": "import numpy as np\\nimport pandas as pd\\n...",
    "main_analysis": "def analyze_data(params):\\n    # Complete implementation\\n    pass",
    "statistical_tests": "def run_statistics(data):\\n    # t-tests, ANOVA, corrections\\n    pass",
    "visualization": "def plot_results(data):\\n    # Publication-quality plots\\n    pass",
    "validation": "def validate_results(data):\\n    # Unit tests and checks\\n    pass"
  }},
  "dependencies": ["numpy>=1.24", "scipy>=1.10", "statsmodels>=0.14"],
  "statistical_methods": {{
    "primary_test": "Two-sample t-test (two-tailed)",
    "alpha": 0.05,
    "power": 0.8,
    "effect_size": "Cohen's d=0.8",
    "correction": "Bonferroni for k=3 comparisons",
    "sample_size_justification": "Power analysis: n=15 per group for 80% power"
  }},
  "expected_outputs": [
    "Output 1: Mean±SEM with 95% CI",
    "Output 2: P-values for all comparisons",
    "Output 3: Effect sizes with confidence intervals"
  ],
  "validation_tests": [
    "Test 1: Verify input data shape",
    "Test 2: Check for NaN/inf values",
    "Test 3: Confirm statistical assumptions (normality, homoscedasticity)"
  ]
}}

EXAMPLE - High quality code design:
{{
  "experiment_design": {{
    "objective": "Quantify CRISPR-Cas9 on-target editing efficiency and off-target effects in HEK293T cells targeting BRCA1 exon 5",
    "method": "Deep amplicon sequencing (10,000x coverage) + TIDE analysis + computational off-target prediction (Cas-OFFinder)",
    "parameters": {{
      "guide_rna": "5'-GGCTATCACCTCACCAGTAG-3' (20nt)",
      "pam_sequence": "NGG",
      "cells": "HEK293T (ATCC CRL-3216)",
      "transfection": "Lipofectamine 3000, 2.5μg plasmid/well",
      "analysis_timepoint": "72h post-transfection",
      "sequencing_depth": "10,000x minimum per sample"
    }},
    "expected_runtime": "~45min for sequencing analysis (12 samples)",
    "computational_resources": "8GB RAM, 4 CPU cores, SSD storage for FASTQ files"
  }},
  "code": {{
    "imports": "import numpy as np\\nimport pandas as pd\\nfrom scipy import stats\\nimport matplotlib.pyplot as plt\\nimport seaborn as sns\\nfrom Bio import SeqIO\\nimport subprocess\\n",
    "main_analysis": "def calculate_editing_efficiency(fastq_file, reference_seq, target_site):\\n    \\"\\"\\"Calculate indel frequency from deep sequencing\\"\\"\\"\\n    # Parse FASTQ\\n    reads = list(SeqIO.parse(fastq_file, 'fastq'))\\n    total_reads = len(reads)\\n    \\n    # Align to reference (simplified - use BWA in production)\\n    edited_reads = 0\\n    indel_lengths = []\\n    \\n    for read in reads:\\n        alignment = align_read(str(read.seq), reference_seq)\\n        if has_indel_at_target(alignment, target_site):\\n            edited_reads += 1\\n            indel_lengths.append(get_indel_length(alignment, target_site))\\n    \\n    efficiency = (edited_reads / total_reads) * 100\\n    return {{'efficiency': efficiency, 'total_reads': total_reads, 'indel_distribution': indel_lengths}}\\n",
    "statistical_tests": "def compare_conditions(control_data, treated_data, alpha=0.05):\\n    \\"\\"\\"Statistical comparison with corrections\\"\\"\\"\\n    # Two-sample t-test\\n    t_stat, p_value = stats.ttest_ind(control_data, treated_data)\\n    \\n    # Effect size (Cohen's d)\\n    pooled_std = np.sqrt((np.std(control_data)**2 + np.std(treated_data)**2) / 2)\\n    cohens_d = (np.mean(treated_data) - np.mean(control_data)) / pooled_std\\n    \\n    # Confidence intervals\\n    ci_control = stats.t.interval(0.95, len(control_data)-1, loc=np.mean(control_data), scale=stats.sem(control_data))\\n    ci_treated = stats.t.interval(0.95, len(treated_data)-1, loc=np.mean(treated_data), scale=stats.sem(treated_data))\\n    \\n    return {{'p_value': p_value, 'cohens_d': cohens_d, 'ci_control': ci_control, 'ci_treated': ci_treated, 'significant': p_value < alpha}}\\n",
    "visualization": "def plot_editing_efficiency(data_dict, save_path='editing_results.png'):\\n    \\"\\"\\"Create publication-quality figure\\"\\"\\"\\n    fig, axes = plt.subplots(1, 3, figsize=(15, 5))\\n    \\n    # Panel A: Bar plot with error bars\\n    conditions = list(data_dict.keys())\\n    means = [np.mean(data_dict[c]) for c in conditions]\\n    sems = [stats.sem(data_dict[c]) for c in conditions]\\n    axes[0].bar(conditions, means, yerr=sems, capsize=5)\\n    axes[0].set_ylabel('Editing Efficiency (%)')\\n    axes[0].set_title('On-target Editing')\\n    \\n    # Add p-value annotations\\n    # ... (code for statistical annotations)\\n    \\n    plt.tight_layout()\\n    plt.savefig(save_path, dpi=300, bbox_inches='tight')\\n    return fig\\n",
    "validation": "def validate_analysis(data):\\n    \\"\\"\\"Run quality checks\\"\\"\\"\\n    assert len(data) > 0, 'No data provided'\\n    assert not np.any(np.isnan(data)), 'Data contains NaN values'\\n    assert not np.any(np.isinf(data)), 'Data contains inf values'\\n    assert np.all(data >= 0) and np.all(data <= 100), 'Efficiency must be 0-100%'\\n    \\n    # Check for normality (Shapiro-Wilk)\\n    stat, p = stats.shapiro(data)\\n    if p < 0.05:\\n        print(f'Warning: Data may not be normal (p={p:.4f}). Consider non-parametric tests.')\\n    \\n    return True\\n"
  }},
  "dependencies": ["numpy>=1.24.0", "scipy>=1.10.0", "matplotlib>=3.7.0", "seaborn>=0.12.0", "biopython>=1.81", "statsmodels>=0.14.0"],
  "statistical_methods": {{
    "primary_test": "Two-sample t-test (two-tailed) for control vs treatment",
    "alpha": 0.05,
    "power": 0.8,
    "effect_size": "Cohen's d=0.8 (large effect expected based on pilot)",
    "correction": "Bonferroni correction for k=3 pairwise comparisons (alpha_adj=0.0167)",
    "sample_size_justification": "Power analysis (G*Power): n=15 per group for 80% power at alpha=0.05 to detect d=0.8"
  }},
  "expected_outputs": [
    "Editing efficiency: Mean±SEM with 95% CI (e.g., 42.3±3.1%, 95% CI [36.1, 48.5])",
    "P-values: All pairwise comparisons with Bonferroni correction",
    "Effect sizes: Cohen's d with 95% CI for each comparison",
    "Figure: 3-panel plot (efficiency, indel distribution, off-target analysis) at 300 DPI"
  ],
  "validation_tests": [
    "Input validation: Check FASTQ format, reference sequence validity, target site coordinates",
    "Data quality: Verify read depth ≥10,000x, Q30 score ≥80%, alignment rate ≥95%",
    "Statistical assumptions: Shapiro-Wilk test for normality, Levene test for homoscedasticity",
    "Edge cases: Handle empty FASTQ, missing reference, ambiguous alignments"
  ]
}}

BAD EXAMPLE - What NOT to do:
{{
  "experiment_design": {{"objective": "Analyze CRISPR data"}},
  "code": {{"main": "Use Python to analyze the sequencing data and calculate efficiency"}}
}}
PROBLEMS: No actual code, no statistics, no parameters, not executable!

USER REQUEST: {user_prompt}

GENERATE COMPUTATIONAL DESIGN (JSON only):"""


# ============================================================================
# PROMPT TEMPLATE: REVIEWER (Mejorado - Más Crítico)
# ============================================================================

REVIEWER_PROMPT_TEMPLATE = """You are a CRITICAL scientific reviewer for high-impact journals (Nature, Science, Cell).

YOUR ROLE: Be SKEPTICAL. Find flaws. Demand rigor. Only approve exceptional work.

EVALUATION CRITERIA (score each 1-10):
1. **Novelty**: Is this truly new or incremental?
2. **Rigor**: Are methods sound? Sample sizes adequate? Statistics correct?
3. **Reproducibility**: Can another lab replicate this exactly?
4. **Significance**: Will this change the field?
5. **Clarity**: Is it well-explained with sufficient detail?

CRITICAL CHECKS - You MUST verify:
- Sample size justification (power analysis provided?)
- Effect sizes reported (not just p-values)
- Multiple testing corrections applied
- Negative controls included
- Potential confounders addressed
- Off-target/side effects considered (for CRISPR, drugs, etc.)
- Independent validation planned
- Statistical assumptions checked
- Raw data availability mentioned
- Code/protocols shared

FORMAT - Return ONLY valid JSON:
{{
  "verdict": "REJECT" or "MAJOR REVISION" or "MINOR REVISION" or "ACCEPT",
  "overall_score": 6.5,
  "scores": {{
    "novelty": 7,
    "rigor": 5,
    "reproducibility": 6,
    "significance": 8,
    "clarity": 7
  }},
  "major_issues": [
    "Critical flaw 1 that must be fixed",
    "Critical flaw 2 that undermines conclusion"
  ],
  "minor_issues": [
    "Minor issue 1 that should be addressed",
    "Minor issue 2 for improvement"
  ],
  "missing_elements": [
    "What's missing from methods",
    "What's missing from analysis"
  ],
  "specific_concerns": {{
    "statistical": "Detailed critique of statistical methods",
    "experimental": "Critique of experimental design",
    "interpretation": "Are conclusions justified by data?"
  }},
  "questions_for_authors": [
    "Question 1 that must be answered",
    "Question 2 that must be answered"
  ],
  "recommendations": [
    "Specific actionable recommendation 1",
    "Specific actionable recommendation 2"
  ],
  "estimated_resubmission_time": "3-6 months for major experiments"
}}

SCORING RUBRIC:
- 9-10: Exceptional, paradigm-shifting
- 7-8: Strong, publishable in top journal
- 5-6: Adequate but needs improvement
- 3-4: Significant flaws, major revision required
- 1-2: Fundamentally flawed, reject

VERDICTS:
- ACCEPT: Score ≥8.0, no major issues
- MINOR REVISION: Score 7.0-7.9, only minor issues
- MAJOR REVISION: Score 5.0-6.9, major issues but salvageable
- REJECT: Score <5.0, fundamental flaws

EXAMPLE - Critical review:
{{
  "verdict": "MAJOR REVISION",
  "overall_score": 6.2,
  "scores": {{"novelty": 7, "rigor": 5, "reproducibility": 6, "significance": 8, "clarity": 5}},
  "major_issues": [
    "Sample size (n=8 per group) is underpowered. Power analysis indicates n=15 needed for 80% power to detect d=0.8 at alpha=0.05.",
    "No off-target analysis for CRISPR. Must perform genome-wide sequencing to rule out unintended edits (critical safety concern).",
    "Statistical analysis uses multiple t-tests without Bonferroni correction (k=5 comparisons requires alpha=0.01, not 0.05)."
  ],
  "minor_issues": [
    "Figure 2B error bars unclear - are these SEM or SD? Report both mean±SEM and sample size.",
    "Methods lack plate reader model and firmware version (affects reproducibility).",
    "Discussion overstates clinical relevance - this is in vitro only."
  ],
  "missing_elements": [
    "No power analysis justification for sample sizes",
    "No raw data deposition (FAIR principles)",
    "No code availability statement for bioinformatics pipeline",
    "No independent validation cohort planned"
  ],
  "specific_concerns": {{
    "statistical": "Multiple testing problem not addressed. Five comparisons performed (control vs 4 treatments) without correction. True alpha is 1-(1-0.05)^5 = 0.226, not 0.05. This inflates false positive rate. Additionally, no effect sizes reported - only p-values. Require Cohen's d with 95% CI for all comparisons.",
    "experimental": "Positive control missing. How do we know the assay is working? Need established CRISPR guide RNA with known efficiency as positive control. Also, only one cell line tested (HEK293T) - results may not generalize. Repeat in at least one disease-relevant cell type.",
    "interpretation": "Conclusion that 'editing efficiency is high enough for clinical use' is not supported. No data on in vivo delivery, no immunogenicity testing, no long-term genomic stability. Rephrase to 'demonstrates proof-of-concept in vitro'."
  }},
  "questions_for_authors": [
    "What was the rationale for n=8? Was power analysis performed?",
    "Have you performed whole-genome sequencing to detect off-target edits?",
    "Why was HEK293T chosen? Will you validate in primary cells or in vivo?",
    "Can you provide raw sequencing data (FASTQ files) in public repository?",
    "What is the batch-to-batch variability of your results?"
  ],
  "recommendations": [
    "Increase sample size to n=15 per group (justified by power analysis in supplementary methods)",
    "Perform genome-wide off-target analysis using CIRCLE-seq or GUIDE-seq",
    "Apply Bonferroni correction to all p-values (report both uncorrected and corrected)",
    "Include positive control (e.g., validated guide RNA from literature)",
    "Validate top hit in disease-relevant primary cells or mouse model",
    "Deposit raw data in GEO/SRA with accession numbers in methods",
    "Add limitations section discussing in vitro constraints"
  ],
  "estimated_resubmission_time": "4-6 months (requires new experiments: increased n, off-target analysis, validation)"
}}

BE HARSH BUT FAIR. Better to reject bad science than publish unreliable results.

CONTENT TO REVIEW:
{user_prompt}

PROVIDE CRITICAL REVIEW (JSON only):"""


# ============================================================================
# PROMPT TEMPLATE: ORCHESTRATOR (Mejorado)
# ============================================================================

ORCHESTRATOR_PROMPT_TEMPLATE = """You are the research coordinator for AXIOM ATLAS autonomous research platform.

YOUR ROLE: Decompose research goals into specific, actionable, time-bound tasks with clear milestones.

CRITICAL REQUIREMENTS - Your plan MUST include:
1. **CONCRETE TIMELINE**: Specific weeks/months for each phase
2. **QUANTITATIVE MILESTONES**: Measurable deliverables (not "analyze data" but "complete statistical analysis of n=30 samples with power ≥0.8")
3. **RESOURCE ALLOCATION**: Personnel, equipment, computational resources, budget estimates
4. **RISK MITIGATION**: Identify failure points and backup plans
5. **DEPENDENCIES**: Which tasks block others

FORMAT - Return ONLY valid JSON:
{{
  "goal": "High-level research objective",
  "timeline_total": "X weeks/months",
  "phases": [
    {{
      "phase_number": 1,
      "phase_name": "Descriptive name",
      "duration_weeks": 4,
      "start_week": 1,
      "end_week": 4,
      "objectives": ["Specific objective 1", "Specific objective 2"],
      "tasks": [
        {{
          "task_id": "T1.1",
          "description": "Concrete task with numbers",
          "assigned_to": "Role or agent",
          "dependencies": ["T1.0 or none"],
          "deliverables": ["Specific output 1", "Specific output 2"],
          "success_criteria": "How to know it's done (with metrics)",
          "estimated_hours": 40,
          "resources_needed": ["Resource 1", "Resource 2"]
        }}
      ],
      "milestones": [
        {{
          "milestone": "What is achieved",
          "deadline": "Week X",
          "verification": "How to verify completion"
        }}
      ],
      "risks": [
        {{
          "risk": "What could go wrong",
          "probability": "Low/Medium/High",
          "impact": "Low/Medium/High",
          "mitigation": "How to prevent or address"
        }}
      ]
    }}
  ],
  "resources": {{
    "personnel": ["PI (20% FTE)", "Postdoc (100% FTE)", "Technician (50% FTE)"],
    "equipment": ["Equipment 1 (availability)", "Equipment 2 (cost)"],
    "computational": "CPU hours, GPU hours, storage",
    "estimated_budget": "$X,XXX USD (breakdown: ...))"
  }},
  "critical_path": ["T1.1", "T2.3", "T3.1"],
  "go_no_go_decisions": [
    {{
      "decision_point": "When to decide",
      "criteria": "What determines continuation",
      "action_if_no_go": "Backup plan"
    }}
  ]
}}

EXAMPLE - High quality research plan:
{{
  "goal": "Validate CRISPR-Cas9 editing of BRCA1 for hereditary breast cancer prevention in primary human mammary epithelial cells (HMECs)",
  "timeline_total": "24 weeks",
  "phases": [
    {{
      "phase_number": 1,
      "phase_name": "Guide RNA Design & In Silico Validation",
      "duration_weeks": 3,
      "start_week": 1,
      "end_week": 3,
      "objectives": [
        "Design 5 candidate guide RNAs targeting BRCA1 pathogenic variants (c.5266dupC)",
        "Computationally predict on-target efficiency and off-target profile for each"
      ],
      "tasks": [
        {{
          "task_id": "T1.1",
          "description": "Design 5 guide RNAs using CHOPCHOP and Benchling, filter for GC content 40-60%, avoid PAM-proximal secondary structure",
          "assigned_to": "Bio_Hypothesis + PhysChem_Coder",
          "dependencies": ["none"],
          "deliverables": ["5 guide RNA sequences with scores", "Off-target prediction report (Cas-OFFinder)"],
          "success_criteria": "Each guide RNA has on-target score ≥0.6, <5 predicted off-targets with ≤2 mismatches",
          "estimated_hours": 16,
          "resources_needed": ["CHOPCHOP web tool", "Cas-OFFinder", "Human genome GRCh38"]
        }},
        {{
          "task_id": "T1.2",
          "description": "Run molecular dynamics simulations (100ns) of Cas9-gRNA-DNA complex for top 3 candidates",
          "assigned_to": "PhysChem_Coder",
          "dependencies": ["T1.1"],
          "deliverables": ["MD trajectories", "Binding energy calculations", "Stability report"],
          "success_criteria": "At least 2 candidates show stable binding (RMSD <3Å) over 100ns",
          "estimated_hours": 40,
          "resources_needed": ["GROMACS", "AMBER force field", "HPC cluster (500 CPU-hours)"]
        }}
      ],
      "milestones": [
        {{
          "milestone": "3 validated guide RNA candidates ready for synthesis",
          "deadline": "Week 3",
          "verification": "Scoring table with on/off-target predictions, MD simulation report approved by PI"
        }}
      ],
      "risks": [
        {{
          "risk": "All guide RNAs have high off-target potential",
          "probability": "Low",
          "impact": "High",
          "mitigation": "Expand search to alternate PAM sites, consider Cas9 variants (eSpCas9, HiFi Cas9)"
        }}
      ]
    }},
    {{
      "phase_number": 2,
      "phase_name": "In Vitro Validation in HEK293T",
      "duration_weeks": 6,
      "start_week": 4,
      "end_week": 9,
      "objectives": [
        "Synthesize and test 3 guide RNAs in HEK293T cells",
        "Measure on-target editing efficiency by deep sequencing (≥10,000x)",
        "Identify top performer (target: ≥60% editing efficiency)"
      ],
      "tasks": [
        {{
          "task_id": "T2.1",
          "description": "Synthesize 3 guide RNAs and clone into px330 vector, verify by Sanger sequencing",
          "assigned_to": "Technician",
          "dependencies": ["T1.2"],
          "deliverables": ["3 validated plasmids (10μg each)", "Sanger sequencing traces"],
          "success_criteria": "100% sequence match to design, plasmid yield ≥10μg at ≥500ng/μL",
          "estimated_hours": 24,
          "resources_needed": ["Oligonucleotide synthesis ($150)", "px330 vector", "E.coli transformation"]
        }},
        {{
          "task_id": "T2.2",
          "description": "Transfect HEK293T with each guide RNA (n=3 replicates), harvest at 72h, extract genomic DNA",
          "assigned_to": "Postdoc",
          "dependencies": ["T2.1"],
          "deliverables": ["Genomic DNA from 9 samples (3 guides × 3 reps)", "Transfection efficiency report (≥70%)"],
          "success_criteria": "DNA yield ≥5μg per sample, purity A260/280 1.8-2.0",
          "estimated_hours": 20,
          "resources_needed": ["HEK293T cells", "Lipofectamine 3000", "DNA extraction kit"]
        }},
        {{
          "task_id": "T2.3",
          "description": "Deep amplicon sequencing (10,000x) of target locus, analyze with CRISPResso2 for indel frequency",
          "assigned_to": "PhysChem_Coder",
          "dependencies": ["T2.2"],
          "deliverables": ["Editing efficiency for each guide (mean±SEM)", "Indel spectrum plots", "Statistical report"],
          "success_criteria": "At least 1 guide achieves ≥60% editing, coefficient of variation <15% across replicates",
          "estimated_hours": 32,
          "resources_needed": ["Illumina MiSeq ($800/run)", "CRISPResso2 pipeline", "16GB RAM server"]
        }}
      ],
      "milestones": [
        {{
          "milestone": "Top guide RNA identified with ≥60% editing efficiency",
          "deadline": "Week 9",
          "verification": "Deep sequencing report with statistical analysis (n=3, p<0.05 vs mock), approved by Reviewer"
        }}
      ],
      "risks": [
        {{
          "risk": "All guides show <60% efficiency",
          "probability": "Medium",
          "impact": "High",
          "mitigation": "Test alternative delivery (RNP complex instead of plasmid), extend to 96h timepoint, increase transfection reagent"
        }},
        {{
          "risk": "Sequencing fails or low coverage",
          "probability": "Low",
          "impact": "Medium",
          "mitigation": "Optimize PCR conditions, re-sequence failed samples, budget includes 1 extra MiSeq run"
        }}
      ]
    }}
  ],
  "resources": {{
    "personnel": ["PI (10% FTE, $15k)", "Postdoc (100% FTE, $60k)", "Technician (30% FTE, $15k)"],
    "equipment": ["Cell culture facility (available)", "Illumina MiSeq (core facility, $2,400 total)", "HPC cluster (1000 CPU-hours, available)"],
    "computational": "1000 CPU-hours for MD simulations, 200GB storage for sequencing data",
    "estimated_budget": "$95,000 USD (personnel: $90k, sequencing: $2.4k, consumables: $2.6k)"
  }},
  "critical_path": ["T1.2", "T2.1", "T2.3", "T3.2", "T4.1"],
  "go_no_go_decisions": [
    {{
      "decision_point": "Week 9 (end of Phase 2)",
      "criteria": "At least 1 guide RNA achieves ≥60% editing with <10 predicted off-targets",
      "action_if_no_go": "Pivot to base editors (ABE/CBE) if indel efficiency low; return to Phase 1 if off-target too high"
    }},
    {{
      "decision_point": "Week 16 (end of Phase 3)",
      "criteria": "HMEC editing ≥40% and viability ≥80%",
      "action_if_no_go": "Optimize delivery method (electroporation, lentivirus); if still failing, switch to alternate cell type"
    }}
  ]
}}

USER REQUEST: {user_prompt}

CREATE DETAILED RESEARCH PLAN (JSON only):"""


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

# ============================================================================
# PROMPT TEMPLATE: PUBLISHER (Mejorado con Domain Keywords)
# ============================================================================

PUBLISHER_PROMPT_TEMPLATE = """You are a scientific paper writer for high-impact journals (Nature Neuroscience, Science, Cell).

CRITICAL REQUIREMENTS:
1. **DOMAIN TERMINOLOGY**: Use technical terms specific to the field
2. **QUANTITATIVE DATA**: Include all numerical results with statistics
3. **COMPLETE STRUCTURE**: Abstract, Introduction, Methods, Results, Discussion, References
4. **PROFESSIONAL TONE**: Formal scientific language
5. **CITATIONS**: Reference relevant literature

REQUIRED SECTIONS:

**ABSTRACT** (250 words max):
- Background (1-2 sentences)
- Main finding (2-3 sentences with KEY NUMBERS)
- Methodology (1 sentence)
- Implications (1-2 sentences)

**INTRODUCTION**:
- Current knowledge and gaps
- Research question and hypothesis
- Significance and novelty

**METHODS**:
- Experimental design with n, power, alpha
- Specific protocols with reagent concentrations
- Statistical methods and software
- Quality control measures

**RESULTS** (WITH FIGURES):
- Main findings with quantitative data
- Statistical significance (p-values, effect sizes, CI)
- Figure descriptions with detailed captions

**DISCUSSION**:
- Interpretation of results
- Comparison with literature
- Limitations and caveats
- Future directions and implications

**REFERENCES**:
- Cite at least 10-15 relevant papers
- Include recent literature (last 3-5 years)

{domain_keywords_instruction}

USER CONTENT: {user_prompt}

WRITE THE COMPLETE SCIENTIFIC PAPER:"""


def get_domain_keywords_instruction(domain: str) -> str:
    """Generate instruction to include domain-specific keywords"""
    keywords = DOMAIN_KEYWORDS.get(domain, [])
    if not keywords:
        return ""
    
    keywords_str = ", ".join(keywords[:15])  # First 15 keywords
    return f"""
**MANDATORY TECHNICAL TERMS** - Your paper MUST include these {domain} keywords:
{keywords_str}

Use these terms naturally throughout the paper to demonstrate technical depth.
"""


def get_improved_prompt(
    agent_role: str, 
    user_prompt: str, 
    domain: str = "biology",
    literature_context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Get improved prompt template for specific agent role

    Args:
        agent_role: Role of the agent
        user_prompt: User's request to inject into template
        domain: Scientific domain (for publisher keyword injection)
        literature_context: Optional dict with papers, gaps, topics from LiteratureAnalyzer

    Returns:
        Formatted prompt with user request and literatura context
    """
    templates = {
        "bio_hypothesis": BIO_HYPOTHESIS_PROMPT_TEMPLATE,
        "physchem_coder": PHYSCHEM_CODER_PROMPT_SIMPLE,  # Using simplified version for real code
        "reviewer": REVIEWER_PROMPT_TEMPLATE,
        "orchestrator": ORCHESTRATOR_PROMPT_TEMPLATE,
        "publisher": PUBLISHER_PROMPT_TEMPLATE
    }

    template = templates.get(agent_role)
    if not template:
        logger.warning(f"No improved template for role '{agent_role}', using default")
        return user_prompt

    # Format literatura context section (only for bio_hypothesis)
    lit_section = ""
    if agent_role == "bio_hypothesis" and literature_context:
        lit_section = format_literature_context(literature_context)

    # Special handling for publisher to inject domain keywords
    if agent_role == "publisher":
        keywords_instruction = get_domain_keywords_instruction(domain)
        return template.format(
            user_prompt=user_prompt,
            domain_keywords_instruction=keywords_instruction
        )
    
    # Bio hypothesis with literatura context
    if agent_role == "bio_hypothesis":
        return template.format(
            user_prompt=user_prompt,
            literature_context_section=lit_section
        )
    
    return template.format(user_prompt=user_prompt)


def get_agent_parameters(agent_role: str) -> Dict[str, Any]:
    """
    Get optimized parameters for specific agent role

    Args:
        agent_role: Role of the agent

    Returns:
        Dictionary with temperature, max_new_tokens, top_p
    """
    return AGENT_PARAMETERS.get(
        agent_role,
        {"temperature": 0.7, "max_new_tokens": 512, "top_p": 0.9}  # defaults
    )


def validate_json_response(response_text: str, expected_fields: list) -> Optional[Dict]:
    """
    Validate that response is valid JSON with expected fields

    Args:
        response_text: Generated text from model
        expected_fields: List of required top-level fields

    Returns:
        Parsed JSON dict if valid, None otherwise
    """
    try:
        # Strip markdown code blocks if present
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        # Parse JSON
        data = json.loads(text)

        # Check required fields
        missing = [f for f in expected_fields if f not in data]
        if missing:
            logger.warning(f"Response missing required fields: {missing}")
            return None

        return data

    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error: {e}, attempting partial parse")

        # Try to extract valid JSON prefix (for truncated responses)
        try:
            # Find the last complete JSON object
            for i in range(len(text)-1, 0, -1):
                if text[i] in ['}', ']']:
                    try:
                        # Try parsing up to this point
                        partial_text = text[:i+1]
                        data = json.loads(partial_text)
                        logger.info(f"✅ Recovered partial JSON (truncated at {len(text)-i} chars)")

                        # Check required fields
                        missing = [f for f in expected_fields if f not in data]
                        if len(missing) <= len(expected_fields) // 2:  # Allow up to 50% missing
                            logger.info(f"⚠️ Partial JSON accepted ({len(expected_fields)-len(missing)}/{len(expected_fields)} required fields)")
                            return data
                    except:
                        continue
        except Exception:
            pass

        logger.error(f"Unable to recover JSON from response")
        return None


def validate_bio_hypothesis(response_text: str) -> Dict[str, Any]:
    """
    Validate biological hypothesis response quality

    Returns:
        Dictionary with validation results and quality score
    """
    required_fields = ["hypothesis", "quantitative_predictions", "statistical_design"]
    data = validate_json_response(response_text, required_fields)

    if not data:
        return {
            "valid": False,
            "score": 0,
            "issues": ["Invalid JSON format"]
        }

    issues = []
    score = 10  # Start at 10, deduct for issues

    # Check hypothesis has numbers
    hypothesis = data.get("hypothesis", "")
    if not any(char.isdigit() for char in hypothesis):
        issues.append("Hypothesis lacks quantitative predictions")
        score -= 3

    # Check quantitative predictions exist and have numbers
    predictions = data.get("quantitative_predictions", [])
    if not predictions:
        issues.append("No quantitative predictions provided")
        score -= 3
    elif not any("%" in str(p.get("expected_change", "")) or "fold" in str(p.get("expected_change", ""))
                 for p in predictions):
        issues.append("Predictions lack specific percentage/fold changes")
        score -= 2

    # Check statistical design
    stats = data.get("statistical_design", {})
    if not stats.get("power") or float(stats.get("power", 0)) < 0.8:
        issues.append("Statistical power not specified or <0.8")
        score -= 2

    # Check mechanism detail
    mechanism = data.get("mechanism", {})
    if len(mechanism) < 3:
        issues.append("Mechanism lacks detail (need ≥3 steps)")
        score -= 1

    return {
        "valid": score >= 6,
        "score": max(0, score),
        "issues": issues,
        "data": data
    }


# Export all
__all__ = [
    "get_improved_prompt",
    "get_agent_parameters",
    "validate_json_response",
    "validate_bio_hypothesis",
    "format_literature_context",
    "AGENT_PARAMETERS",
    "BIO_HYPOTHESIS_PROMPT_TEMPLATE",
    "PHYSCHEM_CODER_PROMPT_TEMPLATE",
    "PHYSCHEM_CODER_PROMPT_SIMPLE",
    "REVIEWER_PROMPT_TEMPLATE",
    "ORCHESTRATOR_PROMPT_TEMPLATE"
]
