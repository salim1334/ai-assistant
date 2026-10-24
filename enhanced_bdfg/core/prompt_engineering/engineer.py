"""
Prompt Engineering Module

This module contains the PromptEngineer class, which creates and optimizes prompts
for different analytics domains and business types.
"""

import logging
import re
import json
from typing import Dict, Any, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PromptEngineer:
    """
    The PromptEngineer creates and optimizes prompts for different analytics domains.
    
    It handles prompt template management, customization based on business profiles,
    and optimization for different model types and sizes.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the PromptEngineer.
        
        Args:
            config: Configuration parameters for the prompt engineer.
        """
        self.config = config or {}
        logger.info("Initializing PromptEngineer")
        
        # Load base templates
        self.templates = self._load_templates()
        
        # Load domain-specific templates
        self.domain_templates = self._load_domain_templates()
        
        # Load industry-specific templates
        self.industry_templates = self._load_industry_templates()
        
        logger.info("PromptEngineer initialized successfully")
    
    def _load_templates(self) -> Dict[str, str]:
        """
        Load base prompt templates.
        
        Returns:
            A dictionary containing base prompt templates.
        """
        # In a real implementation, this would load from files
        return {
            "system": """You are an AI assistant specialized in {domain} analytics for {industry} businesses.
Your goal is to help {business_name} with {task_description}.
Use your expertise to provide valuable insights and recommendations.""",
            
            "user": """I need help with {task_description} for my {industry} business.
Here is the relevant data:
{data_placeholder}

Please analyze this information and provide {output_format}.""",
            
            "few_shot": """Example 1:
User: I need to understand our sales trends for the past quarter.
Data: [Sales data for Q1-Q3 2024]
Assistant: Based on your sales data, I've identified three key trends:
1. Weekend sales have increased by 15% compared to weekdays
2. Product category A has shown consistent growth of 5% month-over-month
3. There's a noticeable dip in sales during the second week of each month

Example 2:
User: How can we improve our customer retention?
Data: [Customer retention metrics for 2023-2024]
Assistant: After analyzing your customer retention data, I recommend:
1. Implementing a loyalty program targeting customers who haven't made a purchase in 30-45 days
2. Improving your onboarding process to address the 20% drop-off after first purchase
3. Creating personalized re-engagement campaigns for your high-value customers who have become inactive"""
        }
    
    def _load_domain_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Load domain-specific prompt templates.
        
        Returns:
            A dictionary containing domain-specific prompt templates.
        """
        # In a real implementation, this would load from files
        return {
            "descriptive": {
                "system": """You are a Descriptive Analytics Assistant for {business_name}, a {industry} business.
Your role is to analyze historical data to identify patterns and trends.
Focus on {key_metrics} that are critical for this business type.
When analyzing data, first summarize what you see, then identify patterns,
and finally highlight any anomalies or notable trends.""",
                
                "user": """I need to understand the patterns and trends in this data:
{data_placeholder}

Please provide a descriptive analysis focusing on {key_metrics}.
Include a summary of the data, key patterns you've identified, and any notable anomalies."""
            },
            
            "diagnostic": {
                "system": """You are a Diagnostic Analytics Assistant for {business_name}, a {industry} business.
Your role is to determine why certain events occurred by identifying root causes.
Focus on understanding the factors behind changes in {key_metrics}.
When diagnosing issues, first identify the specific problem, then analyze
potential causes, and finally determine the most likely explanation with
supporting evidence.""",
                
                "user": """We've noticed the following issue with our {key_metrics}:
{data_placeholder}

Please diagnose the root cause of this issue.
Include your analysis of potential causes and determine the most likely explanation
with supporting evidence from the data."""
            },
            
            "predictive": {
                "system": """You are a Predictive Analytics Assistant for {business_name}, a {industry} business.
Your role is to forecast future trends and outcomes based on historical data.
Focus on predicting future values of {key_metrics} that are critical for business planning.
When making predictions, first analyze historical patterns, then identify
relevant external factors, and finally provide forecasts with confidence levels
and potential scenarios.""",
                
                "user": """Based on this historical data:
{data_placeholder}

Please forecast the future trends for our {key_metrics} over the next {time_period}.
Include your analysis of historical patterns, relevant external factors,
and provide forecasts with confidence levels and potential scenarios."""
            },
            
            "prescriptive": {
                "system": """You are a Prescriptive Analytics Assistant for {business_name}, a {industry} business.
Your role is to recommend actions to optimize business outcomes.
Focus on providing actionable recommendations to improve {key_metrics}.
When making recommendations, first identify the specific goal, then analyze
potential actions and their expected outcomes, and finally prioritize
recommendations based on feasibility, cost, and expected impact.""",
                
                "user": """We want to improve our {key_metrics}. Here's our current data:
{data_placeholder}

Please recommend specific actions we should take to optimize these metrics.
For each recommendation, explain the expected outcome, feasibility,
estimated cost, and potential impact."""
            },
            
            "cognitive": {
                "system": """You are a Cognitive Analytics Assistant for {business_name}, a {industry} business.
Your role is to analyze unstructured data like text, images, and human feedback.
Focus on extracting insights from {data_type} to support business decisions.
When processing unstructured data, first extract key concepts and sentiments,
then relate them to business objectives, and finally translate them
into actionable business insights.""",
                
                "user": """I need you to analyze this unstructured {data_type}:
{data_placeholder}

Please extract key concepts and sentiments, relate them to our business objectives,
and translate them into actionable insights we can use to improve our operations."""
            }
        }
    
    def _load_industry_templates(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """
        Load industry-specific prompt templates.
        
        Returns:
            A dictionary containing industry-specific prompt templates.
        """
        # In a real implementation, this would load from files
        return {
            "retail": {
                "descriptive": {
                    "system": """You are a Retail Analytics Assistant for {business_name}.
Your role is to analyze sales data, inventory movements, and customer behavior.
Focus on sales trends, inventory turnover, and customer demographics.
When analyzing data, first summarize the overall performance, then identify
seasonal patterns and product category trends, and finally highlight any
anomalies or notable changes in customer behavior.""",
                    
                    "user": """I need to understand our retail performance based on this data:
{data_placeholder}

Please analyze our sales trends, inventory turnover, and customer demographics.
Include seasonal patterns, product category performance, and any notable
changes in customer behavior."""
                },
                
                "diagnostic": {
                    "system": """You are a Retail Diagnostic Assistant for {business_name}.
Your role is to determine why sales, inventory, or customer metrics have changed.
Focus on understanding the factors behind fluctuations in revenue, product performance, and customer behavior.
When diagnosing issues, first identify the specific metric that has changed,
then analyze potential causes including marketing activities, pricing changes,
competitor actions, and seasonal factors, and finally determine the most
likely explanation with supporting evidence.""",
                    
                    "user": """We've noticed the following issue with our retail metrics:
{data_placeholder}

Please diagnose why this has happened, considering our marketing activities,
pricing changes, competitor actions, and seasonal factors.
Provide the most likely explanation with supporting evidence."""
                }
            },
            
            "restaurant": {
                "descriptive": {
                    "system": """You are a Restaurant Analytics Assistant for {business_name}.
Your role is to analyze sales data, menu performance, and customer visits.
Focus on dish popularity, peak hours, and table turnover rates.
When analyzing data, first summarize the overall performance, then identify
patterns in customer preferences and busy periods, and finally highlight any
anomalies or notable trends in food or beverage sales.""",
                    
                    "user": """I need to understand our restaurant performance based on this data:
{data_placeholder}

Please analyze our dish popularity, peak hours, and table turnover rates.
Include patterns in customer preferences, busy periods, and any notable
trends in food or beverage sales."""
                },
                
                "prescriptive": {
                    "system": """You are a Restaurant Optimization Assistant for {business_name}.
Your role is to recommend actions to optimize menu performance, operational efficiency, and customer satisfaction.
Focus on providing actionable recommendations to improve revenue, reduce costs, and enhance dining experience.
When making recommendations, first identify the specific business goal,
then analyze potential actions like menu engineering, staffing adjustments,
service process improvements, and marketing initiatives, and finally prioritize
recommendations based on feasibility, cost, and expected impact on key metrics.""",
                    
                    "user": """We want to improve our restaurant's performance. Here's our current data:
{data_placeholder}

Please recommend specific actions for menu engineering, staffing adjustments,
service process improvements, and marketing initiatives.
For each recommendation, explain the expected outcome, feasibility,
estimated cost, and potential impact on our revenue and customer satisfaction."""
                }
            },

            "fmcg_distribution": {
                "descriptive": {
                    "system": """You are an attentive Alarm CRM assistant for {business_name}.
You analyze kiosk orders, delivery success, and territory coverage for Ethiopian FMCG
(water, diapers, hygiene). You remember the operator's language and open loops.""",
                    "user": """Demand and distribution data:
{data_placeholder}

Summarize which sub-cities are hot vs dark, and whether vans should roll."""
                },
                "prescriptive": {
                    "system": """You are a business developer for {business_name}'s Alarm CRM ecosystem.
Recommend manufacturer acquisition, kiosk density plays, QR carton onboarding, and
when NOT to dispatch a van.""",
                    "user": """Goal: replace guesswork distribution.
{data_placeholder}

Give a prioritized action plan."""
                }
            }
        }
    
    def create_prompt(self, domain: str, business_profile: Dict[str, Any], 
                     prompt_type: str = "system", custom_fields: Dict[str, Any] = None) -> str:
        """
        Create a prompt for a specific domain and business.
        
        Args:
            domain: The analytics domain (descriptive, diagnostic, predictive, prescriptive, cognitive).
            business_profile: The business profile.
            prompt_type: The type of prompt to create (system, user, few_shot).
            custom_fields: Custom fields to include in the prompt.
            
        Returns:
            A customized prompt.
        """
        logger.info(f"Creating {prompt_type} prompt for {domain} analytics")
        
        # Get business information
        business_name = business_profile.get("name", "Business")
        industry = business_profile.get("industry", {}).get("code", "retail")
        key_metrics = business_profile.get("key_metrics", [])
        key_metrics_str = ", ".join(key_metrics) if key_metrics else "relevant business metrics"
        
        # Start with base fields
        fields = {
            "business_name": business_name,
            "industry": industry,
            "domain": domain,
            "key_metrics": key_metrics_str,
            "data_placeholder": "{data}",  # Placeholder to be replaced with actual data
            "task_description": f"{domain} analytics",
            "output_format": "insights and recommendations",
            "time_period": "3 months",
            "data_type": "customer feedback" if industry in ["retail", "restaurant"] else "documents"
        }
        
        # Add custom fields
        if custom_fields:
            fields.update(custom_fields)
        
        # Get the appropriate template
        template = self._get_template(domain, industry, prompt_type)
        
        # Replace placeholders
        prompt = self._replace_placeholders(template, fields)
        
        logger.info(f"Created {prompt_type} prompt for {domain} analytics")
        return prompt
    
    def _get_template(self, domain: str, industry: str, prompt_type: str) -> str:
        """
        Get the appropriate template for a domain, industry, and prompt type.
        
        Args:
            domain: The analytics domain.
            industry: The industry code.
            prompt_type: The type of prompt.
            
        Returns:
            The template string.
        """
        # Try to get industry-specific template
        if industry in self.industry_templates and domain in self.industry_templates[industry] and prompt_type in self.industry_templates[industry][domain]:
            return self.industry_templates[industry][domain][prompt_type]
        
        # Try to get domain-specific template
        if domain in self.domain_templates and prompt_type in self.domain_templates[domain]:
            return self.domain_templates[domain][prompt_type]
        
        # Fall back to base template
        return self.templates.get(prompt_type, "")
    
    def _replace_placeholders(self, template: str, fields: Dict[str, Any]) -> str:
        """
        Replace placeholders in a template with actual values.
        
        Args:
            template: The template string.
            fields: The fields to replace.
            
        Returns:
            The template with placeholders replaced.
        """
        result = template
        for key, value in fields.items():
            placeholder = "{" + key + "}"
            result = result.replace(placeholder, str(value))
        return result
    
    def optimize_prompt(self, prompt: str, model_info: Dict[str, Any]) -> str:
        """
        Optimize a prompt for a specific model.
        
        Args:
            prompt: The prompt to optimize.
            model_info: Information about the model.
            
        Returns:
            The optimized prompt.
        """
        logger.info(f"Optimizing prompt for model: {model_info.get('name', 'unknown')}")
        
        # Get model parameters
        model_size = model_info.get("parameters", "7B")
        context_length = model_info.get("context_length", 4096)
        
        # Convert model size to numeric value (billions of parameters)
        if isinstance(model_size, str):
            if model_size.endswith("B"):
                model_size = float(model_size[:-1])
            else:
                model_size = float(model_size) / 1e9  # Convert to billions
        
        # Optimize based on model size
        if model_size < 3:
            # For smaller models, simplify the prompt
            prompt = self._simplify_prompt(prompt)
        elif model_size > 30:
            # For larger models, add more detail
            prompt = self._enhance_prompt(prompt)
        
        # Ensure prompt fits within context length
        if len(prompt) > context_length / 2:  # Use at most half of context for prompt
            prompt = self._truncate_prompt(prompt, context_length / 2)
        
        logger.info("Prompt optimization completed")
        return prompt
    
    def _simplify_prompt(self, prompt: str) -> str:
        """
        Simplify a prompt for smaller models.
        
        Args:
            prompt: The prompt to simplify.
            
        Returns:
            The simplified prompt.
        """
        # Remove examples if present
        prompt = re.sub(r"Example \d+:.*?(?=Example \d+:|$)", "", prompt, flags=re.DOTALL)
        
        # Shorten instructions
        prompt = re.sub(r"When (analyzing|diagnosing|making|processing).*?\.", "", prompt, flags=re.DOTALL)
        
        # Remove detailed explanations
        prompt = re.sub(r"\(.*?\)", "", prompt)
        
        # Remove extra whitespace
        prompt = re.sub(r"\n\s*\n", "\n\n", prompt)
        
        return prompt.strip()
    
    def _enhance_prompt(self, prompt: str) -> str:
        """
        Enhance a prompt for larger models.
        
        Args:
            prompt: The prompt to enhance.
            
        Returns:
            The enhanced prompt.
        """
        # Add more detailed instructions
        if "When analyzing data" not in prompt and "descriptive" in prompt.lower():
            prompt += "\n\nWhen analyzing data, please provide:\n1. A comprehensive summary of the data\n2. Detailed patterns and trends identified\n3. Statistical significance of findings\n4. Visualizations that would help understand the data\n5. Recommendations based on the analysis"
        
        if "When diagnosing issues" not in prompt and "diagnostic" in prompt.lower():
            prompt += "\n\nWhen diagnosing issues, please provide:\n1. A clear definition of the problem\n2. Analysis of all potential causes\n3. Evidence supporting or refuting each cause\n4. The most likely root cause with confidence level\n5. Recommended next steps for verification"
        
        if "When making predictions" not in prompt and "predictive" in prompt.lower():
            prompt += "\n\nWhen making predictions, please provide:\n1. Analysis of historical patterns\n2. Relevant external factors considered\n3. Multiple forecast scenarios (best, expected, worst case)\n4. Confidence levels for each prediction\n5. Key indicators to monitor for forecast adjustments"
        
        if "When making recommendations" not in prompt and "prescriptive" in prompt.lower():
            prompt += "\n\nWhen making recommendations, please provide:\n1. Clear business goals addressed\n2. Detailed action plans for each recommendation\n3. Expected outcomes with metrics\n4. Implementation requirements and timeline\n5. Prioritization based on impact, cost, and feasibility"
        
        return prompt
    
    def _truncate_prompt(self, prompt: str, max_length: int) -> str:
        """
        Truncate a prompt to fit within a maximum length.
        
        Args:
            prompt: The prompt to truncate.
            max_length: The maximum length.
            
        Returns:
            The truncated prompt.
        """
        if len(prompt) <= max_length:
            return prompt
        
        # Split into sections
        sections = re.split(r"\n\s*\n", prompt)
        
        # Keep the first and last sections
        result = sections[0]
        remaining_length = max_length - len(result) - 4  # 4 for "\n\n" and potential ellipsis
        
        if remaining_length > len(sections[-1]):
            # We can keep the last section
            result += "\n\n...\n\n" + sections[-1]
        else:
            # Just truncate
            result = prompt[:max_length - 3] + "..."
        
        return result
    
    def create_few_shot_examples(self, domain: str, industry: str) -> str:
        """
        Create few-shot examples for a specific domain and industry.
        
        Args:
            domain: The analytics domain.
            industry: The industry code.
            
        Returns:
            A string containing few-shot examples.
        """
        logger.info(f"Creating few-shot examples for {domain} analytics in {industry}")
        
        # In a real implementation, this would load from a database of examples
        examples = {
            "retail": {
                "descriptive": [
                    {
                        "user": "I need to understand our sales trends for the past quarter.",
                        "data": "[Sales data for Q1-Q3 2024]",
                        "assistant": "Based on your sales data, I've identified three key trends:\n1. Weekend sales have increased by 15% compared to weekdays\n2. Product category A has shown consistent growth of 5% month-over-month\n3. There's a noticeable dip in sales during the second week of each month"
                    },
                    {
                        "user": "How are our different store locations performing?",
                        "data": "[Store performance data for 2024]",
                        "assistant": "After analyzing your store performance data:\n1. Your downtown location has the highest revenue but lowest profit margin (15%)\n2. Suburban locations show consistent performance with 22% profit margins\n3. The new mall location is growing fastest at 8% month-over-month\n4. Online sales now represent 35% of total revenue, up from 28% last year"
                    }
                ],
                "diagnostic": [
                    {
                        "user": "Why did our sales drop 20% in July?",
                        "data": "[Sales and marketing data for Q2-Q3 2024]",
                        "assistant": "After analyzing your July sales decline, I've identified these likely causes:\n1. Primary factor: Competitor's flash sale (July 10-17) coincided with your 20% drop\n2. Contributing factor: Your marketing spend decreased by 15% in July\n3. Contributing factor: Website outage on July 15-16 (typically high-volume days)\n\nThe combination of these factors, particularly the competitor's aggressive promotion during your reduced marketing presence, appears to be the root cause of the sales decline."
                    }
                ]
            },
            "restaurant": {
                "prescriptive": [
                    {
                        "user": "How can we improve our dinner service profitability?",
                        "data": "[Menu performance and service data for 2024]",
                        "assistant": "Based on your data, I recommend these actions to improve dinner service profitability:\n\n1. Menu Engineering:\n   - Promote your high-margin pasta dishes more prominently (currently 15% of sales but 22% of profit)\n   - Consider reformulating or replacing the seafood platter (high food cost at 42%)\n   - Add 2-3 new high-margin appetizers to increase check averages\n\n2. Staffing Adjustments:\n   - Adjust server scheduling to match peak times (currently overstaffed Mondays and Tuesdays)\n   - Cross-train bar staff to help with table service during 7-9pm rush\n\n3. Table Management:\n   - Reconfigure floor plan to add two 2-top tables (potential $450/night increase)\n   - Implement 15-minute table turnover improvement process (could increase capacity by 8%)\n\nPriority recommendation: Menu engineering changes can be implemented immediately with minimal cost and potential 5% profit improvement within 30 days."
                    }
                ]
            }
        }
        
        # Get examples for the domain and industry
        domain_examples = examples.get(industry, {}).get(domain, [])
        
        # If no specific examples, try to get examples for any domain in the industry
        if not domain_examples:
            for d, e in examples.get(industry, {}).items():
                if e:
                    domain_examples = e
                    break
        
        # If still no examples, get any examples
        if not domain_examples:
            for i in examples:
                for d, e in examples[i].items():
                    if e:
                        domain_examples = e
                        break
                if domain_examples:
                    break
        
        # Format examples
        result = ""
        for i, example in enumerate(domain_examples[:2]):  # Use at most 2 examples
            result += f"Example {i+1}:\n"
            result += f"User: {example['user']}\n"
            result += f"Data: {example['data']}\n"
            result += f"Assistant: {example['assistant']}\n\n"
        
        logger.info(f"Created {len(domain_examples[:2])} few-shot examples")
        return result.strip()
    
    def create_prompt_set(self, domain: str, business_profile: Dict[str, Any], 
                         model_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Create a complete set of prompts for a specific domain and business.
        
        Args:
            domain: The analytics domain.
            business_profile: The business profile.
            model_info: Information about the model.
            
        Returns:
            A dictionary containing different types of prompts.
        """
        logger.info(f"Creating prompt set for {domain} analytics")
        
        # Get business information
        business_name = business_profile.get("name", "Business")
        industry = business_profile.get("industry", {}).get("code", "retail")
        
        # Create prompts
        system_prompt = self.create_prompt(domain, business_profile, "system")
        user_prompt = self.create_prompt(domain, business_profile, "user")
        few_shot_examples = self.create_few_shot_examples(domain, industry)
        
        # Optimize prompts
        system_prompt = self.optimize_prompt(system_prompt, model_info)
        
        # Create prompt set
        prompt_set = {
            "system": system_prompt,
            "user": user_prompt,
            "few_shot": few_shot_examples,
            "combined": f"{system_prompt}\n\n{few_shot_examples}\n\n{user_prompt}"
        }
        
        logger.info(f"Created prompt set for {domain} analytics for {business_name}")
        return prompt_set
    
    def save_prompt_set(self, prompt_set: Dict[str, str], output_dir: str, 
                       domain: str, business_name: str) -> Dict[str, str]:
        """
        Save a prompt set to files.
        
        Args:
            prompt_set: The prompt set to save.
            output_dir: The directory to save to.
            domain: The analytics domain.
            business_name: The business name.
            
        Returns:
            A dictionary mapping prompt types to file paths.
        """
        import os
        
        # Create sanitized business name
        sanitized_name = business_name.lower().replace(" ", "_")
        
        # Create directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save prompts
        file_paths = {}
        for prompt_type, prompt in prompt_set.items():
            file_name = f"{sanitized_name}_{domain}_{prompt_type}.txt"
            file_path = os.path.join(output_dir, file_name)
            
            with open(file_path, "w") as f:
                f.write(prompt)
            
            file_paths[prompt_type] = file_path
            logger.info(f"Saved {prompt_type} prompt to {file_path}")
        
        return file_paths
