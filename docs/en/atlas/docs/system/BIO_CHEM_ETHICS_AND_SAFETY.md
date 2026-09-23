> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="controles-éticos-y-de-seguridad-para-módulos-de-biología-y-química"></a>
# Ethical and Safety Controls for Biology and Chemistry Modules

This annex complements `ETHICS_AND_SAFETY.md` by focusing on domains with higher potential for dual-use or biosecurity risk: computational biology, genomics, computational chemistry, molecular dynamics, and metabolic networks.

<a id="1-dominios-y-riesgos-específicos"></a>
## 1. Domains and Specific Risks
| Domain | Main Risks | Base Classification | Examples of Abuse | Primary Mitigation Measure |
|---------|---------------------|--------------------|-------------------|----------------------------|
| computational_biology | Neural reconstruction, ecosystem modeling | High | Models extrapolated to ecosystem manipulation | Scale limitation, human review |
| genomics | Sensitive data, re-identification | Very High | Infer identity or private variants | Anonymization, irreversible hashing |
| metabolic_networks | Optimization of biosynthetic pathways | Very High | Unauthorized biochemical design | Require signed legitimate purpose |
| neuro_simulation | Massive resource models | High | Use for training adversarial schemes | GPU quotas and objective validation |
| computational_chemistry | Molecular properties | Medium-High | Triaging sensitive molecules | Automated screening limit |
| quantum_chemistry | Precision energies | High | Accelerated design of sensitive materials | Restriction of advanced basis sets |
| molecular_dynamics | Prepare complex systems | High | Simulation of viral replication (risk) | Pattern exclusion taxonomy |
| systems_biology | Comprehensive modeling | Very High | Multi-pathway manipulation scenarios | Multiple signature (4-eyes) |
| synthetic_biology | Construct design | Critical | Construction/biological agent | Default block + whitelist |
| biosecurity_assessment | Vulnerability assessment | Critical | Identification of biological attack vectors | Isolation + reinforced logging |

<a id="2-política-yaml-pesos-de-dominio"></a>
## 2. YAML Policy (Domain Weights)
The weights added in `config/ethics_policy.yaml` raise to HIGH/CRITICAL levels faster for sensitive domains. Adjust under governance: changes require dual approval (Lead Scientist + Compliance Officer).

<a id="3-escalamiento-de-controles"></a>
## 3. Escalation of Controls
| Risk Level | Bio/Chem Requirement | Additional Controls |
|--------------|-----------------------|-----------------------|
| LOW | Trivial analytical operations | Standard logging |
| MEDIUM | Basic descriptors, alignments | Parameter limits, reduced sampling |
| HIGH | Broad molecular screening, MD simulation > short | Simple signature + justification ≥15 chars |
| CRITICAL | Sensitive genomics, synthetic_biology, optimized network design | Dual signature, possible veto, daily audit |

<a id="4-patrón-de-integración-ethics-gate"></a>
## 4. Ethics Gate Integration Pattern
Recommended pseudocode before executing a sensitive task:
```python
from app.ethics_gate import EthicsGate, ExperimentRequest

gate = EthicsGate(policy_path="config/ethics_policy.yaml")

req = ExperimentRequest(
    domain="genomics",
    description="Análisis regulatorio de red génica anonimizada",
    resources={"gpu_hours": 2, "memory_gb": 32},
    data_sensitivity="high",
    declared_intent="Investigar regulación epigenética en cohortes públicas",
    justification="Proyecto aprobado IRB #2025-AG-17 con anonimización completa",
    justification_signature="investigadorA|2025-09-09"
)
decision = gate.evaluate(req, auto_anchor=True)
if not decision.allowed:
    raise PermissionError(f"Bloqueado: {decision.reason}")
```

<a id="5-límites-operacionales-recomendados"></a>
## 5. Recommended Operational Limits
| Parameter | Suggested Hard Limit | Rationale |
|-----------|-----------------------|----------|
| num_neurons (Brian2) | ≤ 50k | Avoid resource abuse / massive scaling without review |
| genome sequence length analysis | ≤ 3e7 bases per job | Avoid unapproved complete human datasets |
| conformers per molecule | ≤ 100 | Limit intensive search potential massive screening |
| quantum basis set | Restrict to sto-3g / 6-31g* in standard mode | Avoid unsupervised high-precision calculations |
| MD box atoms | ≤ 150k | Cost control and attack surface |
| metabolic reactions (model) | ≤ 5000 | Identify suspicious expansions |

Exceeding hard limit → escalate to CRITICAL and require dual signature.

<a id="6-patrón-de-detección-de-uso-dual-heurística"></a>
## 6. Dual-Use Detection Pattern (Heuristic)
Combined indicators (if ≥2 → escalate to HIGH minimum):
1. Keywords: "optimize biosynthetic pathway", "synthetic construct", "viral assembly".
2. Request parameters above historical 95 percentile.
3. Sequences with length > partial human genomic threshold.
4. Repetition of similar jobs (iterative screening) in <24h.
5. Mix of domains (genomics + synthetic_biology) in the same session.

<a id="7-métricas-adicionales-específicas"></a>
## 7. Additional Specific Metrics
| Metric | Description | Action |
|---------|-------------|--------|
| bio_high_jobs_total | HIGH/CRITICAL bio/chem jobs | Review weekly |
| dual_use_flags_total | Heuristic detections | Immediate audit |
| synthetic_blocked_total | synthetic_biology blocks | Confirm legitimacy |
| md_large_box_attempts | Attempts to exceed atom limit | Adjust policy |

<a id="8-reglas-de-sanitización"></a>
## 8. Sanitization Rules
- Never store raw sequences if they belong to identifiable subjects.
- SHA-256 hash + truncation (first 12 bytes) for non-reversible tracking.
- Remove geographic / demographic metadata before analysis.

<a id="9-checklist-pre-ejecución-crítica"></a>
## 9. CRITICAL Pre-Execution Checklist
- [ ] Justification ≥ 50 characters
- [ ] Dual signature registered
- [ ] Request hash anchored
- [ ] IRB / Ethics Committee validation (reference ID)
- [ ] Parameters within approved limits
- [ ] Data deletion/retention plan

<a id="10-futuras-extensiones"></a>
## 10. Future Extensions
| Idea | Benefit |
|------|-----------|
| Prohibited sequence scanner (restrictive BLAST DB) | Automatic blocking of sensitive patterns |
| ML textual risk classifier | Reduction of false negatives in intent |
| Multi-party signature (threshold signatures) | Greater audit robustness |
| External WORM registry | Non-repudiable evidence |

<a id="11-declaración"></a>
## 11. Statement
The capabilities described here are for legitimate research purposes. Any attempt at misuse (biosecurity, illicit synthesis, regulatory exploitation) must be blocked and reported to the internal compliance authority.

<a id="12-mejores-prácticas-internacionales-síntesis"></a>
## 12. International Best Practices (Synthesis)

Based on guidelines from leading regulatory and scientific bodies, this section consolidates recognized standards for responsible research in computational biology and chemistry.

<a id="121-marco-nih-national-institutes-of-health---estados-unidos"></a>
### 12.1 NIH (National Institutes of Health) Framework - United States
| Principle | Bio/Chem Computational Application |
|-----------|-----------------------------------|
| Scientific Rigor | Experimental validation of computational results before publication |
| Transparency | Open code and data (when safe); reproducible methodology |
| Social Responsibility | Consideration of dual-use impact and social benefit |
| Participant Protection | Strict anonymization of genomic/medical data |

<a id="122-whooms---ética-en-investigación-de-salud"></a>
### 12.2 WHO/PAHO - Ethics in Health Research
| Guideline | Suggested Implementation |
|-----------|-------------------------|
| Informed Consent | Clear disclaimer about diagnostic limitations of models |
| Risk Minimization | Computational limits to avoid overinterpretation |
| Distributive Justice | Equitable access to tools; avoid algorithmic biases |
| Beneficence | Prioritize therapeutic vs. sensitive commercial applications |

<a id="123-ga4gh-global-alliance-for-genomics-and-health"></a>
### 12.3 GA4GH (Global Alliance for Genomics and Health)
| Framework | Specific Control |
|-----------|-------------------|
| FAIR Principles | Findable, Accessible, Interoperable, Reusable data with ethical metadata |
| Privacy by Design | Differential privacy techniques in population analyses |
| International Standards | GDPR/HIPAA compliance according to jurisdiction |
| Federated Learning | Avoid centralization of sensitive data |

<a id="124-oecd---responsible-innovation"></a>
### 12.4 OECD - Responsible Innovation
| Pillar | Metric/Process |
|-------|----------------|
| Anticipation | Prospective assessment of emerging risks (e.g., genomic editing) |
| Inclusion | Multi-stakeholder consultation for controversial applications |
| Reflexivity | Periodic policy review in light of technological advances |
| Adaptability | Flexible frameworks that evolve with the field |

<a id="125-nsabb-national-science-advisory-board-for-biosecurity---dual-use"></a>
### 12.5 NSABB (National Science Advisory Board for Biosecurity) - Dual Use
| Dual-Use Category | Warning Signal | Mitigation |
|---------------------|-----------------|------------|
| Dangerous Information | Exact methodology for pathogenic synthesis | Publication with critical technical omissions |
| Sensitive Technology | Automated agent design tools | Access restriction + institutional whitelist |
| Risk Data | Complete pathogen genomes | Controlled access via IRB/committees |
| Emerging Capabilities | AI that accelerates threat design | Pause development until regulatory frameworks |

<a id="126-elixir---infraestructura-datos-biológicos-europa"></a>
### 12.6 ELIXIR - European Biological Data Infrastructure
| Standard | Application |
|----------|------------|
| Data Stewardship | Data management plans with ethical considerations |
| Interoperability | Secure APIs that preserve privacy |
| Training & Outreach | Continuing education in biological data ethics |
| Compliance Monitoring | Regular audits of policy adherence |

<a id="127-síntesis-de-recomendaciones-adoptadas"></a>
### 12.7 Synthesis of Adopted Recommendations

**Technical Controls:**
- Irreversible anonymization (hashing + salt) before analysis.
- Automatic limits on parameters that could reveal sensitive information.
- Exhaustive logging with timestamping for external auditing.
- Sandboxing of high-risk experiments.

**Procedural Controls:**
- Prospective (not just reactive) ethical review for new capabilities.
- Documentation of limitations and disclaimers in all outputs.
- Mandatory training of personnel in computational biosecurity.
- Incident response protocols specific to biological data breaches.

**Governance Controls:**
- Interdisciplinary committee (scientists, ethicists, legal, security).
- Annual external review by an independent auditor.
- Whistleblowing policies to report misuse.
- Coordination with national regulatory authorities when applicable.
<a id="128-adaptación-al-ethics-gate"></a>
### 12.8 Adaptation to the Ethics Gate
The above principles map to our implementation:
- **Heuristic scoring** incorporates elements of anticipation (OECD) and dual-use categorization (NSABB).
- **YAML policy** allows adaptability without code recompilation.
- **Digital signature** provides non-repudiation for critical decisions.
- **Merkle anchoring** facilitates external auditing (ELIXIR).
- **Metrics** allow continuous monitoring of adherence (WHO).

**Pending Future Implementation:**
- Federated Learning hooks for analysis without data centralization.
- Privacy-preserving computation (e.g., homomorphic computation).
- Integration with IRB/institutional ethics committees.
- Transparency dashboard for external stakeholders.

<a id="13-protección-de-proyectos-open-source-bioquímica"></a>
## 13. Protection of Open Source Bio/Chemistry Projects

<a id="131-el-dilema-del-código-abierto-en-ciencias-de-la-vida"></a>
### 13.1 The Open Source Dilemma in Life Sciences
Open source projects in biology and chemistry face the challenge of **promoting scientific transparency** while **minimizing dual-use risks**. There is no perfect solution, but mitigation strategies have been developed.

<a id="132-mecanismos-de-protección-establecidos"></a>
### 13.2 Established Protection Mechanisms

<a id="a-screening-de-contribuidores"></a>
#### A) **Contributor Screening**
| Strategy | Implementation | Examples |
|------------|----------------|----------|
| Institutional whitelist | Only verified academic/governmental organizations | BioConductor, NCBI tools |
| Identity verification | Require ORCID + institutional affiliation | Galaxy Project, ELIXIR |
| Vetting process | Manual review of new contributors by maintainers | OpenMM, RDKit |

<a id="b-limitación-funcional-safeguarding"></a>
#### B) **Functional Limitation (Safeguarding)**
| Technique | Description | Application |
|---------|-------------|-----------|
| Bounded parameters | Hard limits on input ranges | Limit genome size, basis sets |
| Separate modules | Sensitive functionality in separate packages | PyMOL vs. PyMOL-PSI |
| Gradual deprecation | Remove problematic functions in future versions | Sunset dangerous APIs |

<a id="c-ofuscación-selectiva"></a>
#### C) **Selective Obfuscation**
| Method | Pros | Cons | Recommended Use |
|--------|------|---------|-----------------|
| Incomplete algorithms | Preserves critical IP | Reduces reproducibility | Proprietary validation methods |
| Synthetic data | Avoids real exposure | Lower precision | Demos and tutorials |
| Abstractions | Hides implementation | Limits customization | High-level APIs |

<a id="d-licencias-restrictivas"></a>
#### D) **Restrictive Licenses**
| License | Restrictions | Bio/Chem Applicability |
|----------|---------------|------------------------|
| Academic-only | Non-commercial/educational use only | Experimental algorithms |
| No-derivatives | Prohibits modifications | Validated diagnostic software |
| Geographical | Country/region restriction | ITAR/EAR compliance |
| Field-of-use | Limits application domain | "Basic research only" |

<a id="133-estrategias-por-tipo-de-riesgo"></a>
### 13.3 Strategies by Risk Type

<a id="bioseguridad-patógenostoxinas"></a>
#### **Biosecurity (Pathogens/Toxins)**
- **Sequence screening**: Compare against restricted organism lists (Australia Group, CDC)
- **Fragmentation**: Publish only non-functional subsequences
- **Delayed release**: Temporary embargo until review by biosafety boards
- **Watermarking**: Detectable marks in generated sequences

<a id="química-dual-use-explosivosvenenos"></a>
#### **Dual-Use Chemistry (Explosives/Poisons)**
- **Descriptor filtering**: Omit properties such as toxicity/detonation energy
- **Synthesis pathway obscuration**: Do not publish complete synthesis routes
- **Precursor monitoring**: Alert on compounds in control lists
- **Collaborative filtering**: Crowd-sourcing of malicious use detection

<a id="propiedad-intelectual-sensible"></a>
#### **Sensitive Intellectual Property**
- **Clean room implementations**: Reimplement algorithms without original code
- **Differential privacy**: Controlled noise in screening results
- **Federated approaches**: Distributed model without centralizing data
- **Homomorphic computation**: Analysis without revealing inputs

<a id="134-casos-de-estudio-conocidos"></a>
### 13.4 Known Case Studies

<a id="openeye-omega-conformer-generation"></a>
#### **OpenEye OMEGA (Conformer Generation)**
- Free academic license with commercial limitations
- Public API but proprietary core algorithms
- Automatic limits on number of conformers for unverified users

<a id="gromacsopenmm-molecular-dynamics"></a>
#### **GROMACS/OpenMM (Molecular Dynamics)**
- Completely open code BUT limited documentation for advanced parameters
- Community self-regulates problematic uses via mailing lists
- HPC integration requires institutional credentials

<a id="biopython-sequence-analysis"></a>
#### **BioPython (Sequence Analysis)**
- Database search functions require API keys
- Automatic rate limiting to prevent mass scraping
- Documentation includes prominent ethical warnings

<a id="135-implementación-sugerida-para-axiom"></a>
### 13.5 Suggested Implementation for AXIOM

<a id="nivel-1-controles-técnicos"></a>
#### **Level 1: Technical Controls**
```python
# Ejemplo: Screening automático en computational_chemistry
RESTRICTED_PATTERNS = [
    "(?i).*explosive.*",
    "(?i).*toxin.*synthesis.*",
    "(?i).*bioweapon.*"
]

def screen_description(desc: str) -> bool:
    import re
    for pattern in RESTRICTED_PATTERNS:
        if re.search(pattern, desc):
            return False  # Bloquear
    return True
```

<a id="nivel-2-restricciones-de-acceso"></a>
#### **Level 2: Access Restrictions**
- **Soft limits**: Anonymous users → basic functionality
- **Verified users**: Academic affiliation → full access
- **Trusted contributors**: Track record → experimental functions

<a id="nivel-3-transparencia-controlada"></a>
#### **Level 3: Controlled Transparency**
- **Public audit logs**: Hash of requests (without content)
- **Community reporting**: Mechanism to report suspicious use
- **Regular reviews**: Quarterly review of usage patterns

<a id="136-limitaciones-de-protección-open-source"></a>
### 13.6 Limitations of Open Source Protection

**❌ Cannot Be Completely Prevented:**
- Malicious fork of the code
- Reverse engineering of algorithms
- Use by state/criminal actors
- Combination with other tools to create dangerous capabilities

**✅ Can Be Mitigated:**
- Automated mass access
- Accidental use by legitimate researchers
- Proliferation to unsophisticated users
- Lack of traceability for audits

<a id="137-recomendaciones-finales"></a>
### 13.7 Final Recommendations

1. **Gradual transparency**: Basic functionality open, advanced restricted
2. **Community engagement**: Involve community in self-regulation
3. **Legal compliance**: Alignment with national/international regulations
4. **Continuous monitoring**: Automatic alerts for anomalous patterns
5. **Responsible disclosure**: Protocols for reporting found vulnerabilities

<a id="para-axiom-específicamente"></a>
#### **For AXIOM Specifically:**
- Implement `EthicsGate` as a minimum protection layer
- Consider dual license (open core + enterprise)
- Clearly document limitations and disclaimers
- Establish a community review process for new sensitive capabilities
- Collaborate with international organizations (GA4GH, OECD) for standards alignment

---
Maintainer: AXIOM Ethics Committee – Minimum quarterly review.
