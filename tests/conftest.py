import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def pytest_report_header(config):
    """Print a one-line geospatial-env fingerprint at the top of every pytest
    run. When something fails on a collaborator's machine, this is the
    quickest way to spot a version skew or a missing PROJ data dir.

    Output looks like:
        geo-stack: geopandas 1.0.1 | shapely 2.0.6 (GEOS 3.13.0) | pyproj 3.7.0 (PROJ 9.5.1) | pyogrio 0.10.0
        conda env: bioweavers-gdf
    """
    parts = []
    try:
        import geopandas
        parts.append(f"geopandas {geopandas.__version__}")
    except ImportError:
        parts.append("geopandas MISSING")
    try:
        import shapely
        parts.append(f"shapely {shapely.__version__} (GEOS {shapely.geos_version_string})")
    except ImportError:
        parts.append("shapely MISSING")
    try:
        import pyproj
        parts.append(f"pyproj {pyproj.__version__} (PROJ {pyproj.proj_version_str})")
    except ImportError:
        parts.append("pyproj MISSING")
    try:
        import pyogrio
        parts.append(f"pyogrio {pyogrio.__version__}")
    except ImportError:
        parts.append("pyogrio MISSING")

    env = os.environ.get("CONDA_DEFAULT_ENV", "<not in conda>")
    return [f"geo-stack: {' | '.join(parts)}", f"conda env: {env}"]
