#%%
from pathlib import Path
import geopandas as gpd
import numpy as np

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




