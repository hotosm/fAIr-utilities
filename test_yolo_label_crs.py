"""Regression test for #48 — YOLO labels collapse to wrong pixels on CRS mismatch.

Verifies that reproject_coordinates() makes label normalization correct when the label
GeoJSON and the chip are in different coordinate reference systems.

Note: importing hot_fair_utilities pulls in rasterio/pyproj (project dependencies), so this
runs under the project's normal test environment / CI.
"""
import pytest

pyproj = pytest.importorskip("pyproj")
from pyproj import Transformer

from hot_fair_utilities.preprocessing.yolo_v8.utils import (
    convert_coordinates,
    flatten_list,
    reproject_coordinates,
)

# A small chip in EPSG:4326, as get_geo_data() would report it.
GEO_DICT = {
    "crs": "EPSG:4326",
    "left": 45.3200, "right": 45.3210, "top": 2.0410, "bottom": 2.0400,
    "width": 0.0010, "height": 0.0010,
}
# A building polygon inside the chip, expressed in the chip's CRS (4326).
POLY_4326 = [[
    [45.3203, 2.0407], [45.3206, 2.0407], [45.3206, 2.0404], [45.3203, 2.0404], [45.3203, 2.0407],
]]


def _deep(poly):
    return [[list(pt) for pt in ring] for ring in poly]


def _to_3857(poly):
    tf = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    return [[list(tf.transform(x, y)) for (x, y) in ring] for ring in poly]


def _pct_on_boundary(coords):
    flat = flatten_list(coords)
    return sum(1 for v in flat if v in (0, 1)) / len(flat)


def test_matched_crs_is_correct():
    out = convert_coordinates(_deep(POLY_4326), GEO_DICT)
    assert _pct_on_boundary(out) == 0.0
    assert out[0][0] == [0.3, 0.3]


def test_mismatched_crs_collapses_without_reprojection():
    # Reproduces the bug: 3857 label points against a 4326 chip collapse to 0/1.
    out = convert_coordinates(_to_3857(POLY_4326), GEO_DICT)
    assert _pct_on_boundary(out) == 1.0  # every point pinned to a boundary -> useless labels


def test_reprojection_fixes_collapse():
    # The fix: reproject labels into the chip CRS first; result matches the matched-CRS case.
    reproj = reproject_coordinates(_to_3857(POLY_4326), "EPSG:3857", GEO_DICT["crs"])
    out = convert_coordinates(reproj, GEO_DICT)
    expected = convert_coordinates(_deep(POLY_4326), GEO_DICT)
    assert _pct_on_boundary(out) == 0.0
    for got, exp in zip(flatten_list(out), flatten_list(expected)):
        assert abs(got - exp) < 1e-3


def test_reproject_is_noop_when_crs_match():
    poly = _deep(POLY_4326)
    assert reproject_coordinates(poly, "EPSG:4326", "EPSG:4326") == poly
