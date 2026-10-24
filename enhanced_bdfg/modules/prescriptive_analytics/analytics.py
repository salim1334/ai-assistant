"""
Prescriptive Analytics Module

This module contains the PrescriptiveAnalytics class, which provides prescriptive analytics
capabilities for recommending actions to optimize business outcomes.
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

class PrescriptiveAnalytics:
    """
    The PrescriptiveAnalytics class provides methods for recommending actions
    to optimize business outcomes.
    
    It includes functionality for optimization, decision analysis, action planning,
    and impact assessment.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the PrescriptiveAnalytics module.
        
        Args:
            config: Configuration parameters for the module.
        """
        self.config = config or {}
        logger.info("Initializing PrescriptiveAnalytics module")
        
        # Set default parameters
        self.optimization_iterations = self.config.get("optimization_iterations", 1000)
        self.confidence_level = self.config.get("confidence_level", 0.95)
        self.risk_tolerance = self.config.get("risk_tolerance", 0.5)  # 0 = risk averse, 1 = risk seeking
        self.max_recommendations = self.config.get("max_recommendations", 5)
        
        logger.info("PrescriptiveAnalytics module initialized successfully")
    
    def optimize_resource_allocation(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
                                   resources: List[Dict[str, Any]],
                                   constraints: List[Dict[str, Any]],
                                   objective: str = "maximize_profit") -> Dict[str, Any]:
        """
        Optimize resource allocation to maximize an objective.
        
        Args:
            data: Historical data as DataFrame or dictionary/list of dictionaries.
            resources: List of resources to allocate, each with name, cost, and capacity.
            constraints: List of constraints on resource allocation.
            objective: Objective function to optimize (maximize_profit, minimize_cost, maximize_revenue).
            
        Returns:
            A dictionary containing optimization results.
        """
        logger.info(f"Optimizing resource allocation for {objective}")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        # Validate resources
        if not resources:
            logger.error("No resources provided")
            return {"error": "No resources provided"}
        
        # Try different optimization methods
        optimization_results = {}
        
        # Linear programming
        lp_result = self._optimize_with_linear_programming(df, resources, constraints, objective)
        if lp_result and "error" not in lp_result:
            optimization_results["linear_programming"] = lp_result
        
        # Genetic algorithm
        ga_result = self._optimize_with_genetic_algorithm(df, resources, constraints, objective)
        if ga_result and "error" not in ga_result:
            optimization_results["genetic_algorithm"] = ga_result
        
        # If no optimization methods were successful, return error
        if not optimization_results:
            logger.error("All optimization methods failed")
            return {"error": "All optimization methods failed"}
        
        # Select best result based on objective value
        best_method = self._select_best_optimization(optimization_results, objective)
        
        # Prepare final result
        final_result = {
            "method": best_method,
            "allocation": optimization_results[best_method]["allocation"],
            "objective_value": optimization_results[best_method]["objective_value"],
            "constraints_satisfied": optimization_results[best_method]["constraints_satisfied"],
            "all_methods": list(optimization_results.keys())
        }
        
        logger.info(f"Resource allocation optimization completed using {best_method}")
        return final_result
    
    def _optimize_with_linear_programming(self, df: pd.DataFrame, 
                                        resources: List[Dict[str, Any]],
                                        constraints: List[Dict[str, Any]],
                                        objective: str) -> Optional[Dict[str, Any]]:
        """
        Optimize using linear programming.
        
        Args:
            df: Historical data.
            resources: List of resources to allocate.
            constraints: List of constraints on resource allocation.
            objective: Objective function to optimize.
            
        Returns:
            A dictionary containing optimization results, or None if optimization fails.
        """
        try:
            from scipy.optimize import linprog
            
            # Extract resource names and costs
            resource_names = [r["name"] for r in resources]
            resource_costs = [r["cost"] for r in resources]
            resource_capacities = [r.get("capacity", float('inf')) for r in resources]
            
            # Extract constraint coefficients
            constraint_coefficients = []
            constraint_bounds = []
            
            for constraint in constraints:
                if "coefficients" in constraint and "bound" in constraint:
                    # Ensure coefficients match resources
                    if len(constraint["coefficients"]) == len(resources):
                        constraint_coefficients.append(constraint["coefficients"])
                        constraint_bounds.append(constraint["bound"])
            
            # Set up objective function (negative for maximization)
            if objective == "maximize_profit" or objective == "maximize_revenue":
                # Extract profit or revenue coefficients from resources
                if objective == "maximize_profit":
                    objective_coefficients = [-r.get("profit", 0) for r in resources]
                else:
                    objective_coefficients = [-r.get("revenue", 0) for r in resources]
            else:
                # Minimize cost
                objective_coefficients = resource_costs
            
            # Add capacity constraints
            for i, capacity in enumerate(resource_capacities):
                if capacity < float('inf'):
                    coef = [0] * len(resources)
                    coef[i] = 1
                    constraint_coefficients.append(coef)
                    constraint_bounds.append(capacity)
            
            # Add non-negativity bounds
            bounds = [(0, None) for _ in resources]
            
            # Solve linear programming problem
            result = linprog(
                c=objective_coefficients,
                A_ub=constraint_coefficients if constraint_coefficients else None,
                b_ub=constraint_bounds if constraint_bounds else None,
                bounds=bounds,
                method='highs'
            )
            
            if result.success:
                # Calculate objective value
                if objective == "maximize_profit":
                    objective_value = -result.fun  # Negate because we minimized negative profit
                elif objective == "maximize_revenue":
                    objective_value = -result.fun  # Negate because we minimized negative revenue
                else:
                    objective_value = result.fun
                
                # Prepare allocation
                allocation = {}
                for i, name in enumerate(resource_names):
                    allocation[name] = result.x[i]
                
                # Check if constraints are satisfied
                constraints_satisfied = True
                if constraint_coefficients:
                    for i, coef in enumerate(constraint_coefficients):
                        constraint_value = sum(c * x for c, x in zip(coef, result.x))
                        if constraint_value > constraint_bounds[i] + 1e-6:  # Allow small numerical error
                            constraints_satisfied = False
                            break
                
                # Prepare result
                optimization_result = {
                    "allocation": allocation,
                    "objective_value": objective_value,
                    "constraints_satisfied": constraints_satisfied,
                    "iterations": result.nit
                }
                
                return optimization_result
            else:
                logger.warning(f"Linear programming optimization failed: {result.message}")
                return None
            
        except Exception as e:
            logger.warning(f"Linear programming optimization failed: {e}")
            return None
    
    def _optimize_with_genetic_algorithm(self, df: pd.DataFrame, 
                                       resources: List[Dict[str, Any]],
                                       constraints: List[Dict[str, Any]],
                                       objective: str) -> Optional[Dict[str, Any]]:
        """
        Optimize using genetic algorithm.
        
        Args:
            df: Historical data.
            resources: List of resources to allocate.
            constraints: List of constraints on resource allocation.
            objective: Objective function to optimize.
            
        Returns:
            A dictionary containing optimization results, or None if optimization fails.
        """
        try:
            # Extract resource names and costs
            resource_names = [r["name"] for r in resources]
            resource_costs = [r["cost"] for r in resources]
            resource_capacities = [r.get("capacity", float('inf')) for r in resources]
            
            # Extract constraint coefficients
            constraint_coefficients = []
            constraint_bounds = []
            
            for constraint in constraints:
                if "coefficients" in constraint and "bound" in constraint:
                    # Ensure coefficients match resources
                    if len(constraint["coefficients"]) == len(resources):
                        constraint_coefficients.append(constraint["coefficients"])
                        constraint_bounds.append(constraint["bound"])
            
            # Define fitness function
            def fitness_function(allocation):
                # Check constraints
                for i, coef in enumerate(constraint_coefficients):
                    constraint_value = sum(c * x for c, x in zip(coef, allocation))
                    if constraint_value > constraint_bounds[i]:
                        return -float('inf')  # Invalid solution
                
                # Check capacity constraints
                for i, capacity in enumerate(resource_capacities):
                    if allocation[i] > capacity:
                        return -float('inf')  # Invalid solution
                
                # Calculate objective value
                if objective == "maximize_profit":
                    profits = [r.get("profit", 0) for r in resources]
                    return sum(p * a for p, a in zip(profits, allocation))
                elif objective == "maximize_revenue":
                    revenues = [r.get("revenue", 0) for r in resources]
                    return sum(r * a for r, a in zip(revenues, allocation))
                else:
                    # Minimize cost (return negative for maximization problem)
                    return -sum(c * a for c, a in zip(resource_costs, allocation))
            
            # Implement simple genetic algorithm
            population_size = 100
            num_generations = self.optimization_iterations
            mutation_rate = 0.1
            
            # Initialize population
            population = []
            for _ in range(population_size):
                # Random allocation within capacity constraints
                individual = [np.random.uniform(0, min(cap, 100)) for cap in resource_capacities]
                population.append(individual)
            
            best_fitness = -float('inf')
            best_individual = None
            
            # Evolution
            for generation in range(num_generations):
                # Evaluate fitness
                fitness_scores = [fitness_function(ind) for ind in population]
                
                # Check for new best
                max_fitness = max(fitness_scores)
                if max_fitness > best_fitness:
                    best_fitness = max_fitness
                    best_individual = population[fitness_scores.index(max_fitness)]
                
                # Selection (tournament selection)
                new_population = []
                for _ in range(population_size):
                    # Select two random individuals
                    i1, i2 = np.random.randint(0, population_size, 2)
                    # Tournament
                    if fitness_scores[i1] > fitness_scores[i2]:
                        new_population.append(population[i1])
                    else:
                        new_population.append(population[i2])
                
                # Crossover and mutation
                for i in range(0, population_size, 2):
                    if i + 1 < population_size:
                        # Crossover
                        crossover_point = np.random.randint(1, len(resources))
                        new_population[i][:crossover_point], new_population[i+1][:crossover_point] = \
                            new_population[i+1][:crossover_point], new_population[i][:crossover_point]
                        
                        # Mutation
                        for j in range(len(resources)):
                            if np.random.random() < mutation_rate:
                                new_population[i][j] = np.random.uniform(0, min(resource_capacities[j], 100))
                            if np.random.random() < mutation_rate:
                                new_population[i+1][j] = np.random.uniform(0, min(resource_capacities[j], 100))
                
                population = new_population
            
            if best_individual is not None:
                # Calculate objective value
                objective_value = best_fitness
                
                # Prepare allocation
                allocation = {}
                for i, name in enumerate(resource_names):
                    allocation[name] = best_individual[i]
                
                # Check if constraints are satisfied
                constraints_satisfied = True
                for i, coef in enumerate(constraint_coefficients):
                    constraint_value = sum(c * x for c, x in zip(coef, best_individual))
                    if constraint_value > constraint_bounds[i] + 1e-6:  # Allow small numerical error
                        constraints_satisfied = False
                        break
                
                # Prepare result
                optimization_result = {
                    "allocation": allocation,
                    "objective_value": objective_value,
                    "constraints_satisfied": constraints_satisfied,
                    "iterations": num_generations
                }
                
                return optimization_result
            else:
                logger.warning("Genetic algorithm optimization failed to find valid solution")
                return None
            
        except Exception as e:
            logger.warning(f"Genetic algorithm optimization failed: {e}")
            return None
    
    def _select_best_optimization(self, optimization_results: Dict[str, Dict[str, Any]], 
                                objective: str) -> str:
        """
        Select the best optimization result based on objective value.
        
        Args:
            optimization_results: Dictionary of optimization results by method.
            objective: Objective function being optimized.
            
        Returns:
            Name of the best optimization method.
        """
        # For maximization objectives, higher is better
        if objective.startswith("maximize"):
            best_method = max(optimization_results.items(), 
                             key=lambda x: x[1]["objective_value"])[0]
        # For minimization objectives, lower is better
        else:
            best_method = min(optimization_results.items(), 
                             key=lambda x: x[1]["objective_value"])[0]
        
        return best_method
    
    def analyze_decision_options(self, options: List[Dict[str, Any]],
                               criteria: List[Dict[str, Any]],
                               weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Analyze decision options based on multiple criteria.
        
        Args:
            options: List of decision options, each with name and criteria values.
            criteria: List of criteria to evaluate options against.
            weights: Optional dictionary of criteria weights.
            
        Returns:
            A dictionary containing decision analysis results.
        """
        logger.info(f"Analyzing {len(options)} decision options against {len(criteria)} criteria")
        
        # Validate inputs
        if not options:
            logger.error("No options provided")
            return {"error": "No options provided"}
        
        if not criteria:
            logger.error("No criteria provided")
            return {"error": "No criteria provided"}
        
        # Extract criteria names
        criteria_names = [c["name"] for c in criteria]
        
        # Set default weights if not provided
        if weights is None:
            weights = {c["name"]: 1.0 / len(criteria) for c in criteria}
        else:
            # Normalize weights to sum to 1
            total_weight = sum(weights.values())
            if total_weight > 0:
                weights = {k: v / total_weight for k, v in weights.items()}
        
        # Create evaluation matrix
        evaluation_matrix = []
        for option in options:
            option_values = []
            for criterion in criteria_names:
                if criterion in option:
                    option_values.append(option[criterion])
                else:
                    logger.warning(f"Criterion {criterion} not found for option {option['name']}")
                    option_values.append(0)
            evaluation_matrix.append(option_values)
        
        # Try different decision analysis methods
        analysis_results = {}
        
        # Weighted sum model
        wsm_result = self._analyze_with_weighted_sum(options, criteria, weights, evaluation_matrix)
        if wsm_result:
            analysis_results["weighted_sum"] = wsm_result
        
        # TOPSIS method
        topsis_result = self._analyze_with_topsis(options, criteria, weights, evaluation_matrix)
        if topsis_result:
            analysis_results["topsis"] = topsis_result
        
        # If no analysis methods were successful, return error
        if not analysis_results:
            logger.error("All decision analysis methods failed")
            return {"error": "All decision analysis methods failed"}
        
        # Combine results
        final_result = {
            "options": [o["name"] for o in options],
            "criteria": criteria_names,
            "weights": weights,
            "methods": analysis_results
        }
        
        # Calculate consensus ranking
        consensus_ranking = self._calculate_consensus_ranking(analysis_results)
        final_result["consensus_ranking"] = consensus_ranking
        
        # Add recommendations
        recommendations = []
        for i, option_name in enumerate(consensus_ranking):
            if i < self.max_recommendations:
                option_data = next((o for o in options if o["name"] == option_name), None)
                if option_data:
                    # Find strengths and weaknesses
                    strengths = []
                    weaknesses = []
                    
                    for j, criterion in enumerate(criteria):
                        criterion_name = criterion["name"]
                        criterion_direction = criterion.get("direction", "maximize")
                        criterion_weight = weights.get(criterion_name, 0)
                        
                        # Find option index
                        option_index = next((i for i, o in enumerate(options) if o["name"] == option_name), None)
                        
                        if option_index is not None:
                            criterion_value = evaluation_matrix[option_index][j]
                            
                            # Compare to average
                            criterion_values = [row[j] for row in evaluation_matrix]
                            average_value = sum(criterion_values) / len(criterion_values)
                            
                            if criterion_direction == "maximize":
                                if criterion_value > average_value:
                                    strengths.append(f"Strong in {criterion_name} ({criterion_value:.2f} vs avg {average_value:.2f})")
                                elif criterion_value < average_value:
                                    weaknesses.append(f"Weak in {criterion_name} ({criterion_value:.2f} vs avg {average_value:.2f})")
                            else:
                                if criterion_value < average_value:
                                    strengths.append(f"Strong in {criterion_name} ({criterion_value:.2f} vs avg {average_value:.2f})")
                                elif criterion_value > average_value:
                                    weaknesses.append(f"Weak in {criterion_name} ({criterion_value:.2f} vs avg {average_value:.2f})")
                    
                    recommendations.append({
                        "rank": i + 1,
                        "option": option_name,
                        "strengths": strengths[:3],  # Top 3 strengths
                        "weaknesses": weaknesses[:2],  # Top 2 weaknesses
                        "description": option_data.get("description", "")
                    })
        
        final_result["recommendations"] = recommendations
        
        logger.info(f"Decision analysis completed with {len(recommendations)} recommendations")
        return final_result
    
    def _analyze_with_weighted_sum(self, options: List[Dict[str, Any]],
                                 criteria: List[Dict[str, Any]],
                                 weights: Dict[str, float],
                                 evaluation_matrix: List[List[float]]) -> Optional[Dict[str, Any]]:
        """
        Analyze decision options using weighted sum model.
        
        Args:
            options: List of decision options.
            criteria: List of criteria.
            weights: Dictionary of criteria weights.
            evaluation_matrix: Matrix of option values for each criterion.
            
        Returns:
            A dictionary containing analysis results, or None if analysis fails.
        """
        try:
            # Normalize evaluation matrix
            normalized_matrix = []
            for i in range(len(evaluation_matrix)):
                normalized_row = []
                for j in range(len(evaluation_matrix[0])):
                    # Get all values for this criterion
                    criterion_values = [row[j] for row in evaluation_matrix]
                    max_value = max(criterion_values)
                    min_value = min(criterion_values)
                    
                    if max_value == min_value:
                        normalized_value = 1.0  # All options are equal
                    else:
                        # Normalize based on criterion direction
                        criterion_direction = criteria[j].get("direction", "maximize")
                        
                        if criterion_direction == "maximize":
                            normalized_value = (evaluation_matrix[i][j] - min_value) / (max_value - min_value)
                        else:
                            normalized_value = (max_value - evaluation_matrix[i][j]) / (max_value - min_value)
                    
                    normalized_row.append(normalized_value)
                
                normalized_matrix.append(normalized_row)
            
            # Calculate weighted sum for each option
            weighted_sums = []
            for i, option in enumerate(options):
                weighted_sum = 0
                for j, criterion in enumerate(criteria):
                    criterion_name = criterion["name"]
                    criterion_weight = weights.get(criterion_name, 0)
                    weighted_sum += normalized_matrix[i][j] * criterion_weight
                
                weighted_sums.append({
                    "option": option["name"],
                    "score": weighted_sum
                })
            
            # Sort options by score (descending)
            weighted_sums.sort(key=lambda x: x["score"], reverse=True)
            
            # Create ranking
            ranking = [ws["option"] for ws in weighted_sums]
            
            # Prepare result
            result = {
                "ranking": ranking,
                "scores": {ws["option"]: ws["score"] for ws in weighted_sums}
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"Weighted sum analysis failed: {e}")
            return None
    
    def _analyze_with_topsis(self, options: List[Dict[str, Any]],
                           criteria: List[Dict[str, Any]],
                           weights: Dict[str, float],
                           evaluation_matrix: List[List[float]]) -> Optional[Dict[str, Any]]:
        """
        Analyze decision options using TOPSIS method.
        
        Args:
            options: List of decision options.
            criteria: List of criteria.
            weights: Dictionary of criteria weights.
            evaluation_matrix: Matrix of option values for each criterion.
            
        Returns:
            A dictionary containing analysis results, or None if analysis fails.
        """
        try:
            # Convert evaluation matrix to numpy array
            matrix = np.array(evaluation_matrix)
            
            # Calculate normalized decision matrix
            # Normalize by dividing each value by the square root of sum of squares for that criterion
            norm = np.sqrt(np.sum(matrix**2, axis=0))
            normalized_matrix = matrix / norm
            
            # Calculate weighted normalized decision matrix
            weight_values = [weights.get(c["name"], 0) for c in criteria]
            weighted_matrix = normalized_matrix * weight_values
            
            # Determine ideal and negative-ideal solutions
            ideal = np.zeros(len(criteria))
            negative_ideal = np.zeros(len(criteria))
            
            for j in range(len(criteria)):
                criterion_direction = criteria[j].get("direction", "maximize")
                
                if criterion_direction == "maximize":
                    ideal[j] = np.max(weighted_matrix[:, j])
                    negative_ideal[j] = np.min(weighted_matrix[:, j])
                else:
                    ideal[j] = np.min(weighted_matrix[:, j])
                    negative_ideal[j] = np.max(weighted_matrix[:, j])
            
            # Calculate separation measures
            separation_ideal = np.sqrt(np.sum((weighted_matrix - ideal)**2, axis=1))
            separation_negative = np.sqrt(np.sum((weighted_matrix - negative_ideal)**2, axis=1))
            
            # Calculate relative closeness to ideal solution
            relative_closeness = separation_negative / (separation_ideal + separation_negative)
            
            # Create ranking
            topsis_scores = []
            for i, option in enumerate(options):
                topsis_scores.append({
                    "option": option["name"],
                    "score": relative_closeness[i]
                })
            
            # Sort options by score (descending)
            topsis_scores.sort(key=lambda x: x["score"], reverse=True)
            
            # Create ranking
            ranking = [ts["option"] for ts in topsis_scores]
            
            # Prepare result
            result = {
                "ranking": ranking,
                "scores": {ts["option"]: ts["score"] for ts in topsis_scores}
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"TOPSIS analysis failed: {e}")
            return None
    
    def _calculate_consensus_ranking(self, analysis_results: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        Calculate consensus ranking from multiple analysis methods.
        
        Args:
            analysis_results: Dictionary of analysis results by method.
            
        Returns:
            List of options in consensus ranking order.
        """
        # Extract rankings from each method
        rankings = []
        for method, result in analysis_results.items():
            if "ranking" in result:
                rankings.append(result["ranking"])
        
        if not rankings:
            return []
        
        # Get all unique options
        all_options = set()
        for ranking in rankings:
            all_options.update(ranking)
        
        # Calculate Borda count for each option
        borda_scores = {option: 0 for option in all_options}
        
        for ranking in rankings:
            for i, option in enumerate(ranking):
                # Higher rank (lower index) gets more points
                borda_scores[option] += len(ranking) - i
        
        # Sort options by Borda score (descending)
        consensus_ranking = sorted(all_options, key=lambda x: borda_scores[x], reverse=True)
        
        return consensus_ranking
    
    def generate_action_plan(self, objectives: List[Dict[str, Any]],
                           actions: List[Dict[str, Any]],
                           constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate an action plan to achieve objectives.
        
        Args:
            objectives: List of objectives to achieve.
            actions: List of possible actions.
            constraints: Optional constraints on the action plan.
            
        Returns:
            A dictionary containing the action plan.
        """
        logger.info(f"Generating action plan for {len(objectives)} objectives with {len(actions)} possible actions")
        
        # Validate inputs
        if not objectives:
            logger.error("No objectives provided")
            return {"error": "No objectives provided"}
        
        if not actions:
            logger.error("No actions provided")
            return {"error": "No actions provided"}
        
        # Set default constraints if not provided
        if constraints is None:
            constraints = {
                "max_actions": 10,
                "max_cost": float('inf'),
                "max_duration": float('inf')
            }
        
        # Calculate action impacts on objectives
        action_impacts = self._calculate_action_impacts(actions, objectives)
        
        # Generate action plan
        action_plan = self._generate_optimal_action_plan(actions, objectives, action_impacts, constraints)
        
        if not action_plan:
            logger.error("Failed to generate action plan")
            return {"error": "Failed to generate action plan"}
        
        # Calculate expected outcomes
        expected_outcomes = self._calculate_expected_outcomes(action_plan, objectives, action_impacts)
        
        # Prepare final result
        final_result = {
            "plan": action_plan,
            "expected_outcomes": expected_outcomes,
            "total_cost": sum(a["cost"] for a in action_plan),
            "total_duration": sum(a["duration"] for a in action_plan),
            "action_count": len(action_plan)
        }
        
        logger.info(f"Action plan generated with {len(action_plan)} actions")
        return final_result
    
    def _calculate_action_impacts(self, actions: List[Dict[str, Any]],
                                objectives: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """
        Calculate the impact of each action on each objective.
        
        Args:
            actions: List of possible actions.
            objectives: List of objectives to achieve.
            
        Returns:
            Dictionary mapping action IDs to dictionaries of objective impacts.
        """
        action_impacts = {}
        
        for action in actions:
            action_id = action["id"]
            action_impacts[action_id] = {}
            
            # Get explicit impacts if defined
            explicit_impacts = action.get("impacts", {})
            
            for objective in objectives:
                objective_id = objective["id"]
                
                # Use explicit impact if available
                if objective_id in explicit_impacts:
                    action_impacts[action_id][objective_id] = explicit_impacts[objective_id]
                else:
                    # Calculate impact based on relevance
                    action_categories = set(action.get("categories", []))
                    objective_categories = set(objective.get("categories", []))
                    
                    # Calculate overlap between action and objective categories
                    category_overlap = len(action_categories.intersection(objective_categories))
                    
                    if category_overlap > 0:
                        # More overlap means higher impact
                        impact = 0.2 * category_overlap
                    else:
                        impact = 0.0
                    
                    action_impacts[action_id][objective_id] = impact
        
        return action_impacts
    
    def _generate_optimal_action_plan(self, actions: List[Dict[str, Any]],
                                    objectives: List[Dict[str, Any]],
                                    action_impacts: Dict[str, Dict[str, float]],
                                    constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate an optimal action plan using a greedy algorithm.
        
        Args:
            actions: List of possible actions.
            objectives: List of objectives to achieve.
            action_impacts: Dictionary of action impacts on objectives.
            constraints: Constraints on the action plan.
            
        Returns:
            List of actions in the optimal plan.
        """
        # Extract constraints
        max_actions = constraints.get("max_actions", 10)
        max_cost = constraints.get("max_cost", float('inf'))
        max_duration = constraints.get("max_duration", float('inf'))
        
        # Calculate objective weights
        objective_weights = {}
        for objective in objectives:
            objective_weights[objective["id"]] = objective.get("weight", 1.0)
        
        # Calculate action effectiveness (weighted impact across all objectives)
        action_effectiveness = {}
        for action in actions:
            action_id = action["id"]
            effectiveness = 0
            
            for objective_id, weight in objective_weights.items():
                impact = action_impacts[action_id].get(objective_id, 0)
                effectiveness += impact * weight
            
            # Normalize by cost and duration
            cost = action.get("cost", 0)
            duration = action.get("duration", 0)
            
            if cost > 0 and duration > 0:
                normalized_effectiveness = effectiveness / (cost * duration)
            elif cost > 0:
                normalized_effectiveness = effectiveness / cost
            elif duration > 0:
                normalized_effectiveness = effectiveness / duration
            else:
                normalized_effectiveness = effectiveness
            
            action_effectiveness[action_id] = normalized_effectiveness
        
        # Sort actions by effectiveness (descending)
        sorted_actions = sorted(actions, key=lambda x: action_effectiveness[x["id"]], reverse=True)
        
        # Generate plan using greedy algorithm
        plan = []
        total_cost = 0
        total_duration = 0
        selected_action_ids = set()
        
        for action in sorted_actions:
            action_id = action["id"]
            
            # Skip if action already in plan
            if action_id in selected_action_ids:
                continue
            
            # Check constraints
            if len(plan) >= max_actions:
                break
            
            cost = action.get("cost", 0)
            if total_cost + cost > max_cost:
                continue
            
            duration = action.get("duration", 0)
            if total_duration + duration > max_duration:
                continue
            
            # Add action to plan
            plan.append(action)
            selected_action_ids.add(action_id)
            total_cost += cost
            total_duration += duration
        
        # Sort plan by priority and dependencies
        sorted_plan = self._sort_plan_by_dependencies(plan)
        
        return sorted_plan
    
    def _sort_plan_by_dependencies(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort the action plan based on dependencies and priorities.
        
        Args:
            plan: List of actions in the plan.
            
        Returns:
            Sorted list of actions.
        """
        # Create dependency graph
        dependency_graph = {}
        for action in plan:
            action_id = action["id"]
            dependencies = action.get("dependencies", [])
            dependency_graph[action_id] = dependencies
        
        # Topological sort
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(action_id):
            if action_id in temp_visited:
                # Cyclic dependency, break it
                return
            
            if action_id in visited:
                return
            
            temp_visited.add(action_id)
            
            for dependency in dependency_graph.get(action_id, []):
                if dependency in dependency_graph:
                    visit(dependency)
            
            temp_visited.remove(action_id)
            visited.add(action_id)
            order.append(action_id)
        
        for action in plan:
            if action["id"] not in visited:
                visit(action["id"])
        
        # Reverse to get correct order
        order.reverse()
        
        # Create sorted plan
        action_map = {action["id"]: action for action in plan}
        sorted_plan = [action_map[action_id] for action_id in order if action_id in action_map]
        
        return sorted_plan
    
    def _calculate_expected_outcomes(self, plan: List[Dict[str, Any]],
                                   objectives: List[Dict[str, Any]],
                                   action_impacts: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Calculate expected outcomes for each objective based on the action plan.
        
        Args:
            plan: List of actions in the plan.
            objectives: List of objectives to achieve.
            action_impacts: Dictionary of action impacts on objectives.
            
        Returns:
            Dictionary mapping objective IDs to expected outcomes.
        """
        expected_outcomes = {}
        
        for objective in objectives:
            objective_id = objective["id"]
            baseline = objective.get("baseline", 0)
            target = objective.get("target", 100)
            
            # Calculate total impact
            total_impact = 0
            for action in plan:
                action_id = action["id"]
                impact = action_impacts[action_id].get(objective_id, 0)
                total_impact += impact
            
            # Calculate expected outcome
            # Impact of 1.0 means reaching the target
            expected_value = baseline + total_impact * (target - baseline)
            
            # Ensure outcome is between baseline and target
            expected_value = max(baseline, min(target, expected_value))
            
            expected_outcomes[objective_id] = expected_value
        
        return expected_outcomes
    
    def assess_recommendation_impact(self, recommendation: Dict[str, Any],
                                   historical_data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
                                   target_metrics: List[str]) -> Dict[str, Any]:
        """
        Assess the potential impact of a recommendation.
        
        Args:
            recommendation: Dictionary describing the recommendation.
            historical_data: Historical data as DataFrame or dictionary/list of dictionaries.
            target_metrics: List of metrics to assess impact on.
            
        Returns:
            A dictionary containing impact assessment results.
        """
        logger.info(f"Assessing impact of recommendation: {recommendation.get('name', 'unnamed')}")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(historical_data)
        
        # Validate inputs
        if not target_metrics:
            logger.error("No target metrics provided")
            return {"error": "No target metrics provided"}
        
        # Check if target metrics exist in data
        missing_metrics = [m for m in target_metrics if m not in df.columns]
        if missing_metrics:
            logger.error(f"Target metrics {missing_metrics} not found in data")
            return {"error": f"Target metrics {missing_metrics} not found in data"}
        
        # Extract recommendation parameters
        recommendation_type = recommendation.get("type", "unknown")
        expected_effects = recommendation.get("expected_effects", {})
        
        # Calculate baseline metrics
        baseline_metrics = {}
        for metric in target_metrics:
            if pd.api.types.is_numeric_dtype(df[metric]):
                baseline_metrics[metric] = {
                    "mean": df[metric].mean(),
                    "median": df[metric].median(),
                    "std": df[metric].std(),
                    "min": df[metric].min(),
                    "max": df[metric].max()
                }
        
        # Calculate expected impact
        impact_assessment = {}
        
        for metric in target_metrics:
            if metric in baseline_metrics:
                # Get baseline
                baseline = baseline_metrics[metric]["mean"]
                
                # Get expected effect
                if metric in expected_effects:
                    effect = expected_effects[metric]
                else:
                    # Estimate effect based on recommendation type
                    effect = self._estimate_effect(recommendation_type, metric)
                
                # Calculate expected value
                expected_value = baseline * (1 + effect)
                
                # Calculate percent change
                percent_change = effect * 100
                
                # Determine confidence level based on specificity of effect
                if metric in expected_effects:
                    confidence = 0.8  # Higher confidence for explicitly specified effects
                else:
                    confidence = 0.5  # Lower confidence for estimated effects
                
                impact_assessment[metric] = {
                    "baseline": baseline,
                    "expected_value": expected_value,
                    "absolute_change": expected_value - baseline,
                    "percent_change": percent_change,
                    "confidence": confidence
                }
        
        # Calculate overall impact score
        if impact_assessment:
            # Average percent change across all metrics
            avg_percent_change = np.mean([abs(impact["percent_change"]) for impact in impact_assessment.values()])
            
            # Average confidence across all metrics
            avg_confidence = np.mean([impact["confidence"] for impact in impact_assessment.values()])
            
            # Overall impact score (percent change * confidence)
            overall_impact_score = avg_percent_change * avg_confidence / 100
        else:
            avg_percent_change = 0
            avg_confidence = 0
            overall_impact_score = 0
        
        # Prepare final result
        final_result = {
            "recommendation": recommendation.get("name", "unnamed"),
            "type": recommendation_type,
            "baseline_metrics": baseline_metrics,
            "impact_assessment": impact_assessment,
            "overall_impact": {
                "avg_percent_change": avg_percent_change,
                "avg_confidence": avg_confidence,
                "impact_score": overall_impact_score
            }
        }
        
        logger.info(f"Impact assessment completed with overall score: {overall_impact_score:.2f}")
        return final_result
    
    def _estimate_effect(self, recommendation_type: str, metric: str) -> float:
        """
        Estimate the effect of a recommendation on a metric based on type.
        
        Args:
            recommendation_type: Type of recommendation.
            metric: Target metric.
            
        Returns:
            Estimated effect as a decimal (e.g., 0.05 for 5% increase).
        """
        # Define typical effects for different recommendation types and metrics
        typical_effects = {
            "pricing_optimization": {
                "revenue": 0.05,
                "profit": 0.07,
                "sales_volume": -0.02,
                "conversion_rate": 0.03
            },
            "marketing_campaign": {
                "revenue": 0.08,
                "customer_acquisition": 0.15,
                "website_traffic": 0.20,
                "conversion_rate": 0.05
            },
            "cost_reduction": {
                "expenses": -0.10,
                "profit": 0.05,
                "operational_efficiency": 0.08
            },
            "product_improvement": {
                "customer_satisfaction": 0.12,
                "retention_rate": 0.08,
                "revenue": 0.04
            },
            "process_optimization": {
                "operational_efficiency": 0.15,
                "processing_time": -0.20,
                "error_rate": -0.25
            }
        }
        
        # Get effect for recommendation type and metric
        if recommendation_type in typical_effects and metric in typical_effects[recommendation_type]:
            return typical_effects[recommendation_type][metric]
        
        # Default effects for common metrics
        default_effects = {
            "revenue": 0.03,
            "profit": 0.03,
            "sales_volume": 0.03,
            "customer_satisfaction": 0.05,
            "conversion_rate": 0.02,
            "retention_rate": 0.02,
            "expenses": -0.03,
            "error_rate": -0.05,
            "processing_time": -0.05
        }
        
        # Return default effect for metric if available
        if metric in default_effects:
            return default_effects[metric]
        
        # Default small positive effect
        return 0.01
    
    def prioritize_recommendations(self, recommendations: List[Dict[str, Any]],
                                 historical_data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
                                 target_metrics: List[str],
                                 constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Prioritize recommendations based on impact, cost, and feasibility.
        
        Args:
            recommendations: List of recommendations to prioritize.
            historical_data: Historical data as DataFrame or dictionary/list of dictionaries.
            target_metrics: List of metrics to assess impact on.
            constraints: Optional constraints on implementation.
            
        Returns:
            A dictionary containing prioritized recommendations.
        """
        logger.info(f"Prioritizing {len(recommendations)} recommendations")
        
        # Validate inputs
        if not recommendations:
            logger.error("No recommendations provided")
            return {"error": "No recommendations provided"}
        
        # Set default constraints if not provided
        if constraints is None:
            constraints = {
                "max_budget": float('inf'),
                "max_time": float('inf'),
                "max_recommendations": 5
            }
        
        # Assess impact of each recommendation
        impact_assessments = []
        
        for recommendation in recommendations:
            assessment = self.assess_recommendation_impact(recommendation, historical_data, target_metrics)
            
            if "error" not in assessment:
                impact_assessments.append({
                    "recommendation": recommendation,
                    "assessment": assessment
                })
        
        # Calculate priority score for each recommendation
        prioritized_recommendations = []
        
        for item in impact_assessments:
            recommendation = item["recommendation"]
            assessment = item["assessment"]
            
            # Extract parameters
            impact_score = assessment["overall_impact"]["impact_score"]
            cost = recommendation.get("cost", 0)
            time_to_implement = recommendation.get("time_to_implement", 0)
            feasibility = recommendation.get("feasibility", 0.5)
            
            # Calculate priority score
            # Higher impact, lower cost, lower time, higher feasibility = higher score
            if cost > 0:
                cost_factor = 1 / cost
            else:
                cost_factor = 1.0
            
            if time_to_implement > 0:
                time_factor = 1 / time_to_implement
            else:
                time_factor = 1.0
            
            priority_score = impact_score * cost_factor * time_factor * feasibility
            
            prioritized_recommendations.append({
                "recommendation": recommendation["name"],
                "description": recommendation.get("description", ""),
                "type": recommendation.get("type", "unknown"),
                "impact_score": impact_score,
                "cost": cost,
                "time_to_implement": time_to_implement,
                "feasibility": feasibility,
                "priority_score": priority_score,
                "expected_effects": assessment["impact_assessment"]
            })
        
        # Sort by priority score (descending)
        prioritized_recommendations.sort(key=lambda x: x["priority_score"], reverse=True)
        
        # Apply constraints
        max_budget = constraints.get("max_budget", float('inf'))
        max_time = constraints.get("max_time", float('inf'))
        max_recommendations = constraints.get("max_recommendations", 5)
        
        filtered_recommendations = []
        total_cost = 0
        max_time_used = 0
        
        for rec in prioritized_recommendations:
            # Check budget constraint
            if total_cost + rec["cost"] > max_budget:
                continue
            
            # Check time constraint (assuming recommendations can be implemented in parallel)
            if rec["time_to_implement"] > max_time:
                continue
            
            # Add recommendation
            filtered_recommendations.append(rec)
            total_cost += rec["cost"]
            max_time_used = max(max_time_used, rec["time_to_implement"])
            
            # Check max recommendations constraint
            if len(filtered_recommendations) >= max_recommendations:
                break
        
        # Prepare implementation plan
        implementation_plan = []
        
        for i, rec in enumerate(filtered_recommendations):
            implementation_plan.append({
                "step": i + 1,
                "recommendation": rec["recommendation"],
                "description": rec["description"],
                "time_to_implement": rec["time_to_implement"],
                "cost": rec["cost"],
                "expected_impact": {
                    metric: details["percent_change"] 
                    for metric, details in rec["expected_effects"].items()
                }
            })
        
        # Prepare final result
        final_result = {
            "prioritized_recommendations": filtered_recommendations,
            "implementation_plan": implementation_plan,
            "total_cost": total_cost,
            "estimated_implementation_time": max_time_used,
            "recommendation_count": len(filtered_recommendations)
        }
        
        logger.info(f"Prioritization completed with {len(filtered_recommendations)} recommendations")
        return final_result
    
    def analyze(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
               objectives: List[Dict[str, Any]],
               possible_actions: List[Dict[str, Any]],
               constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform a comprehensive prescriptive analysis.
        
        Args:
            data: Historical data as DataFrame or dictionary/list of dictionaries.
            objectives: List of objectives to achieve.
            possible_actions: List of possible actions.
            constraints: Optional constraints on implementation.
            
        Returns:
            A dictionary containing the analysis results.
        """
        logger.info("Performing comprehensive prescriptive analysis")
        
        # Convert to DataFrame if necessary
        df = self._ensure_dataframe(data)
        
        # Validate inputs
        if not objectives:
            logger.error("No objectives provided")
            return {"error": "No objectives provided"}
        
        if not possible_actions:
            logger.error("No possible actions provided")
            return {"error": "No possible actions provided"}
        
        # Set default constraints if not provided
        if constraints is None:
            constraints = {
                "max_budget": float('inf'),
                "max_time": float('inf'),
                "max_actions": 10,
                "max_recommendations": 5
            }
        
        # Generate action plan
        action_plan = self.generate_action_plan(objectives, possible_actions, constraints)
        
        # Extract target metrics from objectives
        target_metrics = []
        for objective in objectives:
            if "metric" in objective:
                target_metrics.append(objective["metric"])
        
        # Convert actions to recommendations
        recommendations = []
        for action in possible_actions:
            recommendation = {
                "name": action.get("name", action.get("id", "unnamed")),
                "description": action.get("description", ""),
                "type": action.get("type", "unknown"),
                "cost": action.get("cost", 0),
                "time_to_implement": action.get("duration", 0),
                "feasibility": action.get("feasibility", 0.5),
                "expected_effects": action.get("impacts", {})
            }
            recommendations.append(recommendation)
        
        # Prioritize recommendations
        prioritized_recommendations = self.prioritize_recommendations(
            recommendations, df, target_metrics, constraints
        )
        
        # Prepare final result
        final_result = {
            "action_plan": action_plan,
            "prioritized_recommendations": prioritized_recommendations
        }
        
        logger.info("Comprehensive prescriptive analysis completed")
        return final_result
    
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
