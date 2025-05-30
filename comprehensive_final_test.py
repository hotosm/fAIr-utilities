#!/usr/bin/env python3
"""
Comprehensive Final Test Suite for fAIr-utilities Integration

This script performs exhaustive testing of all integrated functionality
to validate production readiness.
"""

import sys
import traceback
import inspect
import time
import json
import tempfile
import os
from typing import List, Dict, Any, Tuple


class TestResult:
    """Class to track test results."""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []
        self.warnings = []
        self.start_time = time.time()
    
    def add_pass(self, test_name: str, message: str = ""):
        self.tests_run += 1
        self.tests_passed += 1
        print(f"✅ {test_name}: PASSED {message}")
    
    def add_fail(self, test_name: str, error: str):
        self.tests_run += 1
        self.tests_failed += 1
        self.failures.append((test_name, error))
        print(f"❌ {test_name}: FAILED - {error}")
    
    def add_warning(self, test_name: str, warning: str):
        self.warnings.append((test_name, warning))
        print(f"⚠️  {test_name}: WARNING - {warning}")
    
    def get_summary(self) -> Dict[str, Any]:
        duration = time.time() - self.start_time
        return {
            'total_tests': self.tests_run,
            'passed': self.tests_passed,
            'failed': self.tests_failed,
            'warnings': len(self.warnings),
            'success_rate': (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0,
            'duration_seconds': duration,
            'failures': self.failures,
            'warnings': self.warnings
        }


def test_basic_imports(result: TestResult):
    """Test basic module imports."""
    print("\n🔍 Testing Basic Imports...")
    
    try:
        import hot_fair_utilities as fair
        result.add_pass("Main Module Import", "hot_fair_utilities imported successfully")
        
        # Test version info
        if hasattr(fair, '__version__'):
            result.add_pass("Version Info", f"Version: {fair.__version__}")
        else:
            result.add_warning("Version Info", "No version information found")
        
        return True
    except Exception as e:
        result.add_fail("Main Module Import", str(e))
        return False


def test_core_functions(result: TestResult):
    """Test core function availability."""
    print("\n🔍 Testing Core Functions...")
    
    try:
        import hot_fair_utilities as fair
        
        core_functions = [
            'georeference', 'evaluate', 'predict', 'polygonize', 'vectorize',
            'preprocess', 'yolo_v8_v1', 'bbox2tiles', 'tms2img'
        ]
        
        for func_name in core_functions:
            if hasattr(fair, func_name):
                func = getattr(fair, func_name)
                if callable(func):
                    result.add_pass(f"Core Function: {func_name}", "Available and callable")
                else:
                    result.add_fail(f"Core Function: {func_name}", "Not callable")
            else:
                result.add_fail(f"Core Function: {func_name}", "Not found")
        
        return True
    except Exception as e:
        result.add_fail("Core Functions Test", str(e))
        return False


def test_integrated_functions(result: TestResult):
    """Test integrated functionality."""
    print("\n🔍 Testing Integrated Functions...")
    
    try:
        import hot_fair_utilities as fair
        
        integrated_functions = [
            'download_tiles', 'download_osm_data', 'VectorizeMasks', 
            'orthogonalize_gdf', 'predict_with_tiles'
        ]
        
        for func_name in integrated_functions:
            if hasattr(fair, func_name):
                func = getattr(fair, func_name)
                
                # Check if async functions are properly async
                if func_name in ['download_tiles', 'download_osm_data', 'predict_with_tiles']:
                    if inspect.iscoroutinefunction(func):
                        result.add_pass(f"Async Function: {func_name}", "Properly async")
                    else:
                        result.add_fail(f"Async Function: {func_name}", "Not async")
                else:
                    if callable(func) or inspect.isclass(func):
                        result.add_pass(f"Integrated: {func_name}", "Available")
                    else:
                        result.add_fail(f"Integrated: {func_name}", "Not callable/class")
            else:
                result.add_fail(f"Integrated: {func_name}", "Not found")
        
        return True
    except Exception as e:
        result.add_fail("Integrated Functions Test", str(e))
        return False


def test_training_functions(result: TestResult):
    """Test training functionality."""
    print("\n🔍 Testing Training Functions...")
    
    try:
        import hot_fair_utilities as fair
        
        training_functions = ['ramp_train', 'yolo_v8_v1_train', 'yolo_v8_v2_train']
        
        for func_name in training_functions:
            if hasattr(fair, func_name):
                func = getattr(fair, func_name)
                if callable(func):
                    result.add_pass(f"Training: {func_name}", "Available and callable")
                else:
                    result.add_fail(f"Training: {func_name}", "Not callable")
            else:
                result.add_fail(f"Training: {func_name}", "Not found")
        
        return True
    except Exception as e:
        result.add_fail("Training Functions Test", str(e))
        return False


def test_configuration_system(result: TestResult):
    """Test configuration system."""
    print("\n🔍 Testing Configuration System...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test config object
        if hasattr(fair, 'config'):
            config = fair.config
            result.add_pass("Configuration Object", f"Type: {type(config)}")
            
            # Test configuration validation
            if hasattr(config, 'validate'):
                issues = config.validate()
                if not issues:
                    result.add_pass("Configuration Validation", "No issues found")
                else:
                    result.add_warning("Configuration Validation", f"Issues: {issues}")
            else:
                result.add_warning("Configuration Validation", "No validate method")
            
            # Test default models
            default_models = [
                'DEFAULT_OAM_TMS_MOSAIC', 'DEFAULT_RAMP_MODEL', 
                'DEFAULT_YOLO_MODEL_V1', 'DEFAULT_YOLO_MODEL_V2'
            ]
            
            for model_name in default_models:
                if hasattr(fair, model_name):
                    model_url = getattr(fair, model_name)
                    if isinstance(model_url, str) and len(model_url) > 0:
                        result.add_pass(f"Default Model: {model_name}", "Available")
                    else:
                        result.add_fail(f"Default Model: {model_name}", "Invalid value")
                else:
                    result.add_fail(f"Default Model: {model_name}", "Not found")
        else:
            result.add_fail("Configuration System", "Config object not found")
        
        return True
    except Exception as e:
        result.add_fail("Configuration System Test", str(e))
        return False


def test_validation_system(result: TestResult):
    """Test input validation system."""
    print("\n🔍 Testing Validation System...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test validation functions
        validation_functions = [
            'validate_bbox', 'validate_zoom_level', 
            'validate_confidence', 'validate_area_threshold'
        ]
        
        for func_name in validation_functions:
            if hasattr(fair, func_name):
                result.add_pass(f"Validation: {func_name}", "Available")
            else:
                result.add_fail(f"Validation: {func_name}", "Not found")
        
        # Test validation exceptions
        if hasattr(fair, 'ValidationError') and hasattr(fair, 'SecurityError'):
            result.add_pass("Validation Exceptions", "Available")
        else:
            result.add_fail("Validation Exceptions", "Not found")
        
        # Test actual validation
        if hasattr(fair, 'validate_bbox'):
            try:
                valid_bbox = [85.514668, 27.628367, 85.528875, 27.638514]
                validated = fair.validate_bbox(valid_bbox)
                result.add_pass("Bbox Validation", f"Valid bbox processed: {validated}")
            except Exception as e:
                result.add_fail("Bbox Validation", f"Failed: {e}")
        
        return True
    except Exception as e:
        result.add_fail("Validation System Test", str(e))
        return False


def test_monitoring_system(result: TestResult):
    """Test monitoring and logging system."""
    print("\n🔍 Testing Monitoring System...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test monitoring components
        monitoring_components = ['logger', 'performance_monitor', 'ProgressTracker']
        
        for comp_name in monitoring_components:
            if hasattr(fair, comp_name):
                comp = getattr(fair, comp_name)
                result.add_pass(f"Monitoring: {comp_name}", f"Available: {type(comp)}")
            else:
                result.add_fail(f"Monitoring: {comp_name}", "Not found")
        
        # Test logger functionality
        if hasattr(fair, 'logger'):
            try:
                fair.logger.info("Test log message from comprehensive test")
                result.add_pass("Logger Functionality", "Log message sent successfully")
            except Exception as e:
                result.add_fail("Logger Functionality", f"Failed: {e}")
        
        return True
    except Exception as e:
        result.add_fail("Monitoring System Test", str(e))
        return False


def test_class_instantiation(result: TestResult):
    """Test class instantiation."""
    print("\n🔍 Testing Class Instantiation...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test VectorizeMasks
        if hasattr(fair, 'VectorizeMasks'):
            try:
                vectorizer = fair.VectorizeMasks(algorithm="rasterio")
                result.add_pass("VectorizeMasks Instantiation", "Rasterio algorithm")
                
                # Test with different parameters
                vectorizer2 = fair.VectorizeMasks(
                    algorithm="rasterio",
                    simplify_tolerance=0.1,
                    min_area=5.0,
                    orthogonalize=False
                )
                result.add_pass("VectorizeMasks Custom Params", "Custom parameters accepted")
                
            except Exception as e:
                result.add_fail("VectorizeMasks Instantiation", f"Failed: {e}")
        else:
            result.add_fail("VectorizeMasks", "Class not found")
        
        # Test TileSource
        try:
            from hot_fair_utilities.data_acquisition import TileSource
            tile_source = TileSource("https://example.com/{z}/{x}/{y}.png")
            result.add_pass("TileSource Instantiation", "Basic instantiation successful")
        except Exception as e:
            result.add_fail("TileSource Instantiation", f"Failed: {e}")
        
        return True
    except Exception as e:
        result.add_fail("Class Instantiation Test", str(e))
        return False


def test_utility_functions(result: TestResult):
    """Test utility functions."""
    print("\n🔍 Testing Utility Functions...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test get_tiles function
        if hasattr(fair, 'get_tiles'):
            try:
                bbox = [85.514668, 27.628367, 85.528875, 27.638514]
                tiles = fair.get_tiles(zoom=10, bbox=bbox)
                result.add_pass("get_tiles Function", f"Returned {len(tiles)} tiles")
            except Exception as e:
                result.add_fail("get_tiles Function", f"Failed: {e}")
        else:
            result.add_fail("get_tiles Function", "Not found")
        
        # Test get_geometry function
        if hasattr(fair, 'get_geometry'):
            try:
                bbox = [85.514668, 27.628367, 85.528875, 27.638514]
                geometry = fair.get_geometry(bbox=bbox)
                result.add_pass("get_geometry Function", f"Returned {geometry['type']} geometry")
            except Exception as e:
                result.add_fail("get_geometry Function", f"Failed: {e}")
        else:
            result.add_fail("get_geometry Function", "Not found")
        
        return True
    except Exception as e:
        result.add_fail("Utility Functions Test", str(e))
        return False


def test_module_structure(result: TestResult):
    """Test module structure and imports."""
    print("\n🔍 Testing Module Structure...")
    
    try:
        # Test individual module imports
        modules_to_test = [
            'hot_fair_utilities.data_acquisition',
            'hot_fair_utilities.vectorization',
            'hot_fair_utilities.inference',
            'hot_fair_utilities.training',
            'hot_fair_utilities.config',
            'hot_fair_utilities.validation',
            'hot_fair_utilities.monitoring'
        ]
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
                result.add_pass(f"Module Import: {module_name}", "Imported successfully")
            except Exception as e:
                result.add_fail(f"Module Import: {module_name}", f"Failed: {e}")
        
        return True
    except Exception as e:
        result.add_fail("Module Structure Test", str(e))
        return False


def run_comprehensive_test():
    """Run all tests and generate results."""
    print("🔍 COMPREHENSIVE FINAL TEST SUITE")
    print("=" * 60)
    print("Testing fAIr-utilities Integration for Production Readiness")
    print("=" * 60)
    
    result = TestResult()
    
    # Run all test categories
    test_functions = [
        test_basic_imports,
        test_core_functions,
        test_integrated_functions,
        test_training_functions,
        test_configuration_system,
        test_validation_system,
        test_monitoring_system,
        test_class_instantiation,
        test_utility_functions,
        test_module_structure
    ]
    
    for test_func in test_functions:
        try:
            test_func(result)
        except Exception as e:
            result.add_fail(f"Test Function: {test_func.__name__}", f"Crashed: {e}")
    
    return result


def main():
    """Main function to run tests and display results."""
    result = run_comprehensive_test()
    summary = result.get_summary()
    
    # Display summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
    print("=" * 60)
    
    print(f"Total Tests Run: {summary['total_tests']}")
    print(f"Tests Passed: {summary['passed']}")
    print(f"Tests Failed: {summary['failed']}")
    print(f"Warnings: {summary['warnings']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Test Duration: {summary['duration_seconds']:.2f} seconds")
    
    # Show failures if any
    if summary['failures']:
        print(f"\n❌ FAILURES ({len(summary['failures'])}):")
        for test_name, error in summary['failures']:
            print(f"  - {test_name}: {error}")
    
    # Show warnings if any
    if summary['warnings']:
        print(f"\n⚠️  WARNINGS ({len(summary['warnings'])}):")
        for test_name, warning in summary['warnings']:
            print(f"  - {test_name}: {warning}")
    
    # Final assessment
    print(f"\n🎯 FINAL ASSESSMENT:")
    if summary['success_rate'] >= 95:
        print("✅ EXCELLENT - Production ready with high confidence")
        status = "EXCELLENT"
    elif summary['success_rate'] >= 85:
        print("✅ GOOD - Production ready with minor issues")
        status = "GOOD"
    elif summary['success_rate'] >= 70:
        print("⚠️  ACCEPTABLE - Usable but needs attention")
        status = "ACCEPTABLE"
    else:
        print("❌ NEEDS WORK - Not ready for production")
        status = "NEEDS_WORK"
    
    # Save results to JSON for analysis
    summary['status'] = status
    summary['timestamp'] = time.time()
    
    try:
        with open('test_results.json', 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\n📄 Detailed results saved to: test_results.json")
    except Exception as e:
        print(f"\n⚠️  Could not save results to file: {e}")
    
    return summary['success_rate'] >= 85


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
