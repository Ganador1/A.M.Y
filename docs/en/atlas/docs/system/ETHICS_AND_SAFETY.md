> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="ética-seguridad-y-uso-responsable"></a>
# Ethics, Safety, and Responsible Use

This project includes modules for scientific computing, simulation, cryptography, and process execution that can entail technical, legal, or security risks if used incorrectly. This document centralizes warnings, best practices, and limitations.

<a id="principios-de-uso-responsable"></a>
## Principles of responsible use
- Comply with applicable laws and licenses (software, data, export, encryption).
- Do not use the system to harm, violate privacy, or bypass controls.
- Inform end users of limitations, biases, and margins of error.
- Protect credentials, keys, and sensitive data.
- Respect resource limits (CPU/GPU/memory) to avoid abuse or unexpected costs.

<a id="áreas-de-riesgo-y-advertencias"></a>
## Risk areas and warnings

<a id="1-criptografía-y-claves-approuterscryptography-diagnose_rsapy"></a>
### 1) Cryptography and keys (app/routers/cryptography, diagnose_rsa.py)
- Do not generate, store, or transmit private keys in plain text.
- Avoid using insecure key sizes or non-cryptographic RNG.
- Comply with export regulations and local regulations on encryption.
- Use reviewed libraries; avoid implementing cryptographic algorithms from scratch.

<a id="2-endpoints-y-red-fastapi-requestshttpx-scripts-de-test"></a>
### 2) Endpoints and network (FastAPI, requests/httpx, test scripts)
- Expose the server only on trusted networks and with authentication (JWT/API keys).
- Validate and sanitize input; limit rates and add role-based access control.
- Never log secrets or PII. Review `server.log` and configurations.

<a id="3-ejecución-de-códigoprocesos-subprocess-evalexec-en-pde"></a>
### 3) Code/Process execution (subprocess, eval/exec in PDE)
- `eval/exec` is dangerous. In `pde_service.py` it is limited, but should be avoided with user input.
- Do not execute system commands with untrusted input. Use argument lists and timeouts.
- Isolate intensive processes (containers) and set resource limits.

<a id="4-base-de-datos-y-ficheros-sqlalchemy-sqlite3-open"></a>
### 4) Database and files (SQLAlchemy, sqlite3, open())
- Use parameterized queries; do not build SQL with strings.
- Encrypt sensitive data at rest and in transit. Manage migrations securely.
- Control file permissions. Do not store PII without a legal basis.

<a id="5-gpudftsimulaciones-gpaw-ase-deepxde-pytorch"></a>
### 5) GPU/DFT/Simulations (GPAW, ASE, DeepXDE, PyTorch)
- High energy consumption/cost: configure limits (mesh size, k-points, steps).
- Respect licenses and citations of code and scientific data.
- Do not use results without validation for critical decisions.

<a id="6-servicios-médicos-avanzados-strain-analysis-multiscale-models-advanced-clinical-validation"></a>
### 6) Advanced Medical Services (Strain Analysis, Multiscale Models, Advanced Clinical Validation)
- **CRITICAL WARNING**: These services process sensitive medical data. Comply with HIPAA/GDPR and obtain informed consent.
- **Clinical Limitations**: Results are support tools, they do not replace professional medical judgment.
- **Required Validation**: Validate algorithms against clinical standards before diagnostic use.
- **Privacy**: Anonymize data before processing. Do not store medical images without encryption.
- **Responsibility**: Document limitations, margins of error, and cases where the algorithm may fail.
- **Consent**: Obtain ethical approval for use of medical data in research.
- **Transparency**: Explain algorithms to clinical users and patients when appropriate.

<a id="7-servicios-científicos-avanzados-plasma-physics-additive-manufacturing"></a>
### 7) Advanced Scientific Services (Plasma Physics, Additive Manufacturing)
- **Safety Risks**: Plasma simulations can model processes with dual applications (medical/military).
- **Export Licenses**: Verify ITAR/EAR regulations for plasma physics algorithms.
- **Scientific Validation**: Results require experimental validation before publication or application.
- **Computational Resources**: Intensive processes can affect system availability.
- **Intellectual Property**: Respect patents and copyrights in additive manufacturing designs.
- **Environmental Impact**: Consider the energy footprint of high-performance simulations.

<a id="8-caché-y-redis"></a>
### 8) Cache and Redis
- Do not cache sensitive data. Define correct expiration and invalidation.
- Secure Redis with password/TLS and access control lists.

<a id="datos-personales-y-cumplimiento"></a>
## Personal data and compliance
- Minimize data collection. Define retention and deletion.
- Inform users about data use. Facilitate export and deletion.
- Consider GDPR/CCPA or other regulations according to your jurisdiction.

<a id="riesgos-específicos-de-ia-médica-y-científica"></a>
## Specific risks of medical and scientific AI

<a id="extensión-biología-y-química-computacional-resumen"></a>
### Extension: Computational Biology and Chemistry (Summary)
For expanded details see `BIO_CHEM_ETHICS_AND_SAFETY.md`.
| Sensitive Domain | Risks | Base Mitigation |
|------------------|---------|-----------------|
| Genomics | Re-identification, privacy | Strict anonymization, hashing, CRITICAL gating |
| Metabolic Networks | Biosynthetic pathway design | Dual signature, model limits |
| Advanced Computational Chemistry | Massive screening | Conformer and batch size limit |
| Molecular Dynamics | Derivation of sensitive structures | Atom and force field control |
| Synthetic Biology | Unauthorized construction | Block by default + whitelist |
| Biosecurity / Assessment | Vulnerability detection | Isolation + reinforced auditing |

<a id="ia-en-medicina-y-salud"></a>
### AI in Medicine and Health
- **Data Biases**: Models can inherit biases from training data (underrepresentation of demographic groups).
- **False Positives/Negatives**: Risk of erroneous diagnoses with serious consequences for patients.
- **Technological Dependence**: Does not replace clinical experience; use it as a complementary tool.
- **Genetic Privacy**: Genomic data requires special protection under medical privacy laws.
- **Health Equity**: Ensure algorithms work equitably across diverse populations.

<a id="ia-en-investigación-científica"></a>
### AI in Scientific Research
- **Reproducibility**: Fully document parameters, data, and versions for reproducibility.
- **Experimental Validation**: Computational results require experimental validation before scientific claims.
- **Scientific Fraud**: Avoid manipulation of results or cherry-picking of data.
- **Ethical Collaboration**: Transparency in public-private collaborations, especially with sensitive data.
- **Environmental Impact**: High-performance simulations have a significant energy footprint.

<a id="gobernanza-de-ia"></a>
### AI Governance
- **Regular Audits**: Periodically review algorithms for biases, accuracy, and security.
- **Explainability**: Implement methods to explain AI decisions (XAI - Explainable AI).
- **Continuous Monitoring**: Alert system for performance degradation or anomaly detection.
- **Responsible Update**: Model update plan with full validation before deployment.

<a id="registro-y-monitoreo"></a>
## Logging and monitoring
- Log metrics without exposing sensitive data.
- Set alerts for anomalous resource use or repeated errors.

<a id="protocolos-de-emergencia-y-respuesta-a-incidentes"></a>
## Emergency protocols and incident response

<a id="incidentes-médicos"></a>
### Medical Incidents
- **Algorithm Failure**: Fallback protocol to traditional methods if AI fails.
- **Data Breach**: Immediate notification to affected parties and regulatory authorities.
- **Adverse Clinical Outcome**: Complete documentation and root-cause analysis.
- **Response Time**: Maximum 24 hours for critical health incidents.

<a id="incidentes-científicos"></a>
### Scientific Incidents
- **Simulation Error**: Cross-verification with alternative methods.
- **Data Loss**: Redundant backups and disaster recovery.
- **Data Contamination**: Isolation protocols and dataset cleaning.
- **Validation Failure**: Full review before publication or application.

<a id="recuperación-de-desastres"></a>
### Disaster Recovery
- **Continuity Plan**: Maintenance of critical services during interruptions.
- **Communication**: Clear channels to inform stakeholders about incidents.
- **Lessons Learned**: Post-incident analysis and continuous improvement of protocols.

<a id="versionado-y-almacenamiento-de-datos"></a>
## Versioning and data storage
- Do not version PII/secrets/restrictive licenses. Use .gitignore/.dvcignore.
- Configure limits: MAX_VERSION_FILE_BYTES (e.g., 500MB per file) and space quotas.
- Restrict paths with STRICT_DATA_PATHS=1 and ALLOWED_DATA_ROOT (default ./data).
- Verify integrity with checksums (SHA-256) and change audits.
- DVC is optional; protect remotes with secure credentials and TLS.

<a id="limitaciones-y-descargo-de-responsabilidad"></a>
## Limitations and disclaimer
- The software is provided "as is", without warranties. Use it at your own risk.
- Educational or demo modules are not hardened for production.
- Scientific results may vary depending on parameters and environment.

<a id="checklist-rápido-antes-de-producción"></a>
## Quick checklist before production
- [ ] Secure environment variables (no secrets in repository)
- [ ] HTTPS/TLS on endpoints, authentication and authorization active
- [ ] Input sanitization and rate limits
- [ ] Logs without PII or secrets
- [ ] Data retention policies
- [ ] Resource limits and quotas configured

<a id="referencias"></a>
## References
- OWASP Top 10, ASVS
- NIST SP 800-53 / 800-57 (key management)
- Responsible AI: transparency, fairness, robustness, privacy
- FDA Guidance for Medical Device Software
- EU AI Act (Artificial Intelligence Act)
- WHO Guidelines for Digital Health
- ACM Code of Ethics for Computing
- ASME Standards for Additive Manufacturing
- IEEE Standards for Plasma Physics Simulations

---

<a id="matriz-de-evaluación-de-riesgo-propuesta"></a>
## Risk Assessment Matrix (Proposal)
| Level | Description | Examples | Required Controls |
|-------|-------------|----------|----------------------|
| Low | No security/privacy impact | Symbolic algebra, simple visualizations | Basic logging |
| Medium | Moderate use of resources or non-sensitive data | Numerical optimization, small simulations | Resource limits, metrics |
| High | Sensitive data or intensive computing | Medical images, multiscale models | Isolation, hash traceability, human review |
| Critical | Potential dual-use or direct clinical impact | Advanced plasma, automated clinical analysis | Formal ethical review, manual gating, reinforced auditing |

<a id="controles-graduales-escalonamiento"></a>
## Gradual Controls (Escalation)
1. Passive observation (metrics only)
2. Parameter limitation (safe ranges)
3. Partial sandboxing (limited resources)
4. Double human confirmation (4-eyes)
5. Ethical gate with signed justification

<a id="checklist-dual-use-antes-de-ejecución"></a>
## Dual-Use Checklist before Execution
- Can the result be reused for physical, biological, or industrial harm?
- Are there applicable export restrictions (ITAR/EAR)?
- Is there a less risky alternative for the scientific objective?
- Is the legitimate purpose and limits of use documented?
- Does the code/experiment include validation references and disclaimers?

If ≥2 "yes" answers → escalate to ethical review before continuing.

<a id="mecanismo-de-override-responsable"></a>
## Responsible Override Mechanism
| Condition | Override Requirement | Log |
|-----------|-----------------------|---------|
| Automatic block due to high risk | Digital signature of 2 responsible parties | Hash + timestamp integrity chain |
| Resource excess | Justification of need | Before/after metrics |
| Unvalidated experimental algorithm | Attached validation plan | Linked ticket |

<a id="red-teaming-científico-plan"></a>
## Scientific Red Teaming (Plan)
| Phase | Objective | Frequency |
|------|----------|-----------|
| Adversarial simulation | Find unsafe parameters | Semiannual |
| Corrupt data injection | Evaluate validation robustness | Quarterly |
| Reproducibility audit | Confirm replicability | Annual |

<a id="roles-humanos-y-responsabilidades"></a>
## Human Roles and Responsibilities
| Role | Ethical Responsibility |
|-----|-----------------------|
| Scientific Lead | Final approval of critical experiments |
| Compliance Officer | Verify regulations and licenses |
| Data Steward | Data classification and anonymization |
| SecOps | Oversee operational security |
| Ethics Committee | Review dual-use and clinical cases |

<a id="respuesta-a-incidentes-extensión"></a>
## Incident Response (Extension)
| Type | Target Time (TTR) | Key Actions |
|------|----------------------|---------------|
| Sensitive data breach | < 4h containment | Isolate, revoke keys, notify |
| Unauthorized massive GPU use | < 2h | Cut session, analyze logs |
| Integrity chain failure | < 6h | Rebuild Merkle, compare backups |
| Clinical model drift | < 24h | Deploy previous stable version |

<a id="métricas-éticas-operacionales-adicionales"></a>
## Operational Ethical Metrics (Additional)
| Metric | Formula | Threshold | Action |
|---------|---------|--------|--------|
| risk_event_rate | risk_events / executions | < 1% | Review rules if > |
| override_ratio | overrides / blocks | < 30% | Audit reasons |
| dual_use_flags | approved flags / total flags | N/A | Trend monitoring |
| reproducibility_gap | |ref_result - current_result| | < defined tolerance | Adjust pipeline |

<a id="integración-con-otros-documentos"></a>
## Integration with Other Documents
- See `ETHICS_COMPLIANCE_PLAN.md` for bias and gating roadmap.
- See `INTEGRITY_PIPELINE_UNIFICATION.md` for hash chaining and auditing.

<a id="ejemplo-de-uso-práctico-ethics-gate"></a>
## Practical Use Example (Ethics Gate)
```python
from app.ethics_gate import EthicsGate, ExperimentRequest

gate = EthicsGate()
req = ExperimentRequest(
	domain="medical_imaging",
	description="Segmentación de estudios anonimizada para validación",
	resources={"gpu_hours": 3, "memory_gb": 48},
	data_sensitivity="high",
	declared_intent="Mejorar precisión diagnóstica",
	justification="Validación prospectiva controlada con comité aprobado",
	justification_signature="usuarioX|2025-09-09"
)
decision = gate.evaluate(req)
if not decision.allowed:
	raise RuntimeError(f"Bloqueado: {decision.reason} (nivel {decision.level})")
```
The hash `decision.hash_record` can be concatenated in the integrity pipeline for an auditable chain.

<a id="política-yaml-y-configuración-dinámica"></a>
### YAML Policy and Dynamic Configuration
You can adjust thresholds, domains, and levels that require signature by creating a YAML file (default path in `ETHICS_POLICY_PATH` or passing it as an argument to the constructor):

```yaml
thresholds:
	low: 3      # <3 => LOW
	medium: 7   # 3-6 => MEDIUM, 7-10 => HIGH
	high: 11    # >=11 => CRITICAL
domain_weights:
	medical_imaging: 5
	clinical_validation: 6
	plasma_physics: 4
signature_levels: ["HIGH", "CRITICAL"]
```

Example with explicit policy and dry-run:
```python
gate = EthicsGate(policy_path="config/ethics_policy.yaml")
preview = gate.evaluate(req, dry_run=True)  # No persiste en log ni ancla
print(preview.level, preview.risk_score)
```

<a id="métricas-expuestas-prometheus-opcional"></a>
### Exposed Metrics (optional Prometheus)
If `prometheus_client` is installed, they are registered (labels: level, allowed):
- ethics_risk_events_total{level,allowed}
- ethics_overrides_total{level}
- ethics_malicious_block_total
- ethics_high_pending (Gauge)
Integrate a standard endpoint (`/metrics`) in FastAPI to expose them.

<a id="firma-digital-y-cadena-de-integridad"></a>
### Digital Signature and Integrity Chain
If `cryptography` (Ed25519) is available, an ephemeral key is generated:
```python
pub = gate.export_public_key()
sig = gate.sign_chain()          # Firma hash agregado actual
assert gate.verify_chain_signature(sig)
```
It is recommended to persist the private key externally (HSM/secure file) for audit continuity.

<a id="anclaje-merkle-hook"></a>
### Merkle Anchoring (Hook)
`evaluate(..., auto_anchor=True)` triggers `_try_anchor_chain()` which invokes `anchor_hook(chain_hash)` if configured. Integrate here your service for:
- Blockchain / external notarization
- Batched Merkle registry
- Transparency scheme or third-party attest ledger

<a id="buenas-prácticas-de-uso-del-gate"></a>
### Best Practices for Using the Gate
- Use `dry_run=True` in UI to show the user why it would be blocked.
- Require a minimum justification length (≥15 chars by default) in overrides.
- Monitor `override_ratio` (see Operational Ethical Metrics section) to detect signature abuse.
- Version the YAML policy and apply change control / review.
- Implement controlled rotation of Ed25519 keys if signatures are published externally.

<a id="roadmap-ético-ampliado"></a>
## Expanded Ethical Roadmap
| Phase | Deliverable | Success Metric |
|------|---------|------------------|
| Q4 2025 | Implement dynamic risk matrix | Coverage ≥ 90% of classified executions |
| Q1 2026 | Configurable YAML Ethics Gate | <5% false blocks |
| Q1 2026 | Partial automated red teaming | ≥3 actionable findings |
| Q2 2026 | Automatically generated ethical report | Consistent monthly publication |

<a id="consideraciones-ambientales"></a>
## Environmental Considerations
- Energy monitor (kWh/job) planned.
- Penalty for configurations with >p95 consumption.
- Recommendation for batches outside peak hours.

<a id="declaración-de-limitación-adicional"></a>
## Additional Limitation Statement
This framework mitigates risks but does not guarantee total elimination of abuse. It requires continuous human oversight and periodic review of metrics and policies.
