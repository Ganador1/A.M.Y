def gbm_innovative_treatments_synthesis(query_topic=None):
    """Returns synthesized GBM innovative treatment knowledge.
    
    TIER 1 - HIGHEST CONFIDENCE FINDINGS:
    - DCVax-L (dendritic cell vaccine): Most robust positive signal in GBM immunotherapy.
      Phase III trial: median OS 23.4 months (vs ~15 mo standard). 5-year survival 13% (vs 5.7% historical).
      FDA regulatory pathway advancing. Not yet FDA-approved but most promising immunotherapy.
    - Neoadjuvant anti-PD-1 (nivolumab): Perioperative timing dramatically improves outcomes.
      UCLA study: median OS not reached vs 14.2 mo adjuvant-only. Cloughesy et al. landmark finding.
    - CheckMate-143: Nivolumab vs bevacizumab in recurrent GBM - NEGATIVE for primary endpoint OS.
      Monotherapy checkpoint inhibitors alone insufficient for GBM.
    - Vorasidenib: FDA-approved July 2024 for IDH-mutant grade 2 astrocytoma/oligodendroglioma (INDIGO trial).
      Not for IDH-wildtype GBM but validates IDH-targeting in glioma.
    
    TIER 2 - PROMISING WITH CAVEATS:
    - CAR-T cell therapy: IL13Rα2, EGFRvIII, HER2 targets. Local delivery (intraventricular, intratumoral)
      shows dramatic but transient responses. Challenge: antigen escape, T-cell exhaustion, manufacturing.
    - Oncolytic viruses: DNX-2401 (adenovirus) phase I 11.7 mo median OS. PVSRIPO (poliovirus) phase I
      21.1 mo median OS but phase III halted. HSV-1 G207 pediatric trial promising.
    - Convection-enhanced delivery (CED): Superior local drug concentrations. FDA-approved RNF device.
      Challenge: coverage monitoring, catheter placement.
    - Nanoparticle delivery: PEGylated liposomes, polymeric NPs crossing disrupted BBB. Preclinical promise,
      limited clinical data.
    
    TIER 3 - EMERGING/EARLY STAGE:
    - Bispecific antibodies (EGFRvIII×CD3): Early clinical evaluation.
    - mRNA vaccines: Personalized neoantigen approach, preclinical/early phase.
    - CRISPR gene therapy: Preclinical stage for GBM.
    - Metabolic targeting (IDH, glutaminase, oxidative phosphorylation): Early trials.
    - Tumor treating fields + immunotherapy: Rationale strong, trials ongoing.
    
    CROSS-CUTTING PRINCIPLES:
    1. Local delivery > systemic delivery for BBB penetration
    2. Combination therapy essential due to tumor heterogeneity and adaptive resistance
    3. Neoadjuvant/perioperative timing of immunotherapy superior to adjuvant-only
    4. Patient selection (biomarker-driven) critical - IDH status, MGMT methylation, EGFR amplification
    5. TME modulation (reducing immunosuppression) necessary complement to immunotherapy
    6. Recurrent GBM remains hardest target; newly diagnosed shows more promise
    
    KEY ONGOING TRIALS (2024-2025):
    - DCVax-L regulatory submission pathway
    - SurVaxM phase II/III (survivin-targeting vaccine)
    - Multiple CAR-T trials with local delivery strategies
    - Neoadjuvant PD-1 + TMZ + radiation combinations
    - PARP inhibitor (BGB-290) radiosensitizer trials
    """
    
    knowledge_base = {
        'immunotherapy': {
            'car_t': {'targets': ['IL13Rα2', 'EGFRvIII', 'HER2', 'B7-H3'], 
                      'key_finding': 'Local delivery essential; transient responses; antigen escape challenge',
                      'best_result': 'Intraventricular IL13Rα2 CAR-T: dramatic transient responses'},
            'dcvax_l': {'phase': 'III completed', 'median_os': '23.4 months', 
                        '5yr_survival': '13% vs 5.7% historical', 'fda_status': 'Regulatory pathway advancing'},
            'checkpoint_inhibitors': {'monotherapy': 'Negative (CheckMate-143)',
                                      'neoadjuvant': 'Promising (Cloughesy et al.)',
                                      'key_insight': 'Timing and combination critical'}},
        'oncolytic_viruses': {
            'dnx_2401': {'type': 'Adenovirus', 'phase': 'I/II', 'median_os': '11.7 months'},
            'pvsripo': {'type': 'Poliovirus', 'phase_I_median_os': '21.1 months', 'phase_III': 'Halted'},
            'g207': {'type': 'HSV-1', 'promising_in': 'Pediatric GBM'}},
        'drug_delivery': {
            'ced': {'status': 'FDA-approved device (RNF)', 'advantage': 'Bypasses BBB', 'challenge': 'Coverage monitoring'},
            'nanoparticles': {'status': 'Preclinical/early clinical', 'advantage': 'Tunable pharmacokinetics'},
            'bbb_disruption': {'methods': ['Focused ultrasound', 'osmotic (mannitol)', 'receptor-mediated']}},
        'targeted_therapy': {
            'vorasidenib': {'status': 'FDA-approved July 2024', 'indication': 'IDH-mutant grade 2 glioma'},
            'egfr_inhibitors': {'challenge': 'Resistance via alternative pathways', 'approaches': ['amivantamab bispecific', 'depatuxizumab mafodotin']},
            'braf': {'dabrafenib_trametinib': 'Active in BRAF-mutant gliomas'}},
        'combination_strategies': {
            'principles': ['Local delivery preferred', 'Multi-modal required', 'Neoadjuvant timing superior', 'TME modulation essential'],
            'synthetic_lethality': ['PARP + radiation', 'IDH + DNA damage'],
            'radiosensitizers': ['PARP inhibitors', 'IDH inhibitors']}
    }
    
    if query_topic and query_topic in knowledge_base:
        return knowledge_base[query_topic]
    return knowledge_base
