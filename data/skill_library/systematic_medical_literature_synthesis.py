def research_innovative_cancer_treatments(disease_name, standard_survival_months):
    """Systematic research framework for innovative cancer treatments."""
    
    # Step 1: Define therapeutic challenges
    challenges = identify_therapeutic_challenges(disease_name)
    # e.g., for GBM: BBB, heterogeneity, immunosuppression, recurrence
    
    # Step 2: Decompose into modality sub-goals
    sub_goals = [
        'immunotherapy_approaches',      # CAR-T, vaccines, checkpoint inhibitors
        'viral_gene_therapy',             # Oncolytic viruses, gene therapy
        'novel_delivery_systems',        # Nanoparticles, CED, BBB disruption
        'targeted_molecular_therapy',    # Kinase inhibitors, mutation-specific
        'combination_microenvironment'   # TME modulation, synthetic lethality
    ]
    
    # Step 3: Research each with year-specific clinical trial focus
    findings = {}
    for goal in sub_goals:
        findings[goal] = research_modality(disease_name, goal, years='2023-2024')
    
    # Step 4: Identify cross-cutting patterns
    patterns = identify_patterns(findings)
    # Expected patterns for aggressive cancers:
    # - Local delivery > systemic for protected sites
    # - Neoadjuvant timing > adjuvant-only for immunotherapy
    # - Combination > single modality due to heterogeneity
    # - TME modulation is critical enabler
    
    # Step 5: Synthesize with confidence weighting
    synthesis = {
        'most_promising_approaches': rank_by_evidence(findings),
        'key_patterns': patterns,
        'regulatory_pipeline': track_regulatory_status(findings),
        'research_gaps': identify_gaps(findings),
        'comparison_to_standard': compare_to_standard(findings, standard_survival_months)
    }
    
    return synthesis