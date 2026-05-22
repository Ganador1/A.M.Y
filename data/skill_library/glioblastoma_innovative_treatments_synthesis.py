def synthesize_gbm_treatments(query_type='overview'):
    """
    Comprehensive GBM innovative treatments knowledge base.
    
    Parameters:
        query_type: 'overview', 'immunotherapy', 'oncolytic_virus', 
                    'drug_delivery', 'targeted_therapy', 'combinations',
                    'clinical_trials', 'regulatory_status', 'key_patterns'
    
    Returns:
        Structured synthesis of GBM treatment research findings
    """
    knowledge = {
        'overview': {
            'standard_of_care': 'Stupp protocol (surgery + RT + temozolomide)',
            'median_os_standard': '~15 months',
            'key_challenges': [
                'Blood-brain barrier limits systemic drug delivery',
                'Intratumoral heterogeneity drives resistance',
                'Immunosuppressive TME inhibits immune therapies',
                'Near-certain recurrence within 6-7 months'
            ],
            'paradigm_shifts': [
                'Local delivery outperforms systemic for BBB penetration',
                'Neoadjuvant timing critical for immunotherapy efficacy',
                'Multi-modal combinations required for durable responses',
                'Personalized approaches based on molecular profiling'
            ]
        },
        'immunotherapy': {
            'car_t': {
                'targets': ['IL13Rα2', 'EGFRvIII', 'GD2', 'B7-H3'],
                'key_finding': 'Locoregional delivery shows 2-10x survival benefit vs systemic',
                'best_results': 'IL13Rα2 CAR-T with IL-15 armoring in phase I',
                'challenge': 'Tumor antigen escape and heterogeneity'
            },
            'dcvax_l': {
                'status': 'Phase III completed (ACT IV trial)',
                'median_os': '23.4 months (strongest positive signal in GBM immunotherapy)',
                'mechanism': 'Autologous dendritic cell vaccine pulsed with tumor lysate',
                'regulatory': 'Seeking FDA pathway for approval'
            },
            'checkpoint_inhibitors': {
                'monotherapy': 'Failed in CheckMate 143 (nivolumab vs bevacizumab)',
                'neoadjuvant_approach': 'Anti-PD-1 given before surgery shows 2.2x OS improvement',
                'mechanism': 'Priming immune response during antigen release from surgery',
                'ongoing': 'Multiple trials testing neoadjuvant + adjuvant combination'
            },
            'bispecific_antibodies': {
                'targets': 'EGFRvIII×CD3, IL13Rα2×CD3',
                'advantage': 'Off-the-shelf, dual-targeting potential',
                'status': 'Early clinical development'
            }
        },
        'oncolytic_virus': {
            'dnx_2401': {
                'type': 'Oncolytic adenovirus (Delta-24-RGD)',
                'mechanism': 'Replicates in Rb-deficient tumor cells, induces immunogenic cell death',
                'results': 'Phase I: 20% 3-year survival in recurrent GBM',
                'combination': 'With pembrolizumab showing enhanced responses',
                'status': 'Phase II ongoing'
            },
            'pvsripo': {
                'type': 'Attenuated poliovirus recombinant',
                'mechanism': 'Targets CD155 (Nectin-1) overexpressed on GBM',
                'results': 'Phase I: 21% 3-year survival, durable responders',
                'status': 'Phase II (GBM-001) ongoing'
            },
            'g207': {
                'type': 'Genetically modified HSV-1',
                'mechanism': 'Deletion of ICP34.5 and ICP6 for tumor-selective replication',
                'results': 'Phase I in pediatric brain tumors, adult GBM trials',
                'safety': 'Excellent safety profile'
            }
        },
        'drug_delivery': {
            'ced': {
                'name': 'Convection-Enhanced Delivery',
                'advantage': 'Bypasses BBB, achieves high local concentrations',
                'applications': 'Gene therapy vectors, chemotherapeutics, immunotoxins',
                'challenge': 'Distribution heterogeneity, catheter placement accuracy'
            },
            'focused_ultrasound': {
                'name': 'MRI-guided Focused Ultrasound (MRgFUS)',
                'mechanism': 'Transient BBB disruption with microbubbles',
                'advantage': 'Non-invasive, targeted, reversible BBB opening',
                'results': 'Enhanced delivery of anti-PD-1, trastuzumab, doxorubicin',
                'status': 'Early clinical trials showing safety and feasibility'
            },
            'nanoparticles': {
                'types': 'Lipid, polymeric, magnetic, dendrimer-based',
                'advantage': '5-10x CNS concentration vs systemic delivery',
                'surface_modification': 'PEGylation, transferrin/EGF ligand conjugation',
                'challenge': 'Scale-up, regulatory pathway, biodistribution control'
            }
        },
        'targeted_therapy': {
            'idh_mutant': {
                'drug': 'Vorasidenib (IDH1/2 inhibitor)',
                'status': 'FDA approved August 2024 (first targeted therapy for glioma)',
                'trial': 'INDIGO phase III: significant PFS improvement',
                'note': 'Only ~5-10% of primary GBM are IDH-mutant; more relevant for lower-grade gliomas'
            },
            'egfr': {
                'targets': ['EGFRvIII (30-50% of GBM)', 'EGFR amplification (50% of GBM)'],
                'agents': 'Amivantamab (bispecific EGFR/MET), depatuxizumab mafodotin (ADC)',
                'challenge': 'Resistance via EGFRvIII-negative clones, compensatory pathways',
                'approach': 'Combination with immune therapies showing promise'
            },
            'braf_v600e': {
                'agents': 'Dabrafenib + trametinib (BRAF/MEK inhibition)',
                'status': 'FDA approved for BRAF V600E solid tumors including GBM',
                'prevalence': '~2-3% of GBM',
                'results': 'Response rates 25-33% in GBM'
            },
            'parp_inhibitors': {
                'agents': 'BGB-290 (niraparib), olaparib, veliparib',
                'mechanism': 'Synthetic lethality in HR-deficient tumors; radiosensitization',
                'approach': 'Combination with radiation to enhance DNA damage',
                'status': 'Phase I/II trials ongoing'
            },
            'metabolic': {
                'targets': ['IDH1/2', 'LDH-A', 'glutaminase', 'oxidative phosphorylation'],
                'rationale': 'GBM metabolic reprogramming creates vulnerabilities',
                'status': 'Early-phase clinical investigation'
            }
        },
        'combinations': {
            'key_principle': 'Single-modality approaches fail due to tumor heterogeneity and adaptive resistance',
            'promising_combos': [
                'Neoadjuvant anti-PD-1 + surgery + adjuvant anti-PD-1',
                'Oncolytic virus + checkpoint inhibitor (virus primes immune response)',
                'CAR-T + checkpoint inhibitor (prevent T-cell exhaustion)',
                'PARP inhibitor + radiation (synthetic lethality + radiosensitization)',
                'Focused ultrasound BBB disruption + systemic immunotherapy',
                'Multi-antigen CAR-T (address heterogeneity)'
            ],
            'tme_modulation': [
                'CSF-1R inhibitors to reprogram macrophages',
                'TGF-β blockade to reduce immunosuppression',
                'STING agonists to activate innate immunity'
            ]
        },
        'key_patterns': {
            'local_over_systemic': 'Local/locoregional delivery consistently outperforms systemic delivery for BBB penetration',
            'neoadjuvant_timing': 'Perioperative immunotherapy timing shows superior outcomes (antigen release during surgery primes immune response)',
            'combination_necessity': 'Single-modality approaches show limited efficacy due to tumor heterogeneity and adaptive resistance',
            'heterogeneity_challenge': 'Molecular and spatial heterogeneity requires multi-target or adaptive approaches',
            'immunosuppressive_tme': 'TME modulation essential for immunotherapy efficacy',
            'personalization': 'Molecular profiling (IDH, MGMT, EGFR, BRAF status) guides treatment selection'
        },
        'regulatory_status_2024': {
            'vorasidenib': 'FDA approved Aug 2024 for IDH-mutant glioma',
            'dabrafenib_trametinib': 'FDA approved for BRAF V600E solid tumors including GBM',
            'dcvax_l': 'Phase III positive, seeking regulatory pathway',
            'dnx_2401': 'Phase II ongoing',
            'pvsripo': 'Phase II ongoing',
            'car_t_gbm': 'Multiple phase I trials, no regulatory approval yet',
            'focused_ultrasound': 'Early clinical trials for BBB disruption'
        }
    }
    
    if query_type in knowledge:
        return knowledge[query_type]
    return knowledge