def design_combination_trial_protocol(cancer_type, resistance_mechanisms, available_modalities, biomarker_data):
    """
    Design a sequential multi-modal combination trial for aggressive cancers.
    
    Based on GBM-SONIC framework: Sonicated Oncolytic Neo-Immunologic Combination.
    
    Parameters:
    - cancer_type: str (e.g., 'glioblastoma_multiforme')
    - resistance_mechanisms: list of dominant resistance mechanisms
    - available_modalities: dict of treatment modalities with evidence levels
    - biomarker_data: dict of available predictive biomarkers
    
    Returns:
    - Complete trial protocol with phases, endpoints, stratification criteria
    """
    
    # Step 1: Rank modalities by combinatorial value
    # Key principle: mechanism-converting agents > additive agents
    modality_ranking = rank_by_combinatorial_value(
        available_modalities,
        resistance_mechanisms
    )
    
    # Step 2: Design sequential delivery exploiting synergistic timing
    # Phase A: Barrier disruption (e.g., focused ultrasound for BBB)
    # Phase B: Payload delivery (e.g., oncolytic virus during BBB window)
    # Phase C: Immune maintenance (e.g., checkpoint inhibitor after viral priming)
    sequential_protocol = design_sequential_phases(
        modality_ranking,
        timing_constraints=get_synergistic_timing_windows()
    )
    
    # Step 3: Biomarker-guided patient stratification
    # Stratify by: (a) treatment sensitivity predictors (MGMT, IDH),
    # (b) immune competence (PD-L1, TIL density),
    # (c) tumor biology (molecular subtype)
    stratification_criteria = define_stratification(
        biomarker_data,
        modality_ranking
    )
    
    # Step 4: Define adaptive endpoints
    # Primary: OS at 12/24 months
    # Secondary: PFS, radiographic response, immune activation biomarkers
    # Exploratory: circulating tumor DNA, immune repertoire dynamics
    endpoints = define_adaptive_endpoints(
        cancer_type,
        sequential_protocol
    )
    
    # Step 5: Regulatory pathway planning
    # Multi-product combination requires: coordinated IND/IDE,
    # breakthrough therapy designation pursuit, manufacturing logistics
    regulatory_plan = plan_regulatory_pathway(
        sequential_protocol,
        combination_type='device_drug_biologic'
    )
    
    return {
        'trial_name': generate_trial_acronym(cancer_type, sequential_protocol),
        'phases': sequential_protocol,
        'stratification': stratification_criteria,
        'endpoints': endpoints,
        'regulatory_pathway': regulatory_plan,
        'tier_ranking': modality_ranking,
        'combination_rationale': explain_synergy(resistance_mechanisms, sequential_protocol)
    }

def rank_by_combinatorial_value(modalities, resistance_mechanisms):
    """
    Rank treatment modalities by their combinatorial potential.
    
    Key insight: Agents that CONVERT resistance mechanisms
    (e.g., oncolytic viruses converting immunosuppressive TME)
    have higher combinatorial value than agents that merely
    ADD an effect (e.g., additional cytotoxic agent).
    """
    tier_1 = []  # High evidence + high combinatorial value
    tier_2 = []  # Moderate evidence OR moderate combinatorial value  
    tier_3 = []  # Limited evidence + limited combinatorial value
    
    for modality, evidence in modalities.items():
        combo_score = calculate_combinatorial_score(
            modality, resistance_mechanisms
        )
        if combo_score >= 0.8 and evidence['phase'] >= 2:
            tier_1.append(modality)
        elif combo_score >= 0.5 or evidence['phase'] >= 2:
            tier_2.append(modality)
        else:
            tier_3.append(modality)
    
    return {'tier_1': tier_1, 'tier_2': tier_2, 'tier_3': tier_3}

def get_synergistic_timing_windows():
    """
    Define optimal timing windows for sequential combination.
    
    Based on GBM-SONIC protocol:
    - Focused ultrasound BBB disruption: 4-6 hour window
    - Oncolytic virus delivery: within BBB disruption window
    - Checkpoint inhibitor: 7-14 days post-viral priming
    - Repeat cycle: every 4-6 weeks
    """
    return {
        'bbb_disruption_window_hours': [4, 6],
        'viral_delivery_window': 'within_bbb_disruption',
        'checkpoint_inhibitor_start_days': [7, 14],
        'cycle_repeat_weeks': [4, 6]
    }