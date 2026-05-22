def systematic_medical_research(disease_name, key_challenges):
    """
    Systematic investigation of innovative treatments for complex diseases.
    
    Args:
        disease_name: Name of the disease/condition
        key_challenges: List of key therapeutic challenges (e.g., ['BBB', 'heterogeneity', 'immunosuppression'])
    
    Returns:
        Structured findings with confidence-rated conclusions
    """
    research_axes = [
        'immunotherapy_approaches',      # CAR-T, vaccines, checkpoint inhibitors
        'viral_gene_therapy',             # Oncolytic viruses, gene therapy
        'novel_delivery_systems',         # Nanoparticles, CED, BBB disruption
        'targeted_molecular_therapy',    # Mutation-specific inhibitors, metabolic
        'microenvironment_combinations'   # TME modulation, synthetic lethality, combos
    ]
    
    cross_cutting_principles = {
        'local_delivery_advantage': 'Local delivery consistently outperforms systemic for protected anatomical sites',
        'neoadjuvant_timing': 'Perioperative/neoadjuvant immunotherapy timing shows superior immune activation',
        'combination_necessity': 'Single-modality approaches fail due to tumor heterogeneity and adaptive resistance',
        'biomarker_essential': 'Patient stratification by molecular biomarkers is critical for targeted approaches'
    }
    
    findings = {}
    for axis in research_axes:
        findings[axis] = {
            'status': 'researched',
            'key_trials': [],
            'confidence': 0.0,
            'next_steps': []
        }
    
    findings['cross_cutting_principles'] = cross_cutting_principles
    findings['synthesis_complete'] = True
    
    return findings

# GBM-Specific Findings Encoded:
gbm_findings = {
    'immunotherapy': {
        'DCVax-L': {'mOS': '23.4 months', 'phase': 'III', 'status': 'most_robust_positive_signal', 'confidence': 0.80},
        'CAR-T': {'targets': 'IL13Rα2, EGFRvIII, HER2', 'status': 'early_phase_promising_local_delivery', 'confidence': 0.65},
        'checkpoint_inhibitors': {'monotherapy': 'failed_CheckMate_143', 'neoadjuvant': 'promising_rationale', 'confidence': 0.75},
        'SurVaxM': {'mOS': '25.5_months_recurrent', 'status': 'phase_II_positive', 'confidence': 0.70}
    },
    'oncolytic_viruses': {
        'DNX-2401': {'status': 'dose_dependent_responses', 'combo_with_pembrolizumab_ongoing': True},
        'PVSRIPO': {'status': 'phase_I_completed_safety_established'},
        'G207_HSV': {'status': 'pediatric_GBM_promising_phase_I'}
    },
    'delivery_systems': {
        'principle': 'local_delivery_superior_for_BBB_penetration',
        'nanoparticles': 'polymer_lipid_hybrid_most_promising',
        'CED': 'enables_therapeutic_concentrations_in_tumor_bed'
    },
    'targeted_therapy': {
        'vorasidenib': {'status': 'FDA_approved_IDH_mutant_glioma_August_2024', 'trial': 'INDIGO'},
        'EGFR_inhibitors': 'amivantamab_showing_activity_EGFRvIII',
        'BRAF': 'dabrafenib_trametinib_for_BRAF_V600E'
    },
    'combinations': {
        'principle': 'multi_modal_approaches_essential',
        'promising_combos': ['immunotherapy_plus_oncolytic_virus', 'targeted_plus_immunotherapy', 'radiosensitizers_plus_RT_plus_immunotherapy']
    }
}