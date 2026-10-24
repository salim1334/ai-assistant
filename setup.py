"""
Enhanced BDFG Framework - Setup Script
"""

from setuptools import setup, find_packages

setup(
    name="enhanced_bdfg",
    version="1.2.0",
    author="BDFG Framework Team",
    author_email="info@bdfgframework.com",
    description="Business Development Framework Generator — personalized, learning assistants",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bdfgframework/enhanced-bdfg",
    packages=find_packages(),
    include_package_data=True,
    package_data={"enhanced_bdfg": ["ui/static/*"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.110.0",
        "uvicorn>=0.27.0",
        "httpx>=0.27.0",
        "pydantic>=2.0.0",
        "psutil>=5.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.5b2",
            "flake8>=3.9.0",
            "mypy>=0.812",
        ],
        "analytics": [
            "numpy>=1.20.0",
            "pandas>=1.3.0",
            "matplotlib>=3.4.0",
            "scikit-learn>=1.0.0",
            "nltk>=3.6.0",
            "spacy>=3.0.0",
            "gensim>=4.0.0",
            "statsmodels>=0.13.0",
            "scipy>=1.7.0",
        ],
        "workspace": [
            "google-api-python-client>=2.0.0",
            "google-auth-httplib2>=0.1.0",
            "google-auth-oauthlib>=0.5.0",
        ],
        "gui": [
            "pandas>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bdfg=enhanced_bdfg.cli:main",
        ],
    },
)
