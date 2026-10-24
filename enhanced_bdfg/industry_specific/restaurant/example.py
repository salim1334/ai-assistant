# Restaurant Business Framework

This sample framework demonstrates how the BDFG system can be configured and used for a restaurant business. It includes specialized components for menu optimization, table management, inventory control, and customer experience analysis.

## Business Profile

```json
{
  "business_type": "restaurant",
  "business_size": "small",
  "business_name": "Bistro Nouveau",
  "industry": "full_service_restaurant",
  "cuisine_type": "contemporary_american",
  "years_in_operation": 2,
  "num_employees": 15,
  "annual_revenue": 750000,
  "location_type": "urban_downtown",
  "seating_capacity": 60,
  "has_bar": true,
  "offers_takeout": true,
  "offers_delivery": true,
  "goals": [
    "increase_profit_margin",
    "reduce_food_waste",
    "improve_table_turnover",
    "enhance_customer_experience",
    "optimize_staffing_levels"
  ],
  "challenges": [
    "high_food_costs",
    "staff_turnover",
    "seasonal_demand_fluctuations",
    "competition_from_nearby_restaurants",
    "managing_online_reviews"
  ],
  "target_audience": {
    "age_range": "25-55",
    "demographics": ["urban_professionals", "foodies", "couples"],
    "income_level": "middle_to_upper"
  },
  "data_sources": [
    "pos_system",
    "reservation_system",
    "inventory_management_system",
    "employee_scheduling_system",
    "online_review_platforms"
  ]
}
```

## Module Configuration

### Business Intelligence Module

```python
from bdfg.modules import BusinessIntelligenceModule

# Configure the Business Intelligence Module for restaurants
bi_config = {
    "kpi_tracking": {
        "primary_kpis": [
            "average_check_size",
            "food_cost_percentage",
            "labor_cost_percentage",
            "table_turnover_rate",
            "covers_per_day",
            "revenue_per_available_seat_hour"
        ],
        "secondary_kpis": [
            "sales_by_menu_category",
            "sales_by_daypart",
            "beverage_to_food_ratio",
            "comps_and_voids_percentage",
            "check_splitting_frequency",
            "tip_percentage"
        ],
        "update_frequency": "daily"
    },
    "forecasting": {
        "methods": ["arima", "prophet", "exponential_smoothing"],
        "forecast_periods": {
            "short_term": 7,  # days
            "medium_term": 30,  # days
            "long_term": 90   # days
        },
        "variables": [
            "covers_by_daypart",
            "sales_by_day_of_week",
            "sales_by_menu_category",
            "special_events_impact"
        ]
    },
    "reporting": {
        "automated_reports": [
            {
                "name": "Daily Sales and Operations Summary",
                "frequency": "daily",
                "components": ["sales_overview", "labor_summary", "food_cost_summary", "top_selling_items"]
            },
            {
                "name": "Weekly Performance Report",
                "frequency": "weekly",
                "components": ["weekly_sales_analysis", "staff_performance", "menu_item_analysis", "customer_feedback_summary"]
            },
            {
                "name": "Monthly Business Review",
                "frequency": "monthly",
                "components": ["monthly_p&l_analysis", "menu_engineering", "staff_productivity", "customer_satisfaction_trends"]
            }
        ]
    },
    "visualization": {
        "dashboard_components": [
            "sales_trends",
            "menu_item_performance",
            "table_utilization",
            "staff_productivity",
            "customer_satisfaction"
        ],
        "chart_types": [
            "time_series",
            "bar_charts",
            "heatmaps",
            "scatter_plots",
            "radar_charts"
        ]
    }
}

# Initialize the module with restaurant-specific configuration
restaurant_bi_module = BusinessIntelligenceModule(bi_config)
```

### Operational Optimization Module

```python
from bdfg.modules import OperationalOptimizationModule

# Configure the Operational Optimization Module for restaurants
op_config = {
    "cost_reduction": {
        "focus_areas": [
            "food_cost_management",
            "labor_optimization",
            "energy_consumption",
            "supply_chain_efficiency",
            "waste_reduction"
        ],
        "analysis_methods": [
            "cost_trend_analysis",
            "comparative_benchmarking",
            "scenario_modeling",
            "recipe_costing"
        ]
    },
    "workflow_optimization": {
        "processes": [
            "kitchen_operations",
            "service_sequence",
            "table_management",
            "reservation_handling",
            "takeout_and_delivery_process"
        ],
        "metrics": [
            "order_to_delivery_time",
            "table_turnover_time",
            "steps_of_service_compliance",
            "kitchen_ticket_times",
            "staff_movement_efficiency"
        ]
    },
    "resource_allocation": {
        "resources": [
            "staff_scheduling",
            "table_assignment",
            "kitchen_station_allocation",
            "inventory_management",
            "equipment_utilization"
        ],
        "optimization_goals": [
            "minimize_labor_cost_percentage",
            "maximize_covers_per_labor_hour",
            "maximize_revenue_per_available_seat_hour",
            "minimize_food_waste"
        ]
    },
    "efficiency_metrics": {
        "operational_metrics": [
            "covers_per_labor_hour",
            "revenue_per_labor_hour",
            "food_preparation_time",
            "table_turnover_rate",
            "kitchen_efficiency_ratio"
        ],
        "benchmarks": {
            "industry_average": True,
            "historical_performance": True,
            "top_performers": True
        }
    }
}

# Initialize the module with restaurant-specific configuration
restaurant_op_module = OperationalOptimizationModule(op_config)
```

### Market Analysis Module

```python
from bdfg.modules import MarketAnalysisModule

# Configure the Market Analysis Module for restaurants
ma_config = {
    "competitor_analysis": {
        "competitors": [
            "nearby_restaurants",
            "similar_cuisine_restaurants",
            "similar_price_point_restaurants",
            "trending_restaurants_in_area"
        ],
        "analysis_dimensions": [
            "menu_offerings",
            "pricing_strategy",
            "service_style",
            "ambiance_and_experience",
            "marketing_approach",
            "online_presence_and_reviews"
        ],
        "data_sources": [
            "mystery_dining",
            "social_media_monitoring",
            "online_review_analysis",
            "menu_comparison",
            "customer_surveys"
        ]
    },
    "customer_trends": {
        "trend_categories": [
            "dietary_preferences",
            "flavor_profiles",
            "dining_occasion_patterns",
            "price_sensitivity",
            "service_expectations",
            "sustainability_concerns"
        ],
        "analysis_methods": [
            "social_media_analysis",
            "sales_pattern_analysis",
            "customer_survey_analysis",
            "industry_report_review",
            "review_sentiment_analysis"
        ]
    },
    "market_opportunities": {
        "opportunity_types": [
            "menu_innovation",
            "service_enhancements",
            "daypart_expansion",
            "private_events",
            "catering_services",
            "retail_product_development"
        ],
        "evaluation_criteria": [
            "market_demand",
            "competition_level",
            "investment_required",
            "alignment_with_brand",
            "profit_potential",
            "operational_feasibility"
        ]
    },
    "positioning": {
        "positioning_dimensions": [
            "price_vs_value",
            "traditional_vs_innovative",
            "casual_vs_formal",
            "speed_vs_experience"
        ],
        "perceptual_mapping": True,
        "differentiation_analysis": True
    }
}

# Initialize the module with restaurant-specific configuration
restaurant_ma_module = MarketAnalysisModule(ma_config)
```

## Sample Analysis Tasks

### Menu Engineering Analysis

```python
def analyze_menu_engineering(data):
    """
    Analyze menu performance to optimize profitability and popularity.
    
    Args:
        data: DataFrame containing menu item sales and cost data
        
    Returns:
        dict: Menu engineering analysis and recommendations
    """
    # Calculate key metrics for each menu item
    menu_analysis = data.copy()
    menu_analysis['contribution_margin'] = menu_analysis['price'] - menu_analysis['food_cost']
    menu_analysis['cm_percentage'] = menu_analysis['contribution_margin'] / menu_analysis['price'] * 100
    
    # Calculate category averages
    category_avg_cm = menu_analysis.groupby('category')['contribution_margin'].mean()
    category_avg_quantity = menu_analysis.groupby('category')['quantity_sold'].mean()
    
    # Classify items based on profitability and popularity
    menu_analysis['cm_performance'] = menu_analysis.apply(
        lambda x: 'high' if x['contribution_margin'] > category_avg_cm[x['category']] else 'low', 
        axis=1
    )
    menu_analysis['popularity_performance'] = menu_analysis.apply(
        lambda x: 'high' if x['quantity_sold'] > category_avg_quantity[x['category']] else 'low', 
        axis=1
    )
    
    # Assign menu engineering categories
    menu_analysis['menu_category'] = menu_analysis.apply(
        lambda x: 'Star' if x['cm_performance'] == 'high' and x['popularity_performance'] == 'high'
                else 'Plow Horse' if x['cm_performance'] == 'low' and x['popularity_performance'] == 'high'
                else 'Puzzle' if x['cm_performance'] == 'high' and x['popularity_performance'] == 'low'
                else 'Dog', 
        axis=1
    )
    
    # Group items by menu engineering category
    categorized_items = {
        'Stars': menu_analysis[menu_analysis['menu_category'] == 'Star'].to_dict('records'),
        'Plow_Horses': menu_analysis[menu_analysis['menu_category'] == 'Plow Horse'].to_dict('records'),
        'Puzzles': menu_analysis[menu_analysis['menu_category'] == 'Puzzle'].to_dict('records'),
        'Dogs': menu_analysis[menu_analysis['menu_category'] == 'Dog'].to_dict('records')
    }
    
    # Generate recommendations for each category
    recommendations = {
        'Stars': "Maintain quality and consistency. Consider strategic price increases. Feature prominently in menu design and server recommendations.",
        'Plow_Horses': "Look for ways to increase contribution margin without affecting popularity. Evaluate portion sizes and ingredient substitutions.",
        'Puzzles': "Increase visibility through menu placement, server recommendations, and marketing. Consider bundling with popular items.",
        'Dogs': "Consider removing from menu or completely redesigning. If kept, minimize menu space and reduce prep time investment."
    }
    
    # Calculate overall menu statistics
    menu_statistics = {
        'average_contribution_margin': menu_analysis['contribution_margin'].mean(),
        'average_food_cost_percentage': (menu_analysis['food_cost'] / menu_analysis['price']).mean() * 100,
        'most_profitable_category': menu_analysis.groupby('category')['contribution_margin'].sum().idxmax(),
        'most_popular_category': menu_analysis.groupby('category')['quantity_sold'].sum().idxmax()
    }
    
    # Generate menu optimization strategies
    menu_strategies = generate_menu_strategies(menu_analysis, categorized_items)
    
    return {
        'item_analysis': menu_analysis.to_dict('records'),
        'categorized_items': categorized_items,
        'menu_statistics': menu_statistics,
        'category_recommendations': recommendations,
        'menu_strategies': menu_strategies
    }

def generate_menu_strategies(menu_analysis, categorized_items):
    """Generate strategic recommendations for menu optimization."""
    strategies = {
        'pricing_strategies': [],
        'menu_design_strategies': [],
        'product_strategies': []
    }
    
    # Pricing strategies
    if len(categorized_items['Stars']) > 0:
        strategies['pricing_strategies'].append(
            "Consider 3-5% price increases on Star items, as they have demonstrated price insensitivity"
        )
    
    if len(categorized_items['Plow_Horses']) > 0:
        strategies['pricing_strategies'].append(
            "Evaluate ingredient costs for Plow Horse items to improve margins without price increases"
        )
    
    if len(categorized_items['Puzzles']) > 0:
        strategies['pricing_strategies'].append(
            "Test 5-8% price reductions on select Puzzle items to evaluate price elasticity"
        )
    
    # Menu design strategies
    strategies['menu_design_strategies'] = [
        "Position Star items in menu hotspots (top right corner, first and last items in categories)",
        "Use visual highlights (boxes, photos) for Puzzle items to increase visibility",
        "Minimize visibility of Dog items or remove entirely",
        "Ensure menu categories are organized by customer decision-making process, not kitchen workflow"
    ]
    
    # Product strategies
    if len(categorized_items['Dogs']) > 3:
        strategies['product_strategies'].append(
            f"Consider removing or replacing {len(categorized_items['Dogs']) - 2} Dog items"
        )
    
    if len(categorized_items['Puzzles']) > 0:
        strategies['product_strategies'].append(
            "Redesign Puzzle items to improve visual appeal or adjust portion sizes"
        )
    
    return strategies
```

### Table Management Optimization

```python
def analyze_table_management(data):
    """
    Analyze table utilization and turnover to optimize seating and reservations.
    
    Args:
        data: DataFrame containing table usage data
        
    Returns:
        dict: Table management analysis and recommendations
    """
    # Calculate key metrics for each table
    table_metrics = data.groupby('table_id').agg({
        'party_size': 'mean',
        'seating_duration_minutes': 'mean',
        'revenue': 'mean',
        'covers': 'sum',
        'utilization_rate': 'mean',
        'turn_time_minutes': 'mean',
        'reservation_count': 'sum',
        'walkup_count': 'sum'
    }).reset_index()
    
    # Calculate revenue per seat hour for each table
    table_metrics['revenue_per_seat_hour'] = (
        table_metrics['revenue'] / 
        (table_metrics['party_size'] * (table_metrics['seating_duration_minutes'] / 60))
    )
    
    # Calculate table efficiency score
    table_metrics['efficiency_score'] = (
        (table_metrics['revenue_per_seat_hour'] * 0.4) + 
        (table_metrics['utilization_rate'] * 0.3) + 
        ((60 / table_metrics['turn_time_minutes']) * 0.3)
    )
    
    # Analyze peak time performance
    peak_performance = analyze_peak_time_performance(data)
    
    # Analyze table configuration effectiveness
    table_config_analysis = analyze_table_configuration(data)
    
    # Generate reservation optimization strategy
    reservation_strategy = generate_reservation_strategy(data)
    
    # Generate table assignment recommendations
    table_assignment_recommendations = generate_table_assignment_recommendations(table_metrics, data)
    
    # Calculate potential revenue improvement
    potential_improvement = calculate_potential_revenue_improvement(table_metrics, data)
    
    return {
        'table_metrics': table_metrics.to_dict('records'),
        'peak_performance': peak_performance,
        'table_configuration_analysis': table_config_analysis,
        'reservation_strategy': reservation_strategy,
        'table_assignment_recommendations': table_assignment_recommendations,
        'potential_revenue_improvement': potential_improvement
    }

def analyze_peak_time_performance(data):
    """Analyze table performance during peak hours."""
    # Filter for peak hours (typically 6-9 PM for dinner service)
    peak_data = data[(data['hour'] >= 18) & (data['hour'] <= 21)]
    
    # Calculate peak time metrics
    peak_metrics = {
        'average_wait_time_minutes': peak_data['wait_time_minutes'].mean(),
        'average_turn_time_minutes': peak_data['turn_time_minutes'].mean(),
        'utilization_rate': peak_data['utilization_rate'].mean() * 100,
        'average_party_size': peak_data['party_size'].mean(),
        'parties_on_waitlist': peak_data['waitlist_count'].mean(),
        'revenue_per_hour': peak_data.groupby('hour')['revenue'].mean().to_dict()
    }
    
    # Identify bottleneck tables during peak times
    bottleneck_tables = peak_data.groupby('table_id')['turn_time_minutes'].mean().nlargest(3).to_dict()
    
    # Identify most efficient tables during peak times
    efficient_tables = peak_data.groupby('table_id')['revenue_per_seat_hour'].mean().nlargest(3).to_dict()
    
    return {
        'peak_metrics': peak_metrics,
        'bottleneck_tables': bottleneck_tables,
        'efficient_tables': efficient_tables,
        'recommendations': [
            f"Target turn time of {int(peak_metrics['average_turn_time_minutes'] * 0.9)} minutes during peak hours",
            "Assign most experienced servers to bottleneck tables",
            "Consider time-limited seating for peak reservation slots",
            "Optimize pre-meal and payment processes to reduce table turn time"
        ]
    }

def analyze_table_configuration(data):
    """Analyze effectiveness of current table configuration."""
    # Calculate metrics by table size
    table_size_metrics = data.groupby('table_size').agg({
        'utilization_rate': 'mean',
        'revenue_per_seat_hour': 'mean',
        'party_size': 'mean',
        'wait_time_minutes': 'mean'
    }).reset_index()
    
    # Calculate mismatch between party size and table size
    table_size_metrics['size_mismatch'] = abs(table_size_metrics['table_size'] - table_size_metrics['party_size'])
    
    # Calculate party size distribution
    party_size_distribution = data['party_size'].value_counts(normalize=True).sort_index().to_dict()
    
    # Calculate current table size distribution
    table_size_distribution = data['table_size'].value_counts(normalize=True).sort_index().to_dict()
    
    # Generate optimal table mix recommendation
    optimal_mix = {}
    for party_size, frequency in party_size_distribution.items():
        # Round up to nearest even number for table size
        recommended_table_size = int(party_size + (party_size % 2))
        if recommended_table_size in optimal_mix:
            optimal_mix[recommended_table_size] += frequency
        else:
            optimal_mix[recommended_table_size] = frequency
    
    # Normalize optimal mix to percentages
    total = sum(optimal_mix.values())
    optimal_mix = {k: round(v / total * 100) for k, v in optimal_mix.items()}
    
    return {
        'table_size_metrics': table_size_metrics.to_dict('records'),
        'party_size_distribution': party_size_distribution,
        'current_table_distribution': table_size_distribution,
        'recommended_table_mix': optimal_mix,
        'configuration_recommendations': [
            f"Adjust table mix to better match party size distribution",
            "Consider flexible seating arrangements with combinable tables",
            "Prioritize {}-top tables based on party size frequency".format(
                max(party_size_distribution.items(), key=lambda x: x[1])[0]
            )
        ]
    }

def generate_reservation_strategy(data):
    """Generate optimal reservation strategy."""
    # Calculate metrics by day of week and hour
    time_metrics = data.groupby(['day_of_week', 'hour']).agg({
        'utilization_rate': 'mean',
        'revenue': 'sum',
        'covers': 'sum',
        'wait_time_minutes': 'mean'
    }).reset_index()
    
    # Identify peak revenue periods
    peak_periods = time_metrics.sort_values('revenue', ascending=False).head(10)[['day_of_week', 'hour']].to_dict('records')
    
    # Calculate reservation vs walkup performance
    res_vs_walkup = data.groupby('reservation_status').agg({
        'revenue_per_person': 'mean',
        'seating_duration_minutes': 'mean',
        'party_size': 'mean'
    }).to_dict('index')
    
    # Generate time slot recommendations
    time_slot_recommendations = {}
    for _, row in time_metrics.iterrows():
        day = row['day_of_week']
        hour = row['hour']
        utilization = row['utilization_rate']
        
        if day not in time_slot_recommendations:
            time_slot_recommendations[day] = {}
            
        if utilization > 0.9:  # High utilization
            time_slot_recommendations[day][hour] = "Limit reservations to 70% of capacity"
        elif utilization > 0.7:  # Medium utilization
            time_slot_recommendations[day][hour] = "Accept reservations for 85% of capacity"
        else:  # Low utilization
            time_slot_recommendations[day][hour] = "Accept all reservations, consider promotions"
    
    return {
        'peak_periods': peak_periods,
        'reservation_vs_walkup_performance': res_vs_walkup,
        'time_slot_recommendations': time_slot_recommendations,
        'general_recommendations': [
            "Implement a reservation buffer of 15 minutes between seatings",
            "Confirm reservations 24 hours in advance to reduce no-shows",
            "Implement credit card holds for peak period reservations",
            "Optimize table assignments based on party size to minimize unused seats"
        ]
    }

def generate_table_assignment_recommendations(table_metrics, data):
    """Generate recommendations for optimal table assignments."""
    # Identify server sections and performance
    server_performance = data.groupby('server_id').agg({
        'turn_time_minutes': 'mean',
        'revenue_per_person': 'mean',
        'customer_satisfaction': 'mean'
    }).sort_values('revenue_per_person', ascending=False).to_dict('index')
    
    # Identify optimal server-table pairings
    server_table_performance = data.groupby(['server_id', 'table_id']).agg({
        'revenue': 'mean',
        'turn_time_minutes': 'mean',
        'customer_satisfaction': 'mean'
    }).reset_index()
    
    # Get top performing server for each table
    top_server_by_table = server_table_performance.loc[
        server_table_performance.groupby('table_id')['revenue'].idxmax()
    ][['table_id', 'server_id', 'revenue']].set_index('table_id').to_dict('index')
    
    return {
        'server_performance': server_performance,
        'top_server_by_table': top_server_by_table,
        'table_assignment_principles': [
            "Assign highest-revenue servers to highest-potential tables",
            "Balance server sections to equalize revenue opportunity",
            "Consider server strengths when assigning sections (bar tables, large parties, etc.)",
            "Rotate servers through different sections to maintain fairness and skill development"
        ]
    }

def calculate_potential_revenue_improvement(table_metrics, data):
    """Calculate potential revenue improvement with optimized table management."""
    # Current metrics
    current_daily_revenue = data.groupby('date')['revenue'].sum().mean()
    current_daily_covers = data.groupby('date')['covers'].sum().mean()
    current_avg_turn_time = data['turn_time_minutes'].mean()
    current_utilization = data['utilization_rate'].mean()
    
    # Potential improvements
    improved_turn_time = current_avg_turn_time * 0.9  # 10% improvement
    improved_utilization = min(current_utilization * 1.15, 0.95)  # 15% improvement, capped at 95%
    
    # Calculate potential revenue
    potential_daily_covers = current_daily_covers * (current_avg_turn_time / improved_turn_time) * (improved_utilization / current_utilization)
    potential_daily_revenue = potential_daily_covers * data['revenue_per_person'].mean()
    
    # Calculate improvement
    revenue_improvement = potential_daily_revenue - current_daily_revenue
    percentage_improvement = (revenue_improvement / current_daily_revenue) * 100
    
    return {
        'current_metrics': {
            'daily_revenue': current_daily_revenue,
            'daily_covers': current_daily_covers,
            'average_turn_time': current_avg_turn_time,
            'utilization_rate': current_utilization
        },
        'potential_metrics': {
            'daily_revenue': potential_daily_revenue,
            'daily_covers': potential_daily_covers,
            'average_turn_time': improved_turn_time,
            'utilization_rate': improved_utilization
        },
        'improvement': {
            'daily_revenue_increase': revenue_improvement,
            'percentage_improvement': percentage_improvement,
            'annual_revenue_increase': revenue_improvement * 365
        }
    }
```

### Labor Optimization Analysis

```python
def analyze_labor_optimization(data):
    """
    Analyze labor costs and staffing levels to optimize scheduling.
    
    Args:
        data: DataFrame containing labor and sales data
        
    Returns:
        dict: Labor optimization analysis and recommendations
    """
    # Calculate key labor metrics
    labor_metrics = {
        'labor_cost_percentage': (data['labor_cost'].sum() / data['sales'].sum()) * 100,
        'sales_per_labor_hour': data['sales'].sum() / data['labor_hours'].sum(),
        'covers_per_labor_hour': data['covers'].sum() / data['labor_hours'].sum(),
        'average_hourly_wage': data['labor_cost'].sum() / data['labor_hours'].sum()
    }
    
    # Analyze labor by department
    department_analysis = data.groupby('department').agg({
        'labor_cost': 'sum',
        'labor_hours': 'sum',
        'sales': 'sum'
    }).reset_index()
    
    department_analysis['labor_cost_percentage'] = (department_analysis['labor_cost'] / department_analysis['sales']) * 100
    department_analysis['sales_per_labor_hour'] = department_analysis['sales'] / department_analysis['labor_hours']
    
    # Analyze labor by day and hour
    time_analysis = data.groupby(['day_of_week', 'hour']).agg({
        'labor_cost': 'mean',
        'labor_hours': 'mean',
        'sales': 'mean',
        'covers': 'mean'
    }).reset_index()
    
    time_analysis['labor_cost_percentage'] = (time_analysis['labor_cost'] / time_analysis['sales']) * 100
    time_analysis['sales_per_labor_hour'] = time_analysis['sales'] / time_analysis['labor_hours']
    time_analysis['covers_per_labor_hour'] = time_analysis['covers'] / time_analysis['labor_hours']
    
    # Identify overstaffed and understaffed periods
    time_analysis['staffing_status'] = time_analysis.apply(
        lambda x: 'Overstaffed' if x['labor_cost_percentage'] > labor_metrics['labor_cost_percentage'] * 1.2
                else 'Understaffed' if x['sales_per_labor_hour'] > labor_metrics['sales_per_labor_hour'] * 1.2
                else 'Optimal',
        axis=1
    )
    
    overstaffed_periods = time_analysis[time_analysis['staffing_status'] == 'Overstaffed'][['day_of_week', 'hour']].to_dict('records')
    understaffed_periods = time_analysis[time_analysis['staffing_status'] == 'Understaffed'][['day_of_week', 'hour']].to_dict('records')
    
    # Generate optimal staffing model
    staffing_model = generate_optimal_staffing_model(data, time_analysis)
    
    # Calculate potential labor savings
    potential_savings = calculate_potential_labor_savings(data, staffing_model)
    
    return {
        'labor_metrics': labor_metrics,
        'department_analysis': department_analysis.to_dict('records'),
        'time_analysis': time_analysis.to_dict('records'),
        'overstaffed_periods': overstaffed_periods,
        'understaffed_periods': understaffed_periods,
        'optimal_staffing_model': staffing_model,
        'potential_savings': potential_savings,
        'recommendations': generate_labor_recommendations(labor_metrics, department_analysis, time_analysis)
    }

def generate_optimal_staffing_model(data, time_analysis):
    """Generate optimal staffing model based on sales and cover patterns."""
    # Calculate baseline staffing needs by department, day, and hour
    baseline_staffing = data.groupby(['department', 'day_of_week', 'hour']).agg({
        'staff_count': 'mean',
        'sales': 'mean',
        'covers': 'mean'
    }).reset_index()
    
    # Calculate optimal staff count based on sales and covers
    baseline_staffing['optimal_staff_count'] = baseline_staffing.apply(
        lambda x: max(
            # Minimum staffing levels by department
            2 if x['department'] == 'Kitchen' else 1,
            # Staff based on sales volume
            round(x['sales'] / 250),  # $250 sales per staff hour as benchmark
            # Staff based on cover volume
            round(x['covers'] / 8)    # 8 covers per staff hour as benchmark
        ),
        axis=1
    )
    
    # Adjust for overstaffed and understaffed periods
    staffing_model = baseline_staffing.merge(
        time_analysis[['day_of_week', 'hour', 'staffing_status']],
        on=['day_of_week', 'hour']
    )
    
    staffing_model['adjusted_staff_count'] = staffing_model.apply(
        lambda x: max(1, round(x['optimal_staff_count'] * 0.8)) if x['staffing_status'] == 'Overstaffed'
                else round(x['optimal_staff_count'] * 1.2) if x['staffing_status'] == 'Understaffed'
                else x['optimal_staff_count'],
        axis=1
    )
    
    # Organize by department and day
    staffing_by_department_day = {}
    for dept in staffing_model['department'].unique():
        staffing_by_department_day[dept] = {}
        for day in staffing_model['day_of_week'].unique():
            day_data = staffing_model[(staffing_model['department'] == dept) & (staffing_model['day_of_week'] == day)]
            staffing_by_department_day[dept][day] = day_data[['hour', 'adjusted_staff_count']].set_index('hour').to_dict()['adjusted_staff_count']
    
    return staffing_by_department_day

def calculate_potential_labor_savings(data, staffing_model):
    """Calculate potential labor savings from optimized scheduling."""
    # Current labor metrics
    current_labor_cost = data['labor_cost'].sum()
    current_labor_hours = data['labor_hours'].sum()
    
    # Calculate current staff hours by department, day, and hour
    current_staffing = data.groupby(['department', 'day_of_week', 'hour']).agg({
        'staff_count': 'mean',
        'labor_hours': 'sum',
        'labor_cost': 'sum'
    }).reset_index()
    
    # Calculate optimized labor hours and cost
    optimized_staffing = current_staffing.copy()
    
    for i, row in optimized_staffing.iterrows():
        dept = row['department']
        day = row['day_of_week']
        hour = row['hour']
        
        # Get optimal staff count from staffing model
        optimal_count = staffing_model.get(dept, {}).get(day, {}).get(hour, row['staff_count'])
        
        # Calculate ratio of optimal to current
        ratio = optimal_count / row['staff_count'] if row['staff_count'] > 0 else 1
        
        # Apply ratio to labor hours and cost
        optimized_staffing.at[i, 'labor_hours'] = row['labor_hours'] * ratio
        optimized_staffing.at[i, 'labor_cost'] = row['labor_cost'] * ratio
    
    # Calculate totals and savings
    optimized_labor_hours = optimized_staffing['labor_hours'].sum()
    optimized_labor_cost = optimized_staffing['labor_cost'].sum()
    
    hours_saved = current_labor_hours - optimized_labor_hours
    cost_saved = current_labor_cost - optimized_labor_cost
    
    return {
        'current_labor_cost': current_labor_cost,
        'optimized_labor_cost': optimized_labor_cost,
        'annual_cost_savings': cost_saved * 52,  # Assuming weekly data
        'hours_saved_per_week': hours_saved,
        'percentage_savings': (cost_saved / current_labor_cost) * 100
    }

def generate_labor_recommendations(labor_metrics, department_analysis, time_analysis):
    """Generate recommendations for labor optimization."""
    recommendations = []
    
    # Overall labor cost recommendations
    if labor_metrics['labor_cost_percentage'] > 30:
        recommendations.append(
            f"Overall labor cost is {labor_metrics['labor_cost_percentage']:.1f}% of sales, which is above the target of 30%. "
            "Focus on reducing labor costs through scheduling optimization."
        )
    
    # Department-specific recommendations
    for _, dept in department_analysis.iterrows():
        if dept['labor_cost_percentage'] > 35:
            recommendations.append(
                f"{dept['department']} labor cost is {dept['labor_cost_percentage']:.1f}% of sales, which is significantly above target. "
                "Review staffing levels and productivity in this department."
            )
    
    # Time-specific recommendations
    overstaffed_count = len(time_analysis[time_analysis['staffing_status'] == 'Overstaffed'])
    if overstaffed_count > 0:
        recommendations.append(
            f"Identified {overstaffed_count} overstaffed periods. Reduce staffing during these times to improve labor efficiency."
        )
    
    understaffed_count = len(time_analysis[time_analysis['staffing_status'] == 'Understaffed'])
    if understaffed_count > 0:
        recommendations.append(
            f"Identified {understaffed_count} understaffed periods. Increase staffing during these times to maintain service quality."
        )
    
    # Scheduling recommendations
    recommendations.extend([
        "Implement staggered scheduling to better match staffing to customer flow",
        "Cross-train staff to increase scheduling flexibility",
        "Schedule based on projected covers rather than fixed shifts",
        "Develop a core team of full-time staff supplemented by part-time staff during peak periods"
    ])
    
    return recommendations
```

## Sample Reports

### Daily Operations Dashboard

```python
def generate_daily_operations_dashboard(data, date):
    """
    Generate a daily operations dashboard for restaurant management.
    
    Args:
        data: DataFrame containing restaurant operations data
        date: Date for the dashboard
        
    Returns:
        dict: Dashboard configuration and data
    """
    # Filter data for the specified date
    daily_data = data[data['date'] == date]
    
    # Calculate daily KPIs
    daily_kpis = {
        "total_sales": daily_data['sales'].sum(),
        "covers": daily_data['covers'].sum(),
        "average_check": daily_data['sales'].sum() / daily_data['covers'].sum() if daily_data['covers'].sum() > 0 else 0,
        "food_cost_percentage": (daily_data['food_cost'].sum() / daily_data['food_sales'].sum()) * 100 if daily_data['food_sales'].sum() > 0 else 0,
        "labor_cost_percentage": (daily_data['labor_cost'].sum() / daily_data['sales'].sum()) * 100 if daily_data['sales'].sum() > 0 else 0,
        "table_turnover_rate": daily_data['table_turns'].mean(),
        "comparison_to_previous_day": calculate_day_over_day_change(data, date),
        "comparison_to_same_day_last_week": calculate_week_over_week_change(data, date)
    }
    
    # Sales by daypart
    daypart_sales = daily_data.groupby('daypart').agg({
        'sales': 'sum',
        'covers': 'sum',
        'food_sales': 'sum',
        'beverage_sales': 'sum'
    }).reset_index()
    
    daypart_sales['average_check'] = daypart_sales['sales'] / daypart_sales['covers']
    daypart_sales['beverage_to_food_ratio'] = daypart_sales['beverage_sales'] / daypart_sales['food_sales']
    
    # Sales by hour
    hourly_sales = daily_data.groupby('hour').agg({
        'sales': 'sum',
        'covers': 'sum',
        'labor_hours': 'sum'
    }).reset_index()
    
    hourly_sales['sales_per_labor_hour'] = hourly_sales['sales'] / hourly_sales['labor_hours']
    hourly_sales['covers_per_labor_hour'] = hourly_sales['covers'] / hourly_sales['labor_hours']
    
    # Top selling menu items
    top_items = daily_data.groupby('menu_item').agg({
        'item_quantity': 'sum',
        'item_sales': 'sum',
        'food_cost': 'sum'
    }).reset_index()
    
    top_items['food_cost_percentage'] = (top_items['food_cost'] / top_items['item_sales']) * 100
    top_items = top_items.sort_values('item_sales', ascending=False).head(10)
    
    # Staff performance
    staff_performance = daily_data.groupby('server_id').agg({
        'sales': 'sum',
        'covers': 'sum',
        'table_count': 'sum',
        'avg_check': 'mean',
        'tip_percentage': 'mean'
    }).reset_index()
    
    staff_performance['sales_per_table'] = staff_performance['sales'] / staff_performance['table_count']
    staff_performance = staff_performance.sort_values('sales', ascending=False)
    
    # Reservation and table metrics
    reservation_metrics = {
        'total_reservations': daily_data['reservation_count'].sum(),
        'walk_ins': daily_data['walk_in_count'].sum(),
        'no_shows': daily_data['no_show_count'].sum(),
        'average_party_size': daily_data['party_size'].mean(),
        'average_wait_time': daily_data['wait_time_minutes'].mean(),
        'average_turn_time': daily_data['turn_time_minutes'].mean()
    }
    
    # Inventory alerts
    inventory_alerts = generate_inventory_alerts(daily_data)
    
    return {
        "date": date,
        "kpis": daily_kpis,
        "daypart_sales": daypart_sales.to_dict('records'),
        "hourly_sales": hourly_sales.to_dict('records'),
        "top_items": top_items.to_dict('records'),
        "staff_performance": staff_performance.to_dict('records'),
        "reservation_metrics": reservation_metrics,
        "inventory_alerts": inventory_alerts,
        "visualization_config": {
            "hourly_sales_chart": {
                "type": "line",
                "data": hourly_sales,
                "options": {
                    "x_axis": "hour",
                    "y_axis": "sales",
                    "title": "Sales by Hour"
                }
            },
            "daypart_sales_chart": {
                "type": "bar",
                "data": daypart_sales,
                "options": {
                    "x_axis": "daypart",
                    "y_axis": "sales",
                    "title": "Sales by Daypart"
                }
            },
            "top_items_chart": {
                "type": "bar",
                "data": top_items,
                "options": {
                    "x_axis": "menu_item",
                    "y_axis": "item_sales",
                    "title": "Top Selling Items"
                }
            }
        }
    }

def generate_inventory_alerts(data):
    """Generate inventory alerts based on daily usage and stock levels."""
    # This would typically connect to inventory management system
    # For this example, we'll simulate some alerts
    
    # Extract unique ingredients used and their quantities
    ingredients_used = {}
    for _, row in data.iterrows():
        for ingredient, quantity in row.get('ingredients_used', {}).items():
            if ingredient in ingredients_used:
                ingredients_used[ingredient] += quantity
            else:
                ingredients_used[ingredient] = quantity
    
    # Compare with par levels (simulated)
    par_levels = {
        'chicken_breast': 20,
        'salmon_fillet': 15,
        'ground_beef': 25,
        'romaine_lettuce': 10,
        'tomatoes': 30,
        'onions': 40,
        'potatoes': 50,
        'white_wine': 12,
        'red_wine': 12
    }
    
    # Current stock levels (simulated)
    current_stock = {
        'chicken_breast': 18,
        'salmon_fillet': 6,
        'ground_beef': 22,
        'romaine_lettuce': 4,
        'tomatoes': 25,
        'onions': 35,
        'potatoes': 45,
        'white_wine': 5,
        'red_wine': 10
    }
    
    # Generate alerts
    alerts = []
    for ingredient, stock in current_stock.items():
        usage = ingredients_used.get(ingredient, 0)
        par = par_levels.get(ingredient, 0)
        
        # Below par level
        if stock < par:
            alerts.append({
                'type': 'below_par',
                'ingredient': ingredient,
                'current_stock': stock,
                'par_level': par,
                'message': f"{ingredient} is below par level ({stock}/{par})"
            })
        
        # Critical level (less than today's usage)
        if stock < usage:
            alerts.append({
                'type': 'critical',
                'ingredient': ingredient,
                'current_stock': stock,
                'daily_usage': usage,
                'message': f"CRITICAL: {ingredient} stock ({stock}) is less than daily usage ({usage})"
            })
    
    return alerts
```

### Menu Engineering Report

```python
def generate_menu_engineering_report(data, period="last_month"):
    """
    Generate a comprehensive menu engineering report.
    
    Args:
        data: DataFrame containing menu item sales and cost data
        period: Time period for analysis
        
    Returns:
        dict: Menu engineering report data and visualizations
    """
    # Filter data for the specified period
    filtered_data = filter_data_by_period(data, period)
    
    # Perform menu engineering analysis
    menu_analysis = analyze_menu_engineering(filtered_data)
    
    # Calculate overall menu performance metrics
    overall_metrics = {
        'total_food_sales': filtered_data['food_sales'].sum(),
        'total_food_cost': filtered_data['food_cost'].sum(),
        'overall_food_cost_percentage': (filtered_data['food_cost'].sum() / filtered_data['food_sales'].sum()) * 100,
        'average_item_contribution_margin': menu_analysis['item_analysis']['contribution_margin'].mean(),
        'number_of_items_sold': filtered_data['item_quantity'].sum(),
        'number_of_menu_items': len(filtered_data['menu_item'].unique())
    }
    
    # Category performance
    category_performance = filtered_data.groupby('category').agg({
        'food_sales': 'sum',
        'food_cost': 'sum',
        'item_quantity': 'sum'
    }).reset_index()
    
    category_performance['food_cost_percentage'] = (category_performance['food_cost'] / category_performance['food_sales']) * 100
    category_performance['sales_percentage'] = (category_performance['food_sales'] / overall_metrics['total_food_sales']) * 100
    category_performance['average_item_price'] = category_performance['food_sales'] / category_performance['item_quantity']
    
    # Menu mix percentage
    menu_mix = filtered_data.groupby('menu_item').agg({
        'item_quantity': 'sum'
    }).reset_index()
    
    menu_mix['menu_mix_percentage'] = (menu_mix['item_quantity'] / menu_mix['item_quantity'].sum()) * 100
    
    # Prepare data for quadrant chart visualization
    quadrant_data = []
    for category, items in menu_analysis['categorized_items'].items():
        for item in items:
            quadrant_data.append({
                'menu_item': item['menu_item'],
                'category': item['category'],
                'contribution_margin': item['contribution_margin'],
                'quantity_sold': item['quantity_sold'],
                'menu_category': category,
                'food_cost_percentage': (item['food_cost'] / item['price']) * 100
            })
    
    # Generate recommendations based on analysis
    recommendations = generate_menu_recommendations(menu_analysis, overall_metrics, category_performance)
    
    return {
        'period': period,
        'overall_metrics': overall_metrics,
        'category_performance': category_performance.to_dict('records'),
        'menu_mix': menu_mix.to_dict('records'),
        'menu_engineering_categories': {
            'stars': len(menu_analysis['categorized_items']['Stars']),
            'plow_horses': len(menu_analysis['categorized_items']['Plow_Horses']),
            'puzzles': len(menu_analysis['categorized_items']['Puzzles']),
            'dogs': len(menu_analysis['categorized_items']['Dogs'])
        },
        'quadrant_data': quadrant_data,
        'recommendations': recommendations,
        'visualization_config': {
            'menu_engineering_quadrant': {
                'type': 'scatter',
                'data': quadrant_data,
                'options': {
                    'x_axis': 'contribution_margin',
                    'y_axis': 'quantity_sold',
                    'color_by': 'menu_category',
                    'size_by': 'food_cost_percentage',
                    'title': 'Menu Engineering Quadrant Analysis'
                }
            },
            'category_performance_chart': {
                'type': 'bar',
                'data': category_performance,
                'options': {
                    'x_axis': 'category',
                    'y_axis': 'food_sales',
                    'title': 'Sales by Menu Category'
                }
            },
            'food_cost_by_category': {
                'type': 'bar',
                'data': category_performance,
                'options': {
                    'x_axis': 'category',
                    'y_axis': 'food_cost_percentage',
                    'title': 'Food Cost Percentage by Category'
                }
            }
        }
    }

def generate_menu_recommendations(menu_analysis, overall_metrics, category_performance):
    """Generate strategic recommendations based on menu engineering analysis."""
    recommendations = {
        'menu_optimization': [],
        'pricing_strategy': [],
        'cost_control': [],
        'menu_design': []
    }
    
    # Menu optimization recommendations
    if len(menu_analysis['categorized_items']['Dogs']) > 3:
        recommendations['menu_optimization'].append(
            f"Consider removing or redesigning {len(menu_analysis['categorized_items']['Dogs']) - 2} Dog items to streamline the menu"
        )
    
    if overall_metrics['number_of_menu_items'] > 30:
        recommendations['menu_optimization'].append(
            f"Menu has {overall_metrics['number_of_menu_items']} items, which may be too extensive. Consider reducing to 25-30 items for better focus and inventory control"
        )
    
    # Identify categories with high food cost
    high_cost_categories = category_performance[category_performance['food_cost_percentage'] > 35]['category'].tolist()
    if high_cost_categories:
        recommendations['cost_control'].append(
            f"Focus on reducing food costs in these high-cost categories: {', '.join(high_cost_categories)}"
        )
    
    # Pricing strategy recommendations
    if overall_metrics['overall_food_cost_percentage'] > 33:
        recommendations['pricing_strategy'].append(
            f"Overall food cost percentage is {overall_metrics['overall_food_cost_percentage']:.1f}%, which is above the target of 33%. Consider strategic price increases on high-volume items"
        )
    
    # Add standard recommendations
    recommendations['menu_design'].extend([
        "Position Star items in prime menu locations (top right corner, first and last items in categories)",
        "Use visual highlights (boxes, photos) for Puzzle items to increase visibility",
        "Minimize visibility of Dog items or remove entirely",
        "Ensure menu categories are organized by customer decision-making process, not kitchen workflow"
    ])
    
    recommendations['pricing_strategy'].extend([
        "Consider 3-5% price increases on Star items, as they have demonstrated price insensitivity",
        "Evaluate ingredient costs for Plow Horse items to improve margins without price increases",
        "Test 5-8% price reductions on select Puzzle items to evaluate price elasticity"
    ])
    
    recommendations['cost_control'].extend([
        "Standardize recipes and portion sizes to ensure consistent food costs",
        "Implement regular inventory counts and track waste by category",
        "Cross-utilize ingredients across menu items to reduce inventory complexity and waste"
    ])
    
    return recommendations
```

## Sample Visualizations

### Restaurant Performance Dashboard

```python
def create_restaurant_performance_dashboard(data, time_period="last_30_days"):
    """
    Create a restaurant performance dashboard with multiple visualizations.
    
    Args:
        data: DataFrame containing restaurant performance data
        time_period: Time period for analysis
        
    Returns:
        dict: Dashboard configuration with multiple visualizations
    """
    # Filter data for the specified time period
    filtered_data = filter_data_by_time_period(data, time_period)
    
    # Create sales trend chart
    sales_trend_chart = {
        "type": "line",
        "data": prepare_sales_trend_data(filtered_data),
        "options": {
            "title": "Sales Trend",
            "x_axis_label": "Date",
            "y_axis_label": "Sales Amount",
            "include_moving_average": True,
            "moving_average_window": 7,
            "series": ["Total Sales", "Food Sales", "Beverage Sales"]
        }
    }
    
    # Create daypart performance chart
    daypart_performance_chart = {
        "type": "bar",
        "data": prepare_daypart_performance_data(filtered_data),
        "options": {
            "title": "Sales by Daypart",
            "x_axis_label": "Daypart",
            "y_axis_label": "Sales Amount",
            "sort_by": "sales",
            "color_scheme": "blue_to_red"
        }
    }
    
    # Create covers heatmap by day and hour
    covers_heatmap = {
        "type": "heatmap",
        "data": prepare_covers_heatmap_data(filtered_data),
        "options": {
            "title": "Covers by Day and Hour",
            "x_axis_label": "Hour of Day",
            "y_axis_label": "Day of Week",
            "color_scheme": "viridis"
        }
    }
    
    # Create menu category performance chart
    category_performance_chart = {
        "type": "pie",
        "data": prepare_category_performance_data(filtered_data),
        "options": {
            "title": "Sales by Menu Category",
            "legend_position": "right",
            "donut": True
        }
    }
    
    # Create labor and food cost chart
    cost_chart = {
        "type": "line",
        "data": prepare_cost_trend_data(filtered_data),
        "options": {
            "title": "Cost Percentages Over Time",
            "x_axis_label": "Date",
            "y_axis_label": "Percentage",
            "series": ["Food Cost %", "Labor Cost %", "Combined Prime Cost %"],
            "include_target_lines": True,
            "target_lines": [
                {"label": "Food Cost Target", "value": 33, "color": "red"},
                {"label": "Labor Cost Target", "value": 30, "color": "blue"},
                {"label": "Prime Cost Target", "value": 63, "color": "green"}
            ]
        }
    }
    
    # Create table utilization chart
    table_utilization_chart = {
        "type": "bar",
        "data": prepare_table_utilization_data(filtered_data),
        "options": {
            "title": "Table Utilization by Day",
            "x_axis_label": "Day of Week",
            "y_axis_label": "Utilization Rate (%)",
            "color_by": "utilization_rate",
            "color_scheme": "green_to_red"
        }
    }
    
    return {
        "title": "Restaurant Performance Dashboard",
        "time_period": time_period,
        "last_updated": get_current_datetime(),
        "charts": {
            "sales_trend": sales_trend_chart,
            "daypart_performance": daypart_performance_chart,
            "covers_heatmap": covers_heatmap,
            "category_performance": category_performance_chart,
            "cost_chart": cost_chart,
            "table_utilization": table_utilization_chart
        },
        "layout": {
            "rows": [
                {
                    "height": "40%",
                    "columns": [
                        {
                            "width": "70%",
                            "chart": "sales_trend"
                        },
                        {
                            "width": "30%",
                            "chart": "category_performance"
                        }
                    ]
                },
                {
                    "height": "30%",
                    "columns": [
                        {
                            "width": "50%",
                            "chart": "covers_heatmap"
                        },
                        {
                            "width": "50%",
                            "chart": "cost_chart"
                        }
                    ]
                },
                {
                    "height": "30%",
                    "columns": [
                        {
                            "width": "50%",
                            "chart": "daypart_performance"
                        },
                        {
                            "width": "50%",
                            "chart": "table_utilization"
                        }
                    ]
                }
            ]
        }
    }
```

## Hardware Configuration

```python
from bdfg.core import HardwareManager

# Configure hardware settings for restaurant framework
hardware_config = {
    "model_preferences": {
        "tier1": "TinyLlama-1.1B",  # For low-end devices
        "tier2": "Mistral-7B",      # For mid-range devices
        "tier3": "Mixtral-8x7B"     # For high-end devices
    },
    "batch_processing": {
        "enabled": True,
        "default_batch_size": 64,
        "max_batch_size": 256
    },
    "colab_fallback": {
        "enabled": True,
        "tasks": ["menu_engineering", "customer_segmentation", "sales_forecasting"]
    },
    "resource_allocation": {
        "memory_buffer_percentage": 20,  # Keep 20% memory free
        "cpu_usage_limit_percentage": 80,
        "prioritize_interactive_tasks": True
    }
}

# Initialize hardware manager with restaurant-specific configuration
hardware_manager = HardwareManager(hardware_config)
```

## Integration Configuration

```python
from bdfg.integrations import GoogleWorkspaceIntegration

# Configure Google Workspace integration for restaurants
google_config = {
    "sheets": {
        "templates": {
            "daily_sales_dashboard": "1AbCdEfGhIjKlMnOpQrStUvWxYz",
            "menu_engineering": "2BcDeFgHiJkLmNoPqRsTuVwXyZ",
            "labor_scheduling": "3CdEfGhIjKlMnOpQrStUvWxYzA"
        },
        "automated_reports": [
            {
                "name": "Daily Sales Report",
                "template": "daily_sales_dashboard",
                "schedule": "daily",
                "time": "23:00",
                "data_source": "pos_system",
                "share_with": ["restaurant_manager@example.com", "chef@example.com"]
            },
            {
                "name": "Weekly Labor Schedule",
                "template": "labor_scheduling",
                "schedule": "weekly",
                "day": "Thursday",
                "time": "10:00",
                "data_source": "scheduling_system",
                "share_with": ["restaurant_manager@example.com", "staff_coordinator@example.com"]
            }
        ]
    },
    "docs": {
        "templates": {
            "monthly_p&l_report": "4DeFgHiJkLmNoPqRsTuVwXyZaB",
            "menu_engineering_report": "5EfGhIjKlMnOpQrStUvWxYzAbC"
        },
        "automated_reports": [
            {
                "name": "Monthly P&L Report",
                "template": "monthly_p&l_report",
                "schedule": "monthly",
                "day": 3,
                "time": "09:00",
                "data_sources": ["pos_system", "accounting_system", "inventory_system"],
                "share_with": ["owner@example.com", "restaurant_manager@example.com", "accountant@example.com"]
            },
            {
                "name": "Quarterly Menu Engineering Report",
                "template": "menu_engineering_report",
                "schedule": "quarterly",
                "data_sources": ["pos_system", "inventory_system"],
                "share_with": ["owner@example.com", "chef@example.com", "restaurant_manager@example.com"]
            }
        ]
    },
    "slides": {
        "templates": {
            "quarterly_performance": "6FgHiJkLmNoPqRsTuVwXyZaBcD",
            "staff_training": "7GhIjKlMnOpQrStUvWxYzAbCdE"
        },
        "automated_presentations": [
            {
                "name": "Quarterly Performance Review",
                "template": "quarterly_performance",
                "schedule": "quarterly",
                "data_sources": ["pos_system", "accounting_system", "customer_feedback_system"],
                "share_with": ["owner@example.com", "management_team@example.com"]
            }
        ]
    }
}

# Initialize Google Workspace integration with restaurant-specific configuration
google_integration = GoogleWorkspaceIntegration(google_config)
```

## Sample Usage

```python
from bdfg import BusinessAssistant

# Create a restaurant business assistant
restaurant_assistant = BusinessAssistant(
    business_profile={
        "business_type": "restaurant",
        "business_size": "small",
        "business_name": "Bistro Nouveau",
        # Additional profile details...
    }
)

# Load sample data
import pandas as pd
sales_data = pd.read_csv("restaurant_sales_data.csv")
menu_data = pd.read_csv("restaurant_menu_data.csv")
labor_data = pd.read_csv("restaurant_labor_data.csv")
table_data = pd.read_csv("restaurant_table_data.csv")

# Analyze menu performance
menu_analysis = restaurant_assistant.analyze_data(
    data=menu_data,
    analysis_type="menu_engineering"
)

# Optimize labor scheduling
labor_recommendations = restaurant_assistant.analyze_data(
    data=labor_data,
    analysis_type="labor_optimization"
)

# Optimize table management
table_recommendations = restaurant_assistant.analyze_data(
    data=table_data,
    analysis_type="table_management"
)

# Generate a daily operations dashboard
daily_dashboard = restaurant_assistant.generate_report(
    data=sales_data,
    report_type="daily_operations_dashboard",
    parameters={"date": "2025-03-30"}
)

# Generate a menu engineering report
menu_report = restaurant_assistant.generate_report(
    data=menu_data,
    report_type="menu_engineering_report",
    parameters={"period": "last_month"}
)

# Ask a business question
response = restaurant_assistant.analyze(
    "What are the top 5 most profitable menu items, and how can we increase their sales?"
)

# Export results to Google Workspace
restaurant_assistant.export_to_google_sheets(
    data=daily_dashboard,
    template="daily_sales_dashboard",
    share_with=["restaurant_manager@example.com"]
)
```
