"""
Diagnostic Analytics Module

This module contains the DiagnosticAnalytics class, which provides diagnostic analytics
capabilities for determining why certain events occurred by identifying root causes.
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional, Tuple, Union
import json
import os
from scipy import stats

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DiagnosticAnalytics:
    """
    The DiagnosticAnalytics class provides methods for determining why certain events
    occurred by identifying root causes.
    
    It includes functionality for root cause analysis, factor identification,
    correlation analysis, and hypothesis testing.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the DiagnosticAnalytics module.
        
        Args:
            config: Configuration parameters for the module.
        """
        self.config = config or {}
        logger.info("Initializing DiagnosticAnalytics module")
        
        # Set default parameters
        self.significance_level = self.config.get("significance_level", 0.05)
        self.correlation_threshold = self.config.get("correlation_threshold", 0.7)
        self.max_factors = self.config.get("max_factors", 5)
        
        logger.info("DiagnosticAnalytics module initialized successfully")
    
    def identify_factors(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
                        target_column: str) -> Dict[str, Any]:
        """
        Identify factors that influence the target variable.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            target_column: Name of the target column to analyze.
            
        Returns:
            A dictionary containing identified factors and their influence.
        """
        logger.info(f"Identifying factors influencing {target_column}")
        
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
        
        factors = {}
        
        # Correlation analysis for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col != target_column]
        
        if numeric_cols:
            # Calculate correlations
            correlations = {}
            for col in numeric_cols:
                corr = df[col].corr(df[target_column])
                if not pd.isna(corr) and abs(corr) >= self.correlation_threshold:
                    correlations[col] = corr
            
            # Sort by absolute correlation
            sorted_correlations = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
            
            # Take top factors
            top_numeric_factors = sorted_correlations[:self.max_factors]
            
            factors["numeric"] = {
                "factors": {col: corr for col, corr in top_numeric_factors},
                "count": len(top_numeric_factors)
            }
        
        # Analysis for categorical columns
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns
        
        if categorical_cols:
            categorical_factors = {}
            
            for col in categorical_cols:
                # Calculate target mean for each category
                category_means = df.groupby(col)[target_column].mean().to_dict()
                
                # Calculate overall mean
                overall_mean = df[target_column].mean()
                
                # Calculate deviation from overall mean
                deviations = {cat: (mean - overall_mean) / overall_mean if overall_mean != 0 else 0
                             for cat, mean in category_means.items()}
                
                # Calculate variance between categories
                if len(category_means) > 1:
                    category_values = list(category_means.values())
                    variance_ratio = max(category_values) / min(category_values) if min(category_values) > 0 else 0
                    
                    # Only include if there's significant variance
                    if variance_ratio > 1.2:  # At least 20% difference
                        categorical_factors[col] = {
                            "category_means": category_means,
                            "deviations": deviations,
                            "variance_ratio": variance_ratio
                        }
            
            # Sort by variance ratio
            sorted_categorical = sorted(categorical_factors.items(), 
                                       key=lambda x: x[1]["variance_ratio"], 
                                       reverse=True)
            
            # Take top factors
            top_categorical_factors = sorted_categorical[:self.max_factors]
            
            factors["categorical"] = {
                "factors": {col: details for col, details in top_categorical_factors},
                "count": len(top_categorical_factors)
            }
        
        # Combine all factors
        all_factors = []
        
        # Add numeric factors
        if "numeric" in factors:
            for col, corr in factors["numeric"]["factors"].items():
                all_factors.append({
                    "factor": col,
                    "type": "numeric",
                    "influence": abs(corr),
                    "direction": "positive" if corr > 0 else "negative",
                    "description": f"{'Positive' if corr > 0 else 'Negative'} correlation of {abs(corr):.2f}"
                })
        
        # Add categorical factors
        if "categorical" in factors:
            for col, details in factors["categorical"]["factors"].items():
                all_factors.append({
                    "factor": col,
                    "type": "categorical",
                    "influence": details["variance_ratio"] - 1,  # Convert to percentage difference
                    "direction": "varies by category",
                    "description": f"Varies by category, up to {(details['variance_ratio']-1)*100:.0f}% difference"
                })
        
        # Sort by influence
        all_factors.sort(key=lambda x: x["influence"], reverse=True)
        
        factors["all_factors"] = all_factors
        factors["top_factors"] = all_factors[:min(5, len(all_factors))]
        
        logger.info(f"Factor identification completed: {len(all_factors)} factors identified")
        return factors
    
    def analyze_correlations(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
                           target_column: str) -> Dict[str, Any]:
        """
        Analyze correlations between variables and the target.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            target_column: Name of the target column to analyze.
            
        Returns:
            A dictionary containing correlation analysis results.
        """
        logger.info(f"Analyzing correlations with {target_column}")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        # Check if target column exists
        if target_column not in df.columns:
            logger.error(f"Target column {target_column} not found in data")
            return {"error": f"Target column {target_column} not found in data"}
        
        correlation_results = {}
        
        # Pearson correlation for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col != target_column]
        
        if numeric_cols:
            pearson_correlations = {}
            spearman_correlations = {}
            p_values = {}
            
            for col in numeric_cols:
                # Pearson correlation (linear)
                pearson_corr, p_value = stats.pearsonr(df[col].dropna(), df[target_column].dropna())
                pearson_correlations[col] = pearson_corr
                
                # Spearman correlation (monotonic, not necessarily linear)
                spearman_corr, _ = stats.spearmanr(df[col].dropna(), df[target_column].dropna())
                spearman_correlations[col] = spearman_corr
                
                p_values[col] = p_value
            
            correlation_results["pearson"] = pearson_correlations
            correlation_results["spearman"] = spearman_correlations
            correlation_results["p_values"] = p_values
            
            # Identify significant correlations
            significant_correlations = {
                col: {
                    "pearson": pearson_correlations[col],
                    "spearman": spearman_correlations[col],
                    "p_value": p_values[col],
                    "is_significant": p_values[col] < self.significance_level
                }
                for col in numeric_cols
                if p_values[col] < self.significance_level and (
                    abs(pearson_correlations[col]) >= self.correlation_threshold or
                    abs(spearman_correlations[col]) >= self.correlation_threshold
                )
            }
            
            correlation_results["significant"] = significant_correlations
        
        # Chi-square test for categorical columns
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns
        
        if categorical_cols and pd.api.types.is_numeric_dtype(df[target_column]):
            chi_square_results = {}
            
            # Discretize target if it's continuous
            if df[target_column].nunique() > 10:
                target_bins = pd.qcut(df[target_column], 4, duplicates='drop')
            else:
                target_bins = df[target_column]
            
            for col in categorical_cols:
                # Create contingency table
                contingency = pd.crosstab(df[col], target_bins)
                
                # Chi-square test
                try:
                    chi2, p, dof, expected = stats.chi2_contingency(contingency)
                    
                    chi_square_results[col] = {
                        "chi2": chi2,
                        "p_value": p,
                        "dof": dof,
                        "is_significant": p < self.significance_level
                    }
                except Exception as e:
                    logger.warning(f"Could not perform chi-square test for {col}: {e}")
            
            correlation_results["chi_square"] = chi_square_results
        
        logger.info(f"Correlation analysis completed")
        return correlation_results
    
    def test_hypothesis(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
                       hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test a hypothesis about the relationship between variables.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            hypothesis: Dictionary describing the hypothesis to test.
                Example: {
                    "type": "difference_in_means",
                    "group_column": "category",
                    "value_column": "sales",
                    "group_a": "A",
                    "group_b": "B"
                }
            
        Returns:
            A dictionary containing hypothesis test results.
        """
        logger.info(f"Testing hypothesis: {hypothesis}")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        # Get hypothesis type
        hypothesis_type = hypothesis.get("type")
        
        if hypothesis_type == "difference_in_means":
            return self._test_difference_in_means(df, hypothesis)
        elif hypothesis_type == "correlation":
            return self._test_correlation(df, hypothesis)
        elif hypothesis_type == "regression":
            return self._test_regression(df, hypothesis)
        elif hypothesis_type == "chi_square":
            return self._test_chi_square(df, hypothesis)
        else:
            logger.error(f"Unsupported hypothesis type: {hypothesis_type}")
            return {"error": f"Unsupported hypothesis type: {hypothesis_type}"}
    
    def _test_difference_in_means(self, df: pd.DataFrame, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test for a difference in means between two groups.
        
        Args:
            df: Input DataFrame.
            hypothesis: Dictionary describing the hypothesis.
            
        Returns:
            A dictionary containing test results.
        """
        # Get parameters
        group_column = hypothesis.get("group_column")
        value_column = hypothesis.get("value_column")
        group_a = hypothesis.get("group_a")
        group_b = hypothesis.get("group_b")
        
        # Validate parameters
        if not all([group_column, value_column, group_a, group_b]):
            return {"error": "Missing required parameters for difference_in_means test"}
        
        if group_column not in df.columns or value_column not in df.columns:
            return {"error": f"Columns {group_column} or {value_column} not found in data"}
        
        # Get group data
        group_a_data = df[df[group_column] == group_a][value_column].dropna()
        group_b_data = df[df[group_column] == group_b][value_column].dropna()
        
        if len(group_a_data) < 2 or len(group_b_data) < 2:
            return {"error": f"Insufficient data for groups {group_a} or {group_b}"}
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(group_a_data, group_b_data, equal_var=False)
        
        # Calculate effect size (Cohen's d)
        mean_a = group_a_data.mean()
        mean_b = group_b_data.mean()
        std_a = group_a_data.std()
        std_b = group_b_data.std()
        
        # Pooled standard deviation
        pooled_std = np.sqrt(((len(group_a_data) - 1) * std_a**2 + (len(group_b_data) - 1) * std_b**2) / 
                            (len(group_a_data) + len(group_b_data) - 2))
        
        # Cohen's d
        cohens_d = (mean_a - mean_b) / pooled_std if pooled_std > 0 else 0
        
        # Interpret effect size
        if abs(cohens_d) < 0.2:
            effect_size_interpretation = "negligible"
        elif abs(cohens_d) < 0.5:
            effect_size_interpretation = "small"
        elif abs(cohens_d) < 0.8:
            effect_size_interpretation = "medium"
        else:
            effect_size_interpretation = "large"
        
        # Prepare results
        results = {
            "test_type": "t-test for independent samples",
            "t_statistic": t_stat,
            "p_value": p_value,
            "is_significant": p_value < self.significance_level,
            "group_a": {
                "name": group_a,
                "count": len(group_a_data),
                "mean": mean_a,
                "std": std_a
            },
            "group_b": {
                "name": group_b,
                "count": len(group_b_data),
                "mean": mean_b,
                "std": std_b
            },
            "difference": mean_a - mean_b,
            "percent_difference": ((mean_a - mean_b) / mean_b) * 100 if mean_b != 0 else float('inf'),
            "effect_size": {
                "cohens_d": cohens_d,
                "interpretation": effect_size_interpretation
            },
            "conclusion": f"{'Significant' if p_value < self.significance_level else 'No significant'} difference found between groups"
        }
        
        return results
    
    def _test_correlation(self, df: pd.DataFrame, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test for correlation between two variables.
        
        Args:
            df: Input DataFrame.
            hypothesis: Dictionary describing the hypothesis.
            
        Returns:
            A dictionary containing test results.
        """
        # Get parameters
        variable_x = hypothesis.get("variable_x")
        variable_y = hypothesis.get("variable_y")
        correlation_type = hypothesis.get("correlation_type", "pearson")
        
        # Validate parameters
        if not all([variable_x, variable_y]):
            return {"error": "Missing required parameters for correlation test"}
        
        if variable_x not in df.columns or variable_y not in df.columns:
            return {"error": f"Columns {variable_x} or {variable_y} not found in data"}
        
        # Get data
        x_data = df[variable_x].dropna()
        y_data = df[variable_y].dropna()
        
        # Ensure data is numeric
        if not pd.api.types.is_numeric_dtype(x_data) or not pd.api.types.is_numeric_dtype(y_data):
            return {"error": f"Variables {variable_x} and {variable_y} must be numeric"}
        
        # Align data (keep only rows where both x and y are not null)
        valid_indices = df[df[variable_x].notna() & df[variable_y].notna()].index
        x_data = df.loc[valid_indices, variable_x]
        y_data = df.loc[valid_indices, variable_y]
        
        if len(x_data) < 3:
            return {"error": "Insufficient data for correlation test"}
        
        # Perform correlation test
        if correlation_type == "pearson":
            corr, p_value = stats.pearsonr(x_data, y_data)
            test_name = "Pearson correlation"
        elif correlation_type == "spearman":
            corr, p_value = stats.spearmanr(x_data, y_data)
            test_name = "Spearman rank correlation"
        elif correlation_type == "kendall":
            corr, p_value = stats.kendalltau(x_data, y_data)
            test_name = "Kendall's tau correlation"
        else:
            return {"error": f"Unsupported correlation type: {correlation_type}"}
        
        # Interpret correlation strength
        if abs(corr) < 0.1:
            strength = "negligible"
        elif abs(corr) < 0.3:
            strength = "weak"
        elif abs(corr) < 0.5:
            strength = "moderate"
        elif abs(corr) < 0.7:
            strength = "strong"
        else:
            strength = "very strong"
        
        # Prepare results
        results = {
            "test_type": test_name,
            "correlation": corr,
            "p_value": p_value,
            "is_significant": p_value < self.significance_level,
            "sample_size": len(x_data),
            "interpretation": {
                "strength": strength,
                "direction": "positive" if corr > 0 else "negative" if corr < 0 else "none"
            },
            "conclusion": f"{'Significant' if p_value < self.significance_level else 'No significant'} {strength} {results['interpretation']['direction']} correlation found"
        }
        
        return results
    
    def _test_regression(self, df: pd.DataFrame, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test a regression model.
        
        Args:
            df: Input DataFrame.
            hypothesis: Dictionary describing the hypothesis.
            
        Returns:
            A dictionary containing test results.
        """
        # Get parameters
        dependent_var = hypothesis.get("dependent_variable")
        independent_vars = hypothesis.get("independent_variables", [])
        
        # Validate parameters
        if not dependent_var or not independent_vars:
            return {"error": "Missing required parameters for regression test"}
        
        if dependent_var not in df.columns:
            return {"error": f"Dependent variable {dependent_var} not found in data"}
        
        for var in independent_vars:
            if var not in df.columns:
                return {"error": f"Independent variable {var} not found in data"}
        
        # Get data
        y = df[dependent_var].dropna()
        X = df[independent_vars].dropna()
        
        # Align data
        valid_indices = df[df[dependent_var].notna() & df[independent_vars].notna().all(axis=1)].index
        y = df.loc[valid_indices, dependent_var]
        X = df.loc[valid_indices, independent_vars]
        
        if len(y) < len(independent_vars) + 2:
            return {"error": "Insufficient data for regression test"}
        
        try:
            # Add constant for intercept
            import statsmodels.api as sm
            X = sm.add_constant(X)
            
            # Fit regression model
            model = sm.OLS(y, X).fit()
            
            # Prepare results
            results = {
                "test_type": "Multiple linear regression",
                "r_squared": model.rsquared,
                "adjusted_r_squared": model.rsquared_adj,
                "f_statistic": model.fvalue,
                "f_pvalue": model.f_pvalue,
                "is_significant": model.f_pvalue < self.significance_level,
                "sample_size": len(y),
                "coefficients": {}
            }
            
            # Add coefficient details
            for i, var in enumerate(['const'] + independent_vars):
                results["coefficients"][var] = {
                    "value": model.params[i],
                    "std_error": model.bse[i],
                    "t_value": model.tvalues[i],
                    "p_value": model.pvalues[i],
                    "is_significant": model.pvalues[i] < self.significance_level
                }
            
            # Add significant predictors
            significant_predictors = [var for var in results["coefficients"] 
                                     if results["coefficients"][var]["is_significant"] and var != 'const']
            
            results["significant_predictors"] = significant_predictors
            results["conclusion"] = f"Model explains {results['r_squared']*100:.1f}% of variance in {dependent_var}"
            
            if significant_predictors:
                results["conclusion"] += f", with {len(significant_predictors)} significant predictors"
            
            return results
            
        except Exception as e:
            logger.error(f"Error in regression test: {e}")
            return {"error": f"Error in regression test: {e}"}
    
    def _test_chi_square(self, df: pd.DataFrame, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test for association between categorical variables.
        
        Args:
            df: Input DataFrame.
            hypothesis: Dictionary describing the hypothesis.
            
        Returns:
            A dictionary containing test results.
        """
        # Get parameters
        variable_a = hypothesis.get("variable_a")
        variable_b = hypothesis.get("variable_b")
        
        # Validate parameters
        if not all([variable_a, variable_b]):
            return {"error": "Missing required parameters for chi-square test"}
        
        if variable_a not in df.columns or variable_b not in df.columns:
            return {"error": f"Columns {variable_a} or {variable_b} not found in data"}
        
        # Create contingency table
        contingency = pd.crosstab(df[variable_a], df[variable_b])
        
        # Perform chi-square test
        try:
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
            
            # Calculate Cramer's V for effect size
            n = contingency.sum().sum()
            phi2 = chi2 / n
            r, k = contingency.shape
            cramers_v = np.sqrt(phi2 / min(k-1, r-1)) if min(k-1, r-1) > 0 else 0
            
            # Interpret effect size
            if cramers_v < 0.1:
                effect_size_interpretation = "negligible"
            elif cramers_v < 0.3:
                effect_size_interpretation = "small"
            elif cramers_v < 0.5:
                effect_size_interpretation = "medium"
            else:
                effect_size_interpretation = "large"
            
            # Prepare results
            results = {
                "test_type": "Chi-square test of independence",
                "chi_square": chi2,
                "p_value": p_value,
                "degrees_of_freedom": dof,
                "is_significant": p_value < self.significance_level,
                "effect_size": {
                    "cramers_v": cramers_v,
                    "interpretation": effect_size_interpretation
                },
                "contingency_table": contingency.to_dict(),
                "conclusion": f"{'Significant' if p_value < self.significance_level else 'No significant'} association found between {variable_a} and {variable_b}"
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error in chi-square test: {e}")
            return {"error": f"Error in chi-square test: {e}"}
    
    def perform_root_cause_analysis(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
                                  target_column: str, 
                                  event_filter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform a comprehensive root cause analysis.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            target_column: Name of the target column to analyze.
            event_filter: Optional filter to focus on specific events.
                Example: {"column": "status", "value": "failed"}
            
        Returns:
            A dictionary containing root cause analysis results.
        """
        logger.info(f"Performing root cause analysis for {target_column}")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        # Apply event filter if provided
        if event_filter and "column" in event_filter and "value" in event_filter:
            filter_column = event_filter["column"]
            filter_value = event_filter["value"]
            
            if filter_column in df.columns:
                filtered_df = df[df[filter_column] == filter_value]
                logger.info(f"Applied filter {filter_column} = {filter_value}, {len(filtered_df)} rows remaining")
            else:
                filtered_df = df
                logger.warning(f"Filter column {filter_column} not found in data")
        else:
            filtered_df = df
        
        # Perform analysis
        analysis_results = {
            "factors": self.identify_factors(filtered_df, target_column),
            "correlations": self.analyze_correlations(filtered_df, target_column)
        }
        
        # Identify top factors
        top_factors = []
        
        # Add numeric factors
        if "factors" in analysis_results and "all_factors" in analysis_results["factors"]:
            top_factors = analysis_results["factors"]["all_factors"][:5]
        
        # Generate hypotheses for top factors
        hypotheses = []
        
        for factor in top_factors:
            factor_name = factor["factor"]
            factor_type = factor["type"]
            
            if factor_type == "numeric":
                # Create correlation hypothesis
                hypotheses.append({
                    "type": "correlation",
                    "variable_x": factor_name,
                    "variable_y": target_column,
                    "correlation_type": "pearson",
                    "description": f"Test correlation between {factor_name} and {target_column}"
                })
            elif factor_type == "categorical":
                # Create chi-square hypothesis
                hypotheses.append({
                    "type": "chi_square",
                    "variable_a": factor_name,
                    "variable_b": target_column if pd.api.types.is_categorical_dtype(df[target_column]) else None,
                    "description": f"Test association between {factor_name} and {target_column}"
                })
        
        # Test hypotheses
        hypothesis_results = {}
        
        for i, hypothesis in enumerate(hypotheses):
            if hypothesis["type"] == "chi_square" and hypothesis["variable_b"] is None:
                # Skip chi-square test if target is not categorical
                continue
                
            hypothesis_results[f"hypothesis_{i+1}"] = {
                "hypothesis": hypothesis,
                "result": self.test_hypothesis(filtered_df, hypothesis)
            }
        
        analysis_results["hypothesis_tests"] = hypothesis_results
        
        # Generate root causes
        root_causes = []
        
        # Add causes from significant correlations
        if "correlations" in analysis_results and "significant" in analysis_results["correlations"]:
            for factor, details in analysis_results["correlations"]["significant"].items():
                root_causes.append({
                    "factor": factor,
                    "evidence": f"Significant {details['pearson']:.2f} correlation with {target_column} (p={details['p_value']:.4f})",
                    "confidence": 0.8 if abs(details["pearson"]) > 0.8 else 0.6
                })
        
        # Add causes from hypothesis tests
        for hypothesis_id, hypothesis_data in hypothesis_results.items():
            result = hypothesis_data["result"]
            
            if "is_significant" in result and result["is_significant"]:
                if hypothesis_data["hypothesis"]["type"] == "correlation":
                    var_x = hypothesis_data["hypothesis"]["variable_x"]
                    root_causes.append({
                        "factor": var_x,
                        "evidence": f"Significant {result['correlation']:.2f} correlation confirmed by hypothesis test (p={result['p_value']:.4f})",
                        "confidence": 0.9 if abs(result["correlation"]) > 0.8 else 0.7
                    })
                elif hypothesis_data["hypothesis"]["type"] == "chi_square":
                    var_a = hypothesis_data["hypothesis"]["variable_a"]
                    root_causes.append({
                        "factor": var_a,
                        "evidence": f"Significant association confirmed by chi-square test (p={result['p_value']:.4f})",
                        "confidence": 0.8 if result["effect_size"]["cramers_v"] > 0.3 else 0.6
                    })
        
        # Remove duplicates and sort by confidence
        unique_factors = set()
        unique_root_causes = []
        
        for cause in sorted(root_causes, key=lambda x: x["confidence"], reverse=True):
            if cause["factor"] not in unique_factors:
                unique_factors.add(cause["factor"])
                unique_root_causes.append(cause)
        
        analysis_results["root_causes"] = unique_root_causes
        
        # Generate conclusion
        if unique_root_causes:
            top_cause = unique_root_causes[0]
            analysis_results["conclusion"] = f"The primary factor affecting {target_column} appears to be {top_cause['factor']} ({top_cause['evidence']})"
            
            if len(unique_root_causes) > 1:
                analysis_results["conclusion"] += f", with {len(unique_root_causes)-1} additional contributing factors"
        else:
            analysis_results["conclusion"] = f"No significant factors affecting {target_column} were identified"
        
        logger.info(f"Root cause analysis completed: {len(unique_root_causes)} causes identified")
        return analysis_results
    
    def compare_segments(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
                        segment_column: str, 
                        metrics: List[str]) -> Dict[str, Any]:
        """
        Compare different segments across multiple metrics.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            segment_column: Name of the column used for segmentation.
            metrics: List of metric columns to compare.
            
        Returns:
            A dictionary containing segment comparison results.
        """
        logger.info(f"Comparing segments based on {segment_column} across {len(metrics)} metrics")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        # Check if columns exist
        if segment_column not in df.columns:
            logger.error(f"Segment column {segment_column} not found in data")
            return {"error": f"Segment column {segment_column} not found in data"}
        
        for metric in metrics:
            if metric not in df.columns:
                logger.error(f"Metric column {metric} not found in data")
                return {"error": f"Metric column {metric} not found in data"}
        
        # Get segments
        segments = df[segment_column].unique()
        
        if len(segments) < 2:
            logger.error(f"At least 2 segments required, found {len(segments)}")
            return {"error": f"At least 2 segments required, found {len(segments)}"}
        
        comparison_results = {
            "segments": list(segments),
            "segment_counts": df[segment_column].value_counts().to_dict(),
            "metrics": {}
        }
        
        # Compare each metric
        for metric in metrics:
            if not pd.api.types.is_numeric_dtype(df[metric]):
                logger.warning(f"Skipping non-numeric metric {metric}")
                continue
                
            metric_results = {
                "segment_values": {},
                "segment_comparisons": {},
                "overall": {
                    "mean": df[metric].mean(),
                    "median": df[metric].median(),
                    "std": df[metric].std()
                }
            }
            
            # Calculate values for each segment
            for segment in segments:
                segment_data = df[df[segment_column] == segment][metric].dropna()
                
                if len(segment_data) > 0:
                    metric_results["segment_values"][segment] = {
                        "count": len(segment_data),
                        "mean": segment_data.mean(),
                        "median": segment_data.median(),
                        "std": segment_data.std(),
                        "min": segment_data.min(),
                        "max": segment_data.max()
                    }
            
            # Compare segments pairwise
            for i, segment_a in enumerate(segments):
                for segment_b in segments[i+1:]:
                    if (segment_a in metric_results["segment_values"] and 
                        segment_b in metric_results["segment_values"]):
                        
                        # Get segment data
                        segment_a_data = df[df[segment_column] == segment_a][metric].dropna()
                        segment_b_data = df[df[segment_column] == segment_b][metric].dropna()
                        
                        if len(segment_a_data) > 1 and len(segment_b_data) > 1:
                            # Perform t-test
                            t_stat, p_value = stats.ttest_ind(segment_a_data, segment_b_data, equal_var=False)
                            
                            # Calculate percent difference
                            mean_a = segment_a_data.mean()
                            mean_b = segment_b_data.mean()
                            percent_diff = ((mean_a - mean_b) / mean_b) * 100 if mean_b != 0 else float('inf')
                            
                            comparison_key = f"{segment_a}_vs_{segment_b}"
                            metric_results["segment_comparisons"][comparison_key] = {
                                "t_statistic": t_stat,
                                "p_value": p_value,
                                "is_significant": p_value < self.significance_level,
                                "difference": mean_a - mean_b,
                                "percent_difference": percent_diff,
                                "higher_segment": segment_a if mean_a > mean_b else segment_b
                            }
            
            # Find best and worst segments
            if metric_results["segment_values"]:
                segment_means = {segment: values["mean"] 
                                for segment, values in metric_results["segment_values"].items()}
                
                best_segment = max(segment_means.items(), key=lambda x: x[1])[0]
                worst_segment = min(segment_means.items(), key=lambda x: x[1])[0]
                
                metric_results["best_segment"] = {
                    "segment": best_segment,
                    "mean": segment_means[best_segment]
                }
                
                metric_results["worst_segment"] = {
                    "segment": worst_segment,
                    "mean": segment_means[worst_segment]
                }
                
                # Calculate max difference
                max_diff_percent = ((segment_means[best_segment] - segment_means[worst_segment]) / 
                                   segment_means[worst_segment]) * 100 if segment_means[worst_segment] != 0 else float('inf')
                
                metric_results["max_difference"] = {
                    "segments": f"{best_segment}_vs_{worst_segment}",
                    "absolute": segment_means[best_segment] - segment_means[worst_segment],
                    "percent": max_diff_percent
                }
            
            comparison_results["metrics"][metric] = metric_results
        
        # Generate insights
        insights = []
        
        for metric, results in comparison_results["metrics"].items():
            if "max_difference" in results:
                max_diff = results["max_difference"]
                
                if abs(max_diff["percent"]) > 20:  # Significant difference threshold
                    insights.append({
                        "metric": metric,
                        "insight": f"{results['best_segment']['segment']} performs {abs(max_diff['percent']):.1f}% better than {results['worst_segment']['segment']} on {metric}",
                        "magnitude": abs(max_diff["percent"])
                    })
            
            # Add insights from significant comparisons
            for comparison, comp_results in results.get("segment_comparisons", {}).items():
                if comp_results["is_significant"] and abs(comp_results["percent_difference"]) > 10:
                    segments = comparison.split("_vs_")
                    insights.append({
                        "metric": metric,
                        "insight": f"Significant difference of {abs(comp_results['percent_difference']):.1f}% between {segments[0]} and {segments[1]} on {metric}",
                        "magnitude": abs(comp_results["percent_difference"])
                    })
        
        # Sort insights by magnitude
        comparison_results["insights"] = sorted(insights, key=lambda x: x["magnitude"], reverse=True)
        
        logger.info(f"Segment comparison completed: {len(comparison_results['insights'])} insights generated")
        return comparison_results
    
    def analyze(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
               target_column: str,
               event_filter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform a comprehensive diagnostic analysis.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            target_column: Name of the target column to analyze.
            event_filter: Optional filter to focus on specific events.
            
        Returns:
            A dictionary containing the analysis results.
        """
        logger.info(f"Performing comprehensive diagnostic analysis for {target_column}")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        # Check if target column exists
        if target_column not in df.columns:
            logger.error(f"Target column {target_column} not found in data")
            return {"error": f"Target column {target_column} not found in data"}
        
        # Perform root cause analysis
        analysis_results = self.perform_root_cause_analysis(df, target_column, event_filter)
        
        # If target is categorical, perform segment comparison
        if not pd.api.types.is_numeric_dtype(df[target_column]):
            # Find numeric columns for comparison
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if numeric_cols:
                segment_comparison = self.compare_segments(df, target_column, numeric_cols)
                analysis_results["segment_comparison"] = segment_comparison
        
        logger.info("Comprehensive diagnostic analysis completed")
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
