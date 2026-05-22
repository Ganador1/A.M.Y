def research_intractable_cancer(cancer_type, standard_survival_months):
    """Structured research protocol for innovative cancer treatments."""
    sub_goals = [
        'immunotherapy_approaches',  # CAR-T, vaccines, checkpoint inhibitors
        'viral_gene_therapy',  # Oncolytic viruses, gene therapy
        'drug_delivery_innovation',  # Nanoparticles, CED, BBB disruption
        'targeted_molecular_therapy',  # Mutation-specific, pathway inhibitors
        'microenvironment_combination',  # TME modulation, synthetic lethality
    ]
    
    evidence_tiers = {
        'Tier1': 'Phase II-III positive with survival benefit',
        'Tier2': 'Phase I-II with promising signals',
        'Tier3': 'Preclinical with strong rationale',
    }
    
    cross_cutting_insights = {
        'delivery': 'Local delivery outperforms systemic for barrier cancers',
        'timing': 'Neoadjuvant/perioperative timing shows superior outcomes',
        'combination': 'Multi-modal approaches needed due to heterogeneity',
        'biomarkers': 'Patient selection critical for targeted approaches',
    }
    
    synthesis = {
        'most_promising': 'Identify based on phase II-III evidence + survival benefit',
        'near_term': 'Combination approaches with existing tools',
        'paradigm_shift': 'Novel modalities requiring phase III validation',
        'key_lesson': 'Single-agent systemic approaches insufficient for barrier cancers'
    }
    
    return {'sub_goals': sub_goals, 'evidence_tiers': evidence_tiers,
            'insights': cross_cutting_insights, 'synthesis': synthesis}