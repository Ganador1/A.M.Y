"""
Advanced Plotly Operations Module for AXIOM

This module provides comprehensive advanced Plotly operations, including:
- Interactive visualizations with Plotly Express and Graph Objects
- Advanced chart types (3D plots, animations, subplots)
- Custom styling and theming
- Dashboard components and layouts
- Real-time data visualization
- Statistical plots and distributions
- Geographic and map visualizations
- Financial charts and time series
- Custom callbacks and interactivity

Author: AXIOM Development Team
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')


class AdvancedPlotlyOperations:
    """
    Advanced Plotly operations for comprehensive interactive data visualization.
    """

    def __init__(self):
        """Initialize the advanced Plotly operations."""
        self.themes = ['plotly', 'plotly_white', 'plotly_dark', 'ggplot2', 'seaborn', 'simple_white', 'none']
        self.color_sequences = px.colors.qualitative.__all__
        self.chart_types = [
            'scatter', 'line', 'bar', 'histogram', 'box', 'violin', 'heatmap',
            'contour', 'surface', 'scatter_3d', 'line_3d', 'mesh_3d', 'scatter_polar',
            'bar_polar', 'choropleth', 'scatter_geo', 'density_heatmap', 'density_contour'
        ]

    def advanced_visualization_pipeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive interactive visualization pipeline.

        Args:
            data: Dictionary containing plot data and configuration

        Returns:
            Dictionary with interactive plot and metadata
        """
        try:
            # Extract data
            df = data.get('dataframe')
            if df is None and 'data' in data:
                df = pd.DataFrame(data['data'])

            chart_type = data.get('type', 'scatter')
            # Title will be handled in individual plot functions

            # Create advanced visualization
            if chart_type in ['scatter', 'line', 'bar', 'histogram', 'box', 'violin']:
                fig = self._create_express_plot(df, chart_type, data)
            elif chart_type in ['heatmap', 'contour', 'surface', 'scatter_3d', 'line_3d']:
                fig = self._create_3d_plot(df, chart_type, data)
            elif chart_type in ['choropleth', 'scatter_geo']:
                fig = self._create_geo_plot(df, chart_type, data)
            else:
                fig = self._create_custom_plot(df, chart_type, data)

            # Apply advanced styling
            fig = self._apply_advanced_styling(fig, data)

            # Add interactivity
            fig = self._add_interactivity(fig, data)

            return {
                'figure': fig,
                'chart_type': chart_type,
                'data_shape': df.shape if df is not None else None,
                'interactive_features': self._get_interactive_features(data),
                'metadata': {
                    'theme': data.get('theme', 'plotly'),
                    'animation_enabled': data.get('animation_frame') is not None,
                    'facets': data.get('facet_row') is not None or data.get('facet_col') is not None
                }
            }

        except Exception as e:
            return {'error': f'Advanced visualization failed: {str(e)}'}

    def _create_express_plot(self, df: pd.DataFrame, chart_type: str,
                           data: Dict[str, Any]) -> go.Figure:
        """Create Plotly Express plots with advanced features."""
        plot_config = {
            'data_frame': df,
            'title': data.get('title', 'Plot'),
            'template': data.get('theme', 'plotly'),
            'width': data.get('width', 800),
            'height': data.get('height', 600)
        }

        # Add common parameters
        for param in ['x', 'y', 'color', 'size', 'symbol', 'facet_row', 'facet_col',
                     'animation_frame', 'animation_group', 'hover_name', 'hover_data']:
            if param in data:
                plot_config[param] = data[param]

        # Create specific plot types
        if chart_type == 'scatter':
            plot_config.update({
                'trendline': data.get('trendline'),
                'marginal_x': data.get('marginal_x'),
                'marginal_y': data.get('marginal_y')
            })
            return px.scatter(**plot_config)

        elif chart_type == 'line':
            plot_config['line_shape'] = data.get('line_shape', 'linear')
            return px.line(**plot_config)

        elif chart_type == 'bar':
            plot_config['barmode'] = data.get('barmode', 'group')
            plot_config['pattern_shape'] = data.get('pattern_shape')
            return px.bar(**plot_config)

        elif chart_type == 'histogram':
            plot_config['nbins'] = data.get('nbins', 30)
            plot_config['histnorm'] = data.get('histnorm')
            plot_config['marginal'] = data.get('marginal')
            return px.histogram(**plot_config)

        elif chart_type == 'box':
            plot_config['notched'] = data.get('notched', False)
            plot_config['points'] = data.get('points', 'outliers')
            return px.box(**plot_config)

        elif chart_type == 'violin':
            plot_config['box'] = data.get('box', False)
            plot_config['points'] = data.get('points', 'outliers')
            return px.violin(**plot_config)

    def _create_3d_plot(self, df: pd.DataFrame, chart_type: str,
                       data: Dict[str, Any]) -> go.Figure:
        """Create 3D and advanced plots."""
        if chart_type == 'scatter_3d':
            return px.scatter_3d(
                df,
                x=data.get('x'),
                y=data.get('y'),
                z=data.get('z'),
                color=data.get('color'),
                size=data.get('size'),
                title=data.get('title', '3D Scatter Plot'),
                template=data.get('theme', 'plotly')
            )

        elif chart_type == 'line_3d':
            return px.line_3d(
                df,
                x=data.get('x'),
                y=data.get('y'),
                z=data.get('z'),
                color=data.get('color'),
                title=data.get('title', '3D Line Plot'),
                template=data.get('theme', 'plotly')
            )

        elif chart_type == 'surface':
            return go.Figure(data=[go.Surface(
                z=data.get('z', np.random.rand(10, 10)),
                colorscale=data.get('colorscale', 'Viridis')
            )])

        elif chart_type == 'heatmap':
            return px.imshow(
                data.get('z', np.random.rand(10, 10)),
                title=data.get('title', 'Heatmap'),
                template=data.get('theme', 'plotly')
            )

        elif chart_type == 'contour':
            return px.imshow(
                data.get('z', np.random.rand(10, 10)),
                title=data.get('title', 'Contour Plot'),
                template=data.get('theme', 'plotly')
            )

    def _create_geo_plot(self, df: pd.DataFrame, chart_type: str,
                        data: Dict[str, Any]) -> go.Figure:
        """Create geographic and map visualizations."""
        if chart_type == 'choropleth':
            return px.choropleth(
                df,
                locations=data.get('locations'),
                locationmode=data.get('locationmode', 'country names'),
                color=data.get('color'),
                hover_name=data.get('hover_name'),
                animation_frame=data.get('animation_frame'),
                title=data.get('title', 'Choropleth Map'),
                template=data.get('theme', 'plotly')
            )

        elif chart_type == 'scatter_geo':
            return px.scatter_geo(
                df,
                lat=data.get('lat'),
                lon=data.get('lon'),
                color=data.get('color'),
                size=data.get('size'),
                hover_name=data.get('hover_name'),
                animation_frame=data.get('animation_frame'),
                title=data.get('title', 'Geographic Scatter Plot'),
                template=data.get('theme', 'plotly')
            )

    def _create_custom_plot(self, df: pd.DataFrame, chart_type: str,
                           data: Dict[str, Any]) -> go.Figure:
        """Create custom advanced plots using graph objects."""
        if chart_type == 'subplots':
            return self._create_subplot_figure(data)

        elif chart_type == 'parallel_coordinates':
            return px.parallel_coordinates(
                df,
                dimensions=data.get('dimensions'),
                color=data.get('color'),
                title=data.get('title', 'Parallel Coordinates'),
                template=data.get('theme', 'plotly')
            )

        elif chart_type == 'parallel_categories':
            return px.parallel_categories(
                df,
                dimensions=data.get('dimensions'),
                color=data.get('color'),
                title=data.get('title', 'Parallel Categories'),
                template=data.get('theme', 'plotly')
            )

        elif chart_type == 'scatter_matrix':
            return px.scatter_matrix(
                df,
                dimensions=data.get('dimensions'),
                color=data.get('color'),
                title=data.get('title', 'Scatter Matrix'),
                template=data.get('theme', 'plotly')
            )

        else:
            # Default to scatter plot
            return px.scatter(df, title='Custom Plot', template=data.get('theme', 'plotly'))

    def _create_subplot_figure(self, data: Dict[str, Any]) -> go.Figure:
        """Create complex subplot figures."""
        subplot_config = data.get('subplot_config', {})
        rows = subplot_config.get('rows', 2)
        cols = subplot_config.get('cols', 2)

        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=subplot_config.get('titles', []),
            specs=subplot_config.get('specs')
        )

        # Add traces to subplots
        traces = data.get('traces', [])
        for trace in traces:
            fig.add_trace(
                trace['data'],
                row=trace.get('row', 1),
                col=trace.get('col', 1)
            )

        fig.update_layout(
            title=data.get('title', 'Subplot Figure'),
            template=data.get('theme', 'plotly')
        )

        return fig

    def _apply_advanced_styling(self, fig: go.Figure, data: Dict[str, Any]) -> go.Figure:
        """Apply advanced styling and customization."""
        # Update layout
        layout_updates = {
            'font': dict(
                family=data.get('font_family', 'Arial'),
                size=data.get('font_size', 12),
                color=data.get('font_color', 'black')
            ),
            'paper_bgcolor': data.get('paper_bgcolor', 'white'),
            'plot_bgcolor': data.get('plot_bgcolor', 'white')
        }

        # Add custom styling
        if 'layout_updates' in data:
            layout_updates.update(data['layout_updates'])

        fig.update_layout(**layout_updates)

        # Update axes
        if 'xaxis' in data:
            fig.update_xaxes(**data['xaxis'])
        if 'yaxis' in data:
            fig.update_yaxes(**data['yaxis'])

        # Add annotations
        if 'annotations' in data:
            fig.add_annotation(**data['annotations'])

        # Add shapes
        if 'shapes' in data:
            fig.add_shape(**data['shapes'])

        return fig

    def _add_interactivity(self, fig: go.Figure, data: Dict[str, Any]) -> go.Figure:
        """Add interactive features to the plot."""
        # Add buttons for interactivity
        if data.get('add_buttons', False):
            fig.update_layout(
                updatemenus=[
                    dict(
                        type="buttons",
                        buttons=[
                            dict(label="Play",
                                method="animate",
                                args=[None, dict(frame=dict(duration=500, redraw=True), mode='immediate')]),
                            dict(label="Pause",
                                method="animate",
                                args=[[None], dict(frame=dict(duration=0, redraw=False), mode='immediate')])
                        ]
                    )
                ]
            )

        # Add sliders for animation
        if data.get('add_sliders', False) and data.get('animation_frame'):
            fig.update_layout(
                sliders=[
                    dict(
                        active=0,
                        steps=[
                            dict(method="animate",
                                args=[[f.name], dict(mode='immediate', frame=dict(duration=300, redraw=True))],
                                label=f.name)
                            for f in fig.frames
                        ] if hasattr(fig, 'frames') and fig.frames else []
                    )
                ]
            )

        return fig

    def _get_interactive_features(self, data: Dict[str, Any]) -> List[str]:
        """Get list of interactive features enabled."""
        features = []
        if data.get('animation_frame'):
            features.append('animation')
        if data.get('hover_name') or data.get('hover_data'):
            features.append('hover_tooltips')
        if data.get('facet_row') or data.get('facet_col'):
            features.append('faceting')
        if data.get('add_buttons', False):
            features.append('play_pause_buttons')
        if data.get('add_sliders', False):
            features.append('sliders')

        return features

    def statistical_visualization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create advanced statistical visualizations.

        Args:
            data: Dictionary containing statistical data

        Returns:
            Dictionary with statistical plots
        """
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=['Distribution Plot', 'Box Plot', 'Violin Plot', 'QQ Plot'],
                specs=[[{'type': 'xy'}, {'type': 'xy'}],
                       [{'type': 'xy'}, {'type': 'xy'}]]
            )

            # Distribution plot
            if 'distribution_data' in data:
                hist_data = data['distribution_data']
                fig.add_trace(
                    go.Histogram(x=hist_data, name='Histogram'),
                    row=1, col=1
                )

            # Box plot
            if 'box_data' in data:
                box_data = data['box_data']
                fig.add_trace(
                    go.Box(y=box_data, name='Box Plot'),
                    row=1, col=2
                )

            # Violin plot
            if 'violin_data' in data:
                violin_data = data['violin_data']
                fig.add_trace(
                    go.Violin(y=violin_data, name='Violin Plot'),
                    row=2, col=1
                )

            # QQ plot
            if 'qq_data' in data:
                qq_data = data['qq_data']
                sorted_data = np.sort(qq_data)
                theoretical = np.random.normal(np.mean(qq_data), np.std(qq_data), len(qq_data))
                theoretical = np.sort(theoretical)

                fig.add_trace(
                    go.Scatter(x=theoretical, y=sorted_data, mode='markers', name='QQ Plot'),
                    row=2, col=2
                )

            fig.update_layout(
                title='Advanced Statistical Visualization',
                template='plotly_white'
            )

            return {
                'figure': fig,
                'plot_types': ['histogram', 'box', 'violin', 'qq'],
                'data_keys': list(data.keys())
            }

        except Exception as e:
            return {'error': f'Statistical visualization failed: {str(e)}'}

    def dashboard_components(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create dashboard components with multiple visualizations.

        Args:
            components: List of component configurations

        Returns:
            Dictionary with dashboard figure
        """
        try:
            # Calculate grid layout
            n_components = len(components)
            rows = int(np.ceil(np.sqrt(n_components)))
            cols = int(np.ceil(n_components / rows))

            fig = make_subplots(
                rows=rows,
                cols=cols,
                subplot_titles=[comp.get('title', f'Component {i+1}') for i, comp in enumerate(components)]
            )

            for i, component in enumerate(components):
                row = i // cols + 1
                col = i % cols + 1

                # Create component visualization
                comp_fig = self.advanced_visualization_pipeline(component)
                if 'figure' in comp_fig:
                    # Add traces from component to dashboard
                    for trace in comp_fig['figure'].data:
                        fig.add_trace(trace, row=row, col=col)

            fig.update_layout(
                title='Interactive Dashboard',
                template='plotly_white',
                height=800
            )

            return {
                'figure': fig,
                'components': len(components),
                'layout': f'{rows}x{cols}'
            }

        except Exception as e:
            return {'error': f'Dashboard creation failed: {str(e)}'}

    def real_time_visualization(self, data_stream: Any,
                               update_interval: int = 1000) -> Dict[str, Any]:
        """
        Create real-time visualization setup.

        Args:
            data_stream: Data stream or generator
            update_interval: Update interval in milliseconds

        Returns:
            Dictionary with real-time visualization setup
        """
        try:
            # Create initial figure
            fig = go.Figure()

            # Add initial data
            if hasattr(data_stream, '__iter__'):
                initial_data = next(iter(data_stream))
                fig.add_trace(go.Scatter(x=initial_data.get('x', []),
                                       y=initial_data.get('y', []),
                                       mode='lines+markers'))

            # Configure for real-time updates
            fig.update_layout(
                title='Real-time Visualization',
                xaxis=dict(range=[0, 100]),
                yaxis=dict(range=[0, 100]),
                template='plotly_white'
            )

            return {
                'figure': fig,
                'update_interval': update_interval,
                'real_time_enabled': True,
                'data_stream_type': type(data_stream).__name__
            }

        except Exception as e:
            return {'error': f'Real-time visualization setup failed: {str(e)}'}

    def financial_charts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create advanced financial charts and visualizations.

        Args:
            data: Dictionary containing financial data

        Returns:
            Dictionary with financial charts
        """
        try:
            fig = make_subplots(
                rows=3, cols=1,
                subplot_titles=['Candlestick', 'Volume', 'Technical Indicators'],
                specs=[[{'type': 'candlestick'}],
                       [{'type': 'bar'}],
                       [{'type': 'scatter'}]],
                shared_xaxes=True,
                vertical_spacing=0.05
            )

            # Candlestick chart
            if 'ohlc' in data:
                ohlc_data = data['ohlc']
                fig.add_trace(
                    go.Candlestick(
                        x=ohlc_data.get('dates', []),
                        open=ohlc_data.get('open', []),
                        high=ohlc_data.get('high', []),
                        low=ohlc_data.get('low', []),
                        close=ohlc_data.get('close', [])
                    ),
                    row=1, col=1
                )

            # Volume chart
            if 'volume' in data:
                fig.add_trace(
                    go.Bar(x=data['dates'], y=data['volume'], name='Volume'),
                    row=2, col=1
                )

            # Technical indicators
            if 'indicators' in data:
                for indicator_name, indicator_data in data['indicators'].items():
                    fig.add_trace(
                        go.Scatter(x=data['dates'], y=indicator_data,
                                 mode='lines', name=indicator_name),
                        row=3, col=1
                    )

            fig.update_layout(
                title='Advanced Financial Chart',
                xaxis_rangeslider_visible=False,
                template='plotly_white'
            )

            return {
                'figure': fig,
                'chart_types': ['candlestick', 'volume', 'indicators'],
                'data_keys': list(data.keys())
            }

        except Exception as e:
            return {'error': f'Financial chart creation failed: {str(e)}'}
