"""
TMS (Tile Map Service) downloader with async support.

This module provides functionality to download tiles from various TMS sources
with support for different tile schemes, georeferencing, and CRS transformations.
"""

import argparse
import asyncio
import json
import os
import re
import mimetypes
from typing import Dict, List, Optional, Union, Any

import aiohttp
import geopandas as gpd
import mercantile
import rasterio
from pyproj import Transformer
from rasterio.transform import from_bounds
from tqdm import tqdm

from ..utils import get_tiles


async def fetch_tilejson(session: aiohttp.ClientSession, tilejson_url: str) -> Dict[str, Any]:
    """Fetch TileJSON metadata from a URL."""
    async with session.get(tilejson_url) as response:
        if response.status != 200:
            raise ValueError(f"Failed to fetch TileJSON from {tilejson_url}: {response.status}")
        return await response.json()


class TileSource:
    """
    Represents a tile source with support for different tile schemes.

    Supports XYZ, TMS, QuadKey, and custom tile schemes.
    """

    def __init__(
        self,
        url: str,
        scheme: str = "xyz",
        format: Optional[str] = 'tif',
        min_zoom: int = 2,
        max_zoom: int = 18
    ):
        self.url = url
        self.scheme = scheme.lower()
        self.format = format
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.tilejson = None

    @classmethod
    async def from_tilejson(cls, session: aiohttp.ClientSession, tilejson_url: str):
        """Create a TileSource from a TileJSON URL."""
        tilejson = await fetch_tilejson(session, tilejson_url)

        source = cls(url="")
        source.tilejson = tilejson
        source.min_zoom = tilejson.get("minzoom", 2)
        source.max_zoom = tilejson.get("maxzoom", 18)

        if "tiles" in tilejson and tilejson["tiles"]:
            source.url = tilejson["tiles"][0]
        else:
            raise ValueError("No tile URLs found in TileJSON")

        source.scheme = tilejson.get("scheme", "xyz").lower()

        if "format" in tilejson:
            source.format = tilejson["format"]
        elif "{format}" in source.url:
            source.format = "png"
            source.url = source.url.replace("{format}", source.format)

        return source

    def get_tile_url(self, tile: mercantile.Tile) -> str:
        """Generate tile URL for a given tile."""
        if self.scheme == "xyz":
            try:
                return self.url.format(z=tile.z, x=tile.x, y=tile.y)
            except KeyError:
                if "{-y}" in self.url:
                    return self.url.format(z=tile.z, x=tile.x).replace("{-y}", str(-tile.y))
                else:
                    raise ValueError(f"Unsupported XYZ format: {self.url}")
        elif self.scheme == "tms":
            y_tms = (2**tile.z) - 1 - tile.y
            return self.url.format(z=tile.z, x=tile.x, y=y_tms)
        elif self.scheme == "quadkey":
            quadkey = mercantile.quadkey(tile)
            return self.url.format(q=quadkey)
        elif self.scheme == "custom":
            return self.url.format(
                z=tile.z,
                x=tile.x,
                y=tile.y,
                q=mercantile.quadkey(tile)
            ).replace("{-y}", str((2**tile.z) - 1 - tile.y)).replace("{2^z}", str(2**tile.z))
        else:
            raise ValueError(f"Unsupported tile scheme: {self.scheme}")

    def is_valid_zoom(self, zoom: int) -> bool:
        """Check if zoom level is within supported range."""
        return self.min_zoom <= zoom <= self.max_zoom


async def download_tile(
    session: aiohttp.ClientSession,
    tile_id: mercantile.Tile,
    tile_source: Union[TileSource, str],
    out_path: str,
    georeference: bool = False,
    prefix: str = "OAM",
    crs: str = "4326",
    extension: str = 'tif',
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> bool:
    """
    Download a single tile asynchronously with robust error handling and retry logic.

    Args:
        session: Active aiohttp client session
        tile_id: Mercantile tile to download
        tile_source: Tile map service URL template or TileSource object
        out_path: Output directory for the tile
        georeference: Whether to add georeference metadata
        prefix: Prefix for output filename
        crs: Coordinate reference system (4326 or 3857)
        extension: File extension for output
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        True if download successful, False otherwise

    Raises:
        ValueError: If invalid parameters provided
        OSError: If file system operations fail
    """
    # Input validation
    if not isinstance(tile_id, mercantile.Tile):
        raise ValueError(f"Invalid tile_id type: {type(tile_id)}")

    if crs not in ["4326", "3857"]:
        raise ValueError(f"Unsupported CRS: {crs}. Must be '4326' or '3857'")

    if not os.path.exists(out_path):
        try:
            os.makedirs(out_path, exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create output directory {out_path}: {e}")

    # Generate tile URL with error handling
    try:
        if isinstance(tile_source, str):
            tile_url = _generate_tile_url_from_template(tile_source, tile_id)
        else:
            tile_url = tile_source.get_tile_url(tile_id)
    except Exception as e:
        print(f"Error generating URL for tile {tile_id}: {e}")
        return False

    tile_filename = f"{prefix}-{tile_id.x}-{tile_id.y}-{tile_id.z}.{extension}"
    tile_path = os.path.join(out_path, tile_filename)

    # Retry logic for download
    for attempt in range(max_retries):
        try:
            async with session.get(tile_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    tile_data = await response.content.read()

                    # Validate downloaded data
                    if len(tile_data) == 0:
                        print(f"Warning: Empty tile data for {tile_id}")
                        return False

                    # Write file with error handling
                    try:
                        with open(tile_path, "wb") as f:
                            f.write(tile_data)
                    except OSError as e:
                        print(f"Error writing tile {tile_id} to {tile_path}: {e}")
                        return False

                    # Apply georeferencing if requested
                    if georeference and extension.lower() in ['tif', 'tiff']:
                        try:
                            _apply_georeferencing(tile_path, tile_id, crs)
                        except Exception as e:
                            print(f"Warning: Georeferencing failed for {tile_path}: {e}")
                            # Continue without georeferencing rather than failing

                    return True

                elif response.status == 404:
                    print(f"Tile {tile_id} not found (404)")
                    return False
                elif response.status == 429:
                    # Rate limited - wait longer before retry
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                    continue
                else:
                    print(f"HTTP {response.status} for tile {tile_id}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (attempt + 1))
                        continue
                    return False

        except asyncio.TimeoutError:
            print(f"Timeout downloading tile {tile_id} (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (attempt + 1))
                continue
            return False
        except aiohttp.ClientError as e:
            print(f"Client error downloading tile {tile_id}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (attempt + 1))
                continue
            return False
        except Exception as e:
            print(f"Unexpected error downloading tile {tile_id}: {e}")
            return False

    return False


def _generate_tile_url_from_template(template: str, tile_id: mercantile.Tile) -> str:
    """
    Generate tile URL from template with comprehensive format support.

    Args:
        template: URL template string
        tile_id: Mercantile tile

    Returns:
        Generated URL

    Raises:
        ValueError: If template format is unsupported
    """
    try:
        return template.format(z=tile_id.z, x=tile_id.x, y=tile_id.y)
    except KeyError:
        try:
            if "{-y}" in template:
                return template.format(z=tile_id.z, x=tile_id.x).replace("{-y}", str(-tile_id.y))
            else:
                raise ValueError(f"Unsupported XYZ format: {template}")
        except KeyError:
            try:
                quadkey = mercantile.quadkey(tile_id)
                return template.format(q=quadkey)
            except KeyError:
                raise ValueError(f"Unsupported URL template format: {template}")


def _apply_georeferencing(tile_path: str, tile_id: mercantile.Tile, crs: str) -> None:
    """
    Apply georeferencing to a tile file.

    Args:
        tile_path: Path to the tile file
        tile_id: Mercantile tile
        crs: Coordinate reference system

    Raises:
        Exception: If georeferencing fails
    """
    bounds = mercantile.bounds(tile_id)

    if crs == "3857":
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
        xmin, ymin = transformer.transform(bounds.west, bounds.south)
        xmax, ymax = transformer.transform(bounds.east, bounds.north)
        mercator_bounds = (xmin, ymin, xmax, ymax)

        with rasterio.Env(CPL_DEBUG=False):
            with rasterio.open(tile_path, "r+") as dataset:
                transform = from_bounds(*mercator_bounds, dataset.width, dataset.height)
                dataset.transform = transform
                dataset.update_tags(ns="rio_georeference", georeferencing_applied="True")
                dataset.crs = rasterio.crs.CRS.from_epsg(3857)
    else:
        with rasterio.Env(CPL_DEBUG=False):
            with rasterio.open(tile_path, "r+") as dataset:
                transform = from_bounds(*bounds, dataset.width, dataset.height)
                dataset.transform = transform
                dataset.update_tags(ns="rio_georeference", georeferencing_applied="True")
                dataset.crs = rasterio.crs.CRS.from_epsg(4326)


async def download_tiles(
    tms: Union[str, TileSource],
    zoom: int,
    out: str = None,
    geojson: Optional[Union[str, dict]] = None,
    bbox: Optional[List[float]] = None,
    within: bool = False,
    georeference: bool = False,
    dump: bool = False,
    prefix: str = "OAM",
    crs: str = "4326",
    tile_scheme: str = "xyz",
    is_tilejson: bool = False,
    extension: str = 'tif',
) -> str:
    """
    Download tiles from a GeoJSON or bounding box asynchronously.

    Args:
        tms: Tile map service URL template
        zoom: Zoom level for tiles
        out: Output directory for downloaded tiles
        geojson: GeoJSON file path, string, or dictionary
        bbox: Bounding box coordinates
        within: Download only tiles completely within geometry
        georeference: Add georeference metadata to tiles
        dump: Dump tile geometries to a GeoJSON file
        prefix: Prefix for output filenames
        crs: Coordinate reference system (4326 or 3857)
        tile_scheme: Tile scheme to use
        is_tilejson: Whether TMS URL is a TileJSON URL
        extension: File extension for tiles

    Returns:
        Path to the chips directory containing downloaded tiles
    """
    if out is None:
        out = os.getcwd()

    chips_dir = os.path.join(out, "chips")
    os.makedirs(chips_dir, exist_ok=True)

    tiles = get_tiles(zoom=zoom, geojson=geojson, bbox=bbox, within=within)
    print(f"Total tiles fetched: {len(tiles)}")

    if dump:
        feature_collection = {
            "type": "FeatureCollection",
            "features": [mercantile.feature(tile) for tile in tiles],
        }

        if crs == "3857":
            gdf = gpd.GeoDataFrame.from_features(feature_collection["features"])
            gdf.set_crs(epsg=4326, inplace=True)
            gdf = gdf.to_crs(epsg=3857)
            reprojected_fc = json.loads(gdf.to_json())
            feature_collection = reprojected_fc

            feature_collection["crs"] = {
                "type": "name",
                "properties": {"name": "urn:ogc:def:crs:EPSG::3857"}
            }
        else:
            feature_collection["crs"] = {
                "type": "name",
                "properties": {"name": "urn:ogc:def:crs:EPSG::4326"}
            }

        with open(os.path.join(out, "tiles.geojson"), "w") as f:
            json.dump(feature_collection, f)

    async with aiohttp.ClientSession() as session:
        if isinstance(tms, str):
            if is_tilejson:
                tile_source = await TileSource.from_tilejson(session, tms)
            else:
                tile_source = TileSource(tms, scheme=tile_scheme)
        else:
            tile_source = tms

        if not tile_source.is_valid_zoom(zoom):
            print(f"Warning: Requested zoom level {zoom} is outside the source's supported range ({tile_source.min_zoom}-{tile_source.max_zoom})")

        tasks = [
            asyncio.create_task(
                download_tile(
                    session,
                    tile_id,
                    tile_source,
                    chips_dir,
                    georeference,
                    prefix,
                    crs,
                    extension=extension,
                )
            )
            for tile_id in tiles
        ]

        pbar = tqdm(total=len(tasks), unit="tile")
        for future in asyncio.as_completed(tasks):
            await future
            pbar.update(1)
        pbar.close()

    return chips_dir