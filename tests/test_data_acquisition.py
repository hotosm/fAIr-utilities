"""
Comprehensive tests for data acquisition module.

Tests cover TMS downloading, OSM data acquisition, error handling,
and edge cases with proper mocking of external dependencies.
"""

import asyncio
import json
import os
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

import aiohttp
import mercantile
import pytest

from hot_fair_utilities.data_acquisition import TileSource, download_tiles, download_osm_data
from hot_fair_utilities.data_acquisition.tms_downloader import _generate_tile_url_from_template, _apply_georeferencing


class TestTileSource(unittest.TestCase):
    """Test TileSource class functionality."""
    
    def test_tile_source_creation(self):
        """Test basic TileSource creation."""
        source = TileSource(
            url="https://example.com/{z}/{x}/{y}.png",
            scheme="xyz"
        )
        self.assertEqual(source.url, "https://example.com/{z}/{x}/{y}.png")
        self.assertEqual(source.scheme, "xyz")
        self.assertEqual(source.min_zoom, 2)
        self.assertEqual(source.max_zoom, 18)
    
    def test_xyz_url_generation(self):
        """Test XYZ URL generation."""
        source = TileSource("https://example.com/{z}/{x}/{y}.png", scheme="xyz")
        tile = mercantile.Tile(x=1, y=2, z=3)
        url = source.get_tile_url(tile)
        self.assertEqual(url, "https://example.com/3/1/2.png")
    
    def test_tms_url_generation(self):
        """Test TMS URL generation."""
        source = TileSource("https://example.com/{z}/{x}/{y}.png", scheme="tms")
        tile = mercantile.Tile(x=1, y=2, z=3)
        url = source.get_tile_url(tile)
        # TMS y = (2^z - 1) - y = (2^3 - 1) - 2 = 7 - 2 = 5
        self.assertEqual(url, "https://example.com/3/1/5.png")
    
    def test_quadkey_url_generation(self):
        """Test QuadKey URL generation."""
        source = TileSource("https://example.com/{q}.png", scheme="quadkey")
        tile = mercantile.Tile(x=1, y=2, z=3)
        url = source.get_tile_url(tile)
        quadkey = mercantile.quadkey(tile)
        self.assertEqual(url, f"https://example.com/{quadkey}.png")
    
    def test_invalid_scheme(self):
        """Test invalid scheme handling."""
        source = TileSource("https://example.com/{z}/{x}/{y}.png", scheme="invalid")
        tile = mercantile.Tile(x=1, y=2, z=3)
        with self.assertRaises(ValueError):
            source.get_tile_url(tile)
    
    def test_zoom_validation(self):
        """Test zoom level validation."""
        source = TileSource("https://example.com/{z}/{x}/{y}.png", min_zoom=5, max_zoom=15)
        self.assertTrue(source.is_valid_zoom(10))
        self.assertFalse(source.is_valid_zoom(3))
        self.assertFalse(source.is_valid_zoom(20))


class TestUrlGeneration(unittest.TestCase):
    """Test URL generation utilities."""
    
    def test_standard_xyz_template(self):
        """Test standard XYZ template."""
        template = "https://example.com/{z}/{x}/{y}.png"
        tile = mercantile.Tile(x=1, y=2, z=3)
        url = _generate_tile_url_from_template(template, tile)
        self.assertEqual(url, "https://example.com/3/1/2.png")
    
    def test_negative_y_template(self):
        """Test negative Y template."""
        template = "https://example.com/{z}/{x}/{-y}.png"
        tile = mercantile.Tile(x=1, y=2, z=3)
        url = _generate_tile_url_from_template(template, tile)
        self.assertEqual(url, "https://example.com/3/1/-2.png")
    
    def test_quadkey_template(self):
        """Test QuadKey template."""
        template = "https://example.com/{q}.png"
        tile = mercantile.Tile(x=1, y=2, z=3)
        url = _generate_tile_url_from_template(template, tile)
        quadkey = mercantile.quadkey(tile)
        self.assertEqual(url, f"https://example.com/{quadkey}.png")
    
    def test_invalid_template(self):
        """Test invalid template handling."""
        template = "https://example.com/{invalid}.png"
        tile = mercantile.Tile(x=1, y=2, z=3)
        with self.assertRaises(ValueError):
            _generate_tile_url_from_template(template, tile)


class TestAsyncDownload(unittest.IsolatedAsyncioTestCase):
    """Test async download functionality with proper mocking."""
    
    async def test_download_tiles_with_bbox(self):
        """Test tile downloading with bounding box."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the download_tile function to avoid actual HTTP requests
            with patch('hot_fair_utilities.data_acquisition.tms_downloader.download_tile') as mock_download:
                mock_download.return_value = True
                
                result = await download_tiles(
                    tms="https://example.com/{z}/{x}/{y}.png",
                    zoom=10,
                    bbox=[0, 0, 1, 1],
                    out=temp_dir,
                    georeference=False
                )
                
                self.assertTrue(os.path.exists(result))
                self.assertTrue(mock_download.called)
    
    async def test_download_tiles_error_handling(self):
        """Test error handling in tile downloading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with invalid parameters
            with self.assertRaises(ValueError):
                await download_tiles(
                    tms="https://example.com/{z}/{x}/{y}.png",
                    zoom=10,
                    bbox=None,  # No bbox or geojson
                    geojson=None,
                    out=temp_dir
                )
    
    @patch('aiohttp.ClientSession.get')
    async def test_download_tile_success(self, mock_get):
        """Test successful tile download."""
        # Mock successful HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content.read.return_value = b"fake_image_data"
        mock_get.return_value.__aenter__.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as temp_dir:
            from hot_fair_utilities.data_acquisition.tms_downloader import download_tile
            
            session = AsyncMock()
            tile = mercantile.Tile(x=1, y=2, z=3)
            
            result = await download_tile(
                session=session,
                tile_id=tile,
                tile_source="https://example.com/{z}/{x}/{y}.png",
                out_path=temp_dir,
                georeference=False
            )
            
            self.assertTrue(result)
    
    @patch('aiohttp.ClientSession.get')
    async def test_download_tile_retry_logic(self, mock_get):
        """Test retry logic for failed downloads."""
        # Mock failed HTTP response that should trigger retry
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_get.return_value.__aenter__.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as temp_dir:
            from hot_fair_utilities.data_acquisition.tms_downloader import download_tile
            
            session = AsyncMock()
            tile = mercantile.Tile(x=1, y=2, z=3)
            
            result = await download_tile(
                session=session,
                tile_id=tile,
                tile_source="https://example.com/{z}/{x}/{y}.png",
                out_path=temp_dir,
                max_retries=2,
                retry_delay=0.1
            )
            
            self.assertFalse(result)
            # Should have been called multiple times due to retries
            self.assertGreater(mock_get.call_count, 1)


class TestOSMDataAcquisition(unittest.IsolatedAsyncioTestCase):
    """Test OSM data acquisition functionality."""
    
    @patch('aiohttp.ClientSession.post')
    @patch('aiohttp.ClientSession.get')
    async def test_osm_data_download_success(self, mock_get, mock_post):
        """Test successful OSM data download."""
        # Mock API responses
        mock_post_response = AsyncMock()
        mock_post_response.json.return_value = {"track_link": "/task/123"}
        mock_post_response.raise_for_status = MagicMock()
        mock_post.return_value.__aenter__.return_value = mock_post_response
        
        mock_get_response = AsyncMock()
        mock_get_response.json.return_value = {
            "status": "SUCCESS",
            "result": {"download_url": "https://example.com/data.zip"}
        }
        mock_get_response.raise_for_status = MagicMock()
        mock_get.return_value.__aenter__.return_value = mock_get_response
        
        # Mock download_snapshot method
        with patch('hot_fair_utilities.data_acquisition.osm_downloader.RawDataAPI.download_snapshot') as mock_download:
            mock_download.return_value = {
                "type": "FeatureCollection",
                "features": []
            }
            
            result = await download_osm_data(
                bbox=[0, 0, 1, 1],
                feature_type="building"
            )
            
            self.assertIsInstance(result, dict)
            self.assertEqual(result["type"], "FeatureCollection")
    
    async def test_osm_data_invalid_input(self):
        """Test OSM data download with invalid input."""
        with self.assertRaises(ValueError):
            await download_osm_data()  # No bbox or geojson


class TestErrorHandling(unittest.TestCase):
    """Test comprehensive error handling."""
    
    def test_tile_source_invalid_parameters(self):
        """Test TileSource with invalid parameters."""
        with self.assertRaises(ValueError):
            source = TileSource("invalid_url", scheme="invalid_scheme")
            tile = mercantile.Tile(x=1, y=2, z=3)
            source.get_tile_url(tile)
    
    def test_georeferencing_invalid_file(self):
        """Test georeferencing with invalid file."""
        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            tile = mercantile.Tile(x=1, y=2, z=3)
            with self.assertRaises(Exception):
                _apply_georeferencing(temp_file.name, tile, "4326")


if __name__ == '__main__':
    unittest.main()
