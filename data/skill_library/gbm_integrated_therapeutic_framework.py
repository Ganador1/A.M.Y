GBM_INTEGRATED_FRAMEWORK = {
  'phase_1_priming': {
    'duration': 'weeks_1-3',
    'objective': 'BBB_disruption_and_immune_priming',
    'modalities': [
      'focused_ultrasound_BBB_opening_24h_before_drug_delivery',
      'oncolytic_virus_DNX2401_or_PVSRIPO_tumor_injection',
      'anti_seizure_perampanel_blocking_AMA_receptor_glioma_synapse'
    ],
    'biomarker_gate': 'MRI_confirmation_BBB_disruption + viral_replication_cytokine_rise',
    'synergy_rationale': 'BBB_opening_enables_viral_and_drug_penetration; virus_converts_cold_to_hot_tumor; synapse_disruption_blocks_invasion_signal'
  },
  'phase_2_metabolic_assault': {
    'duration': 'weeks_2-6',
    'objective': 'exploit_metabolic_vulnerabilities_and_induce_ferroptosis',
    'modalities': [
      'glutaminase_inhibitor_telaglenastat_block_GSC_fuel',
      'GPX4_inhibitor_or_SLC7A11_targetor_induce_ferroptosis',
      'repurposed_metformin_disrupt_oxidative_phosphorylation',
      'nanoparticle_delivery_of_siRNA_against_metabolic_enzymes'
    ],
    'biomarker_gate': 'metabolic_signature_shift_on_MR_spectroscopy + decreasing_circulating_GSC_markers',
    'synergy_rationale': 'metabolic_stress_upregulates_ferroptosis_susceptibility; GSCs_depend_on_glutamine_and_OXPHOS; dual_hit_prevents_metabolic_escape'
  },
  'phase_3_immune_activation': {
    'duration': 'weeks_4-12',
    'objective': 'sustain_adaptive_immune_response_against_tumor',
    'modalities': [
      'bispecific_T-cell_engager_targeting_EGFRvIII_and_CD3',
      'anti_PD1_checkpoint_inhibitor_nivolumab',
      'personalized_mRNA_neoantigen_vaccine_post_oncolytic_priming',
      'gut_microbiome_optimization_prebiotic_probiotic_to_enhance_ICI_response'
    ],
    'biomarker_gate': 'T_cell_infiltration_on_biopsy + ctDNA_clearance + microbiome_diversity_index',
    'synergy_rationale': 'oncolytic_virus_primed_tumor_now_receptive_to_ICI; bispecific_engagers_recruit_T_cells; vaccine_sustains_long_term_memory; microbiome_enhances_systemic_immunity'
  },
  'phase_4_resistance_prevention': {
    'duration': 'weeks_8_indefinite',
    'objective': 'prevent_adaptive_resistance_and_recurrence',
    'modalities': [
      'EZH2_inhibitor_tazemetostat_block_epigenetic_escape',
      'BET_bromodomain_inhibitor_suppress_stemness_programs',
      'exosome_interception_therapy_block_paracrine_resistance_signaling',
      'tumor_treating_fields_TTF_disrupt_mitosis_continuously',
      'organoid_avatar_testing_for_emerging_resistance'
    ],
    'biomarker_gate': 'ctDNA_molecular_residual_disease_monitoring + serial_organoid_drug_sensitivity',
    'synergy_rationale': 'epigenetic_reprogramming_prevents_phenotypic_switching; exosome_interception_blocks_microenvironment_reprogramming; TTF_adds_continuous_pressure; organoid_avatar_enables_real_time_adaptation'
  },
  'adaptive_scheduling': {
    'AI_framework': 'Bayesian_adaptive_trial_design_with_reinforcement_learning_optimization',
    'feedback_biomarkers': [
      'circulating_tumor_DNA_ctDNA_for_molecular_residual_disease',
      'MR_spectroscopy_metabolic_signatures_for_tumor_metabolism',
      'immune_profiling_T_cell_diversity_and_exhaustion_markers',
      'extracellular_vesicle_content_for_emerging_resistance_pathways',
      'gut_microbiome_diversity_for_immunotherapy_response_prediction'
    ],
    'decision_points': 'every_2_weeks_biomarker_panel_triggers_protocol_adjustment',
    'patient_stratification': 'MGMT_methylation + IDH_status + EGFRvIII + MGMT_methylation + immune_hot_cold_classification'
  },
  'key_principles': [
    'temporal_sequencing_matters_priming_before_assault_before_activation',
    'each_modality_creates_vulnerabilities_the_next_exploits',
    'resistance_is_inevitable_plan_for_it_proactively',
    'biomarker_feedback_enables_real_time_adaptation',
    'glioma_stem_cells_are_the_ultimate_target_for_cure'
  ]
}