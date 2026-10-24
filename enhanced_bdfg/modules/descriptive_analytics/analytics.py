"""
Descriptive Analytics Module

This module contains the DescriptiveAnalytics class, which provides descriptive analytics
capabilities for analyzing historical data to identify patterns and trends.
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional, Tuple, Union
import json
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DescriptiveAnalytics:
    """
    The DescriptiveAnalytics class provides methods for analyzing historical data
    to identify patterns and trends.
    
    It includes functionality for data summarization, pattern identification,
    trend analysis, and anomaly detection.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the DescriptiveAnalytics module.
        
        Args:
            config: Configuration parameters for the module.
        """
        self.config = config or {}
        logger.info("Initializing DescriptiveAnalytics module")
        
        # Set default parameters
        self.time_window = self.config.get("time_window", "1M")  # Default 1 month
        self.aggregation_level = self.config.get("aggregation_level", "day")
        self.anomaly_threshold = self.config.get("anomaly_threshold", 2.0)  # Standard deviations
        
        logger.info("DescriptiveAnalytics module initialized successfully")
    
    def summarize_data(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Generate a statistical summary of the data.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            
        Returns:
            A dictionary containing summary statistics.
        """
        logger.info("Generating data summary")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        # Generate summary statistics
        summary = {}
        
        # Basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if not numeric_cols.empty:
            summary["numeric"] = {}
            for col in numeric_cols:
                summary["numeric"][col] = {
                    "mean": df[col].mean(),
                    "median": df[col].median(),
                    "std": df[col].std(),
                    "min": df[col].min(),
                    "max": df[col].max(),
                    "q1": df[col].quantile(0.25),
                    "q3": df[col].quantile(0.75)
                }
        
        # Frequency counts for categorical columns
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns
        if not categorical_cols.empty:
            summary["categorical"] = {}
            for col in categorical_cols:
                value_counts = df[col].value_counts().to_dict()
                # Limit to top 10 categories if there are many
                if len(value_counts) > 10:
                    top_items = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                    value_counts = {k: v for k, v in top_items}
                    value_counts["other"] = df[col].value_counts().sum() - sum(value_counts.values())
                
                summary["categorical"][col] = value_counts
        
        # Record count and column information
        summary["record_count"] = len(df)
        summary["column_count"] = len(df.columns)
        summary["columns"] = list(df.columns)
        
        # Missing value information
        missing_values = df.isnull().sum().to_dict()
        summary["missing_values"] = {k: v for k, v in missing_values.items() if v > 0}
        
        logger.info(f"Data summary generated: {len(df)} records, {len(df.columns)} columns")
        return summary
    
    def identify_patterns(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
                         time_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Identify patterns in the data.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            time_column: Name of the column containing time/date information.
            
        Returns:
            A dictionary containing identified patterns.
        """
        logger.info("Identifying patterns in data")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        patterns = {}
        
        # Time-based patterns if time column is provided
        if time_column and time_column in df.columns:
            # Convert to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(df[time_column]):
                try:
                    df[time_column] = pd.to_datetime(df[time_column])
                except Exception as e:
                    logger.warning(f"Could not convert {time_column} to datetime: {e}")
            
            if pd.api.types.is_datetime64_any_dtype(df[time_column]):
                # Add time components
                df['year'] = df[time_column].dt.year
                df['month'] = df[time_column].dt.month
                df['day'] = df[time_column].dt.day
                df['weekday'] = df[time_column].dt.weekday
                df['hour'] = df[time_column].dt.hour if 'hour' in str(df[time_column].dtype) else None
                
                # Identify time-based patterns
                patterns["time_based"] = self._analyze_time_patterns(df, time_column)
        
        # Correlation patterns for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            # Calculate correlation matrix
            corr_matrix = df[numeric_cols].corr().round(2)
            
            # Find strong correlations (absolute value > 0.7)
            strong_correlations = []
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    if abs(corr_matrix.iloc[i, j]) > 0.7:
                        strong_correlations.append({
                            "variables": (numeric_cols[i], numeric_cols[j]),
                            "correlation": corr_matrix.iloc[i, j]
                        })
            
            patterns["correlations"] = {
                "strong_correlations": strong_correlations,
                "correlation_matrix": corr_matrix.to_dict()
            }
        
        # Distribution patterns
        patterns["distributions"] = {}
        for col in numeric_cols:
            # Check for normal distribution using skewness and kurtosis
            skewness = df[col].skew()
            kurtosis = df[col].kurtosis()
            
            distribution_type = "unknown"
            if abs(skewness) < 0.5 and abs(kurtosis) < 0.5:
                distribution_type = "normal"
            elif skewness > 1:
                distribution_type = "right_skewed"
            elif skewness < -1:
                distribution_type = "left_skewed"
            
            patterns["distributions"][col] = {
                "type": distribution_type,
                "skewness": skewness,
                "kurtosis": kurtosis
            }
        
        # Categorical patterns
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns
        if not categorical_cols.empty:
            patterns["categorical"] = {}
            for col in categorical_cols:
                # Calculate entropy to measure randomness/uniformity
                value_counts = df[col].value_counts(normalize=True)
                entropy = -sum(value_counts * np.log2(value_counts))
                max_entropy = np.log2(len(value_counts)) if len(value_counts) > 0 else 0
                normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
                
                patterns["categorical"][col] = {
                    "unique_values": df[col].nunique(),
                    "entropy": entropy,
                    "normalized_entropy": normalized_entropy,
                    "is_uniform": normalized_entropy > 0.9  # Close to uniform distribution
                }
        
        logger.info(f"Pattern identification completed: {len(patterns)} pattern types identified")
        return patterns
    
    def analyze_trends(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
                      time_column: str, value_column: str) -> Dict[str, Any]:
        """
        Analyze trends in time series data.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            time_column: Name of the column containing time/date information.
            value_column: Name of the column containing the values to analyze.
            
        Returns:
            A dictionary containing trend analysis results.
        """
        logger.info(f"Analyzing trends for {value_column} over {time_column}")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        # Ensure time column is datetime
        if not pd.api.types.is_datetime64_any_dtype(df[time_column]):
            try:
                df[time_column] = pd.to_datetime(df[time_column])
            except Exception as e:
                logger.error(f"Could not convert {time_column} to datetime: {e}")
                return {"error": f"Could not convert {time_column} to datetime"}
        
        # Sort by time
        df = df.sort_values(by=time_column)
        
        # Resample data based on aggregation level
        if self.aggregation_level == "day":
            resampled = df.set_index(time_column).resample('D').agg({value_column: 'mean'})
        elif self.aggregation_level == "week":
            resampled = df.set_index(time_column).resample('W').agg({value_column: 'mean'})
        elif self.aggregation_level == "month":
            resampled = df.set_index(time_column).resample('M').agg({value_column: 'mean'})
        else:
            resampled = df.set_index(time_column)
        
        # Fill missing values
        resampled = resampled.fillna(method='ffill')
        
        # Calculate trend components
        try:
            from statsmodels.tsa.seasonal import seasonal_decompose
            
            # Decompose time series
            result = seasonal_decompose(resampled[value_column], model='additive', period=self._get_period())
            
            trend_analysis = {
                "trend": result.trend.dropna().to_dict(),
                "seasonal": result.seasonal.dropna().to_dict(),
                "residual": result.resid.dropna().to_dict(),
                "original": result.observed.to_dict()
            }
            
            # Calculate overall trend direction and magnitude
            trend_series = result.trend.dropna()
            if len(trend_series) > 1:
                start_value = trend_series.iloc[0]
                end_value = trend_series.iloc[-1]
                change = end_value - start_value
                percent_change = (change / start_value) * 100 if start_value != 0 else float('inf')
                
                trend_analysis["overall"] = {
                    "direction": "increasing" if change > 0 else "decreasing" if change < 0 else "stable",
                    "change": change,
                    "percent_change": percent_change
                }
            
            # Calculate seasonality strength
            if len(result.seasonal.dropna()) > 0:
                seasonality_strength = result.seasonal.std() / (result.trend.std() + result.seasonal.std())
                trend_analysis["seasonality_strength"] = float(seasonality_strength)
            
            logger.info(f"Trend analysis completed for {value_column}")
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
            
            # Fallback to simple trend analysis
            values = resampled[value_column].values
            x = np.arange(len(values))
            
            # Linear regression
            slope, intercept = np.polyfit(x, values, 1)
            
            trend_analysis = {
                "overall": {
                    "direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
                    "slope": float(slope),
                    "intercept": float(intercept)
                },
                "values": resampled[value_column].to_dict()
            }
            
            logger.info(f"Simple trend analysis completed for {value_column}")
            return trend_analysis
    
    def detect_anomalies(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
                        columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Detect anomalies in the data.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            columns: List of columns to check for anomalies. If None, all numeric columns are used.
            
        Returns:
            A dictionary containing detected anomalies.
        """
        logger.info("Detecting anomalies in data")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        # Use all numeric columns if none specified
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        anomalies = {}
        
        # Z-score method for anomaly detection
        for col in columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                # Calculate z-scores
                mean = df[col].mean()
                std = df[col].std()
                
                if std > 0:  # Avoid division by zero
                    z_scores = (df[col] - mean) / std
                    
                    # Identify anomalies
                    anomaly_indices = np.where(abs(z_scores) > self.anomaly_threshold)[0]
                    
                    if len(anomaly_indices) > 0:
                        anomalies[col] = {
                            "indices": anomaly_indices.tolist(),
                            "values": df.iloc[anomaly_indices][col].tolist(),
                            "z_scores": z_scores.iloc[anomaly_indices].tolist(),
                            "threshold": self.anomaly_threshold,
                            "count": len(anomaly_indices),
                            "percentage": (len(anomaly_indices) / len(df)) * 100
                        }
        
        logger.info(f"Anomaly detection completed: {sum(a['count'] for a in anomalies.values())} anomalies found")
        return anomalies
    
    def generate_visualizations(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
                              output_dir: str) -> Dict[str, str]:
        """
        Generate visualizations for the data.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            output_dir: Directory to save the visualizations.
            
        Returns:
            A dictionary mapping visualization types to file paths.
        """
        logger.info("Generating visualizations")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        visualization_paths = {}
        
        # Generate histograms for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if not numeric_cols.empty:
            for col in numeric_cols:
                plt.figure(figsize=(10, 6))
                plt.hist(df[col].dropna(), bins=30, alpha=0.7)
                plt.title(f'Distribution of {col}')
                plt.xlabel(col)
                plt.ylabel('Frequency')
                plt.grid(True, alpha=0.3)
                
                file_path = os.path.join(output_dir, f'histogram_{col}.png')
                plt.savefig(file_path)
                plt.close()
                
                visualization_paths[f'histogram_{col}'] = file_path
        
        # Generate bar charts for categorical columns
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns
        if not categorical_cols.empty:
            for col in categorical_cols:
                if df[col].nunique() <= 20:  # Only for columns with reasonable number of categories
                    plt.figure(figsize=(12, 6))
                    df[col].value_counts().sort_values(ascending=False).head(10).plot(kind='bar')
                    plt.title(f'Top Categories in {col}')
                    plt.xlabel(col)
                    plt.ylabel('Count')
                    plt.grid(True, alpha=0.3)
                    plt.xticks(rotation=45)
                    
                    file_path = os.path.join(output_dir, f'barchart_{col}.png')
                    plt.savefig(file_path)
                    plt.close()
                    
                    visualization_paths[f'barchart_{col}'] = file_path
        
        # Generate correlation heatmap
        if len(numeric_cols) >= 2:
            plt.figure(figsize=(12, 10))
            corr_matrix = df[numeric_cols].corr()
            plt.imshow(corr_matrix, cmap='coolwarm')
            plt.colorbar()
            plt.xticks(range(len(numeric_cols)), numeric_cols, rotation=90)
            plt.yticks(range(len(numeric_cols)), numeric_cols)
            plt.title('Correlation Matrix')
            
            # Add correlation values
            for i in range(len(numeric_cols)):
                for j in range(len(numeric_cols)):
                    plt.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}', 
                             ha='center', va='center', 
                             color='white' if abs(corr_matrix.iloc[i, j]) > 0.5 else 'black')
            
            file_path = os.path.join(output_dir, 'correlation_heatmap.png')
            plt.savefig(file_path)
            plt.close()
            
            visualization_paths['correlation_heatmap'] = file_path
        
        # Generate time series plot if time column exists
        time_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if time_cols:
            time_col = time_cols[0]
            
            # Convert to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
                try:
                    df[time_col] = pd.to_datetime(df[time_col])
                    
                    # Select a numeric column to plot
                    if not numeric_cols.empty:
                        value_col = numeric_cols[0]
                        
                        plt.figure(figsize=(14, 7))
                        plt.plot(df[time_col], df[value_col], marker='o', linestyle='-', alpha=0.7)
                        plt.title(f'{value_col} over Time')
                        plt.xlabel(time_col)
                        plt.ylabel(value_col)
                        plt.grid(True, alpha=0.3)
                        plt.xticks(rotation=45)
                        
                        file_path = os.path.join(output_dir, f'timeseries_{value_col}.png')
                        plt.savefig(file_path)
                        plt.close()
                        
                        visualization_paths[f'timeseries_{value_col}'] = file_path
                except Exception as e:
                    logger.warning(f"Could not convert {time_col} to datetime: {e}")
        
        logger.info(f"Visualizations generated: {len(visualization_paths)} files saved to {output_dir}")
        return visualization_paths
    
    def analyze(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
               time_column: Optional[str] = None,
               value_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform a comprehensive descriptive analysis of the data.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            time_column: Name of the column containing time/date information.
            value_columns: List of columns to analyze. If None, all numeric columns are used.
            
        Returns:
            A dictionary containing the analysis results.
        """
        logger.info("Performing comprehensive descriptive analysis")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        # Identify time column if not provided
        if time_column is None:
            time_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if time_cols:
                time_column = time_cols[0]
                logger.info(f"Automatically selected time column: {time_column}")
        
        # Use all numeric columns if value_columns not provided
        if value_columns is None:
            value_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Perform analysis
        analysis_results = {
            "summary": self.summarize_data(df),
            "patterns": self.identify_patterns(df, time_column)
        }
        
        # Trend analysis for each value column if time column exists
        if time_column and time_column in df.columns:
            analysis_results["trends"] = {}
            for col in value_columns:
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    analysis_results["trends"][col] = self.analyze_trends(df, time_column, col)
        
        # Anomaly detection
        analysis_results["anomalies"] = self.detect_anomalies(df, value_columns)
        
        logger.info("Comprehensive descriptive analysis completed")
        return analysis_results
    
    def _ensure_dataframe(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]) -> pd.DataFrame:
        """
        Convert input data to a pandas DataFrame if it's not already.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            
        Returns:
            A pandas DataFrame.
        """
        if isinstance(data, pd.DataFrame):
            return data
        elif isinstance(data, dict):
            return pd.DataFrame([data])
        elif isinstance(data, list):
            return pd.DataFrame(data)
        else:
            raise ValueError("Data must be a pandas DataFrame, dictionary, or list of dictionaries")
    
    def _analyze_time_patterns(self, df: pd.DataFrame, time_column: str) -> Dict[str, Any]:
        """
        Analyze time-based patterns in the data.
        
        Args:
            df: Input DataFrame with datetime components added.
            time_column: Name of the column containing time/date information.
            
        Returns:
            A dictionary containing time-based patterns.
        """
        time_patterns = {}
        
        # Check for day of week patterns
        if 'weekday' in df.columns:
            weekday_counts = df['weekday'].value_counts().sort_index()
            weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_dict = {i: weekday_names[i] for i in range(7)}
            
            # Calculate weekday vs weekend ratio
            weekday_sum = weekday_counts.iloc[:5].sum()
            weekend_sum = weekday_counts.iloc[5:].sum()
            weekday_weekend_ratio = weekday_sum / weekend_sum if weekend_sum > 0 else float('inf')
            
            time_patterns["day_of_week"] = {
                "counts": {weekday_dict[i]: int(count) for i, count in weekday_counts.items()},
                "weekday_weekend_ratio": weekday_weekend_ratio,
                "most_common_day": weekday_dict[weekday_counts.idxmax()]
            }
        
        # Check for month patterns
        if 'month' in df.columns:
            month_counts = df['month'].value_counts().sort_index()
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            month_dict = {i: month_names[i-1] for i in range(1, 13)}
            
            time_patterns["month"] = {
                "counts": {month_dict[i]: int(count) for i, count in month_counts.items()},
                "most_common_month": month_dict[month_counts.idxmax()]
            }
            
            # Check for quarterly patterns
            df['quarter'] = ((df['month'] - 1) // 3) + 1
            quarter_counts = df['quarter'].value_counts().sort_index()
            
            time_patterns["quarter"] = {
                "counts": {f"Q{i}": int(count) for i, count in quarter_counts.items()},
                "most_common_quarter": f"Q{quarter_counts.idxmax()}"
            }
        
        # Check for hour of day patterns if available
        if 'hour' in df.columns and df['hour'].notna().any():
            hour_counts = df['hour'].value_counts().sort_index()
            
            # Define time periods
            morning = hour_counts.loc[6:11].sum() if 6 in hour_counts.index else 0
            afternoon = hour_counts.loc[12:17].sum() if 12 in hour_counts.index else 0
            evening = hour_counts.loc[18:21].sum() if 18 in hour_counts.index else 0
            night = hour_counts.loc[22:23].sum() if 22 in hour_counts.index else 0
            night += hour_counts.loc[0:5].sum() if 0 in hour_counts.index else 0
            
            time_patterns["hour_of_day"] = {
                "counts": {str(i): int(count) for i, count in hour_counts.items()},
                "most_common_hour": str(hour_counts.idxmax()),
                "time_periods": {
                    "morning (6-11)": int(morning),
                    "afternoon (12-17)": int(afternoon),
                    "evening (18-21)": int(evening),
                    "night (22-5)": int(night)
                }
            }
        
        return time_patterns
    
    def _get_period(self) -> int:
        """
        Determine the period for seasonal decomposition based on aggregation level.
        
        Returns:
            An integer representing the period.
        """
        if self.aggregation_level == "day":
            return 7  # Weekly seasonality
        elif self.aggregation_level == "week":
            return 4  # Monthly seasonality
        elif self.aggregation_level == "month":
            return 12  # Yearly seasonality
        else:
            return 7  # Default to weekly
