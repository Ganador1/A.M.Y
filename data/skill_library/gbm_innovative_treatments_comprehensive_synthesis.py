def synthesize_gbm_treatment_landscape(patient_profile=None):
    """Comprehensive GBM innovative treatment knowledge base and recommendation engine.
    
    Key Findings:
    1. IMMUNOTHERAPY:
       - DCVax-L: Most robust positive signal (median OS 23.4mo vs 16.5mo historical)
       - CAR-T: Local intraventricular delivery (IL13Rα2, EGFRvIII targets) shows responses
       - Checkpoint inhibitors: Monotherapy limited (CheckMate 143 negative); neoadjuvant anti-PD-1 shows improved OS
    2. ONCOLYTIC VIRUSES:
       - DNX-2401 (adenovirus): Phase I/II shows durable responses in recurrent GBM
       - PVSRIPO (poliovirus): Phase I showed extended survival but phase III halted
       - HSV-G47: Ongoing trials in Japan with promising early data
    3. DRUG DELIVERY:
       - CED: Superior local drug concentrations, multiple phase I/II trials
       - Focused ultrasound (MRgFUS): Non-invasive BBB opening, enhancing chemo/immunotherapy delivery
       - Nanoparticles: Preclinical promise, early clinical translation
    4. TARGETED THERAPY:
       - Vorasidenib: FDA-approved Aug 2024 for IDH-mutant glioma (INDIGO trial)
       - Amivantamab: EGFRvIII bispecific, early trials in GBM
       - BRAF: Dabrafenib/trametinib for BRAF V600E mutant GBM
    5. COMBINATION/EMERGING:
       - Synthetic lethality: PARP inhibitors + temozolomide/radiation
       - Radiosensitizers: Various approaches in trials
       - mRNA vaccines, bispecific antibodies: Early development
    
    Cross-cutting principles:
    - Local delivery consistently outperforms systemic for BBB penetration
    - Single-modality approaches insufficient due to heterogeneity
    - Neoadjuvant/perioperative immunotherapy timing shows superior outcomes
    - Multi-modal combinations (local+systemic, immuno+targeted) most promising
    """
    
    treatment_landscape = {
        'immunotherapy': {
            'DCVax-L': {'status': 'Phase III positive', 'median_os': '23.4 months', 'evidence_level': 'Strong'},
            'CAR-T_local': {'status': 'Phase I/II', 'targets': ['IL13Rα2', 'EGFRvIII'], 'delivery': 'intraventricular', 'evidence_level': 'Moderate'},
            'neoadjuvant_antiPD1': {'status': 'Phase II', 'os_benefit': 'significant', 'evidence_level': 'Moderate'},
            'checkpoint_monotherapy': {'status': 'Negative (CheckMate 143)', 'evidence_level': 'Strong'}
        },
        'oncolytic_viruses': {
            'DNX-2401': {'status': 'Phase I/II', 'responses': 'durable in subset', 'evidence_level': 'Moderate'},
            'PVSRIPO': {'status': 'Phase III halted', 'evidence_level': 'Moderate'},
            'G47Δ_HSV': {'status': 'Phase I/II Japan', 'evidence_level': 'Low-Moderate'}
        },
        'drug_delivery': {
            'CED': {'advantage': 'high local concentration', 'status': 'Phase I/II multiple agents', 'evidence_level': 'Moderate'},
            'MRgFUS': {'advantage': 'non-invasive BBB opening', 'status': 'Phase I/II', 'evidence_level': 'Low-Moderate'},
            'nanoparticles': {'advantage': 'targeted delivery', 'status': 'Preclinical-early clinical', 'evidence_level': 'Low'}
        },
        'targeted_therapy': {
            'vorasidenib_IDH': {'status': 'FDA approved Aug 2024', 'indication': 'IDH-mutant glioma', 'evidence_level': 'Strong'},
            'amivantamab_EGFRvIII': {'status': 'Early trials', 'evidence_level': 'Low'},
            'dabrafenib_trametinib_BRAF': {'status': 'Case series/Phase II', 'evidence_level': 'Low-Moderate'}
        },
        'combination_emerging': {
            'PARP_TMZ_radiation': {'status': 'Phase I/II', 'evidence_level': 'Low-Moderate'},
            'mRNA_vaccines': {'status': 'Early development', 'evidence_level': 'Low'},
            'bispecific_antibodies': {'status': 'Early development', 'evidence_level': 'Low'}
        }
    }
    
    if patient_profile:
        # Return personalized recommendations based on biomarker profile
        recommendations = []
        if patient_profile.get('IDH_mutation'):
            recommendations.append(('vorasidenib', 'FDA-approved, Strong evidence'))
        if patient_profile.get('MGMT_methylation'):
            recommendations.append(('temozolomide + PARP inhibitor', 'Synthetic lethality approach'))
        if patient_profile.get('newly_diagnosed'):
            recommendations.append(('DCVax-L + standard chemoradiation', 'Phase III evidence'))
            recommendations.append(('Neoadjuvant anti-PD-1', 'Perioperative timing advantage'))
        if patient_profile.get('recurrent'):
            recommendations.append(('Local CAR-T or oncolytic virus', 'Local delivery advantage'))
            recommendations.append(('CED-delivered agents', 'BBB bypass'))
        return recommendations
    
    return treatment_landscape