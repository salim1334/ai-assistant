"""
Framework Packager Module

This module contains the FrameworkPackager class, which packages the generated
agent framework into deployable formats.
"""

import os
import shutil
import zipfile
import logging
import json
import subprocess
from typing import Dict, Any, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FrameworkPackager:
    """
    The FrameworkPackager packages the generated agent framework into deployable formats.
    
    It handles creating distributable packages, documentation generation, and
    deployment configuration for different environments.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the FrameworkPackager.
        
        Args:
            config: Configuration parameters for the framework packager.
        """
        self.config = config or {}
        logger.info("Initializing FrameworkPackager")
        
        # Set default output directory
        self.output_dir = self.config.get("output_dir", "dist")
        
        # Set default package formats
        self.package_formats = self.config.get("package_formats", ["zip", "wheel"])
        
        logger.info("FrameworkPackager initialized successfully")
    
    def create_zip_package(self, framework_dir: str, output_file: Optional[str] = None) -> str:
        """
        Create a ZIP package of the framework.
        
        Args:
            framework_dir: Directory containing the framework.
            output_file: Optional path for the output ZIP file.
            
        Returns:
            Path to the created ZIP file.
        """
        if output_file is None:
            # Create output directory if it doesn't exist
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Generate output file name
            framework_name = os.path.basename(framework_dir)
            output_file = os.path.join(self.output_dir, f"{framework_name}.zip")
        
        logger.info(f"Creating ZIP package from {framework_dir} to {output_file}")
        
        # Create a zip file
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(framework_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(framework_dir))
                    zipf.write(file_path, arcname)
        
        logger.info(f"ZIP package created at {output_file}")
        return output_file
    
    def create_wheel_package(self, framework_dir: str) -> str:
        """
        Create a Python wheel package of the framework.
        
        Args:
            framework_dir: Directory containing the framework.
            
        Returns:
            Path to the created wheel file.
        """
        logger.info(f"Creating wheel package from {framework_dir}")
        
        # Save current working directory
        original_dir = os.getcwd()
        
        try:
            # Change to framework directory
            os.chdir(framework_dir)
            
            # Create wheel package
            result = subprocess.run(
                ["python", "setup.py", "bdist_wheel"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Find the wheel file
            dist_dir = os.path.join(framework_dir, "dist")
            wheel_files = [f for f in os.listdir(dist_dir) if f.endswith(".whl")]
            
            if not wheel_files:
                raise Exception("No wheel file was created")
            
            wheel_path = os.path.join(dist_dir, wheel_files[0])
            
            # Copy wheel to output directory
            os.makedirs(self.output_dir, exist_ok=True)
            output_path = os.path.join(self.output_dir, wheel_files[0])
            shutil.copy2(wheel_path, output_path)
            
            logger.info(f"Wheel package created at {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating wheel package: {e}")
            raise
        finally:
            # Restore original working directory
            os.chdir(original_dir)
    
    def create_docker_package(self, framework_dir: str, image_name: Optional[str] = None) -> str:
        """
        Create a Docker image of the framework.
        
        Args:
            framework_dir: Directory containing the framework.
            image_name: Optional name for the Docker image.
            
        Returns:
            Name of the created Docker image.
        """
        logger.info(f"Creating Docker image from {framework_dir}")
        
        # Generate image name if not provided
        if image_name is None:
            framework_name = os.path.basename(framework_dir).lower()
            image_name = f"{framework_name}:latest"
        
        # Create Dockerfile
        dockerfile_path = os.path.join(framework_dir, "Dockerfile")
        with open(dockerfile_path, "w") as f:
            f.write(f"""FROM python:3.9-slim

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["python", "app.py"]
""")
        
        # Create .dockerignore
        dockerignore_path = os.path.join(framework_dir, ".dockerignore")
        with open(dockerignore_path, "w") as f:
            f.write("""__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.env
.venv
env/
venv/
ENV/
.git/
.gitignore
Dockerfile
.dockerignore
""")
        
        try:
            # Build Docker image
            result = subprocess.run(
                ["docker", "build", "-t", image_name, framework_dir],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Docker image created: {image_name}")
            
            # Save Docker image
            os.makedirs(self.output_dir, exist_ok=True)
            image_tar_path = os.path.join(self.output_dir, f"{image_name.replace(':', '_')}.tar")
            
            result = subprocess.run(
                ["docker", "save", "-o", image_tar_path, image_name],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Docker image saved to {image_tar_path}")
            return image_name
            
        except Exception as e:
            logger.error(f"Error creating Docker image: {e}")
            raise
    
    def generate_documentation(self, framework_dir: str) -> str:
        """
        Generate documentation for the framework.
        
        Args:
            framework_dir: Directory containing the framework.
            
        Returns:
            Path to the generated documentation.
        """
        logger.info(f"Generating documentation for {framework_dir}")
        
        # Create docs directory
        docs_dir = os.path.join(framework_dir, "docs")
        os.makedirs(docs_dir, exist_ok=True)
        
        # Create basic documentation structure
        self._create_basic_docs(framework_dir, docs_dir)
        
        # Try to generate API documentation with Sphinx
        try:
            self._generate_sphinx_docs(framework_dir, docs_dir)
        except Exception as e:
            logger.warning(f"Could not generate Sphinx documentation: {e}")
            logger.info("Falling back to basic documentation")
        
        logger.info(f"Documentation generated at {docs_dir}")
        return docs_dir
    
    def _create_basic_docs(self, framework_dir: str, docs_dir: str) -> None:
        """
        Create basic documentation for the framework.
        
        Args:
            framework_dir: Directory containing the framework.
            docs_dir: Directory to output documentation.
        """
        # Get framework name
        framework_name = os.path.basename(framework_dir)
        
        # Create index.md
        with open(os.path.join(docs_dir, "index.md"), "w") as f:
            f.write(f"""# {framework_name} Documentation

Welcome to the {framework_name} documentation.

## Overview

This framework provides specialized analytics agents for business intelligence.

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

## Modules

- **Agents**: Domain-specific analytics agents
- **Data**: Data connectors and processors
- **Knowledge**: Industry and business-specific knowledge
- **Models**: Model configurations and weights
- **Tools**: Industry-specific and general tools

## API Reference

See the [API Reference](api.md) for detailed information about the framework's API.
""")
        
        # Create api.md
        with open(os.path.join(docs_dir, "api.md"), "w") as f:
            f.write(f"""# API Reference

## Agents

### DescriptiveAnalyticsAgent

Analyzes historical data to identify patterns and trends.

```python
from agents.descriptive.agent import DescriptiveAnalyticsAgent

agent = DescriptiveAnalyticsAgent('agents/descriptive/config.json')
results = agent.analyze(data)
```

### DiagnosticAnalyticsAgent

Determines why certain events occurred by identifying root causes.

```python
from agents.diagnostic.agent import DiagnosticAnalyticsAgent

agent = DiagnosticAnalyticsAgent('agents/diagnostic/config.json')
results = agent.analyze(data)
```

### PredictiveAnalyticsAgent

Forecasts future trends and outcomes based on historical data.

```python
from agents.predictive.agent import PredictiveAnalyticsAgent

agent = PredictiveAnalyticsAgent('agents/predictive/config.json')
results = agent.analyze(data)
```

### PrescriptiveAnalyticsAgent

Recommends actions to optimize business outcomes.

```python
from agents.prescriptive.agent import PrescriptiveAnalyticsAgent

agent = PrescriptiveAnalyticsAgent('agents/prescriptive/config.json')
results = agent.analyze(data)
```

### CognitiveAnalyticsAgent

Analyzes unstructured data like text, images, and human feedback.

```python
from agents.cognitive.agent import CognitiveAnalyticsAgent

agent = CognitiveAnalyticsAgent('agents/cognitive/config.json')
results = agent.analyze(data)
```
""")
        
        # Create getting_started.md
        with open(os.path.join(docs_dir, "getting_started.md"), "w") as f:
            f.write(f"""# Getting Started

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/{framework_name}.git
cd {framework_name}
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install the package:

```bash
pip install -e .
```

## Quick Start

### Using the Web Interface

1. Start the web interface:

```bash
python app.py
```

2. Open your browser and navigate to http://localhost:8501

3. Select an analytics domain and enter your data in JSON format

4. Click "Analyze" to get results

### Using the Command Line Interface

1. Run the CLI with help to see available options:

```bash
python cli.py --help
```

2. Analyze data with a specific domain:

```bash
python cli.py --domain descriptive --data data.json --output results.json
```

## Examples

### Descriptive Analytics

```python
from agents.descriptive.agent import DescriptiveAnalyticsAgent

# Initialize the agent
agent = DescriptiveAnalyticsAgent('agents/descriptive/config.json')

# Prepare data
data = {
    "sales": [
        {"date": "2024-01-01", "amount": 1200},
        {"date": "2024-01-02", "amount": 1500},
        {"date": "2024-01-03", "amount": 1100},
        # ...
    ]
}

# Analyze data
results = agent.analyze(data)
print(results)
```

### Predictive Analytics

```python
from agents.predictive.agent import PredictiveAnalyticsAgent

# Initialize the agent
agent = PredictiveAnalyticsAgent('agents/predictive/config.json')

# Prepare data
data = {
    "historical_sales": [
        {"date": "2024-01-01", "amount": 1200},
        {"date": "2024-01-02", "amount": 1500},
        {"date": "2024-01-03", "amount": 1100},
        # ...
    ]
}

# Analyze data
forecast = agent.analyze(data)
print(forecast)
```
""")
    
    def _generate_sphinx_docs(self, framework_dir: str, docs_dir: str) -> None:
        """
        Generate Sphinx documentation for the framework.
        
        Args:
            framework_dir: Directory containing the framework.
            docs_dir: Directory to output documentation.
        """
        # Create Sphinx configuration
        sphinx_dir = os.path.join(docs_dir, "sphinx")
        os.makedirs(sphinx_dir, exist_ok=True)
        
        # Create conf.py
        with open(os.path.join(sphinx_dir, "conf.py"), "w") as f:
            f.write(f"""# Configuration file for the Sphinx documentation builder.

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------

project = '{os.path.basename(framework_dir)}'
copyright = '2024, BDFG Framework'
author = 'BDFG Framework'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
""")
        
        # Create index.rst
        with open(os.path.join(sphinx_dir, "index.rst"), "w") as f:
            f.write(f"""Welcome to {os.path.basename(framework_dir)}'s documentation!
{'=' * (len(os.path.basename(framework_dir)) + 24)}

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules
   agents
   data
   knowledge
   models
   tools

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
""")
        
        # Create agents.rst
        with open(os.path.join(sphinx_dir, "agents.rst"), "w") as f:
            f.write("""Agents
======

Descriptive Analytics
--------------------

.. automodule:: agents.descriptive.agent
   :members:
   :undoc-members:
   :show-inheritance:

Diagnostic Analytics
-------------------

.. automodule:: agents.diagnostic.agent
   :members:
   :undoc-members:
   :show-inheritance:

Predictive Analytics
-------------------

.. automodule:: agents.predictive.agent
   :members:
   :undoc-members:
   :show-inheritance:

Prescriptive Analytics
---------------------

.. automodule:: agents.prescriptive.agent
   :members:
   :undoc-members:
   :show-inheritance:

Cognitive Analytics
------------------

.. automodule:: agents.cognitive.agent
   :members:
   :undoc-members:
   :show-inheritance:
""")
        
        # Try to run Sphinx
        try:
            # Save current working directory
            original_dir = os.getcwd()
            
            # Change to Sphinx directory
            os.chdir(sphinx_dir)
            
            # Run sphinx-apidoc
            subprocess.run(
                ["sphinx-apidoc", "-o", ".", "../.."],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Run sphinx-build
            subprocess.run(
                ["sphinx-build", "-b", "html", ".", "_build/html"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Copy built documentation to docs directory
            html_dir = os.path.join(docs_dir, "html")
            os.makedirs(html_dir, exist_ok=True)
            
            for item in os.listdir(os.path.join(sphinx_dir, "_build/html")):
                src = os.path.join(sphinx_dir, "_build/html", item)
                dst = os.path.join(html_dir, item)
                
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
            
        except Exception as e:
            logger.error(f"Error generating Sphinx documentation: {e}")
            raise
        finally:
            # Restore original working directory
            os.chdir(original_dir)
    
    def create_deployment_config(self, framework_dir: str, deployment_type: str) -> str:
        """
        Create deployment configuration for the framework.
        
        Args:
            framework_dir: Directory containing the framework.
            deployment_type: Type of deployment (local, cloud, docker, kubernetes).
            
        Returns:
            Path to the created deployment configuration.
        """
        logger.info(f"Creating {deployment_type} deployment configuration for {framework_dir}")
        
        # Create deployment directory
        deploy_dir = os.path.join(framework_dir, "deployment")
        os.makedirs(deploy_dir, exist_ok=True)
        
        # Create deployment configuration based on type
        if deployment_type == "local":
            config_path = self._create_local_deployment_config(framework_dir, deploy_dir)
        elif deployment_type == "cloud":
            config_path = self._create_cloud_deployment_config(framework_dir, deploy_dir)
        elif deployment_type == "docker":
            config_path = self._create_docker_deployment_config(framework_dir, deploy_dir)
        elif deployment_type == "kubernetes":
            config_path = self._create_kubernetes_deployment_config(framework_dir, deploy_dir)
        else:
            raise ValueError(f"Unsupported deployment type: {deployment_type}")
        
        logger.info(f"Deployment configuration created at {config_path}")
        return config_path
    
    def _create_local_deployment_config(self, framework_dir: str, deploy_dir: str) -> str:
        """
        Create local deployment configuration.
        
        Args:
            framework_dir: Directory containing the framework.
            deploy_dir: Directory to output deployment configuration.
            
        Returns:
            Path to the created deployment configuration.
        """
        config_path = os.path.join(deploy_dir, "local_deployment.md")
        
        with open(config_path, "w") as f:
            f.write(f"""# Local Deployment Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/{os.path.basename(framework_dir)}.git
cd {os.path.basename(framework_dir)}
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install the package:

```bash
pip install -e .
```

## Running the Web Interface

```bash
python app.py
```

The web interface will be available at http://localhost:8501

## Running the Command Line Interface

```bash
python cli.py --help
```

## Configuration

You can customize the framework by editing the configuration files in the `agents` directory.

Each agent has its own configuration file at `agents/<domain>/config.json`.
""")
        
        return config_path
    
    def _create_cloud_deployment_config(self, framework_dir: str, deploy_dir: str) -> str:
        """
        Create cloud deployment configuration.
        
        Args:
            framework_dir: Directory containing the framework.
            deploy_dir: Directory to output deployment configuration.
            
        Returns:
            Path to the created deployment configuration.
        """
        config_path = os.path.join(deploy_dir, "cloud_deployment.md")
        
        with open(config_path, "w") as f:
            f.write(f"""# Cloud Deployment Guide

## AWS Deployment

### Prerequisites

- AWS account
- AWS CLI installed and configured
- Elastic Beanstalk CLI (optional)

### Deployment Steps

1. Create a new Elastic Beanstalk application:

```bash
eb init -p python-3.8 {os.path.basename(framework_dir)}
```

2. Create a new environment:

```bash
eb create {os.path.basename(framework_dir)}-env
```

3. Deploy the application:

```bash
eb deploy
```

## Google Cloud Platform Deployment

### Prerequisites

- GCP account
- gcloud CLI installed and configured

### Deployment Steps

1. Create a new App Engine application:

```bash
gcloud app create
```

2. Deploy the application:

```bash
gcloud app deploy app.yaml
```

## Microsoft Azure Deployment

### Prerequisites

- Azure account
- Azure CLI installed and configured

### Deployment Steps

1. Create a new App Service:

```bash
az webapp up --sku F1 --name {os.path.basename(framework_dir)} --resource-group {os.path.basename(framework_dir)}-group
```

2. Deploy the application:

```bash
az webapp deployment source config-zip --resource-group {os.path.basename(framework_dir)}-group --name {os.path.basename(framework_dir)} --src {os.path.basename(framework_dir)}.zip
```
""")
        
        # Create app.yaml for Google Cloud Platform
        app_yaml_path = os.path.join(deploy_dir, "app.yaml")
        with open(app_yaml_path, "w") as f:
            f.write("""runtime: python39

entrypoint: gunicorn -b :$PORT main:app

env_variables:
  PYTHONUNBUFFERED: 1
""")
        
        # Create Procfile for Heroku
        procfile_path = os.path.join(deploy_dir, "Procfile")
        with open(procfile_path, "w") as f:
            f.write("web: gunicorn main:app")
        
        return config_path
    
    def _create_docker_deployment_config(self, framework_dir: str, deploy_dir: str) -> str:
        """
        Create Docker deployment configuration.
        
        Args:
            framework_dir: Directory containing the framework.
            deploy_dir: Directory to output deployment configuration.
            
        Returns:
            Path to the created deployment configuration.
        """
        config_path = os.path.join(deploy_dir, "docker_deployment.md")
        
        with open(config_path, "w") as f:
            f.write(f"""# Docker Deployment Guide

## Prerequisites

- Docker installed
- Docker Compose installed (optional)

## Building the Docker Image

```bash
docker build -t {os.path.basename(framework_dir)}:latest .
```

## Running the Docker Container

```bash
docker run -p 8000:8000 {os.path.basename(framework_dir)}:latest
```

The web interface will be available at http://localhost:8000

## Using Docker Compose

Create a `docker-compose.yml` file with the following content:

```yaml
version: '3'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
```

Then run:

```bash
docker-compose up
```
""")
        
        # Create docker-compose.yml
        compose_path = os.path.join(deploy_dir, "docker-compose.yml")
        with open(compose_path, "w") as f:
            f.write(f"""version: '3'
services:
  app:
    build: ..
    ports:
      - "8000:8000"
    volumes:
      - ../data:/app/data
""")
        
        return config_path
    
    def _create_kubernetes_deployment_config(self, framework_dir: str, deploy_dir: str) -> str:
        """
        Create Kubernetes deployment configuration.
        
        Args:
            framework_dir: Directory containing the framework.
            deploy_dir: Directory to output deployment configuration.
            
        Returns:
            Path to the created deployment configuration.
        """
        config_path = os.path.join(deploy_dir, "kubernetes_deployment.md")
        
        with open(config_path, "w") as f:
            f.write(f"""# Kubernetes Deployment Guide

## Prerequisites

- Kubernetes cluster
- kubectl installed and configured
- Docker image of the application

## Deployment Steps

1. Create a namespace:

```bash
kubectl create namespace {os.path.basename(framework_dir)}
```

2. Apply the deployment configuration:

```bash
kubectl apply -f deployment.yaml
```

3. Apply the service configuration:

```bash
kubectl apply -f service.yaml
```

4. Check the deployment status:

```bash
kubectl get pods -n {os.path.basename(framework_dir)}
```

5. Access the application:

```bash
kubectl port-forward svc/{os.path.basename(framework_dir)} 8000:8000 -n {os.path.basename(framework_dir)}
```

The web interface will be available at http://localhost:8000
""")
        
        # Create deployment.yaml
        deployment_path = os.path.join(deploy_dir, "deployment.yaml")
        with open(deployment_path, "w") as f:
            f.write(f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {os.path.basename(framework_dir)}
  namespace: {os.path.basename(framework_dir)}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {os.path.basename(framework_dir)}
  template:
    metadata:
      labels:
        app: {os.path.basename(framework_dir)}
    spec:
      containers:
      - name: {os.path.basename(framework_dir)}
        image: {os.path.basename(framework_dir)}:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
          requests:
            cpu: "0.5"
            memory: "512Mi"
""")
        
        # Create service.yaml
        service_path = os.path.join(deploy_dir, "service.yaml")
        with open(service_path, "w") as f:
            f.write(f"""apiVersion: v1
kind: Service
metadata:
  name: {os.path.basename(framework_dir)}
  namespace: {os.path.basename(framework_dir)}
spec:
  selector:
    app: {os.path.basename(framework_dir)}
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
""")
        
        return config_path
    
    def package_framework(self, framework_dir: str, package_formats: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Package the framework in multiple formats.
        
        Args:
            framework_dir: Directory containing the framework.
            package_formats: List of package formats to create.
            
        Returns:
            A dictionary mapping package formats to file paths.
        """
        logger.info(f"Packaging framework from {framework_dir}")
        
        if package_formats is None:
            package_formats = self.package_formats
        
        package_paths = {}
        
        # Create each package format
        for format_name in package_formats:
            try:
                if format_name == "zip":
                    path = self.create_zip_package(framework_dir)
                    package_paths["zip"] = path
                elif format_name == "wheel":
                    path = self.create_wheel_package(framework_dir)
                    package_paths["wheel"] = path
                elif format_name == "docker":
                    path = self.create_docker_package(framework_dir)
                    package_paths["docker"] = path
                else:
                    logger.warning(f"Unsupported package format: {format_name}")
            except Exception as e:
                logger.error(f"Error creating {format_name} package: {e}")
        
        # Generate documentation
        try:
            docs_path = self.generate_documentation(framework_dir)
            package_paths["docs"] = docs_path
        except Exception as e:
            logger.error(f"Error generating documentation: {e}")
        
        # Create deployment configurations
        try:
            local_config = self.create_deployment_config(framework_dir, "local")
            package_paths["local_config"] = local_config
            
            cloud_config = self.create_deployment_config(framework_dir, "cloud")
            package_paths["cloud_config"] = cloud_config
            
            docker_config = self.create_deployment_config(framework_dir, "docker")
            package_paths["docker_config"] = docker_config
            
            k8s_config = self.create_deployment_config(framework_dir, "kubernetes")
            package_paths["kubernetes_config"] = k8s_config
        except Exception as e:
            logger.error(f"Error creating deployment configurations: {e}")
        
        logger.info(f"Framework packaged successfully: {list(package_paths.keys())}")
        return package_paths
