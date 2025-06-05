#!/usr/bin/env python3
"""
Robust dependency installation script for fAIr-utilities.

This script handles all the common installation issues and provides
multiple fallback strategies for each dependency.
"""

import sys
import subprocess
import os


def run_command(cmd, check=True, capture_output=False):
    """Run a command with proper error handling."""
    try:
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, check=check, capture_output=capture_output, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        if check:
            raise e
        return e


def install_dependencies_with_fallback():
    """Install dependencies with multiple fallback strategies."""
    print("🚀 Starting robust dependency installation...")
    
    # Step 1: Upgrade pip and basic tools
    print("\n📦 Step 1: Upgrading pip and basic tools...")
    try:
        run_command("python -m pip install --upgrade pip setuptools wheel")
        print("✅ Pip and basic tools upgraded")
    except Exception as e:
        print(f"⚠️ Pip upgrade failed: {e}")
    
    # Step 2: Install GDAL with multiple strategies
    print("\n🌍 Step 2: Installing GDAL...")
    gdal_installed = False
    
    try:
        # Try to get GDAL version
        result = run_command("gdal-config --version", capture_output=True)
        gdal_version = result.stdout.strip()
        print(f"System GDAL version: {gdal_version}")
        
        # Try different GDAL installation strategies
        strategies = [
            f"pip install GDAL=={gdal_version} --no-cache-dir",
            "pip install GDAL --no-cache-dir",
            f"pip install GDAL=={gdal_version}",
            "pip install GDAL",
        ]
        
        for strategy in strategies:
            try:
                run_command(strategy)
                # Test if GDAL works
                run_command("python -c 'from osgeo import gdal; print(\"GDAL OK\")'")
                gdal_installed = True
                print("✅ GDAL installed successfully")
                break
            except Exception:
                print(f"⚠️ Strategy failed: {strategy}")
                continue
                
    except Exception as e:
        print(f"❌ GDAL installation failed: {e}")
    
    if not gdal_installed:
        print("❌ All GDAL installation strategies failed")
        return False
    
    # Step 3: Install NumPy first with TensorFlow compatibility
    print("\n📦 Step 3: Installing NumPy with TensorFlow compatibility...")

    # Detect Python version for TensorFlow compatibility
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"Python version detected: {python_version}")

    # Install NumPy first with correct version for TensorFlow compatibility
    if python_version == "3.12":
        numpy_version = "numpy>=1.26.0,<2.0.0"  # TensorFlow 2.17+ supports NumPy 2.x
        tf_version = "tensorflow>=2.17.1,<3.0.0"
    elif python_version == "3.11":
        numpy_version = "numpy>=1.22.0,<1.24.0"  # TensorFlow 2.15-2.16 requires NumPy <1.24
        tf_version = "tensorflow>=2.16.0,<3.0.0"
    else:  # Python 3.10
        numpy_version = "numpy>=1.22.0,<1.24.0"  # TensorFlow 2.15 requires NumPy <1.24
        tf_version = "tensorflow>=2.15.0,<3.0.0"

    # Install NumPy first
    try:
        print(f"Installing {numpy_version}...")
        run_command(f"pip install '{numpy_version}' --no-cache-dir")
        print(f"✅ NumPy installed with TensorFlow compatibility")
    except Exception as e:
        print(f"❌ Failed to install NumPy: {e}")
        return False

    core_deps = [
        "matplotlib>=3.5.0,<4.0.0",
        tf_version,  # TensorFlow includes Keras (tf.keras)
        "pandas>=2.0.0,<=2.2.3",
    ]
    
    for dep in core_deps:
        try:
            print(f"Installing {dep}...")
            run_command(f"pip install '{dep}' --no-cache-dir")
            print(f"✅ {dep} installed")
        except Exception as e:
            print(f"❌ Failed to install {dep}: {e}")
            # Try without version constraints
            dep_name = dep.split(">=")[0].split("==")[0].split("<")[0]
            try:
                run_command(f"pip install {dep_name} --no-cache-dir")
                print(f"✅ {dep_name} installed (fallback)")
            except Exception:
                print(f"❌ Complete failure for {dep_name}")
    
    # Step 4: Install computer vision models after TensorFlow
    print("\n🤖 Step 4: Installing computer vision models...")

    # Install segmentation-models
    try:
        run_command("pip install segmentation-models --no-cache-dir")
        print("✅ segmentation-models installed")
    except Exception as e:
        print(f"❌ segmentation-models installation failed: {e}")

    # Install efficientnet with compatibility handling
    try:
        print("Installing efficientnet with compatibility...")
        # Try different efficientnet packages with specific versions
        efficientnet_packages = [
            "efficientnet>=1.1.0,<2.0.0",  # Classic with specific version range
            "efficientnet==1.1.1",  # Specific known working version
            "keras-efficientnet-v2",  # Modern alternative
        ]

        efficientnet_installed = False
        for package in efficientnet_packages:
            try:
                run_command(f"pip install '{package}' --no-cache-dir")
                print(f"✅ {package} installed successfully")

                # Test if it works
                try:
                    run_command([sys.executable, "-c", "import efficientnet; efficientnet.init_keras_custom_objects()"])
                    print(f"✅ {package} working correctly")
                    efficientnet_installed = True
                    break
                except Exception as test_error:
                    print(f"⚠️ {package} installed but not working: {test_error}")
                    if "generic_utils" in str(test_error):
                        print("   Applying compatibility patch...")
                        try:
                            run_command([sys.executable, "fix_efficientnet_compatibility.py"])
                            print("✅ Compatibility patch applied")
                            efficientnet_installed = True
                            break
                        except Exception:
                            print("❌ Compatibility patch failed")
                            continue

            except Exception:
                print(f"⚠️ Failed to install {package}")
                continue

        if not efficientnet_installed:
            print("⚠️ No efficientnet package could be installed or made to work")
            print("   Consider using tf.keras.applications.EfficientNetB0 instead")

    except Exception as e:
        print(f"⚠️ efficientnet installation failed: {e}")
    
    # Step 5: Install remaining geospatial dependencies
    print("\n🌍 Step 5: Installing geospatial dependencies...")
    geo_deps = [
        "shapely>=1.8.0,<3.0.0",
        "geopandas>=0.12.0,<=0.14.4",
        "rasterio>=1.3.0,<2.0.0",
        "mercantile>=1.2.1,<2.0.0",
        "tqdm>=4.67.0,<5.0.0",
        "Pillow>=9.1.0,<11.0.0",
    ]
    
    for dep in geo_deps:
        try:
            print(f"Installing {dep}...")
            run_command(f"pip install '{dep}' --no-cache-dir")
            print(f"✅ {dep} installed")
        except Exception as e:
            print(f"⚠️ Failed to install {dep}: {e}")
    
    return True


def verify_critical_imports():
    """Verify that critical dependencies can be imported."""
    print("\n🔍 Verifying critical imports...")
    
    critical_imports = [
        ("osgeo.gdal", "GDAL"),
        ("matplotlib", "matplotlib"),
        ("tensorflow", "tensorflow"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
    ]
    
    failed = []
    for module, name in critical_imports:
        try:
            __import__(module)
            print(f"✅ {name} import successful")
        except ImportError as e:
            print(f"❌ {name} import failed: {e}")
            failed.append(name)
    
    if failed:
        print(f"\n❌ Critical imports failed: {', '.join(failed)}")
        return False
    else:
        print("\n✅ All critical imports successful")
        return True


def install_optional_packages():
    """Install optional packages with proper error handling."""
    print("\n📦 Installing optional packages...")
    
    # Try fairpredictor
    print("🔍 Installing fairpredictor...")
    fairpredictor_sources = [
        "fairpredictor==0.0.21",
        "fairpredictor",
        "git+https://github.com/hotosm/fairpredictor.git@master",
        "git+https://github.com/hotosm/fairpredictor.git@main",
    ]
    
    for source in fairpredictor_sources:
        try:
            run_command(f"pip install {source}")
            print("✅ fairpredictor installed")
            break
        except Exception:
            print(f"⚠️ Failed: {source}")
            continue
    else:
        print("⚠️ fairpredictor not available from any source")
    
    # Try geoml-toolkits
    print("🔍 Installing geoml-toolkits...")
    geoml_sources = [
        "geoml-toolkits",
        "git+https://github.com/hotosm/geoml-toolkits.git@master",
        "git+https://github.com/hotosm/geoml-toolkits.git@main",
    ]
    
    for source in geoml_sources:
        try:
            run_command(f"pip install {source}")
            print("✅ geoml-toolkits installed")
            break
        except Exception:
            print(f"⚠️ Failed: {source}")
            continue
    else:
        print("⚠️ geoml-toolkits not available from any source")
    
    return True


def main():
    """Main installation process."""
    print("🚀 ROBUST DEPENDENCY INSTALLATION")
    print("=" * 50)
    
    try:
        # Install dependencies
        if not install_dependencies_with_fallback():
            print("❌ Critical dependency installation failed")
            return 1
        
        # Verify critical imports
        if not verify_critical_imports():
            print("❌ Critical import verification failed")
            return 1
        
        # Install optional packages (always succeeds)
        install_optional_packages()
        
        print("\n" + "=" * 50)
        print("🎉 DEPENDENCY INSTALLATION COMPLETE!")
        print("✅ Ready for package installation")
        return 0
        
    except Exception as e:
        print(f"\n❌ Installation failed with exception: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
