"""Environment health checks for the geospatial stack.

Background
----------
We've been bitten by `gdf.to_crs(...)` returning empty or non-finite geometries
on collaborator machines, even in supposedly-correct conda envs. The root cause
is almost always one of:

  1. Wrong package versions — geopandas/shapely/pyproj need to be on a recent
     line that share a compatible C ABI.
  2. Mixed pip + conda installs — two copies of GEOS or PROJ get loaded into
     the same process and produce inf/NaN coordinates (or segfault).
  3. PROJ data dir missing — pyproj can't find proj.db, so transformations
     silently fall back to ballpark or fail.
  4. The Python-side bindings disagree with the underlying C libraries —
     `to_crs` returns garbage that pyproj's own Transformer would not.

These tests catch all four failure modes. If any of them fail on a
collaborator's machine, they have a clear, actionable error message pointing
at the specific layer that's broken.

Run: pytest tests/test_environment.py -v
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import pytest


# --- minimum versions ------------------------------------------------------
# Pinned to the lowest version we've verified works correctly together. Bump
# when you've tested a newer combination.

MIN_GEOPANDAS = (1, 0, 0)
MIN_SHAPELY = (2, 0, 0)
MIN_PYPROJ = (3, 6, 0)
MIN_PYOGRIO = (0, 7, 0)


def _parse_version(v: str) -> tuple[int, int, int]:
    """'1.0.1' -> (1, 0, 1). Tolerates suffixes like '2.0.0.post1'."""
    parts = v.split(".")[:3]
    out = []
    for p in parts:
        # Strip non-numeric trailing chars (e.g. '0rc1' -> '0').
        digits = ""
        for c in p:
            if c.isdigit():
                digits += c
            else:
                break
        out.append(int(digits) if digits else 0)
    while len(out) < 3:
        out.append(0)
    return tuple(out)  # type: ignore[return-value]


def _fmt(v: tuple[int, int, int]) -> str:
    return ".".join(str(x) for x in v)


# --- version checks --------------------------------------------------------

def test_geopandas_minimum_version():
    """Geopandas 1.0+ uses Shapely 2's C internals; older versions can't.
    A geopandas < 1.0 + shapely 2 mix produces silent corruption."""
    import geopandas
    actual = _parse_version(geopandas.__version__)
    assert actual >= MIN_GEOPANDAS, (
        f"geopandas {geopandas.__version__} is too old "
        f"(need >= {_fmt(MIN_GEOPANDAS)}). "
        f"Recreate the env from environment.yml using conda-forge."
    )


def test_shapely_minimum_version():
    """Shapely 2.0 rewrote the C internals. Mixing shapely 1.x with a
    modern geopandas is a known source of silent geometry corruption."""
    import shapely
    actual = _parse_version(shapely.__version__)
    assert actual >= MIN_SHAPELY, (
        f"shapely {shapely.__version__} is too old "
        f"(need >= {_fmt(MIN_SHAPELY)}). "
        f"Recreate the env from environment.yml using conda-forge."
    )


def test_pyproj_minimum_version():
    """pyproj 3.6+ ships PROJ 9, which we rely on for stable area-of-use
    handling and the 'always_xy' transformer behavior."""
    import pyproj
    actual = _parse_version(pyproj.__version__)
    assert actual >= MIN_PYPROJ, (
        f"pyproj {pyproj.__version__} is too old "
        f"(need >= {_fmt(MIN_PYPROJ)}). "
        f"Recreate the env from environment.yml using conda-forge."
    )


def test_pyogrio_available_and_recent():
    """Modern geopandas defaults to pyogrio for I/O. If only fiona is
    installed (or pyogrio is too old), file reads can crash on Windows."""
    pyogrio = pytest.importorskip(
        "pyogrio",
        reason="pyogrio not installed — geopandas will fall back to fiona",
    )
    actual = _parse_version(pyogrio.__version__)
    assert actual >= MIN_PYOGRIO, (
        f"pyogrio {pyogrio.__version__} is too old "
        f"(need >= {_fmt(MIN_PYOGRIO)})."
    )


# --- infrastructure: PROJ data must exist ----------------------------------

def test_proj_data_dir_exists():
    """pyproj needs a data dir on disk to load proj.db. Missing dir => silent
    fallback to ballpark transformations or outright NaN output."""
    import pyproj
    data_dir = Path(pyproj.datadir.get_data_dir())
    assert data_dir.exists(), (
        f"pyproj data dir does not exist: {data_dir}\n"
        f"This usually means pyproj was installed in a way that didn't ship "
        f"PROJ data files. Set the PROJ_DATA env var, or recreate the env."
    )


def test_proj_db_is_findable():
    """proj.db is the database PROJ uses to look up CRS definitions and
    transformation pipelines. No proj.db => no working to_crs."""
    import pyproj
    data_dir = Path(pyproj.datadir.get_data_dir())
    proj_db = data_dir / "proj.db"
    assert proj_db.exists(), (
        f"proj.db not found at {proj_db}.\n"
        f"PROJ_DATA is set to: {os.environ.get('PROJ_DATA', '<unset>')}\n"
        f"PROJ_LIB is set to: {os.environ.get('PROJ_LIB', '<unset>')}\n"
        f"Recreate the env from environment.yml using conda-forge."
    )


# --- functional: the actual failure mode -----------------------------------
# These tests catch the silent-failure case directly: if to_crs is producing
# inf/NaN/empty output, *these* fail with diagnostics, regardless of whether
# the version checks above pass.

# Downtown LA (-118.243, 34.052). Picked because:
#  - clearly inside California (so EPSG:3310 area-of-use is happy)
#  - off the central meridian (so projected x is non-trivial, not just 0)
KNOWN_LON, KNOWN_LAT = -118.243, 34.052


def _make_known_point_gdf():
    import geopandas as gpd
    from shapely.geometry import Point
    return gpd.GeoDataFrame(
        {"geometry": [Point(KNOWN_LON, KNOWN_LAT)]},
        crs="EPSG:4326",
    )


def test_to_crs_produces_finite_coordinates():
    """The headline failure mode: to_crs silently returning non-finite
    coordinates. If this fails, the geospatial C stack is broken."""
    out = _make_known_point_gdf().to_crs(epsg=3310)
    geom = out.geometry.iloc[0]

    assert geom is not None, "to_crs returned a None geometry"
    assert not geom.is_empty, "to_crs returned an empty geometry"
    assert math.isfinite(geom.x), f"to_crs produced non-finite x: {geom.x}"
    assert math.isfinite(geom.y), f"to_crs produced non-finite y: {geom.y}"


def test_to_crs_agrees_with_pyproj_transformer():
    """Strongest cross-check we have: project the same point two ways
    (GeoDataFrame.to_crs vs a direct pyproj.Transformer) and assert they
    produce the same numbers. If they disagree, the GeoPandas <-> pyproj
    binding is corrupt — almost always a binary mismatch from mixed
    pip/conda installs of the C stack."""
    from pyproj import Transformer

    # Reference: pure pyproj transformation. This is the source of truth.
    t = Transformer.from_crs("EPSG:4326", "EPSG:3310", always_xy=True)
    expected_x, expected_y = t.transform(KNOWN_LON, KNOWN_LAT)

    # GeoPandas path — must match pyproj exactly (sub-millimeter).
    out = _make_known_point_gdf().to_crs(epsg=3310)
    actual_x, actual_y = out.geometry.iloc[0].x, out.geometry.iloc[0].y

    assert math.isfinite(actual_x) and math.isfinite(actual_y), (
        f"GeoDataFrame.to_crs returned non-finite coordinates "
        f"({actual_x}, {actual_y}); pyproj.Transformer returned "
        f"({expected_x}, {expected_y}). The geopandas/pyproj binding is "
        f"broken — likely a binary mismatch in the geospatial C stack."
    )
    assert abs(actual_x - expected_x) < 0.001, (
        f"x mismatch between geopandas and pyproj: "
        f"geopandas={actual_x}, pyproj={expected_x}"
    )
    assert abs(actual_y - expected_y) < 0.001, (
        f"y mismatch between geopandas and pyproj: "
        f"geopandas={actual_y}, pyproj={expected_y}"
    )


def test_to_crs_roundtrip_preserves_coordinates():
    """4326 -> 3310 -> 4326 should return the original lon/lat to sub-mm.
    A failing roundtrip means the projection is dropping precision in a way
    that's well beyond floating-point — the kind of damage that produces
    'works on my machine but my collaborator gets garbage.'"""
    gdf = _make_known_point_gdf()
    out = gdf.to_crs(epsg=3310).to_crs(epsg=4326)
    geom = out.geometry.iloc[0]

    assert math.isfinite(geom.x) and math.isfinite(geom.y), (
        f"Roundtrip produced non-finite coordinates: ({geom.x}, {geom.y})"
    )
    # Sub-meter at California latitudes is comfortably less than 1e-5 degrees.
    assert abs(geom.x - KNOWN_LON) < 1e-6, (
        f"Roundtrip lon drifted: original={KNOWN_LON}, after={geom.x}"
    )
    assert abs(geom.y - KNOWN_LAT) < 1e-6, (
        f"Roundtrip lat drifted: original={KNOWN_LAT}, after={geom.y}"
    )


def test_to_crs_preserves_polygon_topology():
    """A polygon must remain a valid, non-empty polygon after reprojection.
    The empty-geometry failure mode shows up here even when single-point
    reprojection looks fine."""
    import geopandas as gpd
    from shapely.geometry import box

    gdf = gpd.GeoDataFrame(
        {"geometry": [box(-119.0, 34.0, -118.5, 34.5)]},
        crs="EPSG:4326",
    )
    out = gdf.to_crs(epsg=3310)
    geom = out.geometry.iloc[0]

    assert geom is not None, "Polygon became None after to_crs"
    assert not geom.is_empty, "Polygon became empty after to_crs"
    assert geom.is_valid, "Polygon became invalid after to_crs"
    # A 0.5-degree square in California should be > 100 km^2 in EPSG:3310.
    assert geom.area > 1e9, (
        f"Reprojected polygon has unexpectedly small area ({geom.area:.0f} m^2). "
        f"Likely a CRS mislabel or transformation collapse."
    )


# --- diagnostic test: always passes, prints env summary --------------------

def test_print_environment_summary(capsys):
    """Always passes. Captures and prints a fingerprint of the geospatial
    stack so when other tests fail on a collaborator's machine, the env info
    is right there in the test output. View it with: pytest -s -v."""
    import geopandas, pyproj, shapely

    lines = [
        "",
        "=" * 60,
        "GEOSPATIAL ENVIRONMENT SUMMARY",
        "=" * 60,
        f"  python:    {sys.version.split()[0]} ({sys.executable})",
        f"  geopandas: {geopandas.__version__}",
        f"  shapely:   {shapely.__version__}  (GEOS {shapely.geos_version_string})",
        f"  pyproj:    {pyproj.__version__}   (PROJ {pyproj.proj_version_str})",
    ]

    try:
        import pyogrio
        gdal_ver = getattr(pyogrio, "__gdal_version_string__", "?")
        lines.append(f"  pyogrio:   {pyogrio.__version__}  (GDAL {gdal_ver})")
    except ImportError:
        lines.append("  pyogrio:   NOT INSTALLED")

    try:
        import fiona
        lines.append(f"  fiona:     {fiona.__version__}  (also installed)")
    except ImportError:
        pass  # fine — pyogrio is preferred

    lines += [
        f"  PROJ data: {pyproj.datadir.get_data_dir()}",
        f"  PROJ_DATA env: {os.environ.get('PROJ_DATA', '<unset>')}",
        f"  conda env: {os.environ.get('CONDA_DEFAULT_ENV', '<not in conda>')}",
        "=" * 60,
        "",
    ]
    print("\n".join(lines))
