"""
Resource Manager Module

This module contains the ResourceManager class, which manages computational resources
for efficient model execution and task scheduling.
"""

import logging
import threading
import time
from typing import Dict, Any, List, Callable, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResourceManager:
    """
    The ResourceManager manages computational resources for efficient model execution.
    
    It handles resource allocation, task scheduling, and batch processing to optimize
    performance on available hardware.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the ResourceManager.
        
        Args:
            config: Configuration parameters for the resource manager.
        """
        self.config = config or {}
        logger.info("Initializing ResourceManager")
        
        # Initialize resource tracking
        self.resource_usage = {
            "cpu": 0.0,  # Percentage of CPU cores in use
            "ram": 0.0,  # Percentage of RAM in use
            "gpu": 0.0   # Percentage of GPU in use (if available)
        }
        
        # Initialize task queue and worker threads
        self.task_queue = []
        self.workers = []
        self.max_workers = self.config.get("max_workers", 4)
        self.worker_lock = threading.Lock()
        
        # Initialize batch processing settings
        self.batch_size = self.config.get("batch_size", 16)
        self.max_sequence_length = self.config.get("max_sequence_length", 2048)
        
        logger.info("ResourceManager initialized successfully")
    
    def update_resource_usage(self, hardware_info: Dict[str, Any]) -> None:
        """
        Update resource usage information based on current system state.
        
        Args:
            hardware_info: Information about available hardware resources.
        """
        import psutil
        
        # Update CPU usage
        cpu_usage = psutil.cpu_percent(interval=0.1) / 100.0
        self.resource_usage["cpu"] = cpu_usage
        
        # Update RAM usage
        memory = psutil.virtual_memory()
        ram_usage = memory.percent / 100.0
        self.resource_usage["ram"] = ram_usage
        
        # Update GPU usage if available (simplified)
        gpu_available = hardware_info.get("gpu", {}).get("available", False)
        if gpu_available:
            # In a real implementation, this would query the GPU
            # For now, we'll just use a placeholder value
            self.resource_usage["gpu"] = 0.5  # 50% usage as a placeholder
        else:
            self.resource_usage["gpu"] = 0.0
        
        logger.debug(f"Resource usage updated: CPU {cpu_usage:.2f}, RAM {ram_usage:.2f}, GPU {self.resource_usage['gpu']:.2f}")
    
    def allocate_resources(self, task_requirements: Dict[str, Any], 
                          hardware_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Allocate resources for a task based on requirements and availability.
        
        Args:
            task_requirements: Resource requirements for the task.
            hardware_info: Information about available hardware resources.
            
        Returns:
            A dictionary containing allocated resources and execution strategy.
        """
        logger.info(f"Allocating resources for task: {task_requirements.get('name', 'unnamed')}")
        
        # Get available resources
        available_ram = hardware_info.get("ram", 8) * (1.0 - self.resource_usage["ram"])
        available_cores = hardware_info.get("cpu", {}).get("cores", 4) * (1.0 - self.resource_usage["cpu"])
        
        # Get task requirements
        required_ram = task_requirements.get("ram_required", 1)
        required_cores = task_requirements.get("cores_required", 1)
        
        # Check if resources are available
        if required_ram > available_ram or required_cores > available_cores:
            logger.warning(f"Insufficient resources for task: {task_requirements.get('name', 'unnamed')}")
            
            # Determine fallback strategy
            if required_ram > available_ram:
                # Need to reduce memory usage
                strategy = "quantize"
                if required_ram > available_ram * 2:  # If even quantization won't help
                    strategy = "offload"
            else:
                # Need to reduce CPU usage
                strategy = "queue"
            
            return {
                "allocated": False,
                "strategy": strategy,
                "available_ram": available_ram,
                "available_cores": available_cores
            }
        
        # Resources are available, allocate them
        logger.info(f"Resources allocated for task: {task_requirements.get('name', 'unnamed')}")
        return {
            "allocated": True,
            "strategy": "direct",
            "ram_allocated": required_ram,
            "cores_allocated": required_cores
        }
    
    def schedule_task(self, task: Callable, task_requirements: Dict[str, Any], 
                     hardware_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule a task for execution based on resource availability.
        
        Args:
            task: The task function to execute.
            task_requirements: Resource requirements for the task.
            hardware_info: Information about available hardware resources.
            
        Returns:
            A dictionary containing task ID and scheduling information.
        """
        # Generate a task ID
        task_id = f"task_{int(time.time())}_{len(self.task_queue)}"
        
        # Allocate resources
        allocation = self.allocate_resources(task_requirements, hardware_info)
        
        # Create task entry
        task_entry = {
            "id": task_id,
            "task": task,
            "requirements": task_requirements,
            "allocation": allocation,
            "status": "pending",
            "result": None,
            "error": None
        }
        
        # Add to queue or execute directly based on allocation strategy
        if allocation["allocated"] and allocation["strategy"] == "direct":
            # Execute directly
            self._execute_task(task_entry)
        else:
            # Add to queue
            self.task_queue.append(task_entry)
            logger.info(f"Task {task_id} added to queue with strategy: {allocation['strategy']}")
            
            # Start worker if needed
            self._ensure_workers()
        
        return {
            "task_id": task_id,
            "status": task_entry["status"],
            "strategy": allocation["strategy"]
        }
    
    def _execute_task(self, task_entry: Dict[str, Any]) -> None:
        """
        Execute a task with allocated resources.
        
        Args:
            task_entry: The task entry containing the task and its information.
        """
        task_id = task_entry["id"]
        logger.info(f"Executing task {task_id}")
        
        task_entry["status"] = "running"
        
        try:
            # Execute the task
            result = task_entry["task"]()
            task_entry["result"] = result
            task_entry["status"] = "completed"
            logger.info(f"Task {task_id} completed successfully")
        except Exception as e:
            task_entry["error"] = str(e)
            task_entry["status"] = "failed"
            logger.error(f"Task {task_id} failed with error: {e}")
    
    def _worker_thread(self) -> None:
        """
        Worker thread function for processing tasks from the queue.
        """
        logger.info("Worker thread started")
        
        while True:
            # Check if there are tasks in the queue
            if not self.task_queue:
                # No tasks, sleep for a bit
                time.sleep(0.1)
                continue
            
            # Get the next task
            with self.worker_lock:
                if not self.task_queue:
                    continue
                
                task_entry = self.task_queue.pop(0)
            
            # Execute the task
            self._execute_task(task_entry)
    
    def _ensure_workers(self) -> None:
        """
        Ensure that worker threads are running to process the task queue.
        """
        with self.worker_lock:
            # Check if we need to start more workers
            while len(self.workers) < self.max_workers:
                # Start a new worker thread
                worker = threading.Thread(target=self._worker_thread, daemon=True)
                worker.start()
                self.workers.append(worker)
                logger.info(f"Started worker thread {len(self.workers)}")
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a scheduled task.
        
        Args:
            task_id: The ID of the task to check.
            
        Returns:
            A dictionary containing task status information.
        """
        # Check the task queue
        for task_entry in self.task_queue:
            if task_entry["id"] == task_id:
                return {
                    "task_id": task_id,
                    "status": task_entry["status"],
                    "result": task_entry.get("result"),
                    "error": task_entry.get("error")
                }
        
        # Task not found
        return {
            "task_id": task_id,
            "status": "unknown",
            "error": "Task not found"
        }
    
    def optimize_batch_size(self, model_info: Dict[str, Any], hardware_info: Dict[str, Any]) -> int:
        """
        Optimize batch size for efficient model execution.
        
        Args:
            model_info: Information about the model.
            hardware_info: Information about available hardware resources.
            
        Returns:
            The optimized batch size.
        """
        # Get model and hardware information
        model_size = model_info.get("parameters", "7B")
        ram_gb = hardware_info.get("ram", 8)
        
        # Convert model size to numeric value (billions of parameters)
        if isinstance(model_size, str):
            if model_size.endswith("B"):
                model_size = float(model_size[:-1])
            else:
                model_size = float(model_size) / 1e9  # Convert to billions
        
        # Calculate optimal batch size based on model size and available RAM
        # This is a simplified heuristic
        if model_size <= 1:
            base_batch_size = 32
        elif model_size <= 3:
            base_batch_size = 16
        elif model_size <= 7:
            base_batch_size = 8
        elif model_size <= 13:
            base_batch_size = 4
        else:
            base_batch_size = 2
        
        # Adjust based on available RAM
        ram_factor = ram_gb / 16.0  # Normalize to 16GB
        adjusted_batch_size = max(1, int(base_batch_size * ram_factor))
        
        # Cap at configured maximum
        optimized_batch_size = min(adjusted_batch_size, self.batch_size)
        
        logger.info(f"Optimized batch size for {model_size}B model: {optimized_batch_size}")
        return optimized_batch_size
    
    def optimize_sequence_length(self, model_info: Dict[str, Any], hardware_info: Dict[str, Any]) -> int:
        """
        Optimize sequence length for efficient model execution.
        
        Args:
            model_info: Information about the model.
            hardware_info: Information about available hardware resources.
            
        Returns:
            The optimized sequence length.
        """
        # Get model and hardware information
        model_size = model_info.get("parameters", "7B")
        ram_gb = hardware_info.get("ram", 8)
        
        # Convert model size to numeric value (billions of parameters)
        if isinstance(model_size, str):
            if model_size.endswith("B"):
                model_size = float(model_size[:-1])
            else:
                model_size = float(model_size) / 1e9  # Convert to billions
        
        # Calculate optimal sequence length based on model size and available RAM
        # This is a simplified heuristic
        if model_size <= 1:
            base_seq_length = 4096
        elif model_size <= 3:
            base_seq_length = 2048
        elif model_size <= 7:
            base_seq_length = 1024
        elif model_size <= 13:
            base_seq_length = 512
        else:
            base_seq_length = 256
        
        # Adjust based on available RAM
        ram_factor = ram_gb / 16.0  # Normalize to 16GB
        adjusted_seq_length = max(256, int(base_seq_length * ram_factor))
        
        # Cap at configured maximum
        optimized_seq_length = min(adjusted_seq_length, self.max_sequence_length)
        
        logger.info(f"Optimized sequence length for {model_size}B model: {optimized_seq_length}")
        return optimized_seq_length
    
    def get_execution_plan(self, model_info: Dict[str, Any], hardware_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get an execution plan for a model based on hardware capabilities.
        
        Args:
            model_info: Information about the model.
            hardware_info: Information about available hardware resources.
            
        Returns:
            A dictionary containing the execution plan.
        """
        # Optimize batch size and sequence length
        batch_size = self.optimize_batch_size(model_info, hardware_info)
        sequence_length = self.optimize_sequence_length(model_info, hardware_info)
        
        # Determine threading strategy
        cpu_cores = hardware_info.get("cpu", {}).get("cores", 4)
        thread_count = min(cpu_cores - 1, 4)  # Use at most 4 threads, leave 1 for system
        
        # Determine GPU usage
        gpu_available = hardware_info.get("gpu", {}).get("available", False)
        
        # Create execution plan
        execution_plan = {
            "batch_size": batch_size,
            "sequence_length": sequence_length,
            "thread_count": thread_count,
            "use_gpu": gpu_available,
            "low_memory_mode": hardware_info.get("ram", 8) < 8
        }
        
        logger.info(f"Execution plan created: {execution_plan}")
        return execution_plan
