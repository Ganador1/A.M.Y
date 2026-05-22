"""
Advanced Matplotlib Operations Module for AXIOM

This module provides comprehensive advanced matplotlib operations, including:
- Advanced plotting with custom styles and themes
- 3D visualization capabilities
- Animation and interactive plotting
- Statistical plotting with advanced features
- Custom colormaps and color management
- Subplot management and complex layouts
- Mathematical text rendering
- Image processing and visualization
- Contour and field plotting
- Specialized charts and visualizations

Author: AXIOM Development Team
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
from typing import Dict, List, Tuple, Union, Any
import numpy as np
import warnings
warnings.filterwarnings('ignore')


class AdvancedMatplotlibOperations:
    """
    Advanced matplotlib operations for comprehensive data visualization.
    """

    def __init__(self):
        """Initialize the advanced matplotlib operations."""
        self.style_sheets = plt.style.available
        self.colormaps = plt.colormaps()
        self.markers = ['o', 'v', '^', '<', '>', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_']
        self.line_styles = ['-', '--', '-.', ':', 'solid', 'dashed', 'dashdot', 'dotted']

    def advanced_plotting_pipeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive plotting pipeline with advanced features.

        Args:
            data: Dictionary containing plot data and configuration

        Returns:
            Dictionary with plot results and metadata
        """
        try:
            # Extract data
            x_data = data.get('x', [])
            y_data = data.get('y', [])
            plot_type = data.get('type', 'line')
            style = data.get('style', 'default')
            title = data.get('title', 'Advanced Plot')
            xlabel = data.get('xlabel', 'X-axis')
            ylabel = data.get('ylabel', 'Y-axis')

            # Apply style
            plt.style.use(style)

            # Create figure with advanced layout
            fig, axes = self._create_advanced_layout(data)

            # Generate plot based on type
            self._generate_advanced_plot(axes, x_data, y_data, plot_type, data)

            # Add advanced annotations
            self._add_advanced_annotations(axes, data)

            # Customize appearance
            self._customize_appearance(fig, axes, title, xlabel, ylabel, data)

            # Add interactive elements if requested
            if data.get('interactive', False):
                self._add_interactive_elements(fig, data)

            return {
                'figure': fig,
                'axes': axes,
                'plot_type': plot_type,
                'style': style,
                'metadata': {
                    'data_points': len(x_data) if x_data else 0,
                    'plot_features': self._get_plot_features(data),
                    'colormap_used': data.get('colormap', 'viridis')
                }
            }

        except Exception as e:
            return {'error': f'Advanced plotting failed: {str(e)}'}

    def _create_advanced_layout(self, data: Dict[str, Any]) -> Tuple[plt.Figure, Union[plt.Axes, np.ndarray]]:
        """Create advanced figure layout with subplots and grids."""
        nrows = data.get('nrows', 1)
        ncols = data.get('ncols', 1)
        figsize = data.get('figsize', (12, 8))

        if nrows == 1 and ncols == 1:
            fig, axes = plt.subplots(figsize=figsize)
        else:
            fig, axes = plt.subplots(nrows, ncols, figsize=figsize)

            # Apply tight layout for better spacing
            plt.tight_layout()

        return fig, axes

    def _generate_advanced_plot(self, axes: Union[plt.Axes, np.ndarray],
                               x_data: List, y_data: List, plot_type: str,
                               data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate advanced plot based on type."""
        plot_methods = {
            'line': self._advanced_line_plot,
            'scatter': self._advanced_scatter_plot,
            'bar': self._advanced_bar_plot,
            'histogram': self._advanced_histogram_plot,
            'contour': self._advanced_contour_plot,
            'surface': self._advanced_surface_plot,
            'animation': self._advanced_animation_plot
        }

        if plot_type in plot_methods:
            return plot_methods[plot_type](axes, x_data, y_data, data)
        else:
            # Default to line plot
            return self._advanced_line_plot(axes, x_data, y_data, data)

    def _advanced_line_plot(self, axes: plt.Axes, x_data: List, y_data: List,
                           data: Dict[str, Any]) -> Dict[str, Any]:
        """Create advanced line plot with multiple series and styling."""
        if not x_data or not y_data:
            return {'error': 'No data provided'}

        # Handle multiple series
        if isinstance(y_data[0], (list, np.ndarray)):
            for i, y_series in enumerate(y_data):
                color = data.get('colors', plt.cm.tab10.colors)[i % len(plt.cm.tab10.colors)]
                linestyle = self.line_styles[i % len(self.line_styles)]
                marker = self.markers[i % len(self.markers)]

                axes.plot(x_data, y_series,
                         color=color,
                         linestyle=linestyle,
                         marker=marker,
                         linewidth=data.get('linewidth', 2),
                         markersize=data.get('markersize', 6),
                         alpha=data.get('alpha', 0.8),
                         label=f'Series {i+1}')
        else:
            axes.plot(x_data, y_data,
                     color=data.get('color', 'blue'),
                     linewidth=data.get('linewidth', 2),
                     marker=data.get('marker', 'o'),
                     markersize=data.get('markersize', 6),
                     alpha=data.get('alpha', 0.8))

        # Add grid and legend
        axes.grid(True, alpha=0.3)
        if data.get('legend', True):
            axes.legend()

        return {'plot_type': 'line', 'series_count': len(y_data) if isinstance(y_data[0], (list, np.ndarray)) else 1}

    def _advanced_scatter_plot(self, axes: plt.Axes, x_data: List, y_data: List,
                              data: Dict[str, Any]) -> Dict[str, Any]:
        """Create advanced scatter plot with size and color mapping."""
        if not x_data or not y_data:
            return {'error': 'No data provided'}

        # Extract size and color data
        sizes = data.get('sizes', np.random.uniform(20, 200, len(x_data)))
        colors = data.get('point_colors', np.random.rand(len(x_data)))

        scatter = axes.scatter(x_data, y_data,
                              s=sizes,
                              c=colors,
                              cmap=data.get('colormap', 'viridis'),
                              alpha=data.get('alpha', 0.6),
                              edgecolors='black',
                              linewidth=0.5)

        # Add colorbar if applicable
        if data.get('colorbar', True):
            plt.colorbar(scatter, ax=axes, label=data.get('colorbar_label', 'Value'))

        axes.grid(True, alpha=0.3)

        return {'plot_type': 'scatter', 'points': len(x_data)}

    def _advanced_bar_plot(self, axes: plt.Axes, x_data: List, y_data: List,
                          data: Dict[str, Any]) -> Dict[str, Any]:
        """Create advanced bar plot with gradients and patterns."""
        if not x_data or not y_data:
            return {'error': 'No data provided'}

        bars = axes.bar(x_data, y_data,
                       color=data.get('bar_colors', plt.cm.Set3.colors[:len(x_data)]),
                       alpha=data.get('alpha', 0.8),
                       edgecolor='black',
                       linewidth=1)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            axes.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.1f}',
                     ha='center', va='bottom')

        axes.grid(True, alpha=0.3, axis='y')

        return {'plot_type': 'bar', 'bars': len(bars)}

    def _advanced_histogram_plot(self, axes: plt.Axes, x_data: List, y_data: List,
                                data: Dict[str, Any]) -> Dict[str, Any]:
        """Create advanced histogram with multiple datasets."""
        if not x_data:
            return {'error': 'No data provided'}

        # Handle multiple datasets
        if isinstance(x_data[0], (list, np.ndarray)):
            for i, dataset in enumerate(x_data):
                color = data.get('colors', plt.cm.tab10.colors)[i % len(plt.cm.tab10.colors)]
                axes.hist(dataset,
                         bins=data.get('bins', 30),
                         alpha=data.get('alpha', 0.7),
                         color=color,
                         label=f'Dataset {i+1}',
                         density=data.get('density', False))
        else:
            axes.hist(x_data,
                     bins=data.get('bins', 30),
                     alpha=data.get('alpha', 0.7),
                     color=data.get('color', 'skyblue'),
                     edgecolor='black',
                     density=data.get('density', False))

        if data.get('legend', True):
            axes.legend()

        return {'plot_type': 'histogram', 'bins': data.get('bins', 30)}

    def _advanced_contour_plot(self, axes: plt.Axes, x_data: List, y_data: List,
                              data: Dict[str, Any]) -> Dict[str, Any]:
        """Create advanced contour plot."""
        if not x_data or not y_data:
            return {'error': 'No data provided'}

        # Create meshgrid if data is 1D
        if len(np.array(x_data).shape) == 1:
            X, Y = np.meshgrid(x_data, y_data)
            Z = data.get('z', np.random.rand(len(x_data), len(y_data)))
        else:
            X, Y, Z = x_data, y_data, data.get('z', np.random.rand(len(x_data), len(y_data)))

        contour = axes.contourf(X, Y, Z,
                               levels=data.get('levels', 20),
                               cmap=data.get('colormap', 'viridis'),
                               alpha=data.get('alpha', 0.8))

        # Add contour lines
        axes.contour(X, Y, Z,
                    levels=data.get('contour_levels', 10),
                    colors='black',
                    linewidths=0.5)

        # Add colorbar
        plt.colorbar(contour, ax=axes, label=data.get('colorbar_label', 'Value'))

        return {'plot_type': 'contour', 'levels': data.get('levels', 20)}

    def _advanced_surface_plot(self, axes: plt.Axes, x_data: List, y_data: List,
                              data: Dict[str, Any]) -> Dict[str, Any]:
        """Create advanced 3D surface plot."""
        if not x_data or not y_data:
            return {'error': 'No data provided'}

        # Create 3D axes if not already 3D
        if not hasattr(axes, 'plot_surface'):
            fig = plt.gcf()
            axes = fig.add_subplot(111, projection='3d')

        # Create meshgrid
        if len(np.array(x_data).shape) == 1:
            X, Y = np.meshgrid(x_data, y_data)
            Z = data.get('z', np.random.rand(len(x_data), len(y_data)))
        else:
            X, Y, Z = x_data, y_data, data.get('z', np.random.rand(len(x_data), len(y_data)))

        # Create surface plot
        surf = axes.plot_surface(X, Y, Z,
                                cmap=data.get('colormap', 'viridis'),
                                alpha=data.get('alpha', 0.8),
                                linewidth=0,
                                antialiased=True)

        # Add colorbar
        plt.colorbar(surf, ax=axes, shrink=0.5, aspect=5, label=data.get('colorbar_label', 'Z Value'))

        return {'plot_type': 'surface', 'projection': '3d'}

    def _advanced_animation_plot(self, axes: plt.Axes, x_data: List, y_data: List,
                                data: Dict[str, Any]) -> Dict[str, Any]:
        """Create advanced animated plot."""
        if not x_data or not y_data:
            return {'error': 'No data provided'}

        # Create animation data
        frames = data.get('frames', 100)
        interval = data.get('interval', 50)

        def animate(frame):
            axes.clear()
            # Update data for animation
            current_x = x_data[:frame+1] if frame < len(x_data) else x_data
            current_y = y_data[:frame+1] if frame < len(y_data) else y_data

            axes.plot(current_x, current_y,
                     color=data.get('color', 'blue'),
                     linewidth=2,
                     marker='o',
                     markersize=4)
            axes.set_xlim(min(x_data), max(x_data))
            axes.set_ylim(min(y_data), max(y_data))
            axes.set_title(f'Frame {frame+1}/{frames}')
            axes.grid(True, alpha=0.3)

        anim = animation.FuncAnimation(plt.gcf(), animate, frames=frames,
                                     interval=interval, repeat=True)

        return {'plot_type': 'animation', 'frames': frames, 'animation': anim}

    def _add_advanced_annotations(self, axes: Union[plt.Axes, np.ndarray],
                                 data: Dict[str, Any]) -> None:
        """Add advanced annotations to the plot."""
        annotations = data.get('annotations', [])

        for ann in annotations:
            if isinstance(ann, dict):
                axes.annotate(ann.get('text', ''),
                             xy=ann.get('xy', (0, 0)),
                             xytext=ann.get('xytext', (0, 0)),
                             arrowprops=ann.get('arrowprops', {'arrowstyle': '->'}),
                             fontsize=ann.get('fontsize', 10),
                             ha=ann.get('ha', 'center'))

    def _customize_appearance(self, fig: plt.Figure, axes: Union[plt.Axes, np.ndarray],
                             title: str, xlabel: str, ylabel: str,
                             data: Dict[str, Any]) -> None:
        """Customize the overall appearance of the plot."""
        # Handle both single axes and array of axes
        if isinstance(axes, np.ndarray):
            for ax in axes.flat:
                self._customize_single_axes(ax, title, xlabel, ylabel, data)
        else:
            self._customize_single_axes(axes, title, xlabel, ylabel, data)

        # Customize figure
        fig.suptitle(data.get('suptitle', ''), fontsize=16, fontweight='bold')
        plt.tight_layout()

    def _customize_single_axes(self, ax: plt.Axes, title: str, xlabel: str,
                              ylabel: str, data: Dict[str, Any]) -> None:
        """Customize a single axes object."""
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)

        # Customize spines
        for spine in ax.spines.values():
            spine.set_linewidth(1.5)

        # Customize ticks
        ax.tick_params(axis='both', which='major', labelsize=10)

    def _add_interactive_elements(self, fig: plt.Figure, data: Dict[str, Any]) -> None:
        """Add interactive elements to the plot."""
        # This would typically involve connecting event handlers
        # For now, we'll add some basic interactive features
        pass

    def _get_plot_features(self, data: Dict[str, Any]) -> List[str]:
        """Get list of advanced features used in the plot."""
        features = []
        if data.get('annotations'):
            features.append('annotations')
        if data.get('interactive', False):
            features.append('interactive')
        if data.get('animation', False):
            features.append('animation')
        if data.get('colormap'):
            features.append('custom_colormap')
        if data.get('3d', False):
            features.append('3d_plotting')

        return features

    def create_custom_colormap(self, colors: List[Tuple[float, float, float]],
                              name: str = 'custom_cmap') -> LinearSegmentedColormap:
        """
        Create a custom colormap from a list of colors.

        Args:
            colors: List of RGB tuples (0-1 range)
            name: Name for the colormap

        Returns:
            Custom LinearSegmentedColormap
        """
        return LinearSegmentedColormap.from_list(name, colors)

    def advanced_image_processing(self, image_data: np.ndarray,
                                operation: str = 'enhance') -> Dict[str, Any]:
        """
        Advanced image processing and visualization.

        Args:
            image_data: Input image array
            operation: Type of processing ('enhance', 'filter', 'segment')

        Returns:
            Dictionary with processed image and metadata
        """
        try:
            fig, axes = plt.subplots(1, 2, figsize=(12, 5))

            # Original image
            axes[0].imshow(image_data, cmap='gray')
            axes[0].set_title('Original Image')
            axes[0].axis('off')

            # Processed image
            if operation == 'enhance':
                processed = self._enhance_image(image_data)
                title = 'Enhanced Image'
            elif operation == 'filter':
                processed = self._filter_image(image_data)
                title = 'Filtered Image'
            elif operation == 'segment':
                processed = self._segment_image(image_data)
                title = 'Segmented Image'
            else:
                processed = image_data
                title = 'Processed Image'

            axes[1].imshow(processed, cmap='gray')
            axes[1].set_title(title)
            axes[1].axis('off')

            plt.tight_layout()

            return {
                'figure': fig,
                'original': image_data,
                'processed': processed,
                'operation': operation
            }

        except Exception as e:
            return {'error': f'Image processing failed: {str(e)}'}

    def _enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Enhance image contrast and brightness."""
        # Simple histogram equalization
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)

        # Apply contrast enhancement
        enhanced = np.clip(image * 1.2 + 20, 0, 255).astype(np.uint8)
        return enhanced

    def _filter_image(self, image: np.ndarray) -> np.ndarray:
        """Apply filtering to image."""
        # Simple Gaussian-like filter
        from scipy.ndimage import gaussian_filter
        filtered = gaussian_filter(image, sigma=1)
        return filtered

    def _segment_image(self, image: np.ndarray) -> np.ndarray:
        """Segment image using thresholding."""
        threshold = np.mean(image)
        segmented = (image > threshold).astype(np.uint8) * 255
        return segmented

    def mathematical_text_rendering(self, expressions: List[str],
                                  positions: List[Tuple[float, float]] = None) -> Dict[str, Any]:
        """
        Render mathematical expressions using LaTeX.

        Args:
            expressions: List of LaTeX mathematical expressions
            positions: List of (x, y) positions for expressions

        Returns:
            Dictionary with rendered expressions and figure
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_xlim(0, 10)
            ax.set_ylim(0, len(expressions) + 1)
            ax.axis('off')

            if positions is None:
                positions = [(1, len(expressions) - i) for i in range(len(expressions))]

            for i, (expr, pos) in enumerate(zip(expressions, positions)):
                ax.text(pos[0], pos[1], f'${expr}$',
                       fontsize=14, ha='left', va='center')

            plt.tight_layout()

            return {
                'figure': fig,
                'expressions': expressions,
                'positions': positions
            }

        except Exception as e:
            return {'error': f'Mathematical text rendering failed: {str(e)}'}

    def statistical_visualization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create advanced statistical visualizations.

        Args:
            data: Dictionary containing statistical data

        Returns:
            Dictionary with statistical plots and metadata
        """
        try:
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle('Advanced Statistical Visualization', fontsize=16)

            # Box plot
            if 'box_data' in data:
                axes[0, 0].boxplot(data['box_data'])
                axes[0, 0].set_title('Box Plot')
                axes[0, 0].grid(True, alpha=0.3)

            # Violin plot
            if 'violin_data' in data:
                axes[0, 1].violinplot(data['violin_data'])
                axes[0, 1].set_title('Violin Plot')
                axes[0, 1].grid(True, alpha=0.3)

            # Histogram with KDE
            if 'hist_data' in data:
                axes[1, 0].hist(data['hist_data'], bins=30, alpha=0.7, density=True)
                axes[1, 0].set_title('Histogram with Density')
                axes[1, 0].grid(True, alpha=0.3)

            # Q-Q plot
            if 'qq_data' in data:
                # Simple Q-Q plot implementation
                sorted_data = np.sort(data['qq_data'])
                theoretical = np.random.normal(np.mean(sorted_data), np.std(sorted_data), len(sorted_data))
                theoretical = np.sort(theoretical)

                axes[1, 1].scatter(theoretical, sorted_data, alpha=0.6)
                axes[1, 1].plot([min(theoretical), max(theoretical)],
                               [min(theoretical), max(theoretical)], 'r--')
                axes[1, 1].set_title('Q-Q Plot')
                axes[1, 1].set_xlabel('Theoretical Quantiles')
                axes[1, 1].set_ylabel('Sample Quantiles')
                axes[1, 1].grid(True, alpha=0.3)

            plt.tight_layout()

            return {
                'figure': fig,
                'plot_types': ['box', 'violin', 'histogram', 'qq_plot'],
                'data_keys': list(data.keys())
            }

        except Exception as e:
            return {'error': f'Statistical visualization failed: {str(e)}'}
