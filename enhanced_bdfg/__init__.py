"""
Enhanced BDFG Framework - Main Package Init
"""

from enhanced_bdfg.core.business_profiler import BusinessProfiler
from enhanced_bdfg.core.model_selector import ModelSelector
from enhanced_bdfg.core.hardware_manager import HardwareManager
from enhanced_bdfg.core.resource_manager import ResourceManager
from enhanced_bdfg.core.agent_generator import AgentGenerator
from enhanced_bdfg.core.framework_controller import FrameworkController
from enhanced_bdfg.core.prompt_engineering import PromptEngineer
from enhanced_bdfg.core.framework_packager import FrameworkPackager

from enhanced_bdfg.runtime.implement import implement_alarm_crm
from enhanced_bdfg.runtime.coordinator import AttentiveCoordinator
from enhanced_bdfg.runtime.packager import create_assistant

__version__ = "1.2.0"

__all__ = [
    "BusinessProfiler",
    "ModelSelector",
    "HardwareManager",
    "ResourceManager",
    "AgentGenerator",
    "FrameworkController",
    "PromptEngineer",
    "FrameworkPackager",
    "implement_alarm_crm",
    "AttentiveCoordinator",
    "create_assistant",
]


def __getattr__(name):
    # Optional analytics extra — imported only when asked for.
    mapping = {
        "DescriptiveAnalytics": "enhanced_bdfg.modules.descriptive_analytics",
        "DiagnosticAnalytics": "enhanced_bdfg.modules.diagnostic_analytics",
        "PredictiveAnalytics": "enhanced_bdfg.modules.predictive_analytics",
        "PrescriptiveAnalytics": "enhanced_bdfg.modules.prescriptive_analytics",
        "CognitiveAnalytics": "enhanced_bdfg.modules.cognitive_analytics",
    }
    if name in mapping:
        import importlib

        mod = importlib.import_module(mapping[name])
        return getattr(mod, name)
    raise AttributeError(name)
