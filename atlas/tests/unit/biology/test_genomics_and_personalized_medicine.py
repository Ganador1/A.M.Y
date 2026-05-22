"""
Tests comprehensivos para servicios médicos - Genómica y Medicina Personalizada
===========================================================================

Suite de testing para AdvancedGenomicsService y PersonalizedMedicineService.
"""

import pytest
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import Dict, List, Any

from app.domains.medicine.advanced_genomics_service import (
    AdvancedGenomicsService, GenomicAnalysisType, VariantType,
    GenomicAnnotation, PharmacogenomicResult
)
from app.domains.medicine.personalized_medicine_service import (
    PersonalizedMedicineService, TreatmentRecommendation, RiskAssessment,
    BiomarkerProfile, ClinicalTrial
)


class TestAdvancedGenomicsService:
    """Test suite para AdvancedGenomicsService"""

    @pytest.fixture
    def genomics_service(self):
        """Fixture para AdvancedGenomicsService"""
        service = AdvancedGenomicsService()
        service.initialize()
        return service

    @pytest.fixture
    def sample_vcf_data(self):
        """Fixture para datos VCF simulados"""
        return {
            "variants": [
                {
                    "chromosome": "chr1",
                    "position": 1234567,
                    "ref_allele": "A",
                    "alt_allele": "G",
                    "quality_score": 95.5,
                    "genotype": "0/1",
                    "read_depth": 45
                },
                {
                    "chromosome": "chr2",
                    "position": 2345678,
                    "ref_allele": "C",
                    "alt_allele": "T",
                    "quality_score": 87.3,
                    "genotype": "1/1",
                    "read_depth": 38
                }
            ],
            "sample_id": "PATIENT_GENOMICS_001",
            "analysis_pipeline": "GATK_v4.2",
            "reference_genome": "GRCh38"
        }

    @pytest.fixture
    def sample_rna_seq_data(self):
        """Fixture para datos RNA-seq simulados"""
        return {
            "gene_expression": {
                "BRCA1": 15.7,
                "BRCA2": 12.3,
                "TP53": 8.9,
                "EGFR": 22.1,
                "KRAS": 11.5
            },
            "sample_id": "RNA_SEQ_001",
            "library_type": "stranded",
            "sequencing_depth": 50000000
        }

    def test_service_initialization(self, genomics_service):
        """Test inicialización del servicio de genómica"""
        assert genomics_service.is_initialized
        assert genomics_service.supported_file_formats == ["vcf", "bed", "fastq", "bam", "gff3"]
        assert len(genomics_service.annotation_databases) > 0
        assert "clinvar" in genomics_service.annotation_databases
        assert "dbsnp" in genomics_service.annotation_databases

    @pytest.mark.asyncio
    async def test_variant_calling_analysis(self, genomics_service, sample_vcf_data):
        """Test análisis de variant calling"""
        with patch.object(genomics_service, '_run_variant_calling') as mock_vc:
            mock_vc.return_value = {
                "total_variants": 4567890,
                "snvs": 4123456,
                "indels": 444434,
                "structural_variants": 12,
                "quality_metrics": {
                    "mean_quality_score": 92.1,
                    "pass_rate": 0.94,
                    "titv_ratio": 2.08
                },
                "processing_time_minutes": 45.7
            }
            
            result = await genomics_service.analyze_genomic_data(
                data=sample_vcf_data,
                analysis_type=GenomicAnalysisType.VARIANT_CALLING,
                reference_genome="GRCh38"
            )
            
            assert result["total_variants"] == 4567890
            assert result["quality_metrics"]["titv_ratio"] > 2.0  # Expected Ti/Tv ratio
            assert result["processing_time_minutes"] < 60
            mock_vc.assert_called_once()

    @pytest.mark.asyncio
    async def test_pharmacogenomics_analysis(self, genomics_service, sample_vcf_data):
        """Test análisis farmacogenómico"""
        with patch.object(genomics_service, '_analyze_pharmacogenomics') as mock_pgx:
            mock_pgx.return_value = PharmacogenomicResult(
                patient_id="PGX_TEST_001",
                drug_recommendations={
                    "warfarin": {
                        "dosage_adjustment": "reduce_25_percent",
                        "confidence": 0.92,
                        "relevant_variants": ["CYP2C9*2", "VKORC1"],
                        "evidence_level": "1A"
                    },
                    "clopidogrel": {
                        "dosage_adjustment": "alternative_medication",
                        "confidence": 0.88,
                        "relevant_variants": ["CYP2C19*2"],
                        "evidence_level": "1A"
                    }
                },
                metabolizer_phenotypes={
                    "CYP2D6": "extensive_metabolizer",
                    "CYP2C19": "poor_metabolizer",
                    "CYP2C9": "intermediate_metabolizer"
                }
            )
            
            result = await genomics_service.perform_pharmacogenomic_analysis(
                genomic_data=sample_vcf_data,
                drug_list=["warfarin", "clopidogrel", "simvastatin"]
            )
            
            assert "warfarin" in result.drug_recommendations
            assert result.drug_recommendations["warfarin"]["confidence"] > 0.9
            assert result.metabolizer_phenotypes["CYP2C19"] == "poor_metabolizer"
            mock_pgx.assert_called_once()

    @pytest.mark.asyncio
    async def test_structural_variant_detection(self, genomics_service):
        """Test detección de variantes estructurales"""
        structural_data = {
            "bam_file": "/path/to/aligned.bam",
            "reference_genome": "GRCh38",
            "sample_id": "SV_TEST_001"
        }
        
        with patch.object(genomics_service, '_detect_structural_variants') as mock_sv:
            mock_sv.return_value = {
                "deletions": [
                    {"chromosome": "chr1", "start": 1000000, "end": 1005000, "size": 5000},
                    {"chromosome": "chr3", "start": 2000000, "end": 2001500, "size": 1500}
                ],
                "insertions": [
                    {"chromosome": "chr2", "position": 1500000, "size": 300, "sequence": "N" * 300}
                ],
                "duplications": [
                    {"chromosome": "chr4", "start": 3000000, "end": 3002000, "copy_number": 3}
                ],
                "translocations": [
                    {"chr1": "chr1", "pos1": 4000000, "chr2": "chr5", "pos2": 1000000}
                ],
                "total_structural_variants": 5
            }
            
            result = await genomics_service.detect_structural_variants(structural_data)
            
            assert result["total_structural_variants"] == 5
            assert len(result["deletions"]) == 2
            assert result["deletions"][0]["size"] == 5000
            assert len(result["translocations"]) == 1
            mock_sv.assert_called_once()

    @pytest.mark.asyncio
    async def test_rna_seq_analysis(self, genomics_service, sample_rna_seq_data):
        """Test análisis RNA-seq"""
        with patch.object(genomics_service, '_analyze_rna_expression') as mock_rna:
            mock_rna.return_value = {
                "differentially_expressed_genes": {
                    "upregulated": ["BRCA1", "TP53", "ATM"],
                    "downregulated": ["EGFR", "MYC"],
                    "total_de_genes": 5
                },
                "pathway_enrichment": {
                    "DNA_repair": {"p_value": 0.001, "genes": ["BRCA1", "TP53", "ATM"]},
                    "cell_cycle": {"p_value": 0.005, "genes": ["TP53", "MYC"]}
                },
                "expression_outliers": ["BRCA1"],
                "fusion_genes": []
            }
            
            result = await genomics_service.analyze_rna_expression(
                expression_data=sample_rna_seq_data,
                comparison_group="normal_tissue",
                fold_change_threshold=2.0
            )
            
            assert result["differentially_expressed_genes"]["total_de_genes"] == 5
            assert "BRCA1" in result["differentially_expressed_genes"]["upregulated"]
            assert result["pathway_enrichment"]["DNA_repair"]["p_value"] < 0.05
            mock_rna.assert_called_once()

    @pytest.mark.asyncio
    async def test_variant_annotation(self, genomics_service, sample_vcf_data):
        """Test anotación de variantes"""
        with patch.object(genomics_service, '_annotate_variants') as mock_ann:
            mock_ann.return_value = [
                GenomicAnnotation(
                    variant_id="chr1:1234567:A>G",
                    gene_symbol="GENE1",
                    transcript_id="NM_001234",
                    consequence="missense_variant",
                    amino_acid_change="p.Ala123Val",
                    clinical_significance="likely_pathogenic",
                    population_frequency=0.001,
                    pathogenicity_scores={
                        "CADD": 25.3,
                        "SIFT": 0.02,
                        "PolyPhen": 0.95
                    }
                ),
                GenomicAnnotation(
                    variant_id="chr2:2345678:C>T",
                    gene_symbol="GENE2",
                    transcript_id="NM_005678",
                    consequence="synonymous_variant",
                    amino_acid_change="p.Ser456Ser",
                    clinical_significance="benign",
                    population_frequency=0.15,
                    pathogenicity_scores={
                        "CADD": 5.1,
                        "SIFT": 1.0,
                        "PolyPhen": 0.01
                    }
                )
            ]
            
            annotations = await genomics_service.annotate_variants(
                variants=sample_vcf_data["variants"],
                annotation_sources=["clinvar", "dbsnp", "ensembl"]
            )
            
            assert len(annotations) == 2
            assert annotations[0].clinical_significance == "likely_pathogenic"
            assert annotations[1].consequence == "synonymous_variant"
            assert annotations[0].pathogenicity_scores["CADD"] > 20  # High impact
            mock_ann.assert_called_once()

    @pytest.mark.asyncio
    async def test_copy_number_variation_analysis(self, genomics_service):
        """Test análisis de variación del número de copias (CNV)"""
        cnv_data = {
            "bam_file": "/path/to/sample.bam",
            "reference_genome": "GRCh38",
            "sample_id": "CNV_TEST_001"
        }
        
        with patch.object(genomics_service, '_analyze_copy_number') as mock_cnv:
            mock_cnv.return_value = {
                "cnv_segments": [
                    {
                        "chromosome": "chr17",
                        "start": 41196312,
                        "end": 41277500,
                        "copy_number": 1,  # Deletion in BRCA1 region
                        "log2_ratio": -1.0,
                        "significance": 0.001
                    },
                    {
                        "chromosome": "chr8",
                        "start": 128748315,
                        "end": 128753680,
                        "copy_number": 4,  # Amplification in MYC region
                        "log2_ratio": 1.0,
                        "significance": 0.005
                    }
                ],
                "total_cnvs": 2,
                "genome_wide_instability_score": 0.15
            }
            
            result = await genomics_service.analyze_copy_number_variations(cnv_data)
            
            assert result["total_cnvs"] == 2
            assert result["cnv_segments"][0]["copy_number"] == 1  # Deletion
            assert result["cnv_segments"][1]["copy_number"] == 4  # Amplification
            assert result["genome_wide_instability_score"] < 0.2
            mock_cnv.assert_called_once()


class TestPersonalizedMedicineService:
    """Test suite para PersonalizedMedicineService"""

    @pytest.fixture
    def medicine_service(self):
        """Fixture para PersonalizedMedicineService"""
        service = PersonalizedMedicineService()
        service.initialize()
        return service

    @pytest.fixture
    def patient_profile(self):
        """Fixture para perfil de paciente"""
        return {
            "patient_id": "PM_TEST_001",
            "age": 45,
            "gender": "female",
            "medical_history": ["breast_cancer", "diabetes_type_2"],
            "current_medications": ["metformin", "tamoxifen"],
            "allergies": ["penicillin"],
            "genomic_profile": {
                "BRCA1_mutation": True,
                "BRCA2_mutation": False,
                "pharmacogenomic_variants": {
                    "CYP2D6": "*1/*4",
                    "CYP2C19": "*2/*2"
                }
            },
            "biomarkers": {
                "ER": "positive",
                "PR": "positive", 
                "HER2": "negative",
                "Ki67": 15.5
            }
        }

    def test_service_initialization(self, medicine_service):
        """Test inicialización del servicio de medicina personalizada"""
        assert medicine_service.is_initialized
        assert len(medicine_service.treatment_protocols) > 0
        assert len(medicine_service.drug_databases) > 0
        assert "oncology" in medicine_service.specialty_modules
        assert "cardiology" in medicine_service.specialty_modules

    @pytest.mark.asyncio
    async def test_generate_treatment_recommendation(self, medicine_service, patient_profile):
        """Test generación de recomendaciones de tratamiento"""
        with patch.object(medicine_service, '_analyze_treatment_options') as mock_treatment:
            mock_treatment.return_value = TreatmentRecommendation(
                patient_id="PM_TEST_001",
                condition="breast_cancer",
                recommended_treatments=[
                    {
                        "treatment_name": "letrozole",
                        "treatment_type": "hormonal_therapy",
                        "confidence_score": 0.92,
                        "rationale": "ER/PR positive, post-menopausal",
                        "expected_efficacy": 0.85,
                        "side_effects_risk": "moderate",
                        "contraindications": []
                    },
                    {
                        "treatment_name": "CDK4/6_inhibitor",
                        "treatment_type": "targeted_therapy",
                        "confidence_score": 0.88,
                        "rationale": "Advanced ER+ disease, Ki67 moderate",
                        "expected_efficacy": 0.78,
                        "side_effects_risk": "high",
                        "contraindications": ["severe_hepatic_impairment"]
                    }
                ],
                genomic_considerations={
                    "BRCA1_mutation": "Consider PARP inhibitors as second-line",
                    "CYP2D6_poor_metabolizer": "Avoid tamoxifen, prefer aromatase inhibitors"
                }
            )
            
            recommendation = await medicine_service.generate_treatment_recommendation(
                patient_profile=patient_profile,
                condition="breast_cancer",
                treatment_goals=["disease_control", "quality_of_life"]
            )
            
            assert len(recommendation.recommended_treatments) == 2
            assert recommendation.recommended_treatments[0]["confidence_score"] > 0.9
            assert "BRCA1_mutation" in recommendation.genomic_considerations
            mock_treatment.assert_called_once()

    @pytest.mark.asyncio
    async def test_risk_assessment(self, medicine_service, patient_profile):
        """Test evaluación de riesgo"""
        with patch.object(medicine_service, '_calculate_risk_scores') as mock_risk:
            mock_risk.return_value = RiskAssessment(
                patient_id="PM_TEST_001",
                risk_scores={
                    "breast_cancer_recurrence": {
                        "score": 0.35,
                        "risk_level": "moderate",
                        "factors": ["BRCA1_mutation", "ER_positive", "age_45"]
                    },
                    "cardiovascular_disease": {
                        "score": 0.15,
                        "risk_level": "low",
                        "factors": ["diabetes", "female_gender"]
                    },
                    "drug_toxicity": {
                        "score": 0.25,
                        "risk_level": "moderate",
                        "factors": ["CYP2D6_poor_metabolizer", "multiple_medications"]
                    }
                },
                recommendations=[
                    "Monitor cardiac function during treatment",
                    "Consider genetic counseling for family members",
                    "Regular mammographic surveillance"
                ]
            )
            
            risk_assessment = await medicine_service.assess_patient_risks(
                patient_profile=patient_profile,
                risk_categories=["disease_recurrence", "treatment_toxicity", "comorbidities"]
            )
            
            assert len(risk_assessment.risk_scores) == 3
            assert risk_assessment.risk_scores["breast_cancer_recurrence"]["score"] == 0.35
            assert "BRCA1_mutation" in risk_assessment.risk_scores["breast_cancer_recurrence"]["factors"]
            assert len(risk_assessment.recommendations) > 0
            mock_risk.assert_called_once()

    @pytest.mark.asyncio
    async def test_biomarker_analysis(self, medicine_service, patient_profile):
        """Test análisis de biomarcadores"""
        with patch.object(medicine_service, '_analyze_biomarker_profile') as mock_biomarker:
            mock_biomarker.return_value = BiomarkerProfile(
                patient_id="PM_TEST_001",
                biomarker_results={
                    "ER": {"status": "positive", "percentage": 85, "significance": "treatment_selection"},
                    "PR": {"status": "positive", "percentage": 70, "significance": "prognosis"},
                    "HER2": {"status": "negative", "score": "1+", "significance": "treatment_exclusion"},
                    "Ki67": {"percentage": 15.5, "interpretation": "moderate_proliferation", "significance": "prognosis"}
                },
                treatment_implications={
                    "hormonal_therapy": "strongly_indicated",
                    "chemotherapy": "consider_based_on_other_factors",
                    "targeted_therapy": "HER2_negative_excludes_trastuzumab"
                },
                prognostic_factors={
                    "overall_prognosis": "good",
                    "recurrence_risk": "intermediate"
                }
            )
            
            biomarker_analysis = await medicine_service.analyze_biomarkers(
                biomarker_data=patient_profile["biomarkers"],
                cancer_type="breast_cancer"
            )
            
            assert biomarker_analysis.biomarker_results["ER"]["status"] == "positive"
            assert biomarker_analysis.treatment_implications["hormonal_therapy"] == "strongly_indicated"
            assert biomarker_analysis.prognostic_factors["overall_prognosis"] == "good"
            mock_biomarker.assert_called_once()

    @pytest.mark.asyncio
    async def test_clinical_trial_matching(self, medicine_service, patient_profile):
        """Test emparejamiento con ensayos clínicos"""
        with patch.object(medicine_service, '_search_clinical_trials') as mock_trials:
            mock_trials.return_value = [
                ClinicalTrial(
                    trial_id="NCT12345678",
                    title="Phase III Study of CDK4/6 Inhibitor in BRCA+ Breast Cancer",
                    phase="3",
                    status="recruiting",
                    eligibility_criteria=[
                        "BRCA1 or BRCA2 mutation positive",
                        "ER/PR positive breast cancer",
                        "Age 18-75 years"
                    ],
                    primary_endpoint="progression_free_survival",
                    locations=["Memorial Sloan Kettering", "Dana Farber"],
                    match_score=0.94,
                    match_reasons=[
                        "BRCA1_mutation_positive",
                        "ER_PR_positive",
                        "age_appropriate"
                    ]
                ),
                ClinicalTrial(
                    trial_id="NCT87654321",
                    title="Biomarker-Driven Treatment Selection Study",
                    phase="2",
                    status="recruiting",
                    eligibility_criteria=[
                        "Metastatic breast cancer",
                        "Previous endocrine therapy"
                    ],
                    primary_endpoint="overall_response_rate",
                    locations=["Mayo Clinic", "Johns Hopkins"],
                    match_score=0.76,
                    match_reasons=[
                        "breast_cancer_diagnosis",
                        "previous_hormonal_therapy"
                    ]
                )
            ]
            
            trials = await medicine_service.find_matching_clinical_trials(
                patient_profile=patient_profile,
                condition="breast_cancer",
                max_results=10
            )
            
            assert len(trials) == 2
            assert trials[0].match_score > 0.9
            assert "BRCA1_mutation_positive" in trials[0].match_reasons
            assert trials[0].phase == "3"
            mock_trials.assert_called_once()

    @pytest.mark.asyncio
    async def test_drug_interaction_analysis(self, medicine_service, patient_profile):
        """Test análisis de interacciones medicamentosas"""
        new_medication = "palbociclib"
        
        with patch.object(medicine_service, '_analyze_drug_interactions') as mock_interactions:
            mock_interactions.return_value = {
                "major_interactions": [
                    {
                        "drugs": ["palbociclib", "tamoxifen"],
                        "interaction_type": "metabolic",
                        "severity": "moderate",
                        "mechanism": "CYP3A4_inhibition",
                        "clinical_effect": "increased_tamoxifen_levels",
                        "recommendation": "monitor_closely"
                    }
                ],
                "minor_interactions": [],
                "contraindications": [],
                "dosage_adjustments": [
                    {
                        "drug": "palbociclib",
                        "adjustment": "reduce_dose_to_100mg",
                        "reason": "CYP2D6_poor_metabolizer"
                    }
                ]
            }
            
            interactions = await medicine_service.analyze_drug_interactions(
                current_medications=patient_profile["current_medications"],
                new_medication=new_medication,
                patient_genomics=patient_profile["genomic_profile"]
            )
            
            assert len(interactions["major_interactions"]) == 1
            assert interactions["major_interactions"][0]["severity"] == "moderate"
            assert len(interactions["dosage_adjustments"]) == 1
            assert interactions["dosage_adjustments"][0]["drug"] == "palbociclib"
            mock_interactions.assert_called_once()

    @pytest.mark.asyncio
    async def test_treatment_response_prediction(self, medicine_service, patient_profile):
        """Test predicción de respuesta al tratamiento"""
        treatment_plan = {
            "primary_treatment": "letrozole",
            "combination_therapy": "CDK4/6_inhibitor",
            "duration_months": 24
        }
        
        with patch.object(medicine_service, '_predict_treatment_response') as mock_prediction:
            mock_prediction.return_value = {
                "response_probability": {
                    "complete_response": 0.15,
                    "partial_response": 0.65,
                    "stable_disease": 0.15,
                    "progressive_disease": 0.05
                },
                "predicted_pfs_months": 28.5,
                "confidence_interval": [22.1, 35.8],
                "factors_influencing_response": {
                    "positive": ["ER_positive", "PR_positive", "low_Ki67"],
                    "negative": ["BRCA1_mutation", "age_under_50"]
                },
                "biomarkers_for_monitoring": ["CA15-3", "CEA", "circulating_tumor_cells"]
            }
            
            prediction = await medicine_service.predict_treatment_response(
                patient_profile=patient_profile,
                treatment_plan=treatment_plan
            )
            
            assert prediction["response_probability"]["partial_response"] > 0.5
            assert prediction["predicted_pfs_months"] > 24
            assert "ER_positive" in prediction["factors_influencing_response"]["positive"]
            assert len(prediction["biomarkers_for_monitoring"]) > 0
            mock_prediction.assert_called_once()


if __name__ == "__main__":
    # Ejecutar tests específicos
    pytest.main([__file__, "-v", "--tb=short"])
