#%%
from pathlib import Path
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import box
from pathlib import Path

#%%
# Create a function to load the boundary file and return a GeoDataFrame.
def load_boundary(file_path: str | Path) -> gpd.GeoDataFrame:
    '''
    Load a boundary file and return a GeoDataFrame.

    Parameters
    ----------
    file_path : str | Path
        Path to the boundary file (GeoJSON or KMZ)

    Returns 
    ----------
    gdf.GeoDataFrame
        GeoDataFrame with the boundary geometry loaded from the file.

    Notes
    ----------
    Returns a GeoDataFrame with the boundary geometry loaded from the file. 
    Sets the CRS to WGS84 (EPSG:4326) if it is not already set.
    The function currently supports GeoJSON and Shapefile formats. 
    KMZ support may be added in the future.
    '''

    # TODO: 
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

# Create a function to create a buffer around the boundary and return a new GeoDataFrame with the buffered geometry.
def create_buffer(gdf: gpd.GeoDataFrame, distance: float) -> gpd.GeoDataFrame:
    '''
    Create a buffer around the geometries in the GeoDataFrame and return a new GeoDataFrame with the buffered geometry.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame with the boundary geometry loaded from the file.
    distance : float
        Distance in meters to buffer around the boundary.

    Returns 
    ----------
    gpd.GeoDataFrame
        GeoDataFrame with the buffered geometry.

    Notes
    ----------
    Returns a GeoDataFrame with the buffered geometry. 
    The original GeoDataFrame is not modified.
    '''

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

# Create a function of get a bounding box from a GeoDataFrame.
def get_bounding_box(gdf: gpd.GeoDataFrame) -> np.ndarray:
    '''
    Get the bounding box of the geometries in a GeoDataFrame.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame with the boundary geometry loaded from the file

    Returns 
    ----------
    np.ndarray
        Array with the bounding box coordinates [minx, miny, maxx, maxy]

    Notes
    ----------
    Returns an array with the bounding box coordinates [minx, miny, maxx, maxy] of the geometries in the GeoDataFrame.
    '''

    bounds = gdf.total_bounds
    return bounds

#%%
# Create a function load all California quads from a file and return a GeoDataFrame.
def load_all_quads(filepath: str | Path) -> gpd.GeoDataFrame:
    '''
    Load all California quads from a file and return a GeoDataFrame.

    Parameters
    ----------
    filepath : str | Path
        Path to the file containing the quad geometries

    Returns
    ----------
    gpd.GeoDataFrame
        GeoDataFrame with the quad geometries loaded from the file
    '''

    filepath = Path(filepath)
    gdf = gpd.read_file(filepath)
    return gdf

#%%
# Create a function to refactor the 'CELL_MAPCODE' column in a CNPS CSV file to extract quad IDs as a list of integers.
def _cell_map_code(id):
    '''
    Refactor the 'CELL_MAPCODE' column in a CNPS CSV file to extract quad IDs as a list of integers.

    Parameters
    ----------
        id : str
            The 'CELL_MAPCODE' value from the CNPS CSV file, which is a string in the format '12345-A1'.

    Returns
    ----------
        int
            An integer representing the quad ID extracted from the 'CELL_MAPCODE' value. 
            The function parses the 'CELL_MAPCODE' string, extracts the numeric part and the letter, 
            converts the letter to a number (A=1, B=2, ..., H=8), and combines them to create a unique integer ID for the quad.
    '''
    lead, tail = str(id).split('-')
    pos = ['','A','B','C','D','E','F','G','H']
    my_num = pos.index(tail[0])
    cell_map_code = str(lead) + str(my_num) + str(tail[1])
    return int(cell_map_code)

# Create a function to get the quads that intersect with the boundary and return a set of quad IDs.
def get_quads(boundary, all_quads):
    '''
    Get the quads that intersect with the boundary and return a set of quad IDs.

    Parameters
    ----------
    boundary : gpd.GeoDataFrame
        GeoDataFrame with the boundary geometry loaded from the file
    all_quads : gpd.GeoDataFrame
        GeoDataFrame with all the California quad geometries loaded from the file

    Returns
    ----------
    set
        A set of quad IDs that intersect with the boundary.
    '''

    #TODO: Ensure CRS consistency before intersect command
    minx, miny, maxx, maxy = boundary.total_bounds
    bbox = box(minx, miny, maxx, maxy)
    quads = all_quads[all_quads.intersects(bbox)].copy()
    # This next line should work, but might not.
    cell_map_codes = [_cell_map_code(id) for id in set(quads['CELL_MAPCODE'])]
    return set(cell_map_codes)

# %%

# Create a function to filter the CNPS data on the set of quads.
def get_species_cnps(cnps_df, quad_ids):
    '''
    Get the species from the CNPS data that are found in the quads that intersect with the boundary.

    Parameters
    ----------
    cnps_df : pd.DataFrame
        DataFrame containing the CNPS species data, which includes a column 'split_quad' that lists the quad IDs associated with each species.
    quad_ids : set
        A set of quad IDs that intersect with the boundary

    Returns
    ----------
    pd.DataFrame
        A DataFrame containing the species from the CNPS data that are found in the quads that intersect with the boundary.
    '''

    # THis is the command to filter the CNPS data on the set of quads we find
    #    Is assume the CNPS list of quads is in the column called 'QUAD_IDS' and the 
    # CNPS data is a dataframe called... df!
    # Also, quad_ids is a set of IDs!

    cnps_species = cnps_df[cnps_df['split_quad'].apply(lambda x: bool(quad_ids.intersection(x)))].copy()
    return cnps_species

# %%

# Create a function to get the species from the CNDDB data that are found in the quads that intersect with the boundary.
def get_species_cnddb(file_path: str | Path, quad_ids):
    '''
    Get the species from the CNDDB data that are found in the quads that intersect with the boundary.

    Parameters
    ----------
    cnps_df : pd.DataFrame
        DataFrame containing the CNDDB species data, which includes a column 'KEYQUAD' that lists the quad IDs associated with each species.
    quad_ids : set
        A set of quad IDs that intersect with the boundary

    Returns
    ----------
    pd.DataFrame
        A DataFrame containing the species from the CNDDB data that are found in the quads that intersect with the boundary.
    '''

    # Read the CNDDB csv file
    file_path = Path(file_path)    
    cnddb_df = pd.read_csv(file_path)
    cnddb_species = cnddb_df[cnddb_df['KEYQUAD'].isin(quad_ids)].copy()
    return cnddb_species

# %%
