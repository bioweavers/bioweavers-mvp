import geopandas as gpd
from shapely.geometry import box
import pytest

from src.geometry import get_quadrangles_intersecting_bbox


def _make_boundary():
    boundary_geom = box(-120.0, 34.0, -119.5, 34.5)
    return gpd.GeoDataFrame({"geometry": [boundary_geom]}, crs=4326)


def _make_quads():
    return gpd.GeoDataFrame(
        {
            "quad_id": [101, 102, 103],
            "quad_name": ["Alpha", "Bravo", "Charlie"],
            "geometry": [
                box(-120.2, 34.2, -119.9, 34.6),  # intersects
                box(-119.7, 33.8, -119.3, 34.1),  # intersects
                box(-121.0, 35.0, -120.5, 35.5),  # no
            ],
        },
        crs=4326,
    )


def test_quads_intersect_bbox_infers_columns():
    boundary = _make_boundary()
    quads = _make_quads()

    result = get_quadrangles_intersecting_bbox(boundary, quads)

    assert list(result["quad_id"]) == [101, 102]
    assert list(result["quad_name"]) == ["Alpha", "Bravo"]


def test_quads_intersect_bbox_explicit_id_column():
    boundary = _make_boundary()
    quads = _make_quads().rename(columns={"quad_id": "QUAD_CODE"})

    result = get_quadrangles_intersecting_bbox(
        boundary,
        quads,
        id_col="QUAD_CODE",
        name_col="quad_name",
    )

    assert list(result["quad_id"]) == [101, 102]


def test_quads_intersect_bbox_missing_id_column_raises():
    boundary = _make_boundary()
    quads = _make_quads().drop(columns=["quad_id"])

    with pytest.raises(ValueError):
        get_quadrangles_intersecting_bbox(boundary, quads)
