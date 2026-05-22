"""
Advanced Pandas Operations Module for AXIOM

This module provides comprehensive advanced pandas operations, including:
- Advanced data manipulation and transformation
- Time series analysis and processing
- Data aggregation and grouping operations
- Advanced indexing and selection techniques
- Data cleaning and preprocessing pipelines
- Statistical analysis and descriptive statistics
- Data visualization integration
- Performance optimization techniques
- Memory-efficient operations
- Advanced merging and joining operations
- Rolling and expanding window operations
- Categorical data handling
- Text data processing and NLP integration

Author: AXIOM Development Team
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
import warnings
warnings.filterwarnings('ignore')


class AdvancedPandasOperations:
    """
    Advanced pandas operations for comprehensive data manipulation and analysis.
    """

    def __init__(self):
        """Initialize the advanced pandas operations."""
        self.time_series_methods = [
            'resample', 'rolling', 'expanding', 'ewm',
            'shift', 'diff', 'pct_change', 'cumsum', 'cumprod'
        ]
        self.aggregation_methods = [
            'mean', 'median', 'std', 'var', 'sum', 'count',
            'min', 'max', 'first', 'last', 'nunique'
        ]
        self.join_types = ['left', 'right', 'outer', 'inner', 'cross']

    def advanced_data_pipeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive data processing and analysis pipeline.

        Args:
            data: Dictionary containing data and configuration

        Returns:
            Dictionary with processed data and analysis results
        """
        try:
            # Load and prepare data
            df = self._load_data(data)

            # Data cleaning and preprocessing
            if data.get('cleaning', True):
                df = self._advanced_data_cleaning(df, data)

            # Feature engineering
            if data.get('feature_engineering', False):
                df = self._advanced_feature_engineering(df, data)

            # Time series processing
            if data.get('time_series_processing', False):
                df = self._time_series_processing(df, data)

            # Statistical analysis
            if data.get('statistical_analysis', False):
                stats_results = self._comprehensive_statistical_analysis(df, data)

            # Advanced aggregations
            if data.get('advanced_aggregations', False):
                aggregation_results = self._advanced_aggregations(df, data)

            # Data visualization preparation
            if data.get('prepare_visualization', False):
                visualization_data = self._prepare_visualization_data(df, data)

            results = {
                'processed_data': df,
                'data_info': {
                    'shape': df.shape,
                    'columns': df.columns.tolist(),
                    'dtypes': df.dtypes.to_dict(),
                    'memory_usage': df.memory_usage(deep=True).sum()
                }
            }

            if 'stats_results' in locals():
                results['statistical_analysis'] = stats_results
            if 'aggregation_results' in locals():
                results['aggregations'] = aggregation_results
            if 'visualization_data' in locals():
                results['visualization'] = visualization_data

            return results

        except Exception as e:
            return {'error': f'Advanced data pipeline failed: {str(e)}'}

    def _load_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Load data from various sources."""
        if 'dataframe' in data:
            return data['dataframe'].copy()
        elif 'csv_file' in data:
            return pd.read_csv(data['csv_file'], **data.get('read_params', {}))
        elif 'excel_file' in data:
            return pd.read_excel(data['excel_file'], **data.get('read_params', {}))
        elif 'json_file' in data:
            return pd.read_json(data['json_file'], **data.get('read_params', {}))
        elif 'sql_query' in data:
            # Assume connection is provided
            return pd.read_sql(data['sql_query'], data['connection'], **data.get('read_params', {}))
        else:
            raise ValueError("No valid data source provided")

    def _advanced_data_cleaning(self, df: pd.DataFrame, data: Dict[str, Any]) -> pd.DataFrame:
        """Perform comprehensive data cleaning operations."""
        df = df.copy()

        # Handle missing values
        if data.get('handle_missing', True):
            df = self._handle_missing_values(df, data)

        # Remove duplicates
        if data.get('remove_duplicates', False):
            df = df.drop_duplicates(**data.get('duplicates_params', {}))

        # Handle outliers
        if data.get('handle_outliers', False):
            df = self._handle_outliers(df, data)

        # Data type optimization
        if data.get('optimize_dtypes', False):
            df = self._optimize_data_types(df, data)

        # Text cleaning
        if data.get('text_cleaning', False):
            df = self._clean_text_data(df, data)

        return df

    def _handle_missing_values(self, df: pd.DataFrame, data: Dict[str, Any]) -> pd.DataFrame:
        """Advanced missing value handling."""
        strategy = data.get('missing_strategy', 'auto')

        if strategy == 'auto':
            # Automatically choose strategy based on data type
            for col in df.columns:
                if df[col].dtype in ['int64', 'float64']:
                    if df[col].isnull().sum() / len(df) < 0.1:  # Less than 10% missing
                        df[col] = df[col].fillna(df[col].median())
                    else:
                        df[col] = df[col].fillna(df[col].mean())
                elif df[col].dtype == 'object':
                    df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else 'Unknown')
        elif strategy == 'drop':
            df = df.dropna(**data.get('dropna_params', {}))
        elif strategy == 'interpolate':
            df = df.interpolate(**data.get('interpolate_params', {}))
        elif strategy == 'knn':
            from sklearn.impute import KNNImputer
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                imputer = KNNImputer(n_neighbors=data.get('knn_neighbors', 5))
                df[numeric_cols] = imputer.fit_transform(df[numeric_cols])

        return df

    def _handle_outliers(self, df: pd.DataFrame, data: Dict[str, Any]) -> pd.DataFrame:
        """Handle outliers using various methods."""
        method = data.get('outlier_method', 'iqr')

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df[col] = np.clip(df[col], lower_bound, upper_bound)
            elif method == 'zscore':
                from scipy import stats
                z_scores = np.abs(stats.zscore(df[col]))
                df[col] = df[col].mask(z_scores > 3, df[col].median())
            elif method == 'isolation_forest':
                from sklearn.ensemble import IsolationForest
                iso = IsolationForest(contamination=data.get('contamination', 0.1), random_state=42)
                outliers = iso.fit_predict(df[[col]])
                df[col] = df[col].mask(outliers == -1, df[col].median())

        return df

    def _optimize_data_types(self, df: pd.DataFrame, data: Dict[str, Any]) -> pd.DataFrame:
        """Optimize data types for memory efficiency."""
        df = df.copy()

        # Convert object columns to category if appropriate
        for col in df.select_dtypes(include=['object']):
            if df[col].nunique() / len(df) < 0.5:  # Less than 50% unique values
                df[col] = df[col].astype('category')

        # Downcast numeric types
        for col in df.select_dtypes(include=['int64']):
            df[col] = pd.to_numeric(df[col], downcast='integer')

        for col in df.select_dtypes(include=['float64']):
            df[col] = pd.to_numeric(df[col], downcast='float')

        return df

    def _clean_text_data(self, df: pd.DataFrame, data: Dict[str, Any]) -> pd.DataFrame:
        """Clean and preprocess text data."""
        import re

        text_columns = data.get('text_columns', df.select_dtypes(include=['object']).columns.tolist())

        for col in text_columns:
            if col in df.columns:
                # Remove special characters
                df[col] = df[col].astype(str).apply(lambda x: re.sub(r'[^\w\s]', '', x))

                # Convert to lowercase
                if data.get('lowercase', True):
                    df[col] = df[col].str.lower()

                # Remove extra whitespace
                df[col] = df[col].str.strip()

                # Remove stopwords if specified
                if data.get('remove_stopwords', False):
                    try:
                        from nltk.corpus import stopwords
                        stop_words = set(stopwords.words('english'))
                        df[col] = df[col].apply(lambda x: ' '.join([word for word in x.split() if word not in stop_words]))
                    except ImportError:
                        pass

        return df

    def _advanced_feature_engineering(self, df: pd.DataFrame, data: Dict[str, Any]) -> pd.DataFrame:
        """Perform advanced feature engineering."""
        df = df.copy()

        # Date/time features
        if data.get('datetime_features', False):
            df = self._create_datetime_features(df, data)

        # Categorical encoding
        if data.get('categorical_encoding', False):
            df = self._encode_categorical_features(df, data)

        # Interaction features
        if data.get('interaction_features', False):
            df = self._create_interaction_features(df, data)

        # Aggregation features
        if data.get('aggregation_features', False):
            df = self._create_aggregation_features(df, data)

        # Text features
        if data.get('text_features', False):
            df = self._create_text_features(df, data)

        return df

    def _create_datetime_features(self, df: pd.DataFrame, data: Dict[str, Any]) -> pd.DataFrame:
        """Create features from datetime columns."""
        datetime_cols = data.get('datetime_columns', [])

        for col in datetime_cols:
            if col in df.columns:
                if not pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = pd.to_datetime(df[col])

                # Extract various datetime components
                df[f'{col}_year'] = df[col].dt.year
                df[f'{col}_month'] = df[col].dt.month
                df[f'{col}_day'] = df[col].dt.day
                df[f'{col}_hour'] = df[col].dt.hour
                df[f'{col}_dayofweek'] = df[col].dt.dayofweek
                df[f'{col}_quarter'] = df[col].dt.quarter
                df[f'{col}_is_weekend'] = df[col].dt.dayofweek.isin([5, 6]).astype(int)

        return df

    def _encode_categorical_features(self, df: pd.DataFrame, data: Dict[str, Any]) -> pd.DataFrame:
        """Encode categorical features using various methods."""
        encoding_method = data.get('encoding_method', 'label')
        categorical_cols = data.get('categorical_columns', df.select_dtypes(include=['object', 'category']).columns.tolist())

        for col in categorical_cols:
            if encoding_method == 'label':
                from sklearn.preprocessing import LabelEncoder
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
            elif encoding_method == 'onehot':
                # One-hot encoding will be handled separately to avoid column explosion
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
                df = pd.concat([df, dummies], axis=1)
            elif encoding_method == 'frequency':
                freq = df[col].value_counts(normalize=True)
                df[f'{col}_freq'] = df[col].map(freq)

        return df

    def _create_interaction_features(self, df: pd.DataFrame, data: Dict[str, Any]) -> pd.DataFrame:
        """Create interaction features between columns."""
        interaction_pairs = data.get('interaction_pairs', [])

        for pair in interaction_pairs:
            if len(pair) == 2 and all(col in df.columns for col in pair):
                col1, col2 = pair
                # Create interaction features
                df[f'{col1}_{col2}_product'] = df[col1] * df[col2]
                df[f'{col1}_{col2}_ratio'] = df[col1] / (df[col2] + 1e-8)  # Avoid division by zero
                df[f'{col1}_{col2}_sum'] = df[col1] + df[col2]
                df[f'{col1}_{col2}_diff'] = df[col1] - df[col2]

        return df

    def _create_aggregation_features(self, df: pd.DataFrame, data: Dict[str, Any]) -> pd.DataFrame:
        """Create aggregation-based features."""
        groupby_cols = data.get('groupby_columns', [])
        agg_functions = data.get('agg_functions', ['mean', 'std', 'min', 'max'])

        if groupby_cols:
            for group_col in groupby_cols:
                if group_col in df.columns:
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    numeric_cols = [col for col in numeric_cols if col != group_col]

                    for func in agg_functions:
                        agg_result = df.groupby(group_col)[numeric_cols].transform(func)
                        for col in numeric_cols:
                            df[f'{col}_{func}_by_{group_col}'] = agg_result[col]

        return df

    def _create_text_features(self, df: pd.DataFrame, data: Dict[str, Any]) -> pd.DataFrame:
        """Create features from text columns."""
        text_columns = data.get('text_columns', df.select_dtypes(include=['object']).columns.tolist())

        for col in text_columns:
            if col in df.columns:
                # Basic text features
                df[f'{col}_length'] = df[col].astype(str).str.len()
                df[f'{col}_word_count'] = df[col].astype(str).str.split().str.len()
                df[f'{col}_unique_words'] = df[col].astype(str).apply(lambda x: len(set(x.split())))

                # Character-based features
                df[f'{col}_uppercase_ratio'] = df[col].astype(str).apply(lambda x: sum(1 for c in x if c.isupper()) / len(x) if len(x) > 0 else 0)
                df[f'{col}_digit_ratio'] = df[col].astype(str).apply(lambda x: sum(1 for c in x if c.isdigit()) / len(x) if len(x) > 0 else 0)

        return df

    def _time_series_processing(self, df: pd.DataFrame, data: Dict[str, Any]) -> pd.DataFrame:
        """Perform advanced time series processing."""
        df = df.copy()

        if 'datetime_column' in data:
            datetime_col = data['datetime_column']
            if datetime_col in df.columns:
                if not pd.api.types.is_datetime64_any_dtype(df[datetime_col]):
                    df[datetime_col] = pd.to_datetime(df[datetime_col])

                df = df.set_index(datetime_col)

                # Resampling
                if data.get('resample', False):
                    freq = data.get('resample_freq', 'D')
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    df_resampled = df[numeric_cols].resample(freq).mean()
                    df = df_resampled

                # Rolling window features
                if data.get('rolling_features', False):
                    window_sizes = data.get('window_sizes', [7, 14, 30])
                    numeric_cols = df.select_dtypes(include=[np.number]).columns

                    for window in window_sizes:
                        for col in numeric_cols:
                            df[f'{col}_rolling_mean_{window}'] = df[col].rolling(window=window).mean()
                            df[f'{col}_rolling_std_{window}'] = df[col].rolling(window=window).std()
                            df[f'{col}_rolling_min_{window}'] = df[col].rolling(window=window).min()
                            df[f'{col}_rolling_max_{window}'] = df[col].rolling(window=window).max()

                # Lag features
                if data.get('lag_features', False):
                    lag_periods = data.get('lag_periods', [1, 7, 14])
                    numeric_cols = df.select_dtypes(include=[np.number]).columns

                    for lag in lag_periods:
                        for col in numeric_cols:
                            df[f'{col}_lag_{lag}'] = df[col].shift(lag)

                # Seasonal decomposition
                if data.get('seasonal_decompose', False):
                    from statsmodels.tsa.seasonal import seasonal_decompose
                    target_col = data.get('target_column')
                    if target_col and target_col in df.columns:
                        decomposition = seasonal_decompose(df[target_col], model='additive', period=data.get('seasonal_period', 7))
                        df[f'{target_col}_trend'] = decomposition.trend
                        df[f'{target_col}_seasonal'] = decomposition.seasonal
                        df[f'{target_col}_residual'] = decomposition.resid

        return df

    def _comprehensive_statistical_analysis(self, df: pd.DataFrame, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive statistical analysis."""
        stats_results = {}

        # Basic descriptive statistics
        stats_results['describe'] = df.describe(include='all').to_dict()

        # Correlation analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            correlation_matrix = df[numeric_cols].corr()
            stats_results['correlation'] = correlation_matrix.to_dict()

            # Highly correlated pairs
            corr_pairs = []
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    corr = correlation_matrix.iloc[i, j]
                    if abs(corr) > data.get('correlation_threshold', 0.7):
                        corr_pairs.append({
                            'var1': numeric_cols[i],
                            'var2': numeric_cols[j],
                            'correlation': corr
                        })
            stats_results['high_correlations'] = corr_pairs

        # Distribution analysis
        distribution_stats = {}
        for col in numeric_cols:
            distribution_stats[col] = {
                'skewness': df[col].skew(),
                'kurtosis': df[col].kurtosis(),
                'normality_test': self._test_normality(df[col])
            }
        stats_results['distribution'] = distribution_stats

        # Outlier analysis
        outlier_stats = {}
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outlier_stats[col] = {
                'outliers_iqr': ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum(),
                'outlier_percentage': ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).mean() * 100
            }
        stats_results['outliers'] = outlier_stats

        return stats_results

    def _test_normality(self, series: pd.Series) -> Dict[str, Any]:
        """Test for normality using multiple tests."""
        try:
            from scipy import stats

            # Shapiro-Wilk test
            shapiro_stat, shapiro_p = stats.shapiro(series.dropna().sample(min(5000, len(series.dropna()))))

            # Kolmogorov-Smirnov test
            ks_stat, ks_p = stats.kstest(series.dropna(), 'norm',
                                       args=(series.mean(), series.std()))

            return {
                'shapiro_wilk': {'statistic': shapiro_stat, 'p_value': shapiro_p},
                'kolmogorov_smirnov': {'statistic': ks_stat, 'p_value': ks_p},
                'is_normal': shapiro_p > 0.05 and ks_p > 0.05
            }
        except Exception as e:
            return {'error': f'Normality test failed: {str(e)}'}

    def _advanced_aggregations(self, df: pd.DataFrame, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform advanced aggregation operations."""
        aggregation_results = {}

        groupby_cols = data.get('groupby_columns', [])
        agg_config = data.get('aggregation_config', {})

        if groupby_cols and agg_config:
            # Multi-level aggregation
            grouped = df.groupby(groupby_cols)

            for agg_name, agg_params in agg_config.items():
                if agg_name == 'pivot_table':
                    pivot = pd.pivot_table(df, **agg_params)
                    aggregation_results['pivot_table'] = pivot.to_dict()
                elif agg_name == 'crosstab':
                    crosstab = pd.crosstab(**agg_params)
                    aggregation_results['crosstab'] = crosstab.to_dict()
                else:
                    # Custom aggregation
                    result = grouped.agg(agg_params)
                    aggregation_results[agg_name] = result.to_dict()

        # Rolling aggregations
        if data.get('rolling_aggregations', False):
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            window_size = data.get('rolling_window', 7)

            rolling_results = {}
            for col in numeric_cols:
                rolling_stats = df[col].rolling(window=window_size).agg(['mean', 'std', 'min', 'max'])
                rolling_results[col] = rolling_stats.to_dict()

            aggregation_results['rolling_stats'] = rolling_results

        return aggregation_results

    def _prepare_visualization_data(self, df: pd.DataFrame, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for visualization."""
        visualization_data = {}

        # Time series plots
        if data.get('time_series_plots', False) and isinstance(df.index, pd.DatetimeIndex):
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            visualization_data['time_series'] = {
                'data': df[numeric_cols].to_dict(),
                'columns': numeric_cols.tolist()
            }

        # Correlation heatmap data
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            visualization_data['correlation_matrix'] = corr_matrix.to_dict()

        # Distribution data
        if data.get('distribution_plots', False):
            distributions = {}
            for col in numeric_cols:
                distributions[col] = {
                    'data': df[col].dropna().tolist(),
                    'bins': data.get('histogram_bins', 30)
                }
            visualization_data['distributions'] = distributions

        # Categorical data for bar plots
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if data.get('categorical_plots', False):
            categorical_data = {}
            for col in categorical_cols:
                value_counts = df[col].value_counts()
                categorical_data[col] = {
                    'categories': value_counts.index.tolist(),
                    'counts': value_counts.values.tolist()
                }
            visualization_data['categorical'] = categorical_data

        return visualization_data

    def advanced_merging_operations(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        Perform advanced merging and joining operations.

        Args:
            data: Dictionary containing dataframes and merge configuration

        Returns:
            Merged DataFrame
        """
        try:
            if 'dataframes' not in data or len(data['dataframes']) < 2:
                raise ValueError("At least two dataframes required for merging")

            dfs = data['dataframes']
            merge_config = data.get('merge_config', {})

            # Start with first dataframe
            result = dfs[0]

            # Perform sequential merges
            for i, df in enumerate(dfs[1:], 1):
                merge_params = merge_config.get(f'merge_{i}', {})
                how = merge_params.get('how', 'left')
                on = merge_params.get('on')
                left_on = merge_params.get('left_on')
                right_on = merge_params.get('right_on')

                result = pd.merge(result, df, how=how, on=on,
                                left_on=left_on, right_on=right_on,
                                suffixes=merge_params.get('suffixes', ('_x', '_y')))

            return result

        except Exception as e:
            raise Exception(f'Advanced merging failed: {str(e)}')

    def memory_optimization_pipeline(self, df: pd.DataFrame, data: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Optimize DataFrame memory usage.

        Args:
            df: Input DataFrame
            data: Configuration dictionary

        Returns:
            Tuple of optimized DataFrame and memory statistics
        """
        try:
            initial_memory = df.memory_usage(deep=True).sum()

            # Optimize data types
            df_optimized = self._optimize_data_types(df, data)

            # Chunk processing for large datasets
            if data.get('chunk_processing', False):
                chunk_size = data.get('chunk_size', 100000)
                if len(df) > chunk_size:
                    df_optimized = self._process_in_chunks(df_optimized, chunk_size, data)

            # Remove unnecessary columns
            if data.get('drop_columns'):
                df_optimized = df_optimized.drop(columns=data['drop_columns'], errors='ignore')

            final_memory = df_optimized.memory_usage(deep=True).sum()

            memory_stats = {
                'initial_memory_mb': initial_memory / 1024**2,
                'final_memory_mb': final_memory / 1024**2,
                'memory_reduction_mb': (initial_memory - final_memory) / 1024**2,
                'memory_reduction_percent': ((initial_memory - final_memory) / initial_memory) * 100
            }

            return df_optimized, memory_stats

        except Exception as e:
            raise Exception(f'Memory optimization failed: {str(e)}')

    def _process_in_chunks(self, df: pd.DataFrame, chunk_size: int, data: Dict[str, Any]) -> pd.DataFrame:
        """Process DataFrame in chunks for memory efficiency."""
        results = []

        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i+chunk_size].copy()

            # Apply processing to chunk
            if data.get('chunk_operations'):
                for operation in data['chunk_operations']:
                    if operation == 'fillna':
                        chunk = chunk.fillna(data.get('fillna_value', 0))
                    elif operation == 'normalize':
                        numeric_cols = chunk.select_dtypes(include=[np.number]).columns
                        chunk[numeric_cols] = (chunk[numeric_cols] - chunk[numeric_cols].mean()) / chunk[numeric_cols].std()

            results.append(chunk)

        return pd.concat(results, ignore_index=True)

    def advanced_groupby_operations(self, df: pd.DataFrame, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform advanced groupby operations with multiple aggregations.

        Args:
            df: Input DataFrame
            data: Configuration dictionary

        Returns:
            Dictionary with groupby results
        """
        try:
            groupby_cols = data.get('groupby_columns', [])
            if not groupby_cols:
                raise ValueError("Groupby columns must be specified")

            grouped = df.groupby(groupby_cols)

            results = {}

            # Multiple aggregations
            if data.get('aggregations'):
                agg_dict = data['aggregations']
                results['aggregated'] = grouped.agg(agg_dict).to_dict()

            # Transform operations
            if data.get('transforms'):
                transform_dict = data['transforms']
                transformed = grouped.transform(transform_dict)
                results['transformed'] = transformed.to_dict()

            # Custom aggregation functions
            if data.get('custom_agg'):
                custom_results = {}
                for col, func in data['custom_agg'].items():
                    if callable(func):
                        custom_results[col] = grouped[col].apply(func).to_dict()
                results['custom'] = custom_results

            # Group-wise operations
            if data.get('group_operations'):
                group_ops = {}
                for operation in data['group_operations']:
                    if operation == 'cumsum':
                        group_ops['cumsum'] = grouped.cumsum().to_dict()
                    elif operation == 'rank':
                        group_ops['rank'] = grouped.rank().to_dict()
                    elif operation == 'pct_change':
                        group_ops['pct_change'] = grouped.pct_change().to_dict()
                results['group_operations'] = group_ops

            return results

        except Exception as e:
            raise Exception(f'Advanced groupby operations failed: {str(e)}')

    def time_series_forecasting_pipeline(self, df: pd.DataFrame, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Advanced time series forecasting pipeline.

        Args:
            df: Time series DataFrame
            data: Configuration dictionary

        Returns:
            Dictionary with forecasting results
        """
        try:
            target_col = data.get('target_column')
            if not target_col or target_col not in df.columns:
                raise ValueError("Target column must be specified and exist in DataFrame")

            # Ensure datetime index
            if 'datetime_column' in data:
                df = df.set_index(data['datetime_column'])

            # Stationarity tests
            stationarity_results = self._test_stationarity(df[target_col])

            # Decomposition
            decomposition_results = self._decompose_time_series(df[target_col], data)

            # Forecasting models
            forecast_results = {}

            if data.get('arima', False):
                forecast_results['arima'] = self._fit_arima_model(df[target_col], data)

            if data.get('prophet', False):
                forecast_results['prophet'] = self._fit_prophet_model(df, target_col, data)

            if data.get('exponential_smoothing', False):
                forecast_results['exp_smoothing'] = self._fit_exponential_smoothing(df[target_col], data)

            return {
                'stationarity': stationarity_results,
                'decomposition': decomposition_results,
                'forecasts': forecast_results,
                'data_info': {
                    'length': len(df),
                    'frequency': pd.infer_freq(df.index) if hasattr(df.index, 'freq') else None
                }
            }

        except Exception as e:
            raise Exception(f'Time series forecasting failed: {str(e)}')

    def _test_stationarity(self, series: pd.Series) -> Dict[str, Any]:
        """Test time series stationarity."""
        try:
            from statsmodels.tsa.stattools import adfuller, kpss

            # Augmented Dickey-Fuller test
            adf_result = adfuller(series.dropna())
            adf_output = {
                'statistic': adf_result[0],
                'p_value': adf_result[1],
                'critical_values': adf_result[4],
                'is_stationary': adf_result[1] < 0.05
            }

            # KPSS test
            kpss_result = kpss(series.dropna())
            kpss_output = {
                'statistic': kpss_result[0],
                'p_value': kpss_result[1],
                'critical_values': kpss_result[3],
                'is_stationary': kpss_result[1] > 0.05
            }

            return {
                'adf_test': adf_output,
                'kpss_test': kpss_output,
                'conclusion': 'Stationary' if adf_output['is_stationary'] and kpss_output['is_stationary'] else 'Non-stationary'
            }

        except Exception as e:
            return {'error': f'Stationarity test failed: {str(e)}'}

    def _decompose_time_series(self, series: pd.Series, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decompose time series into trend, seasonal, and residual components."""
        try:
            from statsmodels.tsa.seasonal import seasonal_decompose

            model = data.get('decomposition_model', 'additive')
            period = data.get('seasonal_period', 7)

            decomposition = seasonal_decompose(series, model=model, period=period)

            return {
                'trend': decomposition.trend.dropna().tolist(),
                'seasonal': decomposition.seasonal.dropna().tolist(),
                'residual': decomposition.resid.dropna().tolist(),
                'observed': decomposition.observed.dropna().tolist(),
                'model': model,
                'period': period
            }

        except Exception as e:
            return {'error': f'Decomposition failed: {str(e)}'}

    def _fit_arima_model(self, series: pd.Series, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fit ARIMA model for forecasting."""
        try:
            from statsmodels.tsa.arima.model import ARIMA

            order = data.get('arima_order', (1, 1, 1))
            model = ARIMA(series, order=order)
            fitted_model = model.fit()

            # Forecast
            forecast_steps = data.get('forecast_steps', 10)
            forecast = fitted_model.forecast(steps=forecast_steps)

            return {
                'order': order,
                'aic': fitted_model.aic,
                'bic': fitted_model.bic,
                'forecast': forecast.tolist(),
                'forecast_steps': forecast_steps,
                'fitted_values': fitted_model.fittedvalues.tolist()
            }

        except Exception as e:
            return {'error': f'ARIMA fitting failed: {str(e)}'}

    def _fit_prophet_model(self, df: pd.DataFrame, target_col: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fit Facebook Prophet model for forecasting."""
        try:
            from prophet import Prophet

            # Prepare data for Prophet
            prophet_df = pd.DataFrame({
                'ds': df.index,
                'y': df[target_col]
            })

            model = Prophet(**data.get('prophet_params', {}))
            model.fit(prophet_df)

            # Make future dataframe
            future_periods = data.get('forecast_steps', 30)
            future = model.make_future_dataframe(periods=future_periods)

            # Forecast
            forecast = model.predict(future)

            return {
                'forecast': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict(),
                'components': {
                    'trend': forecast['trend'].tolist(),
                    'seasonal': forecast['yearly'].tolist() if 'yearly' in forecast.columns else None
                },
                'forecast_periods': future_periods
            }

        except Exception as e:
            return {'error': f'Prophet fitting failed: {str(e)}'}

    def _fit_exponential_smoothing(self, series: pd.Series, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fit exponential smoothing model."""
        try:
            from statsmodels.tsa.holtwinters import ExponentialSmoothing

            model = ExponentialSmoothing(series, **data.get('exp_smoothing_params', {}))
            fitted_model = model.fit()

            # Forecast
            forecast_steps = data.get('forecast_steps', 10)
            forecast = fitted_model.forecast(steps=forecast_steps)

            return {
                'forecast': forecast.tolist(),
                'fitted_values': fitted_model.fittedvalues.tolist(),
                'forecast_steps': forecast_steps,
                'aic': fitted_model.aic if hasattr(fitted_model, 'aic') else None
            }

        except Exception as e:
            return {'error': f'Exponential smoothing failed: {str(e)}'}
