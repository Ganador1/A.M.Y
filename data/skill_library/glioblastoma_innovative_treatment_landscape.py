def get_gbm_treatment_landscape(query_type='overview'):
    knowledge = {
        'immunotherapy': {
            'CAR-T': 'Local delivery (intracavitary/intraventricular) required; targets IL13Rα2, EGFRvIII, HER2; transient responses observed; manufacturing challenges',
            'DCVax-L': 'Phase III positive signal; median OS 19.3mo newly diagnosed, 23.4mo overall; FDA breakthrough designation pending; most robust immunotherapy result',
            'checkpoint_inhibators': 'Monotherapy ineffective (CheckMate-143 negative); neoadjuvant anti-PD-1 shows improved survival (OpDivNeuro); combination strategies needed',
            'bispecific_antibodies': 'Emerging approach; bispecific T-cell engagers targeting EGFRvIII; early trials ongoing'
        },
        'oncolytic_viruses': {
            'DNX-2401_adenovirus': 'Phase I showed 20% 3-year survivors; Phase II with pembrolizumab ongoing',
            'G207_HSV': 'Phase I pediatric showed safety; adult trials ongoing',
            'PVSRIPO_poliovirus': 'Phase I showed 21% 3-year survival; Phase II not meeting primary endpoint',
            'key_limitation': 'Delivery, immune clearance, manufacturing complexity'
        },
        'delivery_systems': {
            'nanoparticles': 'Liposomal/magnetic nanoparticles for targeted delivery; early-phase trials',
            'CED': 'Convection-enhanced delivery bypasses BBB; phase III PRECISE trial negative but methodology criticized; improved catheter design ongoing',
            'BBB_disruption': 'Focused ultrasound (ExAblate) opening BBB for enhanced drug delivery; phase II trials',
            'local_implants': 'Gliadel wafers (carmustine); limited efficacy; new formulations in development'
        },
        'targeted_therapy': {
            'EGFR_inhibitors': 'Amivantamab (bispecific EGFR/MET) showing early activity; depatuxizumab mafodotin failed phase III',
            'IDH_mutations': 'Vorasidenib FDA-approved 2024 for IDH-mutant grade 2 astrocytoma/oligodendroglioma; not for IDH-wildtype GBM',
            'BRAF': 'Dabrafenib+trametinib for BRAF V600E mutant gliomas',
            'metabolic': 'IDH1/2, glutaminase, metabolic reprogramming targets under investigation'
        },
        'combination_strategies': {
            'TME_modulation': 'CSF1R inhibitors, TGF-β blockade, macrophage reprogramming',
            'synthetic_lethality': 'PARP inhibitors + temozolomide; ATR inhibitors for DNA repair defects',
            'radiosensitizers': 'IDH1 inhibitor + radiation; PARP inhibitors as radiosensitizers',
            'paradigm': 'Multi-modal combinations addressing heterogeneity and adaptive resistance are essential'
        },
        'key_principles': [
            'Local delivery > systemic delivery for BBB penetration',
            'Single modality insufficient due to tumor heterogeneity',
            'Neoadjuvant immunotherapy timing improves outcomes',
            'Tumor microenvironment immunosuppression must be addressed',
            'Biomarker-driven patient selection is critical'
        ]
    }
    if query_type == 'overview':
        return knowledge
    elif query_type in knowledge:
        return knowledge[query_type]
    else:
        return f'Available categories: {list(knowledge.keys())}'