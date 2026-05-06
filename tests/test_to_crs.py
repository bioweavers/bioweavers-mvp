"""Tests for src.geometry.safe_to_crs.

safe_to_crs is the defensive wrapper around GeoDataFrame.to_crs that raises
loudly on the four ways a reprojection can silently produce garbage:
  1. Source CRS is missing.
  2. Input contains null or empty geometries.
  3. Input bounds fall outside the target CRS's area of use.
  4. Reprojection produces null/empty/invalid output despite (1)-(3) passing.
"""

from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Polygon, box

from src.geometry import safe_to_crs


SAMPLE_GEOJSON = Path(__file__).parents[1] / "fixtures" / "sample_boundary.geojson"


# --- fixtures --------------------------------------------------------------

@pytest.fixture
def california_gdf():
    """A small polygon inside California, in WGS84 lon/lat.

    Kept off EPSG:3310's central meridian (-120°W) so projected x-coordinates
    are clearly non-zero — useful for the magnitude assertion in
    test_reprojects_california_to_3310.
    """
    return gpd.GeoDataFrame(
        {"geometry": [box(-119.0, 34.0, -118.5, 34.5)]},
        crs="EPSG:4326",
    )


@pytest.fixture
def texas_gdf():
    """A polygon in Texas — outside EPSG:3310's area of use."""
    return gpd.GeoDataFrame(
        {"geometry": [box(-98.0, 30.0, -97.5, 30.5)]},
        crs="EPSG:4326",
    )


@pytest.fixture
def sample_boundary_gdf():
    """The real sample boundary shipped with the repo."""
    if not SAMPLE_GEOJSON.exists():
        pytest.skip(f"sample boundary not found at {SAMPLE_GEOJSON}")
    return gpd.read_file(SAMPLE_GEOJSON)


# --- happy path ------------------------------------------------------------

def test_reprojects_california_to_3310(california_gdf):
    """A WGS84 polygon inside California reprojects cleanly to CA Albers."""
    out = safe_to_crs(california_gdf, 3310)

    assert out.crs.to_epsg() == 3310
    assert len(out) == len(california_gdf)
    assert out.geometry.is_valid.all()
    assert not out.geometry.is_empty.any()
    # CA Albers is in meters; coordinates should be on the order of 1e5-1e6.
    xmin, _, xmax, _ = out.total_bounds
    assert 1e4 < abs(xmin) < 1e7
    assert 1e4 < abs(xmax) < 1e7


def test_reprojects_sample_boundary_to_3310(sample_boundary_gdf):
    """The real sample boundary (assumed to be in CA) reprojects cleanly."""
    out = safe_to_crs(sample_boundary_gdf, 3310)

    assert out.crs.to_epsg() == 3310
    assert len(out) == len(sample_boundary_gdf)
    assert out.geometry.is_valid.all()
    assert not out.geometry.is_empty.any()


def test_roundtrip_preserves_geometry(california_gdf):
    """4326 -> 3310 -> 4326 returns coordinates close to the original."""
    out = safe_to_crs(safe_to_crs(california_gdf, 3310), 4326)

    orig = california_gdf.total_bounds
    final = out.total_bounds
    # Sub-meter precision is plenty for a sanity check.
    assert all(abs(a - b) < 1e-6 for a, b in zip(orig, final))


# --- failure modes ---------------------------------------------------------

def test_raises_on_empty_gdf():
    empty = gpd.GeoDataFrame({"geometry": []}, crs="EPSG:4326")
    with pytest.raises(ValueError, match="empty"):
        safe_to_crs(empty, 3310)


def test_raises_on_missing_crs(california_gdf):
    no_crs = california_gdf.copy()
    no_crs.crs = None
    with pytest.raises(ValueError, match="no CRS"):
        safe_to_crs(no_crs, 3310)


def test_raises_on_null_geometry():
    has_null = gpd.GeoDataFrame(
        {"geometry": [box(-119.0, 34.0, -118.5, 34.5), None]},
        crs="EPSG:4326",
    )
    # Error message is "Input has N null and M empty geometries..." — match on
    # the count + keyword so we verify the function counted nulls correctly.
    with pytest.raises(ValueError, match=r"1 null and 0 empty"):
        safe_to_crs(has_null, 3310)


def test_raises_on_empty_geometry():
    has_empty = gpd.GeoDataFrame(
        {"geometry": [box(-119.0, 34.0, -118.5, 34.5), Polygon()]},
        crs="EPSG:4326",
    )
    with pytest.raises(ValueError, match=r"0 null and 1 empty"):
        safe_to_crs(has_empty, 3310)


def test_raises_when_bounds_outside_area_of_use(texas_gdf):
    """Texas is outside EPSG:3310's California-only area of use."""
    with pytest.raises(ValueError, match="outside EPSG:3310 area of use"):
        safe_to_crs(texas_gdf, 3310)


def test_texas_reprojects_cleanly_to_5070(texas_gdf):
    """Sanity check: Texas IS inside EPSG:5070 (CONUS Albers)."""
    out = safe_to_crs(texas_gdf, 5070)
    assert out.crs.to_epsg() == 5070
    assert out.geometry.is_valid.all()
