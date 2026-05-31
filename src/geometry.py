#%%
# Import necessary libraries.
from pathlib import Path
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import box
from pathlib import Path
import streamlit as st
from shapely.geometry import shape
from shapely.ops import unary_union
from shapely.geometry import mapping
from shapely.geometry import Polygon

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
    
    # Read the boundary file using geopandas.
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

    # During the development phase, `create_buffer()` produced many silent failures and error messages that were difficult to debug.
    # We used `st.session_state.DEBUG:` as a tool to print debug messages to the Streamlit app at various stages of the function to understand where and why the failures were occurring.
    # These lines of code are commented out now, but they were instrumental in identifying issues, and may be helpful for future debugging if similar issues arise again.

    #if st.session_state.DEBUG:
        #st.info("Starting create_buffer()...")

    # Distance should be in meters to match the 
    # CRS we will use for buffering (California Albers)
   
    # Create a copy of the GeoDataFrame to avoid modifying the original
    gdf_buffered = gdf.copy()

    #if st.session_state.DEBUG:
        #st.info(f"\t Ensuring gdf CRS. Current value: {gdf_buffered.crs}")
    
    # Set CRS to WGS84 (EPSG:4326) if not already set, and reproject if necessary.
    if gdf_buffered.crs is None:
        # Use inplace to set the CRS directly on the GeoDataFrame without creating a new object, 
        # which avoids issues with chained assignments and ensures that the CRS is correctly 
        # assigned to the original GeoDataFrame.
        gdf_buffered.set_crs(epsg=4326, inplace=True)
    else:
        gdf_buffered = gdf_buffered.to_crs(epsg=4326)

    #if st.session_state.DEBUG:
        #st.info(f"\t Assigned gdf CRS. Current value: {gdf_buffered.crs}")

    # Set the CRS to the California Albers (EPSG:3310) 
    gdf_buffered = gdf_buffered.to_crs(crs="EPSG:3310", inplace=False)
    
    #st.info(f"Geometry after 3310 reproject: {gdf_buffered.geometry.values}")

    #f st.session_state.DEBUG:
        #st.info(f"\t CRS is {gdf_buffered.crs} which should be the CRS to California Albers (EPSG:3310)")

    #try:
        #st.info(f"Running gdf_final.geometry.buffer with {distance} meters...")
        #st.info(f"Geometry before buffer: {gdf_buffered.geometry.values}")
        #st.info(f"Is valid: {gdf_buffered.geometry.is_valid.values}")

    gdf_buffered['geometry'] = gdf_buffered.geometry.buffer(0)

        #st.info(f"Is valid after buffer(0): {gdf_buffered.geometry.is_valid.values}")

    gdf_buffered['geometry'] = gdf_buffered.geometry.buffer(distance)

    #except Exception as e:
        #st.info(f"Error creating buffer: {e}")

    #if st.session_state.DEBUG:
        #st.info(f"\t Created a buffer around the geometries of the uploaded project boundary.")

    # Reproject the buffered GeoDataFrame back to WGS84 (EPSG:4326) for consistency with other data layers.
    gdf_buffered = gdf_buffered.to_crs(epsg=4326, inplace=False)

    # Return the buffered GeoDataFrame in the original CRS       
    return gdf_buffered

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
    
    # Load all the California quad geometries from the file using geopandas.
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

    # Split the 'CELL_MAPCODE' value into the lead part and the tail part.
    lead, tail = str(id).split('-')

    # Create a mapping of letters to numbers for the tail part.
    pos = ['','A','B','C','D','E','F','G','H']

    # Find the letter in the tail part and convert it to a number using the mapping.
    my_num = pos.index(tail[0])

    # Combine the lead part and the numeric value of the letter to create a unique integer ID for the quad.
    cell_map_code = str(lead) + str(my_num) + str(tail[1])
    return int(cell_map_code)
#%%
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

    # Ensure that the CRS of the boundary and all_quads GeoDataFrames are the same before performing intersection.
    assert boundary.crs == all_quads.crs, "CRS of boundary and all_quads GeoDataFrames must be the same before performing intersection."

    # Get total bounds of the boundary GeoDataFrame.
    minx, miny, maxx, maxy = boundary.total_bounds

    # Create a bounding box geometry from total bounds coordinates of the boundary GeoDataFrame.
    bbox = box(minx, miny, maxx, maxy)

    # Filter the quads that intersect with the bounding box.
    quads = all_quads[all_quads.intersects(bbox)].copy()

    # Refactor the 'CELL_MAPCODE' column in the quads GeoDataFrame to extract quad IDs as a list of integers and return a set of unique quad IDs.
    cell_map_codes = [_cell_map_code(id) for id in set(quads['CELL_MAPCODE'])]
    return set(cell_map_codes)
#%%
def get_neighbors(quad_ids, all_quads: gpd.GeoDataFrame):
    '''
    Find the neighboring quads surrounding a center quad.

    Parameters
    ----------
    quad_ids : list
        List containing quad cell IDs
    all_quads : gpd.GeoDataFrame
        GeoDataFrame containing all available quads to search

    Returns 
    ----------
    set 
        List of CELL_IDs of all neighboring quads, including the center quad(s).
    
    Notes
    ----------
    Buffers selected quad's bounding box by 2% on each side to intersect
    surrounding quads without decimal point precision issues. 
    '''

    # Make a copy of the all_quads GeoDataFrame.
    all_quads = all_quads.copy()
    # Refactor the 'CELL_MAPCODE' column in the quads GeoDataFrame to extract quad IDs as a list of integers.
    all_quads['CELL_MAPCODE'] = all_quads['CELL_MAPCODE'].apply(_cell_map_code)

    # Loop through the list of quad IDs and find the neighboring quads that intersect with the buffered bounding box of each quad.
    neighbors = []
    for id in quad_ids:

        quad = all_quads[all_quads['CELL_MAPCODE'] == id]

        if quad.empty:
            continue  # Skip unmatched IDs.

        minx, miny, maxx, maxy = quad.total_bounds

        # Expand quad bbox by 2% on each side
        dx = (maxx - minx) * 0.02
        dy = (maxy - miny) * 0.02
        bbox = box(minx - dx, miny - dy, maxx + dx, maxy + dy)

        # Find neighboring quads that intersect with the buffered bounding box and add their CELL_MAPCODE values to the neighbors list.
        neighbor_quads = all_quads[all_quads.intersects(bbox)].copy()
        neighbors.extend(neighbor_quads['CELL_MAPCODE'].to_list())

    return list(set(neighbors))
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

    # Filter the CNPS DataFrame to include only the rows where the 'split_quad' column contains at least one quad ID that is in the set of quad IDs that intersect with the boundary.
    cnps_species = cnps_df[cnps_df['split_quad'].apply(lambda x: bool(quad_ids.intersection(x)))].copy()
    return cnps_species

# %%
# Create a function to get the species from the CNDDB data that spatially intersect with the search area.
def get_species_cnddb(file_path: str | Path, boundary: gpd.GeoDataFrame):
    '''
    Get the species from the CNDDB data that spatially intersect with the boundary.

    Parameters
    ----------
    file_path : str | Path
        Path to the CNDDB shapefile or GeoJSON.
    boundary : gpd.GeoDataFrame
        GeoDataFrame of the search area boundary to clip species to.

    Returns
    ----------
    gpd.GeoDataFrame
        A GeoDataFrame containing the species from the CNDDB data that 
        spatially intersect with the boundary.
    '''

    # Define a set of taxon groups to exclude from the search query, as they are considered communities and not individual species.
    excluded_taxongroups = {
        'Dune', 'Forest', 'Herbaceous', 'Inland Waters', 'Marsh', 'Riparian', 'Scrub', 'Woodland', 'Palustrine'
    }

    # Accept either a file path or an already-loaded GeoDataFrame.
    if isinstance(file_path, gpd.GeoDataFrame):
        cnddb_gdf = file_path
    else:
        cnddb_gdf = gpd.read_file(Path(file_path))

    # Filter excluded taxon groups first (faster clip).
    cnddb_gdf = cnddb_gdf[~cnddb_gdf['TAXONGROUP'].isin(excluded_taxongroups)]

    # Ensure CRS match before clipping
    if cnddb_gdf.crs != boundary.crs:
        boundary = boundary.to_crs(cnddb_gdf.crs)

    # Clip to boundary.
    cnddb_species = gpd.clip(cnddb_gdf, boundary)

    return cnddb_species

# %%
# Explicit checks of the functionality of the geometry handling and processing of the functions within this script.
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Load data
    boundary = load_boundary("../data/palisades.geojson")
    all_quads = load_all_quads("../data/california_statewide_index_of_usgs_24k_7_5_minute_quad_topo_maps.geojson")

    # Reproject quads to match boundary CRS if needed
    all_quads = all_quads.to_crs(boundary.crs)

    # Get intersecting quads
    quad_ids = get_quads(boundary, all_quads)
    print(f"Found {len(quad_ids)} intersecting quads: {quad_ids}")

    # Get the quad geometries that matched (for plotting)
    matching_quads = all_quads[all_quads['CELL_MAPCODE'].apply(_cell_map_code).isin(quad_ids)]

    # Plot
    fig, ax = plt.subplots(figsize=(10, 10))
    matching_quads.plot(ax=ax, color="lightblue", edgecolor="blue", alpha=0.5, label="Quads")
    boundary.plot(ax=ax, color="none", edgecolor="red", linewidth=2, label="Boundary")
    ax.legend()
    ax.set_title("Intersecting Quads and Project Boundary")
    plt.show()
# %%
import geopandas as gpd
from pyproj import CRS
# A function used to check and debug the geometry handling and processing within this script.
def safe_to_crs(gdf: gpd.GeoDataFrame, target_epsg: int) -> gpd.GeoDataFrame:
    """to_crs with explicit checks for the four ways it silently produces garbage."""
    n = len(gdf)
    if n == 0:
        raise ValueError("Input GeoDataFrame is empty.")

    # 1. Source CRS must be set. set_crs only labels — if it's wrong, every downstream call lies.
    if gdf.crs is None:
        raise ValueError(
            "Source GeoDataFrame has no CRS. Use set_crs() to label it before reprojecting, "
            "but only if you know what CRS the coordinates are actually in."
        )

    # 2. Input geometries must be non-null and non-empty.
    n_null = gdf.geometry.isna().sum()
    n_empty = gdf.geometry.is_empty.sum()
    if n_null or n_empty:
        raise ValueError(
            f"Input has {n_null} null and {n_empty} empty geometries (of {n}). "
            "Drop or repair these before reprojecting."
        )

    # 3. Input bounds must lie within the target CRS's area of use.
    target = CRS.from_epsg(target_epsg)
    if target.area_of_use is not None:
        w, s, e, n_ = target.area_of_use.bounds  # always lon/lat
        bounds_4326 = gdf.to_crs(epsg=4326).total_bounds
        xmin, ymin, xmax, ymax = bounds_4326
        outside = not (xmin >= w and ymin >= s and xmax <= e and ymax <= n_)
        if outside:
            raise ValueError(
                f"Input bounds [{xmin:.3f}, {ymin:.3f}, {xmax:.3f}, {ymax:.3f}] "
                f"extend outside EPSG:{target_epsg} area of use [{w:.3f}, {s:.3f}, {e:.3f}, {n_:.3f}]. "
                "Reprojection will produce empty or invalid geometries. "
                "Use a CRS whose area of use covers your data."
            )

    # 4. Do the reprojection and validate the output.
    out = gdf.to_crs(epsg=target_epsg)
    out_null = out.geometry.isna().sum()
    out_empty = out.geometry.is_empty.sum()
    out_invalid = (~out.geometry.is_valid).sum()
    if out_null or out_empty or out_invalid:
        raise RuntimeError(
            f"to_crs(epsg={target_epsg}) silently produced "
            f"{out_null} null, {out_empty} empty, {out_invalid} invalid geometries "
            f"out of {n}. Likely causes: source CRS mislabeled, geometries crossing "
            f"the antimeridian, or PROJ falling back to a ballpark transformation."
        )

    return out
