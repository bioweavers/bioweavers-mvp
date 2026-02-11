#%%
from pathlib import Path
from typing import Iterable

import geopandas as gpd
import numpy as np
from shapely.geometry import box

#%%
def load_boundary(file_path: str | Path) -> gpd.GeoDataFrame:
    # TODO: Add documentation
    # Handle different file formats
    # For now, we will assume that the file is a GeoJSON or Shapefile
    # Add kmz support in the future
    file_path = Path(file_path)    
    gdf = gpd.read_file(file_path)
    # Set the CRS to WGS84 (EPSG:4326) if it is not already set
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)
    return gdf

#%%

def create_buffer(gdf: gpd.GeoDataFrame, distance: float) -> gpd.GeoDataFrame:
    # TODO: Add documentation
    # Distance should be in meters to match the 
    # CRS we will use for buffering (California Albers)
    # Create a buffer around the geometries in the GeoDataFrame
    # create a copy of the GeoDataFrame to avoid modifying the original
    gdf_buffered = gdf.copy()
    # Set the CRS to the California Albers (EPSG:3310) 
    # for accurate distance measurements
    gdf_buffered = gdf_buffered.to_crs(epsg=3310)
    gdf_buffered['geometry'] = gdf_buffered.geometry.buffer(distance)
    # Return the buffered GeoDataFrame in the original CRS
    gdf_buffered = gdf_buffered.to_crs(epsg=4326)
    return gdf_buffered

#%%

def get_bounding_box(gdf: gpd.GeoDataFrame) -> np.ndarray:
    # TODO: Add documentation
    # Get the bounding box of the geometries in the GeoDataFrame
    # The bounding box is returned as a list of [minx, miny, maxx, maxy]
    bounds = gdf.total_bounds
    return bounds


def load_quadrangles(quadrangles: str | Path | gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    # Accept either a path or an already-loaded GeoDataFrame
    if isinstance(quadrangles, gpd.GeoDataFrame):
        gdf = quadrangles.copy()
    else:
        gdf = gpd.read_file(Path(quadrangles))
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)
    return gdf


def _resolve_column(columns: Iterable[str], candidates: Iterable[str]) -> str | None:
    lowered = {c.lower(): c for c in columns}
    for candidate in candidates:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    return None


def get_quadrangles_intersecting_bbox(
    boundary_gdf: gpd.GeoDataFrame,
    quadrangles: str | Path | gpd.GeoDataFrame,
    id_col: str | None = None,
    name_col: str | None = None,
) -> gpd.GeoDataFrame:
    # Build a bbox geometry from the boundary and intersect with quads
    boundary_gdf = boundary_gdf.copy()
    if boundary_gdf.crs is None:
        boundary_gdf.set_crs(epsg=4326, inplace=True)

    quads = load_quadrangles(quadrangles)
    if quads.crs != boundary_gdf.crs:
        quads = quads.to_crs(boundary_gdf.crs)

    minx, miny, maxx, maxy = boundary_gdf.total_bounds
    bbox_geom = box(minx, miny, maxx, maxy)
    hits = quads[quads.intersects(bbox_geom)].copy()

    id_col = id_col or _resolve_column(
        hits.columns,
        [
            "quad_id",
            "quadid",
            "quad_code",
            "quadcode",
            "quad_num",
            "quadnum",
            "map_id",
            "mapid",
            "usgs_id",
            "usgsid",
            "gnis_id",
            "gnisid",
            "id",
        ],
    )

    name_col = name_col or _resolve_column(
        hits.columns,
        [
            "quad_name",
            "quadname",
            "map_name",
            "mapname",
            "name",
            "title",
        ],
    )

    if id_col is None:
        raise ValueError(
            "Could not infer a quadrangle ID column. "
            "Pass id_col explicitly (e.g., id_col='QUAD_CODE')."
        )

    cols = [id_col]
    if name_col is not None and name_col != id_col:
        cols.append(name_col)

    result = hits[cols].drop_duplicates()
    result = result.rename(columns={id_col: "quad_id", name_col: "quad_name"})
    result = result.sort_values(by=["quad_id"]).reset_index(drop=True)
    return result



