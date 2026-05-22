class GBMTreatmentKnowledge:
    """Captured knowledge from AMY investigation on GBM innovative treatments."""
    
    TREATMENT_TIERS = {
        'Tier1_Highest_Combinatorial_Value': [
            'oncolytic_viruses_DNX2401_PVSRIPO',
            'focused_ultrasound_BBB_disruption',
            'CAR_T_with_BBB_enhancement'
        ],
        'Tier2_Moderate_Evidence': [
            'nanoparticle_delivery_systems',
            'checkpoint_inhibitors_combined',
            'neoantigen_vaccines'
        ],
        'Tier3_Emerging': [
            'cancer_stem_cell_CD133_targeting',
            'standalone_checkpoint_inhibitors'
        ]
    }
    
    COMBINATION_RATIONALE = {
        'BBB_penetration': 'focused_ultrasound_or_nanoparticles',
        'immunosuppression_reversal': 'oncolytic_viruses_convert_cold_to_hot',
        'heterogeneity_addressing': 'multi_antigen_CAR_T_or_sequential_viruses',
        'optimal_approach': 'sequential_staged_therapy_addressing_all_three_simultaneously'
    }
    
    KEY_CHALLENGES = [
        'BBB_limits_drug_delivery',
        'tumor_heterogeneity_drives_resistance',
        'immunosuppressive_microenvironment_neutralizes_immunotherapy',
        'cancer_stem_cells_drive_recurrent_tumors'
    ]
    
    RESISTANCE_MECHANISMS = {
        'oncolytic_virus_neutralization': 'pre_existing_antibodies_and_rapid_immune_clearance',
        'CAR_T_exhaustion': 'immunosuppressive_TME_and_antigen_escape',
        'checkpoint_inhibitor_failure': 'low_tumor_mutational_burden_and_T_cell_exclusion'
    }
    
    AMY_PROTOCOL_SEQUENTIAL = [
        'Stage1_BBB_Disruption: focused_ultrasound_to_enable_drug_penetration',
        'Stage2_Immune_Priming: oncolytic_virus_to_convert_immunosuppressive_TME',
        'Stage3_Targeted_Kill: CAR_T_or_nanoparticle_delivered_chemotherapy',
        'Stage4_Suppression: checkpoint_inhibitors_to_sustain_immune_response',
        'Stage5_Stem_Cell_Eradication: CD133_targeted_therapy_for_durable_response'
    ]