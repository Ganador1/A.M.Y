# A.M.Y Acceptable Use Policy

*Last updated: 2026-05-21*

This document complements the Apache License 2.0 (LICENSE) under which A.M.Y is distributed. The Apache license grants broad rights; this policy expresses the intent of the project and the responsibilities the project asks its users to honour.

A.M.Y is an autonomous scientific research system. It composes calls to a library of computational tools (SymPy, NumPy, PySCF, ASE, AstroPy, BioPython, ClinicalBERT, and others, all independently available in PyPI) and writes manuscripts with cryptographic provenance.

By using A.M.Y you agree not to use it, or any system derived from it, for the following purposes.

---

## 1. Prohibited uses

### 1.1 Weapons of mass destruction

The system must not be used to assist with the design, synthesis, production, optimisation, weaponisation, or deployment of chemical, biological, radiological, or nuclear weapons of any kind. This includes pathogen enhancement aimed at increasing transmissibility, lethality, host range, or biosafety bypass; fissile material enrichment, plutonium or HEU weaponisation, implosion-lens design, or radiological dispersal devices; and mass-casualty explosive devices.

### 1.2 Cyber abuse

The system must not be used to generate operational malware, exploits, credential-theft tooling, or attack payloads. It must not be used to assist attacks on critical infrastructure (power grids, water treatment, hospital networks, gas pipelines, nuclear plants, air traffic control, election infrastructure).

### 1.3 Mass surveillance and targeting

The system must not be used for mass surveillance, deanonymisation of named individuals, covert biometric identification, social-credit profiling on protected attributes (political, religious, ethnic, sexual orientation), or generation of targeted deepfakes against named victims.

### 1.4 Unauthorised human experimentation

The system must not be used to design or execute research on identified human subjects without informed consent and proper ethical oversight.

### 1.5 Guardrail tampering

The system must not be modified to remove, disable, bypass, or weaken its built-in misuse_guard policy. Forks that disable the guard must use a different project name so that the projects can be distinguished by downstream users.

---

## 2. The misuse_guard

A.M.Y ships with an enforced policy engine at atlas/app/security/misuse_guard.py. The guard fails closed: if the policy module cannot be loaded, all operations are denied. The guard runs before tool execution and before any subprocess starts. It covers the categories above and is tested in tests/test_atlas_misuse_guard.py (7 / 7 pass) and tests/test_security_guardrails.py.

Bypasses of the guard should be reported per SECURITY.md.

---

## 3. Watermarking

Every paper produced by A.M.Y carries a Provenance Watermark block containing the A.M.Y version, generation timestamp, SHA-256 fingerprint of the body, and a link to this repository. The watermark exists so the wider research ecosystem (journals, search engines, peer reviewers) can detect and filter A.M.Y-generated content as it sees fit.

Removing or falsifying the watermark while distributing A.M.Y-generated content as human-authored research is a violation of this policy.

---

## 4. Responsibilities of downstream users

If you use A.M.Y:

- You are responsible for verifying any claim before relying on it in safety-critical contexts.
- You agree that Reflection Agent output (the Self-Review section) is part of the manuscript and should not be hidden when sharing.
- You agree to credit A.M.Y when redistributing generated artifacts and to retain the watermark.
- You are responsible for any consequences of disabling the misuse_guard in a fork.

---

## 5. Relationship to upstream tools

The capabilities that A.M.Y orchestrates (PySCF, ASE, RDKit, AstroPy, BioPython, ClinicalBERT, and dozens of others) are independently available in PyPI and other registries. A.M.Y does not add novel offensive capability; it adds organisation, provenance, and refusal.

This policy applies to A.M.Y itself. The upstream tools are governed by their own licenses and policies.

---

## 6. Reporting violations

To report a misuse_guard bypass or an attempt to use A.M.Y in violation of this policy, see SECURITY.md.

---

## 7. Changes to this policy

This is a living document. Material changes will be noted in CHANGELOG.md. The current version is always the version at the tip of the main branch.

---

Apache License 2.0 governs the legal grant. This policy expresses the project's intent and the community's expectations.
