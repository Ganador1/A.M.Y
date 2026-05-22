def investigate_innovative_cancer_treatments(cancer_type, key_challenges):
    """Research innovative treatments for aggressive cancers.
    
    Args:
        cancer_type: e.g., 'glioblastoma multiforme', 'pancreatic adenocarcinoma'
        key_challenges: list of therapeutic barriers e.g., ['blood-brain barrier', 'immunosuppressive TME']
    
    Returns:
        Structured findings dict with treatment modalities, evidence levels, and recommendations
    """
    sub_goals = [
        'immunotherapy_approaches',  # CAR-T, DC vaccines, checkpoint inhibitors, bispecifics
        'oncolytic_virus_therapy',   # HSV, adenovirus, poliovirus platforms
        'novel_delivery_systems',    # nanoparticles, CED, BBB disruption
        'targeted_molecular',       # actionable mutations, pathway inhibitors, metabolic
        'microenvironment_combination'  # TME modulation, synthetic lethality, multi-modal
    ]
    
    search_patterns = {
        'immunotherapy': f'{cancer_type} immunotherapy CAR-T dendritic cell vaccine checkpoint inhibitor clinical trials 2023 2024',
        'oncolytic_virus': f'{cancer_type} oncolytic virus therapy clinical trials 2023 2024 HSV adenovirus',
        'delivery': f'{cancer_type} novel drug delivery nanoparticles convection-enhanced 2023 2024',
        'targeted': f'{cancer_type} targeted molecular therapy inhibitors mutations 2023 2024',
        'combination': f'{cancer_type} tumor microenvironment combination therapy synthetic lethality 2023 2024'
    }
    
    # Cross-cutting patterns to identify
    meta_patterns = [
        'local_delivery_vs_systemic_efficacy',
        'neoadjuvant_timing_advantages',
        'single_modality_limitations_from_heterogeneity',
        'combination_synergy_potential',
        'regulatory_pathway_status'
    ]
    
    return {
        'sub_goals': sub_goals,
        'search_patterns': search_patterns,
        'meta_patterns': meta_patterns,
        'key_challenges': key_challenges
    }