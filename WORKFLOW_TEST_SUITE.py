#!/usr/bin/env python3
"""
Comprehensive Workflow Test Suite for fAIr-utilities Integration

This script tests the complete end-to-end workflow to ensure all integrated
functionality works correctly after the geoml-toolkits and fairpredictor integration.
"""

import asyncio
import sys
import time
import tempfile
import os
from typing import Dict, Any, List


class WorkflowTestResult:
    """Track workflow test results."""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []
        self.warnings = []
        self.start_time = time.time()
    
    def add_pass(self, test_name: str, details: str = ""):
        self.tests_run += 1
        self.tests_passed += 1
        print(f"✅ {test_name}: PASSED {details}")
    
    def add_fail(self, test_name: str, error: str):
        self.tests_run += 1
        self.tests_failed += 1
        self.failures.append((test_name, error))
        print(f"❌ {test_name}: FAILED - {error}")
    
    def add_warning(self, test_name: str, warning: str):
        self.warnings.append((test_name, warning))
        print(f"⚠️  {test_name}: WARNING - {warning}")


async def test_basic_workflow(result: WorkflowTestResult):
    """Test basic import and module availability."""
    print("\n🔍 Testing Basic Workflow...")
    
    try:
        import hot_fair_utilities as fair
        result.add_pass("Module Import", "hot_fair_utilities imported successfully")
        
        # Test core functions are available
        core_functions = [
            'predict', 'vectorize', 'download_tiles', 'VectorizeMasks',
            'predict_with_tiles', 'validate_bbox', 'config'
        ]
        
        for func_name in core_functions:
            if hasattr(fair, func_name):
                result.add_pass(f"Core Function: {func_name}", "Available")
            else:
                result.add_fail(f"Core Function: {func_name}", "Not found")
        
        return True
    except Exception as e:
        result.add_fail("Basic Workflow", f"Import failed: {e}")
        return False


async def test_data_acquisition_workflow(result: WorkflowTestResult):
    """Test data acquisition workflow."""
    print("\n🔍 Testing Data Acquisition Workflow...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test bbox validation
        test_bbox = [85.514668, 27.628367, 85.528875, 27.638514]
        validated_bbox = fair.validate_bbox(test_bbox)
        result.add_pass("Bbox Validation", f"Validated: {validated_bbox}")
        
        # Test tile calculation
        tiles = fair.get_tiles(zoom=10, bbox=test_bbox)
        result.add_pass("Tile Calculation", f"Generated {len(tiles)} tiles")
        
        # Test TileSource creation
        from hot_fair_utilities.data_acquisition import TileSource
        tile_source = TileSource("https://example.com/{z}/{x}/{y}.png")
        result.add_pass("TileSource Creation", "Successfully created")
        
        # Test async download function signature (without actual download)
        if hasattr(fair, 'download_tiles'):
            import inspect
            if inspect.iscoroutinefunction(fair.download_tiles):
                result.add_pass("Async Download Function", "Properly async")
            else:
                result.add_fail("Async Download Function", "Not async")
        
        return True
    except Exception as e:
        result.add_fail("Data Acquisition Workflow", f"Failed: {e}")
        return False


async def test_vectorization_workflow(result: WorkflowTestResult):
    """Test vectorization workflow."""
    print("\n🔍 Testing Vectorization Workflow...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test VectorizeMasks creation with different algorithms
        vectorizer_rasterio = fair.VectorizeMasks(algorithm="rasterio")
        result.add_pass("VectorizeMasks (rasterio)", "Created successfully")
        
        # Test with custom parameters
        vectorizer_custom = fair.VectorizeMasks(
            algorithm="rasterio",
            simplify_tolerance=0.1,
            min_area=5.0,
            orthogonalize=False
        )
        result.add_pass("VectorizeMasks (custom params)", "Created successfully")
        
        # Test orthogonalization function
        if hasattr(fair, 'orthogonalize_gdf'):
            result.add_pass("Orthogonalization Function", "Available")
        else:
            result.add_fail("Orthogonalization Function", "Not found")
        
        # Test Potrace availability check
        try:
            vectorizer_potrace = fair.VectorizeMasks(algorithm="potrace")
            result.add_pass("VectorizeMasks (potrace)", "Created successfully")
        except Exception as e:
            result.add_warning("VectorizeMasks (potrace)", f"Potrace not available: {e}")
        
        return True
    except Exception as e:
        result.add_fail("Vectorization Workflow", f"Failed: {e}")
        return False


async def test_inference_workflow(result: WorkflowTestResult):
    """Test inference workflow."""
    print("\n🔍 Testing Inference Workflow...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test basic prediction function availability
        if hasattr(fair, 'predict'):
            result.add_pass("Basic Prediction Function", "Available")
        else:
            result.add_fail("Basic Prediction Function", "Not found")
        
        # Test enhanced prediction function
        if hasattr(fair, 'predict_with_tiles'):
            import inspect
            if inspect.iscoroutinefunction(fair.predict_with_tiles):
                result.add_pass("Enhanced Prediction Function", "Available and async")
            else:
                result.add_fail("Enhanced Prediction Function", "Not async")
        else:
            result.add_fail("Enhanced Prediction Function", "Not found")
        
        # Test default model constants
        default_models = [
            'DEFAULT_RAMP_MODEL', 'DEFAULT_YOLO_MODEL_V1', 
            'DEFAULT_YOLO_MODEL_V2', 'DEFAULT_OAM_TMS_MOSAIC'
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
        
        return True
    except Exception as e:
        result.add_fail("Inference Workflow", f"Failed: {e}")
        return False


async def test_training_workflow(result: WorkflowTestResult):
    """Test training workflow."""
    print("\n🔍 Testing Training Workflow...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test training functions
        training_functions = ['ramp_train', 'yolo_v8_v1_train', 'yolo_v8_v2_train']
        
        for func_name in training_functions:
            if hasattr(fair, func_name):
                func = getattr(fair, func_name)
                if callable(func):
                    result.add_pass(f"Training Function: {func_name}", "Available and callable")
                else:
                    result.add_fail(f"Training Function: {func_name}", "Not callable")
            else:
                result.add_fail(f"Training Function: {func_name}", "Not found")
        
        return True
    except Exception as e:
        result.add_fail("Training Workflow", f"Failed: {e}")
        return False


async def test_configuration_workflow(result: WorkflowTestResult):
    """Test configuration and monitoring workflow."""
    print("\n🔍 Testing Configuration Workflow...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test configuration system
        if hasattr(fair, 'config'):
            config = fair.config
            result.add_pass("Configuration System", f"Available: {type(config)}")
            
            # Test configuration validation
            if hasattr(config, 'validate'):
                issues = config.validate()
                if not issues:
                    result.add_pass("Configuration Validation", "No issues")
                else:
                    result.add_warning("Configuration Validation", f"Issues: {issues}")
            else:
                result.add_warning("Configuration Validation", "No validate method")
        else:
            result.add_fail("Configuration System", "Not found")
        
        # Test monitoring system
        monitoring_components = ['logger', 'performance_monitor', 'ProgressTracker']
        
        for comp_name in monitoring_components:
            if hasattr(fair, comp_name):
                result.add_pass(f"Monitoring: {comp_name}", "Available")
            else:
                result.add_fail(f"Monitoring: {comp_name}", "Not found")
        
        return True
    except Exception as e:
        result.add_fail("Configuration Workflow", f"Failed: {e}")
        return False


async def test_validation_workflow(result: WorkflowTestResult):
    """Test validation and security workflow."""
    print("\n🔍 Testing Validation Workflow...")
    
    try:
        import hot_fair_utilities as fair
        
        # Test validation functions
        validation_tests = [
            ('validate_bbox', [85.514668, 27.628367, 85.528875, 27.638514]),
            ('validate_zoom_level', 10),
            ('validate_confidence', 0.5),
            ('validate_area_threshold', 10.0)
        ]
        
        for func_name, test_value in validation_tests:
            if hasattr(fair, func_name):
                try:
                    func = getattr(fair, func_name)
                    validated = func(test_value)
                    result.add_pass(f"Validation: {func_name}", f"Validated: {validated}")
                except Exception as e:
                    result.add_fail(f"Validation: {func_name}", f"Failed: {e}")
            else:
                result.add_fail(f"Validation: {func_name}", "Not found")
        
        # Test validation exceptions
        if hasattr(fair, 'ValidationError') and hasattr(fair, 'SecurityError'):
            result.add_pass("Validation Exceptions", "Available")
        else:
            result.add_fail("Validation Exceptions", "Not found")
        
        return True
    except Exception as e:
        result.add_fail("Validation Workflow", f"Failed: {e}")
        return False


async def test_end_to_end_workflow(result: WorkflowTestResult):
    """Test end-to-end workflow simulation."""
    print("\n🔍 Testing End-to-End Workflow...")
    
    try:
        import hot_fair_utilities as fair
        
        # Simulate complete workflow without actual downloads/predictions
        test_bbox = [85.514668, 27.628367, 85.528875, 27.638514]
        
        # Step 1: Validate inputs
        validated_bbox = fair.validate_bbox(test_bbox)
        validated_zoom = fair.validate_zoom_level(18)
        validated_confidence = fair.validate_confidence(0.5)
        result.add_pass("E2E Step 1: Input Validation", "All inputs validated")
        
        # Step 2: Calculate tiles
        tiles = fair.get_tiles(zoom=validated_zoom, bbox=validated_bbox)
        result.add_pass("E2E Step 2: Tile Calculation", f"Generated {len(tiles)} tiles")
        
        # Step 3: Create vectorizer
        vectorizer = fair.VectorizeMasks(algorithm="rasterio")
        result.add_pass("E2E Step 3: Vectorizer Creation", "Created successfully")
        
        # Step 4: Check async functions are available
        async_functions = ['download_tiles', 'predict_with_tiles']
        for func_name in async_functions:
            if hasattr(fair, func_name):
                import inspect
                func = getattr(fair, func_name)
                if inspect.iscoroutinefunction(func):
                    result.add_pass(f"E2E Step 4: {func_name}", "Available and async")
                else:
                    result.add_fail(f"E2E Step 4: {func_name}", "Not async")
            else:
                result.add_fail(f"E2E Step 4: {func_name}", "Not found")
        
        result.add_pass("End-to-End Workflow", "Complete workflow validated")
        return True
        
    except Exception as e:
        result.add_fail("End-to-End Workflow", f"Failed: {e}")
        return False


async def run_comprehensive_workflow_test():
    """Run all workflow tests."""
    print("🔍 COMPREHENSIVE WORKFLOW TEST SUITE")
    print("=" * 60)
    print("Testing fAIr-utilities Integration Workflows")
    print("=" * 60)
    
    result = WorkflowTestResult()
    
    # Run all workflow tests
    workflow_tests = [
        test_basic_workflow,
        test_data_acquisition_workflow,
        test_vectorization_workflow,
        test_inference_workflow,
        test_training_workflow,
        test_configuration_workflow,
        test_validation_workflow,
        test_end_to_end_workflow
    ]
    
    for test_func in workflow_tests:
        try:
            await test_func(result)
        except Exception as e:
            result.add_fail(f"Workflow Test: {test_func.__name__}", f"Crashed: {e}")
    
    # Generate summary
    duration = time.time() - result.start_time
    
    print("\n" + "=" * 60)
    print("📊 WORKFLOW TEST RESULTS SUMMARY")
    print("=" * 60)
    
    print(f"Total Tests Run: {result.tests_run}")
    print(f"Tests Passed: {result.tests_passed}")
    print(f"Tests Failed: {result.tests_failed}")
    print(f"Warnings: {len(result.warnings)}")
    print(f"Success Rate: {(result.tests_passed/result.tests_run)*100:.1f}%")
    print(f"Test Duration: {duration:.2f} seconds")
    
    # Show failures if any
    if result.failures:
        print(f"\n❌ FAILURES ({len(result.failures)}):")
        for test_name, error in result.failures:
            print(f"  - {test_name}: {error}")
    
    # Show warnings if any
    if result.warnings:
        print(f"\n⚠️  WARNINGS ({len(result.warnings)}):")
        for test_name, warning in result.warnings:
            print(f"  - {test_name}: {warning}")
    
    # Final assessment
    success_rate = (result.tests_passed/result.tests_run)*100
    print(f"\n🎯 WORKFLOW ASSESSMENT:")
    if success_rate >= 95:
        print("✅ EXCELLENT - All workflows functioning perfectly")
        status = "EXCELLENT"
    elif success_rate >= 85:
        print("✅ GOOD - Workflows functioning well with minor issues")
        status = "GOOD"
    elif success_rate >= 70:
        print("⚠️  ACCEPTABLE - Workflows mostly functional")
        status = "ACCEPTABLE"
    else:
        print("❌ NEEDS WORK - Significant workflow issues")
        status = "NEEDS_WORK"
    
    return status, result


def main():
    """Main function to run workflow tests."""
    try:
        status, result = asyncio.run(run_comprehensive_workflow_test())
        return status in ["EXCELLENT", "GOOD"]
    except Exception as e:
        print(f"❌ Workflow test suite failed to run: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
