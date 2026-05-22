def systematic_medical_review(disease, year_range='2023-2024'):
    """Systematic methodology for investigating innovative treatments.
    
    Steps:
    1. DECOMPOSE: Break disease into therapeutic domains:
       - Immunotherapy (cell therapies, vaccines, checkpoint inhibitors)
       - Virotherapy (oncolytic viruses by type)
       - Drug delivery (nanoparticles, CED, BBB disruption)
       - Targeted molecular (mutations, pathways, metabolic)
       - Microenvironment & combination strategies
    
    2. RESEARCH each domain with precise queries:
       - Include disease name, modality, year range, clinical trial phase
       - Track specific agents, trial names (NCT numbers), outcomes
       
    3. IDENTIFY cross-cutting patterns:
       - Delivery route effectiveness comparisons
       - Single vs combination modality outcomes
       - Timing considerations (neoadjuvant vs adjuvant)
       - Biomarker-driven patient selection
       
    4. EVIDENCE HIERARCHY tracking:
       - Phase III results > Phase II > Phase I > Preclinical
       - Note regulatory status (FDA breakthrough, orphan drug)
       
    5. SYNTHESIZE comparative effectiveness:
       - Rank modalities by median OS improvement
       - Identify most promising near-term vs long-term
       - Map remaining challenges
       
    Returns: Structured findings with confidence levels
    """
    domains = [
        'immunotherapy_approaches',
        'oncolytic_virus_therapy',
        'drug_delivery_systems',
        'targeted_molecular_therapies',
        'microenvironment_combination_strategies'
    ]
    
    patterns_to_track = [
        'local_vs_systemic_delivery',
        'single_vs_combination_efficacy',
        'neoadjuvant_timing_advantage',
        'biomarker_selection_benefit',
        'regulatory_milestones'
    ]
    
    return {
        'domains': domains,
        'patterns': patterns_to_track,
        'evidence_hierarchy': ['phase_III', 'phase_II', 'phase_I', 'preclinical']
    }