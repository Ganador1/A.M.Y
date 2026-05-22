def investigate_medical_treatments(disease_name, standard_of_care_info):
    # Phase 1: Map current standard of care and limitations
    limitations = identify_sof_limitations(standard_of_care_info)
    
    # Phase 2: Systematic survey of innovative approaches
    categories = ['cell_therapy', 'viral_therapy', 'targeted_delivery',
                  'immunotherapy', 'genetic_therapy', 'device_therapy']
    approaches = {}
    for cat in categories:
        approaches[cat] = research_category(disease_name, cat)
    
    # Phase 3: Rank by clinical evidence + combinatorial potential
    tier1 = [a for a in approaches.values() if a.evidence >= 'phaseII' and a.combo_value >= 0.8]
    tier2 = [a for a in approaches.values() if a.evidence >= 'phaseI' and a.combo_value >= 0.5]
    tier3 = [a for a in approaches.values() if a.evidence < 'phaseI' or a.combo_value < 0.5]
    
    # Phase 4: Identify combination strategies
    # Key insight: combinations must address ALL core disease mechanisms
    core_mechanisms = identify_core_mechanisms(disease_name)
    optimal_combos = find_synergistic_combinations(tier1 + tier2, core_mechanisms)
    
    # Phase 5: Resistance and failure analysis
    resistance = analyze_resistance_mechanisms(optimal_combos)
    
    # Phase 6: Clinical recommendations with biomarkers
    recommendations = generate_clinical_recommendations(
        optimal_combos, resistance, biomarker_data
    )
    
    return {
        'ranked_treatments': {'tier1': tier1, 'tier2': tier2, 'tier3': tier3},
        'optimal_combinations': optimal_combos,
        'resistance_considerations': resistance,
        'clinical_recommendations': recommendations
    }