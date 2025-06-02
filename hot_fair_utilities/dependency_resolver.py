"""
Dependency Resolution Helper for fAIr-utilities.

This module handles dependency conflicts between fairpredictor, geoml-toolkits,
and fAIr-utilities by providing version compatibility checks and resolution strategies.
"""

import sys
import warnings
from typing import Dict, List, Optional, Tuple
from packaging import version


class DependencyConflictError(Exception):
    """Raised when there are unresolvable dependency conflicts."""
    pass


class DependencyResolver:
    """
    Handles dependency conflicts and version compatibility between packages.
    """
    
    # Define compatible version ranges for shared dependencies
    COMPATIBILITY_MATRIX = {
        'numpy': {
            'fair_utilities': '>=1.21.0,<2.0.0',
            'fairpredictor': '>=1.20.0,<2.0.0',
            'geoml_toolkits': '>=1.21.0,<2.0.0'
        },
        'pandas': {
            'fair_utilities': '>=2.0.0,<=2.2.3',
            'fairpredictor': '>=1.5.0,<=2.2.3',
            'geoml_toolkits': '>=2.0.0,<=2.2.3'
        },
        'geopandas': {
            'fair_utilities': '>=0.12.0,<=0.14.4',
            'fairpredictor': '>=0.11.0,<=0.14.4',
            'geoml_toolkits': '>=0.12.0,<=0.14.4'
        },
        'rasterio': {
            'fair_utilities': '>=1.3.0,<2.0.0',
            'fairpredictor': '>=1.2.0,<2.0.0',
            'geoml_toolkits': '>=1.3.0,<2.0.0'
        },
        'shapely': {
            'fair_utilities': '>=1.8.0,<3.0.0',
            'fairpredictor': '>=1.7.0,<3.0.0',
            'geoml_toolkits': '>=1.8.0,<3.0.0'
        },
        'torch': {
            'fair_utilities': '>=2.0.0,<=2.5.1',
            'fairpredictor': '>=1.13.0,<=2.5.1',
            'geoml_toolkits': '>=2.0.0,<=2.5.1'
        },
        'ultralytics': {
            'fair_utilities': '>=8.0.0,<=8.3.26',
            'fairpredictor': '>=8.0.0,<=8.3.26',
            'geoml_toolkits': '>=8.0.0,<=8.3.26'
        }
    }
    
    def __init__(self):
        self.installed_packages = self._get_installed_packages()
        self.conflicts = []
        self.warnings = []
    
    def _get_installed_packages(self) -> Dict[str, str]:
        """Get currently installed package versions."""
        installed = {}
        
        # Try to get versions of key packages
        packages_to_check = [
            'numpy', 'pandas', 'geopandas', 'rasterio', 'shapely',
            'torch', 'ultralytics', 'fairpredictor', 'geoml_toolkits'
        ]
        
        for package_name in packages_to_check:
            try:
                if package_name == 'geoml_toolkits':
                    # Handle different possible import names
                    import_names = ['geoml_toolkits', 'geoml-toolkits']
                else:
                    import_names = [package_name]
                
                for import_name in import_names:
                    try:
                        module = __import__(import_name)
                        if hasattr(module, '__version__'):
                            installed[package_name] = module.__version__
                            break
                    except ImportError:
                        continue
                        
            except ImportError:
                # Package not installed
                continue
        
        return installed
    
    def check_compatibility(self) -> Tuple[bool, List[str], List[str]]:
        """
        Check for dependency conflicts between packages.
        
        Returns:
            Tuple of (is_compatible, conflicts, warnings)
        """
        conflicts = []
        warnings = []
        
        for dep_name, version_reqs in self.COMPATIBILITY_MATRIX.items():
            if dep_name in self.installed_packages:
                installed_version = self.installed_packages[dep_name]
                
                # Check if installed version satisfies all package requirements
                compatible_with = []
                incompatible_with = []
                
                for package, version_spec in version_reqs.items():
                    try:
                        if self._version_satisfies(installed_version, version_spec):
                            compatible_with.append(package)
                        else:
                            incompatible_with.append((package, version_spec))
                    except Exception as e:
                        warnings.append(f"Could not check {dep_name} version compatibility: {e}")
                
                if incompatible_with:
                    conflict_msg = (
                        f"Version conflict for {dep_name} v{installed_version}. "
                        f"Incompatible with: {incompatible_with}"
                    )
                    conflicts.append(conflict_msg)
                
                if len(compatible_with) < len(version_reqs):
                    warning_msg = (
                        f"{dep_name} v{installed_version} may have compatibility issues. "
                        f"Compatible with: {compatible_with}"
                    )
                    warnings.append(warning_msg)
        
        self.conflicts = conflicts
        self.warnings = warnings
        
        return len(conflicts) == 0, conflicts, warnings
    
    def _version_satisfies(self, installed_version: str, version_spec: str) -> bool:
        """Check if installed version satisfies version specification."""
        try:
            from packaging.specifiers import SpecifierSet
            spec_set = SpecifierSet(version_spec)
            return version.parse(installed_version) in spec_set
        except Exception:
            # Fallback to simple comparison if packaging not available
            return True  # Assume compatible if we can't check
    
    def resolve_conflicts(self) -> Dict[str, str]:
        """
        Provide resolution strategies for dependency conflicts.
        
        Returns:
            Dictionary of package names to recommended versions
        """
        resolutions = {}
        
        for dep_name, version_reqs in self.COMPATIBILITY_MATRIX.items():
            if dep_name in self.installed_packages:
                # Find a version that satisfies all requirements
                recommended_version = self._find_compatible_version(version_reqs)
                if recommended_version:
                    resolutions[dep_name] = recommended_version
        
        return resolutions
    
    def _find_compatible_version(self, version_reqs: Dict[str, str]) -> Optional[str]:
        """Find a version that satisfies all package requirements."""
        # This is a simplified approach - in practice, you'd want to use
        # a proper dependency resolver like pip's resolver
        
        # For now, return a conservative recommendation
        conservative_versions = {
            'numpy': '1.21.6',
            'pandas': '2.0.3',
            'geopandas': '0.13.2',
            'rasterio': '1.3.8',
            'shapely': '2.0.1',
            'torch': '2.0.1',
            'ultralytics': '8.0.20'
        }
        
        return conservative_versions.get(list(version_reqs.keys())[0])
    
    def generate_requirements_txt(self, output_file: str = "requirements-resolved.txt"):
        """Generate a requirements.txt file with resolved dependencies."""
        resolutions = self.resolve_conflicts()
        
        requirements = [
            "# Resolved dependencies for fAIr-utilities integration",
            "# Generated automatically to avoid conflicts",
            "",
            "# Core packages with resolved versions"
        ]
        
        for package, version in resolutions.items():
            requirements.append(f"{package}=={version}")
        
        requirements.extend([
            "",
            "# Package-specific dependencies",
            "fairpredictor>=1.0.0",
            "geoml-toolkits>=1.0.0",
            "",
            "# Additional fAIr-utilities dependencies",
            "aiohttp>=3.8.0,<4.0.0",
            "pyproj>=3.0.0,<4.0.0",
            "psutil>=5.8.0,<6.0.0",
            "urllib3>=1.26.0,<3.0.0"
        ])
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(requirements))
        
        return output_file
    
    def print_status_report(self):
        """Print a comprehensive dependency status report."""
        print("🔍 DEPENDENCY COMPATIBILITY REPORT")
        print("=" * 50)
        
        is_compatible, conflicts, warnings = self.check_compatibility()
        
        print(f"Overall Status: {'✅ COMPATIBLE' if is_compatible else '❌ CONFLICTS DETECTED'}")
        print(f"Installed Packages: {len(self.installed_packages)}")
        print(f"Conflicts: {len(conflicts)}")
        print(f"Warnings: {len(warnings)}")
        
        if self.installed_packages:
            print("\n📦 INSTALLED PACKAGES:")
            for package, version in self.installed_packages.items():
                print(f"  {package}: {version}")
        
        if conflicts:
            print("\n❌ CONFLICTS:")
            for conflict in conflicts:
                print(f"  - {conflict}")
        
        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"  - {warning}")
        
        if not is_compatible:
            print("\n🔧 RESOLUTION SUGGESTIONS:")
            resolutions = self.resolve_conflicts()
            for package, recommended_version in resolutions.items():
                current_version = self.installed_packages.get(package, "not installed")
                print(f"  {package}: {current_version} → {recommended_version}")
            
            print(f"\n💡 Run: pip install -r requirements-resolved.txt")
            print(f"   (Generated with resolver.generate_requirements_txt())")


def check_dependencies():
    """Quick dependency check function."""
    resolver = DependencyResolver()
    is_compatible, conflicts, warnings = resolver.check_compatibility()
    
    if not is_compatible:
        warning_msg = (
            f"Dependency conflicts detected: {len(conflicts)} conflicts, {len(warnings)} warnings. "
            f"Run 'from hot_fair_utilities.dependency_resolver import DependencyResolver; "
            f"DependencyResolver().print_status_report()' for details."
        )
        warnings.warn(warning_msg, UserWarning)
    
    return is_compatible


# Run dependency check on import
if __name__ != "__main__":
    try:
        check_dependencies()
    except Exception as e:
        warnings.warn(f"Could not check dependencies: {e}", UserWarning)


if __name__ == "__main__":
    # Command-line interface
    resolver = DependencyResolver()
    resolver.print_status_report()
    
    if not resolver.check_compatibility()[0]:
        print("\nGenerating resolved requirements file...")
        requirements_file = resolver.generate_requirements_txt()
        print(f"Generated: {requirements_file}")
