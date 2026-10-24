# Usage Examples

## Basic Usage

### Initializing the Framework

```python
from enhanced_bdfg.core.business_profiler import BusinessProfiler
from enhanced_bdfg.core.framework_controller import FrameworkController

# Create a business profile
profiler = BusinessProfiler()
profile = profiler.create_profile(
    name="Sample Business",
    industry="Retail",
    size="Medium",
    annual_revenue=5000000,
    employees=120,
    data_maturity="Intermediate",
    tech_stack=["Python", "SQL", "Tableau", "AWS"],
    business_objectives=[
        {"name": "Increase Sales", "priority": "High"},
        {"name": "Reduce Costs", "priority": "Medium"},
        {"name": "Improve Customer Satisfaction", "priority": "High"}
    ]
)

# Initialize the framework controller
controller = FrameworkController()
controller.initialize_framework(business_profile=profile)
```

### Creating and Executing a Workflow

```python
# Create a workflow
workflow = controller.create_workflow("data_analysis", [
    {"step": "data_loading", "config": {"source": "sales_data.csv"}},
    {"step": "data_processing", "config": {"operations": ["cleaning", "normalization"]}},
    {"step": "analysis", "config": {"type": "descriptive"}}
])

# Execute the workflow
result = controller.execute_workflow(workflow)
```

## Analytics Examples

### Descriptive Analytics

```python
import pandas as pd
from enhanced_bdfg.modules.descriptive_analytics import DescriptiveAnalytics

# Load data
data = pd.read_csv("sales_data.csv")

# Initialize descriptive analytics
analytics = DescriptiveAnalytics()

# Generate data summary
summary = analytics.summarize_data(data)
print(summary)

# Calculate statistics
stats = analytics.calculate_statistics(data, columns=["sales", "revenue", "profit"])
print(stats)

# Analyze trends
trends = analytics.analyze_trends(data, time_column="date", value_column="sales")
print(trends)

# Analyze correlations
correlations = analytics.analyze_correlations(data, columns=["sales", "marketing_spend", "customer_count"])
print(correlations)
```

### Diagnostic Analytics

```python
from enhanced_bdfg.modules.diagnostic_analytics import DiagnosticAnalytics

# Initialize diagnostic analytics
analytics = DiagnosticAnalytics()

# Detect anomalies
anomalies = analytics.detect_anomalies(data, column="sales")
print(f"Found {len(anomalies)} anomalies")

# Analyze root causes
root_causes = analytics.analyze_root_causes(
    data=data,
    target_column="profit",
    event_date="2023-06-15",
    window_size=7
)
print("Root causes:", root_causes)

# Analyze contributing factors
factors = analytics.analyze_contributing_factors(
    data=data,
    target_column="sales",
    factor_columns=["day_of_week", "promotion_active", "weather"]
)
print("Contributing factors:", factors)
```

### Predictive Analytics

```python
from enhanced_bdfg.modules.predictive_analytics import PredictiveAnalytics

# Initialize predictive analytics
analytics = PredictiveAnalytics()

# Forecast time series
forecast = analytics.forecast_time_series(
    data=data,
    time_column="date",
    target_column="sales",
    horizon=30
)
print(f"Forecast for next 30 days: {forecast['forecast']}")

# Build regression model
model = analytics.build_regression_model(
    data=data,
    target_column="profit",
    feature_columns=["sales", "marketing_spend", "inventory_cost"]
)
print(f"Model metrics: {model['metrics']}")
print(f"Feature importance: {model['feature_importance']}")

# Generate scenarios
scenarios = analytics.generate_scenarios(
    data=data,
    time_column="date",
    target_column="sales",
    horizon=30,
    num_scenarios=3
)
print("Scenarios:", scenarios.keys())
```

### Prescriptive Analytics

```python
from enhanced_bdfg.modules.prescriptive_analytics import PrescriptiveAnalytics

# Initialize prescriptive analytics
analytics = PrescriptiveAnalytics()

# Optimize resource allocation
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
    data=data,
    resources=resources,
    constraints=constraints,
    objective="maximize_profit"
)
print("Optimal allocation:", optimization["allocation"])
print("Objective value:", optimization["objective_value"])

# Generate action plan
objectives = [
    {"id": "obj1", "name": "Increase Sales", "weight": 0.5, "baseline": 1000, "target": 1200},
    {"id": "obj2", "name": "Reduce Costs", "weight": 0.3, "baseline": 600, "target": 500},
    {"id": "obj3", "name": "Improve Satisfaction", "weight": 0.2, "baseline": 3.8, "target": 4.5}
]

actions = [
    {"id": "act1", "name": "Marketing Campaign", "cost": 5000, "duration": 30, 
     "categories": ["marketing", "sales"], "impacts": {"obj1": 0.3, "obj3": 0.1}},
    {"id": "act2", "name": "Process Optimization", "cost": 3000, "duration": 45, 
     "categories": ["operations", "costs"], "impacts": {"obj2": 0.4}},
    {"id": "act3", "name": "Staff Training", "cost": 2000, "duration": 15, 
     "categories": ["hr", "service"], "impacts": {"obj3": 0.3, "obj1": 0.1}}
]

action_plan = analytics.generate_action_plan(
    objectives=objectives,
    actions=actions,
    constraints={"max_cost": 8000, "max_duration": 60}
)
print("Action plan:", action_plan["plan"])
print("Expected outcomes:", action_plan["expected_outcomes"])
```

### Cognitive Analytics

```python
from enhanced_bdfg.modules.cognitive_analytics import CognitiveAnalytics

# Initialize cognitive analytics
analytics = CognitiveAnalytics()

# Analyze text
text = "Customer feedback has been very positive about our new product line. The quality and pricing are excellent."
analysis = analytics.analyze_text(text)
print("Text analysis:", analysis)

# Analyze sentiment
sentiment = analytics.analyze_sentiment(text)
print("Sentiment:", sentiment["sentiment"])
print("Sentiment score:", sentiment["compound_score"])

# Extract entities
entities = analytics.extract_entities(text)
print("Entities:", entities)

# Analyze multiple texts
texts = [
    "Customer feedback has been very positive about our new product line.",
    "Several customers complained about shipping delays last month.",
    "The marketing campaign exceeded expectations with a 25% increase in website traffic."
]
collection_analysis = analytics.analyze_text_collection(texts)
print("Collection analysis:", collection_analysis)
```

## Advanced Usage

### Custom Model Selection

```python
from enhanced_bdfg.core.model_selector import ModelSelector

# Initialize model selector
selector = ModelSelector()

# Define model requirements
requirements = {
    "task_type": "classification",
    "data_size": "medium",
    "interpretability": "high",
    "performance_priority": "accuracy",
    "deployment_environment": "cloud",
    "training_time_constraint": "medium",
    "available_hardware": ["cpu", "standard_gpu"]
}

# Select model
model = selector.select_model(requirements)
print("Selected model:", model)

# Get alternative models
alternatives = selector.select_alternative_models(requirements, count=2)
print("Alternative models:", alternatives)

# Compare models
comparison = selector.compare_models([model] + alternatives)
print("Model comparison:", comparison)
```

### Hardware and Resource Management

```python
from enhanced_bdfg.core.hardware_manager import HardwareManager
from enhanced_bdfg.core.resource_manager import ResourceManager

# Initialize managers
hw_manager = HardwareManager()
res_manager = ResourceManager()

# Define hardware specs
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

# Assess hardware
assessment = hw_manager.assess_hardware(hardware_specs)
print("Hardware assessment:", assessment)

# Define resource allocation
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

# Allocate resources
allocation = res_manager.allocate_resources(resource_allocation)
print("Resource allocation:", allocation)

# Optimize hardware usage
optimization = hw_manager.optimize_hardware_usage(hardware_specs, resource_allocation)
print("Hardware optimization:", optimization)

# Optimize resources
resource_optimization = res_manager.optimize_resources(allocation, hardware_specs)
print("Resource optimization:", resource_optimization)
```

### Agent Generation and Orchestration

```python
from enhanced_bdfg.core.agent_generator import AgentGenerator

# Initialize agent generator
generator = AgentGenerator()

# Define agent configuration
agent_config = {
    "agent_type": "data_processing",
    "capabilities": ["data_cleaning", "feature_engineering", "data_transformation"],
    "execution_mode": "batch",
    "input_format": "csv",
    "output_format": "parquet",
    "logging_level": "info",
    "max_runtime": 3600
}

# Create agent
agent = generator.create_agent(agent_config)
print("Agent created:", agent)

# Create multiple agents
agent_configs = [
    {
        "agent_type": "data_processing",
        "capabilities": ["data_cleaning", "feature_engineering"],
        "execution_mode": "batch"
    },
    {
        "agent_type": "model_training",
        "capabilities": ["hyperparameter_tuning", "model_selection"],
        "execution_mode": "batch"
    },
    {
        "agent_type": "inference",
        "capabilities": ["prediction", "explanation"],
        "execution_mode": "real_time"
    }
]

agents = [generator.create_agent(config) for config in agent_configs]

# Configure orchestration
orchestration = generator.configure_orchestration(agents, execution_order="sequential")
print("Orchestration configuration:", orchestration)
```

### Prompt Engineering

```python
from enhanced_bdfg.core.prompt_engineering import PromptEngineer

# Initialize prompt engineer
engineer = PromptEngineer()

# Create template
template = engineer.create_template(
    name="data_analysis",
    template="Analyze the following {data_type} data and provide insights on {focus_area}: {data}"
)
print("Template created:", template)

# Generate prompt
prompt = engineer.generate_prompt(
    template_name="data_analysis",
    parameters={
        "data_type": "time series",
        "focus_area": "sales trends",
        "data": "Monthly sales data for 2023"
    }
)
print("Generated prompt:", prompt)

# List templates
templates = engineer.list_templates()
print("Available templates:", templates)

# Optimize template
optimization = engineer.optimize_template(
    "data_analysis", 
    optimization_criteria={"clarity": 0.8, "specificity": 0.9}
)
print("Template optimization:", optimization)
```

### Framework Packaging

```python
from enhanced_bdfg.core.framework_packager import FrameworkPackager

# Initialize framework packager
packager = FrameworkPackager()

# Create configuration
config = packager.create_configuration(
    business_profile=profile,
    model_requirements=requirements,
    hardware_specs=hardware_specs,
    resource_allocation=resource_allocation
)
print("Configuration created:", config)

# Create package
package = packager.create_package(
    config=config,
    output_format="json",
    include_documentation=True
)
print("Package created:", package)

# Prepare deployment
deployment_package = packager.prepare_deployment(
    package=package,
    environment="development",
    deployment_type="container"
)
print("Deployment package:", deployment_package)

# Generate documentation
documentation = packager.generate_documentation(
    package=package,
    doc_format="markdown"
)
print("Documentation generated:", documentation)
```
