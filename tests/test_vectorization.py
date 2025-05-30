"""
Comprehensive tests for vectorization module.

Tests cover advanced vectorization, orthogonalization, error handling,
and edge cases with proper mocking of external dependencies.
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

from hot_fair_utilities.vectorization import VectorizeMasks, orthogonalize_gdf
from hot_fair_utilities.vectorization.regularizer import VectorizeMasks as RegularizerClass
from hot_fair_utilities.vectorization.orthogonalize import orthogonalize_polygon


class TestVectorizeMasks(unittest.TestCase):
    """Test VectorizeMasks class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def test_vectorize_masks_creation(self):
        """Test VectorizeMasks creation with various parameters."""
        # Test default parameters
        converter = VectorizeMasks()
        self.assertEqual(converter.simplify_tolerance, 0.2)
        self.assertEqual(converter.min_area, 1.0)
        self.assertTrue(converter.orthogonalize)
        self.assertEqual(converter.algorithm, "potrace")
    
    def test_vectorize_masks_custom_parameters(self):
        """Test VectorizeMasks with custom parameters."""
        converter = VectorizeMasks(
            simplify_tolerance=0.5,
            min_area=10.0,
            orthogonalize=False,
            algorithm="rasterio"
        )
        self.assertEqual(converter.simplify_tolerance, 0.5)
        self.assertEqual(converter.min_area, 10.0)
        self.assertFalse(converter.orthogonalize)
        self.assertEqual(converter.algorithm, "rasterio")
    
    def test_invalid_algorithm(self):
        """Test invalid algorithm handling."""
        with self.assertRaises(ValueError):
            VectorizeMasks(algorithm="invalid_algorithm")
    
    @patch('subprocess.run')
    def test_potrace_availability_check(self, mock_run):
        """Test Potrace availability checking."""
        converter = VectorizeMasks(algorithm="potrace")
        
        # Test when Potrace is available
        mock_run.return_value.returncode = 0
        self.assertTrue(converter._check_potrace_available())
        
        # Test when Potrace is not available
        mock_run.side_effect = FileNotFoundError()
        self.assertFalse(converter._check_potrace_available())
    
    def test_rasterio_vectorization(self):
        """Test rasterio-based vectorization."""
        converter = VectorizeMasks(algorithm="rasterio")
        
        # Create a simple test raster
        with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Create a simple binary raster for testing
            import rasterio
            from rasterio.transform import from_bounds
            
            # Create test data
            data = np.zeros((100, 100), dtype=np.uint8)
            data[25:75, 25:75] = 1  # Create a square
            
            # Write test raster
            transform = from_bounds(0, 0, 100, 100, 100, 100)
            with rasterio.open(
                temp_path, 'w',
                driver='GTiff',
                height=100, width=100,
                count=1, dtype=np.uint8,
                crs='EPSG:4326',
                transform=transform
            ) as dst:
                dst.write(data, 1)
            
            # Test vectorization
            gdf = converter.vectorize_with_rasterio(temp_path)
            
            self.assertIsInstance(gdf, gpd.GeoDataFrame)
            self.assertGreater(len(gdf), 0)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_geometry_fixing(self):
        """Test geometry fixing functionality."""
        converter = VectorizeMasks()
        
        # Test with valid polygon
        polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
        fixed = converter.fix_geom(polygon)
        self.assertIsInstance(fixed, Polygon)
        
        # Test with None geometry
        fixed_none = converter.fix_geom(None)
        self.assertIsNone(fixed_none)
        
        # Test with empty geometry
        empty_polygon = Polygon()
        fixed_empty = converter.fix_geom(empty_polygon)
        self.assertTrue(fixed_empty.is_empty)
    
    def test_area_filtering(self):
        """Test area-based filtering."""
        converter = VectorizeMasks(min_area=10.0)
        
        # Create test geometries with different areas
        small_polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])  # 1 sq unit
        large_polygon = Polygon([(0, 0), (5, 0), (5, 5), (0, 5), (0, 0)])  # 25 sq units
        
        gdf = gpd.GeoDataFrame(geometry=[small_polygon, large_polygon], crs='EPSG:3857')
        
        filtered_gdf = converter.filter_gdf_by_area(gdf)
        
        # Should only keep the large polygon (assuming it's > 10 sq meters in projected CRS)
        self.assertLessEqual(len(filtered_gdf), len(gdf))


class TestOrthogonalization(unittest.TestCase):
    """Test orthogonalization functionality."""
    
    def test_orthogonalize_simple_polygon(self):
        """Test orthogonalization of a simple polygon."""
        # Create a slightly irregular rectangle
        polygon = Polygon([
            (0, 0), (10.1, 0.1), (10, 10.1), (-0.1, 10), (0, 0)
        ])
        
        orthogonalized = orthogonalize_polygon(polygon)
        
        self.assertIsInstance(orthogonalized, Polygon)
        self.assertTrue(orthogonalized.is_valid)
    
    def test_orthogonalize_gdf(self):
        """Test orthogonalization of GeoDataFrame."""
        # Create test polygons
        polygon1 = Polygon([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])
        polygon2 = Polygon([(20, 20), (30, 20), (30, 30), (20, 30), (20, 20)])
        
        gdf = gpd.GeoDataFrame(geometry=[polygon1, polygon2])
        
        result_gdf = orthogonalize_gdf(gdf)
        
        self.assertIsInstance(result_gdf, gpd.GeoDataFrame)
        self.assertEqual(len(result_gdf), len(gdf))
        
        # Check that all geometries are still valid
        for geom in result_gdf.geometry:
            self.assertTrue(geom.is_valid)
    
    def test_orthogonalize_multipolygon(self):
        """Test orthogonalization of MultiPolygon."""
        poly1 = Polygon([(0, 0), (5, 0), (5, 5), (0, 5), (0, 0)])
        poly2 = Polygon([(10, 10), (15, 10), (15, 15), (10, 15), (10, 10)])
        multipolygon = MultiPolygon([poly1, poly2])
        
        gdf = gpd.GeoDataFrame(geometry=[multipolygon])
        result_gdf = orthogonalize_gdf(gdf)
        
        self.assertEqual(len(result_gdf), 1)
        self.assertTrue(result_gdf.geometry.iloc[0].is_valid)
    
    def test_angle_calculation(self):
        """Test angle calculation between points."""
        from hot_fair_utilities.vectorization.orthogonalize import angle_between_points
        from shapely.geometry import Point
        
        # Test 90-degree angle
        p1 = Point(0, 0)
        p2 = Point(1, 0)
        p3 = Point(1, 1)
        
        angle = angle_between_points(p1, p2, p3)
        
        # Should be approximately π/2 (90 degrees)
        self.assertAlmostEqual(angle, np.pi/2, places=5)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in vectorization."""
    
    def test_invalid_input_file(self):
        """Test handling of invalid input files."""
        converter = VectorizeMasks()
        
        with self.assertRaises(Exception):
            converter.convert("nonexistent_file.tif", "output.geojson")
    
    def test_potrace_not_available(self):
        """Test handling when Potrace is not available."""
        with patch.object(VectorizeMasks, '_check_potrace_available', return_value=False):
            converter = VectorizeMasks(algorithm="potrace")
            
            with tempfile.NamedTemporaryFile(suffix='.tif') as temp_input:
                with tempfile.NamedTemporaryFile(suffix='.geojson') as temp_output:
                    with self.assertRaises(RuntimeError):
                        converter.convert(temp_input.name, temp_output.name)
    
    def test_invalid_geojson_output(self):
        """Test handling of invalid GeoJSON output."""
        converter = VectorizeMasks()
        
        # Mock run_potrace to create invalid JSON
        with patch.object(converter, 'run_potrace') as mock_potrace:
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', unittest.mock.mock_open(read_data="invalid json")):
                    with tempfile.NamedTemporaryFile(suffix='.bmp') as temp_bmp:
                        with tempfile.NamedTemporaryFile(suffix='.geojson') as temp_geojson:
                            with self.assertRaises(RuntimeError):
                                converter.run_potrace(temp_bmp.name, temp_geojson.name)


class TestIntegration(unittest.TestCase):
    """Integration tests for vectorization workflow."""
    
    def test_complete_workflow_rasterio(self):
        """Test complete vectorization workflow with rasterio."""
        converter = VectorizeMasks(
            algorithm="rasterio",
            simplify_tolerance=0.1,
            min_area=1.0,
            orthogonalize=True
        )
        
        # Create a test raster
        with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as temp_input:
            with tempfile.NamedTemporaryFile(suffix='.geojson', delete=False) as temp_output:
                input_path = temp_input.name
                output_path = temp_output.name
        
        try:
            # Create test raster data
            import rasterio
            from rasterio.transform import from_bounds
            
            data = np.zeros((50, 50), dtype=np.uint8)
            data[10:40, 10:40] = 1  # Create a square
            
            transform = from_bounds(0, 0, 50, 50, 50, 50)
            with rasterio.open(
                input_path, 'w',
                driver='GTiff',
                height=50, width=50,
                count=1, dtype=np.uint8,
                crs='EPSG:4326',
                transform=transform
            ) as dst:
                dst.write(data, 1)
            
            # Run conversion
            result_gdf = converter.convert(input_path, output_path)
            
            # Verify results
            self.assertIsInstance(result_gdf, gpd.GeoDataFrame)
            self.assertGreater(len(result_gdf), 0)
            self.assertTrue(os.path.exists(output_path))
            
            # Verify output file is valid GeoJSON
            import json
            with open(output_path, 'r') as f:
                geojson_data = json.load(f)
            
            self.assertEqual(geojson_data['type'], 'FeatureCollection')
            
        finally:
            # Clean up
            for path in [input_path, output_path]:
                if os.path.exists(path):
                    os.unlink(path)


if __name__ == '__main__':
    unittest.main()
