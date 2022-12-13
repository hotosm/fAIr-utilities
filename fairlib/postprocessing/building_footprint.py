import collections

from geopandas import GeoSeries
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid

from .utils import extract_contours, featurize, opening, parents_in_hierarchy, simplify

CRS = "EPSG:4326"


class BuildingExtract(object):
    def __init__(self, kernel_opening=20, simplify_threshold=0.01):
        """Adapted from: https://github.com/mapbox/robosat"""
        self.kernel_opening = kernel_opening
        self.simplify_threshold = simplify_threshold
        self.features = []

    def extract(self, tile, mask):
        mask = opening(mask, self.kernel_opening)
        multipolygons, hierarchy = extract_contours(mask)

        if hierarchy is None:
            return

        assert (
            len(hierarchy) == 1
        ), "always single hierarchy for all polygons in multipolygon"
        hierarchy = hierarchy[0]

        assert len(multipolygons) == len(hierarchy), "polygons and hierarchy in sync"

        polygons = [
            simplify(polygon, self.simplify_threshold) for polygon in multipolygons
        ]

        # All child ids in hierarchy tree, keyed by root id.
        features = collections.defaultdict(set)

        for i, (polygon, _) in enumerate(zip(polygons, hierarchy)):
            if len(polygon) < 3:
                continue

            ancestors = list(parents_in_hierarchy(i, hierarchy))

            # Only handles polygons with a nesting of two levels for now => no multipolygons.
            if len(ancestors) > 1:
                continue

            # A single mapping: i => {i} implies single free-standing polygon, no inner rings.
            # Otherwise: i => {i, j, k, l} implies: outer ring i, inner rings j, k, l.
            root = ancestors[-1] if ancestors else i

            features[root].add(i)

        for outer, inner in features.items():
            rings = [featurize(tile, polygons[outer], mask.shape[:2])]

            # In mapping i => {i, ..} i is not a child.
            children = inner.difference(set([outer]))

            for child in children:
                rings.append(featurize(tile, polygons[child], mask.shape[:2]))

            feature = make_valid(
                unary_union([make_valid(Polygon(ring)) for ring in rings])
            )

            if type(feature) == MultiPolygon:
                for polygon in feature.geoms:
                    if type(polygon) == Polygon and polygon.area > 0:
                        self.features.append(polygon)
            elif type(feature) == Polygon:
                self.features.append(feature)

    def save(self, out):
        GeoSeries(self.features).set_crs(CRS).to_file(out)
