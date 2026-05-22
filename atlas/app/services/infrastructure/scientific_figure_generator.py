"""
Scientific Figure Generator Service - AXIOM META 4
Automated generation of publication-ready scientific figures with professional formatting.
"""

from __future__ import annotations
import asyncio

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
import matplotlib.patheffects as path_effects

from app.core.bootstrap_logging import logger
from app.services.base_service import BaseService
from app.exceptions.domain.biology import BiologyError
from app.types.scientific_figure_generator_types import (
    ProcessRequestResult,
    GenerateFigureResult,
    GeneratePlotResult,
    GenerateDiagramResult,
    GenerateFlowchartResult,
    GenerateHeatmapResult,
    GenerateNetworkResult,
)


@dataclass
class FigureMetadata:
    """Metadata for generated scientific figures"""
    figure_id: str
    title: str
    caption: str
    figure_type: str  # 'plot', 'diagram', 'flowchart', 'heatmap', 'network'
    domain: str
    filename: str
    format: str = "png"  # png, pdf, svg
    resolution: int = 300  # DPI
    width: float = 6.0  # inches
    height: float = 4.0  # inches
    created_at: datetime = field(default_factory=datetime.now)
    data_hash: Optional[str] = None
    style: str = "publication"  # publication, presentation, draft


@dataclass
class PlotData:
    """Data structure for plot generation"""
    x_data: Optional[np.ndarray] = None
    y_data: Optional[np.ndarray] = None
    z_data: Optional[np.ndarray] = None
    labels: List[str] = field(default_factory=list)
    colors: List[str] = field(default_factory=list)
    error_bars: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ScientificFigureGenerator(BaseService):
    """Service for generating publication-ready scientific figures"""
    
    def __init__(self):
        super().__init__("ScientificFigureGenerator")
        
        # Set publication-quality defaults
        self._setup_matplotlib_style()
        
        # Figure templates for different domains
        self.domain_templates = {
            "biology": {
                "color_palette": "viridis",
                "default_colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],
                "style": "whitegrid"
            },
            "chemistry": {
                "color_palette": "plasma", 
                "default_colors": ["#440154", "#31688e", "#35b779", "#fde725"],
                "style": "whitegrid"
            },
            "physics": {
                "color_palette": "inferno",
                "default_colors": ["#000004", "#56106e", "#bb3754", "#f98e09"],
                "style": "whitegrid"
            },
            "materials": {
                "color_palette": "magma",
                "default_colors": ["#000004", "#3b0f70", "#8c2981", "#de4968"],
                "style": "whitegrid"
            },
            "neuroscience": {
                "color_palette": "cividis",
                "default_colors": ["#00204d", "#31446b", "#63686a", "#c5bebd"],
                "style": "whitegrid"
            }
        }
        
        logger.info("✅ ScientificFigureGenerator initialized")
    
    def _setup_matplotlib_style(self):
        """Configure matplotlib for publication-quality figures"""
        plt.rcParams.update({
            'figure.dpi': 300,
            'savefig.dpi': 300,
            'savefig.bbox': 'tight',
            'savefig.pad_inches': 0.1,
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 11,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9,
            'figure.titlesize': 14,
            'font.family': 'serif',
            'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif'],
            'mathtext.fontset': 'stix',
            'mathtext.rm': 'serif',
            'axes.linewidth': 0.8,
            'grid.linewidth': 0.5,
            'lines.linewidth': 1.2,
            'patch.linewidth': 0.8,
            'xtick.major.width': 0.8,
            'ytick.major.width': 0.8,
            'xtick.minor.width': 0.6,
            'ytick.minor.width': 0.6,
            'xtick.major.size': 4,
            'ytick.major.size': 4,
            'xtick.minor.size': 2,
            'ytick.minor.size': 2
        })
    
    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process figure generation requests"""
        try:
            action = request_data.get("action", "")
            
            if action == "generate_figure":
                return await self.generate_figure(request_data)
            elif action == "generate_plot":
                return await self.generate_plot(request_data)
            elif action == "generate_diagram":
                return await self.generate_diagram(request_data)
            elif action == "generate_flowchart":
                return await self.generate_flowchart(request_data)
            elif action == "generate_heatmap":
                return await self.generate_heatmap(request_data)
            elif action == "generate_network":
                return await self.generate_network(request_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "generate_figure", "generate_plot", "generate_diagram",
                        "generate_flowchart", "generate_heatmap", "generate_network"
                    ]
                }
                
        except BiologyError as e:
            return self.handle_error(e, "process_request")
    
    async def generate_figure(self, request_data: GenerateFigureResult) -> GenerateFigureResult:
        """Generate a scientific figure based on type and data"""
        try:
            figure_type = request_data.get("figure_type", "plot")
            title = request_data.get("title", "Scientific Figure")
            caption = request_data.get("caption", "")
            domain = request_data.get("domain", "general")
            data = request_data.get("data", {})
            output_path = request_data.get("output_path", "./figures")
            
            # Generate figure ID
            figure_id = f"fig_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create output directory
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate figure based on type
            if figure_type == "plot":
                result = await self._generate_plot_figure(figure_id, title, caption, domain, data, output_dir)
            elif figure_type == "diagram":
                result = await self._generate_diagram_figure(figure_id, title, caption, domain, data, output_dir)
            elif figure_type == "flowchart":
                result = await self._generate_flowchart_figure(figure_id, title, caption, domain, data, output_dir)
            elif figure_type == "heatmap":
                result = await self._generate_heatmap_figure(figure_id, title, caption, domain, data, output_dir)
            elif figure_type == "network":
                result = await self._generate_network_figure(figure_id, title, caption, domain, data, output_dir)
            else:
                return {"success": False, "error": f"Unknown figure type: {figure_type}"}
            
            return result
            
        except BiologyError as e:
            return self.handle_error(e, "generate_figure")
    
    async def _generate_plot_figure(self, figure_id: str, title: str, caption: str, 
                                   domain: str, data: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """Generate a scientific plot figure"""
        try:
            # Extract plot data
            plot_data = self._extract_plot_data(data)
            
            # Set domain-specific style
            domain_config = self.domain_templates.get(domain, self.domain_templates["biology"])
            sns.set_style(domain_config["style"])
            sns.set_palette(domain_config["color_palette"])
            
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Detect if x_data is categorical (strings)
            is_categorical = plot_data.x_data is not None and (
                isinstance(plot_data.x_data[0], str) if len(plot_data.x_data) > 0 else False
            )
            
            # Generate plot based on data type
            if plot_data.x_data is not None and plot_data.y_data is not None:
                # Flatten y_data if it's nested and has wrong shape
                y_flat = plot_data.y_data.flatten() if len(plot_data.y_data.shape) > 1 else plot_data.y_data
                
                # Ensure x and y have same length
                x_len = len(plot_data.x_data)
                y_len = len(y_flat)
                
                if x_len != y_len:
                    # Adjust dimensions to match
                    if y_len > x_len:
                        y_flat = y_flat[:x_len]
                    else:
                        plot_data.x_data = plot_data.x_data[:y_len]
                
                if is_categorical:
                    # Use bar plot for categorical data
                    color = plot_data.colors[0] if plot_data.colors else domain_config["default_colors"][0]
                    bars = ax.bar(range(len(plot_data.x_data)), y_flat, color=color, alpha=0.7)
                    ax.set_xticks(range(len(plot_data.x_data)))
                    ax.set_xticklabels(plot_data.x_data, rotation=45, ha='right')
                elif len(plot_data.y_data.shape) > 1:  # Multiple series
                    for i, y_series in enumerate(plot_data.y_data.T):
                        label = plot_data.labels[i] if i < len(plot_data.labels) else f"Series {i+1}"
                        color = plot_data.colors[i] if i < len(plot_data.colors) else domain_config["default_colors"][i % len(domain_config["default_colors"])]
                        
                        if plot_data.error_bars is not None:
                            ax.errorbar(plot_data.x_data, y_series, yerr=plot_data.error_bars[:, i], 
                                      label=label, color=color, marker='o', capsize=3)
                        else:
                            ax.plot(plot_data.x_data, y_series, label=label, color=color, marker='o', linewidth=2)
                else:  # Single series
                    color = plot_data.colors[0] if plot_data.colors else domain_config["default_colors"][0]
                    if plot_data.error_bars is not None:
                        ax.errorbar(plot_data.x_data, plot_data.y_data, yerr=plot_data.error_bars, 
                                  color=color, marker='o', capsize=3)
                    else:
                        ax.plot(plot_data.x_data, plot_data.y_data, color=color, marker='o', linewidth=2)
            
            # Customize plot
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel(data.get("x_label", "X-axis"), fontsize=12)
            ax.set_ylabel(data.get("y_label", "Y-axis"), fontsize=12)
            
            if len(plot_data.labels) > 1:
                ax.legend(loc='best', frameon=True, fancybox=True, shadow=True)
            
            # Add grid
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Add scientific notation if needed (only for numeric axes, not categorical)
            if not is_categorical:
                try:
                    ax.ticklabel_format(style='scientific', axis='both', scilimits=(0,0))
                except (AttributeError, ValueError):
                    pass  # Skip if formatter doesn't support scientific notation
            
            # Tight layout
            plt.tight_layout()
            
            # Save figure
            filename = f"{figure_id}.png"
            filepath = output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            # Create metadata
            metadata = FigureMetadata(
                figure_id=figure_id,
                title=title,
                caption=caption,
                figure_type="plot",
                domain=domain,
                filename=filename,
                data_hash=self._calculate_data_hash(data)
            )
            
            logger.info(f"✅ Generated plot figure: {filename}")
            
            return {
                "success": True,
                "figure_id": figure_id,
                "filename": filename,
                "filepath": str(filepath),
                "metadata": metadata.__dict__,
                "figure_type": "plot"
            }
            
        except BiologyError as e:
            return self.handle_error(e, "_generate_plot_figure")
    
    async def _generate_diagram_figure(self, figure_id: str, title: str, caption: str,
                                     domain: str, data: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """Generate a scientific diagram figure"""
        try:
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Extract diagram elements
            elements = data.get("elements", [])
            connections = data.get("connections", [])
            
            # Draw elements
            for element in elements:
                element_type = element.get("type", "rectangle")
                x, y = element.get("position", [0, 0])
                width, height = element.get("size", [1, 0.5])
                label = element.get("label", "")
                color = element.get("color", "#1f77b4")
                
                if element_type == "rectangle":
                    rect = Rectangle((x, y), width, height, 
                                   facecolor=color, edgecolor='black', linewidth=1.5)
                    ax.add_patch(rect)
                elif element_type == "circle":
                    circle = Circle((x + width/2, y + height/2), width/2,
                                  facecolor=color, edgecolor='black', linewidth=1.5)
                    ax.add_patch(circle)
                
                # Add label
                ax.text(x + width/2, y + height/2, label, 
                       ha='center', va='center', fontsize=10, fontweight='bold')
            
            # Draw connections
            for connection in connections:
                start = connection.get("start", [0, 0])
                end = connection.get("end", [1, 1])
                style = connection.get("style", "solid")
                
                if style == "dashed":
                    linestyle = "--"
                elif style == "dotted":
                    linestyle = ":"
                else:
                    linestyle = "-"
                
                ax.plot([start[0], end[0]], [start[1], end[1]], 
                       color='black', linewidth=2, linestyle=linestyle)
            
            # Customize diagram
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            ax.set_xlim(-0.5, 10.5)
            ax.set_ylim(-0.5, 8.5)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Save figure
            filename = f"{figure_id}.png"
            filepath = output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            # Create metadata
            metadata = FigureMetadata(
                figure_id=figure_id,
                title=title,
                caption=caption,
                figure_type="diagram",
                domain=domain,
                filename=filename,
                data_hash=self._calculate_data_hash(data)
            )
            
            logger.info(f"✅ Generated diagram figure: {filename}")
            
            return {
                "success": True,
                "figure_id": figure_id,
                "filename": filename,
                "filepath": str(filepath),
                "metadata": metadata.__dict__,
                "figure_type": "diagram"
            }
            
        except BiologyError as e:
            return self.handle_error(e, "_generate_diagram_figure")
    
    async def _generate_flowchart_figure(self, figure_id: str, title: str, caption: str,
                                       domain: str, data: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """Generate a scientific flowchart figure"""
        try:
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Extract flowchart steps
            steps = data.get("steps", [])
            
            # Draw flowchart
            for i, step in enumerate(steps):
                x = 2 + (i % 3) * 3
                y = 6 - (i // 3) * 2
                
                step_type = step.get("type", "process")
                label = step.get("label", f"Step {i+1}")
                
                if step_type == "start_end":
                    # Oval shape
                    ellipse = patches.Ellipse((x, y), 1.5, 0.8, 
                                           facecolor='lightgreen', edgecolor='black', linewidth=2)
                    ax.add_patch(ellipse)
                elif step_type == "decision":
                    # Diamond shape
                    diamond = patches.Polygon([(x-0.8, y), (x, y+0.4), (x+0.8, y), (x, y-0.4)],
                                           facecolor='lightyellow', edgecolor='black', linewidth=2)
                    ax.add_patch(diamond)
                else:
                    # Rectangle shape
                    rect = Rectangle((x-0.8, y-0.4), 1.6, 0.8,
                                   facecolor='lightblue', edgecolor='black', linewidth=2)
                    ax.add_patch(rect)
                
                # Add label
                ax.text(x, y, label, ha='center', va='center', fontsize=9, fontweight='bold')
                
                # Draw arrows to next step
                if i < len(steps) - 1:
                    next_x = 2 + ((i+1) % 3) * 3
                    next_y = 6 - ((i+1) // 3) * 2
                    ax.annotate('', xy=(next_x-0.8, next_y), xytext=(x+0.8, y),
                              arrowprops=dict(arrowstyle='->', lw=2, color='black'))
            
            # Customize flowchart
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 8)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Save figure
            filename = f"{figure_id}.png"
            filepath = output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            # Create metadata
            metadata = FigureMetadata(
                figure_id=figure_id,
                title=title,
                caption=caption,
                figure_type="flowchart",
                domain=domain,
                filename=filename,
                data_hash=self._calculate_data_hash(data)
            )
            
            logger.info(f"✅ Generated flowchart figure: {filename}")
            
            return {
                "success": True,
                "figure_id": figure_id,
                "filename": filename,
                "filepath": str(filepath),
                "metadata": metadata.__dict__,
                "figure_type": "flowchart"
            }
            
        except BiologyError as e:
            return self.handle_error(e, "_generate_flowchart_figure")
    
    async def _generate_heatmap_figure(self, figure_id: str, title: str, caption: str,
                                     domain: str, data: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """Generate a scientific heatmap figure"""
        try:
            # Extract heatmap data
            matrix_data = np.array(data.get("matrix", np.random.rand(10, 10)))
            row_labels = data.get("row_labels", [f"Row {i}" for i in range(matrix_data.shape[0])])
            col_labels = data.get("col_labels", [f"Col {i}" for i in range(matrix_data.shape[1])])
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Generate heatmap
            im = ax.imshow(matrix_data, cmap='viridis', aspect='auto')
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label(data.get("colorbar_label", "Value"), fontsize=12)
            
            # Set labels
            ax.set_xticks(range(len(col_labels)))
            ax.set_yticks(range(len(row_labels)))
            ax.set_xticklabels(col_labels, rotation=45, ha='right')
            ax.set_yticklabels(row_labels)
            
            # Add values to cells
            for i in range(matrix_data.shape[0]):
                for j in range(matrix_data.shape[1]):
                    text = ax.text(j, i, f'{matrix_data[i, j]:.2f}',
                                 ha="center", va="center", color="white", fontsize=8)
            
            # Customize heatmap
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel(data.get("x_label", "Columns"), fontsize=12)
            ax.set_ylabel(data.get("y_label", "Rows"), fontsize=12)
            
            # Tight layout
            plt.tight_layout()
            
            # Save figure
            filename = f"{figure_id}.png"
            filepath = output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            # Create metadata
            metadata = FigureMetadata(
                figure_id=figure_id,
                title=title,
                caption=caption,
                figure_type="heatmap",
                domain=domain,
                filename=filename,
                data_hash=self._calculate_data_hash(data)
            )
            
            logger.info(f"✅ Generated heatmap figure: {filename}")
            
            return {
                "success": True,
                "figure_id": figure_id,
                "filename": filename,
                "filepath": str(filepath),
                "metadata": metadata.__dict__,
                "figure_type": "heatmap"
            }
            
        except BiologyError as e:
            return self.handle_error(e, "_generate_heatmap_figure")
    
    async def _generate_network_figure(self, figure_id: str, title: str, caption: str,
                                     domain: str, data: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """Generate a scientific network figure"""
        try:
            # Extract network data
            nodes = data.get("nodes", [])
            edges = data.get("edges", [])
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Draw edges first
            for edge in edges:
                start = edge.get("start", [0, 0])
                end = edge.get("end", [1, 1])
                weight = edge.get("weight", 1)
                
                # Line width based on weight
                linewidth = max(0.5, min(5, weight * 2))
                
                ax.plot([start[0], end[0]], [start[1], end[1]], 
                       color='gray', linewidth=linewidth, alpha=0.6)
            
            # Draw nodes
            for node in nodes:
                x, y = node.get("position", [0, 0])
                label = node.get("label", "")
                size = node.get("size", 100)
                color = node.get("color", "#1f77b4")
                
                # Draw node
                circle = Circle((x, y), size/1000, facecolor=color, 
                              edgecolor='black', linewidth=2)
                ax.add_patch(circle)
                
                # Add label
                ax.text(x, y, label, ha='center', va='center', 
                       fontsize=10, fontweight='bold', color='white')
            
            # Customize network
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            ax.set_xlim(-1, 11)
            ax.set_ylim(-1, 9)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Save figure
            filename = f"{figure_id}.png"
            filepath = output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            # Create metadata
            metadata = FigureMetadata(
                figure_id=figure_id,
                title=title,
                caption=caption,
                figure_type="network",
                domain=domain,
                filename=filename,
                data_hash=self._calculate_data_hash(data)
            )
            
            logger.info(f"✅ Generated network figure: {filename}")
            
            return {
                "success": True,
                "figure_id": figure_id,
                "filename": filename,
                "filepath": str(filepath),
                "metadata": metadata.__dict__,
                "figure_type": "network"
            }
            
        except BiologyError as e:
            return self.handle_error(e, "_generate_network_figure")
    
    def _extract_plot_data(self, data: Dict[str, Any]) -> PlotData:
        """Extract and structure plot data"""
        plot_data = PlotData()
        
        # Extract x and y data
        if "x_data" in data:
            plot_data.x_data = np.array(data["x_data"])
        if "y_data" in data:
            plot_data.y_data = np.array(data["y_data"])
        if "z_data" in data:
            plot_data.z_data = np.array(data["z_data"])
        
        # Extract labels and colors
        plot_data.labels = data.get("labels", [])
        plot_data.colors = data.get("colors", [])
        
        # Extract error bars
        if "error_bars" in data:
            plot_data.error_bars = np.array(data["error_bars"])
        
        # Extract metadata
        plot_data.metadata = data.get("metadata", {})
        
        return plot_data
    
    def _calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash of figure data for integrity verification"""
        import hashlib
        
        # Convert data to JSON string for hashing
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.blake2b(data_str.encode()).hexdigest()[:16]
    
    async def generate_plot(self, request_data: GeneratePlotResult) -> GeneratePlotResult:
        """Convenience method for generating plots"""
        request_data["figure_type"] = "plot"
        return await self.generate_figure(request_data)
    
    async def generate_diagram(self, request_data: GenerateDiagramResult) -> GenerateDiagramResult:
        """Convenience method for generating diagrams"""
        request_data["figure_type"] = "diagram"
        return await self.generate_figure(request_data)
    
    async def generate_flowchart(self, request_data: GenerateFlowchartResult) -> GenerateFlowchartResult:
        """Convenience method for generating flowcharts"""
        request_data["figure_type"] = "flowchart"
        return await self.generate_figure(request_data)
    
    async def generate_heatmap(self, request_data: GenerateHeatmapResult) -> GenerateHeatmapResult:
        """Convenience method for generating heatmaps"""
        request_data["figure_type"] = "heatmap"
        return await self.generate_figure(request_data)
    
    async def generate_network(self, request_data: GenerateNetworkResult) -> GenerateNetworkResult:
        """Convenience method for generating network diagrams"""
        request_data["figure_type"] = "network"
        return await self.generate_figure(request_data)
