"""
User Interface Module for BDFG Framework

This module provides a simplified user interface for non-technical users
to interact with the BDFG framework.
"""

import logging
import os
import json
import time
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import webbrowser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BDFGUserInterface:
    """
    User Interface for the BDFG framework.
    
    This class provides a simplified GUI for non-technical users to:
    - Configure business profiles
    - Import and analyze business data
    - Generate reports and visualizations
    - Export results to Google Workspace
    """
    
    def __init__(self, framework_controller=None):
        """
        Initialize the BDFG User Interface.
        
        Args:
            framework_controller: Optional FrameworkController instance
        """
        self.framework_controller = framework_controller
        self.root = None
        self.business_profile = {}
        self.data_sources = {}
        self.current_analysis = None
        
    def start(self):
        """
        Start the BDFG User Interface.
        """
        self.root = tk.Tk()
        self.root.title("BDFG - Business Development Framework")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Create main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_tab = ttk.Frame(self.notebook)
        self.data_tab = ttk.Frame(self.notebook)
        self.analysis_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)
        self.export_tab = ttk.Frame(self.notebook)
        self.chat_tab = ttk.Frame(self.notebook)
        self.memory_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.setup_tab, text="Business Setup")
        self.notebook.add(self.data_tab, text="Data Import")
        self.notebook.add(self.analysis_tab, text="Analysis")
        self.notebook.add(self.reports_tab, text="Reports")
        self.notebook.add(self.export_tab, text="Export")
        self.notebook.add(self.chat_tab, text="Assistant")
        self.notebook.add(self.memory_tab, text="Memory")
        
        # Initialize tabs
        self._init_setup_tab()
        self._init_data_tab()
        self._init_analysis_tab()
        self._init_reports_tab()
        self._init_export_tab()
        self._init_chat_tab()
        self._init_memory_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Start the main loop
        self.root.mainloop()
    
    def _init_setup_tab(self):
        """Initialize the Business Setup tab."""
        # Create a frame for the form
        form_frame = ttk.LabelFrame(self.setup_tab, text="Business Profile")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Business type
        ttk.Label(form_frame, text="Business Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.business_type_var = tk.StringVar()
        business_types = ["retail", "restaurant", "service", "manufacturing", "farming", "fmcg_distribution"]
        self.business_type_combo = ttk.Combobox(form_frame, textvariable=self.business_type_var, values=business_types)
        self.business_type_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.business_type_combo.bind("<<ComboboxSelected>>", self._on_business_type_change)
        
        # Business name
        ttk.Label(form_frame, text="Business Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.business_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.business_name_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Business size
        ttk.Label(form_frame, text="Business Size:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.business_size_var = tk.StringVar()
        business_sizes = ["micro", "small", "medium", "large"]
        ttk.Combobox(form_frame, textvariable=self.business_size_var, values=business_sizes).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Years in operation
        ttk.Label(form_frame, text="Years in Operation:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.years_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.years_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Number of employees
        ttk.Label(form_frame, text="Number of Employees:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.employees_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.employees_var, width=10).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Annual revenue
        ttk.Label(form_frame, text="Annual Revenue ($):").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.revenue_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.revenue_var, width=15).grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Location
        ttk.Label(form_frame, text="Location:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        self.location_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.location_var, width=30).grid(row=6, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Business goals frame
        goals_frame = ttk.LabelFrame(self.setup_tab, text="Business Goals")
        goals_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Goals
        self.goals_vars = {}
        goals = ["increase_revenue", "reduce_costs", "improve_efficiency", "expand_market", "enhance_customer_experience"]
        for i, goal in enumerate(goals):
            var = tk.BooleanVar()
            ttk.Checkbutton(goals_frame, text=goal.replace("_", " ").title(), variable=var).grid(row=i//3, column=i%3, sticky=tk.W, padx=5, pady=5)
            self.goals_vars[goal] = var
        
        # Challenges frame
        challenges_frame = ttk.LabelFrame(self.setup_tab, text="Business Challenges")
        challenges_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Challenges
        self.challenges_vars = {}
        challenges = ["competition", "cash_flow", "staffing", "marketing", "operations", "technology"]
        for i, challenge in enumerate(challenges):
            var = tk.BooleanVar()
            ttk.Checkbutton(challenges_frame, text=challenge.replace("_", " ").title(), variable=var).grid(row=i//3, column=i%3, sticky=tk.W, padx=5, pady=5)
            self.challenges_vars[challenge] = var
        
        # Buttons
        button_frame = ttk.Frame(self.setup_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save Profile", command=self._save_business_profile).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Load Profile", command=self._load_business_profile).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self._clear_business_profile).pack(side=tk.RIGHT, padx=5)
    
    def _init_data_tab(self):
        """Initialize the Data Import tab."""
        # Create a frame for data sources
        sources_frame = ttk.LabelFrame(self.data_tab, text="Data Sources")
        sources_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Data source types
        ttk.Label(sources_frame, text="Select data source type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.data_source_type_var = tk.StringVar()
        data_source_types = ["sales_data", "inventory_data", "customer_data", "financial_data", "operational_data"]
        self.data_source_combo = ttk.Combobox(sources_frame, textvariable=self.data_source_type_var, values=data_source_types)
        self.data_source_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Import methods
        import_frame = ttk.LabelFrame(sources_frame, text="Import Method")
        import_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # CSV import
        ttk.Button(import_frame, text="Import CSV File", command=self._import_csv).grid(row=0, column=0, padx=5, pady=5)
        
        # Excel import
        ttk.Button(import_frame, text="Import Excel File", command=self._import_excel).grid(row=0, column=1, padx=5, pady=5)
        
        # Google Sheets import
        ttk.Button(import_frame, text="Import from Google Sheets", command=self._import_google_sheets).grid(row=0, column=2, padx=5, pady=5)
        
        # Sample data
        ttk.Button(import_frame, text="Use Sample Data", command=self._use_sample_data).grid(row=0, column=3, padx=5, pady=5)
        
        # Data preview
        preview_frame = ttk.LabelFrame(self.data_tab, text="Data Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a treeview for data preview
        self.preview_tree = ttk.Treeview(preview_frame)
        self.preview_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_tree.configure(yscrollcommand=scrollbar.set)
        
        # Data source info
        info_frame = ttk.Frame(self.data_tab)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.data_info_var = tk.StringVar()
        self.data_info_var.set("No data imported")
        ttk.Label(info_frame, textvariable=self.data_info_var).pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(self.data_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Process Data", command=self._process_data).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Clear Data", command=self._clear_data).pack(side=tk.RIGHT, padx=5)
    
    def _init_analysis_tab(self):
        """Initialize the Analysis tab."""
        # Create a frame for analysis options
        options_frame = ttk.LabelFrame(self.analysis_tab, text="Analysis Options")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Analysis type
        ttk.Label(options_frame, text="Analysis Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.analysis_type_var = tk.StringVar()
        self.analysis_types = []
        self.analysis_combo = ttk.Combobox(options_frame, textvariable=self.analysis_type_var, values=self.analysis_types)
        self.analysis_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.analysis_combo.bind("<<ComboboxSelected>>", self._on_analysis_type_change)
        
        # Analysis parameters frame
        self.params_frame = ttk.LabelFrame(options_frame, text="Analysis Parameters")
        self.params_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Analysis description
        self.analysis_desc_var = tk.StringVar()
        ttk.Label(options_frame, textvariable=self.analysis_desc_var, wraplength=600).grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.analysis_tab, text="Analysis Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a text widget for results
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=10)
        self.results_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = ttk.Frame(self.analysis_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Run Analysis", command=self._run_analysis).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Save Results", command=self._save_analysis_results).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Clear Results", command=self._clear_analysis_results).pack(side=tk.RIGHT, padx=5)
    
    def _init_reports_tab(self):
        """Initialize the Reports tab."""
        # Create a frame for report options
        options_frame = ttk.LabelFrame(self.reports_tab, text="Report Options")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Report type
        ttk.Label(options_frame, text="Report Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.report_type_var = tk.StringVar()
        self.report_types = []
        self.report_combo = ttk.Combobox(options_frame, textvariable=self.report_type_var, values=self.report_types)
        self.report_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.report_combo.bind("<<ComboboxSelected>>", self._on_report_type_change)
        
        # Report parameters frame
        self.report_params_frame = ttk.LabelFrame(options_frame, text="Report Parameters")
        self.report_params_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Report description
        self.report_desc_var = tk.StringVar()
        ttk.Label(options_frame, textvariable=self.report_desc_var, wraplength=600).grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Report preview frame
        preview_frame = ttk.LabelFrame(self.reports_tab, text="Report Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a text widget for preview
        self.report_preview_text = tk.Text(preview_frame, wrap=tk.WORD, height=10)
        self.report_preview_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.report_preview_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_preview_text.configure(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = ttk.Frame(self.reports_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Generate Report", command=self._generate_report).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Save Report", command=self._save_report).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Export to Google Docs", command=self._export_report_to_google_docs).pack(side=tk.RIGHT, padx=5)
    
    def _init_export_tab(self):
        """Initialize the Export tab."""
        # Create a frame for export options
        options_frame = ttk.LabelFrame(self.export_tab, text="Export Options")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Export destination
        ttk.Label(options_frame, text="Export Destination:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.export_dest_var = tk.StringVar()
        export_destinations = ["Google Sheets", "Google Docs", "Google Slides", "CSV File", "Excel File", "PDF File"]
        ttk.Combobox(options_frame, textvariable=self.export_dest_var, values=export_destinations).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Export content
        ttk.Label(options_frame, text="Export Content:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.export_content_var = tk.StringVar()
        self.export_content_types = ["Analysis Results", "Generated Report", "Business Dashboard", "Raw Data"]
        ttk.Combobox(options_frame, textvariable=self.export_content_var, values=self.export_content_types).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Export options frame
        export_options_frame = ttk.LabelFrame(options_frame, text="Export Settings")
        export_options_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # File name
        ttk.Label(export_options_frame, text="File Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.export_filename_var = tk.StringVar()
        ttk.Entry(export_options_frame, textvariable=self.export_filename_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Share with (for Google exports)
        ttk.Label(export_options_frame, text="Share with (email):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.export_share_var = tk.StringVar()
        ttk.Entry(export_options_frame, textvariable=self.export_share_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Include visualizations
        self.export_viz_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(export_options_frame, text="Include Visualizations", variable=self.export_viz_var).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Export format
        ttk.Label(export_options_frame, text="Export Format:").grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.export_format_var = tk.StringVar(value="Standard")
        export_formats = ["Standard", "Detailed", "Executive Summary"]
        ttk.Combobox(export_options_frame, textvariable=self.export_format_var, values=export_formats).grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Export status
        status_frame = ttk.LabelFrame(self.export_tab, text="Export Status")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.export_status_var = tk.StringVar(value="No export in progress")
        ttk.Label(status_frame, textvariable=self.export_status_var, wraplength=600).pack(padx=5, pady=5)
        
        # Progress bar
        self.export_progress = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.export_progress.pack(fill=tk.X, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.export_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Export", command=self._export_content).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Open Last Export", command=self._open_last_export).pack(side=tk.RIGHT, padx=5)
    
    def _on_business_type_change(self, event):
        """Handle business type change event."""
        business_type = self.business_type_var.get()
        
        # Update available analysis types based on business type
        self.analysis_types = self._get_analysis_types_for_business(business_type)
        self.analysis_combo['values'] = self.analysis_types
        
        # Update available report types based on business type
        self.report_types = self._get_report_types_for_business(business_type)
        self.report_combo['values'] = self.report_types
        
        # Update status
        self.status_var.set(f"Selected business type: {business_type}")
    
    def _on_analysis_type_change(self, event):
        """Handle analysis type change event."""
        analysis_type = self.analysis_type_var.get()
        
        # Clear previous parameters
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        # Add parameters based on analysis type
        if analysis_type == "sales_analysis":
            ttk.Label(self.params_frame, text="Time Period:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            period_var = tk.StringVar()
            periods = ["last_week", "last_month", "last_quarter", "last_year", "custom"]
            ttk.Combobox(self.params_frame, textvariable=period_var, values=periods).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
            
            ttk.Label(self.params_frame, text="Group By:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            group_var = tk.StringVar()
            groups = ["day", "week", "month", "category", "product"]
            ttk.Combobox(self.params_frame, textvariable=group_var, values=groups).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
            
            # Update description
            self.analysis_desc_var.set("Sales Analysis: Analyze sales trends, top-selling products, and revenue patterns over time.")
            
        elif analysis_type == "inventory_analysis":
            ttk.Label(self.params_frame, text="Analysis Focus:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            focus_var = tk.StringVar()
            focuses = ["stock_levels", "turnover", "reorder_points", "dead_stock"]
            ttk.Combobox(self.params_frame, textvariable=focus_var, values=focuses).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
            
            # Update description
            self.analysis_desc_var.set("Inventory Analysis: Analyze inventory levels, turnover rates, and identify opportunities for optimization.")
            
        elif analysis_type == "customer_analysis":
            ttk.Label(self.params_frame, text="Segment By:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            segment_var = tk.StringVar()
            segments = ["purchase_frequency", "spend_amount", "location", "demographics"]
            ttk.Combobox(self.params_frame, textvariable=segment_var, values=segments).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
            
            # Update description
            self.analysis_desc_var.set("Customer Analysis: Analyze customer behavior, identify segments, and understand purchasing patterns.")
            
        elif analysis_type == "financial_analysis":
            ttk.Label(self.params_frame, text="Metrics:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            metrics_frame = ttk.Frame(self.params_frame)
            metrics_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
            
            metrics = ["profit_margin", "cash_flow", "roi", "break_even"]
            for i, metric in enumerate(metrics):
                var = tk.BooleanVar(value=True)
                ttk.Checkbutton(metrics_frame, text=metric.replace("_", " ").title(), variable=var).grid(row=i//2, column=i%2, sticky=tk.W, padx=5, pady=2)
            
            # Update description
            self.analysis_desc_var.set("Financial Analysis: Analyze profit margins, cash flow, ROI, and other financial metrics.")
        
        # Update status
        self.status_var.set(f"Selected analysis type: {analysis_type}")
    
    def _on_report_type_change(self, event):
        """Handle report type change event."""
        report_type = self.report_type_var.get()
        
        # Clear previous parameters
        for widget in self.report_params_frame.winfo_children():
            widget.destroy()
        
        # Add parameters based on report type
        if report_type == "sales_report":
            ttk.Label(self.report_params_frame, text="Time Period:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            period_var = tk.StringVar()
            periods = ["last_week", "last_month", "last_quarter", "last_year", "custom"]
            ttk.Combobox(self.report_params_frame, textvariable=period_var, values=periods).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
            
            ttk.Label(self.report_params_frame, text="Report Format:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            format_var = tk.StringVar()
            formats = ["detailed", "summary", "executive"]
            ttk.Combobox(self.report_params_frame, textvariable=format_var, values=formats).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
            
            # Update description
            self.report_desc_var.set("Sales Report: Comprehensive report on sales performance, trends, and key metrics.")
            
        elif report_type == "inventory_report":
            ttk.Label(self.report_params_frame, text="Report Focus:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            focus_var = tk.StringVar()
            focuses = ["stock_levels", "turnover", "reorder_points", "all"]
            ttk.Combobox(self.report_params_frame, textvariable=focus_var, values=focuses).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
            
            # Update description
            self.report_desc_var.set("Inventory Report: Detailed report on inventory status, movement, and optimization opportunities.")
            
        elif report_type == "customer_report":
            ttk.Label(self.report_params_frame, text="Include Segments:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            segments_frame = ttk.Frame(self.report_params_frame)
            segments_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
            
            segments = ["high_value", "frequent", "new", "at_risk"]
            for i, segment in enumerate(segments):
                var = tk.BooleanVar(value=True)
                ttk.Checkbutton(segments_frame, text=segment.replace("_", " ").title(), variable=var).grid(row=i//2, column=i%2, sticky=tk.W, padx=5, pady=2)
            
            # Update description
            self.report_desc_var.set("Customer Report: Analysis of customer segments, behavior patterns, and engagement metrics.")
            
        elif report_type == "financial_report":
            ttk.Label(self.report_params_frame, text="Report Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            type_var = tk.StringVar()
            types = ["profit_and_loss", "cash_flow", "balance_sheet", "comprehensive"]
            ttk.Combobox(self.report_params_frame, textvariable=type_var, values=types).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
            
            # Update description
            self.report_desc_var.set("Financial Report: Detailed financial analysis including profit and loss, cash flow, and key financial metrics.")
        
        # Update status
        self.status_var.set(f"Selected report type: {report_type}")
    
    def _save_business_profile(self):
        """Save the business profile."""
        try:
            # Collect profile data
            self.business_profile = {
                "business_type": self.business_type_var.get(),
                "business_name": self.business_name_var.get(),
                "business_size": self.business_size_var.get(),
                "years_in_operation": int(self.years_var.get()) if self.years_var.get() else 0,
                "num_employees": int(self.employees_var.get()) if self.employees_var.get() else 0,
                "annual_revenue": float(self.revenue_var.get()) if self.revenue_var.get() else 0,
                "location": self.location_var.get(),
                "goals": [goal for goal, var in self.goals_vars.items() if var.get()],
                "challenges": [challenge for challenge, var in self.challenges_vars.items() if var.get()]
            }
            
            # Save to file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Business Profile"
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(self.business_profile, f, indent=4)
                
                self.status_var.set(f"Business profile saved to {file_path}")
                messagebox.showinfo("Success", "Business profile saved successfully!")
            
        except Exception as e:
            logger.error(f"Error saving business profile: {str(e)}")
            messagebox.showerror("Error", f"Failed to save business profile: {str(e)}")
    
    def _load_business_profile(self):
        """Load a business profile from file."""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Load Business Profile"
            )
            
            if file_path:
                with open(file_path, 'r') as f:
                    self.business_profile = json.load(f)
                
                # Update UI with loaded profile
                self.business_type_var.set(self.business_profile.get("business_type", ""))
                self.business_name_var.set(self.business_profile.get("business_name", ""))
                self.business_size_var.set(self.business_profile.get("business_size", ""))
                self.years_var.set(str(self.business_profile.get("years_in_operation", "")))
                self.employees_var.set(str(self.business_profile.get("num_employees", "")))
                self.revenue_var.set(str(self.business_profile.get("annual_revenue", "")))
                self.location_var.set(self.business_profile.get("location", ""))
                
                # Update goals
                for goal, var in self.goals_vars.items():
                    var.set(goal in self.business_profile.get("goals", []))
                
                # Update challenges
                for challenge, var in self.challenges_vars.items():
                    var.set(challenge in self.business_profile.get("challenges", []))
                
                # Trigger business type change event
                self._on_business_type_change(None)
                
                self.status_var.set(f"Business profile loaded from {file_path}")
                messagebox.showinfo("Success", "Business profile loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error loading business profile: {str(e)}")
            messagebox.showerror("Error", f"Failed to load business profile: {str(e)}")
    
    def _clear_business_profile(self):
        """Clear the business profile form."""
        self.business_type_var.set("")
        self.business_name_var.set("")
        self.business_size_var.set("")
        self.years_var.set("")
        self.employees_var.set("")
        self.revenue_var.set("")
        self.location_var.set("")
        
        # Clear goals
        for var in self.goals_vars.values():
            var.set(False)
        
        # Clear challenges
        for var in self.challenges_vars.values():
            var.set(False)
        
        self.business_profile = {}
        self.status_var.set("Business profile cleared")
    
    def _import_csv(self):
        """Import data from a CSV file."""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Import CSV File"
            )
            
            if file_path:
                # Read the CSV file
                data = pd.read_csv(file_path)
                
                # Store the data
                data_source_type = self.data_source_type_var.get()
                if not data_source_type:
                    data_source_type = "unknown"
                
                self.data_sources[data_source_type] = data
                
                # Update data info
                self.data_info_var.set(f"Imported {len(data)} rows from {file_path}")
                
                # Update preview
                self._update_data_preview(data)
                
                self.status_var.set(f"CSV data imported from {file_path}")
            
        except Exception as e:
            logger.error(f"Error importing CSV: {str(e)}")
            messagebox.showerror("Error", f"Failed to import CSV: {str(e)}")
    
    def _import_excel(self):
        """Import data from an Excel file."""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
                title="Import Excel File"
            )
            
            if file_path:
                # Read the Excel file
                data = pd.read_excel(file_path)
                
                # Store the data
                data_source_type = self.data_source_type_var.get()
                if not data_source_type:
                    data_source_type = "unknown"
                
                self.data_sources[data_source_type] = data
                
                # Update data info
                self.data_info_var.set(f"Imported {len(data)} rows from {file_path}")
                
                # Update preview
                self._update_data_preview(data)
                
                self.status_var.set(f"Excel data imported from {file_path}")
            
        except Exception as e:
            logger.error(f"Error importing Excel: {str(e)}")
            messagebox.showerror("Error", f"Failed to import Excel: {str(e)}")
    
    def _import_google_sheets(self):
        """Import data from Google Sheets."""
        # This would require Google Sheets API integration
        messagebox.showinfo("Google Sheets Import", "This feature requires Google Sheets API integration. Please provide the spreadsheet ID and range.")
        
        # For demonstration purposes, we'll use a dialog to get the spreadsheet ID
        spreadsheet_id = simpledialog.askstring("Google Sheets Import", "Enter Spreadsheet ID:")
        if spreadsheet_id:
            range_name = simpledialog.askstring("Google Sheets Import", "Enter Range (e.g., Sheet1!A1:D10):", initialvalue="Sheet1")
            if range_name:
                self.status_var.set(f"Importing from Google Sheets: {spreadsheet_id}, Range: {range_name}")
                
                # This would normally use the Google Sheets API
                # For now, we'll just show a message
                messagebox.showinfo("Google Sheets Import", "This feature will be implemented with the Google Workspace integration.")
    
    def _use_sample_data(self):
        """Use sample data for the selected data source type."""
        try:
            data_source_type = self.data_source_type_var.get()
            if not data_source_type:
                messagebox.showerror("Error", "Please select a data source type first.")
                return
            
            # Generate sample data based on the type
            if data_source_type == "sales_data":
                data = self._generate_sample_sales_data()
            elif data_source_type == "inventory_data":
                data = self._generate_sample_inventory_data()
            elif data_source_type == "customer_data":
                data = self._generate_sample_customer_data()
            elif data_source_type == "financial_data":
                data = self._generate_sample_financial_data()
            elif data_source_type == "operational_data":
                data = self._generate_sample_operational_data()
            else:
                messagebox.showerror("Error", f"No sample data available for {data_source_type}")
                return
            
            # Store the data
            self.data_sources[data_source_type] = data
            
            # Update data info
            self.data_info_var.set(f"Using sample {data_source_type} with {len(data)} rows")
            
            # Update preview
            self._update_data_preview(data)
            
            self.status_var.set(f"Sample {data_source_type} loaded")
            
        except Exception as e:
            logger.error(f"Error using sample data: {str(e)}")
            messagebox.showerror("Error", f"Failed to load sample data: {str(e)}")
    
    def _update_data_preview(self, data):
        """Update the data preview treeview."""
        # Clear existing data
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        # Configure columns
        self.preview_tree["columns"] = list(data.columns)
        self.preview_tree["show"] = "headings"
        
        for column in data.columns:
            self.preview_tree.heading(column, text=column)
            self.preview_tree.column(column, width=100)
        
        # Add data rows (limit to 100 for performance)
        for i, row in data.head(100).iterrows():
            values = [str(row[col]) for col in data.columns]
            self.preview_tree.insert("", "end", values=values)
    
    def _process_data(self):
        """Process the imported data."""
        try:
            if not self.data_sources:
                messagebox.showerror("Error", "No data sources available. Please import data first.")
                return
            
            # This would normally process the data using the framework
            # For now, we'll just show a message
            messagebox.showinfo("Data Processing", "Data processing complete. Ready for analysis.")
            self.status_var.set("Data processed and ready for analysis")
            
            # Update available analysis types based on data sources
            self.analysis_types = self._get_analysis_types_for_data()
            self.analysis_combo['values'] = self.analysis_types
            
            # Update available report types based on data sources
            self.report_types = self._get_report_types_for_data()
            self.report_combo['values'] = self.report_types
            
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            messagebox.showerror("Error", f"Failed to process data: {str(e)}")
    
    def _clear_data(self):
        """Clear the imported data."""
        # Clear data sources
        self.data_sources = {}
        
        # Clear preview
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        # Update data info
        self.data_info_var.set("No data imported")
        
        self.status_var.set("Data cleared")
    
    def _run_analysis(self):
        """Run the selected analysis."""
        try:
            analysis_type = self.analysis_type_var.get()
            if not analysis_type:
                messagebox.showerror("Error", "Please select an analysis type first.")
                return
            
            if not self.data_sources:
                messagebox.showerror("Error", "No data sources available. Please import data first.")
                return
            
            # This would normally run the analysis using the framework
            # For now, we'll generate some sample results
            self.status_var.set(f"Running {analysis_type}...")
            
            # Simulate analysis running
            self.root.update()
            time.sleep(1)  # Simulate processing time
            
            # Generate sample results
            if analysis_type == "sales_analysis":
                results = self._generate_sample_sales_analysis()
            elif analysis_type == "inventory_analysis":
                results = self._generate_sample_inventory_analysis()
            elif analysis_type == "customer_analysis":
                results = self._generate_sample_customer_analysis()
            elif analysis_type == "financial_analysis":
                results = self._generate_sample_financial_analysis()
            else:
                results = f"Analysis results for {analysis_type}\n\nNo specific implementation available."
            
            # Display results
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, results)
            
            # Store current analysis
            self.current_analysis = {
                "type": analysis_type,
                "results": results,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.status_var.set(f"{analysis_type} completed")
            
        except Exception as e:
            logger.error(f"Error running analysis: {str(e)}")
            messagebox.showerror("Error", f"Failed to run analysis: {str(e)}")
    
    def _save_analysis_results(self):
        """Save the analysis results to a file."""
        try:
            if not self.current_analysis:
                messagebox.showerror("Error", "No analysis results available. Please run an analysis first.")
                return
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Analysis Results"
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(f"Analysis Type: {self.current_analysis['type']}\n")
                    f.write(f"Timestamp: {self.current_analysis['timestamp']}\n\n")
                    f.write(self.current_analysis['results'])
                
                self.status_var.set(f"Analysis results saved to {file_path}")
                messagebox.showinfo("Success", "Analysis results saved successfully!")
            
        except Exception as e:
            logger.error(f"Error saving analysis results: {str(e)}")
            messagebox.showerror("Error", f"Failed to save analysis results: {str(e)}")
    
    def _clear_analysis_results(self):
        """Clear the analysis results."""
        self.results_text.delete(1.0, tk.END)
        self.current_analysis = None
        self.status_var.set("Analysis results cleared")
    
    def _generate_report(self):
        """Generate the selected report."""
        try:
            report_type = self.report_type_var.get()
            if not report_type:
                messagebox.showerror("Error", "Please select a report type first.")
                return
            
            if not self.data_sources:
                messagebox.showerror("Error", "No data sources available. Please import data first.")
                return
            
            # This would normally generate the report using the framework
            # For now, we'll generate some sample content
            self.status_var.set(f"Generating {report_type}...")
            
            # Simulate report generation
            self.root.update()
            time.sleep(1)  # Simulate processing time
            
            # Generate sample report
            if report_type == "sales_report":
                report = self._generate_sample_sales_report()
            elif report_type == "inventory_report":
                report = self._generate_sample_inventory_report()
            elif report_type == "customer_report":
                report = self._generate_sample_customer_report()
            elif report_type == "financial_report":
                report = self._generate_sample_financial_report()
            else:
                report = f"Report: {report_type}\n\nNo specific implementation available."
            
            # Display report preview
            self.report_preview_text.delete(1.0, tk.END)
            self.report_preview_text.insert(tk.END, report)
            
            self.status_var.set(f"{report_type} generated")
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def _save_report(self):
        """Save the generated report to a file."""
        try:
            report_content = self.report_preview_text.get(1.0, tk.END)
            if not report_content.strip():
                messagebox.showerror("Error", "No report content available. Please generate a report first.")
                return
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Report"
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(report_content)
                
                self.status_var.set(f"Report saved to {file_path}")
                messagebox.showinfo("Success", "Report saved successfully!")
            
        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")
            messagebox.showerror("Error", f"Failed to save report: {str(e)}")
    
    def _export_report_to_google_docs(self):
        """Export the generated report to Google Docs."""
        try:
            report_content = self.report_preview_text.get(1.0, tk.END)
            if not report_content.strip():
                messagebox.showerror("Error", "No report content available. Please generate a report first.")
                return
            
            # This would normally use the Google Docs API
            # For now, we'll just show a message
            messagebox.showinfo("Google Docs Export", "This feature will be implemented with the Google Workspace integration.")
            self.status_var.set("Report export to Google Docs simulated")
            
        except Exception as e:
            logger.error(f"Error exporting to Google Docs: {str(e)}")
            messagebox.showerror("Error", f"Failed to export to Google Docs: {str(e)}")
    
    def _export_content(self):
        """Export the selected content to the selected destination."""
        try:
            export_dest = self.export_dest_var.get()
            export_content = self.export_content_var.get()
            
            if not export_dest:
                messagebox.showerror("Error", "Please select an export destination.")
                return
            
            if not export_content:
                messagebox.showerror("Error", "Please select content to export.")
                return
            
            # Update status
            self.export_status_var.set(f"Exporting {export_content} to {export_dest}...")
            self.export_progress["value"] = 0
            self.root.update()
            
            # Simulate export process
            for i in range(1, 11):
                time.sleep(0.2)  # Simulate processing time
                self.export_progress["value"] = i * 10
                self.root.update()
            
            # This would normally use the appropriate export method
            # For now, we'll just show a message
            self.export_status_var.set(f"Export of {export_content} to {export_dest} completed!")
            messagebox.showinfo("Export Complete", f"Export of {export_content} to {export_dest} completed successfully!")
            
            self.status_var.set(f"Export to {export_dest} completed")
            
        except Exception as e:
            logger.error(f"Error exporting content: {str(e)}")
            messagebox.showerror("Error", f"Failed to export content: {str(e)}")
            self.export_status_var.set(f"Export failed: {str(e)}")
    
    def _open_last_export(self):
        """Open the last exported file."""
        # This would normally open the last exported file
        # For now, we'll just show a message
        messagebox.showinfo("Open Last Export", "This feature will open the last exported file when implemented.")
    
    # Helper methods
    
    def _get_analysis_types_for_business(self, business_type):
        """Get available analysis types for the given business type."""
        common_types = ["sales_analysis", "inventory_analysis", "customer_analysis", "financial_analysis"]
        
        if business_type == "retail":
            return common_types + ["product_performance", "store_comparison"]
        elif business_type == "restaurant":
            return common_types + ["menu_engineering", "table_turnover"]
        elif business_type == "service":
            return common_types + ["service_efficiency", "client_retention"]
        elif business_type == "manufacturing":
            return common_types + ["production_efficiency", "quality_control"]
        elif business_type == "farming":
            return common_types + ["crop_yield_analysis", "weather_impact"]
        else:
            return common_types
    
    def _get_report_types_for_business(self, business_type):
        """Get available report types for the given business type."""
        common_types = ["sales_report", "inventory_report", "customer_report", "financial_report"]
        
        if business_type == "retail":
            return common_types + ["product_performance_report", "store_comparison_report"]
        elif business_type == "restaurant":
            return common_types + ["menu_engineering_report", "table_turnover_report"]
        elif business_type == "service":
            return common_types + ["service_efficiency_report", "client_retention_report"]
        elif business_type == "manufacturing":
            return common_types + ["production_efficiency_report", "quality_control_report"]
        elif business_type == "farming":
            return common_types + ["crop_yield_report", "weather_impact_report"]
        else:
            return common_types
    
    def _get_analysis_types_for_data(self):
        """Get available analysis types based on available data sources."""
        analysis_types = []
        
        if "sales_data" in self.data_sources:
            analysis_types.extend(["sales_analysis", "product_performance"])
        
        if "inventory_data" in self.data_sources:
            analysis_types.append("inventory_analysis")
        
        if "customer_data" in self.data_sources:
            analysis_types.extend(["customer_analysis", "client_retention"])
        
        if "financial_data" in self.data_sources:
            analysis_types.append("financial_analysis")
        
        if "operational_data" in self.data_sources:
            analysis_types.extend(["operational_efficiency", "resource_utilization"])
        
        return analysis_types if analysis_types else ["No analysis available - import data first"]
    
    def _get_report_types_for_data(self):
        """Get available report types based on available data sources."""
        report_types = []
        
        if "sales_data" in self.data_sources:
            report_types.extend(["sales_report", "product_performance_report"])
        
        if "inventory_data" in self.data_sources:
            report_types.append("inventory_report")
        
        if "customer_data" in self.data_sources:
            report_types.extend(["customer_report", "client_retention_report"])
        
        if "financial_data" in self.data_sources:
            report_types.append("financial_report")
        
        if "operational_data" in self.data_sources:
            report_types.extend(["operational_efficiency_report", "resource_utilization_report"])
        
        return report_types if report_types else ["No reports available - import data first"]
    
    # Sample data generators
    
    def _generate_sample_sales_data(self):
        """Generate sample sales data."""
        import numpy as np
        from datetime import datetime, timedelta
        
        # Generate dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days)]
        
        # Generate products
        products = ["Product A", "Product B", "Product C", "Product D", "Product E"]
        categories = ["Category 1", "Category 1", "Category 2", "Category 2", "Category 3"]
        
        # Generate data
        data = []
        for _ in range(1000):
            date = np.random.choice(dates)
            product_idx = np.random.randint(0, len(products))
            product = products[product_idx]
            category = categories[product_idx]
            quantity = np.random.randint(1, 10)
            price = np.random.uniform(10, 100)
            discount = np.random.uniform(0, 0.2)
            
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "product": product,
                "category": category,
                "quantity": quantity,
                "price": price,
                "discount": discount,
                "revenue": quantity * price * (1 - discount)
            })
        
        return pd.DataFrame(data)
    
    def _generate_sample_inventory_data(self):
        """Generate sample inventory data."""
        import numpy as np
        
        # Generate products
        products = ["Product A", "Product B", "Product C", "Product D", "Product E"]
        categories = ["Category 1", "Category 1", "Category 2", "Category 2", "Category 3"]
        
        # Generate data
        data = []
        for i in range(len(products)):
            stock = np.random.randint(10, 100)
            reorder_point = np.random.randint(5, 20)
            cost = np.random.uniform(5, 50)
            
            data.append({
                "product": products[i],
                "category": categories[i],
                "stock_level": stock,
                "reorder_point": reorder_point,
                "cost": cost,
                "value": stock * cost,
                "status": "Low" if stock <= reorder_point else "OK"
            })
        
        return pd.DataFrame(data)
    
    def _generate_sample_customer_data(self):
        """Generate sample customer data."""
        import numpy as np
        from datetime import datetime, timedelta
        
        # Generate dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # Generate data
        data = []
        for i in range(100):
            first_purchase = start_date + timedelta(days=np.random.randint(0, (end_date - start_date).days))
            last_purchase = first_purchase + timedelta(days=np.random.randint(0, (end_date - first_purchase).days))
            purchases = np.random.randint(1, 20)
            
            data.append({
                "customer_id": f"CUST{i+1:03d}",
                "first_purchase": first_purchase.strftime("%Y-%m-%d"),
                "last_purchase": last_purchase.strftime("%Y-%m-%d"),
                "purchases": purchases,
                "total_spent": np.random.uniform(50, 1000) * purchases,
                "average_order": np.random.uniform(50, 200),
                "location": np.random.choice(["North", "South", "East", "West"]),
                "segment": np.random.choice(["High Value", "Regular", "Occasional", "New"])
            })
        
        return pd.DataFrame(data)
    
    def _generate_sample_financial_data(self):
        """Generate sample financial data."""
        import numpy as np
        from datetime import datetime, timedelta
        
        # Generate dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        months = [start_date + timedelta(days=30*i) for i in range(12)]
        
        # Generate data
        data = []
        for month in months:
            revenue = np.random.uniform(50000, 100000)
            cogs = revenue * np.random.uniform(0.4, 0.6)
            expenses = revenue * np.random.uniform(0.2, 0.3)
            
            data.append({
                "month": month.strftime("%Y-%m"),
                "revenue": revenue,
                "cost_of_goods_sold": cogs,
                "gross_profit": revenue - cogs,
                "expenses": expenses,
                "net_profit": revenue - cogs - expenses,
                "profit_margin": (revenue - cogs - expenses) / revenue * 100
            })
        
        return pd.DataFrame(data)
    
    def _generate_sample_operational_data(self):
        """Generate sample operational data."""
        import numpy as np
        from datetime import datetime, timedelta
        
        # Generate dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days)]
        
        # Generate data
        data = []
        for date in dates:
            staff_hours = np.random.uniform(40, 80)
            orders = np.random.randint(20, 100)
            
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "staff_hours": staff_hours,
                "orders_processed": orders,
                "productivity": orders / staff_hours,
                "errors": np.random.randint(0, 5),
                "customer_wait_time": np.random.uniform(5, 30),
                "equipment_utilization": np.random.uniform(0.5, 0.9) * 100
            })
        
        return pd.DataFrame(data)
    
    # Sample analysis generators
    
    def _generate_sample_sales_analysis(self):
        """Generate sample sales analysis results."""
        return """
# Sales Analysis Results

## Summary
Total Revenue: $78,945.32
Total Units Sold: 2,345
Average Order Value: $33.67

## Top Selling Products
1. Product A - 532 units - $17,856.45
2. Product B - 423 units - $15,234.56
3. Product C - 387 units - $12,987.34

## Sales by Category
- Category 1: $32,456.78 (41.1%)
- Category 2: $28,765.43 (36.4%)
- Category 3: $17,723.11 (22.5%)

## Monthly Trend
- January: $23,456.78 (↑ 5.4%)
- February: $26,789.45 (↑ 14.2%)
- March: $28,699.09 (↑ 7.1%)

## Recommendations
1. Focus marketing efforts on Product A which shows the highest revenue
2. Investigate Category 3 for growth opportunities
3. Prepare for seasonal increase in March based on historical data
4. Consider bundle offers with Products A and C to increase average order value
"""
    
    def _generate_sample_inventory_analysis(self):
        """Generate sample inventory analysis results."""
        return """
# Inventory Analysis Results

## Summary
Total Inventory Value: $45,678.90
Average Stock Level: 47 units
Items Below Reorder Point: 3

## Stock Status
- Healthy Stock: 12 items (60%)
- Low Stock: 5 items (25%)
- Out of Stock: 3 items (15%)

## Inventory Turnover
Overall Turnover Ratio: 4.2
- Category 1: 5.7 (High)
- Category 2: 3.8 (Medium)
- Category 3: 2.9 (Low)

## Items Requiring Attention
1. Product B - 5 units (Reorder Point: 15) - Order 30 units
2. Product D - 8 units (Reorder Point: 10) - Order 22 units
3. Product E - 0 units (Reorder Point: 12) - Order 25 units URGENT

## Dead Stock Analysis
Items with No Movement (90+ days):
- Product F - 23 units - $1,234.56
- Product G - 18 units - $987.65

## Recommendations
1. Place immediate orders for Products B, D, and E
2. Consider promotions to move dead stock (Products F and G)
3. Review reorder points for Category 1 items which have high turnover
4. Implement cycle counting for Category 3 items to improve accuracy
"""
    
    def _generate_sample_customer_analysis(self):
        """Generate sample customer analysis results."""
        return """
# Customer Analysis Results

## Customer Segments
- High Value (20%): 87 customers - $45,678.90 revenue (45%)
- Regular (35%): 152 customers - $32,456.78 revenue (32%)
- Occasional (30%): 130 customers - $18,765.43 revenue (18%)
- New (15%): 65 customers - $5,432.10 revenue (5%)

## Customer Retention
Overall Retention Rate: 68%
- High Value Segment: 82%
- Regular Segment: 74%
- Occasional Segment: 53%

## Customer Acquisition
New Customers (Last 90 Days): 65
Customer Acquisition Cost: $28.45

## Customer Lifetime Value
Average CLV: $876.54
- High Value Segment: $2,345.67
- Regular Segment: $987.65
- Occasional Segment: $432.10

## Geographic Distribution
- North Region: 156 customers (36%)
- South Region: 134 customers (31%)
- East Region: 87 customers (20%)
- West Region: 57 customers (13%)

## Recommendations
1. Implement loyalty program targeting Regular segment to increase retention
2. Develop win-back campaign for Occasional segment
3. Focus acquisition efforts on North and South regions which show highest customer counts
4. Create personalized offers for High Value segment to maintain high retention rate
"""
    
    def _generate_sample_financial_analysis(self):
        """Generate sample financial analysis results."""
        return """
# Financial Analysis Results

## Profitability Metrics
Gross Profit Margin: 42.3%
Net Profit Margin: 18.7%
Return on Investment: 22.4%

## Cash Flow Analysis
Operating Cash Flow: $78,945.32
Free Cash Flow: $65,432.10
Cash Conversion Cycle: 45 days

## Expense Breakdown
- Cost of Goods Sold: $456,789.01 (57.7%)
- Operating Expenses: $187,654.32 (23.6%)
- Marketing & Sales: $87,654.32 (11.1%)
- Administrative: $56,789.01 (7.2%)
- Other: $3,456.78 (0.4%)

## Financial Ratios
Current Ratio: 2.3
Quick Ratio: 1.8
Debt-to-Equity Ratio: 0.45
Asset Turnover Ratio: 1.7

## Break-Even Analysis
Break-Even Point: $345,678.90
Margin of Safety: 27.8%

## Recommendations
1. Focus on reducing Cost of Goods Sold which represents the largest expense
2. Consider refinancing options to improve debt-to-equity ratio
3. Implement stricter accounts receivable policies to improve cash conversion cycle
4. Evaluate marketing expenses against customer acquisition cost for optimization
"""
    
    # Sample report generators
    
    def _generate_sample_sales_report(self):
        """Generate sample sales report."""
        return """
# Monthly Sales Report
## March 2025

### Executive Summary
This report provides an analysis of sales performance for March 2025. Overall sales reached $78,945.32, representing a 7.1% increase compared to February and a 12.3% increase year-over-year. The top-performing product category was Category 1, accounting for 41.1% of total revenue.

### Sales Performance

#### Revenue Breakdown
- Total Revenue: $78,945.32
- Product Sales: $75,432.10 (95.5%)
- Service Revenue: $3,513.22 (4.5%)

#### Sales by Channel
- In-Store: $45,678.90 (57.9%)
- Online: $28,765.43 (36.4%)
- Phone Orders: $4,500.99 (5.7%)

#### Top Selling Products
1. Product A - 532 units - $17,856.45
2. Product B - 423 units - $15,234.56
3. Product C - 387 units - $12,987.34

### Trend Analysis

#### Monthly Comparison
- January: $23,456.78
- February: $26,789.45
- March: $28,699.09
- Q1 Total: $78,945.32

#### Year-over-Year Comparison
- March 2024: $70,321.45
- March 2025: $78,945.32
- Growth: 12.3%

### Customer Insights

#### Sales by Customer Segment
- High Value: $35,525.39 (45%)
- Regular: $25,262.50 (32%)
- Occasional: $14,210.16 (18%)
- New: $3,947.27 (5%)

#### Geographic Distribution
- North Region: $28,420.32 (36%)
- South Region: $24,473.05 (31%)
- East Region: $15,789.06 (20%)
- West Region: $10,262.89 (13%)

### Recommendations

1. **Product Focus**: Continue promoting Product A which shows the strongest performance.
2. **Category Development**: Investigate growth opportunities in Category 3 which has the lowest share.
3. **Channel Optimization**: Increase online marketing efforts to boost the online sales channel.
4. **Customer Targeting**: Develop targeted campaigns for Regular customers to move them to the High Value segment.

### Appendix
- Detailed Product Sales Data
- Daily Sales Breakdown
- Promotion Performance Analysis
- Sales Representative Performance
"""
    
    def _generate_sample_inventory_report(self):
        """Generate sample inventory report."""
        return """
# Inventory Status Report
## March 31, 2025

### Executive Summary
This report provides a comprehensive analysis of inventory status as of March 31, 2025. The total inventory value is $45,678.90 with an average stock level of 47 units per product. Three items are currently below their reorder points and require immediate attention.

### Inventory Overview

#### Inventory Value
- Total Inventory Value: $45,678.90
- Average Item Value: $2,283.95
- Highest Value Category: Category 1 ($23,456.78)

#### Stock Levels
- Total Stock Units: 940
- Average Stock Level: 47 units
- Items Below Reorder Point: 3 (15%)
- Out of Stock Items: 3 (15%)

### Inventory Performance

#### Inventory Turnover
- Overall Turnover Ratio: 4.2
- Category 1: 5.7
- Category 2: 3.8
- Category 3: 2.9

#### Days of Supply
- Overall: 87 days
- Category 1: 64 days
- Category 2: 96 days
- Category 3: 126 days

### Critical Items

#### Items Requiring Immediate Attention
1. Product B - 5 units (Reorder Point: 15) - Order 30 units
2. Product D - 8 units (Reorder Point: 10) - Order 22 units
3. Product E - 0 units (Reorder Point: 12) - Order 25 units URGENT

#### Dead Stock Analysis
Items with No Movement (90+ days):
- Product F - 23 units - $1,234.56
- Product G - 18 units - $987.65

### Inventory Optimization

#### ABC Analysis
- A Items (70% of value): 4 products
- B Items (20% of value): 6 products
- C Items (10% of value): 10 products

#### Recommended Reorder Quantities
1. Product B: 30 units
2. Product D: 22 units
3. Product E: 25 units
4. Product H: 15 units (approaching reorder point)

### Recommendations

1. **Immediate Action**: Place orders for Products B, D, and E which are below reorder points.
2. **Dead Stock Management**: Implement promotions to move Products F and G which show no movement.
3. **Category Management**: Review reorder points for Category 1 items which have high turnover.
4. **Inventory Accuracy**: Implement cycle counting for Category 3 items to improve accuracy.

### Appendix
- Detailed Inventory Listing
- Supplier Contact Information
- Historical Stock Level Trends
- Seasonal Demand Patterns
"""
    
    def _generate_sample_customer_report(self):
        """Generate sample customer report."""
        return """
# Customer Analysis Report
## Q1 2025

### Executive Summary
This report provides an analysis of customer behavior and segmentation for Q1 2025. The business currently has 434 active customers across four segments, with a 68% overall retention rate. The High Value segment (20% of customers) generates 45% of total revenue, highlighting the importance of retention efforts for this group.

### Customer Segmentation

#### Segment Overview
- High Value (20%): 87 customers - $45,678.90 revenue (45%)
- Regular (35%): 152 customers - $32,456.78 revenue (32%)
- Occasional (30%): 130 customers - $18,765.43 revenue (18%)
- New (15%): 65 customers - $5,432.10 revenue (5%)

#### Segment Behavior
- High Value: 8.7 purchases/quarter, $525.04 average order
- Regular: 4.3 purchases/quarter, $213.53 average order
- Occasional: 1.8 purchases/quarter, $144.35 average order
- New: 1.2 purchases/quarter, $83.57 average order

### Customer Retention

#### Retention Metrics
- Overall Retention Rate: 68%
- High Value Segment: 82%
- Regular Segment: 74%
- Occasional Segment: 53%

#### Churn Analysis
- Total Churned Customers: 47
- Churn Rate: 32%
- Average Tenure Before Churn: 8.3 months
- Most Common Churn Reason: Price sensitivity (42%)

### Customer Acquisition

#### Acquisition Metrics
- New Customers (Q1): 65
- Customer Acquisition Cost: $28.45
- Conversion Rate: 3.2%
- Most Effective Acquisition Channel: Organic search (38%)

### Customer Lifetime Value

#### CLV Analysis
- Average CLV: $876.54
- High Value Segment: $2,345.67
- Regular Segment: $987.65
- Occasional Segment: $432.10

#### CLV:CAC Ratio
- Overall Ratio: 30.8:1
- Payback Period: 3.2 months

### Geographic Insights

#### Customer Distribution
- North Region: 156 customers (36%)
- South Region: 134 customers (31%)
- East Region: 87 customers (20%)
- West Region: 57 customers (13%)

#### Regional Performance
- Highest CLV: North Region ($923.45)
- Highest Retention: East Region (72%)
- Fastest Growing: South Region (18% growth)

### Recommendations

1. **Retention Strategy**: Implement a tiered loyalty program targeting the Regular segment to increase retention and move them toward the High Value segment.
2. **Win-back Campaign**: Develop targeted offers for the Occasional segment which has the lowest retention rate.
3. **Acquisition Focus**: Optimize marketing spend toward organic search which shows the highest effectiveness.
4. **Geographic Expansion**: Increase marketing efforts in the West Region which has the lowest customer count but potential for growth.

### Appendix
- Detailed Segment Profiles
- Customer Journey Analysis
- Retention Curve Analysis
- Acquisition Channel Performance
"""
    
    def _generate_sample_financial_report(self):
        """Generate sample financial report."""
        return """
# Financial Performance Report
## Q1 2025

### Executive Summary
This report provides a comprehensive analysis of financial performance for Q1 2025. The business achieved total revenue of $789,453.21 with a gross profit margin of 42.3% and a net profit margin of 18.7%. Overall financial health is strong with a current ratio of 2.3 and a debt-to-equity ratio of 0.45.

### Income Statement Analysis

#### Revenue
- Total Revenue: $789,453.21
- Product Revenue: $723,456.78 (91.6%)
- Service Revenue: $65,996.43 (8.4%)
- YoY Growth: 15.3%

#### Profitability
- Gross Profit: $334,098.71 (42.3% margin)
- Operating Profit: $167,765.43 (21.2% margin)
- Net Profit: $147,627.75 (18.7% margin)
- EBITDA: $187,654.32 (23.8% margin)

#### Expense Breakdown
- Cost of Goods Sold: $456,789.01 (57.7%)
- Operating Expenses: $187,654.32 (23.6%)
- Marketing & Sales: $87,654.32 (11.1%)
- Administrative: $56,789.01 (7.2%)
- Other: $3,456.78 (0.4%)

### Cash Flow Analysis

#### Cash Flow Summary
- Operating Cash Flow: $178,945.32
- Investing Cash Flow: -$45,678.90
- Financing Cash Flow: -$67,890.12
- Net Cash Flow: $65,376.30

#### Cash Metrics
- Cash Conversion Cycle: 45 days
- Days Sales Outstanding: 32 days
- Days Inventory Outstanding: 53 days
- Days Payable Outstanding: 40 days

### Balance Sheet Analysis

#### Asset Overview
- Total Assets: $1,234,567.89
- Current Assets: $567,890.12 (46%)
- Fixed Assets: $666,677.77 (54%)

#### Liability Overview
- Total Liabilities: $456,789.01
- Current Liabilities: $246,789.01 (54%)
- Long-term Liabilities: $210,000.00 (46%)

#### Equity Overview
- Total Equity: $777,778.88
- Retained Earnings: $567,890.12 (73%)
- Paid-in Capital: $209,888.76 (27%)

### Financial Ratios

#### Liquidity Ratios
- Current Ratio: 2.3
- Quick Ratio: 1.8
- Cash Ratio: 0.9

#### Efficiency Ratios
- Asset Turnover: 1.7
- Inventory Turnover: 6.8
- Receivables Turnover: 11.4

#### Leverage Ratios
- Debt-to-Equity: 0.45
- Interest Coverage: 12.3
- Debt Ratio: 0.37

#### Profitability Ratios
- Return on Assets (ROA): 12.0%
- Return on Equity (ROE): 19.0%
- Return on Investment (ROI): 22.4%

### Break-Even Analysis

#### Break-Even Metrics
- Break-Even Point: $345,678.90
- Margin of Safety: 27.8%
- Contribution Margin: 65.3%

### Recommendations

1. **Cost Management**: Focus on reducing Cost of Goods Sold which represents the largest expense category.
2. **Debt Management**: Consider refinancing options to improve the debt-to-equity ratio and reduce interest expenses.
3. **Cash Flow Optimization**: Implement stricter accounts receivable policies to reduce Days Sales Outstanding and improve the cash conversion cycle.
4. **Revenue Diversification**: Increase service revenue which shows higher margins than product revenue.

### Appendix
- Detailed Income Statement
- Cash Flow Statement
- Balance Sheet
- Ratio Analysis Trends
- Comparative Industry Benchmarks
"""

    def _init_chat_tab(self):
        """Alarm CRM / attentive assistant chat tab."""
        frame = ttk.LabelFrame(self.chat_tab, text="Talk to the business-developer assistant")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.chat_log = tk.Text(frame, wrap=tk.WORD, height=16, state=tk.DISABLED)
        self.chat_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        row = ttk.Frame(frame)
        row.pack(fill=tk.X, padx=5, pady=5)
        self.chat_input_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.chat_input_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row, text="Send", command=self._send_chat).pack(side=tk.RIGHT, padx=5)
        ttk.Label(frame, text="Uses a generated Alarm CRM pack if BDFG_ALARM_ROOT is set.").pack(anchor=tk.W)

    def _init_memory_tab(self):
        """Show learned user facts and open loops."""
        frame = ttk.LabelFrame(self.memory_tab, text="What the assistant remembers")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.memory_text = tk.Text(frame, wrap=tk.WORD, height=18, state=tk.DISABLED)
        self.memory_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Button(frame, text="Refresh memory", command=self._refresh_memory).pack(anchor=tk.E, padx=5, pady=5)

    def _assistant(self):
        root = os.environ.get("BDFG_ALARM_ROOT")
        if not root or not os.path.isdir(root):
            return None
        from enhanced_bdfg.runtime.implement import load_coordinator
        if not hasattr(self, "_coord") or self._coord is None:
            self._coord = load_coordinator(root)
        return self._coord

    def _send_chat(self):
        msg = self.chat_input_var.get().strip()
        if not msg:
            return
        coord = self._assistant()
        reply = coord.chat(msg) if coord else (
            "Generate a pack first: bdfg implement alarm-crm --output ./generated/alarm_crm "
            "then set BDFG_ALARM_ROOT to that folder."
        )
        self.chat_input_var.set("")
        self.chat_log.configure(state=tk.NORMAL)
        self.chat_log.insert(tk.END, f"You: {msg}\nAssistant: {reply}\n\n")
        self.chat_log.configure(state=tk.DISABLED)
        self._refresh_memory()

    def _refresh_memory(self):
        coord = self._assistant()
        text = coord.memory.context_block(coord.user_id, coord.tenant_id) if coord else "No assistant loaded."
        self.memory_text.configure(state=tk.NORMAL)
        self.memory_text.delete("1.0", tk.END)
        self.memory_text.insert("1.0", text)
        self.memory_text.configure(state=tk.DISABLED)

# Command-line interface
if __name__ == "__main__":
    ui = BDFGUserInterface()
    ui.start()
