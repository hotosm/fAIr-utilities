"""
Advanced vectorization and regularization of raster masks.

This module provides the VectorizeMasks class for converting GeoTIFF files
to GeoJSON with advanced geometry cleaning, regularization, and orthogonalization.
"""

import argparse
import json
import logging
import os
import subprocess
from typing import List, Tuple, Union

import geopandas as gpd
import numpy as np
import rasterio
from PIL import Image
from rasterio import features
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Polygon
from shapely.ops import polygonize

try:
    from shapely.ops import unary_union
except ImportError:
    from shapely.ops import cascaded_union as unary_union

from .orthogonalize import orthogonalize_gdf


class VectorizeMasks:
    """
    A class to convert GeoTIFF files to GeoJSON with advanced geometry cleaning.

    This class provides methods to:
    1. Convert GeoTIFF to vector data using either Potrace or direct rasterization
    2. Clean and simplify geometries
    3. Optionally orthogonalize shapes
    """

    def __init__(
        self,
        simplify_tolerance: float = 0.2,
        min_area: float = 1.0,
        orthogonalize: bool = True,
        algorithm: str = "potrace",
        tmp_dir: str = None,
        logger: logging.Logger = None,
    ):
        """
        Initialize the converter with configuration parameters.

        Args:
            simplify_tolerance: Tolerance for geometry simplification (in CRS units, meters for projected CRS)
            min_area: Minimum area for polygons to keep (in square meters)
            orthogonalize: Whether to orthogonalize geometries to snap to 45 degrees
            algorithm: Vectorization algorithm to use ('potrace' or 'rasterio')
            tmp_dir: Directory for temporary files (defaults to current directory)
            logger: Logger instance (creates a new one if not provided)
        """
        self.simplify_tolerance = simplify_tolerance
        self.min_area = min_area
        self.orthogonalize = orthogonalize
        self.algorithm = algorithm.lower()
        self.tmp_dir = tmp_dir or os.getcwd()

        # Validate algorithm choice
        if self.algorithm not in ["potrace", "rasterio"]:
            raise ValueError("Algorithm must be either 'potrace' or 'rasterio'")

        # Set up logging
        self.logger = logger or self._setup_logger()

    @staticmethod
    def _setup_logger() -> logging.Logger:
        """Set up and return a logger instance."""
        logger = logging.getLogger("VectorizeMasks")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        return logger

    def run_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """
        Run a command via subprocess, logging its stdout and stderr.

        Args:
            cmd: Command to run as a list of strings

        Returns:
            CompletedProcess instance

        Raises:
            RuntimeError: If command fails
        """
        self.logger.info("Running command: " + " ".join(cmd))
        try:
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.stdout:
                self.logger.info("stdout:\n" + result.stdout)
            if result.stderr:
                self.logger.info("stderr:\n" + result.stderr)
            return result
        except subprocess.CalledProcessError as e:
            self.logger.error("Command failed: " + " ".join(cmd))
            self.logger.error(e.stderr)
            raise RuntimeError(f"Command failed: {' '.join(cmd)}")

    def convert_tif_to_bmp(
        self, input_tif: str, output_bmp: str
    ) -> Tuple[rasterio.Affine, str]:
        """
        Read the GeoTIFF with rasterio, then convert its first band into an 8-bit
        BMP image using Pillow. Returns the affine transform and CRS.

        Args:
            input_tif: Path to input GeoTIFF file
            output_bmp: Path to output BMP file

        Returns:
            Tuple containing the affine transform and CRS
        """
        with rasterio.open(input_tif) as src:
            # Read the first band as a NumPy array
            array = src.read(1)
            transform = src.transform
            crs = src.crs

        # Scale array to 0-255 if needed
        if array.dtype != np.uint8:
            array = ((array - array.min()) / (array.max() - array.min()) * 255).astype(
                np.uint8
            )
        # Flip array vertically (BMP origin is at bottom-left)
        array = np.flipud(array)

        # Create a PIL image and save as BMP
        img = Image.fromarray(array)
        img.save(output_bmp, format="BMP")
        self.logger.info(f"BMP image saved as {output_bmp}")
        return transform, crs

    def run_potrace(self, bmp_file: str, output_geojson: str) -> None:
        """
        Run the Potrace command to vectorize the bitmap with comprehensive error handling.

        Args:
            bmp_file: Path to input BMP file
            output_geojson: Path to output GeoJSON file

        Raises:
            RuntimeError: If Potrace is not available or command fails
            FileNotFoundError: If input file doesn't exist
        """
        # Check if Potrace is available
        if not self._check_potrace_available():
            raise RuntimeError(
                "Potrace is not available. Please install Potrace or use 'rasterio' algorithm instead. "
                "Install instructions: https://potrace.sourceforge.net/"
            )

        # Validate input file
        if not os.path.exists(bmp_file):
            raise FileNotFoundError(f"Input BMP file not found: {bmp_file}")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_geojson), exist_ok=True)

        cmd = ["potrace", "-b", "geojson", "-o", output_geojson, bmp_file, "-i"]

        try:
            self.run_command(cmd)

            # Validate output was created
            if not os.path.exists(output_geojson):
                raise RuntimeError(f"Potrace failed to create output file: {output_geojson}")

            # Validate output is valid JSON
            try:
                with open(output_geojson, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Potrace generated invalid GeoJSON: {e}")

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Potrace command failed: {e.stderr}")

    def _check_potrace_available(self) -> bool:
        """
        Check if Potrace is available in the system PATH.

        Returns:
            True if Potrace is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["potrace", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False

    def pixel_to_geo(
        self, coord: Tuple[float, float], transform: rasterio.Affine
    ) -> List[float]:
        """
        Convert pixel coordinates (col, row) to geographic coordinates (x, y)
        using the affine transform.

        Args:
            coord: Tuple of (column, row) pixel coordinates
            transform: Affine transform from rasterio

        Returns:
            List containing [x, y] geographic coordinates
        """
        # Note: coord[0] is the column (x pixel) and coord[1] is the row (y pixel)
        x, y = transform * (coord[0], coord[1])
        return [x, y]

    def update_geojson_coords(
        self, geojson_file: str, transform: rasterio.Affine, crs: str
    ) -> None:
        """
        Read the GeoJSON produced by Potrace (which is in pixel coordinates),
        convert every coordinate to geographic space using the transform,
        and add CRS info.

        Args:
            geojson_file: Path to the GeoJSON file to update
            transform: Affine transform from rasterio
            crs: Coordinate Reference System as string
        """
        with open(geojson_file, "r") as f:
            geojson_data = json.load(f)

        def convert_ring(ring):
            return [self.pixel_to_geo(pt, transform) for pt in ring]

        for feature in geojson_data.get("features", []):
            geom = feature.get("geometry")
            if not geom:
                continue

            if geom["type"] == "Polygon":
                new_rings = []
                for ring in geom["coordinates"]:
                    new_rings.append(convert_ring(ring))
                feature["geometry"]["coordinates"] = new_rings

            elif geom["type"] == "MultiPolygon":
                new_polygons = []
                for polygon in geom["coordinates"]:
                    new_polygon = []
                    for ring in polygon:
                        new_polygon.append(convert_ring(ring))
                    new_polygons.append(new_polygon)
                feature["geometry"]["coordinates"] = new_polygons

        # Embed the CRS (non-standard but useful)
        if crs:
            geojson_data["crs"] = {
                "type": "name",
                "properties": {"name": str(crs)},
            }

        with open(geojson_file, "w") as f:
            json.dump(geojson_data, f, indent=2)
        self.logger.info(f"Updated GeoJSON saved as {geojson_file}")

    def vectorize_with_rasterio(
        self, input_tiff: str, threshold: float = 0
    ) -> gpd.GeoDataFrame:
        """
        Vectorize a GeoTIFF directly using rasterio.features without intermediate files.

        Args:
            input_tiff: Path to input GeoTIFF file
            threshold: Threshold value for binary mask (default: 0)

        Returns:
            GeoDataFrame with vectorized polygons
        """
        self.logger.info(f"Vectorizing {input_tiff} using rasterio.features")

        with rasterio.open(input_tiff) as src:
            # Read the first band as a NumPy array
            raster = src.read(1)
            transform = src.transform
            crs = src.crs

            # Create a binary mask based on threshold
            mask = raster > threshold

            # Extract shapes and values
            shapes = list(
                features.shapes(mask.astype(np.uint8), mask=mask, transform=transform)
            )

        # Convert shapes to polygons
        polygons = []
        for shape, value in shapes:
            if value == 1:  # Only include shapes where the mask is True
                # Create a polygon from the shape
                polygon = Polygon(shape["coordinates"][0])

                # Simplify the polygon
                if self.simplify_tolerance > 0:
                    polygon = polygon.simplify(self.simplify_tolerance)

                polygons.append(polygon)

        # Create a GeoDataFrame
        gdf = gpd.GeoDataFrame(geometry=polygons, crs=crs)

        self.logger.info(f"Created {len(gdf)} polygons from raster")
        return gdf

    def linestring_to_holefree_polygon(
        self, geom: Union[LineString, MultiLineString]
    ) -> Union[Polygon, MultiPolygon]:
        """
        Converts a LineString or MultiLineString into a hole-free Polygon.

        - Ensures each LineString is closed (first=last coordinate)
        - Polygonizes the result
        - Unions them if multiple polygons result (MultiLineString)
        - Removes any holes (keeps only the exterior boundary)

        Args:
            geom: LineString or MultiLineString geometry

        Returns:
            A single Polygon or MultiPolygon (hole-free)
        """
        if geom.is_empty:
            return geom

        if geom.geom_type == "LineString":
            # Ensure closed
            coords = list(geom.coords)
            if coords[0] != coords[-1]:
                coords.append(coords[0])
            poly = Polygon(coords)

            # Fix invalid geometry if needed
            if not poly.is_valid:
                poly = poly.buffer(0)

            # Remove holes by creating a new polygon from the exterior
            poly = Polygon(poly.exterior)
            return poly

        elif geom.geom_type == "MultiLineString":
            # Polygonize all lines
            polys = list(polygonize(geom))
            if not polys:
                return geom  # or return None

            # Union them into one geometry
            unioned = unary_union(polys)

            # Fix invalid geometry if needed
            if not unioned.is_valid:
                unioned = unioned.buffer(0)

            # Remove holes from the unioned result
            if unioned.geom_type == "Polygon":
                return Polygon(unioned.exterior)
            elif unioned.geom_type == "MultiPolygon":
                new_polys = []
                for p in unioned.geoms:
                    new_polys.append(Polygon(p.exterior))
                return unary_union(new_polys)
            else:
                # Should not happen if polygonize gave only polygons
                return unioned

        else:
            # If it's already a Polygon or MultiPolygon, etc., leave as-is or adapt as needed
            return geom

    def filter_gdf_by_area(
        self, gdf: gpd.GeoDataFrame, min_area: float = None
    ) -> gpd.GeoDataFrame:
        """
        Filter a GeoDataFrame to remove features smaller than a minimum area.

        Args:
            gdf: Input GeoDataFrame
            min_area: Minimum area threshold in square meters (uses self.min_area if None)

        Returns:
            Filtered GeoDataFrame
        """
        min_area = min_area if min_area is not None else self.min_area
        orig_crs = gdf.crs

        # Project to a metric CRS if the current one is geographic
        if orig_crs is None or orig_crs.is_geographic:
            gdf_proj = gdf.to_crs("EPSG:3857")
        else:
            gdf_proj = gdf.copy()

        # Calculate areas and filter
        gdf_proj["area_m2"] = gdf_proj.area
        gdf_proj = gdf_proj[gdf_proj["area_m2"] >= min_area].copy()

        # Convert back to original CRS if needed
        if gdf_proj.crs != orig_crs:
            gdf_proj = gdf_proj.to_crs(orig_crs)

        return gdf_proj.drop(columns=["area_m2"])

    def fix_geom(self, geom):
        """
        Fix geometry issues: convert LineStrings to Polygons, remove holes,
        fix invalid geometries.

        Args:
            geom: Input geometry

        Returns:
            Fixed geometry
        """
        if geom is None or geom.is_empty:
            return geom

        if geom.geom_type in ["LineString", "MultiLineString"]:
            geom = self.linestring_to_holefree_polygon(geom)

        # If it's a Polygon/MultiPolygon, also remove holes
        if geom.geom_type == "Polygon":
            # buffer(0) to fix invalid, then remove holes
            if not geom.is_valid:
                geom = geom.buffer(0)
            geom = Polygon(geom.exterior)

        elif geom.geom_type == "MultiPolygon":
            # Same logic for each sub-polygon
            new_polys = []
            for p in geom.geoms:
                if not p.is_valid:
                    p = p.buffer(0)
                new_polys.append(Polygon(p.exterior))
            geom = unary_union(new_polys)

        return geom

    def load_and_fix_geojson(
        self, geojson_file: str, simplify_tolerance: float = None
    ) -> gpd.GeoDataFrame:
        """
        Load the GeoJSON into a GeoDataFrame, convert LineStrings to Polygons,
        fix invalid geometries, and simplify with the given tolerance.

        Args:
            geojson_file: Path to input GeoJSON file
            simplify_tolerance: Tolerance for simplification (uses self.simplify_tolerance if None)

        Returns:
            Cleaned GeoDataFrame
        """
        simplify_tolerance = (
            simplify_tolerance
            if simplify_tolerance is not None
            else self.simplify_tolerance
        )
        gdf = gpd.read_file(geojson_file)

        # Fix geometries
        gdf["geometry"] = gdf["geometry"].apply(self.fix_geom)

        # Simplify geometries
        gdf["geometry"] = gdf["geometry"].simplify(
            simplify_tolerance, preserve_topology=True
        )

        return gdf

    def clean_and_process_gdf(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Apply geometry cleaning, simplification, orthogonalization, and filtering to a GeoDataFrame.

        Args:
            gdf: Input GeoDataFrame

        Returns:
            Processed GeoDataFrame
        """
        # Fix geometries
        gdf["geometry"] = gdf["geometry"].apply(self.fix_geom)

        # Simplify geometries
        if self.simplify_tolerance > 0:
            gdf["geometry"] = gdf["geometry"].simplify(
                self.simplify_tolerance, preserve_topology=True
            )

        # Orthogonalize if requested
        if self.orthogonalize:
            self.logger.info("Orthogonalizing geometries...")
            gdf = orthogonalize_gdf(gdf)

        # Filter by area
        if self.min_area > 0:
            orig_count = len(gdf)
            gdf = self.filter_gdf_by_area(gdf)
            self.logger.info(
                f"Filtered out {orig_count - len(gdf)} features below {self.min_area} sq meters"
            )

        return gdf

    def convert(
        self, input_tiff: str, output_geojson: str, cleanup_temp: bool = True
    ) -> gpd.GeoDataFrame:
        """
        Convert a GeoTIFF file to a GeoJSON file with cleaned geometries using the specified algorithm.

        Args:
            input_tiff: Path to input GeoTIFF file
            output_geojson: Path to output GeoJSON file
            cleanup_temp: Whether to remove temporary files after processing

        Returns:
            Final GeoDataFrame that was saved to the output file
        """
        # Choose vectorization method based on algorithm
        if self.algorithm == "potrace":
            self.logger.info(f"Using Potrace algorithm for vectorization")
            gdf = self._convert_with_potrace(input_tiff, output_geojson, cleanup_temp)
        else:  # rasterio
            self.logger.info(f"Using rasterio.features for vectorization")
            gdf = self._convert_with_rasterio(input_tiff, output_geojson)

        return gdf

    def _convert_with_potrace(
        self, input_tiff: str, output_geojson: str, cleanup_temp: bool
    ) -> gpd.GeoDataFrame:
        """
        Convert using the Potrace algorithm with temporary files.

        Args:
            input_tiff: Path to input GeoTIFF file
            output_geojson: Path to output GeoJSON file
            cleanup_temp: Whether to clean up temporary files

        Returns:
            Final processed GeoDataFrame
        """
        # Create temporary BMP file
        bmp_file = os.path.join(self.tmp_dir, "temp_mask.bmp")
        temp_geojson = os.path.join(self.tmp_dir, "temp_potrace.geojson")

        try:
            # Convert TIFF to BMP and get transform/CRS
            transform, crs = self.convert_tif_to_bmp(input_tiff, bmp_file)

            # Run Potrace
            self.run_potrace(bmp_file, temp_geojson)

            # Update coordinates from pixel to geo
            self.update_geojson_coords(temp_geojson, transform, crs)

            # Load and process the GeoJSON
            gdf = self.load_and_fix_geojson(temp_geojson)
            gdf = self.clean_and_process_gdf(gdf)

            # Save final result
            gdf.to_file(output_geojson, driver="GeoJSON")
            self.logger.info(f"Final GeoJSON saved as {output_geojson}")

            return gdf

        finally:
            # Clean up temporary files
            if cleanup_temp:
                for temp_file in [bmp_file, temp_geojson]:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        self.logger.info(f"Removed temporary file: {temp_file}")

    def _convert_with_rasterio(
        self, input_tiff: str, output_geojson: str
    ) -> gpd.GeoDataFrame:
        """
        Convert using rasterio.features directly.

        Args:
            input_tiff: Path to input GeoTIFF file
            output_geojson: Path to output GeoJSON file

        Returns:
            Final processed GeoDataFrame
        """
        # Vectorize directly with rasterio
        gdf = self.vectorize_with_rasterio(input_tiff)

        # Apply cleaning and processing
        gdf = self.clean_and_process_gdf(gdf)

        # Save final result
        gdf.to_file(output_geojson, driver="GeoJSON")
        self.logger.info(f"Final GeoJSON saved as {output_geojson}")

        return gdf