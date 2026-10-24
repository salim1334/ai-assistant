"""
Model Selector Module

This module contains the ModelSelector class, which selects appropriate AI models
based on business profile and hardware capabilities.
"""

import logging
from typing import Dict, Any, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelSelector:
    """
    The ModelSelector selects appropriate AI models based on business profile and hardware capabilities.
    
    It considers the business type, analytics domains, and available hardware resources
    to select the most appropriate models for each domain.
    """
    
    def __init__(self, config: Dict[str, Any] = None, hardware_manager = None):
        """
        Initialize the ModelSelector.
        
        Args:
            config: Configuration parameters for the model selector.
            hardware_manager: Instance of HardwareManager for hardware capability detection.
        """
        self.config = config or {}
        self.hardware_manager = hardware_manager
        logger.info("Initializing ModelSelector")
        
        # Load model registry
        self.model_registry = self._load_model_registry()
        
        # Load domain-specific model requirements
        self.domain_requirements = self._load_domain_requirements()
        
        # Load industry-specific model preferences
        self.industry_preferences = self._load_industry_preferences()
        
        logger.info("ModelSelector initialized successfully")
    
    def _load_model_registry(self) -> Dict[str, Any]:
        """
        Load the model registry containing available models and their characteristics.
        
        Returns:
            A dictionary mapping model names to their characteristics.
        """
        # In a real implementation, this would load from a file or database
        return {
            "qwen35_4b": {
                "name": "Qwen 2.5 / 3.5 small (local Ollama)",
                "size": "small",
                "parameters": "1.5B-4B",
                "ram_required": 4,
                "disk_required": 3,
                "backend": "local",
                "capabilities": ["text_generation", "reasoning", "instruction_following"],
                "quantization_options": ["4bit", "8bit"],
                "strengths": ["local_privacy", "low_resource_usage", "offline"],
                "weaknesses": ["specialized_knowledge"]
            },
            "tinyllama": {
                "name": "TinyLlama",
                "size": "small",
                "parameters": "1.1B",
                "ram_required": 2,  # GB
                "disk_required": 1,  # GB
                "capabilities": ["text_generation", "basic_reasoning"],
                "quantization_options": ["4bit", "8bit"],
                "strengths": ["efficiency", "low_resource_usage"],
                "weaknesses": ["complex_reasoning", "specialized_knowledge"]
            },
            "phi2": {
                "name": "Phi-2",
                "size": "small",
                "parameters": "2.7B",
                "ram_required": 4,  # GB
                "disk_required": 2,  # GB
                "capabilities": ["text_generation", "reasoning", "code_generation"],
                "quantization_options": ["4bit", "8bit"],
                "strengths": ["efficiency", "reasoning"],
                "weaknesses": ["specialized_knowledge"]
            },
            "mistral7b": {
                "name": "Mistral-7B",
                "size": "medium",
                "parameters": "7B",
                "ram_required": 8,  # GB
                "disk_required": 4,  # GB
                "capabilities": ["text_generation", "reasoning", "instruction_following"],
                "quantization_options": ["4bit", "8bit", "16bit"],
                "strengths": ["reasoning", "instruction_following"],
                "weaknesses": ["resource_usage"]
            },
            "llama3": {
                "name": "Llama-3",
                "size": "large",
                "parameters": "8B",
                "ram_required": 16,  # GB
                "disk_required": 8,  # GB
                "capabilities": ["text_generation", "reasoning", "instruction_following", "specialized_knowledge"],
                "quantization_options": ["4bit", "8bit", "16bit"],
                "strengths": ["reasoning", "instruction_following", "knowledge"],
                "weaknesses": ["resource_usage"]
            },
            "mixtral": {
                "name": "Mixtral-8x7B",
                "size": "xlarge",
                "parameters": "47B",
                "ram_required": 32,  # GB
                "disk_required": 24,  # GB
                "capabilities": ["text_generation", "reasoning", "instruction_following", "specialized_knowledge", "complex_reasoning"],
                "quantization_options": ["4bit", "8bit"],
                "strengths": ["reasoning", "instruction_following", "knowledge", "complex_reasoning"],
                "weaknesses": ["resource_usage", "speed"]
            },
            "openai": {
                "name": "OpenAI (cloud API)",
                "size": "cloud",
                "parameters": "api",
                "ram_required": 0,
                "disk_required": 0,
                "backend": "openai",
                "capabilities": ["text_generation", "reasoning", "instruction_following", "specialized_knowledge", "complex_reasoning"],
                "quantization_options": [],
                "strengths": ["quality", "no_local_ram"],
                "weaknesses": ["requires_key", "online"]
            },
            "anthropic": {
                "name": "Anthropic Claude (cloud API)",
                "size": "cloud",
                "parameters": "api",
                "ram_required": 0,
                "disk_required": 0,
                "backend": "anthropic",
                "capabilities": ["text_generation", "reasoning", "instruction_following", "specialized_knowledge", "complex_reasoning"],
                "quantization_options": [],
                "strengths": ["quality", "no_local_ram"],
                "weaknesses": ["requires_key", "online"]
            },
            "gemini": {
                "name": "Google Gemini (cloud API)",
                "size": "cloud",
                "parameters": "api",
                "ram_required": 0,
                "disk_required": 0,
                "backend": "gemini",
                "capabilities": ["text_generation", "reasoning", "instruction_following", "specialized_knowledge"],
                "quantization_options": [],
                "strengths": ["quality", "no_local_ram"],
                "weaknesses": ["requires_key", "online"]
            }
        }
    
    def _load_domain_requirements(self) -> Dict[str, Any]:
        """
        Load domain-specific model requirements.
        
        Returns:
            A dictionary mapping analytics domains to model requirements.
        """
        # In a real implementation, this would load from a file or database
        return {
            "descriptive": {
                "required_capabilities": ["text_generation"],
                "preferred_capabilities": ["specialized_knowledge"],
                "min_size": "small"
            },
            "diagnostic": {
                "required_capabilities": ["text_generation", "reasoning"],
                "preferred_capabilities": ["complex_reasoning"],
                "min_size": "medium"
            },
            "predictive": {
                "required_capabilities": ["text_generation", "reasoning"],
                "preferred_capabilities": ["specialized_knowledge"],
                "min_size": "medium"
            },
            "prescriptive": {
                "required_capabilities": ["text_generation", "reasoning", "instruction_following"],
                "preferred_capabilities": ["complex_reasoning"],
                "min_size": "medium"
            },
            "cognitive": {
                "required_capabilities": ["text_generation", "reasoning", "specialized_knowledge"],
                "preferred_capabilities": ["complex_reasoning"],
                "min_size": "large"
            }
        }
    
    def _load_industry_preferences(self) -> Dict[str, Any]:
        """
        Load industry-specific model preferences.
        
        Returns:
            A dictionary mapping industries to model preferences.
        """
        # In a real implementation, this would load from a file or database
        return {
            "retail": {
                "descriptive": ["mistral7b", "phi2"],
                "diagnostic": ["mistral7b", "llama3"],
                "predictive": ["llama3", "mistral7b"],
                "prescriptive": ["llama3", "mixtral"],
                "cognitive": ["mixtral", "llama3"]
            },
            "restaurant": {
                "descriptive": ["phi2", "mistral7b"],
                "diagnostic": ["mistral7b", "llama3"],
                "predictive": ["mistral7b", "llama3"],
                "prescriptive": ["llama3", "mistral7b"],
                "cognitive": ["llama3", "mixtral"]
            },
            "legal": {
                "descriptive": ["mistral7b", "llama3"],
                "diagnostic": ["llama3", "mixtral"],
                "predictive": ["llama3", "mixtral"],
                "prescriptive": ["mixtral", "llama3"],
                "cognitive": ["mixtral", "llama3"]
            },
            "manufacturing": {
                "descriptive": ["phi2", "mistral7b"],
                "diagnostic": ["mistral7b", "llama3"],
                "predictive": ["llama3", "mistral7b"],
                "prescriptive": ["llama3", "mixtral"],
                "cognitive": ["llama3", "mixtral"]
            },
            "healthcare": {
                "descriptive": ["mistral7b", "llama3"],
                "diagnostic": ["llama3", "mixtral"],
                "predictive": ["llama3", "mixtral"],
                "prescriptive": ["mixtral", "llama3"],
                "cognitive": ["mixtral", "llama3"]
            },
            "professional_services": {
                "descriptive": ["phi2", "mistral7b"],
                "diagnostic": ["mistral7b", "llama3"],
                "predictive": ["mistral7b", "llama3"],
                "prescriptive": ["llama3", "mistral7b"],
                "cognitive": ["llama3", "mixtral"]
            },
            "ecommerce": {
                "descriptive": ["phi2", "mistral7b"],
                "diagnostic": ["mistral7b", "llama3"],
                "predictive": ["llama3", "mistral7b"],
                "prescriptive": ["llama3", "mixtral"],
                "cognitive": ["mixtral", "llama3"]
            },
            "fmcg_distribution": {
                "descriptive": ["qwen35_4b", "phi2", "mistral7b"],
                "diagnostic": ["mistral7b", "qwen35_4b"],
                "predictive": ["mistral7b", "llama3"],
                "prescriptive": ["llama3", "mistral7b"],
                "cognitive": ["llama3", "mistral7b"]
            }
        }
    
    def _get_size_rank(self, size: str) -> int:
        """
        Get the numerical rank of a model size.
        
        Args:
            size: The model size (small, medium, large, xlarge).
            
        Returns:
            The numerical rank of the size.
        """
        size_ranks = {
            "small": 1,
            "medium": 2,
            "large": 3,
            "xlarge": 4
        }
        return size_ranks.get(size.lower(), 0)
    
    def _model_meets_requirements(self, model_data: Dict[str, Any], requirements: Dict[str, Any]) -> bool:
        """
        Check if a model meets the specified requirements.
        
        Args:
            model_data: The model data from the registry.
            requirements: The requirements to check against.
            
        Returns:
            True if the model meets the requirements, False otherwise.
        """
        # Check required capabilities
        for capability in requirements.get("required_capabilities", []):
            if capability not in model_data.get("capabilities", []):
                return False
        
        # Check minimum size
        min_size = requirements.get("min_size", "small")
        if self._get_size_rank(model_data.get("size", "small")) < self._get_size_rank(min_size):
            return False
        
        return True
    
    def _score_model(self, model_name: str, model_data: Dict[str, Any], 
                    requirements: Dict[str, Any], hardware_info: Dict[str, Any],
                    preferred_models: List[str]) -> float:
        """
        Score a model based on how well it meets requirements and hardware constraints.
        
        Args:
            model_name: The name of the model.
            model_data: The model data from the registry.
            requirements: The domain requirements.
            hardware_info: Information about available hardware.
            preferred_models: List of preferred models for this domain and industry.
            
        Returns:
            A score representing how suitable the model is (higher is better).
        """
        score = 0.0
        
        # Base score for meeting requirements
        if self._model_meets_requirements(model_data, requirements):
            score += 50.0
        else:
            return 0.0  # Model doesn't meet basic requirements
        
        # Score for preferred capabilities
        for capability in requirements.get("preferred_capabilities", []):
            if capability in model_data.get("capabilities", []):
                score += 10.0
        
        # Score for hardware compatibility
        available_ram = hardware_info.get("ram", 0)
        required_ram = model_data.get("ram_required", 0)
        
        if required_ram <= available_ram:
            score += 20.0
        elif required_ram * 0.5 <= available_ram:  # Can run with quantization
            score += 10.0
        else:
            score -= 30.0  # Significant penalty for not fitting in RAM
        
        # Score for being a preferred model
        if model_name in preferred_models:
            score += 15.0 * (len(preferred_models) - preferred_models.index(model_name))
        
        # Adjust score based on quantization options if RAM is limited
        if required_ram > available_ram * 0.8:
            if "4bit" in model_data.get("quantization_options", []):
                score += 5.0
            if "8bit" in model_data.get("quantization_options", []):
                score += 3.0
        
        return score
    
    def select_model_for_domain(self, domain: str, business_profile: Dict[str, Any], 
                               hardware_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select the most appropriate model for a specific analytics domain.
        
        Args:
            domain: The analytics domain (descriptive, diagnostic, predictive, prescriptive, cognitive).
            business_profile: The business profile.
            hardware_info: Information about available hardware.
            
        Returns:
            A dictionary containing the selected model and configuration.
        """
        logger.info(f"Selecting model for {domain} analytics domain")
        
        # Get domain requirements
        requirements = self.domain_requirements.get(domain, {})
        
        # Get industry preferences
        industry_code = business_profile.get("industry", {}).get("code", "retail")
        preferred_models = self.industry_preferences.get(industry_code, {}).get(domain, [])
        
        # Score each model
        model_scores = {}
        for model_name, model_data in self.model_registry.items():
            if model_data.get("backend") in ("openai", "anthropic", "gemini") or model_data.get("size") == "cloud":
                continue
            score = self._score_model(model_name, model_data, requirements, hardware_info, preferred_models)
            model_scores[model_name] = score
        
        # Select the highest scoring model
        selected_model = max(model_scores.items(), key=lambda x: x[1], default=(None, 0))
        
        if selected_model[0] is None or selected_model[1] == 0:
            logger.warning(f"No suitable model found for {domain} analytics domain, using fallback")
            # Fallback to the smallest model that meets requirements
            for model_name, model_data in sorted(self.model_registry.items(), 
                                               key=lambda x: x[1].get("ram_required", 0)):
                if self._model_meets_requirements(model_data, requirements):
                    selected_model = (model_name, 0)
                    break
        
        # If still no model found, use the smallest available model
        if selected_model[0] is None:
            logger.warning(f"No model meets requirements for {domain} analytics domain, using smallest model")
            selected_model = min(self.model_registry.items(), 
                               key=lambda x: x[1].get("ram_required", float('inf')))
            selected_model = (selected_model[0], 0)
        
        # Determine if quantization is needed
        model_data = self.model_registry.get(selected_model[0], {})
        required_ram = model_data.get("ram_required", 0)
        available_ram = hardware_info.get("ram", 0)
        
        quantization = None
        if required_ram > available_ram:
            # Need quantization
            quantization_options = model_data.get("quantization_options", [])
            if "4bit" in quantization_options:
                quantization = "4bit"
            elif "8bit" in quantization_options:
                quantization = "8bit"
        
        logger.info(f"Selected {model_data.get('name', selected_model[0])} for {domain} analytics domain" + 
                   (f" with {quantization} quantization" if quantization else ""))
        
        return {
            "model_name": selected_model[0],
            "model_data": model_data,
            "quantization": quantization,
            "score": selected_model[1]
        }
    
    def select_models(self, business_profile: Dict[str, Any], hardware_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select appropriate models for all analytics domains based on business profile and hardware.
        
        Args:
            business_profile: The business profile.
            hardware_info: Information about available hardware.
            
        Returns:
            A dictionary mapping analytics domains to selected models.
        """
        logger.info("Selecting models for all analytics domains")
        
        # Get hardware info from hardware manager if available
        if hardware_info is None and self.hardware_manager is not None:
            hardware_info = self.hardware_manager.get_hardware_info()
        
        # Default hardware info if not provided
        if hardware_info is None:
            logger.warning("No hardware info provided, using default values")
            hardware_info = {
                "ram": 8,  # GB
                "disk": 20,  # GB
                "cpu_cores": 4,
                "gpu": False
            }
        
        # Select models for each domain
        selected_models = {}
        for domain in self.domain_requirements.keys():
            selected_models[domain] = self.select_model_for_domain(domain, business_profile, hardware_info)
        
        return selected_models
    
    def get_model_config(self, model_selection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the configuration for a selected model.
        
        Args:
            model_selection: The model selection from select_model_for_domain.
            
        Returns:
            A dictionary containing the model configuration.
        """
        model_name = model_selection.get("model_name")
        model_data = model_selection.get("model_data", {})
        quantization = model_selection.get("quantization")
        
        config = {
            "model_name": model_name,
            "model_path": f"models/{model_name}",
            "parameters": model_data.get("parameters"),
            "size": model_data.get("size"),
            "capabilities": model_data.get("capabilities", []),
            "strengths": model_data.get("strengths", []),
            "weaknesses": model_data.get("weaknesses", [])
        }
        
        if quantization:
            config["quantization"] = quantization
            config["model_path"] += f"_{quantization}"
        
        return config
    
    def get_fallback_chain(self, domain: str, business_profile: Dict[str, Any]) -> List[str]:
        """
        Get a fallback chain of models for a specific domain.
        
        Args:
            domain: The analytics domain.
            business_profile: The business profile.
            
        Returns:
            A list of model names in fallback order.
        """
        industry_code = business_profile.get("industry", {}).get("code", "retail")
        preferred_models = self.industry_preferences.get(industry_code, {}).get(domain, [])
        
        # Start with preferred models
        fallback_chain = preferred_models.copy()
        
        # Add other models that meet requirements
        requirements = self.domain_requirements.get(domain, {})
        for model_name, model_data in self.model_registry.items():
            if model_name not in fallback_chain and self._model_meets_requirements(model_data, requirements):
                fallback_chain.append(model_name)
        
        # Add remaining models as last resort
        for model_name in self.model_registry.keys():
            if model_name not in fallback_chain:
                fallback_chain.append(model_name)
        
        return fallback_chain
