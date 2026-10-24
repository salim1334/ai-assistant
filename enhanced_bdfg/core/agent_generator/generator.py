"""
Agent Generator Module

This module contains the AgentGenerator class, which generates customized agent frameworks
based on business profiles and selected models.
"""

import os
import json
import shutil
import logging
import zipfile
from typing import Dict, Any, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentGenerator:
    """
    The AgentGenerator creates customized agent frameworks for specific businesses.
    
    It generates domain-specific agents, customizes prompts, creates knowledge bases,
    and packages everything into a deployable framework.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the AgentGenerator.
        
        Args:
            config: Configuration parameters for the agent generator.
        """
        self.config = config or {}
        logger.info("Initializing AgentGenerator")
        
        # Load prompt templates
        self.prompt_templates = self._load_prompt_templates()
        
        # Load knowledge base templates
        self.knowledge_templates = self._load_knowledge_templates()
        
        # Load tool configurations
        self.tool_configs = self._load_tool_configs()
        
        # Load framework templates
        self.framework_templates = self._load_framework_templates()
        
        logger.info("AgentGenerator initialized successfully")
    
    def _load_prompt_templates(self) -> Dict[str, Any]:
        """
        Load prompt templates for different analytics domains and business types.
        
        Returns:
            A dictionary containing prompt templates.
        """
        # In a real implementation, this would load from files
        return {
            "descriptive": {
                "base": """You are a Descriptive Analytics Agent for a {business_type} business.
Your role is to analyze historical data to identify patterns and trends.
Focus on {key_metrics} that are critical for this business type.
When analyzing data, first summarize what you see, then identify patterns,
and finally highlight any anomalies or notable trends.""",
                "retail": """You are a Descriptive Analytics Agent for a retail business.
Your role is to analyze sales data, inventory movements, and customer behavior.
Focus on sales trends, inventory turnover, and customer demographics.
When analyzing data, first summarize the overall performance, then identify
seasonal patterns and product category trends, and finally highlight any
anomalies or notable changes in customer behavior.""",
                "restaurant": """You are a Descriptive Analytics Agent for a restaurant business.
Your role is to analyze sales data, menu performance, and customer visits.
Focus on dish popularity, peak hours, and table turnover rates.
When analyzing data, first summarize the overall performance, then identify
patterns in customer preferences and busy periods, and finally highlight any
anomalies or notable trends in food or beverage sales.""",
                "legal": """You are a Descriptive Analytics Agent for a legal practice.
Your role is to analyze case data, billing information, and client interactions.
Focus on case resolution times, billing efficiency, and client retention.
When analyzing data, first summarize the overall practice performance, then identify
patterns in case types and outcomes, and finally highlight any anomalies or
notable trends in client acquisition or retention."""
            },
            "diagnostic": {
                "base": """You are a Diagnostic Analytics Agent for a {business_type} business.
Your role is to determine why certain events occurred by identifying root causes.
Focus on understanding the factors behind changes in {key_metrics}.
When diagnosing issues, first identify the specific problem, then analyze
potential causes, and finally determine the most likely explanation with
supporting evidence.""",
                "retail": """You are a Diagnostic Analytics Agent for a retail business.
Your role is to determine why sales, inventory, or customer metrics have changed.
Focus on understanding the factors behind fluctuations in revenue, product performance, and customer behavior.
When diagnosing issues, first identify the specific metric that has changed,
then analyze potential causes including marketing activities, pricing changes,
competitor actions, and seasonal factors, and finally determine the most
likely explanation with supporting evidence.""",
                "restaurant": """You are a Diagnostic Analytics Agent for a restaurant business.
Your role is to determine why sales, food costs, or customer satisfaction metrics have changed.
Focus on understanding the factors behind fluctuations in revenue, dish popularity, and customer feedback.
When diagnosing issues, first identify the specific metric that has changed,
then analyze potential causes including menu changes, pricing adjustments,
staff performance, and seasonal factors, and finally determine the most
likely explanation with supporting evidence.""",
                "legal": """You are a Diagnostic Analytics Agent for a legal practice.
Your role is to determine why case outcomes, billing efficiency, or client satisfaction has changed.
Focus on understanding the factors behind fluctuations in case success rates, revenue, and client retention.
When diagnosing issues, first identify the specific metric that has changed,
then analyze potential causes including case complexity, attorney workload,
procedural changes, and external legal factors, and finally determine the most
likely explanation with supporting evidence."""
            },
            "predictive": {
                "base": """You are a Predictive Analytics Agent for a {business_type} business.
Your role is to forecast future trends and outcomes based on historical data.
Focus on predicting future values of {key_metrics} that are critical for business planning.
When making predictions, first analyze historical patterns, then identify
relevant external factors, and finally provide forecasts with confidence levels
and potential scenarios.""",
                "retail": """You are a Predictive Analytics Agent for a retail business.
Your role is to forecast sales, inventory needs, and customer behavior.
Focus on predicting future revenue, stock requirements, and customer trends.
When making predictions, first analyze historical sales patterns, then identify
relevant factors like seasonality, marketing plans, and market trends, and finally
provide forecasts with confidence levels and potential scenarios for different
product categories and customer segments.""",
                "restaurant": """You are a Predictive Analytics Agent for a restaurant business.
Your role is to forecast sales, ingredient needs, and staffing requirements.
Focus on predicting future revenue, food costs, and peak service times.
When making predictions, first analyze historical sales patterns, then identify
relevant factors like seasonality, local events, and weather forecasts, and finally
provide forecasts with confidence levels and potential scenarios for different
meal periods and menu categories.""",
                "legal": """You are a Predictive Analytics Agent for a legal practice.
Your role is to forecast case outcomes, resource needs, and business development opportunities.
Focus on predicting future case resolution rates, staffing requirements, and revenue streams.
When making predictions, first analyze historical case patterns, then identify
relevant factors like court schedules, regulatory changes, and market conditions, and finally
provide forecasts with confidence levels and potential scenarios for different
practice areas and client segments."""
            },
            "prescriptive": {
                "base": """You are a Prescriptive Analytics Agent for a {business_type} business.
Your role is to recommend actions to optimize business outcomes.
Focus on providing actionable recommendations to improve {key_metrics}.
When making recommendations, first identify the specific goal, then analyze
potential actions and their expected outcomes, and finally prioritize
recommendations based on feasibility, cost, and expected impact.""",
                "retail": """You are a Prescriptive Analytics Agent for a retail business.
Your role is to recommend actions to optimize sales, inventory, and customer satisfaction.
Focus on providing actionable recommendations to improve revenue, reduce costs, and enhance customer experience.
When making recommendations, first identify the specific business goal,
then analyze potential actions like pricing adjustments, inventory optimization,
marketing initiatives, and customer service improvements, and finally prioritize
recommendations based on feasibility, cost, and expected impact on key metrics.""",
                "restaurant": """You are a Prescriptive Analytics Agent for a restaurant business.
Your role is to recommend actions to optimize menu performance, operational efficiency, and customer satisfaction.
Focus on providing actionable recommendations to improve revenue, reduce costs, and enhance dining experience.
When making recommendations, first identify the specific business goal,
then analyze potential actions like menu engineering, staffing adjustments,
service process improvements, and marketing initiatives, and finally prioritize
recommendations based on feasibility, cost, and expected impact on key metrics.""",
                "legal": """You are a Prescriptive Analytics Agent for a legal practice.
Your role is to recommend actions to optimize case management, resource allocation, and client development.
Focus on providing actionable recommendations to improve case outcomes, operational efficiency, and client satisfaction.
When making recommendations, first identify the specific business goal,
then analyze potential actions like case prioritization, staffing adjustments,
process improvements, and client communication strategies, and finally prioritize
recommendations based on feasibility, cost, and expected impact on key metrics."""
            },
            "cognitive": {
                "base": """You are a Cognitive Analytics Agent for a {business_type} business.
Your role is to analyze unstructured data like text, images, and human feedback.
When processing {data_type}, first extract key concepts and sentiments,
then relate them to business objectives, and finally translate them
into actionable business insights.""",
                "retail": """You are a Cognitive Analytics Agent for a retail business.
Your role is to analyze unstructured data like customer reviews, social media mentions, and support interactions.
Focus on extracting customer sentiment, product feedback, and emerging trends.
When processing customer feedback, first extract key themes and sentiments,
then relate them to specific products or services, and finally translate them
into actionable insights for product development, marketing, and customer service teams.""",
                "restaurant": """You are a Cognitive Analytics Agent for a restaurant business.
Your role is to analyze unstructured data like customer reviews, social media mentions, and comment cards.
Focus on extracting customer sentiment, dish feedback, and service quality insights.
When processing customer feedback, first extract key themes and sentiments,
then relate them to specific menu items or service aspects, and finally translate them
into actionable insights for menu development, staff training, and operational improvements.""",
                "legal": """You are a Cognitive Analytics Agent for a legal practice.
Your role is to analyze unstructured data like case documents, client communications, and legal opinions.
Focus on extracting key legal concepts, precedent patterns, and client sentiment.
When processing legal documents, first extract key arguments and citations,
then identify relevant precedents and legal principles, and finally translate them
into actionable insights for case strategy, knowledge management, and client communication."""
            }
        }
    
    def _load_knowledge_templates(self) -> Dict[str, Any]:
        """
        Load knowledge base templates for different business types.
        
        Returns:
            A dictionary containing knowledge base templates.
        """
        # In a real implementation, this would load from files
        return {
            "retail": {
                "inventory_management": {
                    "title": "Inventory Management Best Practices",
                    "content": """
# Inventory Management Best Practices for Retail

## Key Metrics
- Inventory Turnover Ratio: 4-6 times per year is typical for retail
- Days of Supply: 30-60 days is common for most retail categories
- Shrinkage Rate: Industry average is 1.5% of sales
- In-Stock Rate: Target 95-98% for optimal customer satisfaction

## Ordering Methods
- Economic Order Quantity (EOQ): Balances ordering costs with holding costs
- Just-in-Time (JIT): Minimizes inventory holding costs
- Min/Max System: Sets minimum and maximum inventory levels

## Forecasting Techniques
- Moving Average: Simple method for stable demand
- Exponential Smoothing: Gives more weight to recent data
- Seasonal Forecasting: Accounts for predictable seasonal fluctuations

## Technology Solutions
- Barcode Systems: For accurate tracking
- RFID: For real-time inventory visibility
- Inventory Management Software: For automation and analytics
                    """
                },
                "customer_segmentation": {
                    "title": "Customer Segmentation Strategies",
                    "content": """
# Customer Segmentation Strategies for Retail

## Segmentation Methods
- Demographic: Age, gender, income, education
- Geographic: Location, urban/suburban/rural
- Behavioral: Purchase history, frequency, average order value
- Psychographic: Lifestyle, values, interests

## Key Customer Segments
- New Customers: First-time buyers
- Loyal Customers: Regular purchasers
- High-Value Customers: Top 20% by revenue
- At-Risk Customers: Declining purchase frequency
- Lapsed Customers: Haven't purchased in defined period

## Targeting Strategies
- Personalized Marketing: Tailored messages based on segment
- Loyalty Programs: Rewards for repeat purchases
- Win-Back Campaigns: Special offers for lapsed customers
- Upsell/Cross-sell: Complementary product recommendations

## Measurement Metrics
- Customer Lifetime Value (CLV)
- Customer Acquisition Cost (CAC)
- Retention Rate
- Conversion Rate by Segment
                    """
                }
            },
            "restaurant": {
                "menu_engineering": {
                    "title": "Menu Engineering Principles",
                    "content": """
# Menu Engineering Principles for Restaurants

## Menu Classification Matrix
- Stars: High popularity, high profit margin
- Plow Horses: High popularity, low profit margin
- Puzzles: Low popularity, high profit margin
- Dogs: Low popularity, low profit margin

## Key Metrics
- Food Cost Percentage: Target 28-32% for full-service restaurants
- Contribution Margin: Revenue minus variable costs
- Menu Mix Percentage: Percentage of total sales for each item
- Price Elasticity: How demand changes with price adjustments

## Menu Design Strategies
- Menu Psychology: Eye movement patterns and attention focus
- Item Placement: Strategic positioning of high-margin items
- Descriptive Language: Compelling item descriptions
- Price Presentation: Removing currency symbols, using round numbers

## Implementation Process
- Menu Analysis: Calculate costs and track sales
- Item Classification: Categorize using the matrix
- Menu Redesign: Apply strategic design principles
- Testing and Iteration: Monitor performance and adjust
                    """
                },
                "staff_scheduling": {
                    "title": "Staff Scheduling Optimization",
                    "content": """
# Staff Scheduling Optimization for Restaurants

## Key Metrics
- Labor Cost Percentage: Target 25-30% of revenue
- Sales Per Labor Hour: Measure of staff productivity
- Server Efficiency: Average tables/guests handled per shift
- Staff Turnover Rate: Industry average is 75% annually

## Scheduling Methods
- Demand-Based Scheduling: Staff based on forecasted business volume
- Fixed Scheduling: Consistent shifts for staff stability
- Hybrid Scheduling: Core staff with flexible additions

## Optimization Strategies
- Peak Period Analysis: Identify busy times requiring maximum staffing
- Skill-Based Scheduling: Match employee skills to shift requirements
- Cross-Training: Increase staff flexibility
- Split Shifts: Cover peak periods without overstaffing during slow times

## Technology Solutions
- Scheduling Software: Automated schedule creation
- Time and Attendance Systems: Track actual hours worked
- POS Integration: Link labor to sales data
- Mobile Communication: Real-time schedule updates and shift swapping
                    """
                }
            },
            "legal": {
                "case_management": {
                    "title": "Case Management Best Practices",
                    "content": """
# Case Management Best Practices for Legal Practices

## Key Metrics
- Case Resolution Time: Average time to close cases by type
- Billable Hours Ratio: Percentage of time that is billable
- Case Profitability: Revenue minus costs per case
- Client Satisfaction: Measured through surveys and retention

## Case Prioritization
- Urgency: Deadline-driven prioritization
- Value: Focus on high-value cases
- Complexity: Resource allocation based on case complexity
- Client Importance: Strategic prioritization of key clients

## Workflow Optimization
- Standardized Processes: Templates and checklists for common case types
- Task Assignment: Matching tasks to appropriate skill levels
- Progress Tracking: Regular status updates and milestone tracking
- Bottleneck Identification: Identifying and resolving process delays

## Technology Solutions
- Case Management Software: Centralized case information
- Document Automation: Template-based document generation
- Time Tracking Systems: Accurate billing and productivity analysis
- Client Portals: Transparent communication and document sharing
                    """
                },
                "legal_research": {
                    "title": "Legal Research Efficiency",
                    "content": """
# Legal Research Efficiency for Legal Practices

## Research Methods
- Precedent Analysis: Identifying relevant case law
- Statutory Interpretation: Understanding legislative intent
- Secondary Sources: Leveraging treatises and law reviews
- Analogical Reasoning: Applying similar case principles

## Efficiency Strategies
- Research Planning: Defining scope and objectives before starting
- Database Selection: Choosing appropriate research platforms
- Search Term Optimization: Effective keyword and Boolean strategies
- Research Memoranda: Documenting findings for future reference

## Quality Control
- Multiple Source Verification: Cross-checking information
- Currency Checking: Ensuring law is still valid and not overturned
- Shepardizing/KeyCiting: Verifying precedential value
- Peer Review: Having research reviewed by colleagues

## Technology Solutions
- Legal Research Platforms: Westlaw, LexisNexis, Bloomberg Law
- AI-Assisted Research: Predictive analytics and recommendation engines
- Knowledge Management Systems: Capturing and sharing research insights
- Citation Management: Tracking and organizing legal citations
                    """
                }
            },
            "manufacturing": {
                "production_optimization": {
                    "title": "Production Optimization Strategies",
                    "content": """
# Production Optimization Strategies for Manufacturing

## Key Metrics
- Overall Equipment Effectiveness (OEE): Industry benchmark is 85%
- Throughput Rate: Units produced per time period
- Cycle Time: Time to complete one unit
- Defect Rate: Percentage of units with quality issues

## Optimization Methods
- Lean Manufacturing: Eliminating waste in processes
- Six Sigma: Reducing variation and defects
- Theory of Constraints: Identifying and addressing bottlenecks
- Total Productive Maintenance: Maximizing equipment reliability

## Implementation Strategies
- Value Stream Mapping: Visualizing the production process
- Standardized Work: Documenting best practices
- Quick Changeover (SMED): Reducing setup times
- Continuous Improvement (Kaizen): Ongoing process refinement

## Technology Solutions
- Manufacturing Execution Systems (MES): Real-time production tracking
- Industrial IoT: Connected equipment and sensors
- Predictive Maintenance: Anticipating equipment failures
- Digital Twins: Virtual models of production processes
                    """
                },
                "supply_chain_management": {
                    "title": "Supply Chain Management Excellence",
                    "content": """
# Supply Chain Management Excellence for Manufacturing

## Key Metrics
- Inventory Turns: Industry average is 4-6 times per year
- Lead Time: Time from order to delivery
- On-Time Delivery: Percentage of orders delivered on schedule
- Supply Chain Costs: As percentage of revenue

## Management Strategies
- Supplier Relationship Management: Collaborative partnerships
- Demand Forecasting: Accurate prediction of material needs
- Risk Management: Identifying and mitigating supply chain risks
- Inventory Optimization: Balancing stock levels with service requirements

## Optimization Techniques
- Just-in-Time (JIT): Minimizing inventory holding
- Vendor-Managed Inventory (VMI): Supplier manages stock levels
- ABC Analysis: Prioritizing inventory by value and criticality
- Economic Order Quantity (EOQ): Optimizing order sizes

## Technology Solutions
- Supply Chain Management Software: End-to-end visibility
- RFID and Barcode Systems: Automated tracking
- Blockchain: Transparent and secure supply chain records
- AI-Powered Forecasting: Advanced demand prediction
                    """
                }
            }
        }
    
    def _load_tool_configs(self) -> Dict[str, Any]:
        """
        Load tool configurations for different business types.
        
        Returns:
            A dictionary containing tool configurations.
        """
        # In a real implementation, this would load from files
        return {
            "retail": [
                {
                    "name": "inventory_analyzer",
                    "description": "Analyzes inventory data to identify slow-moving items, stockouts, and reorder points",
                    "parameters": {
                        "data_source": "inventory_management_system",
                        "time_period": "30_days",
                        "categories": "all"
                    }
                },
                {
                    "name": "sales_forecaster",
                    "description": "Forecasts sales by product category based on historical data and seasonality",
                    "parameters": {
                        "data_source": "pos_system",
                        "forecast_period": "90_days",
                        "confidence_level": "0.95"
                    }
                },
                {
                    "name": "customer_segmenter",
                    "description": "Segments customers based on purchase behavior, frequency, and value",
                    "parameters": {
                        "data_source": "crm_system",
                        "segmentation_method": "rfm",
                        "segment_count": "5"
                    }
                }
            ],
            "restaurant": [
                {
                    "name": "menu_analyzer",
                    "description": "Analyzes menu performance to identify stars, plow horses, puzzles, and dogs",
                    "parameters": {
                        "data_source": "pos_system",
                        "time_period": "90_days",
                        "categories": "all"
                    }
                },
                {
                    "name": "staff_scheduler",
                    "description": "Optimizes staff scheduling based on forecasted demand and labor costs",
                    "parameters": {
                        "data_source": "pos_system",
                        "forecast_period": "14_days",
                        "staff_roles": "all"
                    }
                },
                {
                    "name": "food_cost_calculator",
                    "description": "Calculates food cost percentage and identifies cost-saving opportunities",
                    "parameters": {
                        "data_source": "inventory_system",
                        "recipe_database": "current_menu",
                        "include_waste": "true"
                    }
                }
            ],
            "legal": [
                {
                    "name": "case_analyzer",
                    "description": "Analyzes case outcomes and identifies factors contributing to success",
                    "parameters": {
                        "data_source": "case_management_system",
                        "case_types": "all",
                        "time_period": "365_days"
                    }
                },
                {
                    "name": "billing_optimizer",
                    "description": "Identifies billing inefficiencies and opportunities for improved realization",
                    "parameters": {
                        "data_source": "billing_system",
                        "attorney_filter": "all",
                        "client_filter": "all"
                    }
                },
                {
                    "name": "document_analyzer",
                    "description": "Analyzes legal documents to extract key information and precedents",
                    "parameters": {
                        "document_source": "document_management_system",
                        "document_types": "all",
                        "analysis_depth": "comprehensive"
                    }
                }
            ],
            "manufacturing": [
                {
                    "name": "production_analyzer",
                    "description": "Analyzes production efficiency and identifies bottlenecks",
                    "parameters": {
                        "data_source": "mes_system",
                        "production_lines": "all",
                        "time_period": "30_days"
                    }
                },
                {
                    "name": "quality_controller",
                    "description": "Monitors quality metrics and identifies root causes of defects",
                    "parameters": {
                        "data_source": "quality_management_system",
                        "product_lines": "all",
                        "defect_categories": "all"
                    }
                },
                {
                    "name": "maintenance_scheduler",
                    "description": "Predicts equipment maintenance needs and optimizes maintenance schedules",
                    "parameters": {
                        "data_source": "equipment_monitoring_system",
                        "equipment_types": "all",
                        "prediction_horizon": "90_days"
                    }
                }
            ]
        }
    
    def _load_framework_templates(self) -> Dict[str, Any]:
        """
        Load framework templates for different deployment scenarios.
        
        Returns:
            A dictionary containing framework templates.
        """
        # In a real implementation, this would load from files
        return {
            "local": {
                "requirements": [
                    "python>=3.8",
                    "torch>=1.8.0",
                    "transformers>=4.5.0",
                    "pandas>=1.2.0",
                    "numpy>=1.19.0",
                    "scikit-learn>=0.24.0",
                    "matplotlib>=3.3.0",
                    "streamlit>=1.0.0"
                ],
                "directory_structure": {
                    "agents": ["descriptive", "diagnostic", "predictive", "prescriptive", "cognitive"],
                    "data": ["connectors", "processors", "storage"],
                    "knowledge": ["industry", "business_specific"],
                    "models": ["configs", "weights"],
                    "tools": ["industry_specific", "general"],
                    "ui": ["web", "cli"]
                },
                "entry_points": {
                    "cli": "cli.py",
                    "web": "app.py"
                }
            },
            "cloud": {
                "requirements": [
                    "python>=3.8",
                    "torch>=1.8.0",
                    "transformers>=4.5.0",
                    "pandas>=1.2.0",
                    "numpy>=1.19.0",
                    "scikit-learn>=0.24.0",
                    "matplotlib>=3.3.0",
                    "fastapi>=0.68.0",
                    "uvicorn>=0.15.0",
                    "gunicorn>=20.1.0"
                ],
                "directory_structure": {
                    "agents": ["descriptive", "diagnostic", "predictive", "prescriptive", "cognitive"],
                    "data": ["connectors", "processors", "storage"],
                    "knowledge": ["industry", "business_specific"],
                    "models": ["configs", "weights"],
                    "tools": ["industry_specific", "general"],
                    "api": ["routers", "middleware", "schemas"]
                },
                "entry_points": {
                    "api": "main.py",
                    "worker": "worker.py"
                }
            }
        }
    
    def customize_prompt(self, domain: str, business_profile: Dict[str, Any]) -> str:
        """
        Customize a prompt template for a specific business.
        
        Args:
            domain: The analytics domain (descriptive, diagnostic, predictive, prescriptive, cognitive).
            business_profile: The business profile.
            
        Returns:
            A customized prompt.
        """
        industry_code = business_profile.get("industry", {}).get("code", "retail")
        business_name = business_profile.get("name", "Business")
        key_metrics = business_profile.get("key_metrics", [])
        key_metrics_str = ", ".join(key_metrics) if key_metrics else "relevant business metrics"
        
        # Get the appropriate template
        templates = self.prompt_templates.get(domain, {})
        
        # Try to get industry-specific template, fall back to base
        template = templates.get(industry_code, templates.get("base", ""))
        
        # Replace placeholders
        prompt = template.replace("{business_type}", industry_code)
        prompt = prompt.replace("{key_metrics}", key_metrics_str)
        prompt = prompt.replace("{business_name}", business_name)
        
        # For cognitive analytics, add data type
        if domain == "cognitive":
            data_type = "customer feedback" if industry_code == "retail" or industry_code == "restaurant" else "documents"
            prompt = prompt.replace("{data_type}", data_type)
        
        # For prescriptive analytics, add decision domain
        if domain == "prescriptive":
            decision_domain = "inventory and pricing" if industry_code == "retail" else \
                             "menu and staffing" if industry_code == "restaurant" else \
                             "case strategy and resource allocation" if industry_code == "legal" else \
                             "production planning and maintenance"
            prompt = prompt.replace("{decision_domain}", decision_domain)
        
        # For diagnostic analytics, add problem domain
        if domain == "diagnostic":
            problem_domain = "sales and inventory" if industry_code == "retail" else \
                            "revenue and customer satisfaction" if industry_code == "restaurant" else \
                            "case outcomes and client retention" if industry_code == "legal" else \
                            "production efficiency and quality control"
            prompt = prompt.replace("{problem_domain}", problem_domain)
        
        logger.info(f"Customized prompt for {domain} analytics in {industry_code} business")
        return prompt
    
    def create_knowledge_base(self, business_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a knowledge base for a specific business.
        
        Args:
            business_profile: The business profile.
            
        Returns:
            A dictionary containing the knowledge base.
        """
        industry_code = business_profile.get("industry", {}).get("code", "retail")
        
        # Get industry-specific knowledge templates
        industry_knowledge = self.knowledge_templates.get(industry_code, {})
        
        # Create knowledge base
        knowledge_base = {
            "industry": {},
            "business_specific": {}
        }
        
        # Add industry knowledge
        for key, knowledge_item in industry_knowledge.items():
            knowledge_base["industry"][key] = {
                "title": knowledge_item["title"],
                "content": knowledge_item["content"]
            }
        
        # Add business-specific knowledge
        # In a real implementation, this would extract from business profile
        business_name = business_profile.get("name", "Business")
        business_description = business_profile.get("description", "")
        years_in_business = business_profile.get("years_in_business", 0)
        
        knowledge_base["business_specific"]["profile"] = {
            "title": f"{business_name} Profile",
            "content": f"""
# {business_name} Profile

## Business Overview
{business_description}

## Key Information
- Years in Business: {years_in_business}
- Industry: {business_profile.get('industry', {}).get('name', industry_code)}
- Size: {business_profile.get('size', 'small')}

## Key Challenges
{', '.join(business_profile.get('challenges', []))}

## Business Goals
{', '.join(business_profile.get('goals', []))}

## Key Metrics
{', '.join(business_profile.get('key_metrics', []))}
            """
        }
        
        logger.info(f"Created knowledge base for {business_name} ({industry_code})")
        return knowledge_base
    
    def select_tools(self, business_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Select appropriate tools for a specific business.
        
        Args:
            business_profile: The business profile.
            
        Returns:
            A list of selected tools.
        """
        industry_code = business_profile.get("industry", {}).get("code", "retail")
        
        # Get industry-specific tools
        industry_tools = self.tool_configs.get(industry_code, [])
        
        # In a real implementation, this would be more sophisticated
        # For now, we'll just return all tools for the industry
        logger.info(f"Selected {len(industry_tools)} tools for {industry_code} business")
        return industry_tools
    
    def generate_agent_config(self, domain: str, business_profile: Dict[str, Any], 
                             model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate configuration for a domain-specific agent.
        
        Args:
            domain: The analytics domain (descriptive, diagnostic, predictive, prescriptive, cognitive).
            business_profile: The business profile.
            model_config: The model configuration.
            
        Returns:
            A dictionary containing the agent configuration.
        """
        # Customize prompt
        prompt = self.customize_prompt(domain, business_profile)
        
        # Create agent configuration
        agent_config = {
            "name": f"{domain.capitalize()}AnalyticsAgent",
            "domain": domain,
            "description": f"{domain.capitalize()} analytics for {business_profile.get('name', 'Business')}",
            "prompt": prompt,
            "model": model_config,
            "tools": self.select_tools(business_profile),
            "parameters": {
                "temperature": 0.7 if domain == "cognitive" else 0.3,
                "top_p": 0.9,
                "max_tokens": 1000
            }
        }
        
        logger.info(f"Generated configuration for {domain} analytics agent")
        return agent_config
    
    def generate_framework(self, business_profile: Dict[str, Any], 
                          model_configs: Dict[str, Dict[str, Any]],
                          output_dir: str,
                          deployment_type: str = "local") -> str:
        """
        Generate a complete agent framework for a specific business.
        
        Args:
            business_profile: The business profile.
            model_configs: Configurations for models for each domain.
            output_dir: Directory to output the generated framework.
            deployment_type: Type of deployment (local or cloud).
            
        Returns:
            Path to the generated framework.
        """
        business_name = business_profile.get("name", "Business")
        sanitized_name = business_name.lower().replace(" ", "_")
        framework_dir = os.path.join(output_dir, f"{sanitized_name}_framework")
        
        logger.info(f"Generating framework for {business_name} in {framework_dir}")
        
        # Create framework directory
        os.makedirs(framework_dir, exist_ok=True)
        
        # Get framework template
        template = self.framework_templates.get(deployment_type, self.framework_templates.get("local", {}))
        
        # Create directory structure
        for dir_name, subdirs in template.get("directory_structure", {}).items():
            dir_path = os.path.join(framework_dir, dir_name)
            os.makedirs(dir_path, exist_ok=True)
            
            for subdir in subdirs:
                subdir_path = os.path.join(dir_path, subdir)
                os.makedirs(subdir_path, exist_ok=True)
        
        # Create requirements.txt
        with open(os.path.join(framework_dir, "requirements.txt"), "w") as f:
            f.write("\n".join(template.get("requirements", [])))
        
        # Create README.md
        with open(os.path.join(framework_dir, "README.md"), "w") as f:
            f.write(f"""# {business_name} Analytics Framework

This framework provides specialized analytics agents for {business_name}.

## Features

- Descriptive Analytics: Historical data analysis and pattern recognition
- Diagnostic Analytics: Root cause analysis and problem identification
- Predictive Analytics: Forecasting and trend projection
- Prescriptive Analytics: Action recommendation and optimization
- Cognitive Analytics: Unstructured data processing and human-like reasoning

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Web Interface

```bash
python app.py
```

### Command Line Interface

```bash
python cli.py --help
```
""")
        
        # Generate agent configurations
        agent_configs = {}
        for domain in ["descriptive", "diagnostic", "predictive", "prescriptive", "cognitive"]:
            model_config = model_configs.get(domain, {})
            agent_config = self.generate_agent_config(domain, business_profile, model_config)
            agent_configs[domain] = agent_config
            
            # Write agent configuration
            agent_dir = os.path.join(framework_dir, "agents", domain)
            with open(os.path.join(agent_dir, "config.json"), "w") as f:
                json.dump(agent_config, f, indent=2)
            
            # Write agent implementation
            with open(os.path.join(agent_dir, "agent.py"), "w") as f:
                f.write(f"""\"\"\"
{domain.capitalize()} Analytics Agent for {business_name}

This module implements the {domain.capitalize()} Analytics Agent, which {self._get_agent_description(domain)}.
\"\"\"

import logging
import json
from typing import Dict, Any, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class {domain.capitalize()}AnalyticsAgent:
    \"\"\"
    {domain.capitalize()} Analytics Agent for {business_name}.
    
    This agent {self._get_agent_description(domain)}.
    \"\"\"
    
    def __init__(self, config_path: str = None):
        \"\"\"
        Initialize the agent.
        
        Args:
            config_path: Path to the agent configuration file.
        \"\"\"
        self.config = None
        if config_path:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            # Use default configuration
            self.config = {json.dumps(agent_config, indent=2)}
        
        logger.info(f"Initialized {domain.capitalize()} Analytics Agent")
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Analyze data and provide {domain} insights.
        
        Args:
            data: The data to analyze.
            
        Returns:
            A dictionary containing analysis results.
        \"\"\"
        logger.info(f"Performing {domain} analysis")
        
        # In a real implementation, this would use the configured model to analyze the data
        # For now, we'll just return a placeholder result
        
        return {{
            "analysis_type": "{domain}",
            "results": f"Sample {domain} analysis results for {{data.get('name', 'unknown')}}",
            "confidence": 0.85
        }}
    
    def get_tools(self) -> List[Dict[str, Any]]:
        \"\"\"
        Get the tools available to this agent.
        
        Returns:
            A list of tool configurations.
        \"\"\"
        return self.config.get("tools", [])
""")
        
        # Create knowledge base
        knowledge_base = self.create_knowledge_base(business_profile)
        
        # Write industry knowledge
        industry_dir = os.path.join(framework_dir, "knowledge", "industry")
        for key, knowledge_item in knowledge_base["industry"].items():
            with open(os.path.join(industry_dir, f"{key}.md"), "w") as f:
                f.write(knowledge_item["content"])
        
        # Write business-specific knowledge
        business_dir = os.path.join(framework_dir, "knowledge", "business_specific")
        for key, knowledge_item in knowledge_base["business_specific"].items():
            with open(os.path.join(business_dir, f"{key}.md"), "w") as f:
                f.write(knowledge_item["content"])
        
        # Create entry points
        for entry_name, entry_file in template.get("entry_points", {}).items():
            if entry_name == "cli":
                with open(os.path.join(framework_dir, entry_file), "w") as f:
                    f.write(f"""#!/usr/bin/env python
\"\"\"
Command Line Interface for {business_name} Analytics Framework
\"\"\"

import argparse
import logging
import json
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.descriptive.agent import DescriptiveAnalyticsAgent
from agents.diagnostic.agent import DiagnosticAnalyticsAgent
from agents.predictive.agent import PredictiveAnalyticsAgent
from agents.prescriptive.agent import PrescriptiveAnalyticsAgent
from agents.cognitive.agent import CognitiveAnalyticsAgent

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='{business_name} Analytics Framework')
    parser.add_argument('--domain', choices=['descriptive', 'diagnostic', 'predictive', 'prescriptive', 'cognitive'],
                        help='Analytics domain to use')
    parser.add_argument('--data', type=str, help='Path to data file for analysis')
    parser.add_argument('--output', type=str, help='Path to output file for results')
    
    args = parser.parse_args()
    
    if not args.domain:
        parser.print_help()
        return
    
    # Load data
    data = {{}}
    if args.data:
        with open(args.data, 'r') as f:
            data = json.load(f)
    
    # Create agent
    agent = None
    if args.domain == 'descriptive':
        agent = DescriptiveAnalyticsAgent('agents/descriptive/config.json')
    elif args.domain == 'diagnostic':
        agent = DiagnosticAnalyticsAgent('agents/diagnostic/config.json')
    elif args.domain == 'predictive':
        agent = PredictiveAnalyticsAgent('agents/predictive/config.json')
    elif args.domain == 'prescriptive':
        agent = PrescriptiveAnalyticsAgent('agents/prescriptive/config.json')
    elif args.domain == 'cognitive':
        agent = CognitiveAnalyticsAgent('agents/cognitive/config.json')
    
    # Perform analysis
    results = agent.analyze(data)
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
    else:
        print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
""")
            elif entry_name == "web":
                with open(os.path.join(framework_dir, entry_file), "w") as f:
                    f.write(f"""#!/usr/bin/env python
\"\"\"
Web Interface for {business_name} Analytics Framework
\"\"\"

import streamlit as st
import json
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.descriptive.agent import DescriptiveAnalyticsAgent
from agents.diagnostic.agent import DiagnosticAnalyticsAgent
from agents.predictive.agent import PredictiveAnalyticsAgent
from agents.prescriptive.agent import PrescriptiveAnalyticsAgent
from agents.cognitive.agent import CognitiveAnalyticsAgent

# Initialize agents
descriptive_agent = DescriptiveAnalyticsAgent('agents/descriptive/config.json')
diagnostic_agent = DiagnosticAnalyticsAgent('agents/diagnostic/config.json')
predictive_agent = PredictiveAnalyticsAgent('agents/predictive/config.json')
prescriptive_agent = PrescriptiveAnalyticsAgent('agents/prescriptive/config.json')
cognitive_agent = CognitiveAnalyticsAgent('agents/cognitive/config.json')

# Set up the Streamlit app
st.title('{business_name} Analytics Framework')

st.sidebar.header('Analytics Domain')
domain = st.sidebar.selectbox('Select Domain', 
                             ['Descriptive', 'Diagnostic', 'Predictive', 'Prescriptive', 'Cognitive'])

st.sidebar.header('Data Input')
data_input = st.sidebar.text_area('Enter JSON data for analysis', '{{"name": "Sample Data"}}')

if st.sidebar.button('Analyze'):
    try:
        data = json.loads(data_input)
        
        st.header(f'{{domain}} Analytics Results')
        
        if domain == 'Descriptive':
            results = descriptive_agent.analyze(data)
        elif domain == 'Diagnostic':
            results = diagnostic_agent.analyze(data)
        elif domain == 'Predictive':
            results = predictive_agent.analyze(data)
        elif domain == 'Prescriptive':
            results = prescriptive_agent.analyze(data)
        elif domain == 'Cognitive':
            results = cognitive_agent.analyze(data)
        
        st.json(results)
        
    except json.JSONDecodeError:
        st.error('Invalid JSON data. Please check your input.')
    except Exception as e:
        st.error(f'Error during analysis: {{str(e)}}')

st.sidebar.header('Available Tools')
tool_domain = st.sidebar.selectbox('Select Domain for Tools', 
                                 ['Descriptive', 'Diagnostic', 'Predictive', 'Prescriptive', 'Cognitive'])

if tool_domain == 'Descriptive':
    tools = descriptive_agent.get_tools()
elif tool_domain == 'Diagnostic':
    tools = diagnostic_agent.get_tools()
elif tool_domain == 'Predictive':
    tools = predictive_agent.get_tools()
elif tool_domain == 'Prescriptive':
    tools = prescriptive_agent.get_tools()
elif tool_domain == 'Cognitive':
    tools = cognitive_agent.get_tools()

st.header(f'{{tool_domain}} Analytics Tools')
for tool in tools:
    st.subheader(tool.get('name', 'Unknown Tool'))
    st.write(tool.get('description', 'No description available'))
    st.write('Parameters:')
    st.json(tool.get('parameters', {{}}))
    st.write('---')
""")
            elif entry_name == "api":
                with open(os.path.join(framework_dir, entry_file), "w") as f:
                    f.write(f"""#!/usr/bin/env python
\"\"\"
API for {business_name} Analytics Framework
\"\"\"

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
import sys
from typing import Dict, Any, List, Optional

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.descriptive.agent import DescriptiveAnalyticsAgent
from agents.diagnostic.agent import DiagnosticAnalyticsAgent
from agents.predictive.agent import PredictiveAnalyticsAgent
from agents.prescriptive.agent import PrescriptiveAnalyticsAgent
from agents.cognitive.agent import CognitiveAnalyticsAgent

# Initialize agents
descriptive_agent = DescriptiveAnalyticsAgent('agents/descriptive/config.json')
diagnostic_agent = DiagnosticAnalyticsAgent('agents/diagnostic/config.json')
predictive_agent = PredictiveAnalyticsAgent('agents/predictive/config.json')
prescriptive_agent = PrescriptiveAnalyticsAgent('agents/prescriptive/config.json')
cognitive_agent = CognitiveAnalyticsAgent('agents/cognitive/config.json')

app = FastAPI(title="{business_name} Analytics API")

class AnalysisRequest(BaseModel):
    data: Dict[str, Any]

@app.get("/")
def read_root():
    return {{"message": "Welcome to the {business_name} Analytics API"}}

@app.post("/analyze/descriptive")
def analyze_descriptive(request: AnalysisRequest):
    try:
        results = descriptive_agent.analyze(request.data)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/diagnostic")
def analyze_diagnostic(request: AnalysisRequest):
    try:
        results = diagnostic_agent.analyze(request.data)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/predictive")
def analyze_predictive(request: AnalysisRequest):
    try:
        results = predictive_agent.analyze(request.data)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/prescriptive")
def analyze_prescriptive(request: AnalysisRequest):
    try:
        results = prescriptive_agent.analyze(request.data)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/cognitive")
def analyze_cognitive(request: AnalysisRequest):
    try:
        results = cognitive_agent.analyze(request.data)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/{{domain}}")
def get_tools(domain: str):
    if domain == "descriptive":
        return descriptive_agent.get_tools()
    elif domain == "diagnostic":
        return diagnostic_agent.get_tools()
    elif domain == "predictive":
        return predictive_agent.get_tools()
    elif domain == "prescriptive":
        return prescriptive_agent.get_tools()
    elif domain == "cognitive":
        return cognitive_agent.get_tools()
    else:
        raise HTTPException(status_code=404, detail=f"Domain {{domain}} not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
""")
        
        # Create main package file
        with open(os.path.join(framework_dir, "__init__.py"), "w") as f:
            f.write(f"""\"\"\"
{business_name} Analytics Framework

This framework provides specialized analytics agents for {business_name}.
\"\"\"

__version__ = "1.0.0"
""")
        
        # Create setup.py
        with open(os.path.join(framework_dir, "setup.py"), "w") as f:
            f.write(f"""from setuptools import setup, find_packages

setup(
    name="{sanitized_name}_analytics",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        {", ".join([f'"{req}"' for req in template.get("requirements", [])])}
    ],
    author="BDFG Framework",
    author_email="info@bdfg.example.com",
    description="{business_name} Analytics Framework",
    keywords="analytics, business intelligence, AI",
    python_requires=">=3.8",
)
""")
        
        logger.info(f"Generated framework for {business_name} in {framework_dir}")
        return framework_dir
    
    def package_framework(self, framework_dir: str, output_file: str = None) -> str:
        """
        Package a generated framework into a distributable format.
        
        Args:
            framework_dir: Directory containing the generated framework.
            output_file: Path to the output package file.
            
        Returns:
            Path to the packaged framework.
        """
        if output_file is None:
            output_file = f"{framework_dir}.zip"
        
        logger.info(f"Packaging framework from {framework_dir} to {output_file}")
        
        # Create a zip file
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(framework_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(framework_dir))
                    zipf.write(file_path, arcname)
        
        logger.info(f"Framework packaged to {output_file}")
        return output_file
    
    def _get_agent_description(self, domain: str) -> str:
        """
        Get a description for a domain-specific agent.
        
        Args:
            domain: The analytics domain.
            
        Returns:
            A description string.
        """
        if domain == "descriptive":
            return "analyzes historical data to identify patterns and trends"
        elif domain == "diagnostic":
            return "determines why certain events occurred by identifying root causes"
        elif domain == "predictive":
            return "forecasts future trends and outcomes based on historical data"
        elif domain == "prescriptive":
            return "recommends actions to optimize business outcomes"
        elif domain == "cognitive":
            return "analyzes unstructured data like text, images, and human feedback"
        else:
            return "provides analytics capabilities"
