"""
Hardware Manager Module

This module contains the HardwareManager class, which detects and manages hardware resources
for optimal model selection and execution.
"""

import os
import platform
import logging
import psutil
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HardwareManager:
    """
    The HardwareManager detects and manages hardware resources.
    
    It provides information about available CPU, RAM, disk space, and GPU resources
    to guide model selection and execution strategies.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the HardwareManager.
        
        Args:
            config: Configuration parameters for the hardware manager.
        """
        self.config = config or {}
        logger.info("Initializing HardwareManager")
        
        # Store hardware info cache
        self.hardware_info = None
        
        # Load hardware profiles
        self.hardware_profiles = self._load_hardware_profiles()
        
        logger.info("HardwareManager initialized successfully")
    
    def _load_hardware_profiles(self) -> Dict[str, Any]:
        """
        Load hardware profiles for different device types.
        
        Returns:
            A dictionary mapping device types to hardware profiles.
        """
        # In a real implementation, this would load from a file or database
        return {
            "raspberry_pi": {
                "name": "Raspberry Pi",
                "cpu_cores_max": 4,
                "ram_max": 8,  # GB
                "disk_max": 64,  # GB
                "recommended_models": ["tinyllama", "qwen35_4b", "phi2"],
                "quantization": "4bit"
            },
            "laptop": {
                "name": "Standard Laptop",
                "cpu_cores_max": 8,
                "ram_max": 16,  # GB
                "disk_max": 512,  # GB
                "recommended_models": ["phi2", "mistral7b"],
                "quantization": "8bit"
            },
            "desktop": {
                "name": "Desktop Computer",
                "cpu_cores_max": 16,
                "ram_max": 32,  # GB
                "disk_max": 1024,  # GB
                "recommended_models": ["mistral7b", "llama3"],
                "quantization": "8bit"
            },
            "workstation": {
                "name": "High-End Workstation",
                "cpu_cores_max": 32,
                "ram_max": 128,  # GB
                "disk_max": 2048,  # GB
                "recommended_models": ["llama3", "mixtral"],
                "quantization": None
            },
            "server": {
                "name": "Server",
                "cpu_cores_max": 64,
                "ram_max": 256,  # GB
                "disk_max": 4096,  # GB
                "recommended_models": ["mixtral"],
                "quantization": None
            }
        }
    
    def detect_hardware(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Detect available hardware resources.
        
        Args:
            force_refresh: Whether to force a refresh of the hardware info cache.
            
        Returns:
            A dictionary containing information about available hardware resources.
        """
        if self.hardware_info is not None and not force_refresh:
            return self.hardware_info
        
        logger.info("Detecting hardware resources")
        
        # Get CPU info
        cpu_count = psutil.cpu_count(logical=True)
        cpu_physical = psutil.cpu_count(logical=False)
        
        # Get memory info
        memory = psutil.virtual_memory()
        ram_gb = round(memory.total / (1024 ** 3), 1)  # Convert bytes to GB
        
        # Get disk info
        disk = psutil.disk_usage('/')
        disk_gb = round(disk.total / (1024 ** 3), 1)  # Convert bytes to GB
        
        # Get system info
        system = platform.system()
        release = platform.release()
        
        # Detect GPU (simplified, would be more complex in a real implementation)
        gpu_info = self._detect_gpu()
        
        # Determine device type
        device_type = self._determine_device_type(cpu_count, ram_gb, disk_gb)
        
        # Create hardware info dictionary
        self.hardware_info = {
            "cpu": {
                "cores": cpu_count,
                "physical_cores": cpu_physical
            },
            "ram": ram_gb,
            "disk": disk_gb,
            "gpu": gpu_info,
            "system": {
                "os": system,
                "release": release
            },
            "device_type": device_type,
            "profile": self.hardware_profiles.get(device_type, {})
        }
        
        logger.info(f"Detected {device_type} with {cpu_count} CPU cores, {ram_gb} GB RAM, {disk_gb} GB disk")
        if gpu_info:
            logger.info(f"GPU detected: {gpu_info.get('name', 'Unknown')}")
        
        return self.hardware_info
    
    def _detect_gpu(self) -> Optional[Dict[str, Any]]:
        """
        Detect available GPU resources via nvidia-smi, PyTorch, or platform tools.
        """
        # NVIDIA via nvidia-smi
        smi_paths = ["/usr/bin/nvidia-smi", "nvidia-smi"]
        for smi in smi_paths:
            try:
                import subprocess
                result = subprocess.run(
                    [smi, "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                    capture_output=True, text=True, timeout=5,
                )
                if result.returncode == 0 and result.stdout.strip():
                    line = result.stdout.strip().splitlines()[0]
                    parts = [p.strip() for p in line.split(",")]
                    name = parts[0] if parts else "NVIDIA GPU"
                    memory = None
                    if len(parts) > 1:
                        try:
                            memory = float(parts[1]) / 1024.0  # MiB -> GiB
                        except ValueError:
                            memory = None
                    return {"name": name, "available": True, "memory": memory, "vendor": "nvidia"}
            except Exception as e:
                logger.debug("nvidia-smi probe failed: %s", e)

        try:
            import torch
            if torch.cuda.is_available():
                name = torch.cuda.get_device_name(0)
                mem = None
                try:
                    mem = round(torch.cuda.get_device_properties(0).total_memory / (1024 ** 3), 1)
                except Exception:
                    pass
                return {"name": name, "available": True, "memory": mem, "vendor": "cuda"}
        except Exception:
            pass

        if platform.system() == "Darwin":
            try:
                gpu_info = os.popen("system_profiler SPDisplaysDataType").read()
                if "Metal" in gpu_info or "Apple" in gpu_info:
                    return {"name": "Apple GPU", "available": True, "memory": None, "vendor": "apple"}
            except Exception as e:
                logger.warning("Error detecting Apple GPU: %s", e)

        if platform.system() == "Windows":
            try:
                wmic = os.popen("wmic path win32_VideoController get name").read()
                if "NVIDIA" in wmic:
                    return {"name": "NVIDIA GPU", "available": True, "memory": None, "vendor": "nvidia"}
            except Exception as e:
                logger.warning("Error detecting Windows GPU: %s", e)

        return None
    
    def _determine_device_type(self, cpu_count: int, ram_gb: float, disk_gb: float) -> str:
        """
        Determine the device type based on hardware specifications.
        
        Args:
            cpu_count: Number of CPU cores.
            ram_gb: Amount of RAM in GB.
            disk_gb: Amount of disk space in GB.
            
        Returns:
            The determined device type.
        """
        # Check if it's a Raspberry Pi or similar
        if cpu_count <= 4 and ram_gb <= 8:
            return "raspberry_pi"
        
        # Check if it's a laptop
        elif cpu_count <= 8 and ram_gb <= 16:
            return "laptop"
        
        # Check if it's a desktop
        elif cpu_count <= 16 and ram_gb <= 32:
            return "desktop"
        
        # Check if it's a workstation
        elif cpu_count <= 32 and ram_gb <= 128:
            return "workstation"
        
        # Otherwise, it's a server
        else:
            return "server"
    
    def get_recommended_models(self) -> Dict[str, Any]:
        """
        Get recommended models based on detected hardware.
        
        Returns:
            A dictionary containing recommended models and configurations.
        """
        # Ensure hardware has been detected
        if self.hardware_info is None:
            self.detect_hardware()
        
        device_type = self.hardware_info.get("device_type", "laptop")
        profile = self.hardware_profiles.get(device_type, {})
        
        return {
            "recommended_models": profile.get("recommended_models", ["phi2"]),
            "quantization": profile.get("quantization", "8bit")
        }
    
    def get_resource_constraints(self) -> Dict[str, Any]:
        """
        Get resource constraints for model execution.
        
        Returns:
            A dictionary containing resource constraints.
        """
        # Ensure hardware has been detected
        if self.hardware_info is None:
            self.detect_hardware()
        
        # Calculate available resources for model execution
        # In a real implementation, this would be more sophisticated
        ram_gb = self.hardware_info.get("ram", 8)
        cpu_cores = self.hardware_info.get("cpu", {}).get("cores", 4)
        
        # Reserve some resources for the system
        available_ram = max(1, ram_gb - 2)  # Reserve 2GB for system
        available_cores = max(1, cpu_cores - 1)  # Reserve 1 core for system
        
        return {
            "available_ram": available_ram,
            "available_cores": available_cores,
            "can_use_gpu": self.hardware_info.get("gpu", {}).get("available", False)
        }
    
    def get_hardware_info(self) -> Dict[str, Any]:
        """
        Get the detected hardware information.
        
        Returns:
            A dictionary containing information about available hardware resources.
        """
        # Ensure hardware has been detected
        if self.hardware_info is None:
            self.detect_hardware()
        
        return self.hardware_info
    
    def optimize_execution_settings(self, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize execution settings for a model based on hardware capabilities.
        
        Args:
            model_config: The model configuration.
            
        Returns:
            A dictionary containing optimized execution settings.
        """
        # Ensure hardware has been detected
        if self.hardware_info is None:
            self.detect_hardware()
        
        # Get resource constraints
        constraints = self.get_resource_constraints()
        
        # Determine thread count
        thread_count = min(constraints["available_cores"], 4)  # Use at most 4 threads
        
        # Determine batch size
        batch_size = 1  # Default
        if constraints["available_ram"] > 8:
            batch_size = 4
        elif constraints["available_ram"] > 4:
            batch_size = 2
        
        # Determine whether to use GPU
        use_gpu = constraints["can_use_gpu"]
        
        # Create execution settings
        execution_settings = {
            "thread_count": thread_count,
            "batch_size": batch_size,
            "use_gpu": use_gpu,
            "low_memory_mode": constraints["available_ram"] < 4
        }
        
        logger.info(f"Optimized execution settings: {execution_settings}")
        return execution_settings
