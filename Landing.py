# Import necessary libraries.
import json
import os
import tempfile
from pathlib import Path

import debugpy
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st
from shapely.geometry import Polygon, mapping, shape
from shapely.ops import unary_union

# Set up Streamlit app configuration and debugging.
# The following code checks if a debug client is already connected. If not, it attempts to listen for debug connections on port 5678. This allows you to attach a debugger (e.g., from VS Code) to the Streamlit app for debugging purposes. The try-except block handles the case where the port might already be in use, which can happen in certain environments that don't support debugging.
if not debugpy.is_client_connected():
    try:
        debugpy.listen(5678)  # Listen for debug connections on port 5678.
    except RuntimeError:
        pass  # Handle the case where the port is already in use (e.g., when running in an environment that doesn't support debugging).

st.session_state.DEBUG = True
st.set_page_config(layout="wide")

# Title of the page.
st.title('Landing Page')

# View uploaded boundary.
st.header("Upload Project Boundary", divider="blue")

# Import necessary functions from src modules.
from src.geometry import (
    _cell_map_code,
    create_buffer,
    get_bounding_box,
    get_neighbors,
    get_quads,
    get_species_cnddb,
    get_species_cnps,
    load_all_quads,
    load_boundary,
)
from src.species import (
    plot_cnddb_species_date_range,
    plot_cnddb_species_distribution_streamlit,
    plot_species_map_streamlit,
    refactor_cnps,
)

# Import data and perform necessary preprocessing at startup.

# Load all California quads data once at startup
all_quads_path = Path(
    "data/california_statewide_index_of_usgs_24k_7_5_minute_quad_topo_maps.geojson"
)
all_quads = load_all_quads(all_quads_path)

# Load CNPS data once at startup.
cnps_path = Path("data/CNPS_RAW.csv")
cnps = refactor_cnps(cnps_path)

# Load CNDDB data once at startup.
cnddb_path = Path("data/mock_cnddb_data.geojson")
cnddb = gpd.read_file(cnddb_path)

# Create file upload button for user to upload their own boundary file (GeoJSON format).
uploaded_file = st.file_uploader(
    label="Please upload the project boundary GeoJSON file.",
    type='geojson',
    accept_multiple_files=False,
    help="Drag and drop a .geojson file here, or click to browse.",
)

# Save to session state only when a new file is uploaded.
if uploaded_file is not None:
    st.session_state.uploaded_boundary = uploaded_file.getvalue()
    st.session_state.uploaded_boundary_name = uploaded_file.name

# Restore from session state if user navigated away and came back to page 1.
elif "uploaded_boundary" in st.session_state:
    import io

    uploaded_file = io.BytesIO(st.session_state.uploaded_boundary)
    uploaded_file.name = st.session_state.uploaded_boundary_name

# View uploaded boundary.
st.header("Project Boundary Preview", divider="blue")

# If a file is uploaded, read it as a GeoDataFrame and display it on a map.
if uploaded_file is not None:

    search_area = None
    run_buffer = False

    # Read the uploaded GeoJSON file into a GeoDataFrame.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".geojson") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    project_boundary_gdf = gpd.read_file(tmp_path)
    os.unlink(tmp_path)

    # After creating project_boundary_gdf, save it
    st.session_state.project_boundary_gdf = project_boundary_gdf

    # st.info(f"Loaded GeoDataFrame: {project_boundary_gdf.crs}")
    # st.info(f"Geometry: {project_boundary_gdf.geometry.values}")

    # Set CRS to WGS84 (EPSG:4326) if not already set, and reproject if necessary.
    if st.session_state.project_boundary_gdf.crs is None:
        st.session_state.project_boundary_gdf = (
            st.session_state.project_boundary_gdf.set_crs(epsg=4326)
        )
    else:
        st.session_state.project_boundary_gdf = (
            st.session_state.project_boundary_gdf.to_crs(epsg=4326)
        )

    # Convert boundary GeoDataFrame to GeoJSON format for pydeck.
    st.session_state.geojson_data = json.loads(
        st.session_state.project_boundary_gdf.to_json()
    )

    # Calculate the center of the boundary for initial map view.
    minx, miny, maxx, maxy = st.session_state.project_boundary_gdf.total_bounds
    center_lat = (miny + maxy) / 2
    center_lon = (minx + maxx) / 2

    # Create a pydeck layer to display the boundary.
    st.session_state.project_boundary_layer = pdk.Layer(
        type='GeoJsonLayer',
        data=st.session_state.geojson_data,
        pickable=True,
        stroked=True,
        filled=False,
        get_line_color="'#B22222'",  # Boundary defined by black line.
        line_width_min_pixels=2,
    )  # Ensures line is visible at any zoom.

    # Set the initial view state of the map to center on the boundary.
    view_state = pdk.ViewState(
        latitude=center_lat, longitude=center_lon, zoom=12, pitch=0
    )

    # Render the map with the boundary layer.
    st.pydeck_chart(
        pdk.Deck(
            layers=[
                st.session_state.project_boundary_layer
            ],  # Map the project boundary layer.
            initial_view_state=view_state,  # Set initial view to center on the boundary.
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        )
    )  # Add a basemap.

    # View project boundary with an applied buffer.
    st.header("Search Radius Criteria", divider="blue")

    # Define buffer search options for `st.radio()`.
    buffer_option_names = ['2-Mile', '5-Mile', '10-Mile', '9-Quad']

    # Create a radio button for buffer search options.
    # buffer_choice = st.radio("Select a buffer search option:", buffer_option_names)

    # search_area = None

    buffer_choice = st.radio(
        "Select a buffer search option:", buffer_option_names, key="buffer_radio"
    )
    run_buffer = st.button("Apply Buffer", type="primary")  # ADD THIS

    if run_buffer:  # only runs when clicked
        if buffer_choice == '2-Mile':
            distance = 3218.69
            search_area = create_buffer(st.session_state.project_boundary_gdf, distance)
            st.session_state.search_area = search_area
        elif buffer_choice == '5-Mile':
            distance = 8046.72
            search_area = create_buffer(st.session_state.project_boundary_gdf, distance)
            st.session_state.search_area = search_area
        elif buffer_choice == '10-Mile':
            distance = 16093.4
            search_area = create_buffer(st.session_state.project_boundary_gdf, distance)
            st.session_state.search_area = search_area
        elif buffer_choice == '9-Quad':
            all_quads = all_quads.to_crs(st.session_state.project_boundary_gdf.crs)
            quad_ids = get_quads(st.session_state.project_boundary_gdf, all_quads)
            buffer_quad_search = get_neighbors(quad_ids, all_quads)
            search_area = all_quads[
                all_quads['CELL_MAPCODE'].apply(_cell_map_code).isin(buffer_quad_search)
            ]
            st.session_state.search_area = search_area

    # Display the search area on a map using pydeck.
    if search_area is not None:

        # Reproject search area to WGS84 for mapping.
        search_area_wgs = st.session_state.search_area.to_crs(epsg=4326)

        # Convert search area GeoDataFrame to GeoJSON format for pydeck.
        geojson_search = json.loads(search_area_wgs.to_json())

        # Calculate the center of the search area for initial map view.
        minx, miny, maxx, maxy = search_area_wgs.total_bounds
        center_lat = (miny + maxy) / 2
        center_lon = (minx + maxx) / 2

        # Create a pydeck layer to display the buffered project boundary.
        buffer_layer = pdk.Layer(
            type="GeoJsonLayer",
            data=geojson_search,
            stroked=True,  # Display the boundary of the buffer.
            filled=True,
            get_fill_color=[108, 173, 191, 80],  # Fill color of the buffer.
            get_line_color=[108, 173, 191],  # Line color of the buffer boundary.
            line_width_min_pixels=1,  # Minimum line width to ensure visibility at all zoom levels.
        )

        # Set the initial view state of the map to center on the search area.
        view_state = pdk.ViewState(
            latitude=center_lat, longitude=center_lon, zoom=10, pitch=0
        )

        # Render the map with buffer and project boundary layers.
        st.pydeck_chart(
            pdk.Deck(
                layers=[
                    buffer_layer,
                    st.session_state.project_boundary_layer,
                ],  # `project_boundary_layer` is defined in the previous cell and will be rendered on top of the buffer layer.
                initial_view_state=view_state,
                map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            )
        )

    # After defining the search area, query the CNDDB and CNPS datasets.
    if run_buffer and search_area is not None:

        # Extract the quad IDs from the search area. (IS THIS WHAT ITS DOING)
        if buffer_choice == '9-Quad':
            # `Search_area` is already quads, extract IDs directly.
            search_quad_ids = set(
                st.session_state.search_area['CELL_MAPCODE']
                .apply(_cell_map_code)
                .tolist()
            )
        else:
            # Reproject quads to match the search area CRS for accurate spatial intersection.
            all_quads_reproj = all_quads.to_crs(st.session_state.search_area.crs)

            # st.write("search_area bounds:", search_area.total_bounds)
            # st.write("search_area CRS:", search_area.crs)
            # st.write("search_area geometry:", search_area.geometry.values)

            # `Search_area` is a buffered polygon, find which quads intersect it.
            search_quad_ids = get_quads(st.session_state.search_area, all_quads_reproj)

        # Query CNDDB dataset using the extracted quad IDs.
        cnddb_species = get_species_cnddb(cnddb_path, search_quad_ids)

        # Query CNPS dataset using the extracted quad IDs.
        cnps_species = get_species_cnps(cnps, search_quad_ids)

        # if "cnps_raw" not in st.session_state:
        #     st.session_state.cnps_raw = pd.read_csv("app/data/CNPS_RAW.csv")

        # if "cnddb_raw" not in st.session_state:
        #     st.session_state.cnddb_raw = pd.read_csv("app/data/cnddb_test_data.csv")

        if "editor_version" not in st.session_state:
            st.session_state.editor_version = 0

        st.session_state.cnps_raw = cnps_species
        st.session_state.cnddb_raw = cnddb_species

        # -------------------------------------------------------------------------
        # prevent the Table page from exporting an old or mismatched PTO table after a new buffer search.
        for key in ["formatted_cnps", "formatted_cnddb", "combined_pto", "pto_editor"]:
            if key in st.session_state:
                del st.session_state[key]
        # -------------------------------------------------------------------------

        st.session_state.editor_version += 1

        # st.session_state.search_area = search_area          # add this
        # st.session_state.project_boundary_gdf = project_boundary_gdf  # add this
        st.session_state.results_ready = True  # add this
