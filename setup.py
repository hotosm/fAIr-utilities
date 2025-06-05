"""
Setup configuration for hot-fair-utilities.

This setup.py provides fallback support for installations that don't use pyproject.toml.
The primary configuration is in pyproject.toml following PEP 621 standards.
"""

import os
from setuptools import find_packages, setup

# Read version from pyproject.toml or fallback
def get_version():
    """Get version from pyproject.toml or use fallback."""
    try:
        # Try tomli first (for Python < 3.11)
        try:
            import tomli
        except ImportError:
            # Fallback to tomllib for Python 3.11+
            import tomllib as tomli

        with open("pyproject.toml", "rb") as f:
            data = tomli.load(f)
            return data["project"]["version"]
    except (ImportError, FileNotFoundError, KeyError):
        return "2.0.12"  # Fallback version

# Read long description from README
def get_long_description():
    """Get long description from README.md."""
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Comprehensive AI-assisted mapping utilities with integrated fairpredictor and geoml-toolkits functionality."

# Define dependencies (should match pyproject.toml)
INSTALL_REQUIRES = [
    # Core geospatial dependencies (shared)
    "shapely>=1.8.0,<3.0.0",
    "numpy>=1.21.0,<2.0.0",
    "Pillow>=9.1.0,<11.0.0",
    "geopandas>=0.12.0,<=0.14.4",
    "pandas>=2.0.0,<=2.2.3",
    "rasterio>=1.3.0,<2.0.0",
    "mercantile>=1.2.1,<2.0.0",
    "tqdm>=4.67.0,<5.0.0",
    "rtree>=1.0.0,<2.0.0",
    "matplotlib>=3.5.0,<4.0.0",

    # Computer vision dependencies (shared)
    "opencv-python-headless>=4.8.0,<=4.10.0.84",
    "torch>=2.0.0,<=2.5.1",
    "torchvision>=0.10.0,<=0.20.1",
    "torchaudio>=2.0.0,<=2.5.1",
    "ultralytics>=8.0.0,<=8.3.26",

    # ML model dependencies (existing)
    "ramp-fair==0.1.2",
    "protobuf>=3.20.2,<5.0.0",
    "tensorflow>=2.10.0,<3.0.0",

    # Package dependencies (NEW: use actual packages when available)
    # Note: Using available versions instead of 1.0.0
    # "fairpredictor>=0.0.21",  # Use available version (uncomment when needed)
    # "geoml-toolkits>=0.0.1",  # Use available version (uncomment when needed)

    # Additional dependencies for integration layer
    "aiohttp>=3.8.0,<4.0.0",
    "pyproj>=3.0.0,<4.0.0",
    "psutil>=5.8.0,<6.0.0",
    "urllib3>=1.26.0,<3.0.0",
]

# Optional dependencies
EXTRAS_REQUIRE = {
    "dev": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
        "black>=22.0.0",
        "flake8>=5.0.0",
        "mypy>=1.0.0",
        "pre-commit>=2.20.0",
    ],
    "test": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
        "pytest-mock>=3.10.0",
        "responses>=0.22.0",
    ],
    "docs": [
        "sphinx>=5.0.0",
        "sphinx-rtd-theme>=1.2.0",
        "myst-parser>=0.18.0",
    ],
    "monitoring": [
        "psutil>=5.8.0,<6.0.0",
    ],
    "packages": [
        # Optional package dependencies (when available)
        # "fairpredictor>=1.0.0",  # Uncomment when available on PyPI
        # "geoml-toolkits>=1.0.0",  # Uncomment when available on PyPI
    ],
}

# Add 'all' extra that includes everything
EXTRAS_REQUIRE["all"] = list(set(sum(EXTRAS_REQUIRE.values(), [])))

setup(
    name="hot-fair-utilities",
    version=get_version(),
    description="Comprehensive AI-assisted mapping utilities with integrated fairpredictor and geoml-toolkits functionality",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="HOT OSM Team",
    author_email="tech@hotosm.org",
    url="https://github.com/hotosm/fAIr-utilities",
    project_urls={
        "Bug Reports": "https://github.com/hotosm/fAIr-utilities/issues",
        "Source": "https://github.com/hotosm/fAIr-utilities",
        "Documentation": "https://github.com/hotosm/fAIr-utilities/blob/main/README.md",
    },
    packages=find_packages(include=["hot_fair_utilities", "hot_fair_utilities.*"]),
    package_dir={"": "."},
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="ai mapping geospatial machine-learning computer-vision gis",
    zip_safe=False,
)
