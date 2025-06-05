#!/usr/bin/env python3
"""
Comprehensive dependency installation script for fAIr-utilities.

This script installs all dependencies in the correct order with proper error handling.
"""

import sys
import subprocess


def run_command(cmd, check=True, capture_output=False):
    """Run a command with proper error handling."""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=capture_output, text=True)
        return result
    except subprocess.CalledProcessError as e:
        if check:
            raise e
        return e


def install_system_packages():
    """Install system packages required for GDAL."""
    print("🔍 Installing system packages...")
    try:
        run_command("sudo apt-get update")
        run_command("sudo apt-get install -y gdal-bin libgdal-dev")
        print("✅ System packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ System packages installation failed: {e}")
        return False


def install_gdal():
    """Install GDAL Python bindings."""
    print("🔍 Installing GDAL Python bindings...")
    try:
        # Get GDAL version
        result = run_command("gdal-config --version", capture_output=True)
        gdal_version = result.stdout.strip()
        print(f"GDAL version: {gdal_version}")
        
        # Install GDAL Python bindings
        run_command(f"pip install GDAL=={gdal_version} --no-cache-dir")
        print("✅ GDAL Python bindings installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ GDAL installation failed: {e}")
        return False


def install_core_dependencies():
    """Install core Python dependencies."""
    print("🔍 Installing core dependencies...")
    
    core_deps = [
        "matplotlib",
        "segmentation-models",
        "numpy",
        "pandas",
        "shapely",
        "geopandas",
        "rasterio",
        "mercantile",
        "tqdm",
        "Pillow",
    ]
    
    failed = []
    for dep in core_deps:
        try:
            print(f"📦 Installing {dep}...")
            run_command(f"pip install {dep} --no-cache-dir")
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ {dep} installation failed")
            failed.append(dep)
    
    if failed:
        print(f"⚠️ Failed to install: {', '.join(failed)}")
        return False
    else:
        print("✅ All core dependencies installed successfully")
        return True


def install_optional_packages():
    """Install optional packages with fallback strategies."""
    print("🔍 Installing optional packages...")
    
    # Try fairpredictor
    print("📦 Installing fairpredictor...")
    fairpredictor_installed = False
    
    # Try PyPI first
    try:
        run_command("pip install fairpredictor==0.0.21")
        fairpredictor_installed = True
        print("✅ fairpredictor installed from PyPI")
    except subprocess.CalledProcessError:
        print("⚠️ fairpredictor not available on PyPI")
    
    # Try Git repositories if PyPI failed
    if not fairpredictor_installed:
        git_repos = [
            "git+https://github.com/hotosm/fairpredictor.git@main",
            "git+https://github.com/hotosm/fairpredictor.git@master",
            "git+https://github.com/kshitijrajsharma/fairpredictor.git@main",
            "git+https://github.com/kshitijrajsharma/fairpredictor.git@master",
        ]
        
        for repo in git_repos:
            try:
                run_command(f"pip install {repo}")
                fairpredictor_installed = True
                print(f"✅ fairpredictor installed from {repo}")
                break
            except subprocess.CalledProcessError:
                continue
    
    if not fairpredictor_installed:
        print("⚠️ fairpredictor not available from any source")
    
    # Try geoml-toolkits
    print("📦 Installing geoml-toolkits...")
    geoml_installed = False
    
    # Try PyPI first
    try:
        run_command("pip install geoml-toolkits")
        geoml_installed = True
        print("✅ geoml-toolkits installed from PyPI")
    except subprocess.CalledProcessError:
        print("⚠️ geoml-toolkits not available on PyPI")
    
    # Try Git repositories if PyPI failed
    if not geoml_installed:
        git_repos = [
            "git+https://github.com/hotosm/geoml-toolkits.git@main",
            "git+https://github.com/hotosm/geoml-toolkits.git@master",
            "git+https://github.com/kshitijrajsharma/geoml-toolkits.git@main",
            "git+https://github.com/kshitijrajsharma/geoml-toolkits.git@master",
        ]
        
        for repo in git_repos:
            try:
                run_command(f"pip install {repo}")
                geoml_installed = True
                print(f"✅ geoml-toolkits installed from {repo}")
                break
            except subprocess.CalledProcessError:
                continue
    
    if not geoml_installed:
        print("⚠️ geoml-toolkits not available from any source")
    
    return True  # Always return True since these are optional


def verify_installations():
    """Verify that all critical dependencies are working."""
    print("🔍 Verifying installations...")
    
    critical_imports = [
        ("osgeo.gdal", "GDAL"),
        ("matplotlib", "matplotlib"),
        ("segmentation_models", "segmentation-models"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
    ]
    
    failed = []
    for module, name in critical_imports:
        try:
            __import__(module)
            print(f"✅ {name} import successful")
        except ImportError:
            print(f"❌ {name} import failed")
            failed.append(name)
    
    if failed:
        print(f"❌ Critical dependencies failed: {', '.join(failed)}")
        return False
    else:
        print("✅ All critical dependencies verified")
        return True


def main():
    """Main installation process."""
    print("🚀 Starting comprehensive dependency installation...")
    print("=" * 60)
    
    steps = [
        ("System Packages", install_system_packages),
        ("GDAL Python Bindings", install_gdal),
        ("Core Dependencies", install_core_dependencies),
        ("Optional Packages", install_optional_packages),
        ("Verification", verify_installations),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        try:
            if not step_func():
                if step_name in ["System Packages", "GDAL Python Bindings", "Core Dependencies", "Verification"]:
                    print(f"❌ Critical step '{step_name}' failed")
                    return 1
                else:
                    print(f"⚠️ Optional step '{step_name}' had issues but continuing...")
        except Exception as e:
            print(f"❌ Step '{step_name}' failed with exception: {e}")
            if step_name in ["System Packages", "GDAL Python Bindings", "Core Dependencies", "Verification"]:
                return 1
    
    print("\n" + "=" * 60)
    print("🎉 DEPENDENCY INSTALLATION COMPLETE!")
    print("✅ fAIr-utilities is ready for installation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
