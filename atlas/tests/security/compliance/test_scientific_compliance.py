"""
Scientific compliance validation tests for FAIR data principles and reproducibility standards.

Propósito:
    Validar el cumplimiento con estándares científicos internacionales incluyendo
    principios FAIR (Findable, Accessible, Interoperable, Reusable), reproducibilidad
    computacional, gestión de datos de investigación, y mejores prácticas científicas.

Coverage:
    - FAIR data principles compliance validation
    - Computational reproducibility assessment
    - Research data management validation
    - Scientific metadata standards compliance
    - Open science practices validation
    - Ethics and responsible AI compliance
    - Publication and citation standards
    - Data provenance and lineage tracking
"""

import pytest
import os
from typing import List
from dataclasses import dataclass, field
from pathlib import Path
import re
from datetime import datetime, timezone


@dataclass
class ComplianceViolation:
    """Container for compliance violation findings."""
    standard: str
    category: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    violation_id: str
    title: str
    description: str
    affected_component: str
    requirement: str
    current_state: str
    recommended_action: str
    compliance_score: float  # 0.0 - 1.0


@dataclass
class FAIRAssessment:
    """Container for FAIR principles assessment."""
    findable_score: float
    accessible_score: float
    interoperable_score: float
    reusable_score: float
    overall_score: float
    violations: List[ComplianceViolation] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ReproducibilityAssessment:
    """Container for reproducibility assessment."""
    computational_score: float
    data_score: float
    documentation_score: float
    environment_score: float
    overall_score: float
    violations: List[ComplianceViolation] = field(default_factory=list)
    missing_components: List[str] = field(default_factory=list)


@dataclass
class ComplianceReport:
    """Container for complete compliance assessment report."""
    assessment_date: datetime
    project_name: str
    fair_assessment: FAIRAssessment
    reproducibility_assessment: ReproducibilityAssessment
    ethics_compliance_score: float
    open_science_score: float
    overall_compliance_score: float
    critical_violations: int
    high_violations: int
    medium_violations: int
    low_violations: int
    total_violations: int
    compliance_status: str  # COMPLIANT, PARTIALLY_COMPLIANT, NON_COMPLIANT


class ScientificComplianceValidator:
    """Validator for scientific compliance standards."""

    def __init__(self, project_root: str = ".") -> None:
        self.project_root = Path(project_root)
        self.violations: List[ComplianceViolation] = []

    async def validate_fair_principles(self) -> FAIRAssessment:
        """Validate FAIR (Findable, Accessible, Interoperable, Reusable) principles."""

        print("🔍 Validating FAIR Principles...")

        findable_score = await self._assess_findability()
        accessible_score = await self._assess_accessibility()
        interoperable_score = await self._assess_interoperability()
        reusable_score = await self._assess_reusability()

        overall_score = (findable_score + accessible_score + interoperable_score + reusable_score) / 4

        # Generate recommendations
        recommendations = []
        if findable_score < 0.7:
            recommendations.append("Improve metadata documentation and data cataloging")
        if accessible_score < 0.7:
            recommendations.append("Implement standardized data access protocols")
        if interoperable_score < 0.7:
            recommendations.append("Adopt standard data formats and vocabularies")
        if reusable_score < 0.7:
            recommendations.append("Add comprehensive licensing and usage documentation")

        return FAIRAssessment(
            findable_score=findable_score,
            accessible_score=accessible_score,
            interoperable_score=interoperable_score,
            reusable_score=reusable_score,
            overall_score=overall_score,
            violations=[v for v in self.violations if "FAIR" in v.standard],
            recommendations=recommendations
        )

    async def validate_reproducibility(self) -> ReproducibilityAssessment:
        """Validate computational reproducibility standards."""

        print("🔬 Validating Reproducibility Standards...")

        computational_score = await self._assess_computational_reproducibility()
        data_score = await self._assess_data_reproducibility()
        documentation_score = await self._assess_documentation_reproducibility()
        environment_score = await self._assess_environment_reproducibility()

        overall_score = (computational_score + data_score + documentation_score + environment_score) / 4

        # Identify missing components
        missing_components = []
        if computational_score < 0.8:
            missing_components.append("Deterministic algorithms and seed management")
        if data_score < 0.8:
            missing_components.append("Data versioning and provenance tracking")
        if documentation_score < 0.8:
            missing_components.append("Comprehensive methodology documentation")
        if environment_score < 0.8:
            missing_components.append("Reproducible computational environment")

        return ReproducibilityAssessment(
            computational_score=computational_score,
            data_score=data_score,
            documentation_score=documentation_score,
            environment_score=environment_score,
            overall_score=overall_score,
            violations=[v for v in self.violations if "REPRODUCIBILITY" in v.standard],
            missing_components=missing_components
        )

    async def validate_ethics_compliance(self) -> float:
        """Validate ethics and responsible AI compliance."""

        print("⚖️ Validating Ethics Compliance...")

        score_components = []

        # Check for ethics gate implementation
        ethics_gate_score = await self._check_ethics_gate()
        score_components.append(ethics_gate_score)

        # Check for bias detection and mitigation
        bias_detection_score = await self._check_bias_detection()
        score_components.append(bias_detection_score)

        # Check for informed consent mechanisms
        consent_score = await self._check_informed_consent()
        score_components.append(consent_score)

        # Check for data privacy protection
        privacy_score = await self._check_data_privacy()
        score_components.append(privacy_score)

        # Check for transparency and explainability
        explainability_score = await self._check_explainability()
        score_components.append(explainability_score)

        return sum(score_components) / len(score_components) if score_components else 0.0

    async def validate_open_science_practices(self) -> float:
        """Validate open science practices compliance."""

        print("🌐 Validating Open Science Practices...")

        score_components = []

        # Check for open source licensing
        open_source_score = await self._check_open_source_licensing()
        score_components.append(open_source_score)

        # Check for open data availability
        open_data_score = await self._check_open_data()
        score_components.append(open_data_score)

        # Check for open access publications
        open_access_score = await self._check_open_access()
        score_components.append(open_access_score)

        # Check for collaborative development practices
        collaboration_score = await self._check_collaboration_practices()
        score_components.append(collaboration_score)

        return sum(score_components) / len(score_components) if score_components else 0.0

    # FAIR Principles Assessment Methods

    async def _assess_findability(self) -> float:
        """Assess Findable component of FAIR principles."""
        score = 0.0
        total_checks = 0

        # Check for metadata files
        metadata_files = [
            "README.md", "METADATA.json", "datacite.yml",
            "dublin_core.xml", "schema.org.json"
        ]

        for meta_file in metadata_files:
            total_checks += 1
            if (self.project_root / meta_file).exists():
                score += 1.0

        # Check for DOI or persistent identifiers
        total_checks += 1
        if await self._has_persistent_identifier():
            score += 1.0
        else:
            self.violations.append(ComplianceViolation(
                standard="FAIR-F1",
                category="Findable",
                severity="HIGH",
                violation_id="FAIR_F1_NO_PID",
                title="No Persistent Identifier",
                description="Project lacks persistent identifier (DOI, ORCID, etc.)",
                affected_component="Project metadata",
                requirement="F1: (Meta)data are assigned globally unique and persistent identifiers",
                current_state="No persistent identifier found",
                recommended_action="Register DOI or other persistent identifier",
                compliance_score=0.0
            ))

        # Check for rich metadata
        total_checks += 1
        if await self._has_rich_metadata():
            score += 1.0
        else:
            self.violations.append(ComplianceViolation(
                standard="FAIR-F2",
                category="Findable",
                severity="MEDIUM",
                violation_id="FAIR_F2_POOR_METADATA",
                title="Insufficient Metadata",
                description="Project metadata lacks richness and detail",
                affected_component="Metadata documentation",
                requirement="F2: Data are described with rich metadata",
                current_state="Basic or missing metadata",
                recommended_action="Enhance metadata with detailed descriptions, keywords, and context",
                compliance_score=0.3
            ))

        # Check for searchability
        total_checks += 1
        if await self._is_searchable():
            score += 1.0

        return score / total_checks if total_checks > 0 else 0.0

    async def _assess_accessibility(self) -> float:
        """Assess Accessible component of FAIR principles."""
        score = 0.0
        total_checks = 0

        # Check for standardized access protocols
        total_checks += 1
        if await self._has_standard_protocols():
            score += 1.0
        else:
            self.violations.append(ComplianceViolation(
                standard="FAIR-A1",
                category="Accessible",
                severity="HIGH",
                violation_id="FAIR_A1_NO_STANDARD_PROTOCOL",
                title="Non-standard Access Protocol",
                description="Data access doesn't use standardized protocols",
                affected_component="API endpoints",
                requirement="A1: (Meta)data are retrievable by their identifier using standardized protocol",
                current_state="Custom or non-standard access methods",
                recommended_action="Implement REST API, OAI-PMH, or other standard protocols",
                compliance_score=0.2
            ))

        # Check for authentication and authorization clarity
        total_checks += 1
        if await self._has_clear_access_conditions():
            score += 1.0

        # Check for metadata accessibility even when data is not
        total_checks += 1
        if await self._metadata_always_accessible():
            score += 1.0

        return score / total_checks if total_checks > 0 else 0.0

    async def _assess_interoperability(self) -> float:
        """Assess Interoperable component of FAIR principles."""
        score = 0.0
        total_checks = 0

        # Check for standard data formats
        total_checks += 1
        if await self._uses_standard_formats():
            score += 1.0
        else:
            self.violations.append(ComplianceViolation(
                standard="FAIR-I1",
                category="Interoperable",
                severity="MEDIUM",
                violation_id="FAIR_I1_PROPRIETARY_FORMATS",
                title="Proprietary Data Formats",
                description="Data uses proprietary or non-standard formats",
                affected_component="Data storage and exchange",
                requirement="I1: (Meta)data use formal, accessible, shared, and broadly applicable language",
                current_state="Proprietary formats detected",
                recommended_action="Convert to standard formats (JSON, CSV, HDF5, etc.)",
                compliance_score=0.4
            ))

        # Check for controlled vocabularies
        total_checks += 1
        if await self._uses_controlled_vocabularies():
            score += 1.0

        # Check for semantic standards
        total_checks += 1
        if await self._uses_semantic_standards():
            score += 1.0

        return score / total_checks if total_checks > 0 else 0.0

    async def _assess_reusability(self) -> float:
        """Assess Reusable component of FAIR principles."""
        score = 0.0
        total_checks = 0

        # Check for clear licensing
        total_checks += 1
        if await self._has_clear_license():
            score += 1.0
        else:
            self.violations.append(ComplianceViolation(
                standard="FAIR-R1",
                category="Reusable",
                severity="CRITICAL",
                violation_id="FAIR_R1_NO_LICENSE",
                title="Missing License",
                description="No clear license specified for data and code reuse",
                affected_component="Legal framework",
                requirement="R1: (Meta)data are richly described with accurate and relevant attributes",
                current_state="No license file found",
                recommended_action="Add appropriate open source license (MIT, Apache, CC, etc.)",
                compliance_score=0.0
            ))

        # Check for provenance information
        total_checks += 1
        if await self._has_provenance_info():
            score += 1.0

        # Check for quality standards
        total_checks += 1
        if await self._meets_quality_standards():
            score += 1.0

        return score / total_checks if total_checks > 0 else 0.0

    # Reproducibility Assessment Methods

    async def _assess_computational_reproducibility(self) -> float:
        """Assess computational reproducibility."""
        score = 0.0
        total_checks = 0

        # Check for requirements.txt or equivalent
        total_checks += 1
        req_files = ["requirements.txt", "environment.yml", "Pipfile", "pyproject.toml"]
        if any((self.project_root / f).exists() for f in req_files):
            score += 1.0
        else:
            self.violations.append(ComplianceViolation(
                standard="REPRODUCIBILITY-COMP1",
                category="Computational",
                severity="HIGH",
                violation_id="REPRO_COMP1_NO_DEPS",
                title="Missing Dependency Specification",
                description="No dependency specification file found",
                affected_component="Environment setup",
                requirement="Explicit dependency management for reproducible environments",
                current_state="No requirements.txt, environment.yml, or equivalent",
                recommended_action="Create requirements.txt or equivalent dependency file",
                compliance_score=0.1
            ))

        # Check for version pinning
        total_checks += 1
        if await self._has_version_pinning():
            score += 1.0

        # Check for deterministic algorithms
        total_checks += 1
        if await self._uses_deterministic_algorithms():
            score += 1.0
        else:
            self.violations.append(ComplianceViolation(
                standard="REPRODUCIBILITY-COMP2",
                category="Computational",
                severity="MEDIUM",
                violation_id="REPRO_COMP2_NON_DETERMINISTIC",
                title="Non-deterministic Algorithms",
                description="Code may use non-deterministic algorithms without seed management",
                affected_component="Algorithm implementation",
                requirement="Deterministic or properly seeded random processes",
                current_state="Potential non-deterministic behavior detected",
                recommended_action="Implement seed management for random processes",
                compliance_score=0.6
            ))

        return score / total_checks if total_checks > 0 else 0.0

    async def _assess_data_reproducibility(self) -> float:
        """Assess data reproducibility."""
        score = 0.0
        total_checks = 0

        # Check for data versioning
        total_checks += 1
        if await self._has_data_versioning():
            score += 1.0
        else:
            self.violations.append(ComplianceViolation(
                standard="REPRODUCIBILITY-DATA1",
                category="Data",
                severity="HIGH",
                violation_id="REPRO_DATA1_NO_VERSIONING",
                title="No Data Versioning",
                description="Data lacks version control or versioning system",
                affected_component="Data management",
                requirement="Version-controlled data for reproducible analysis",
                current_state="No data versioning detected",
                recommended_action="Implement DVC, Git LFS, or similar data versioning",
                compliance_score=0.2
            ))

        # Check for data provenance
        total_checks += 1
        if await self._has_data_provenance():
            score += 1.0

        # Check for data validation
        total_checks += 1
        if await self._has_data_validation():
            score += 1.0

        return score / total_checks if total_checks > 0 else 0.0

    async def _assess_documentation_reproducibility(self) -> float:
        """Assess documentation reproducibility."""
        score = 0.0
        total_checks = 0

        # Check for comprehensive README
        total_checks += 1
        readme_score = await self._assess_readme_quality()
        score += readme_score

        # Check for methodology documentation
        total_checks += 1
        if await self._has_methodology_docs():
            score += 1.0
        else:
            self.violations.append(ComplianceViolation(
                standard="REPRODUCIBILITY-DOC1",
                category="Documentation",
                severity="MEDIUM",
                violation_id="REPRO_DOC1_NO_METHODOLOGY",
                title="Missing Methodology Documentation",
                description="Insufficient documentation of scientific methodology",
                affected_component="Documentation",
                requirement="Detailed methodology documentation for reproducibility",
                current_state="Limited or missing methodology documentation",
                recommended_action="Create comprehensive methodology documentation",
                compliance_score=0.3
            ))

        # Check for API documentation
        total_checks += 1
        if await self._has_api_documentation():
            score += 1.0

        return score / total_checks if total_checks > 0 else 0.0

    async def _assess_environment_reproducibility(self) -> float:
        """Assess environment reproducibility."""
        score = 0.0
        total_checks = 0

        # Check for containerization
        total_checks += 1
        container_files = ["Dockerfile", "docker-compose.yml", "singularity.def"]
        if any((self.project_root / f).exists() for f in container_files):
            score += 1.0
        else:
            self.violations.append(ComplianceViolation(
                standard="REPRODUCIBILITY-ENV1",
                category="Environment",
                severity="MEDIUM",
                violation_id="REPRO_ENV1_NO_CONTAINER",
                title="No Containerization",
                description="Environment not containerized for reproducibility",
                affected_component="Environment setup",
                requirement="Containerized environment for consistent reproduction",
                current_state="No Docker, Singularity, or similar found",
                recommended_action="Create Dockerfile or equivalent container specification",
                compliance_score=0.4
            ))

        # Check for CI/CD configuration
        total_checks += 1
        ci_files = [".github/workflows", ".gitlab-ci.yml", "jenkins", ".circleci"]
        if any((self.project_root / f).exists() for f in ci_files):
            score += 1.0

        # Check for environment variables documentation
        total_checks += 1
        if (self.project_root / ".env.example").exists() or await self._has_env_docs():
            score += 1.0

        return score / total_checks if total_checks > 0 else 0.0

    # Helper Methods for Compliance Checks

    async def _has_persistent_identifier(self) -> bool:
        """Check if project has persistent identifier."""
        # Check for DOI in README or metadata
        readme_files = ["README.md", "README.rst", "README.txt"]
        doi_pattern = r"doi\.org|DOI:|doi:"

        for readme_file in readme_files:
            file_path = self.project_root / readme_file
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if re.search(doi_pattern, content, re.IGNORECASE):
                        return True
                except Exception:
                    continue

        # Check metadata files
        metadata_files = ["CITATION.cff", "codemeta.json", "datacite.yml"]
        for meta_file in metadata_files:
            if (self.project_root / meta_file).exists():
                return True

        return False

    async def _has_rich_metadata(self) -> bool:
        """Check if project has rich metadata."""
        readme_path = self.project_root / "README.md"
        if not readme_path.exists():
            return False

        try:
            content = readme_path.read_text(encoding='utf-8')
            # Check for key metadata elements
            required_elements = [
                r"author|contributor|creator",
                r"description|abstract|summary",
                r"keyword|tag|topic",
                r"license|licensing",
                r"citation|cite|reference"
            ]

            found_elements = sum(1 for pattern in required_elements
                               if re.search(pattern, content, re.IGNORECASE))

            return found_elements >= 3  # At least 3 out of 5 elements
        except Exception:
            return False

    async def _is_searchable(self) -> bool:
        """Check if project is searchable/discoverable."""
        # Check for presence in package indexes or repositories
        setup_files = ["setup.py", "pyproject.toml", "package.json"]
        return any((self.project_root / f).exists() for f in setup_files)

    async def _has_standard_protocols(self) -> bool:
        """Check if data uses standard access protocols."""
        # Look for REST API, GraphQL, or standard protocols
        api_indicators = [
            "app/routers", "api", "endpoints",
            "swagger", "openapi", "graphql"
        ]

        for indicator in api_indicators:
            if (self.project_root / indicator).exists():
                return True

        # Check for protocol documentation
        try:
            readme_content = (self.project_root / "README.md").read_text(encoding='utf-8')
            protocol_patterns = [
                r"REST|RESTful", r"GraphQL", r"OpenAPI",
                r"HTTP API", r"Web API", r"SPARQL"
            ]
            return any(re.search(pattern, readme_content, re.IGNORECASE)
                      for pattern in protocol_patterns)
        except Exception:
            return False

    async def _has_clear_access_conditions(self) -> bool:
        """Check for clear access conditions."""
        # Check for authentication documentation
        auth_docs = ["auth", "authentication", "authorization", "access"]
        doc_dirs = ["docs", "documentation", "."]

        for doc_dir in doc_dirs:
            dir_path = self.project_root / doc_dir
            if dir_path.exists():
                for auth_term in auth_docs:
                    if any(auth_term in f.name.lower() for f in dir_path.rglob("*")):
                        return True

        return False

    async def _metadata_always_accessible(self) -> bool:
        """Check if metadata is always accessible."""
        # Metadata should be in repository even if data isn't
        metadata_files = [
            "README.md", "METADATA.json", "schema.json",
            "datacite.yml", "dublin_core.xml"
        ]
        return any((self.project_root / f).exists() for f in metadata_files)

    async def _uses_standard_formats(self) -> bool:
        """Check if standard data formats are used."""
        standard_formats = [
            ".json", ".csv", ".xml", ".yaml", ".yml",
            ".hdf5", ".h5", ".nc", ".parquet", ".arrow"
        ]

        data_dirs = ["data", "datasets", "results", "output"]
        for data_dir in data_dirs:
            dir_path = self.project_root / data_dir
            if dir_path.exists():
                for file_path in dir_path.rglob("*"):
                    if file_path.suffix.lower() in standard_formats:
                        return True

        return False

    async def _uses_controlled_vocabularies(self) -> bool:
        """Check for controlled vocabularies usage."""
        # Look for schema files or vocabulary definitions
        vocab_files = [
            "schema.json", "vocabulary.json", "ontology.owl",
            "terms.json", "glossary.md", "taxonomy.yaml"
        ]
        return any((self.project_root / f).exists() for f in vocab_files)

    async def _uses_semantic_standards(self) -> bool:
        """Check for semantic standards usage."""
        # Look for semantic web standards
        semantic_indicators = [
            "schema.org", "dublin_core", "datacite",
            "json-ld", "rdf", "owl", "skos"
        ]

        for _, _, files in os.walk(self.project_root):
            for file in files:
                if any(indicator in file.lower() for indicator in semantic_indicators):
                    return True

        return False

    async def _has_clear_license(self) -> bool:
        """Check for clear licensing."""
        license_files = ["LICENSE", "LICENSE.txt", "LICENSE.md", "COPYING"]
        if any((self.project_root / f).exists() for f in license_files):
            return True

        # Check for license in README
        try:
            readme_content = (self.project_root / "README.md").read_text(encoding='utf-8')
            license_patterns = [
                r"license|licensing", r"MIT|Apache|GPL|BSD|CC",
                r"rights|copyright", r"terms of use"
            ]
            return any(re.search(pattern, readme_content, re.IGNORECASE)
                      for pattern in license_patterns)
        except Exception:
            return False

    async def _has_provenance_info(self) -> bool:
        """Check for data provenance information."""
        provenance_files = [
            "PROVENANCE.md", "CHANGELOG.md", "HISTORY.md",
            "provenance.json", "lineage.json"
        ]
        return any((self.project_root / f).exists() for f in provenance_files)

    async def _meets_quality_standards(self) -> bool:
        """Check if project meets quality standards."""
        quality_indicators = [
            "tests", "test_", "spec_", ".github/workflows",
            "pytest.ini", "tox.ini", ".pre-commit-config.yaml"
        ]

        for indicator in quality_indicators:
            if any(indicator in str(p) for p in self.project_root.rglob("*")):
                return True

        return False

    async def _has_version_pinning(self) -> bool:
        """Check for dependency version pinning."""
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            try:
                content = req_file.read_text(encoding='utf-8')
                # Check for version specifications
                version_patterns = [r"==", r">=.*,<", r"~=", r"\^"]
                return any(re.search(pattern, content) for pattern in version_patterns)
            except Exception:
                return False
        return False

    async def _uses_deterministic_algorithms(self) -> bool:
        """Check for deterministic algorithm usage."""
        # Look for random seed management
        python_files = list(self.project_root.rglob("*.py"))
        seed_patterns = [
            r"random\.seed", r"np\.random\.seed", r"torch\.manual_seed",
            r"tf\.random\.set_seed", r"PYTHONHASHSEED"
        ]

        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                if any(re.search(pattern, content) for pattern in seed_patterns):
                    return True
            except Exception:
                continue

        return False

    async def _has_data_versioning(self) -> bool:
        """Check for data versioning."""
        versioning_indicators = [
            ".dvc", "dvc.yaml", ".gitattributes",
            "data_version", "version.json"
        ]
        return any((self.project_root / f).exists() for f in versioning_indicators)

    async def _has_data_provenance(self) -> bool:
        """Check for data provenance tracking."""
        return await self._has_provenance_info()

    async def _has_data_validation(self) -> bool:
        """Check for data validation."""
        validation_files = [
            "schema.json", "validate.py", "validation.py",
            "great_expectations", "pandera", "cerberus"
        ]

        for val_file in validation_files:
            if (self.project_root / val_file).exists():
                return True

            # Check in subdirectories
            for path in self.project_root.rglob("*"):
                if val_file in str(path):
                    return True

        return False

    async def _assess_readme_quality(self) -> float:
        """Assess README quality for reproducibility."""
        readme_path = self.project_root / "README.md"
        if not readme_path.exists():
            return 0.0

        try:
            content = readme_path.read_text(encoding='utf-8')

            # Check for essential sections
            sections = [
                r"installation|install|setup",
                r"usage|example|demo",
                r"requirements|dependencies",
                r"license|licensing",
                r"citation|cite|reference"
            ]

            score = sum(1 for section in sections
                       if re.search(section, content, re.IGNORECASE))

            return score / len(sections)
        except Exception:
            return 0.0

    async def _has_methodology_docs(self) -> bool:
        """Check for methodology documentation."""
        method_files = [
            "METHODOLOGY.md", "METHODS.md", "APPROACH.md",
            "methodology", "methods", "approach"
        ]

        for method_file in method_files:
            if (self.project_root / method_file).exists():
                return True

            # Check in docs directory
            docs_dir = self.project_root / "docs"
            if docs_dir.exists():
                for path in docs_dir.rglob("*"):
                    if method_file in str(path).lower():
                        return True

        return False

    async def _has_api_documentation(self) -> bool:
        """Check for API documentation."""
        api_docs = [
            "swagger", "openapi", "redoc", "api_docs",
            "docs/api", "api.md", "endpoints.md"
        ]

        for api_doc in api_docs:
            if (self.project_root / api_doc).exists():
                return True

            # Check for documentation generators
            if any(api_doc in str(p) for p in self.project_root.rglob("*")):
                return True

        return False

    async def _has_env_docs(self) -> bool:
        """Check for environment variables documentation."""
        env_docs = [
            "ENVIRONMENT.md", "CONFIG.md", "SETUP.md",
            "environment", "configuration"
        ]

        for env_doc in env_docs:
            if (self.project_root / env_doc).exists():
                return True

        return False

    # Ethics and Open Science Assessment Methods

    async def _check_ethics_gate(self) -> float:
        """Check for ethics gate implementation."""
        ethics_files = [
            "app/services/ethics_gate.py",
            "ethics", "ethical_review", "ethics_config.yaml"
        ]

        for ethics_file in ethics_files:
            if (self.project_root / ethics_file).exists():
                return 1.0

        return 0.0

    async def _check_bias_detection(self) -> float:
        """Check for bias detection mechanisms."""
        bias_indicators = [
            "bias_detection", "fairness", "bias_audit",
            "equity", "discrimination"
        ]

        for indicator in bias_indicators:
            if any(indicator in str(p) for p in self.project_root.rglob("*")):
                return 1.0

        return 0.0

    async def _check_informed_consent(self) -> float:
        """Check for informed consent mechanisms."""
        consent_files = [
            "consent", "privacy_policy", "terms_of_service",
            "data_usage", "user_agreement"
        ]

        for consent_file in consent_files:
            if any(consent_file in str(p) for p in self.project_root.rglob("*")):
                return 1.0

        return 0.0

    async def _check_data_privacy(self) -> float:
        """Check for data privacy protection."""
        privacy_indicators = [
            "privacy", "gdpr", "anonymization", "pseudonymization",
            "data_protection", "pii", "personal_data"
        ]

        for indicator in privacy_indicators:
            if any(indicator in str(p) for p in self.project_root.rglob("*")):
                return 1.0

        return 0.0

    async def _check_explainability(self) -> float:
        """Check for AI explainability features."""
        explainability_indicators = [
            "explainable", "interpretable", "explanation",
            "lime", "shap", "xai", "interpretability"
        ]

        for indicator in explainability_indicators:
            if any(indicator in str(p) for p in self.project_root.rglob("*")):
                return 1.0

        return 0.0

    async def _check_open_source_licensing(self) -> float:
        """Check for open source licensing."""
        if await self._has_clear_license():
            license_file = None
            for lic_file in ["LICENSE", "LICENSE.txt", "LICENSE.md"]:
                if (self.project_root / lic_file).exists():
                    license_file = self.project_root / lic_file
                    break

            if license_file:
                try:
                    content = license_file.read_text(encoding='utf-8')
                    open_licenses = [
                        "MIT", "Apache", "GPL", "BSD", "Mozilla",
                        "Creative Commons", "CC", "Unlicense"
                    ]
                    if any(lic in content for lic in open_licenses):
                        return 1.0
                except Exception:
                    pass

        return 0.0

    async def _check_open_data(self) -> float:
        """Check for open data availability."""
        # Look for public data repositories or APIs
        open_data_indicators = [
            "api", "dataset", "open_data", "public_data",
            "zenodo", "figshare", "dryad", "osf"
        ]

        try:
            readme_content = (self.project_root / "README.md").read_text(encoding='utf-8')
            if any(indicator in readme_content.lower() for indicator in open_data_indicators):
                return 1.0
        except Exception:
            pass

        return 0.0

    async def _check_open_access(self) -> float:
        """Check for open access publications."""
        # Look for publication references or preprints
        publication_indicators = [
            "arxiv", "biorxiv", "preprint", "publication",
            "paper", "article", "journal", "conference"
        ]

        try:
            readme_content = (self.project_root / "README.md").read_text(encoding='utf-8')
            if any(indicator in readme_content.lower() for indicator in publication_indicators):
                return 1.0
        except Exception:
            pass

        return 0.0

    async def _check_collaboration_practices(self) -> float:
        """Check for collaborative development practices."""
        # Look for collaboration indicators
        collab_indicators = [
            ".github", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
            "CONTRIBUTORS.md", "pull_request_template"
        ]

        for indicator in collab_indicators:
            if (self.project_root / indicator).exists():
                return 1.0

        return 0.0

    def generate_compliance_report(
        self,
        fair_assessment: FAIRAssessment,
        reproducibility_assessment: ReproducibilityAssessment,
        ethics_score: float,
        open_science_score: float
    ) -> ComplianceReport:
        """Generate comprehensive compliance report."""

        # Calculate overall compliance score
        scores = [
            fair_assessment.overall_score,
            reproducibility_assessment.overall_score,
            ethics_score,
            open_science_score
        ]
        overall_score = sum(scores) / len(scores)

        # Count violations by severity
        all_violations = self.violations
        critical_count = sum(1 for v in all_violations if v.severity == "CRITICAL")
        high_count = sum(1 for v in all_violations if v.severity == "HIGH")
        medium_count = sum(1 for v in all_violations if v.severity == "MEDIUM")
        low_count = sum(1 for v in all_violations if v.severity == "LOW")

        # Determine compliance status
        if overall_score >= 0.8 and critical_count == 0 and high_count <= 2:
            status = "COMPLIANT"
        elif overall_score >= 0.6 and critical_count <= 1 and high_count <= 5:
            status = "PARTIALLY_COMPLIANT"
        else:
            status = "NON_COMPLIANT"

        return ComplianceReport(
            assessment_date=datetime.now(timezone.utc),
            project_name="AXIOM ATLAS",
            fair_assessment=fair_assessment,
            reproducibility_assessment=reproducibility_assessment,
            ethics_compliance_score=ethics_score,
            open_science_score=open_science_score,
            overall_compliance_score=overall_score,
            critical_violations=critical_count,
            high_violations=high_count,
            medium_violations=medium_count,
            low_violations=low_count,
            total_violations=len(all_violations),
            compliance_status=status
        )


class TestScientificCompliance:
    """Scientific compliance validation test suite."""

    @pytest.mark.compliance
    @pytest.mark.slow
    async def test_comprehensive_scientific_compliance(self) -> None:
        """Run comprehensive scientific compliance validation."""

        # Initialize validator
        project_root = "."
        validator = ScientificComplianceValidator(project_root)

        print("\n🔬 Starting Comprehensive Scientific Compliance Assessment...")

        # 1. FAIR Principles Validation
        print("\n📋 FAIR Principles Assessment...")
        fair_assessment = await validator.validate_fair_principles()

        # 2. Reproducibility Validation
        print("\n🔄 Reproducibility Assessment...")
        reproducibility_assessment = await validator.validate_reproducibility()

        # 3. Ethics Compliance Validation
        print("\n⚖️ Ethics Compliance Assessment...")
        ethics_score = await validator.validate_ethics_compliance()

        # 4. Open Science Practices Validation
        print("\n🌐 Open Science Practices Assessment...")
        open_science_score = await validator.validate_open_science_practices()

        # Generate comprehensive report
        compliance_report = validator.generate_compliance_report(
            fair_assessment=fair_assessment,
            reproducibility_assessment=reproducibility_assessment,
            ethics_score=ethics_score,
            open_science_score=open_science_score
        )

        # Print detailed report
        self._print_compliance_report(compliance_report)

        # Compliance assertions
        assert compliance_report.overall_compliance_score >= 0.6, \
            f"Overall compliance score too low: {compliance_report.overall_compliance_score:.2f}"

        assert compliance_report.critical_violations <= 2, \
            f"Too many critical violations: {compliance_report.critical_violations}"

        assert fair_assessment.overall_score >= 0.5, \
            f"FAIR principles score too low: {fair_assessment.overall_score:.2f}"

        assert reproducibility_assessment.overall_score >= 0.5, \
            f"Reproducibility score too low: {reproducibility_assessment.overall_score:.2f}"

        print("\n✅ Scientific compliance assessment completed!")
        print(f"🎯 Overall Compliance Status: {compliance_report.compliance_status}")
        print(f"📊 Overall Score: {compliance_report.overall_compliance_score:.2f}")

    def _print_compliance_report(self, report: ComplianceReport) -> None:
        """Print comprehensive compliance report."""
        print("\n" + "="*80)
        print("🔬 SCIENTIFIC COMPLIANCE ASSESSMENT REPORT")
        print("="*80)

        print("\n📋 REPORT DETAILS:")
        print(f"  Project: {report.project_name}")
        print(f"  Assessment Date: {report.assessment_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"  Overall Status: {report.compliance_status}")
        print(f"  Overall Score: {report.overall_compliance_score:.2f}")

        print("\n📊 COMPLIANCE SCORES:")
        print(f"  🔍 FAIR Principles: {report.fair_assessment.overall_score:.2f}")
        print(f"    - Findable: {report.fair_assessment.findable_score:.2f}")
        print(f"    - Accessible: {report.fair_assessment.accessible_score:.2f}")
        print(f"    - Interoperable: {report.fair_assessment.interoperable_score:.2f}")
        print(f"    - Reusable: {report.fair_assessment.reusable_score:.2f}")

        print(f"  🔄 Reproducibility: {report.reproducibility_assessment.overall_score:.2f}")
        print(f"    - Computational: {report.reproducibility_assessment.computational_score:.2f}")
        print(f"    - Data: {report.reproducibility_assessment.data_score:.2f}")
        print(f"    - Documentation: {report.reproducibility_assessment.documentation_score:.2f}")
        print(f"    - Environment: {report.reproducibility_assessment.environment_score:.2f}")

        print(f"  ⚖️ Ethics Compliance: {report.ethics_compliance_score:.2f}")
        print(f"  🌐 Open Science: {report.open_science_score:.2f}")

        print("\n⚠️ VIOLATIONS SUMMARY:")
        print(f"  🔴 Critical: {report.critical_violations}")
        print(f"  🟠 High: {report.high_violations}")
        print(f"  🟡 Medium: {report.medium_violations}")
        print(f"  🔵 Low: {report.low_violations}")
        print(f"  📊 Total: {report.total_violations}")

        # Show top violations
        if report.critical_violations > 0 or report.high_violations > 0:
            print("\n🚨 TOP PRIORITY VIOLATIONS:")
            all_violations = []
            all_violations.extend(report.fair_assessment.violations)
            all_violations.extend(report.reproducibility_assessment.violations)

            # Sort by severity
            severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
            top_violations = sorted(all_violations,
                                  key=lambda v: severity_order.get(v.severity, 4))[:5]

            for violation in top_violations:
                print(f"  🚨 {violation.severity}: {violation.title}")
                print(f"     Component: {violation.affected_component}")
                print(f"     Action: {violation.recommended_action}")

        # Show recommendations
        all_recommendations = []
        all_recommendations.extend(report.fair_assessment.recommendations)
        all_recommendations.extend(report.reproducibility_assessment.missing_components)

        if all_recommendations:
            print("\n💡 KEY RECOMMENDATIONS:")
            for i, recommendation in enumerate(all_recommendations[:5], 1):
                print(f"  {i}. {recommendation}")

        # Compliance roadmap
        print("\n🗺️ COMPLIANCE ROADMAP:")
        if report.compliance_status == "NON_COMPLIANT":
            print("  🔴 IMMEDIATE ACTION REQUIRED:")
            print("    1. Address all critical violations")
            print("    2. Implement basic FAIR principles")
            print("    3. Add essential documentation")
            print("    4. Establish reproducibility practices")
        elif report.compliance_status == "PARTIALLY_COMPLIANT":
            print("  🟡 IMPROVEMENT NEEDED:")
            print("    1. Resolve high-priority violations")
            print("    2. Enhance metadata and documentation")
            print("    3. Strengthen reproducibility measures")
            print("    4. Implement open science practices")
        else:
            print("  🟢 MAINTAIN COMPLIANCE:")
            print("    1. Regular compliance monitoring")
            print("    2. Continuous improvement")
            print("    3. Stay updated with standards")
            print("    4. Share best practices")

        print("="*80)