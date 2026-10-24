"""
Framework Controller Module

This module contains the FrameworkController class, which orchestrates the entire BDFG process,
from business profiling to agent framework generation and packaging.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

# Import core components
from enhanced_bdfg.core.business_profiler.profiler import BusinessProfiler
from enhanced_bdfg.core.model_selector.selector import ModelSelector
from enhanced_bdfg.core.agent_generator.generator import AgentGenerator
from enhanced_bdfg.core.resource_manager.manager import ResourceManager
from enhanced_bdfg.core.hardware_manager.manager import HardwareManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FrameworkController:
    """
    The FrameworkController orchestrates the entire BDFG process.
    
    It coordinates the interaction between the BusinessProfiler, ModelSelector,
    AgentGenerator, ResourceManager, and HardwareManager to create a customized
    agent framework for a specific business.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the FrameworkController.
        
        Args:
            config_path: Optional path to a configuration file.
        """
        self.config = self._load_config(config_path)
        logger.info("Initializing FrameworkController")
        
        # Initialize core components
        self.business_profiler = BusinessProfiler(self.config.get('business_profiler', {}))
        self.hardware_manager = HardwareManager(self.config.get('hardware_manager', {}))
        self.resource_manager = ResourceManager(self.config.get('resource_manager', {}))
        self.model_selector = ModelSelector(self.config.get('model_selector', {}), self.hardware_manager)
        self.agent_generator = AgentGenerator(self.config.get('agent_generator', {}))
        
        logger.info("FrameworkController initialized successfully")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from a file or use default configuration.
        
        Args:
            config_path: Path to a configuration file.
            
        Returns:
            A dictionary containing configuration parameters.
        """
        default_config = {
            'business_profiler': {},
            'model_selector': {},
            'agent_generator': {},
            'resource_manager': {},
            'hardware_manager': {}
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Configuration loaded from {config_path}")
                return {**default_config, **config}
            except Exception as e:
                logger.error(f"Error loading configuration from {config_path}: {e}")
                logger.info("Using default configuration")
                return default_config
        else:
            logger.info("Using default configuration")
            return default_config
    
    def create_business_profile(self, business_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a business profile using the BusinessProfiler.
        
        Args:
            business_info: Dictionary containing basic business information.
            
        Returns:
            A comprehensive business profile.
        """
        logger.info("Creating business profile")
        if hasattr(self.business_profiler, "create_profile_from_info") and isinstance(business_info, dict):
            profile = self.business_profiler.create_profile_from_info(business_info)
        else:
            profile = self.business_profiler.create_profile(business_info)
        logger.info("Business profile created successfully")
        return profile
    
    def select_models(self, business_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select appropriate models based on the business profile and hardware capabilities.
        
        Args:
            business_profile: The business profile.
            
        Returns:
            A dictionary mapping analytics domains to selected models.
        """
        logger.info("Selecting models based on business profile and hardware capabilities")
        hardware_info = self.hardware_manager.detect_hardware()
        models = self.model_selector.select_models(business_profile, hardware_info)
        logger.info(f"Selected models: {models}")
        return models
    
    def generate_agent_framework(self, business_profile: Dict[str, Any], 
                                selected_models: Dict[str, Any], output_dir: str,
                                deployment_type: str = "local") -> str:
        """
        Generate a customized agent framework for the business.
        
        Args:
            business_profile: The business profile.
            selected_models: The selected models for each analytics domain.
            output_dir: Directory to output the generated framework.
            deployment_type: Type of deployment (local or cloud).
            
        Returns:
            Path to the generated framework directory.
        """
        logger.info("Generating agent framework")
        
        # Convert model selections to model configs
        model_configs = {}
        for domain, model_selection in selected_models.items():
            model_configs[domain] = self.model_selector.get_model_config(model_selection)
        
        # Generate the framework
        framework_dir = self.agent_generator.generate_framework(
            business_profile, 
            model_configs, 
            output_dir,
            deployment_type
        )
        
        logger.info(f"Agent framework generated successfully at {framework_dir}")
        return framework_dir
    
    def package_framework(self, framework_dir: str, output_file: Optional[str] = None) -> str:
        """
        Package the generated framework for deployment.
        
        Args:
            framework_dir: Directory containing the generated framework.
            output_file: Optional path for the output package file.
            
        Returns:
            Path to the packaged framework.
        """
        logger.info(f"Packaging framework from {framework_dir}")
        package_path = self.agent_generator.package_framework(framework_dir, output_file)
        logger.info(f"Framework packaged successfully to {package_path}")
        return package_path
    
    def run(self, business_info: Dict[str, Any], output_dir: str, 
           deployment_type: str = "local", package: bool = True) -> str:
        """
        Run the entire BDFG process from business profiling to framework packaging.
        
        Args:
            business_info: Dictionary containing basic business information.
            output_dir: Directory where the framework will be generated.
            deployment_type: Type of deployment (local or cloud).
            package: Whether to package the framework after generation.
            
        Returns:
            Path to the generated framework or packaged framework.
        """
        logger.info("Starting BDFG process")
        
        # Create business profile
        profile = self.create_business_profile(business_info)
        
        # Select models
        models = self.select_models(profile)
        
        # Generate agent framework
        framework_dir = self.generate_agent_framework(profile, models, output_dir, deployment_type)
        
        # Package framework if requested
        if package:
            result_path = self.package_framework(framework_dir)
        else:
            result_path = framework_dir
        
        logger.info("BDFG process completed successfully")
        return result_path

    def implement_alarm_crm(self, output_dir: str, seed: bool = True) -> dict:
        """Generate a runnable Alarm CRM assistant package."""
        from enhanced_bdfg.runtime.implement import implement_alarm_crm
        return implement_alarm_crm(output_dir, seed=seed)
    
    def optimize_resource_usage(self, model_configs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Optimize resource usage for the selected models.
        
        Args:
            model_configs: The model configurations for each analytics domain.
            
        Returns:
            A dictionary containing optimized execution settings.
        """
        logger.info("Optimizing resource usage for selected models")
        
        # Get hardware information
        hardware_info = self.hardware_manager.detect_hardware()
        
        # Get resource constraints
        constraints = self.hardware_manager.get_resource_constraints()
        
        # Create execution plans for each model
        execution_plans = {}
        for domain, model_config in model_configs.items():
            execution_plans[domain] = self.resource_manager.get_execution_plan(model_config, hardware_info)
        
        # Create overall resource optimization plan
        optimization_plan = {
            "execution_plans": execution_plans,
            "resource_constraints": constraints,
            "hardware_info": hardware_info,
            "recommendations": {
                "batch_processing": constraints["available_ram"] > 8,
                "quantization": constraints["available_ram"] < 16,
                "offloading": constraints["available_ram"] < 8,
                "use_gpu": constraints["can_use_gpu"]
            }
        }
        
        logger.info("Resource usage optimization completed")
        return optimization_plan
    
    def validate_framework(self, framework_dir: str) -> Dict[str, Any]:
        """
        Validate a generated framework to ensure it meets requirements.
        
        Args:
            framework_dir: Directory containing the generated framework.
            
        Returns:
            A dictionary containing validation results.
        """
        logger.info(f"Validating framework at {framework_dir}")
        
        validation_results = {
            "valid": True,
            "issues": [],
            "components": {}
        }
        
        # Check if directory exists
        if not os.path.exists(framework_dir):
            validation_results["valid"] = False
            validation_results["issues"].append(f"Framework directory {framework_dir} does not exist")
            return validation_results
        
        # Check for required files and directories
        required_files = ["requirements.txt", "README.md", "setup.py", "__init__.py"]
        required_dirs = ["agents", "knowledge", "data", "models", "tools"]
        
        for file in required_files:
            file_path = os.path.join(framework_dir, file)
            if not os.path.exists(file_path):
                validation_results["valid"] = False
                validation_results["issues"].append(f"Required file {file} is missing")
        
        for dir_name in required_dirs:
            dir_path = os.path.join(framework_dir, dir_name)
            if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
                validation_results["valid"] = False
                validation_results["issues"].append(f"Required directory {dir_name} is missing")
        
        # Check for agent implementations
        agent_domains = ["descriptive", "diagnostic", "predictive", "prescriptive", "cognitive"]
        validation_results["components"]["agents"] = {}
        
        for domain in agent_domains:
            agent_dir = os.path.join(framework_dir, "agents", domain)
            agent_config = os.path.join(agent_dir, "config.json")
            agent_impl = os.path.join(agent_dir, "agent.py")
            
            domain_valid = os.path.exists(agent_dir) and os.path.exists(agent_config) and os.path.exists(agent_impl)
            validation_results["components"]["agents"][domain] = domain_valid
            
            if not domain_valid:
                validation_results["valid"] = False
                validation_results["issues"].append(f"{domain.capitalize()} agent implementation is incomplete")
        
        # Check for entry points
        entry_points = ["cli.py", "app.py"]
        validation_results["components"]["entry_points"] = {}
        
        for entry_point in entry_points:
            entry_path = os.path.join(framework_dir, entry_point)
            entry_valid = os.path.exists(entry_path)
            validation_results["components"]["entry_points"][entry_point] = entry_valid
            
            if not entry_valid:
                validation_results["valid"] = False
                validation_results["issues"].append(f"Entry point {entry_point} is missing")
        
        logger.info(f"Framework validation completed: {'Valid' if validation_results['valid'] else 'Invalid'}")
        if not validation_results["valid"]:
            logger.warning(f"Validation issues: {validation_results['issues']}")
        
        return validation_results
