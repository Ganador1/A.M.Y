def investigate_disease_treatments(disease_name, key_challenges):
    """Systematic investigation of innovative treatments for complex diseases.
    
    Args:
        disease_name: Name of disease (e.g., 'glioblastoma multiforme')
        key_challenges: List of therapeutic challenges (e.g., ['BBB', 'heterogeneity', 'immunosuppression'])
    
    Returns:
        Structured findings across five research domains with cross-cutting synthesis
    """
    domains = {
        'immunotherapy': {
            'focus': ['CAR-T', 'dendritic_cell_vaccines', 'checkpoint_inhibitors', 'bispecific_antibodies'],
            'metrics': ['overall_survival', 'progression_free_survival', 'response_rate', 'clinical_trial_phase'],
            'search_pattern': f'{{therapy}} {{disease}} {{year_range}} clinical trial results'
        },
        'biological_therapies': {
            'focus': ['oncolytic_viruses', 'mRNA_vaccines', 'gene_therapy'],
            'metrics': ['safety_profile', 'viral_delivery_efficiency', 'FDA_status', 'median_survival'],
            'search_pattern': f'{{modality}} {{disease}} {{year_range}} trial outcomes regulatory status'
        },
        'drug_delivery': {
            'focus': ['nanoparticles', 'convection_enhanced_delivery', 'BBB_disruption', 'local_delivery'],
            'metrics': ['CNS_concentration_achieved', 'delivery_efficiency', 'safety', 'pharmacokinetics'],
            'search_pattern': f'{{delivery_method}} {{disease}} {{year_range}} BBB penetration'
        },
        'targeted_therapy': {
            'focus': ['mutation_specific_inhibitors', 'signaling_pathways', 'metabolic_vulnerabilities'],
            'metrics': ['target_inhibition', 'biomarker_prediction', 'resistance_mechanisms', 'combination_potential'],
            'search_pattern': f'{{target}} inhibitor {{disease}} {{year_range}} clinical trial'
        },
        'combination_tme': {
            'focus': ['tumor_microenvironment_modulation', 'synthetic_lethality', 'radiosensitizers', 'multi_modal'],
            'metrics': ['synergy_score', 'immune_activation', 'resistance_overcoming', 'survival_benefit'],
            'search_pattern': f'{{approach}} {{disease}} {{year_range}} combination therapy'
        }
    }
    
    # Cross-cutting pattern recognition
    synthesis_rules = [
        'Compare local vs systemic delivery efficacy across all modalities',
        'Identify neoadjuvant vs adjuvant timing advantages',
        'Map single-modality limitations and resistance mechanisms',
        'Catalog most promising combination strategies',
        'Track regulatory milestones (FDA breakthrough, fast track, approval)',
        'Assess which approaches address which key challenges'
    ]
    
    return {'domains': domains, 'synthesis_rules': synthesis_rules}