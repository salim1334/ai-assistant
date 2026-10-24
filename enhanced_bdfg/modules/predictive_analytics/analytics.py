"""
Predictive Analytics Module

This module contains the PredictiveAnalytics class, which provides predictive analytics
capabilities for forecasting future trends and outcomes based on historical data.
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional, Tuple, Union
import json
import os
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PredictiveAnalytics:
    """
    The PredictiveAnalytics class provides methods for forecasting future trends
    and outcomes based on historical data.
    
    It includes functionality for time series forecasting, regression modeling,
    classification, and scenario analysis.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the PredictiveAnalytics module.
        
        Args:
            config: Configuration parameters for the module.
        """
        self.config = config or {}
        logger.info("Initializing PredictiveAnalytics module")
        
        # Set default parameters
        self.forecast_horizon = self.config.get("forecast_horizon", 30)  # Default 30 periods
        self.confidence_level = self.config.get("confidence_level", 0.95)
        self.seasonality_mode = self.config.get("seasonality_mode", "additive")
        self.cross_validation_folds = self.config.get("cross_validation_folds", 5)
        
        logger.info("PredictiveAnalytics module initialized successfully")
    
    def forecast_time_series(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
                           time_column: str, target_column: str,
                           horizon: Optional[int] = None) -> Dict[str, Any]:
        """
        Forecast future values of a time series.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            time_column: Name of the column containing time/date information.
            target_column: Name of the column containing the values to forecast.
            horizon: Number of periods to forecast. If None, uses the default forecast_horizon.
            
        Returns:
            A dictionary containing forecast results.
        """
        logger.info(f"Forecasting time series for {target_column} over {horizon or self.forecast_horizon} periods")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        # Check if columns exist
        if time_column not in df.columns:
            logger.error(f"Time column {time_column} not found in data")
            return {"error": f"Time column {time_column} not found in data"}
        
        if target_column not in df.columns:
            logger.error(f"Target column {target_column} not found in data")
            return {"error": f"Target column {target_column} not found in data"}
        
        # Ensure time column is datetime
        if not pd.api.types.is_datetime64_any_dtype(df[time_column]):
            try:
                df[time_column] = pd.to_datetime(df[time_column])
            except Exception as e:
                logger.error(f"Could not convert {time_column} to datetime: {e}")
                return {"error": f"Could not convert {time_column} to datetime"}
        
        # Sort by time
        df = df.sort_values(by=time_column)
        
        # Set horizon if not provided
        if horizon is None:
            horizon = self.forecast_horizon
        
        # Determine frequency
        freq = self._infer_frequency(df[time_column])
        
        # Try different forecasting methods
        forecast_results = {}
        
        # Try Prophet if available
        prophet_forecast = self._forecast_with_prophet(df, time_column, target_column, horizon, freq)
        if prophet_forecast and "error" not in prophet_forecast:
            forecast_results["prophet"] = prophet_forecast
        
        # Try ARIMA
        arima_forecast = self._forecast_with_arima(df, time_column, target_column, horizon, freq)
        if arima_forecast and "error" not in arima_forecast:
            forecast_results["arima"] = arima_forecast
        
        # Try exponential smoothing
        ets_forecast = self._forecast_with_ets(df, time_column, target_column, horizon, freq)
        if ets_forecast and "error" not in ets_forecast:
            forecast_results["exponential_smoothing"] = ets_forecast
        
        # If no forecasts were successful, try simple methods
        if not forecast_results:
            # Try simple moving average
            ma_forecast = self._forecast_with_moving_average(df, time_column, target_column, horizon, freq)
            if ma_forecast:
                forecast_results["moving_average"] = ma_forecast
            
            # Try naive forecast
            naive_forecast = self._forecast_with_naive(df, time_column, target_column, horizon, freq)
            if naive_forecast:
                forecast_results["naive"] = naive_forecast
        
        # If still no forecasts, return error
        if not forecast_results:
            logger.error("All forecasting methods failed")
            return {"error": "All forecasting methods failed"}
        
        # Select best forecast based on validation metrics
        best_method = self._select_best_forecast(forecast_results)
        
        # Prepare final result
        final_result = {
            "forecast": forecast_results[best_method]["forecast"],
            "confidence_intervals": forecast_results[best_method].get("confidence_intervals", {}),
            "method": best_method,
            "metrics": forecast_results[best_method].get("metrics", {}),
            "all_methods": list(forecast_results.keys())
        }
        
        # Add forecast dates
        if "forecast_dates" in forecast_results[best_method]:
            final_result["forecast_dates"] = forecast_results[best_method]["forecast_dates"]
        
        logger.info(f"Time series forecast completed using {best_method} method")
        return final_result
    
    def _forecast_with_prophet(self, df: pd.DataFrame, time_column: str, target_column: str,
                             horizon: int, freq: str) -> Optional[Dict[str, Any]]:
        """
        Forecast using Facebook Prophet.
        
        Args:
            df: Input DataFrame.
            time_column: Name of the time column.
            target_column: Name of the target column.
            horizon: Number of periods to forecast.
            freq: Frequency of the time series.
            
        Returns:
            A dictionary containing forecast results, or None if Prophet is not available.
        """
        try:
            from prophet import Prophet
            
            # Prepare data for Prophet
            prophet_df = df[[time_column, target_column]].copy()
            prophet_df.columns = ['ds', 'y']
            
            # Handle missing values
            prophet_df = prophet_df.dropna()
            
            # Create and fit model
            model = Prophet(
                seasonality_mode=self.seasonality_mode,
                interval_width=self.confidence_level
            )
            
            # Add weekly seasonality if frequency is daily or higher
            if freq in ['D', 'H', 'min']:
                model.add_seasonality(name='weekly', period=7, fourier_order=3)
            
            # Add monthly seasonality if frequency is weekly or higher
            if freq in ['D', 'W', 'H', 'min']:
                model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
            
            # Add yearly seasonality if frequency is monthly or higher
            if freq in ['D', 'W', 'M', 'H', 'min']:
                model.add_seasonality(name='yearly', period=365.25, fourier_order=10)
            
            model.fit(prophet_df)
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=horizon, freq=freq)
            
            # Generate forecast
            forecast = model.predict(future)
            
            # Extract results
            forecast_dates = forecast['ds'].tail(horizon).dt.strftime('%Y-%m-%d').tolist()
            forecast_values = forecast['yhat'].tail(horizon).tolist()
            lower_bound = forecast['yhat_lower'].tail(horizon).tolist()
            upper_bound = forecast['yhat_upper'].tail(horizon).tolist()
            
            # Calculate metrics on training data
            train_predictions = forecast['yhat'].iloc[:-horizon].values
            train_actual = prophet_df['y'].values
            
            mse = np.mean((train_predictions - train_actual) ** 2)
            rmse = np.sqrt(mse)
            mae = np.mean(np.abs(train_predictions - train_actual))
            mape = np.mean(np.abs((train_actual - train_predictions) / train_actual)) * 100
            
            # Prepare result
            result = {
                "forecast": forecast_values,
                "forecast_dates": forecast_dates,
                "confidence_intervals": {
                    "lower": lower_bound,
                    "upper": upper_bound
                },
                "metrics": {
                    "mse": mse,
                    "rmse": rmse,
                    "mae": mae,
                    "mape": mape
                },
                "components": {
                    "trend": forecast['trend'].tail(horizon).tolist(),
                    "weekly": forecast['weekly'].tail(horizon).tolist() if 'weekly' in forecast.columns else None,
                    "yearly": forecast['yearly'].tail(horizon).tolist() if 'yearly' in forecast.columns else None
                }
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"Prophet forecasting failed: {e}")
            return None
    
    def _forecast_with_arima(self, df: pd.DataFrame, time_column: str, target_column: str,
                           horizon: int, freq: str) -> Optional[Dict[str, Any]]:
        """
        Forecast using ARIMA/SARIMA models.
        
        Args:
            df: Input DataFrame.
            time_column: Name of the time column.
            target_column: Name of the target column.
            horizon: Number of periods to forecast.
            freq: Frequency of the time series.
            
        Returns:
            A dictionary containing forecast results, or None if forecasting fails.
        """
        try:
            from statsmodels.tsa.statespace.sarimax import SARIMAX
            
            # Prepare data
            series = df.set_index(time_column)[target_column]
            
            # Handle missing values
            series = series.dropna()
            
            # Determine if seasonality should be included
            seasonal = False
            seasonal_order = (0, 0, 0, 0)
            
            if freq == 'D':
                seasonal = True
                seasonal_order = (1, 0, 1, 7)  # Weekly seasonality
            elif freq == 'W':
                seasonal = True
                seasonal_order = (1, 0, 1, 52)  # Yearly seasonality
            elif freq == 'M':
                seasonal = True
                seasonal_order = (1, 0, 1, 12)  # Yearly seasonality
            elif freq == 'Q':
                seasonal = True
                seasonal_order = (1, 0, 1, 4)  # Yearly seasonality
            
            # Create and fit model
            if seasonal:
                model = SARIMAX(
                    series,
                    order=(1, 1, 1),
                    seasonal_order=seasonal_order,
                    enforce_stationarity=False,
                    enforce_invertibility=False
                )
            else:
                model = SARIMAX(
                    series,
                    order=(1, 1, 1),
                    enforce_stationarity=False,
                    enforce_invertibility=False
                )
            
            model_fit = model.fit(disp=False)
            
            # Generate forecast
            forecast = model_fit.get_forecast(steps=horizon)
            forecast_values = forecast.predicted_mean.tolist()
            
            # Get confidence intervals
            conf_int = forecast.conf_int(alpha=1-self.confidence_level)
            lower_bound = conf_int.iloc[:, 0].tolist()
            upper_bound = conf_int.iloc[:, 1].tolist()
            
            # Generate forecast dates
            last_date = series.index[-1]
            forecast_dates = []
            
            for i in range(1, horizon + 1):
                if freq == 'D':
                    next_date = last_date + timedelta(days=i)
                elif freq == 'W':
                    next_date = last_date + timedelta(weeks=i)
                elif freq == 'M':
                    next_date = last_date + pd.DateOffset(months=i)
                elif freq == 'Q':
                    next_date = last_date + pd.DateOffset(months=3*i)
                elif freq == 'Y':
                    next_date = last_date + pd.DateOffset(years=i)
                else:
                    next_date = last_date + pd.DateOffset(days=i)
                
                forecast_dates.append(next_date.strftime('%Y-%m-%d'))
            
            # Calculate metrics on training data
            train_predictions = model_fit.get_prediction().predicted_mean
            train_actual = series.values
            
            mse = np.mean((train_predictions - train_actual) ** 2)
            rmse = np.sqrt(mse)
            mae = np.mean(np.abs(train_predictions - train_actual))
            mape = np.mean(np.abs((train_actual - train_predictions) / train_actual)) * 100
            
            # Prepare result
            result = {
                "forecast": forecast_values,
                "forecast_dates": forecast_dates,
                "confidence_intervals": {
                    "lower": lower_bound,
                    "upper": upper_bound
                },
                "metrics": {
                    "mse": mse,
                    "rmse": rmse,
                    "mae": mae,
                    "mape": mape,
                    "aic": model_fit.aic,
                    "bic": model_fit.bic
                }
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"ARIMA forecasting failed: {e}")
            return None
    
    def _forecast_with_ets(self, df: pd.DataFrame, time_column: str, target_column: str,
                         horizon: int, freq: str) -> Optional[Dict[str, Any]]:
        """
        Forecast using Exponential Smoothing.
        
        Args:
            df: Input DataFrame.
            time_column: Name of the time column.
            target_column: Name of the target column.
            horizon: Number of periods to forecast.
            freq: Frequency of the time series.
            
        Returns:
            A dictionary containing forecast results, or None if forecasting fails.
        """
        try:
            from statsmodels.tsa.holtwinters import ExponentialSmoothing
            
            # Prepare data
            series = df.set_index(time_column)[target_column]
            
            # Handle missing values
            series = series.dropna()
            
            # Determine seasonality
            seasonal = False
            seasonal_periods = 1
            
            if freq == 'D':
                seasonal = True
                seasonal_periods = 7  # Weekly seasonality
            elif freq == 'W':
                seasonal = True
                seasonal_periods = 52  # Yearly seasonality
            elif freq == 'M':
                seasonal = True
                seasonal_periods = 12  # Yearly seasonality
            elif freq == 'Q':
                seasonal = True
                seasonal_periods = 4  # Yearly seasonality
            
            # Create and fit model
            if seasonal and len(series) >= 2 * seasonal_periods:
                model = ExponentialSmoothing(
                    series,
                    trend='add',
                    seasonal=self.seasonality_mode,
                    seasonal_periods=seasonal_periods
                )
            else:
                model = ExponentialSmoothing(
                    series,
                    trend='add',
                    seasonal=None
                )
            
            model_fit = model.fit()
            
            # Generate forecast
            forecast = model_fit.forecast(horizon)
            forecast_values = forecast.tolist()
            
            # Generate forecast dates
            last_date = series.index[-1]
            forecast_dates = []
            
            for i in range(1, horizon + 1):
                if freq == 'D':
                    next_date = last_date + timedelta(days=i)
                elif freq == 'W':
                    next_date = last_date + timedelta(weeks=i)
                elif freq == 'M':
                    next_date = last_date + pd.DateOffset(months=i)
                elif freq == 'Q':
                    next_date = last_date + pd.DateOffset(months=3*i)
                elif freq == 'Y':
                    next_date = last_date + pd.DateOffset(years=i)
                else:
                    next_date = last_date + pd.DateOffset(days=i)
                
                forecast_dates.append(next_date.strftime('%Y-%m-%d'))
            
            # Calculate metrics on training data
            train_predictions = model_fit.fittedvalues
            train_actual = series.values
            
            mse = np.mean((train_predictions - train_actual) ** 2)
            rmse = np.sqrt(mse)
            mae = np.mean(np.abs(train_predictions - train_actual))
            mape = np.mean(np.abs((train_actual - train_predictions) / train_actual)) * 100
            
            # Prepare result
            result = {
                "forecast": forecast_values,
                "forecast_dates": forecast_dates,
                "metrics": {
                    "mse": mse,
                    "rmse": rmse,
                    "mae": mae,
                    "mape": mape
                }
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"Exponential smoothing forecasting failed: {e}")
            return None
    
    def _forecast_with_moving_average(self, df: pd.DataFrame, time_column: str, target_column: str,
                                    horizon: int, freq: str) -> Optional[Dict[str, Any]]:
        """
        Forecast using simple moving average.
        
        Args:
            df: Input DataFrame.
            time_column: Name of the time column.
            target_column: Name of the target column.
            horizon: Number of periods to forecast.
            freq: Frequency of the time series.
            
        Returns:
            A dictionary containing forecast results, or None if forecasting fails.
        """
        try:
            # Prepare data
            series = df.set_index(time_column)[target_column]
            
            # Handle missing values
            series = series.dropna()
            
            # Calculate moving average
            window = min(len(series) // 3, 12)  # Use at most 1/3 of the data or 12 periods
            window = max(window, 1)  # Ensure window is at least 1
            
            ma = series.rolling(window=window).mean()
            
            # Generate forecast
            last_ma = ma.iloc[-1]
            forecast_values = [last_ma] * horizon
            
            # Generate forecast dates
            last_date = series.index[-1]
            forecast_dates = []
            
            for i in range(1, horizon + 1):
                if freq == 'D':
                    next_date = last_date + timedelta(days=i)
                elif freq == 'W':
                    next_date = last_date + timedelta(weeks=i)
                elif freq == 'M':
                    next_date = last_date + pd.DateOffset(months=i)
                elif freq == 'Q':
                    next_date = last_date + pd.DateOffset(months=3*i)
                elif freq == 'Y':
                    next_date = last_date + pd.DateOffset(years=i)
                else:
                    next_date = last_date + pd.DateOffset(days=i)
                
                forecast_dates.append(next_date.strftime('%Y-%m-%d'))
            
            # Calculate metrics on training data
            train_predictions = ma.dropna().values
            train_actual = series.iloc[window-1:].values[:len(train_predictions)]
            
            mse = np.mean((train_predictions - train_actual) ** 2)
            rmse = np.sqrt(mse)
            mae = np.mean(np.abs(train_predictions - train_actual))
            mape = np.mean(np.abs((train_actual - train_predictions) / train_actual)) * 100
            
            # Prepare result
            result = {
                "forecast": forecast_values,
                "forecast_dates": forecast_dates,
                "metrics": {
                    "mse": mse,
                    "rmse": rmse,
                    "mae": mae,
                    "mape": mape
                }
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"Moving average forecasting failed: {e}")
            return None
    
    def _forecast_with_naive(self, df: pd.DataFrame, time_column: str, target_column: str,
                           horizon: int, freq: str) -> Optional[Dict[str, Any]]:
        """
        Forecast using naive method (last value).
        
        Args:
            df: Input DataFrame.
            time_column: Name of the time column.
            target_column: Name of the target column.
            horizon: Number of periods to forecast.
            freq: Frequency of the time series.
            
        Returns:
            A dictionary containing forecast results, or None if forecasting fails.
        """
        try:
            # Prepare data
            series = df.set_index(time_column)[target_column]
            
            # Handle missing values
            series = series.dropna()
            
            # Generate forecast
            last_value = series.iloc[-1]
            forecast_values = [last_value] * horizon
            
            # Generate forecast dates
            last_date = series.index[-1]
            forecast_dates = []
            
            for i in range(1, horizon + 1):
                if freq == 'D':
                    next_date = last_date + timedelta(days=i)
                elif freq == 'W':
                    next_date = last_date + timedelta(weeks=i)
                elif freq == 'M':
                    next_date = last_date + pd.DateOffset(months=i)
                elif freq == 'Q':
                    next_date = last_date + pd.DateOffset(months=3*i)
                elif freq == 'Y':
                    next_date = last_date + pd.DateOffset(years=i)
                else:
                    next_date = last_date + pd.DateOffset(days=i)
                
                forecast_dates.append(next_date.strftime('%Y-%m-%d'))
            
            # Calculate metrics on training data
            train_predictions = series.shift(1).dropna().values
            train_actual = series.iloc[1:].values
            
            mse = np.mean((train_predictions - train_actual) ** 2)
            rmse = np.sqrt(mse)
            mae = np.mean(np.abs(train_predictions - train_actual))
            mape = np.mean(np.abs((train_actual - train_predictions) / train_actual)) * 100
            
            # Prepare result
            result = {
                "forecast": forecast_values,
                "forecast_dates": forecast_dates,
                "metrics": {
                    "mse": mse,
                    "rmse": rmse,
                    "mae": mae,
                    "mape": mape
                }
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"Naive forecasting failed: {e}")
            return None
    
    def _select_best_forecast(self, forecast_results: Dict[str, Dict[str, Any]]) -> str:
        """
        Select the best forecasting method based on metrics.
        
        Args:
            forecast_results: Dictionary of forecast results by method.
            
        Returns:
            Name of the best forecasting method.
        """
        # Define priority order of methods
        method_priority = ["prophet", "arima", "exponential_smoothing", "moving_average", "naive"]
        
        # Filter to methods that are available
        available_methods = [m for m in method_priority if m in forecast_results]
        
        if not available_methods:
            return list(forecast_results.keys())[0]  # Return any method if none in priority list
        
        # Check if metrics are available
        metrics_available = all("metrics" in forecast_results[m] for m in available_methods)
        
        if not metrics_available:
            return available_methods[0]  # Return highest priority method if metrics not available
        
        # Compare methods based on RMSE
        best_method = available_methods[0]
        best_rmse = forecast_results[best_method]["metrics"].get("rmse", float('inf'))
        
        for method in available_methods[1:]:
            rmse = forecast_results[method]["metrics"].get("rmse", float('inf'))
            if rmse < best_rmse:
                best_method = method
                best_rmse = rmse
        
        return best_method
    
    def _infer_frequency(self, time_series: pd.Series) -> str:
        """
        Infer the frequency of a time series.
        
        Args:
            time_series: Series of datetime values.
            
        Returns:
            Frequency string (D, W, M, Q, Y).
        """
        # Calculate differences between consecutive timestamps
        if len(time_series) < 2:
            return 'D'  # Default to daily if not enough data
        
        diffs = pd.Series(time_series.sort_values().diff().dropna())
        
        # Calculate the most common difference
        most_common_diff = diffs.value_counts().index[0]
        
        # Determine frequency based on most common difference
        if most_common_diff <= pd.Timedelta(hours=36):
            return 'D'  # Daily
        elif most_common_diff <= pd.Timedelta(days=10):
            return 'W'  # Weekly
        elif most_common_diff <= pd.Timedelta(days=45):
            return 'M'  # Monthly
        elif most_common_diff <= pd.Timedelta(days=135):
            return 'Q'  # Quarterly
        else:
            return 'Y'  # Yearly
    
    def build_regression_model(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
                             target_column: str, feature_columns: List[str] = None) -> Dict[str, Any]:
        """
        Build a regression model to predict a target variable.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            target_column: Name of the target column to predict.
            feature_columns: List of feature columns to use. If None, uses all numeric columns.
            
        Returns:
            A dictionary containing model results.
        """
        logger.info(f"Building regression model for {target_column}")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        # Check if target column exists
        if target_column not in df.columns:
            logger.error(f"Target column {target_column} not found in data")
            return {"error": f"Target column {target_column} not found in data"}
        
        # Check if target column is numeric
        if not pd.api.types.is_numeric_dtype(df[target_column]):
            logger.error(f"Target column {target_column} must be numeric")
            return {"error": f"Target column {target_column} must be numeric"}
        
        # Select feature columns
        if feature_columns is None:
            # Use all numeric columns except target
            feature_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            feature_columns = [col for col in feature_columns if col != target_column]
        else:
            # Verify feature columns exist
            missing_columns = [col for col in feature_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Feature columns {missing_columns} not found in data")
                return {"error": f"Feature columns {missing_columns} not found in data"}
        
        if not feature_columns:
            logger.error("No feature columns available")
            return {"error": "No feature columns available"}
        
        # Handle missing values
        df = df.dropna(subset=[target_column] + feature_columns)
        
        if len(df) < 10:
            logger.error("Insufficient data after removing missing values")
            return {"error": "Insufficient data after removing missing values"}
        
        # Prepare data
        X = df[feature_columns]
        y = df[target_column]
        
        # Try different regression models
        model_results = {}
        
        # Linear regression
        linear_model = self._build_linear_regression(X, y)
        if linear_model:
            model_results["linear"] = linear_model
        
        # Random forest
        rf_model = self._build_random_forest_regression(X, y)
        if rf_model:
            model_results["random_forest"] = rf_model
        
        # Gradient boosting
        gb_model = self._build_gradient_boosting_regression(X, y)
        if gb_model:
            model_results["gradient_boosting"] = gb_model
        
        # If no models were successful, return error
        if not model_results:
            logger.error("All regression models failed")
            return {"error": "All regression models failed"}
        
        # Select best model based on metrics
        best_model = self._select_best_regression_model(model_results)
        
        # Prepare final result
        final_result = {
            "model_type": best_model,
            "metrics": model_results[best_model]["metrics"],
            "feature_importance": model_results[best_model]["feature_importance"],
            "all_models": list(model_results.keys())
        }
        
        # Add coefficients for linear model
        if best_model == "linear" and "coefficients" in model_results[best_model]:
            final_result["coefficients"] = model_results[best_model]["coefficients"]
        
        logger.info(f"Regression model built successfully using {best_model}")
        return final_result
    
    def _build_linear_regression(self, X: pd.DataFrame, y: pd.Series) -> Optional[Dict[str, Any]]:
        """
        Build a linear regression model.
        
        Args:
            X: Feature DataFrame.
            y: Target Series.
            
        Returns:
            A dictionary containing model results, or None if model building fails.
        """
        try:
            from sklearn.linear_model import LinearRegression
            from sklearn.model_selection import cross_val_score, train_test_split
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Create and fit model
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Calculate cross-validation score
            cv_scores = cross_val_score(model, X, y, cv=self.cross_validation_folds, scoring='neg_mean_squared_error')
            cv_rmse = np.sqrt(-cv_scores.mean())
            
            # Get coefficients
            coefficients = {}
            for i, col in enumerate(X.columns):
                coefficients[col] = model.coef_[i]
            
            # Calculate feature importance (absolute coefficient values)
            feature_importance = {}
            for col, coef in coefficients.items():
                feature_importance[col] = abs(coef)
            
            # Normalize feature importance
            total_importance = sum(feature_importance.values())
            if total_importance > 0:
                for col in feature_importance:
                    feature_importance[col] /= total_importance
            
            # Prepare result
            result = {
                "metrics": {
                    "mse": mse,
                    "rmse": rmse,
                    "mae": mae,
                    "r2": r2,
                    "cv_rmse": cv_rmse
                },
                "coefficients": coefficients,
                "feature_importance": feature_importance,
                "intercept": model.intercept_
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"Linear regression failed: {e}")
            return None
    
    def _build_random_forest_regression(self, X: pd.DataFrame, y: pd.Series) -> Optional[Dict[str, Any]]:
        """
        Build a random forest regression model.
        
        Args:
            X: Feature DataFrame.
            y: Target Series.
            
        Returns:
            A dictionary containing model results, or None if model building fails.
        """
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import cross_val_score, train_test_split
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Create and fit model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Calculate cross-validation score
            cv_scores = cross_val_score(model, X, y, cv=self.cross_validation_folds, scoring='neg_mean_squared_error')
            cv_rmse = np.sqrt(-cv_scores.mean())
            
            # Get feature importance
            feature_importance = {}
            for i, col in enumerate(X.columns):
                feature_importance[col] = model.feature_importances_[i]
            
            # Prepare result
            result = {
                "metrics": {
                    "mse": mse,
                    "rmse": rmse,
                    "mae": mae,
                    "r2": r2,
                    "cv_rmse": cv_rmse
                },
                "feature_importance": feature_importance
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"Random forest regression failed: {e}")
            return None
    
    def _build_gradient_boosting_regression(self, X: pd.DataFrame, y: pd.Series) -> Optional[Dict[str, Any]]:
        """
        Build a gradient boosting regression model.
        
        Args:
            X: Feature DataFrame.
            y: Target Series.
            
        Returns:
            A dictionary containing model results, or None if model building fails.
        """
        try:
            from sklearn.ensemble import GradientBoostingRegressor
            from sklearn.model_selection import cross_val_score, train_test_split
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Create and fit model
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Calculate cross-validation score
            cv_scores = cross_val_score(model, X, y, cv=self.cross_validation_folds, scoring='neg_mean_squared_error')
            cv_rmse = np.sqrt(-cv_scores.mean())
            
            # Get feature importance
            feature_importance = {}
            for i, col in enumerate(X.columns):
                feature_importance[col] = model.feature_importances_[i]
            
            # Prepare result
            result = {
                "metrics": {
                    "mse": mse,
                    "rmse": rmse,
                    "mae": mae,
                    "r2": r2,
                    "cv_rmse": cv_rmse
                },
                "feature_importance": feature_importance
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"Gradient boosting regression failed: {e}")
            return None
    
    def _select_best_regression_model(self, model_results: Dict[str, Dict[str, Any]]) -> str:
        """
        Select the best regression model based on metrics.
        
        Args:
            model_results: Dictionary of model results by type.
            
        Returns:
            Name of the best model type.
        """
        # Define priority order of metrics
        metrics_priority = ["r2", "cv_rmse", "rmse", "mae"]
        
        # Find first available metric
        for metric in metrics_priority:
            if all(metric in model_results[model_type]["metrics"] for model_type in model_results):
                # For R2, higher is better
                if metric == "r2":
                    best_model = max(model_results.items(), 
                                    key=lambda x: x[1]["metrics"][metric])[0]
                # For error metrics, lower is better
                else:
                    best_model = min(model_results.items(), 
                                    key=lambda x: x[1]["metrics"][metric])[0]
                
                return best_model
        
        # If no common metrics, return first model
        return list(model_results.keys())[0]
    
    def build_classification_model(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
                                 target_column: str, feature_columns: List[str] = None) -> Dict[str, Any]:
        """
        Build a classification model to predict a categorical target.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            target_column: Name of the target column to predict.
            feature_columns: List of feature columns to use. If None, uses all numeric columns.
            
        Returns:
            A dictionary containing model results.
        """
        logger.info(f"Building classification model for {target_column}")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        # Check if target column exists
        if target_column not in df.columns:
            logger.error(f"Target column {target_column} not found in data")
            return {"error": f"Target column {target_column} not found in data"}
        
        # Select feature columns
        if feature_columns is None:
            # Use all numeric columns except target
            feature_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            feature_columns = [col for col in feature_columns if col != target_column]
        else:
            # Verify feature columns exist
            missing_columns = [col for col in feature_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Feature columns {missing_columns} not found in data")
                return {"error": f"Feature columns {missing_columns} not found in data"}
        
        if not feature_columns:
            logger.error("No feature columns available")
            return {"error": "No feature columns available"}
        
        # Handle missing values
        df = df.dropna(subset=[target_column] + feature_columns)
        
        if len(df) < 10:
            logger.error("Insufficient data after removing missing values")
            return {"error": "Insufficient data after removing missing values"}
        
        # Prepare data
        X = df[feature_columns]
        y = df[target_column]
        
        # Try different classification models
        model_results = {}
        
        # Logistic regression
        logistic_model = self._build_logistic_regression(X, y)
        if logistic_model:
            model_results["logistic"] = logistic_model
        
        # Random forest
        rf_model = self._build_random_forest_classification(X, y)
        if rf_model:
            model_results["random_forest"] = rf_model
        
        # Gradient boosting
        gb_model = self._build_gradient_boosting_classification(X, y)
        if gb_model:
            model_results["gradient_boosting"] = gb_model
        
        # If no models were successful, return error
        if not model_results:
            logger.error("All classification models failed")
            return {"error": "All classification models failed"}
        
        # Select best model based on metrics
        best_model = self._select_best_classification_model(model_results)
        
        # Prepare final result
        final_result = {
            "model_type": best_model,
            "metrics": model_results[best_model]["metrics"],
            "feature_importance": model_results[best_model]["feature_importance"],
            "all_models": list(model_results.keys()),
            "classes": model_results[best_model].get("classes", [])
        }
        
        # Add coefficients for logistic model
        if best_model == "logistic" and "coefficients" in model_results[best_model]:
            final_result["coefficients"] = model_results[best_model]["coefficients"]
        
        logger.info(f"Classification model built successfully using {best_model}")
        return final_result
    
    def _build_logistic_regression(self, X: pd.DataFrame, y: pd.Series) -> Optional[Dict[str, Any]]:
        """
        Build a logistic regression model.
        
        Args:
            X: Feature DataFrame.
            y: Target Series.
            
        Returns:
            A dictionary containing model results, or None if model building fails.
        """
        try:
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import cross_val_score, train_test_split
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
            from sklearn.preprocessing import LabelEncoder
            
            # Encode target if it's not numeric
            if not pd.api.types.is_numeric_dtype(y):
                label_encoder = LabelEncoder()
                y = label_encoder.fit_transform(y)
                classes = label_encoder.classes_.tolist()
            else:
                classes = sorted(y.unique().tolist())
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Create and fit model
            model = LogisticRegression(max_iter=1000, random_state=42)
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            
            # For binary classification
            if len(classes) == 2:
                precision = precision_score(y_test, y_pred)
                recall = recall_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred)
                
                try:
                    y_prob = model.predict_proba(X_test)[:, 1]
                    auc = roc_auc_score(y_test, y_prob)
                except:
                    auc = None
            else:
                # For multiclass
                precision = precision_score(y_test, y_pred, average='weighted')
                recall = recall_score(y_test, y_pred, average='weighted')
                f1 = f1_score(y_test, y_pred, average='weighted')
                auc = None
            
            # Calculate cross-validation score
            cv_scores = cross_val_score(model, X, y, cv=self.cross_validation_folds, scoring='accuracy')
            cv_accuracy = cv_scores.mean()
            
            # Get coefficients
            coefficients = {}
            if len(classes) == 2:
                # Binary classification
                for i, col in enumerate(X.columns):
                    coefficients[col] = model.coef_[0][i]
            else:
                # Multiclass classification
                for i, col in enumerate(X.columns):
                    coefficients[col] = {}
                    for j, cls in enumerate(classes):
                        coefficients[col][cls] = model.coef_[j][i]
            
            # Calculate feature importance (absolute coefficient values)
            feature_importance = {}
            if len(classes) == 2:
                # Binary classification
                for col, coef in coefficients.items():
                    feature_importance[col] = abs(coef)
            else:
                # Multiclass classification - use average absolute coefficient
                for col in X.columns:
                    feature_importance[col] = np.mean([abs(coefficients[col][cls]) for cls in classes])
            
            # Normalize feature importance
            total_importance = sum(feature_importance.values())
            if total_importance > 0:
                for col in feature_importance:
                    feature_importance[col] /= total_importance
            
            # Prepare result
            result = {
                "metrics": {
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                    "f1": f1,
                    "cv_accuracy": cv_accuracy
                },
                "coefficients": coefficients,
                "feature_importance": feature_importance,
                "classes": classes
            }
            
            if auc is not None:
                result["metrics"]["auc"] = auc
            
            return result
            
        except Exception as e:
            logger.warning(f"Logistic regression failed: {e}")
            return None
    
    def _build_random_forest_classification(self, X: pd.DataFrame, y: pd.Series) -> Optional[Dict[str, Any]]:
        """
        Build a random forest classification model.
        
        Args:
            X: Feature DataFrame.
            y: Target Series.
            
        Returns:
            A dictionary containing model results, or None if model building fails.
        """
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import cross_val_score, train_test_split
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
            from sklearn.preprocessing import LabelEncoder
            
            # Encode target if it's not numeric
            if not pd.api.types.is_numeric_dtype(y):
                label_encoder = LabelEncoder()
                y = label_encoder.fit_transform(y)
                classes = label_encoder.classes_.tolist()
            else:
                classes = sorted(y.unique().tolist())
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Create and fit model
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            
            # For binary classification
            if len(classes) == 2:
                precision = precision_score(y_test, y_pred)
                recall = recall_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred)
                
                try:
                    y_prob = model.predict_proba(X_test)[:, 1]
                    auc = roc_auc_score(y_test, y_prob)
                except:
                    auc = None
            else:
                # For multiclass
                precision = precision_score(y_test, y_pred, average='weighted')
                recall = recall_score(y_test, y_pred, average='weighted')
                f1 = f1_score(y_test, y_pred, average='weighted')
                auc = None
            
            # Calculate cross-validation score
            cv_scores = cross_val_score(model, X, y, cv=self.cross_validation_folds, scoring='accuracy')
            cv_accuracy = cv_scores.mean()
            
            # Get feature importance
            feature_importance = {}
            for i, col in enumerate(X.columns):
                feature_importance[col] = model.feature_importances_[i]
            
            # Prepare result
            result = {
                "metrics": {
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                    "f1": f1,
                    "cv_accuracy": cv_accuracy
                },
                "feature_importance": feature_importance,
                "classes": classes
            }
            
            if auc is not None:
                result["metrics"]["auc"] = auc
            
            return result
            
        except Exception as e:
            logger.warning(f"Random forest classification failed: {e}")
            return None
    
    def _build_gradient_boosting_classification(self, X: pd.DataFrame, y: pd.Series) -> Optional[Dict[str, Any]]:
        """
        Build a gradient boosting classification model.
        
        Args:
            X: Feature DataFrame.
            y: Target Series.
            
        Returns:
            A dictionary containing model results, or None if model building fails.
        """
        try:
            from sklearn.ensemble import GradientBoostingClassifier
            from sklearn.model_selection import cross_val_score, train_test_split
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
            from sklearn.preprocessing import LabelEncoder
            
            # Encode target if it's not numeric
            if not pd.api.types.is_numeric_dtype(y):
                label_encoder = LabelEncoder()
                y = label_encoder.fit_transform(y)
                classes = label_encoder.classes_.tolist()
            else:
                classes = sorted(y.unique().tolist())
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Create and fit model
            model = GradientBoostingClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            
            # For binary classification
            if len(classes) == 2:
                precision = precision_score(y_test, y_pred)
                recall = recall_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred)
                
                try:
                    y_prob = model.predict_proba(X_test)[:, 1]
                    auc = roc_auc_score(y_test, y_prob)
                except:
                    auc = None
            else:
                # For multiclass
                precision = precision_score(y_test, y_pred, average='weighted')
                recall = recall_score(y_test, y_pred, average='weighted')
                f1 = f1_score(y_test, y_pred, average='weighted')
                auc = None
            
            # Calculate cross-validation score
            cv_scores = cross_val_score(model, X, y, cv=self.cross_validation_folds, scoring='accuracy')
            cv_accuracy = cv_scores.mean()
            
            # Get feature importance
            feature_importance = {}
            for i, col in enumerate(X.columns):
                feature_importance[col] = model.feature_importances_[i]
            
            # Prepare result
            result = {
                "metrics": {
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                    "f1": f1,
                    "cv_accuracy": cv_accuracy
                },
                "feature_importance": feature_importance,
                "classes": classes
            }
            
            if auc is not None:
                result["metrics"]["auc"] = auc
            
            return result
            
        except Exception as e:
            logger.warning(f"Gradient boosting classification failed: {e}")
            return None
    
    def _select_best_classification_model(self, model_results: Dict[str, Dict[str, Any]]) -> str:
        """
        Select the best classification model based on metrics.
        
        Args:
            model_results: Dictionary of model results by type.
            
        Returns:
            Name of the best model type.
        """
        # Define priority order of metrics
        metrics_priority = ["f1", "auc", "accuracy", "cv_accuracy"]
        
        # Find first available metric
        for metric in metrics_priority:
            if all(metric in model_results[model_type]["metrics"] for model_type in model_results):
                # For all classification metrics, higher is better
                best_model = max(model_results.items(), 
                                key=lambda x: x[1]["metrics"][metric])[0]
                return best_model
        
        # If no common metrics, return first model
        return list(model_results.keys())[0]
    
    def generate_scenarios(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
                         time_column: str, target_column: str,
                         horizon: int = None, num_scenarios: int = 3) -> Dict[str, Any]:
        """
        Generate multiple forecast scenarios.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            time_column: Name of the column containing time/date information.
            target_column: Name of the column containing the values to forecast.
            horizon: Number of periods to forecast. If None, uses the default forecast_horizon.
            num_scenarios: Number of scenarios to generate.
            
        Returns:
            A dictionary containing scenario forecasts.
        """
        logger.info(f"Generating {num_scenarios} forecast scenarios for {target_column}")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        # Set horizon if not provided
        if horizon is None:
            horizon = self.forecast_horizon
        
        # Get base forecast
        base_forecast = self.forecast_time_series(df, time_column, target_column, horizon)
        
        if "error" in base_forecast:
            return base_forecast
        
        # Generate scenarios
        scenarios = {
            "base": {
                "forecast": base_forecast["forecast"],
                "description": "Expected scenario based on current trends"
            }
        }
        
        # Calculate historical volatility
        if target_column in df.columns and pd.api.types.is_numeric_dtype(df[target_column]):
            # Calculate percent changes
            pct_changes = df[target_column].pct_change().dropna()
            
            # Calculate volatility (standard deviation of percent changes)
            volatility = pct_changes.std()
            
            # Generate optimistic scenario
            optimistic_forecast = []
            for i, value in enumerate(base_forecast["forecast"]):
                # Increase by volatility, with larger increases for later periods
                optimistic_factor = 1 + (volatility * (1 + i / horizon))
                optimistic_forecast.append(value * optimistic_factor)
            
            scenarios["optimistic"] = {
                "forecast": optimistic_forecast,
                "description": f"Optimistic scenario with growth exceeding expectations by {volatility*100:.1f}% initially, increasing over time"
            }
            
            # Generate pessimistic scenario
            pessimistic_forecast = []
            for i, value in enumerate(base_forecast["forecast"]):
                # Decrease by volatility, with larger decreases for later periods
                pessimistic_factor = 1 - (volatility * (1 + i / horizon))
                pessimistic_forecast.append(value * pessimistic_factor)
            
            scenarios["pessimistic"] = {
                "forecast": pessimistic_forecast,
                "description": f"Pessimistic scenario with growth below expectations by {volatility*100:.1f}% initially, decreasing further over time"
            }
            
            # If more scenarios requested, add them
            if num_scenarios > 3:
                # Generate very optimistic scenario
                very_optimistic_forecast = []
                for i, value in enumerate(base_forecast["forecast"]):
                    # Increase by 2x volatility
                    very_optimistic_factor = 1 + (2 * volatility * (1 + i / horizon))
                    very_optimistic_forecast.append(value * very_optimistic_factor)
                
                scenarios["very_optimistic"] = {
                    "forecast": very_optimistic_forecast,
                    "description": f"Very optimistic scenario with growth exceeding expectations by {2*volatility*100:.1f}% initially, increasing over time"
                }
            
            if num_scenarios > 4:
                # Generate very pessimistic scenario
                very_pessimistic_forecast = []
                for i, value in enumerate(base_forecast["forecast"]):
                    # Decrease by 2x volatility
                    very_pessimistic_factor = 1 - (2 * volatility * (1 + i / horizon))
                    very_pessimistic_forecast.append(value * very_pessimistic_factor)
                
                scenarios["very_pessimistic"] = {
                    "forecast": very_pessimistic_forecast,
                    "description": f"Very pessimistic scenario with growth below expectations by {2*volatility*100:.1f}% initially, decreasing further over time"
                }
        
        # Add forecast dates if available
        if "forecast_dates" in base_forecast:
            for scenario in scenarios:
                scenarios[scenario]["forecast_dates"] = base_forecast["forecast_dates"]
        
        # Add confidence intervals if available
        if "confidence_intervals" in base_forecast:
            scenarios["base"]["confidence_intervals"] = base_forecast["confidence_intervals"]
        
        logger.info(f"Generated {len(scenarios)} forecast scenarios")
        return scenarios
    
    def analyze(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
               time_column: Optional[str] = None,
               target_column: Optional[str] = None,
               feature_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform a comprehensive predictive analysis.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            time_column: Name of the column containing time/date information.
            target_column: Name of the target column to predict.
            feature_columns: List of feature columns to use. If None, uses all numeric columns.
            
        Returns:
            A dictionary containing the analysis results.
        """
        logger.info("Performing comprehensive predictive analysis")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        # Identify time column if not provided
        if time_column is None:
            time_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if time_cols:
                time_column = time_cols[0]
                logger.info(f"Automatically selected time column: {time_column}")
        
        # Identify target column if not provided
        if target_column is None:
            # Use the first numeric column that's not the time column
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if col != time_column:
                    target_column = col
                    logger.info(f"Automatically selected target column: {target_column}")
                    break
        
        if target_column is None:
            logger.error("No suitable target column found")
            return {"error": "No suitable target column found"}
        
        analysis_results = {}
        
        # Time series forecasting if time column exists
        if time_column and time_column in df.columns:
            try:
                forecast = self.forecast_time_series(df, time_column, target_column)
                if "error" not in forecast:
                    analysis_results["time_series_forecast"] = forecast
                    
                    # Generate scenarios
                    scenarios = self.generate_scenarios(df, time_column, target_column)
                    if "error" not in scenarios:
                        analysis_results["forecast_scenarios"] = scenarios
            except Exception as e:
                logger.warning(f"Time series forecasting failed: {e}")
        
        # Regression or classification model
        try:
            if pd.api.types.is_numeric_dtype(df[target_column]):
                # Regression
                model = self.build_regression_model(df, target_column, feature_columns)
                if "error" not in model:
                    analysis_results["regression_model"] = model
            else:
                # Classification
                model = self.build_classification_model(df, target_column, feature_columns)
                if "error" not in model:
                    analysis_results["classification_model"] = model
        except Exception as e:
            logger.warning(f"Model building failed: {e}")
        
        if not analysis_results:
            logger.error("All predictive analyses failed")
            return {"error": "All predictive analyses failed"}
        
        logger.info("Comprehensive predictive analysis completed")
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
