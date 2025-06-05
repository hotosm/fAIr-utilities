"""
Integration tests for the new fAIr-utilities functionality.

This test suite validates the integration of geoml-toolkits and fairpredictor
functionality into the main fAIr-utilities package.
"""

import asyncio
import json
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon

# Import the integrated modules
try:
    import hot_fair_utilities as fair
    from hot_fair_utilities.data_acquisition import TileSource, download_tiles
    from hot_fair_utilities.vectorization import VectorizeMasks, orthogonalize_gdf
    from hot_fair_utilities.inference import predict_with_tiles
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure hot_fair_utilities is properly installed")
    exit(1)


class TestDataAcquisition(unittest.TestCase):
    """Test data acquisition functionality."""
    
    def test_tile_source_creation(self):
        """Test TileSource class creation and URL generation."""
        # Test XYZ scheme
        source = TileSource(
            url="https://example.com/{z}/{x}/{y}.png",
            scheme="xyz"
        )
        
        import mercantile
        tile = mercantile.Tile(x=1, y=2, z=3)
        url = source.get_tile_url(tile)
        expected = "https://example.com/3/1/2.png"
        self.assertEqual(url, expected)
    
    def test_tile_source_tms_scheme(self):
        """Test TMS scheme URL generation."""
        source = TileSource(
            url="https://example.com/{z}/{x}/{y}.png",
            scheme="tms"
        )
        
        import mercantile
        tile = mercantile.Tile(x=1, y=2, z=3)
        url = source.get_tile_url(tile)
        # TMS y = (2^z - 1) - y = (2^3 - 1) - 2 = 7 - 2 = 5
        expected = "https://example.com/3/1/5.png"
        self.assertEqual(url, expected)
    
    def test_quadkey_scheme(self):
        """Test QuadKey scheme URL generation."""
        source = TileSource(
            url="https://example.com/{q}.png",
            scheme="quadkey"
        )
        
        import mercantile
        tile = mercantile.Tile(x=1, y=2, z=3)
        url = source.get_tile_url(tile)
        quadkey = mercantile.quadkey(tile)
        expected = f"https://example.com/{quadkey}.png"
        self.assertEqual(url, expected)


class TestVectorization(unittest.TestCase):
    """Test vectorization functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def test_vectorize_masks_creation(self):
        """Test VectorizeMasks class creation."""
        converter = VectorizeMasks(
            simplify_tolerance=0.2,
            min_area=5.0,
            orthogonalize=True,
            algorithm="rasterio"
        )
        
        self.assertEqual(converter.simplify_tolerance, 0.2)
        self.assertEqual(converter.min_area, 5.0)
        self.assertTrue(converter.orthogonalize)
        self.assertEqual(converter.algorithm, "rasterio")
    
    def test_orthogonalize_gdf(self):
        """Test orthogonalization of GeoDataFrame."""
        # Create a simple polygon
        polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
        gdf = gpd.GeoDataFrame(geometry=[polygon])
        
        # Apply orthogonalization
        result_gdf = orthogonalize_gdf(gdf)
        
        # Should return a GeoDataFrame with same number of features
        self.assertEqual(len(result_gdf), len(gdf))
        self.assertIsInstance(result_gdf, gpd.GeoDataFrame)
    
    def test_fix_geom_method(self):
        """Test geometry fixing method."""
        converter = VectorizeMasks()
        
        # Test with valid polygon
        polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
        fixed = converter.fix_geom(polygon)
        self.assertIsInstance(fixed, Polygon)
        
        # Test with None geometry
        fixed_none = converter.fix_geom(None)
        self.assertIsNone(fixed_none)


class TestUtilities(unittest.TestCase):
    """Test utility functions."""
    
    def test_get_tiles_with_bbox(self):
        """Test get_tiles function with bbox."""
        bbox = [85.514668, 27.628367, 85.528875, 27.638514]
        tiles = fair.get_tiles(zoom=18, bbox=bbox)
        
        self.assertIsInstance(tiles, list)
        self.assertGreater(len(tiles), 0)
        
        # Check that tiles are mercantile.Tile objects
        import mercantile
        for tile in tiles:
            self.assertIsInstance(tile, mercantile.Tile)
    
    def test_get_geometry_with_bbox(self):
        """Test get_geometry function with bbox."""
        bbox = [85.514668, 27.628367, 85.528875, 27.638514]
        geometry = fair.get_geometry(bbox=bbox)
        
        self.assertIsInstance(geometry, dict)
        self.assertEqual(geometry['type'], 'Polygon')
        self.assertIn('coordinates', geometry)


class TestInference(unittest.TestCase):
    """Test inference functionality."""
    
    def test_download_or_validate_model(self):
        """Test model download/validation function."""
        from hot_fair_utilities.inference.enhanced_predict import download_or_validate_model
        
        # Test with non-existent local file
        with self.assertRaises(FileNotFoundError):
            download_or_validate_model("non_existent_model.pt")
        
        # Test with existing file (create a dummy file)
        with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as tmp:
            tmp.write(b"dummy model data")
            tmp_path = tmp.name
        
        try:
            result = download_or_validate_model(tmp_path)
            self.assertEqual(result, tmp_path)
        finally:
            os.unlink(tmp_path)
    
    def test_default_models_defined(self):
        """Test that default models are properly defined."""
        self.assertTrue(hasattr(fair, 'DEFAULT_RAMP_MODEL'))
        self.assertTrue(hasattr(fair, 'DEFAULT_YOLO_MODEL_V1'))
        self.assertTrue(hasattr(fair, 'DEFAULT_YOLO_MODEL_V2'))
        self.assertTrue(hasattr(fair, 'DEFAULT_OAM_TMS_MOSAIC'))
        
        # Check they are strings (URLs)
        self.assertIsInstance(fair.DEFAULT_RAMP_MODEL, str)
        self.assertIsInstance(fair.DEFAULT_YOLO_MODEL_V1, str)
        self.assertIsInstance(fair.DEFAULT_YOLO_MODEL_V2, str)
        self.assertIsInstance(fair.DEFAULT_OAM_TMS_MOSAIC, str)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""
    
    def test_imports(self):
        """Test that all new modules can be imported."""
        # Test main imports
        self.assertTrue(hasattr(fair, 'download_tiles'))
        self.assertTrue(hasattr(fair, 'download_osm_data'))
        self.assertTrue(hasattr(fair, 'VectorizeMasks'))
        self.assertTrue(hasattr(fair, 'orthogonalize_gdf'))
        self.assertTrue(hasattr(fair, 'predict_with_tiles'))
    
    def test_module_structure(self):
        """Test that the module structure is correct."""
        # Check that new modules exist
        import hot_fair_utilities.data_acquisition
        import hot_fair_utilities.vectorization
        
        # Check that classes are available
        from hot_fair_utilities.data_acquisition import TileSource
        from hot_fair_utilities.vectorization import VectorizeMasks
        
        self.assertTrue(callable(TileSource))
        self.assertTrue(callable(VectorizeMasks))


class TestAsyncFunctionality(unittest.TestCase):
    """Test async functionality."""
    
    def test_async_function_signatures(self):
        """Test that async functions are properly defined."""
        import inspect
        
        # Check that download_tiles is async
        self.assertTrue(inspect.iscoroutinefunction(fair.download_tiles))
        
        # Check that download_osm_data is async
        self.assertTrue(inspect.iscoroutinefunction(fair.download_osm_data))
        
        # Check that predict_with_tiles is async
        self.assertTrue(inspect.iscoroutinefunction(fair.predict_with_tiles))


def run_integration_tests():
    """
    Run all integration tests.
    """
    print("🧪 Running fAIr-utilities Integration Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestDataAcquisition,
        TestVectorization,
        TestUtilities,
        TestInference,
        TestIntegration,
        TestAsyncFunctionality,
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("🧪 Test Summary")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed! Integration successful.")
    else:
        print("\n❌ Some tests failed. Check the output above.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)
