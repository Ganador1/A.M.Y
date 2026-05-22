"""
Supplementary Materials Generation Example - AXIOM META 4
Demonstrates automated generation of supplementary materials for scientific publications.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.supplementary_materials_generator import SupplementaryMaterialsGenerator


async def example_supplementary_package():
    """Example of generating complete supplementary materials package"""
    print("📚 Generating Complete Supplementary Materials Package...")
    
    generator = SupplementaryMaterialsGenerator()
    
    # Sample publication data
    publication_data = {
        "publication_id": "pub_20250101_001",
        "materials_config": {
            "include_extended_methods": True,
            "include_supplementary_data": True,
            "include_protocols": True,
            "include_supplementary_figures": True,
            "include_supplementary_tables": True,
            "figures_count": 3,
            "tables_count": 2
        },
        "experimental_data": {
            "overview": "This study employed advanced machine learning techniques for autonomous scientific discovery.",
            "protocols": [
                {
                    "name": "Neural Network Training Protocol",
                    "objective": "Train neural networks for scientific hypothesis generation",
                    "materials": ["Training dataset", "GPU computing resources", "Python libraries"],
                    "procedure": [
                        "Data preprocessing and cleaning",
                        "Model architecture design",
                        "Hyperparameter optimization",
                        "Training with validation",
                        "Model evaluation and testing"
                    ],
                    "expected_results": "Trained model capable of generating scientific hypotheses",
                    "troubleshooting": [
                        {"problem": "Overfitting", "solution": "Implement dropout and regularization"},
                        {"problem": "Slow convergence", "solution": "Adjust learning rate and batch size"}
                    ]
                }
            ],
            "equipment": [
                {
                    "name": "High-Performance Computing Cluster",
                    "type": "Computing Infrastructure",
                    "manufacturer": "AXIOM Technologies",
                    "model": "HPC-5000",
                    "settings": "GPU acceleration enabled",
                    "calibration": "Daily performance monitoring"
                }
            ],
            "reagents": [
                {
                    "name": "Scientific Literature Dataset",
                    "cas_number": "N/A",
                    "purity": "Peer-reviewed sources only",
                    "supplier": "Academic databases",
                    "storage": "Distributed storage system",
                    "safety": "Standard data security protocols"
                }
            ],
            "data_analysis": "Advanced statistical analysis including Bayesian inference and cross-validation",
            "statistical_analysis": "Multiple comparison corrections and power analysis",
            "quality_control": "Automated quality control with human oversight"
        },
        "data_sources": {
            "description": "Comprehensive dataset of scientific literature and experimental results",
            "format": "CSV, JSON, XML formats",
            "access": "Available through AXIOM platform with DOI",
            "datasets": [
                {
                    "name": "Literature Database",
                    "type": "Text Data",
                    "size": "15.2 GB",
                    "format": "JSON",
                    "description": "Processed scientific literature",
                    "hash": "abc123def456ghi789",
                    "access_url": "https://axiom.ai/data/literature_db.json"
                },
                {
                    "name": "Experimental Results",
                    "type": "Numerical Data",
                    "size": "2.8 MB",
                    "format": "CSV",
                    "description": "Validation experiment results",
                    "hash": "def456ghi789jkl012",
                    "access_url": "https://axiom.ai/data/experimental_results.csv"
                }
            ],
            "processing_pipeline": "Automated data processing with quality control and validation",
            "validation_methods": "Cross-validation, holdout testing, and statistical validation"
        },
        "protocol_data": {
            "objective": "Detailed protocol for autonomous scientific research using AI",
            "materials": [
                {"name": "Research Platform", "specifications": "AXIOM META-4 with GPU acceleration"},
                {"name": "Data Sources", "specifications": "Scientific literature databases"},
                {"name": "Computing Resources", "specifications": "High-performance computing cluster"}
            ],
            "equipment": [
                {"name": "GPU Computing Nodes", "specifications": "NVIDIA A100 GPUs"},
                {"name": "Storage Systems", "specifications": "Distributed file system"},
                {"name": "Network Infrastructure", "specifications": "High-speed interconnect"}
            ],
            "procedure": [
                {
                    "title": "System Initialization",
                    "description": "Initialize autonomous research system and verify components",
                    "duration": "10 minutes",
                    "temperature": "Ambient (20-25°C)",
                    "notes": "Full system self-check required"
                },
                {
                    "title": "Data Loading",
                    "description": "Load and validate scientific literature datasets",
                    "duration": "30 minutes",
                    "temperature": "Ambient",
                    "notes": "Data integrity verification"
                },
                {
                    "title": "Model Training",
                    "description": "Train AI models for hypothesis generation",
                    "duration": "4-6 hours",
                    "temperature": "Ambient",
                    "notes": "Monitor GPU temperature and usage"
                }
            ],
            "troubleshooting": [
                {
                    "problem": "GPU memory overflow",
                    "symptoms": "Training stops with memory error",
                    "cause": "Batch size too large",
                    "solution": "Reduce batch size or use gradient accumulation",
                    "prevention": "Monitor memory usage during training"
                },
                {
                    "problem": "Data loading failure",
                    "symptoms": "Cannot load datasets",
                    "cause": "Corrupted data files",
                    "solution": "Verify data integrity and reload",
                    "prevention": "Regular data validation checks"
                }
            ],
            "notes": "This protocol enables fully autonomous scientific research with AI",
            "safety_information": "Standard computing safety protocols and data security measures"
        },
        "figure_data": {
            "figure_1": {
                "title": "Model Architecture Overview",
                "description": "Schematic diagram of the neural network architecture",
                "data_source": "Model configuration files",
                "analysis_methods": "Architecture visualization",
                "interpretation": "Shows the structure of the hypothesis generation model"
            },
            "figure_2": {
                "title": "Training Performance",
                "description": "Training loss and validation accuracy over time",
                "data_source": "Training logs and metrics",
                "analysis_methods": "Performance curve analysis",
                "interpretation": "Demonstrates model convergence and performance"
            },
            "figure_3": {
                "title": "Hypothesis Validation Results",
                "description": "Validation results for generated hypotheses",
                "data_source": "Validation experiments",
                "analysis_methods": "Statistical validation",
                "interpretation": "Shows high validation success rate"
            }
        },
        "table_data": {
            "table_1": {
                "title": "Model Performance Metrics",
                "description": "Comprehensive performance metrics for the AI model",
                "data_source": "Model evaluation results",
                "statistical_methods": "Descriptive statistics and confidence intervals",
                "interpretation": "Key performance indicators for the model",
                "table_data": "Accuracy: 94.2%, Precision: 91.8%, Recall: 89.5%, F1-Score: 90.6%",
                "notes": "All metrics calculated using 10-fold cross-validation"
            },
            "table_2": {
                "title": "Computational Resources",
                "description": "Computational resources and performance metrics",
                "data_source": "System monitoring data",
                "statistical_methods": "Resource utilization analysis",
                "interpretation": "Efficiency and resource usage characteristics",
                "table_data": "GPU Utilization: 85%, Memory Usage: 12.3 GB, Training Time: 4.2 hours",
                "notes": "Metrics collected over 100 training runs"
            }
        }
    }
    
    result = await generator.generate_supplementary_package({
        "action": "generate_supplementary_package",
        **publication_data,
        "output_path": "./examples/supplementary_materials"
    })
    
    if result["success"]:
        print(f"✅ Supplementary package generated: {result['package_id']}")
        print(f"📦 Total materials: {result['total_materials']}")
        print(f"📊 Total size: {result['total_size']} bytes")
        print(f"📁 Package path: {result['package_path']}")
        
        print("\n📋 Materials included:")
        for material in result["materials"]:
            print(f"   - {material['title']} ({material['material_type']})")
            print(f"     File: {material['file_path']}")
            print(f"     Size: {material['file_size']} bytes")
    else:
        print(f"❌ Package generation failed: {result['error']}")


async def example_extended_methods():
    """Example of generating extended methods"""
    print("\n📖 Generating Extended Methods...")
    
    generator = SupplementaryMaterialsGenerator()
    
    experimental_data = {
        "overview": "Detailed experimental methods for autonomous scientific discovery research.",
        "protocols": [
            {
                "name": "Literature Analysis Protocol",
                "objective": "Analyze scientific literature for pattern recognition",
                "materials": ["PubMed database", "Text processing tools", "Machine learning libraries"],
                "procedure": [
                    "Download scientific abstracts",
                    "Preprocess and clean text",
                    "Extract key concepts and relationships",
                    "Train pattern recognition models",
                    "Validate pattern accuracy"
                ],
                "expected_results": "Identified patterns in scientific literature",
                "troubleshooting": [
                    {"problem": "Low text quality", "solution": "Improve preprocessing pipeline"},
                    {"problem": "Pattern overfitting", "solution": "Use regularization techniques"}
                ]
            }
        ],
        "equipment": [
            {
                "name": "Text Processing Server",
                "type": "Computing Equipment",
                "manufacturer": "AXIOM Technologies",
                "model": "TPS-2000",
                "settings": "High-memory configuration",
                "calibration": "Weekly performance testing"
            }
        ],
        "reagents": [
            {
                "name": "Scientific Abstracts",
                "cas_number": "N/A",
                "purity": "Peer-reviewed sources",
                "supplier": "PubMed, arXiv, bioRxiv",
                "storage": "Distributed text storage",
                "safety": "Standard data handling protocols"
            }
        ],
        "data_analysis": "Natural language processing and machine learning analysis",
        "statistical_analysis": "Text mining statistics and pattern validation",
        "quality_control": "Automated quality control with manual review"
    }
    
    result = await generator.generate_extended_methods({
        "action": "generate_extended_methods",
        "publication_id": "pub_20250101_002",
        "experimental_data": experimental_data,
        "output_path": "./examples/supplementary_materials"
    })
    
    if result["success"]:
        print(f"✅ Extended methods generated: {result['filename']}")
        print(f"📁 File path: {result['file_path']}")
        print(f"📊 File size: {result['file_size']} bytes")
    else:
        print(f"❌ Extended methods generation failed: {result['error']}")


async def example_supplementary_data():
    """Example of generating supplementary data"""
    print("\n📊 Generating Supplementary Data...")
    
    generator = SupplementaryMaterialsGenerator()
    
    data_sources = {
        "description": "Raw data and supplementary datasets from autonomous research experiments.",
        "format": "CSV, JSON, and XML formats",
        "access": "Available through AXIOM platform with persistent URLs",
        "datasets": [
            {
                "name": "Hypothesis Generation Dataset",
                "type": "Research Data",
                "size": "5.2 MB",
                "format": "CSV",
                "description": "Generated hypotheses with validation scores",
                "hash": "abc123def456ghi789",
                "access_url": "https://axiom.ai/data/hypotheses_dataset.csv"
            },
            {
                "name": "Validation Results",
                "type": "Experimental Data",
                "size": "1.8 MB",
                "format": "JSON",
                "description": "Validation experiment results",
                "hash": "def456ghi789jkl012",
                "access_url": "https://axiom.ai/data/validation_results.json"
            }
        ],
        "processing_pipeline": "Automated data processing with quality control and validation",
        "validation_methods": "Cross-validation, statistical testing, and expert review"
    }
    
    result = await generator.generate_supplementary_data({
        "action": "generate_supplementary_data",
        "publication_id": "pub_20250101_003",
        "data_sources": data_sources,
        "output_path": "./examples/supplementary_materials"
    })
    
    if result["success"]:
        print(f"✅ Supplementary data generated: {result['filename']}")
        print(f"📁 File path: {result['file_path']}")
        print(f"📊 File size: {result['file_size']} bytes")
    else:
        print(f"❌ Supplementary data generation failed: {result['error']}")


async def example_protocol():
    """Example of generating experimental protocol"""
    print("\n🔬 Generating Experimental Protocol...")
    
    generator = SupplementaryMaterialsGenerator()
    
    protocol_data = {
        "objective": "Detailed protocol for autonomous scientific hypothesis generation and validation",
        "materials": [
            {"name": "Research Platform", "specifications": "AXIOM META-4 with AI capabilities"},
            {"name": "Data Sources", "specifications": "Scientific literature databases"},
            {"name": "Validation Tools", "specifications": "Statistical analysis software"}
        ],
        "equipment": [
            {"name": "Computing Infrastructure", "specifications": "High-performance computing cluster"},
            {"name": "Storage Systems", "specifications": "Distributed file system"},
            {"name": "Network Infrastructure", "specifications": "High-speed data network"}
        ],
        "procedure": [
            {
                "title": "System Initialization",
                "description": "Initialize autonomous research system and verify all components",
                "duration": "15 minutes",
                "temperature": "Ambient (20-25°C)",
                "notes": "Complete system self-check required"
            },
            {
                "title": "Data Collection",
                "description": "Collect and validate scientific literature data",
                "duration": "45 minutes",
                "temperature": "Ambient",
                "notes": "Data integrity verification essential"
            },
            {
                "title": "Hypothesis Generation",
                "description": "Generate scientific hypotheses using AI models",
                "duration": "2-3 hours",
                "temperature": "Ambient",
                "notes": "Monitor system performance"
            },
            {
                "title": "Validation",
                "description": "Validate generated hypotheses through experimental testing",
                "duration": "4-6 hours",
                "temperature": "Ambient",
                "notes": "Statistical validation required"
            }
        ],
        "troubleshooting": [
            {
                "problem": "System initialization failure",
                "symptoms": "Error messages during startup",
                "cause": "Configuration or hardware issues",
                "solution": "Check configuration files and hardware status",
                "prevention": "Regular system maintenance and monitoring"
            },
            {
                "problem": "Data collection errors",
                "symptoms": "Incomplete or corrupted data",
                "cause": "Network or source issues",
                "solution": "Verify network connectivity and data sources",
                "prevention": "Implement data validation checks"
            }
        ],
        "notes": "This protocol enables fully autonomous scientific research with AI",
        "safety_information": "Standard computing safety protocols and data security measures"
    }
    
    result = await generator.generate_protocol({
        "action": "generate_protocol",
        "publication_id": "pub_20250101_004",
        "protocol_data": protocol_data,
        "output_path": "./examples/supplementary_materials"
    })
    
    if result["success"]:
        print(f"✅ Protocol generated: {result['filename']}")
        print(f"📁 File path: {result['file_path']}")
        print(f"📊 File size: {result['file_size']} bytes")
    else:
        print(f"❌ Protocol generation failed: {result['error']}")


async def example_supplementary_figure():
    """Example of generating supplementary figure"""
    print("\n📈 Generating Supplementary Figure...")
    
    generator = SupplementaryMaterialsGenerator()
    
    figure_data = {
        "title": "Model Performance Comparison",
        "description": "Comparison of different AI models for hypothesis generation",
        "data_source": "Model evaluation experiments",
        "analysis_methods": "Comparative statistical analysis",
        "interpretation": "Shows superior performance of the proposed model",
        "software_used": "Python, matplotlib, seaborn",
        "parameters": "Standard evaluation parameters",
        "resolution": "300 DPI",
        "color_scheme": "Scientific color palette",
        "related_data": ["Training data", "Validation results", "Test metrics"]
    }
    
    result = await generator.generate_supplementary_figure({
        "action": "generate_supplementary_figure",
        "publication_id": "pub_20250101_005",
        "figure_number": 1,
        "figure_data": figure_data,
        "output_path": "./examples/supplementary_materials"
    })
    
    if result["success"]:
        print(f"✅ Supplementary figure generated: {result['filename']}")
        print(f"📁 File path: {result['file_path']}")
        print(f"📊 File size: {result['file_size']} bytes")
    else:
        print(f"❌ Supplementary figure generation failed: {result['error']}")


async def example_supplementary_table():
    """Example of generating supplementary table"""
    print("\n📋 Generating Supplementary Table...")
    
    generator = SupplementaryMaterialsGenerator()
    
    table_data = {
        "title": "Dataset Statistics",
        "description": "Statistical summary of the training and validation datasets",
        "data_source": "Dataset analysis results",
        "statistical_methods": "Descriptive statistics and distribution analysis",
        "interpretation": "Shows balanced and representative datasets",
        "table_data": "Sample count: 10,000, Mean: 0.5, Std: 0.2, Min: 0.1, Max: 0.9",
        "notes": "All statistics calculated using standard methods"
    }
    
    result = await generator.generate_supplementary_table({
        "action": "generate_supplementary_table",
        "publication_id": "pub_20250101_006",
        "table_number": 1,
        "table_data": table_data,
        "output_path": "./examples/supplementary_materials"
    })
    
    if result["success"]:
        print(f"✅ Supplementary table generated: {result['filename']}")
        print(f"📁 File path: {result['file_path']}")
        print(f"📊 File size: {result['file_size']} bytes")
    else:
        print(f"❌ Supplementary table generation failed: {result['error']}")


async def main():
    """Run all supplementary materials generation examples"""
    print("🚀 AXIOM META 4 - Supplementary Materials Generation Examples")
    print("=" * 70)
    
    # Create output directory
    output_dir = Path("./examples/supplementary_materials")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Run all examples
        await example_supplementary_package()
        await example_extended_methods()
        await example_supplementary_data()
        await example_protocol()
        await example_supplementary_figure()
        await example_supplementary_table()
        
        print("\n" + "=" * 70)
        print("✅ All supplementary materials generation examples completed successfully!")
        print(f"📁 Supplementary materials saved to: {output_dir.absolute()}")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
