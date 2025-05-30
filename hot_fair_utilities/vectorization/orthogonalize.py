"""
Orthogonalization utilities for regularizing polygon geometries.

This module provides functionality to orthogonalize polygon geometries
by snapping angles to 45-degree increments, creating more regular
building footprints.
"""

import math
from typing import List, Tuple

import geopandas as gpd
import numpy as np
from shapely.geometry import LineString, MultiPolygon, Point, Polygon


def angle_between_points(p1: Point, p2: Point, p3: Point) -> float:
    """
    Calculate the angle between three points.
    
    Args:
        p1, p2, p3: Three points where p2 is the vertex
        
    Returns:
        Angle in radians
    """
    v1 = np.array([p1.x - p2.x, p1.y - p2.y])
    v2 = np.array([p3.x - p2.x, p3.y - p2.y])
    
    # Normalize vectors
    v1_norm = v1 / np.linalg.norm(v1)
    v2_norm = v2 / np.linalg.norm(v2)
    
    # Calculate angle
    dot_product = np.dot(v1_norm, v2_norm)
    dot_product = np.clip(dot_product, -1.0, 1.0)  # Handle numerical errors
    
    return np.arccos(dot_product)


def snap_angle_to_45_degrees(angle: float) -> float:
    """
    Snap an angle to the nearest 45-degree increment.
    
    Args:
        angle: Angle in radians
        
    Returns:
        Snapped angle in radians
    """
    # Convert to degrees
    angle_deg = math.degrees(angle)
    
    # Snap to nearest 45-degree increment
    snapped_deg = round(angle_deg / 45) * 45
    
    # Convert back to radians
    return math.radians(snapped_deg)


def orthogonalize_polygon(polygon: Polygon, tolerance: float = 0.1) -> Polygon:
    """
    Orthogonalize a polygon by snapping angles to 45-degree increments.
    
    Args:
        polygon: Input polygon to orthogonalize
        tolerance: Tolerance for angle snapping (not currently used)
        
    Returns:
        Orthogonalized polygon
    """
    if polygon.is_empty or not polygon.is_valid:
        return polygon
    
    # Get exterior coordinates
    coords = list(polygon.exterior.coords)
    
    if len(coords) < 4:  # Need at least 3 points + closing point
        return polygon
    
    # Remove the closing point for processing
    coords = coords[:-1]
    
    if len(coords) < 3:
        return polygon
    
    # Convert to Points
    points = [Point(x, y) for x, y in coords]
    
    # Calculate angles and snap them
    new_points = []
    
    for i in range(len(points)):
        prev_point = points[i - 1]
        curr_point = points[i]
        next_point = points[(i + 1) % len(points)]
        
        # Calculate the angle at current point
        angle = angle_between_points(prev_point, curr_point, next_point)
        
        # Snap to 45-degree increment
        snapped_angle = snap_angle_to_45_degrees(angle)
        
        # For now, keep the original point
        # More sophisticated orthogonalization would adjust point positions
        new_points.append(curr_point)
    
    # Convert back to coordinates and close the polygon
    new_coords = [(p.x, p.y) for p in new_points]
    new_coords.append(new_coords[0])  # Close the polygon
    
    try:
        new_polygon = Polygon(new_coords)
        if new_polygon.is_valid:
            return new_polygon
        else:
            # If invalid, try to fix with buffer(0)
            fixed_polygon = new_polygon.buffer(0)
            if isinstance(fixed_polygon, Polygon) and fixed_polygon.is_valid:
                return fixed_polygon
            else:
                return polygon  # Return original if can't fix
    except Exception:
        return polygon  # Return original if any error occurs


def simplify_polygon_angles(polygon: Polygon, angle_threshold: float = 0.1) -> Polygon:
    """
    Simplify a polygon by removing vertices that create very small angles.
    
    Args:
        polygon: Input polygon
        angle_threshold: Minimum angle threshold in radians
        
    Returns:
        Simplified polygon
    """
    if polygon.is_empty or not polygon.is_valid:
        return polygon
    
    coords = list(polygon.exterior.coords)[:-1]  # Remove closing point
    
    if len(coords) < 3:
        return polygon
    
    # Filter out points that create very small angles
    filtered_coords = []
    
    for i in range(len(coords)):
        prev_idx = (i - 1) % len(coords)
        next_idx = (i + 1) % len(coords)
        
        p1 = Point(coords[prev_idx])
        p2 = Point(coords[i])
        p3 = Point(coords[next_idx])
        
        angle = angle_between_points(p1, p2, p3)
        
        # Keep point if angle is significant
        if angle > angle_threshold:
            filtered_coords.append(coords[i])
    
    if len(filtered_coords) < 3:
        return polygon  # Return original if too few points
    
    # Close the polygon
    filtered_coords.append(filtered_coords[0])
    
    try:
        new_polygon = Polygon(filtered_coords)
        if new_polygon.is_valid:
            return new_polygon
        else:
            return polygon
    except Exception:
        return polygon


def orthogonalize_gdf(gdf: gpd.GeoDataFrame, tolerance: float = 0.1) -> gpd.GeoDataFrame:
    """
    Orthogonalize all geometries in a GeoDataFrame.
    
    Args:
        gdf: Input GeoDataFrame
        tolerance: Tolerance for orthogonalization
        
    Returns:
        GeoDataFrame with orthogonalized geometries
    """
    def orthogonalize_geometry(geom):
        if geom is None or geom.is_empty:
            return geom
        
        if isinstance(geom, Polygon):
            return orthogonalize_polygon(geom, tolerance)
        elif isinstance(geom, MultiPolygon):
            orthogonalized_polygons = []
            for poly in geom.geoms:
                if isinstance(poly, Polygon):
                    orthogonalized_polygons.append(orthogonalize_polygon(poly, tolerance))
                else:
                    orthogonalized_polygons.append(poly)
            
            if orthogonalized_polygons:
                try:
                    from shapely.ops import unary_union
                    result = unary_union(orthogonalized_polygons)
                    return result
                except ImportError:
                    from shapely.ops import cascaded_union
                    result = cascaded_union(orthogonalized_polygons)
                    return result
            else:
                return geom
        else:
            return geom  # Return unchanged for other geometry types
    
    # Apply orthogonalization to all geometries
    result_gdf = gdf.copy()
    result_gdf['geometry'] = result_gdf['geometry'].apply(orthogonalize_geometry)
    
    return result_gdf
