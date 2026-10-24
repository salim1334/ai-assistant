# Installation Guide

## System Requirements

The Enhanced BDFG Framework requires the following:

- Python 3.8 or higher
- Pip package manager
- Sufficient disk space for dependencies (approximately 500MB)
- Recommended: 8GB+ RAM for larger datasets

## Installation Methods

### Using Pip (Recommended)

The simplest way to install the Enhanced BDFG Framework is using pip:

```bash
pip install enhanced-bdfg
```

For a specific version:

```bash
pip install enhanced-bdfg==1.0.0
```

### From Source

To install from source:

1. Clone the repository:
   ```bash
   git clone https://github.com/bdfgframework/enhanced-bdfg.git
   cd enhanced-bdfg
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

### Using Requirements File

You can also install the dependencies using the requirements file:

```bash
pip install -r requirements.txt
```

## Optional Dependencies

For development and testing, install the development dependencies:

```bash
pip install enhanced-bdfg[dev]
```

## Verifying Installation

To verify that the installation was successful, run:

```python
import enhanced_bdfg
print(enhanced_bdfg.__version__)
```

This should print the version number of the installed package.

## Troubleshooting

If you encounter issues during installation:

1. Ensure you have the latest version of pip:
   ```bash
   pip install --upgrade pip
   ```

2. Check for conflicting dependencies:
   ```bash
   pip check
   ```

3. Try installing in a virtual environment:
   ```bash
   python -m venv bdfg_env
   source bdfg_env/bin/activate  # On Windows: bdfg_env\Scripts\activate
   pip install enhanced-bdfg
   ```

For more detailed troubleshooting, see the [Troubleshooting](troubleshooting.md) guide.
