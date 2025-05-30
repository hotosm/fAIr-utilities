"""
OSM data downloader using HOT Raw Data API.

This module provides functionality to download OpenStreetMap data
via the Humanitarian OpenStreetMap Team (HOT) Raw Data API.
"""

import asyncio
import io
import json
import os
import zipfile
from typing import Any, Dict, List, Optional, Union

import aiohttp
import geopandas as gpd
try:
    from shapely.ops import unary_union
except ImportError:
    from shapely.ops import cascaded_union as unary_union

from ..utils import get_geometry, split_geojson_by_tiles


def detect_and_ensure_4326_geometry(geojson: Union[str, dict]) -> Dict[str, Any]:
    """
    Detect CRS from GeoJSON, convert to EPSG:4326 if needed, and union all geometries.

    Args:
        geojson: GeoJSON file path, string, or dictionary

    Returns:
        Single unioned GeoJSON geometry in EPSG:4326
    """
    if isinstance(geojson, str):
        if os.path.exists(geojson):
            gdf = gpd.read_file(geojson)
        else:
            try:
                geojson_data = json.loads(geojson)
                if "features" in geojson_data:
                    gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
                else:
                    gdf = gpd.GeoDataFrame(geometry=[gpd.GeoSeries.from_json(geojson)[0]])
            except json.JSONDecodeError:
                raise ValueError(f"Invalid GeoJSON string provided")
    else:
        if "features" in geojson:
            gdf = gpd.GeoDataFrame.from_features(geojson["features"])
        else:
            gdf = gpd.GeoDataFrame(geometry=[gpd.GeoSeries.from_json(json.dumps(geojson))[0]])

    if gdf.crs is None:
        print("Warning: No CRS found in GeoJSON. Assuming EPSG:4326 (WGS84).")
        gdf.set_crs(epsg=4326, inplace=True)
    elif gdf.crs.to_epsg() != 4326:
        original_crs = gdf.crs.to_epsg()
        print(f"Converting GeoJSON from EPSG:{original_crs} to EPSG:4326 for API compatibility...")
        gdf = gdf.to_crs(epsg=4326)

    unioned_geometry = unary_union(gdf.geometry.values)
    return (gpd.GeoSeries([unioned_geometry]).set_crs(epsg=4326).__geo_interface__)


def reproject_geojson(geojson_data: Dict[str, Any], target_crs: str) -> Dict[str, Any]:
    """
    Reproject GeoJSON data to the specified CRS.

    Args:
        geojson_data (dict): GeoJSON data to reproject
        target_crs (str): Target CRS (e.g., "4326" or "3857")

    Returns:
        dict: Reprojected GeoJSON data
    """
    # Skip reprojection if target is already 4326 (which is what the API returns)
    if target_crs == "4326":
        return geojson_data

    # Create a GeoDataFrame from the GeoJSON
    gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])

    # Set the CRS to 4326 (the CRS of the data from the API)
    gdf.set_crs(epsg=4326, inplace=True)

    # Reproject to the target CRS
    gdf = gdf.to_crs(epsg=int(target_crs))

    # Convert back to GeoJSON
    reprojected_geojson = json.loads(gdf.to_json())

    # Add CRS information to the GeoJSON
    reprojected_geojson["crs"] = {
        "type": "name",
        "properties": {"name": f"urn:ogc:def:crs:EPSG::{target_crs}"}
    }

    return reprojected_geojson


class RawDataAPI:
    """
    A client for interacting with the Humanitarian OpenStreetMap Team (HOT) Raw Data API.
    """

    def __init__(self, base_api_url: str = "https://api-prod.raw-data.hotosm.org/v1"):
        """
        Initialize the RawDataAPI with a base API URL.

        Args:
            base_api_url (str): Base URL for the Raw Data API.
                                Defaults to HOT's production API.
        """
        self.BASE_API_URL = base_api_url
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Referer": "fair-utilities-python-lib",
        }

    async def request_snapshot(
        self, geometry: Dict[str, Any], feature_type: str = "building"
    ) -> Dict[str, Any]:
        """
        Request a snapshot of OSM data for a given geometry.

        Args:
            geometry (dict): GeoJSON geometry to query
            feature_type (str): Type of features to download. Defaults to "building"

        Returns:
            dict: API response containing task tracking information
        """

        payload = {
            "fileName": "fair-utilities",
            "geometry": geometry,
            "filters": {"tags": {"all_geometry": {"join_or": {feature_type: []}}}},
            "geometryType": ["polygon"],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_API_URL}/snapshot/",
                data=json.dumps(payload),
                headers=self.headers,
            ) as response:
                response_data = await response.json()
                try:
                    response.raise_for_status()
                except Exception as ex:
                    error_message = json.dumps(response_data)
                    raise Exception(f"Error: {error_message}") from ex
                return response_data

    async def poll_task_status(self, task_link: str) -> Dict[str, Any]:
        """
        Poll the API to check the status of a submitted task.

        Args:
            task_link (str): Task tracking URL from the snapshot request

        Returns:
            dict: Task status details
        """
        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(
                    url=f"{self.BASE_API_URL}{task_link}", headers=self.headers
                ) as response:
                    response.raise_for_status()
                    res = await response.json()
                    if res["status"] in ["SUCCESS", "FAILED"]:
                        return res
                    await asyncio.sleep(2)

    async def download_snapshot(
        self,
        download_url: str,
    ) -> Dict[str, Any]:
        """
        Download the snapshot data from the provided URL.

        Args:
            download_url (str): URL to download the data

        Returns:
            dict: Parsed GeoJSON data
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url=download_url, headers=self.headers) as response:
                response.raise_for_status()
                data = await response.read()
                with zipfile.ZipFile(io.BytesIO(data), "r") as zip_ref:
                    with zip_ref.open("fair-utilities.geojson") as file:
                        return json.load(file)

    async def last_updated(self) -> str:
        """
        Get the last updated date from the API status endpoint.

        Returns:
            str: The last updated date.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_API_URL}/status", headers=self.headers
            ) as response:
                response_data = await response.json()
                try:
                    response.raise_for_status()
                except Exception as ex:
                    error_message = json.dumps(response_data)
                    raise Exception(f"Error: {error_message}") from ex
                return response_data["lastUpdated"]


async def download_osm_data(
    geojson: Optional[Union[str, dict]] = None,
    bbox: Optional[List[float]] = None,
    api_url: str = "https://api-prod.raw-data.hotosm.org/v1",
    feature_type: str = "building",
    dump: bool = False,
    out: str = None,
    split: bool = False,
    split_prefix: str = "OAM",
    crs: str = "4326",
) -> Union[Dict[str, Any], str]:
    """
    Main async function to download OSM data for a given geometry.

    Args:
        geojson (str|dict): GeoJSON file path, string, or dictionary
        bbox (list): Bounding box coordinates [xmin, ymin, xmax, ymax]
        api_url (str): Base API URL
        feature_type (str): Type of features to download
        dump (bool): Whether to save the result to a file
        out (str): Output directory for saving files
        split (bool): Whether to split the output by tiles
        split_prefix (str): Prefix for split files
        crs (str): Coordinate reference system for output data (4326 or 3857)

    Returns:
        dict: Downloaded GeoJSON data or output path if dump=True
    """
    # Handle input with bbox or geojson
    if geojson is not None:
        # Detect CRS and convert to 4326 for API compatibility
        geometry = detect_and_ensure_4326_geometry(geojson)
    else:
        # For bbox, assume it's in EPSG:4326 as that's the common format
        geometry = get_geometry(None, bbox)

    api = RawDataAPI(api_url)
    print("OSM Data Last Updated : ", await api.last_updated())
    task_response = await api.request_snapshot(geometry, feature_type)
    task_link = task_response.get("track_link")

    if not task_link:
        raise RuntimeError("No task link found in API response")

    result = await api.poll_task_status(task_link)

    if result["status"] == "SUCCESS" and result["result"].get("download_url"):
        download_url = result["result"]["download_url"]
        result_geojson = await api.download_snapshot(download_url)

        # Reproject if needed (API returns in 4326)
        if crs != "4326":
            print(f"Reprojecting output from EPSG:4326 to EPSG:{crs}...")
            result_geojson = reproject_geojson(result_geojson, crs)

        if dump and out:
            os.makedirs(out, exist_ok=True)
            output_path = os.path.join(out, "osm-result.geojson")
            print(f"Dumping GeoJSON data (EPSG:{crs}) to file: {output_path}")

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result_geojson, f)

            if split:
                split_dir = os.path.join(out, "split")
                print(f"Splitting GeoJSON with respect to tiles, saving to: {split_dir}")
                os.makedirs(split_dir, exist_ok=True)
                split_geojson_by_tiles(
                    output_path,
                    geojson,
                    os.path.join(out, "split"),
                    prefix=split_prefix,
                )
            return out

        return result_geojson

    raise RuntimeError(f"Task failed with status: {result['status']}")
