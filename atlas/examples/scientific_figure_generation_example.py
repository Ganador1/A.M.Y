"""
Scientific Figure Generation Example - AXIOM META 4
Demonstrates the automated generation of publication-ready scientific figures.
"""

import asyncio
import numpy as np
from pathlib import Path
import sys

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.scientific_figure_generator import ScientificFigureGenerator


async def example_plot_generation():
    """Example of generating scientific plots"""
    print("🔬 Generating Scientific Plot Example...")
    
    generator = ScientificFigureGenerator()
    
    # Generate sample data
    x_data = np.linspace(0, 10, 100)
    y1 = np.sin(x_data) + 0.1 * np.random.randn(100)
    y2 = np.cos(x_data) + 0.1 * np.random.randn(100)
    y3 = np.sin(x_data + np.pi/4) + 0.1 * np.random.randn(100)
    
    # Create plot data
    plot_data = {
        "x_data": x_data.tolist(),
        "y_data": [y1.tolist(), y2.tolist(), y3.tolist()],
        "labels": ["Sine Wave", "Cosine Wave", "Phase Shifted Sine"],
        "colors": ["#1f77b4", "#ff7f0e", "#2ca02c"],
        "x_label": "Time (s)",
        "y_label": "Amplitude",
        "metadata": {"experiment": "waveform_analysis", "sample_rate": "100 Hz"}
    }
    
    result = await generator.generate_plot({
        "action": "generate_plot",
        "title": "Multi-Frequency Waveform Analysis",
        "caption": "Comparison of different waveform patterns in experimental data",
        "domain": "physics",
        "data": plot_data,
        "output_path": "./examples/figures"
    })
    
    if result["success"]:
        print(f"✅ Plot generated: {result['filename']}")
        print(f"📁 File path: {result['filepath']}")
    else:
        print(f"❌ Plot generation failed: {result['error']}")


async def example_diagram_generation():
    """Example of generating scientific diagrams"""
    print("\n🔬 Generating Scientific Diagram Example...")
    
    generator = ScientificFigureGenerator()
    
    # Create diagram elements
    diagram_data = {
        "elements": [
            {
                "type": "rectangle",
                "position": [1, 1],
                "size": [2, 1],
                "label": "Sample",
                "color": "#1f77b4"
            },
            {
                "type": "rectangle", 
                "position": [5, 1],
                "size": [2, 1],
                "label": "Analyzer",
                "color": "#ff7f0e"
            },
            {
                "type": "circle",
                "position": [3, 4],
                "size": [1, 1],
                "label": "Detector",
                "color": "#2ca02c"
            }
        ],
        "connections": [
            {
                "start": [3, 2],
                "end": [5, 2],
                "style": "solid"
            },
            {
                "start": [6, 2],
                "end": [3.5, 4],
                "style": "dashed"
            }
        ]
    }
    
    result = await generator.generate_diagram({
        "action": "generate_diagram",
        "title": "Experimental Setup Diagram",
        "caption": "Schematic representation of the experimental apparatus",
        "domain": "chemistry",
        "data": diagram_data,
        "output_path": "./examples/figures"
    })
    
    if result["success"]:
        print(f"✅ Diagram generated: {result['filename']}")
        print(f"📁 File path: {result['filepath']}")
    else:
        print(f"❌ Diagram generation failed: {result['error']}")


async def example_flowchart_generation():
    """Example of generating flowcharts"""
    print("\n🔬 Generating Flowchart Example...")
    
    generator = ScientificFigureGenerator()
    
    # Create flowchart steps
    flowchart_data = {
        "steps": [
            {"type": "start_end", "label": "Start"},
            {"type": "process", "label": "Sample Preparation"},
            {"type": "process", "label": "Data Collection"},
            {"type": "decision", "label": "Quality Check"},
            {"type": "process", "label": "Analysis"},
            {"type": "process", "label": "Validation"},
            {"type": "start_end", "label": "End"}
        ]
    }
    
    result = await generator.generate_flowchart({
        "action": "generate_flowchart",
        "title": "Research Workflow Process",
        "caption": "Standard workflow for experimental research validation",
        "domain": "biology",
        "data": flowchart_data,
        "output_path": "./examples/figures"
    })
    
    if result["success"]:
        print(f"✅ Flowchart generated: {result['filename']}")
        print(f"📁 File path: {result['filepath']}")
    else:
        print(f"❌ Flowchart generation failed: {result['error']}")


async def example_heatmap_generation():
    """Example of generating heatmaps"""
    print("\n🔬 Generating Heatmap Example...")
    
    generator = ScientificFigureGenerator()
    
    # Create sample heatmap data
    np.random.seed(42)
    matrix_data = np.random.rand(8, 10)
    
    heatmap_data = {
        "matrix": matrix_data.tolist(),
        "row_labels": [f"Sample {i+1}" for i in range(8)],
        "col_labels": [f"Gene {i+1}" for i in range(10)],
        "colorbar_label": "Expression Level",
        "x_label": "Genes",
        "y_label": "Samples"
    }
    
    result = await generator.generate_heatmap({
        "action": "generate_heatmap",
        "title": "Gene Expression Heatmap",
        "caption": "Expression levels across different genes and samples",
        "domain": "biology",
        "data": heatmap_data,
        "output_path": "./examples/figures"
    })
    
    if result["success"]:
        print(f"✅ Heatmap generated: {result['filename']}")
        print(f"📁 File path: {result['filepath']}")
    else:
        print(f"❌ Heatmap generation failed: {result['error']}")


async def example_network_generation():
    """Example of generating network diagrams"""
    print("\n🔬 Generating Network Diagram Example...")
    
    generator = ScientificFigureGenerator()
    
    # Create network data
    network_data = {
        "nodes": [
            {"position": [2, 6], "label": "Protein A", "size": 150, "color": "#1f77b4"},
            {"position": [6, 6], "label": "Protein B", "size": 120, "color": "#ff7f0e"},
            {"position": [4, 4], "label": "Complex AB", "size": 200, "color": "#2ca02c"},
            {"position": [2, 2], "label": "Enzyme X", "size": 100, "color": "#d62728"},
            {"position": [6, 2], "label": "Product Y", "size": 80, "color": "#9467bd"}
        ],
        "edges": [
            {"start": [2, 6], "end": [4, 4], "weight": 2.0},
            {"start": [6, 6], "end": [4, 4], "weight": 2.0},
            {"start": [4, 4], "end": [2, 2], "weight": 1.5},
            {"start": [2, 2], "end": [6, 2], "weight": 1.0}
        ]
    }
    
    result = await generator.generate_network({
        "action": "generate_network",
        "title": "Protein Interaction Network",
        "caption": "Network of protein-protein interactions and enzymatic reactions",
        "domain": "biology",
        "data": network_data,
        "output_path": "./examples/figures"
    })
    
    if result["success"]:
        print(f"✅ Network diagram generated: {result['filename']}")
        print(f"📁 File path: {result['filepath']}")
    else:
        print(f"❌ Network generation failed: {result['error']}")


async def example_batch_generation():
    """Example of batch figure generation"""
    print("\n🔬 Generating Batch Figures Example...")
    
    generator = ScientificFigureGenerator()
    
    # Create multiple figures
    figures = [
        {
            "figure_type": "plot",
            "title": "Batch Plot 1",
            "caption": "First batch plot",
            "domain": "physics",
            "data": {
                "x_data": [1, 2, 3, 4, 5],
                "y_data": [[1, 4, 2, 5, 3]],
                "labels": ["Data Series 1"],
                "x_label": "X",
                "y_label": "Y"
            }
        },
        {
            "figure_type": "plot",
            "title": "Batch Plot 2", 
            "caption": "Second batch plot",
            "domain": "chemistry",
            "data": {
                "x_data": [1, 2, 3, 4, 5],
                "y_data": [[2, 5, 3, 6, 4]],
                "labels": ["Data Series 2"],
                "x_label": "X",
                "y_label": "Y"
            }
        }
    ]
    
    # Generate figures one by one (simulating batch)
    for i, figure_config in enumerate(figures):
        result = await generator.generate_figure({
            "action": "generate_figure",
            **figure_config,
            "output_path": "./examples/figures"
        })
        
        if result["success"]:
            print(f"✅ Batch figure {i+1} generated: {result['filename']}")
        else:
            print(f"❌ Batch figure {i+1} failed: {result['error']}")


async def main():
    """Run all figure generation examples"""
    print("🚀 AXIOM META 4 - Scientific Figure Generation Examples")
    print("=" * 60)
    
    # Create output directory
    output_dir = Path("./examples/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Run all examples
        await example_plot_generation()
        await example_diagram_generation()
        await example_flowchart_generation()
        await example_heatmap_generation()
        await example_network_generation()
        await example_batch_generation()
        
        print("\n" + "=" * 60)
        print("✅ All figure generation examples completed successfully!")
        print(f"📁 Figures saved to: {output_dir.absolute()}")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
