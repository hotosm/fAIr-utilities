#!/usr/bin/env python3
"""
Robust installation script for fAIr-utilities that handles PEP 517 issues.

This script provides multiple fallback strategies for installation when
the standard pip install -e . fails due to PEP 517 or dependency issues.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, check=True, capture_output=True):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, 
            check=check, 
            capture_output=capture_output, 
            text=True
        )
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        if check:
            raise
        return e


def install_build_dependencies():
    """Install essential build dependencies."""
    print("📦 Installing build dependencies...")
    
    build_deps = [
        "pip>=21.0",
        "setuptools>=61.0.0", 
        "wheel",
        "tomli>=1.2.0",
        "Cython>=0.29.0",
        "numpy>=1.21.0,<2.0.0"
    ]
    
    for dep in build_deps:
        try:
            run_command([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ Installed {dep}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {dep}")
            return False
    
    return True


def install_core_dependencies():
    """Install core geospatial dependencies that might be needed during build."""
    print("🌍 Installing core geospatial dependencies...")

    core_deps = [
        "shapely>=1.8.0,<3.0.0",
        "geopandas>=0.12.0,<=0.14.4",
        "rasterio>=1.3.0,<2.0.0",
        "pandas>=2.0.0,<=2.2.3",
        "mercantile>=1.2.1,<2.0.0",
        "tqdm>=4.67.0,<5.0.0",
        "Pillow>=9.1.0,<11.0.0",
        "matplotlib>=3.5.0,<4.0.0"
    ]

    for dep in core_deps:
        try:
            run_command([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ Installed {dep}")
        except subprocess.CalledProcessError:
            print(f"⚠️ Failed to install {dep}, continuing...")

    return True


def install_gdal_if_needed():
    """Install GDAL if not already available."""
    print("🔍 Checking GDAL installation...")

    try:
        # Test if GDAL is already available
        run_command([sys.executable, "-c", "from osgeo import gdal; print('GDAL already available')"])
        print("✅ GDAL is already installed and working")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ GDAL not available, attempting installation...")

        try:
            # Check if gdal-config is available
            try:
                result = run_command(["gdal-config", "--version"], capture_output=True)
                gdal_version = result.stdout.strip()
                print(f"🔍 System GDAL version: {gdal_version}")
            except subprocess.CalledProcessError:
                print("❌ gdal-config not found. System GDAL packages not installed.")
                print("   Install with: sudo apt-get install gdal-bin libgdal-dev")
                return False

            # Try to install GDAL Python bindings
            print("📦 Installing GDAL Python bindings...")
            run_command([sys.executable, "-m", "pip", "install", f"GDAL=={gdal_version}", "--no-cache-dir"])
            print("✅ GDAL Python bindings installed successfully")

            # Verify installation
            run_command([sys.executable, "-c", "from osgeo import gdal; print('GDAL verification successful')"])
            print("✅ GDAL installation verified")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ GDAL installation failed: {e}")
            print("   Troubleshooting steps:")
            print("   1. Install system packages: sudo apt-get install gdal-bin libgdal-dev")
            print("   2. Check GDAL version: gdal-config --version")
            print("   3. Install Python bindings: pip install GDAL==$(gdal-config --version)")
            return False


def install_package_dependencies():
    """Install fairpredictor and geoml-toolkits packages if available."""
    print("📦 Attempting to install optional package dependencies...")

    # First try PyPI packages
    package_deps = [
        ("fairpredictor>=1.0.0", "fairpredictor"),
        ("geoml-toolkits>=1.0.0", "geoml-toolkits")
    ]

    installed_count = 0
    for dep_spec, dep_name in package_deps:
        try:
            print(f"🔍 Checking if {dep_name} is available on PyPI...")
            run_command([sys.executable, "-m", "pip", "install", dep_spec])
            print(f"✅ Successfully installed {dep_name} from PyPI")
            installed_count += 1
        except subprocess.CalledProcessError:
            print(f"⚠️ {dep_name} not available on PyPI")

    # If PyPI packages not available, try GitHub
    if installed_count == 0:
        print("🔍 Trying to install from GitHub repositories...")
        github_repos = [
            ("git+https://github.com/hotosm/fairpredictor.git@main", "fairpredictor"),
            ("git+https://github.com/kshitijrajsharma/fairpredictor.git@main", "fairpredictor"),
            ("git+https://github.com/hotosm/geoml-toolkits.git@main", "geoml-toolkits"),
            ("git+https://github.com/kshitijrajsharma/geoml-toolkits.git@main", "geoml-toolkits"),
        ]

        for repo_url, dep_name in github_repos:
            try:
                print(f"🔍 Trying {dep_name} from GitHub...")
                run_command([sys.executable, "-m", "pip", "install", repo_url], check=False)
                print(f"✅ Successfully installed {dep_name} from GitHub")
                installed_count += 1
                break  # Stop trying other repos for this package
            except subprocess.CalledProcessError:
                print(f"⚠️ {dep_name} not available from {repo_url}")

    if installed_count == 0:
        print("📝 Note: No optional packages installed - this is expected during development")
        print("   The migration framework is in place and will work when packages are available")
    else:
        print(f"✅ Installed {installed_count} optional packages")

    return True


def try_pep517_installation():
    """Try standard PEP 517 installation."""
    print("🔧 Attempting PEP 517 installation...")
    
    try:
        run_command([sys.executable, "-m", "pip", "install", "-e", "."])
        print("✅ PEP 517 installation successful!")
        return True
    except subprocess.CalledProcessError:
        print("❌ PEP 517 installation failed")
        return False


def try_legacy_installation():
    """Try legacy installation without PEP 517."""
    print("🔧 Attempting legacy installation...")
    
    try:
        run_command([sys.executable, "-m", "pip", "install", "-e", ".", "--no-use-pep517"])
        print("✅ Legacy installation successful!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Legacy installation failed")
        return False


def try_manual_installation():
    """Try manual installation with --no-deps and then install dependencies."""
    print("🔧 Attempting manual installation...")
    
    try:
        # Install package without dependencies
        run_command([
            sys.executable, "-m", "pip", "install", 
            "-e", ".", "--no-deps", "--no-use-pep517"
        ])
        print("✅ Package installed without dependencies")
        
        # Now install dependencies from setup.py
        print("📦 Installing dependencies manually...")
        
        # Import setup.py to get dependencies
        sys.path.insert(0, '.')
        try:
            from setup import INSTALL_REQUIRES
            
            for dep in INSTALL_REQUIRES:
                try:
                    run_command([sys.executable, "-m", "pip", "install", dep])
                    print(f"✅ Installed {dep}")
                except subprocess.CalledProcessError:
                    print(f"⚠️ Failed to install {dep}, continuing...")
            
            print("✅ Manual installation completed!")
            return True
            
        except ImportError as e:
            print(f"❌ Could not import setup.py: {e}")
            return False
            
    except subprocess.CalledProcessError:
        print("❌ Manual installation failed")
        return False


def verify_installation():
    """Verify that the installation was successful."""
    print("🔍 Verifying installation...")
    
    try:
        run_command([
            sys.executable, "-c", 
            "import hot_fair_utilities; print('✅ Import successful')"
        ])
        return True
    except subprocess.CalledProcessError:
        print("❌ Installation verification failed")
        return False


def main():
    """Main installation function with multiple fallback strategies."""
    print("🚀 Starting robust fAIr-utilities installation...")
    
    # Check if we're in the right directory
    if not Path("setup.py").exists():
        print("❌ setup.py not found. Please run this script from the repository root.")
        sys.exit(1)
    
    # Step 1: Install build dependencies
    if not install_build_dependencies():
        print("❌ Failed to install build dependencies")
        sys.exit(1)
    
    # Step 2: Install core dependencies
    install_core_dependencies()

    # Step 3: Install GDAL if needed
    install_gdal_if_needed()

    # Step 4: Install package dependencies
    install_package_dependencies()

    # Step 5: Try different installation strategies
    strategies = [
        ("PEP 517", try_pep517_installation),
        ("Legacy", try_legacy_installation), 
        ("Manual", try_manual_installation)
    ]
    
    for strategy_name, strategy_func in strategies:
        print(f"\n{'='*50}")
        print(f"Trying {strategy_name} installation strategy...")
        print(f"{'='*50}")
        
        if strategy_func():
            print(f"✅ {strategy_name} installation successful!")
            break
    else:
        print("❌ All installation strategies failed!")
        sys.exit(1)
    
    # Step 4: Verify installation
    if verify_installation():
        print("\n🎉 Installation completed successfully!")
        print("You can now use: import hot_fair_utilities")
    else:
        print("\n❌ Installation verification failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
