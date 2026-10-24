"""
Enhanced BDFG Framework - Test Script

This script tests the functionality of the Enhanced BDFG Framework components.
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path to import the enhanced_bdfg package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from enhanced_bdfg.core.business_profiler import BusinessProfiler
    from enhanced_bdfg.core.model_selector import ModelSelector
    from enhanced_bdfg.core.hardware_manager import HardwareManager
    from enhanced_bdfg.core.resource_manager import ResourceManager
    from enhanced_bdfg.core.agent_generator import AgentGenerator
    from enhanced_bdfg.core.framework_controller import FrameworkController
    from enhanced_bdfg.core.prompt_engineering import PromptEngineer
    from enhanced_bdfg.core.framework_packager import FrameworkPackager

    from enhanced_bdfg.modules.descriptive_analytics import DescriptiveAnalytics
    from enhanced_bdfg.modules.diagnostic_analytics import DiagnosticAnalytics
    from enhanced_bdfg.modules.predictive_analytics import PredictiveAnalytics
    from enhanced_bdfg.modules.prescriptive_analytics import PrescriptiveAnalytics
    from enhanced_bdfg.modules.cognitive_analytics import CognitiveAnalytics
    
    logger.info("Successfully imported all Enhanced BDFG Framework components")
except ImportError as e:
    logger.error(f"Error importing Enhanced BDFG Framework components: {e}")
    sys.exit(1)

def create_test_data():
    """Create sample data for testing the framework components."""
    logger.info("Creating test data...")
    
    # Create sample business profile data
    business_profile = {
        "name": "Sample Business",
        "industry": "Retail",
        "size": "Medium",
        "annual_revenue": 5000000,
        "employees": 120,
        "data_maturity": "Intermediate",
        "tech_stack": ["Python", "SQL", "Tableau", "AWS"],
        "business_objectives": [
            {"name": "Increase Sales", "priority": "High"},
            {"name": "Reduce Costs", "priority": "Medium"},
            {"name": "Improve Customer Satisfaction", "priority": "High"}
        ]
    }
    
    # Create sample time series data for analytics modules
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    n = len(dates)
    
    # Create sales data with trend, seasonality, and noise
    trend = np.linspace(1000, 1500, n)  # Upward trend
    seasonality = 200 * np.sin(np.linspace(0, 2*np.pi*12, n))  # Yearly seasonality
    weekly = 100 * (np.arange(n) % 7 < 5).astype(float)  # Weekly pattern (weekday vs weekend)
    noise = np.random.normal(0, 50, n)  # Random noise
    
    sales = trend + seasonality + weekly + noise
    
    # Create customer data
    customer_satisfaction = np.random.normal(4.0, 0.5, n)  # Customer satisfaction scores (1-5)
    customer_satisfaction = np.clip(customer_satisfaction, 1, 5)
    
    # Create cost data
    costs = trend * 0.6 + np.random.normal(0, 30, n)  # Costs as percentage of sales plus noise
    
    # Combine into DataFrame
    df = pd.DataFrame({
        'date': dates,
        'sales': sales,
        'costs': costs,
        'profit': sales - costs,
        'customer_satisfaction': customer_satisfaction,
        'day_of_week': dates.dayofweek,
        'month': dates.month
    })
    
    # Create sample text data for cognitive analytics
    sample_texts = [
        "Our customers have been very satisfied with the new product line. The quality and pricing are excellent.",
        "Several customers complained about shipping delays last month. We need to improve our logistics.",
        "The marketing campaign exceeded expectations with a 25% increase in website traffic.",
        "The quarterly financial results show a 15% increase in revenue compared to last year.",
        "Employee satisfaction survey indicates high morale but concerns about work-life balance."
    ]
    
    # Create sample model requirements for model selector
    model_requirements = {
        "task_type": "classification",
        "data_size": "medium",
        "interpretability": "high",
        "performance_priority": "accuracy",
        "deployment_environment": "cloud",
        "training_time_constraint": "medium",
        "available_hardware": ["cpu", "standard_gpu"]
    }
    
    # Create sample hardware specifications
    hardware_specs = {
        "cpu": {
            "cores": 8,
            "memory": 32,
            "type": "Intel Xeon"
        },
        "gpu": {
            "count": 1,
            "memory": 16,
            "type": "NVIDIA T4"
        },
        "storage": {
            "capacity": 1000,
            "type": "SSD"
        },
        "network": {
            "bandwidth": "10Gbps"
        }
    }
    
    # Create sample resource allocation
    resource_allocation = {
        "data_processing": {
            "cpu_cores": 4,
            "memory": 16,
            "priority": "high"
        },
        "model_training": {
            "cpu_cores": 6,
            "gpu_memory": 12,
            "memory": 24,
            "priority": "high"
        },
        "inference": {
            "cpu_cores": 2,
            "gpu_memory": 4,
            "memory": 8,
            "priority": "medium"
        }
    }
    
    # Create sample agent configuration
    agent_config = {
        "agent_type": "data_processing",
        "capabilities": ["data_cleaning", "feature_engineering", "data_transformation"],
        "execution_mode": "batch",
        "input_format": "csv",
        "output_format": "parquet",
        "logging_level": "info",
        "max_runtime": 3600
    }
    
    # Create sample prompt templates
    prompt_templates = {
        "data_analysis": "Analyze the following data and provide insights: {data}",
        "model_explanation": "Explain the following model results in simple terms: {results}",
        "recommendation": "Based on the analysis, recommend actions for: {objective}"
    }
    
    # Save test data to files
    os.makedirs("test_data", exist_ok=True)
    
    # Save business profile
    with open("test_data/business_profile.json", "w") as f:
        json.dump(business_profile, f, indent=2)
    
    # Save time series data
    df.to_csv("test_data/time_series_data.csv", index=False)
    
    # Save text data
    with open("test_data/sample_texts.txt", "w") as f:
        f.write("\n\n".join(sample_texts))
    
    # Save model requirements
    with open("test_data/model_requirements.json", "w") as f:
        json.dump(model_requirements, f, indent=2)
    
    # Save hardware specs
    with open("test_data/hardware_specs.json", "w") as f:
        json.dump(hardware_specs, f, indent=2)
    
    # Save resource allocation
    with open("test_data/resource_allocation.json", "w") as f:
        json.dump(resource_allocation, f, indent=2)
    
    # Save agent config
    with open("test_data/agent_config.json", "w") as f:
        json.dump(agent_config, f, indent=2)
    
    # Save prompt templates
    with open("test_data/prompt_templates.json", "w") as f:
        json.dump(prompt_templates, f, indent=2)
    
    logger.info("Test data created successfully")
    return {
        "business_profile": business_profile,
        "time_series_data": df,
        "sample_texts": sample_texts,
        "model_requirements": model_requirements,
        "hardware_specs": hardware_specs,
        "resource_allocation": resource_allocation,
        "agent_config": agent_config,
        "prompt_templates": prompt_templates
    }

def test_business_profiler(test_data):
    """Test the BusinessProfiler component."""
    logger.info("Testing BusinessProfiler...")
    
    try:
        # Initialize BusinessProfiler
        profiler = BusinessProfiler()
        
        # Test profile creation
        profile = profiler.create_profile(
            name=test_data["business_profile"]["name"],
            industry=test_data["business_profile"]["industry"],
            size=test_data["business_profile"]["size"],
            annual_revenue=test_data["business_profile"]["annual_revenue"],
            employees=test_data["business_profile"]["employees"],
            data_maturity=test_data["business_profile"]["data_maturity"],
            tech_stack=test_data["business_profile"]["tech_stack"],
            business_objectives=test_data["business_profile"]["business_objectives"]
        )
        
        # Test profile validation
        validation_result = profiler.validate_profile(profile)
        
        # Test profile analysis
        analysis_result = profiler.analyze_profile(profile)
        
        # Test recommendation generation
        recommendations = profiler.generate_recommendations(profile)
        
        logger.info("BusinessProfiler tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"BusinessProfiler test failed: {e}")
        return False

def test_model_selector(test_data):
    """Test the ModelSelector component."""
    logger.info("Testing ModelSelector...")
    
    try:
        # Initialize ModelSelector
        selector = ModelSelector()
        
        # Test model selection
        selected_model = selector.select_model(test_data["model_requirements"])
        
        # Test model evaluation
        evaluation_criteria = {
            "accuracy": 0.85,
            "precision": 0.82,
            "recall": 0.88,
            "f1_score": 0.85,
            "training_time": 120,
            "inference_time": 0.05
        }
        evaluation_result = selector.evaluate_model(selected_model, evaluation_criteria)
        
        # Test model comparison
        alternative_model = selector.select_alternative_models(test_data["model_requirements"], count=2)
        comparison_result = selector.compare_models([selected_model] + alternative_model)
        
        logger.info("ModelSelector tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"ModelSelector test failed: {e}")
        return False

def test_hardware_manager(test_data):
    """Test the HardwareManager component."""
    logger.info("Testing HardwareManager...")
    
    try:
        # Initialize HardwareManager
        manager = HardwareManager()
        
        # Test hardware assessment
        assessment = manager.assess_hardware(test_data["hardware_specs"])
        
        # Test hardware recommendation
        recommendation = manager.recommend_hardware(test_data["model_requirements"])
        
        # Test optimization
        optimization = manager.optimize_hardware_usage(test_data["hardware_specs"], test_data["resource_allocation"])
        
        # Test scaling plan
        scaling_plan = manager.create_scaling_plan(test_data["hardware_specs"], growth_projection=0.2)
        
        logger.info("HardwareManager tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"HardwareManager test failed: {e}")
        return False

def test_resource_manager(test_data):
    """Test the ResourceManager component."""
    logger.info("Testing ResourceManager...")
    
    try:
        # Initialize ResourceManager
        manager = ResourceManager()
        
        # Test resource allocation
        allocation = manager.allocate_resources(test_data["resource_allocation"])
        
        # Test resource monitoring
        monitoring_config = manager.configure_monitoring(allocation)
        
        # Test resource optimization
        optimization = manager.optimize_resources(allocation, test_data["hardware_specs"])
        
        # Test resource scaling
        scaling_plan = manager.plan_resource_scaling(allocation, growth_factor=1.5)
        
        logger.info("ResourceManager tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"ResourceManager test failed: {e}")
        return False

def test_agent_generator(test_data):
    """Test the AgentGenerator component."""
    logger.info("Testing AgentGenerator...")
    
    try:
        # Initialize AgentGenerator
        generator = AgentGenerator()
        
        # Test agent creation
        agent = generator.create_agent(test_data["agent_config"])
        
        # Test agent validation
        validation = generator.validate_agent(agent)
        
        # Test agent deployment
        deployment_config = generator.prepare_deployment(agent, environment="development")
        
        # Test agent orchestration
        orchestration = generator.configure_orchestration([agent], execution_order="sequential")
        
        logger.info("AgentGenerator tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"AgentGenerator test failed: {e}")
        return False

def test_framework_controller(test_data):
    """Test the FrameworkController component."""
    logger.info("Testing FrameworkController...")
    
    try:
        # Initialize FrameworkController
        controller = FrameworkController()
        
        # Test initialization
        initialization = controller.initialize_framework(
            business_profile=test_data["business_profile"],
            hardware_specs=test_data["hardware_specs"],
            resource_allocation=test_data["resource_allocation"]
        )
        
        # Test workflow creation
        workflow = controller.create_workflow("data_analysis", [
            {"step": "data_loading", "config": {"source": "test_data/time_series_data.csv"}},
            {"step": "data_processing", "config": {"operations": ["cleaning", "normalization"]}},
            {"step": "analysis", "config": {"type": "descriptive"}}
        ])
        
        # Test execution
        execution_result = controller.execute_workflow(workflow)
        
        # Test monitoring
        monitoring_result = controller.monitor_execution(execution_id=execution_result["execution_id"])
        
        logger.info("FrameworkController tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"FrameworkController test failed: {e}")
        return False

def test_prompt_engineer(test_data):
    """Test the PromptEngineer component."""
    logger.info("Testing PromptEngineer...")
    
    try:
        # Initialize PromptEngineer
        engineer = PromptEngineer()
        
        # Test template creation
        template = engineer.create_template(
            name="custom_analysis",
            template="Analyze the following {data_type} data and provide insights on {focus_area}: {data}"
        )
        
        # Test prompt generation
        prompt = engineer.generate_prompt(
            template_name="custom_analysis",
            parameters={
                "data_type": "time series",
                "focus_area": "sales trends",
                "data": "Monthly sales data for 2023"
            }
        )
        
        # Test template management
        templates = engineer.list_templates()
        
        # Test template optimization
        optimization = engineer.optimize_template("custom_analysis", optimization_criteria={"clarity": 0.8, "specificity": 0.9})
        
        logger.info("PromptEngineer tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"PromptEngineer test failed: {e}")
        return False

def test_framework_packager(test_data):
    """Test the FrameworkPackager component."""
    logger.info("Testing FrameworkPackager...")
    
    try:
        # Initialize FrameworkPackager
        packager = FrameworkPackager()
        
        # Test configuration creation
        config = packager.create_configuration(
            business_profile=test_data["business_profile"],
            model_requirements=test_data["model_requirements"],
            hardware_specs=test_data["hardware_specs"],
            resource_allocation=test_data["resource_allocation"]
        )
        
        # Test package creation
        package = packager.create_package(
            config=config,
            output_format="json",
            include_documentation=True
        )
        
        # Test deployment preparation
        deployment_package = packager.prepare_deployment(
            package=package,
            environment="development",
            deployment_type="container"
        )
        
        # Test documentation generation
        documentation = packager.generate_documentation(
            package=package,
            doc_format="markdown"
        )
        
        logger.info("FrameworkPackager tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"FrameworkPackager test failed: {e}")
        return False

def test_descriptive_analytics(test_data):
    """Test the DescriptiveAnalytics module."""
    logger.info("Testing DescriptiveAnalytics...")
    
    try:
        # Initialize DescriptiveAnalytics
        analytics = DescriptiveAnalytics()
        
        # Test data summary
        summary = analytics.summarize_data(test_data["time_series_data"])
        
        # Test statistical analysis
        stats = analytics.calculate_statistics(test_data["time_series_data"], columns=["sales", "costs", "profit"])
        
        # Test trend analysis
        trends = analytics.analyze_trends(test_data["time_series_data"], time_column="date", value_column="sales")
        
        # Test correlation analysis
        correlations = analytics.analyze_correlations(test_data["time_series_data"], columns=["sales", "costs", "profit", "customer_satisfaction"])
        
        # Test comprehensive analysis
        comprehensive = analytics.analyze(test_data["time_series_data"])
        
        logger.info("DescriptiveAnalytics tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"DescriptiveAnalytics test failed: {e}")
        return False

def test_diagnostic_analytics(test_data):
    """Test the DiagnosticAnalytics module."""
    logger.info("Testing DiagnosticAnalytics...")
    
    try:
        # Initialize DiagnosticAnalytics
        analytics = DiagnosticAnalytics()
        
        # Test anomaly detection
        anomalies = analytics.detect_anomalies(test_data["time_series_data"], column="sales")
        
        # Test root cause analysis
        root_causes = analytics.analyze_root_causes(
            data=test_data["time_series_data"],
            target_column="profit",
            event_date="2023-06-15",
            window_size=7
        )
        
        # Test factor analysis
        factors = analytics.analyze_contributing_factors(
            data=test_data["time_series_data"],
            target_column="sales",
            factor_columns=["day_of_week", "month", "customer_satisfaction"]
        )
        
        # Test pattern recognition
        patterns = analytics.identify_patterns(
            data=test_data["time_series_data"],
            time_column="date",
            value_column="sales"
        )
        
        # Test comprehensive analysis
        comprehensive = analytics.analyze(
            data=test_data["time_series_data"],
            target_column="profit"
        )
        
        logger.info("DiagnosticAnalytics tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"DiagnosticAnalytics test failed: {e}")
        return False

def test_predictive_analytics(test_data):
    """Test the PredictiveAnalytics module."""
    logger.info("Testing PredictiveAnalytics...")
    
    try:
        # Initialize PredictiveAnalytics
        analytics = PredictiveAnalytics()
        
        # Test time series forecasting
        forecast = analytics.forecast_time_series(
            data=test_data["time_series_data"],
            time_column="date",
            target_column="sales",
            horizon=30
        )
        
        # Test regression model
        regression = analytics.build_regression_model(
            data=test_data["time_series_data"],
            target_column="profit",
            feature_columns=["sales", "costs", "customer_satisfaction"]
        )
        
        # Test scenario generation
        scenarios = analytics.generate_scenarios(
            data=test_data["time_series_data"],
            time_column="date",
            target_column="sales",
            horizon=30,
            num_scenarios=3
        )
        
        # Test comprehensive analysis
        comprehensive = analytics.analyze(
            data=test_data["time_series_data"],
            time_column="date",
            target_column="sales"
        )
        
        logger.info("PredictiveAnalytics tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"PredictiveAnalytics test failed: {e}")
        return False

def test_prescriptive_analytics(test_data):
    """Test the PrescriptiveAnalytics module."""
    logger.info("Testing PrescriptiveAnalytics...")
    
    try:
        # Initialize PrescriptiveAnalytics
        analytics = PrescriptiveAnalytics()
        
        # Test resource optimization
        resources = [
            {"name": "Marketing Budget", "cost": 1000, "capacity": 10000, "profit": 2.5},
            {"name": "Production Capacity", "cost": 500, "capacity": 5000, "profit": 1.8},
            {"name": "Staff Hours", "cost": 50, "capacity": 2000, "profit": 1.2}
        ]
        
        constraints = [
            {"coefficients": [1, 0.5, 0.1], "bound": 15000},
            {"coefficients": [0.1, 1, 0.2], "bound": 6000}
        ]
        
        optimization = analytics.optimize_resource_allocation(
            data=test_data["time_series_data"],
            resources=resources,
            constraints=constraints,
            objective="maximize_profit"
        )
        
        # Test decision analysis
        options = [
            {"name": "Option A", "cost": 5000, "expected_return": 8000, "risk": 0.3, "implementation_time": 30},
            {"name": "Option B", "cost": 3000, "expected_return": 5000, "risk": 0.2, "implementation_time": 15},
            {"name": "Option C", "cost": 8000, "expected_return": 12000, "risk": 0.4, "implementation_time": 60}
        ]
        
        criteria = [
            {"name": "cost", "direction": "minimize"},
            {"name": "expected_return", "direction": "maximize"},
            {"name": "risk", "direction": "minimize"},
            {"name": "implementation_time", "direction": "minimize"}
        ]
        
        weights = {"cost": 0.3, "expected_return": 0.4, "risk": 0.2, "implementation_time": 0.1}
        
        decision = analytics.analyze_decision_options(
            options=options,
            criteria=criteria,
            weights=weights
        )
        
        # Test action plan generation
        objectives = [
            {"id": "obj1", "name": "Increase Sales", "weight": 0.5, "baseline": 1000, "target": 1200},
            {"id": "obj2", "name": "Reduce Costs", "weight": 0.3, "baseline": 600, "target": 500},
            {"id": "obj3", "name": "Improve Satisfaction", "weight": 0.2, "baseline": 3.8, "target": 4.5}
        ]
        
        actions = [
            {"id": "act1", "name": "Marketing Campaign", "cost": 5000, "duration": 30, "categories": ["marketing", "sales"],
             "impacts": {"obj1": 0.3, "obj3": 0.1}},
            {"id": "act2", "name": "Process Optimization", "cost": 3000, "duration": 45, "categories": ["operations", "costs"],
             "impacts": {"obj2": 0.4}},
            {"id": "act3", "name": "Staff Training", "cost": 2000, "duration": 15, "categories": ["hr", "service"],
             "impacts": {"obj3": 0.3, "obj1": 0.1}}
        ]
        
        action_plan = analytics.generate_action_plan(
            objectives=objectives,
            actions=actions,
            constraints={"max_cost": 8000, "max_duration": 60}
        )
        
        # Test comprehensive analysis
        comprehensive = analytics.analyze(
            data=test_data["time_series_data"],
            objectives=objectives,
            possible_actions=actions
        )
        
        logger.info("PrescriptiveAnalytics tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"PrescriptiveAnalytics test failed: {e}")
        return False

def test_cognitive_analytics(test_data):
    """Test the CognitiveAnalytics module."""
    logger.info("Testing CognitiveAnalytics...")
    
    try:
        # Initialize CognitiveAnalytics
        analytics = CognitiveAnalytics()
        
        # Test text analysis
        text_analysis = analytics.analyze_text(test_data["sample_texts"][0])
        
        # Test sentiment analysis
        sentiment = analytics.analyze_sentiment(test_data["sample_texts"][0])
        
        # Test entity extraction
        entities = analytics.extract_entities(test_data["sample_texts"][0])
        
        # Test keyword extraction
        keywords = analytics.extract_keywords(test_data["sample_texts"][0])
        
        # Test text collection analysis
        collection_analysis = analytics.analyze_text_collection(test_data["sample_texts"])
        
        # Test comprehensive analysis
        comprehensive = analytics.analyze(test_data["sample_texts"][0], analysis_type="text")
        
        logger.info("CognitiveAnalytics tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"CognitiveAnalytics test failed: {e}")
        return False

def run_all_tests():
    """Run all component tests."""
    logger.info("Starting Enhanced BDFG Framework tests...")
    
    # Create test data
    test_data = create_test_data()
    
    # Run component tests
    test_results = {
        "BusinessProfiler": test_business_profiler(test_data),
        "ModelSelector": test_model_selector(test_data),
        "HardwareManager": test_hardware_manager(test_data),
        "ResourceManager": test_resource_manager(test_data),
        "AgentGenerator": test_agent_generator(test_data),
        "FrameworkController": test_framework_controller(test_data),
        "PromptEngineer": test_prompt_engineer(test_data),
        "FrameworkPackager": test_framework_packager(test_data),
        "DescriptiveAnalytics": test_descriptive_analytics(test_data),
        "DiagnosticAnalytics": test_diagnostic_analytics(test_data),
        "PredictiveAnalytics": test_predictive_analytics(test_data),
        "PrescriptiveAnalytics": test_prescriptive_analytics(test_data),
        "CognitiveAnalytics": test_cognitive_analytics(test_data)
    }
    
    # Print test summary
    logger.info("Test Summary:")
    all_passed = True
    for component, result in test_results.items():
        status = "PASSED" if result else "FAILED"
        if not result:
            all_passed = False
        logger.info(f"{component}: {status}")
    
    if all_passed:
        logger.info("All tests passed successfully!")
    else:
        logger.warning("Some tests failed. Check the logs for details.")
    
    return test_results

if __name__ == "__main__":
    run_all_tests()
