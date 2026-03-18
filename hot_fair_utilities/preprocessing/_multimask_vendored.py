"""Multimask generation helpers for building footprint segmentation.

This module provides geometry-to-mask conversion utilities used by
``multimasks_from_polygons.py`` to produce multi-channel training masks
(footprint, boundary, contact) from GeoJSON building polygons.

"""

import logging
import os
from warnings import warn

import geopandas as gpd
import numpy as np
import pandas as pd
import pyproj
import rasterio
import shapely.affinity
import shapely.wkt
from affine import Affine
from fiona._err import CPLE_OpenFailedError
from fiona.errors import DriverError
from rasterio import features
from shapely.geometry import Point, Polygon, mapping, shape
from shapely.geometry.base import BaseGeometry
from shapely.geometry.collection import GeometryCollection
from shapely.ops import cascaded_union

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

try:
    from osgeo import gdal, osr
except Exception:
    gdal = None
    osr = None


# ── File / pairing helpers ──────────────────────────────────────────────


def build_mask_path(mask_dir, chip_path):
    """Build the output mask filename from a chip path.

    Args:
        mask_dir:  Directory where masks will be written.
        chip_path: Full path to the source chip file.

    Returns:
        str: ``<mask_dir>/<chip_basename>.mask.tif``
    """
    basename = os.path.splitext(os.path.basename(chip_path))[0]
    return os.path.join(mask_dir, basename + ".mask.tif")


def pair_chips_and_labels(chip_dir, label_dir):
    """Match chip TIF files to GeoJSON label files by shared basename.

    Args:
        chip_dir:  Directory containing ``<name>.tif`` chip files.
        label_dir: Directory containing ``<name>.geojson`` label files.

    Returns:
        list[tuple[str,str]]: Ordered (chip_path, label_path) pairs.

    Raises:
        FileNotFoundError: If a chip file expected from a label is missing.
    """
    geojson_names = sorted(
        f for f in os.listdir(label_dir) if f.endswith(".geojson")
    )
    pairs = []
    for gj_name in geojson_names:
        stem = os.path.splitext(gj_name)[0]
        chip_path = os.path.join(chip_dir, stem + ".tif")
        if not os.path.exists(chip_path):
            raise FileNotFoundError(f"Missing: required image chip file {chip_path}")
        pairs.append((chip_path, os.path.join(label_dir, gj_name)))
    return pairs


# ── Array layout ────────────────────────────────────────────────────────


def channels_last_to_first(array_hwc):
    """Transpose a [H, W, C] array to [C, H, W].

    Args:
        array_hwc: numpy array with shape (height, width, channels).

    Returns:
        numpy array with shape (channels, height, width).
    """
    return array_hwc.transpose(2, 0, 1)


# ── Input normalisation ────────────────────────────────────────────────


def open_rasterio(im):
    """Ensure *im* is an open rasterio DatasetReader.

    Args:
        im: A file path (str) or an already-open ``rasterio.DatasetReader``.

    Returns:
        rasterio.DatasetReader
    """
    if isinstance(im, str):
        return rasterio.open(im)
    if isinstance(im, rasterio.DatasetReader):
        return im
    raise ValueError(f"{im} is not an accepted image format for rasterio.")


def load_geodataframe(source):
    """Load a GeoDataFrame from *source* (path or pass-through).

    Args:
        source: File path (GeoJSON / CSV with geometry) **or** GeoDataFrame.

    Returns:
        gpd.GeoDataFrame
    """
    if isinstance(source, gpd.GeoDataFrame):
        return source
    if isinstance(source, str):
        if source.lower().endswith("csv"):
            return gpd.read_file(
                source, GEOM_POSSIBLE_NAMES="geometry", KEEP_GEOM_COLUMNS="NO"
            )
        try:
            return gpd.read_file(source)
        except (DriverError, CPLE_OpenFailedError):
            warn(
                f"GeoDataFrame couldn't be loaded: either {source} isn't a "
                "valid path or it isn't a valid vector file. "
                "Returning an empty GeoDataFrame."
            )
            return gpd.GeoDataFrame()
    raise ValueError(f"{source} is not an accepted GeoDataFrame format.")


def load_dataframe(source):
    """Load a DataFrame from *source* (path or pass-through).

    Args:
        source: File path (JSON → GeoDataFrame, CSV → DataFrame) **or**
                an already-loaded ``pd.DataFrame``.

    Returns:
        pd.DataFrame or gpd.GeoDataFrame
    """
    if isinstance(source, pd.DataFrame):
        return source
    if isinstance(source, str):
        if source.lower().endswith("json"):
            return load_geodataframe(source)
        return pd.read_csv(source)
    raise ValueError(f"{source} is not an accepted DataFrame format.")


def ensure_geometry(geom):
    """Normalise *geom* to a Shapely geometry object.

    Args:
        geom: A Shapely BaseGeometry, WKT string, or [x, y] coordinate pair.

    Returns:
        shapely.geometry.base.BaseGeometry
    """
    if isinstance(geom, BaseGeometry):
        return geom
    if isinstance(geom, str):
        return shapely.wkt.loads(geom)
    if isinstance(geom, list) and len(geom) == 2:
        return Point(geom)
    return geom


# ── CRS ────────────────────────────────────────────────────────────────


def normalise_crs(input_crs, return_rasterio=False):
    """Normalise *input_crs* to a ``pyproj.CRS`` (optionally rasterio CRS).

    Args:
        input_crs:       Any CRS representation understood by pyproj.
        return_rasterio: If True, convert the result to a rasterio CRS.

    Returns:
        pyproj.CRS or rasterio.crs.CRS (when *return_rasterio* is True).
    """
    if input_crs is None:
        return None
    out_crs = input_crs if isinstance(input_crs, pyproj.CRS) else pyproj.CRS(input_crs)
    if return_rasterio:
        gdal_version = tuple(int(x) for x in rasterio.__gdal_version__.split(".")[:2])
        wkt = out_crs.to_wkt() if gdal_version >= (3, 0) else out_crs.to_wkt("WKT1_GDAL")
        out_crs = rasterio.crs.CRS.from_wkt(wkt)
    return out_crs


def projection_unit(crs):
    """Return the unit name string of a CRS.

    Args:
        crs: Any CRS representation.

    Returns:
        str or None: e.g. ``"metre"``, ``"degree"``.
    """
    crs = normalise_crs(crs)
    if crs is None:
        return None
    units = [axis.unit_name for axis in crs.axis_info if axis.unit_name]
    return units[-1] if units else None


def vector_projection_unit(vector_file):
    """Return the projection unit for a vector file or GeoDataFrame.

    Args:
        vector_file: Path to a vector file **or** a GeoDataFrame.

    Returns:
        str or None
    """
    return projection_unit(load_geodataframe(vector_file).crs)


def extract_crs(obj):
    """Extract a ``pyproj.CRS`` from a geo-registered object.

    Supports ``gpd.GeoDataFrame``, ``rasterio.DatasetReader``, and
    ``osgeo.gdal.Dataset`` (when GDAL bindings are available).

    Args:
        obj: A geo-registered object.

    Returns:
        pyproj.CRS
    """
    if isinstance(obj, gpd.GeoDataFrame):
        return normalise_crs(obj.crs)
    if isinstance(obj, rasterio.DatasetReader):
        return normalise_crs(obj.crs)
    if gdal is not None and isinstance(obj, gdal.Dataset):
        epsg = int(
            osr.SpatialReference(wkt=obj.GetProjection()).GetAttrValue("AUTHORITY", 1)
        )
        return normalise_crs(epsg)
    raise TypeError(f"Cannot extract CRS from object of type {type(obj)}")


def is_metric_crs(gdf):
    """Return True when the GeoDataFrame's CRS uses metre-based units.

    Args:
        gdf: A GeoDataFrame **or** path to a vector file.

    Returns:
        bool
    """
    unit = str(vector_projection_unit(gdf)).strip().lower()
    return unit in ("meter", "metre", '"meter"', '"metre"', "'meter'", "'metre'")


# ── Affine / coordinate transform ──────────────────────────────────────


def coerce_affine(xform):
    """Convert a list or GDAL-ordered tuple into an ``Affine`` object.

    Args:
        xform: A 6- or 9-element sequence, or an ``Affine`` instance.

    Returns:
        affine.Affine
    """
    if isinstance(xform, Affine):
        return xform
    xform = list(xform)[:6]
    if rasterio.transform.tastes_like_gdal(xform):
        return Affine.from_gdal(*xform)
    return Affine(*xform)


def round_geometry(geom, precision=2):
    """Round a geometry's coordinates to *precision* decimal places.

    Args:
        geom:      Shapely geometry or WKT string.
        precision: Number of decimal places.

    Returns:
        shapely.geometry.base.BaseGeometry
    """
    if isinstance(geom, str):
        geom = shapely.wkt.loads(geom)
    geojson = mapping(geom)
    geojson["coordinates"] = np.round(np.array(geojson["coordinates"]), precision)
    return shape(geojson)


def transform_geometry(geom, raster_src=None, affine_obj=None, inverse=False, precision=None):
    """Apply an affine transform to a geometry (pixel↔geo conversion).

    Args:
        geom:       Shapely geometry or WKT string.
        raster_src: Path / rasterio dataset to derive the affine from.
        affine_obj: Explicit ``Affine`` (or 6/9-element list).
        inverse:    If True, invert the affine before applying.
        precision:  Optional coordinate rounding.

    Returns:
        Same type as *geom* (shapely or WKT string).
    """
    if raster_src is None and affine_obj is None:
        raise ValueError("Either raster_src or affine_obj must be provided.")

    if raster_src is not None:
        if isinstance(raster_src, (str, rasterio.DatasetReader)):
            affine_xform = open_rasterio(raster_src).transform
        elif gdal is not None and isinstance(raster_src, gdal.Dataset):
            affine_xform = Affine.from_gdal(*raster_src.GetGeoTransform())
        else:
            raise TypeError("Unsupported raster_src type for transform_geometry.")
    else:
        affine_xform = affine_obj if isinstance(affine_obj, Affine) else coerce_affine(affine_obj)

    if inverse:
        affine_xform = ~affine_xform

    is_wkt = isinstance(geom, str)
    g = shapely.wkt.loads(geom) if is_wkt else geom
    if not isinstance(g, BaseGeometry):
        raise TypeError("geom must be a Shapely geometry or WKT string.")

    transformed = shapely.affinity.affine_transform(
        g,
        [affine_xform.a, affine_xform.b, affine_xform.d,
         affine_xform.e, affine_xform.xoff, affine_xform.yoff],
    )
    if is_wkt:
        transformed = shapely.wkt.dumps(transformed)
    if precision is not None:
        transformed = round_geometry(transformed, precision=precision)
    return transformed


# ── GeoDataFrame coordinate conversion ──────────────────────────────────


def geo_to_pixel_gdf(gdf, reference_im):
    """Convert georeferenced geometries to pixel coordinates.

    Args:
        gdf:          GeoDataFrame with georeferenced geometries.
        reference_im: Raster path or dataset (provides the affine).

    Returns:
        gpd.GeoDataFrame with pixel-space geometries (crs=None).
    """
    ref = open_rasterio(reference_im)
    inv_affine = ~ref.transform
    out = gdf.copy()
    out["geometry"] = out["geometry"].apply(
        transform_geometry, affine_obj=inv_affine, inverse=False
    )
    out.crs = None
    return out


def pixel_to_geo_gdf(
    df, im_path=None, affine_obj=None, crs=None,
    geom_col="geometry", precision=None, output_path=None,
):
    """Convert pixel-coordinate geometries to georeferenced coordinates.

    Args:
        df:          DataFrame with pixel-space geometries.
        im_path:     Raster path (derives affine + CRS).
        affine_obj:  Explicit affine (required when *im_path* is None).
        crs:         Explicit CRS     (required when *im_path* is None).
        geom_col:    Name of the geometry column.
        precision:   Optional coordinate rounding.
        output_path: If set, save result to GeoJSON or CSV.

    Returns:
        gpd.GeoDataFrame with georeferenced geometries.
    """
    if im_path is not None:
        im = open_rasterio(im_path)
        affine_obj = im.transform
        crs = im.crs
    else:
        if not affine_obj or not crs:
            raise ValueError("If im_path is not provided, affine_obj and crs are required.")
    crs = normalise_crs(crs)
    tmp_df = apply_affine_to_gdf(df, affine_obj, geom_col=geom_col, precision=precision)
    result = gpd.GeoDataFrame(tmp_df)
    result.set_crs(crs, allow_override=True)
    if output_path is not None:
        if output_path.lower().endswith("json"):
            result.to_file(output_path, driver="GeoJSON")
        else:
            result.to_csv(output_path, index=False)
    return result


def apply_affine_to_gdf(gdf, affine_obj, inverse=False, geom_col="geometry", precision=None):
    """Apply an affine transform to every geometry in a GeoDataFrame.

    Args:
        gdf:        GeoDataFrame, or path to JSON/CSV file.
        affine_obj: ``Affine`` instance (or list).
        inverse:    Invert the affine before applying.
        geom_col:   Name of the geometry column.
        precision:  Optional coordinate rounding.

    Returns:
        gpd.GeoDataFrame with transformed geometries (crs=None).
    """
    if isinstance(gdf, str):
        if gdf.lower().endswith("json"):
            gdf = gpd.read_file(gdf)
        elif gdf.lower().endswith("csv"):
            gdf = pd.read_csv(gdf)
        else:
            raise ValueError("The file format is incompatible with this function.")
    if "geometry" not in gdf.columns:
        gdf = gdf.rename(columns={geom_col: "geometry"})
    if not isinstance(gdf["geometry"].iloc[0], Polygon):
        gdf["geometry"] = gdf["geometry"].apply(shapely.wkt.loads)
    gdf["geometry"] = gdf["geometry"].apply(
        transform_geometry, affine_obj=affine_obj, inverse=inverse,
    )
    if precision is not None:
        gdf["geometry"] = gdf["geometry"].apply(round_geometry, precision=precision)
    gdf.crs = None
    return gdf


# ── Reprojection ────────────────────────────────────────────────────────


def reproject_vector(
    input_object, input_crs=None, target_crs=None,
    target_object=None, dest_path=None, resampling_method="cubic",
):
    """Reproject a GeoDataFrame to a new CRS.

    Args:
        input_object:     GeoDataFrame or path to vector file.
        input_crs:        Override CRS for *input_object*.
        target_crs:       Desired output CRS.
        target_object:    Derive *target_crs* from this object's CRS.
        dest_path:        If set, save reprojected data to GeoJSON.
        resampling_method: Ignored (raster-only parameter kept for API compat).

    Returns:
        gpd.GeoDataFrame in *target_crs*.
    """
    del resampling_method

    if isinstance(input_object, str):
        data = load_geodataframe(input_object)
    elif isinstance(input_object, gpd.GeoDataFrame):
        data = input_object
    else:
        raise TypeError("reproject_vector supports GeoDataFrame inputs only.")

    input_crs = normalise_crs(input_crs) if input_crs else normalise_crs(extract_crs(data))

    if target_object is not None and target_crs is None:
        if isinstance(target_object, str):
            target_data = load_geodataframe(target_object)
        elif isinstance(target_object, gpd.GeoDataFrame):
            target_data = target_object
        else:
            raise TypeError("target_object must be a GeoDataFrame or vector filepath.")
        target_crs = extract_crs(target_data)

    if target_crs is not None:
        target_crs = normalise_crs(target_crs)
    else:
        if input_crs is None:
            raise ValueError("An input CRS must be provided by input_data or input_crs.")
        target_crs = data.estimate_utm_crs()
        if target_crs is None:
            return data

    output = data.to_crs(target_crs)
    if dest_path is not None:
        output.to_file(dest_path, driver="GeoJSON")
    return output


# ── Geometry intersection ───────────────────────────────────────────────


def find_internal_intersections(polygons):
    """Compute pairwise intersection geometries among a set of polygons.

    Uses a spatial index to find bounding-box candidates, then computes
    exact intersections only between actual neighbours.

    Args:
        polygons: Iterable of Shapely geometries **or** a GeoSeries.

    Returns:
        Shapely geometry (union of all pairwise intersections), or an
        empty GeometryCollection when there are none.
    """
    gs = polygons if isinstance(polygons, gpd.GeoSeries) else gpd.GeoSeries(polygons).reset_index(drop=True)
    sindex = gs.sindex
    candidates = gs.apply(lambda g: list(sindex.intersection(g.bounds)))
    candidates = candidates.dropna()
    candidates = candidates[candidates.apply(len) > 1]
    if len(candidates) == 0:
        return GeometryCollection()

    candidates.name = "intersectors"
    candidates.index.name = "gs_idx"
    candidates = candidates.reset_index()
    candidates["intersectors"] = candidates.apply(
        lambda row: [i for i in row["intersectors"] if i != row["gs_idx"]], axis=1,
    )
    parts = []
    candidates.apply(
        lambda row: parts.append(
            gs[row["gs_idx"]].intersection(cascaded_union(gs[row["intersectors"]]))
        ),
        axis=1,
    )
    return cascaded_union(parts)


# ── Mask rasterisation ──────────────────────────────────────────────────


def rasterise_geometries(
    df, out_file, reference_im, geom_col, do_transform, shape, burn_value,
):
    """Burn geometries from *df* into a single-band uint8 raster mask.

    Args:
        df:           GeoDataFrame whose *geom_col* holds geometries.
        out_file:     Path to write mask (None to skip writing).
        reference_im: Raster for shape/transform (path or dataset).
        geom_col:     Column name containing geometries.
        do_transform: If True, use the reference image's affine;
                      if False, use an identity affine (pixel coords).
        shape:        Fallback (H, W) when *reference_im* is None.
        burn_value:   Value to burn for each geometry (e.g. 255).

    Returns:
        np.ndarray of shape (H, W), dtype uint8.
    """
    if len(df) == 0 and not out_file:
        return np.zeros(shape=shape, dtype="uint8")

    affine_obj = None if do_transform else Affine(1, 0, 0, 0, 1, 0)

    if reference_im:
        reference_im = open_rasterio(reference_im)
        shape = reference_im.shape
        if do_transform:
            affine_obj = reference_im.transform

    geom_list = list(df[geom_col])
    if len(df) > 0:
        output_arr = features.rasterize(
            shapes=geom_list, fill=0, default_value=burn_value,
            out_shape=shape, transform=affine_obj, dtype="uint8",
        )
    else:
        output_arr = np.zeros(shape=shape, dtype="uint8")

    if out_file:
        meta = reference_im.meta.copy()
        meta.update(count=1, dtype="uint8", nodata=None)
        with rasterio.open(out_file, "w", **meta) as dst:
            dst.write(np.expand_dims(output_arr, axis=0))

    return output_arr


# ── Multimask encoding ──────────────────────────────────────────────────


def onehot_to_sparse_mask(onehot_mask):
    """Convert a one-hot [H, W, C] multimask to sparse [H, W, 1].

    Channel order:  0 = footprint → class 1,
                    1 = boundary  → class 2,
                    2 = contact   → class 3.
    Priority: contact > boundary > footprint (last writer wins).

    Args:
        onehot_mask: np.ndarray of shape (H, W, 3), dtype uint8.

    Returns:
        np.ndarray of shape (H, W, 1), dtype uint8 with class IDs.
    """
    sparse = np.zeros(onehot_mask.shape[:2], dtype=np.uint8)
    sparse[onehot_mask[:, :, 2] > 0] = 3   # contact
    sparse[onehot_mask[:, :, 0] > 0] = 1   # footprint
    sparse[onehot_mask[:, :, 1] > 0] = 2   # boundary
    return np.expand_dims(sparse, axis=-1)


# ── Channel-specific dataframe builders ─────────────────────────────────


def build_interior_df(df, boundary_width, reference_im, meters, geom_col="geometry", out_file=None):
    """Shrink polygons inward to isolate boundary pixels.

    Applies a negative buffer (``-boundary_width``) so that the
    *boundary channel* = footprint_mask − interior_mask.

    Args:
        df:             GeoDataFrame of building polygons.
        boundary_width: Buffer distance (pixels or metres).
        reference_im:   Reference raster for affine.
        meters:         True if *boundary_width* is in metres.
        geom_col:       Geometry column name.
        out_file:       Optional path to save result.

    Returns:
        gpd.GeoDataFrame of shrunk polygons (empty rows removed).
    """
    interior = buffer_geometries(
        df, buffer=-boundary_width, reference_im=reference_im, meters=meters,
    )
    interior = interior[~interior.is_empty]
    if out_file:
        interior.to_file(out_file)
    return interior


def build_contact_df(df, contact_spacing, reference_im, meters, geom_col):
    """Identify zones where neighbouring buildings are in close contact.

    Expands each polygon by *contact_spacing*, then finds pairwise
    overlaps between the expanded polygons of different buildings.

    Args:
        df:              GeoDataFrame of building polygons.
        contact_spacing: Expansion distance (pixels or metres).
        reference_im:    Reference raster for affine.
        meters:          True if *contact_spacing* is in metres.
        geom_col:        Geometry column name.

    Returns:
        gpd.GeoDataFrame of contact-zone geometries (may be empty).
    """
    df = df.copy()
    df["t_index"] = range(len(df))
    expanded = buffer_geometries(df, buffer=contact_spacing, reference_im=reference_im)
    joined = expanded.overlay(df, how="intersection")
    joined = joined[joined["t_index_1"] != joined["t_index_2"]]
    joined = joined[~joined.is_empty]
    joined = joined[["t_index_1", "t_index_2", "geometry"]]
    if len(joined) == 0:
        return joined

    def _lookup(series, idx_col):
        return joined.apply(
            lambda row: expanded.loc[expanded["t_index"] == row[idx_col], "geometry"].values[0],
            axis=1,
        )

    b1 = gpd.GeoSeries(_lookup(joined, "t_index_1"), crs=joined.crs)
    b2 = gpd.GeoSeries(_lookup(joined, "t_index_2"), crs=joined.crs)
    contact_geoms = b1.intersection(b2, align=True)

    return gpd.GeoDataFrame(
        {"t1": joined["t_index_1"], "t2": joined["t_index_2"], "geometry": contact_geoms},
        crs=joined.crs,
    )


# ── Geometry buffering ──────────────────────────────────────────────────


def buffer_geometries(df, buffer, meters=False, reference_im=None, geom_col="geometry", affine_obj=None):
    """Buffer all geometries, handling pixel↔geo conversions as needed.

    The function converts to an appropriate coordinate space for
    buffering, applies the buffer, then converts back to the original
    CRS so downstream callers see no CRS change.

    Args:
        df:           GeoDataFrame of geometries.
        buffer:       Buffer distance (positive = expand, negative = shrink).
        meters:       If True, buffer in metric space.
        reference_im: Reference raster for affine transforms.
        geom_col:     Geometry column name.
        affine_obj:   Explicit affine (used when reference_im is None).

    Returns:
        gpd.GeoDataFrame with buffered geometries.
    """
    df = df[~df.is_empty]
    if len(df) == 0:
        return df.copy()

    if reference_im is not None:
        reference_im = open_rasterio(reference_im)

    orig_crs = normalise_crs(df.crs) if hasattr(df, "crs") else None

    if not meters:
        if hasattr(df, "crs") and reference_im is not None:
            work_df = geo_to_pixel_gdf(df.copy(), reference_im)
        elif hasattr(df, "crs") and reference_im is None:
            work_df = apply_affine_to_gdf(df.copy(), affine_obj=affine_obj, inverse=True)
        else:
            work_df = df.copy()
    else:
        if hasattr(df, "crs"):
            work_df = df.copy() if is_metric_crs(df) else reproject_vector(df.copy())
        else:
            if reference_im is not None:
                work_df = pixel_to_geo_gdf(df.copy(), im_path=reference_im)
            else:
                raise ValueError(
                    "meters=True requires either a GeoDataFrame with CRS or a reference_im."
                )

    work_df[geom_col] = work_df[geom_col].apply(lambda g: g.buffer(buffer))
    work_df = work_df.explode(ignore_index=True)

    work_crs = normalise_crs(getattr(work_df, "crs", None))
    if work_crs != orig_crs:
        if orig_crs is not None and work_crs is not None:
            buffered = work_df.to_crs(orig_crs.to_wkt())
        elif orig_crs is None:
            buffered = geo_to_pixel_gdf(work_df, reference_im)
        else:
            buffered = pixel_to_geo_gdf(
                work_df, im_path=reference_im, affine_obj=affine_obj, crs=orig_crs,
            )
    else:
        buffered = work_df

    return buffered


# ── Main entry point ────────────────────────────────────────────────────


def dataframe_to_pixel_mask(
    df, channels=("footprint",), out_file=None, reference_im=None,
    geom_col="geometry", do_transform=None, affine_obj=None,
    shape=(900, 900), out_type="int", burn_value=255, **kwargs,
):
    """Convert a GeoDataFrame of building polygons to a multi-channel pixel mask.

    Generates one mask channel per entry in *channels*:
      - ``"footprint"``: filled building polygons
      - ``"boundary"``:  footprint minus negatively-buffered interior
      - ``"contact"``:   zones where expanded neighbours overlap

    Args:
        df:           GeoDataFrame of building polygons.
        channels:     Sequence of channel names to generate.
        out_file:     Path to write the stacked mask (None to skip).
        reference_im: Reference raster for shape and affine.
        geom_col:     Geometry column name.
        do_transform: Whether to apply geo→pixel transform.
        affine_obj:   Explicit affine (overrides reference_im).
        shape:        Fallback (H, W) when reference_im is None.
        out_type:     Output dtype hint (default ``"int"``).
        burn_value:   Value burnt for each geometry (default 255).
        **kwargs:     ``meters`` (bool), ``boundary_width`` (int),
                      ``contact_spacing`` (int).

    Returns:
        np.ndarray of shape (H, W, len(channels)), dtype uint8.
    """
    if isinstance(channels, str):
        channels = [channels]

    if out_file and not reference_im:
        raise ValueError("reference_im is required when saving to out_file.")

    meters = kwargs.get("meters", False)

    # Clean geometries with a zero-buffer pass.
    df = buffer_geometries(df, 0, meters=meters, reference_im=reference_im)

    mask_dict = {}

    if "footprint" in channels:
        mask_dict["footprint"] = rasterise_geometries(
            df=df, reference_im=reference_im, geom_col=geom_col,
            do_transform=do_transform, shape=shape,
            burn_value=burn_value, out_file=None,
        )

    if "boundary" in channels:
        try:
            interior = build_interior_df(
                df, geom_col=geom_col, reference_im=reference_im,
                meters=kwargs.get("meters", False),
                boundary_width=kwargs.get("boundary_width", 3),
            )
            interior_mask = rasterise_geometries(
                df=interior, reference_im=reference_im, geom_col=geom_col,
                do_transform=do_transform, shape=shape,
                burn_value=burn_value, out_file=None,
            )
            mask_dict["boundary"] = mask_dict["footprint"] - interior_mask
        except KeyError:
            log.info("Could not compute boundary channel (KeyError), using zeros.")
            mask_dict["boundary"] = np.zeros(shape)

    if "contact" in channels:
        try:
            contacts = build_contact_df(
                df, geom_col=geom_col, reference_im=reference_im,
                meters=kwargs.get("meters", False),
                contact_spacing=kwargs.get("contact_spacing", 8),
            )
            mask_dict["contact"] = rasterise_geometries(
                df=contacts, reference_im=reference_im, geom_col=geom_col,
                do_transform=do_transform, shape=shape,
                burn_value=burn_value, out_file=None,
            )
        except KeyError:
            log.info("Could not compute contact channel (KeyError), using zeros.")
            mask_dict["contact"] = np.zeros(shape)

    output_arr = np.stack([mask_dict[c] for c in channels], axis=-1)

    if reference_im:
        reference_im = open_rasterio(reference_im)
    if out_file:
        meta = reference_im.meta.copy()
        meta.update(count=output_arr.shape[-1], dtype="uint8")
        with rasterio.open(out_file, "w", **meta) as dst:
            for c in range(1, 1 + output_arr.shape[-1]):
                dst.write(output_arr[:, :, c - 1], indexes=c)

    return output_arr


# ── Transform inference ─────────────────────────────────────────────────


def should_transform(df, reference_im, affine_obj):
    """Infer whether a geo→pixel transform is needed.

    Returns True when *df* carries a CRS **and** a reference image or
    affine is available to perform the transform.

    Args:
        df:           GeoDataFrame (may or may not have ``crs``).
        reference_im: Reference raster (or None).
        affine_obj:   Explicit affine (or None).

    Returns:
        bool
    """
    crs = getattr(df, "crs", None)
    if not crs:
        return False
    return reference_im is not None or affine_obj is not None
