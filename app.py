import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
# import folium
# from streamlit_folium import st_folium
# import tempfile
import json
from pathlib import Path
import streamlit as st
import geopandas as gpd
import json
import pydeck as pdk
import fiona

# Title of the page.
st.title('Testing Export PTO functionality')

# Import necessary functions from src modules.
from src.geometry import _cell_map_code, load_boundary, create_buffer, get_bounding_box, load_all_quads, get_quads, get_species_cnps, get_species_cnddb, get_neighbors
from src.species import plot_species_map_streamlit, refactor_cnps, plot_cnddb_species_distribution_streamlit, plot_cnddb_species_date_range

# Import data and perform necessary preprocessing at startup.

# Load all California quads data once at startup
all_quads_path = Path("data/california_statewide_index_of_usgs_24k_7_5_minute_quad_topo_maps.geojson")
all_quads = load_all_quads(all_quads_path) 

# Load CNPS data once at startup.
cnps_path = Path("data/CNPS_RAW.csv")
cnps = refactor_cnps(cnps_path)

# Load CNDDB data once at startup.
cnddb_path = Path("data/mock_cnddb_data.geojson")
cnddb = gpd.read_file(cnddb_path)

# Create file upload button for user to upload their own boundary file (GeoJSON format).
uploaded_file = st.file_uploader(
    label="Upload project boundary file.",
    type='geojson',
    accept_multiple_files=False,
    help="Drag and drop a .geojson file here, or click to browse.")

# View uploaded boundary.
st.header("Project Boundary Preview")

# If a file is uploaded, read it as a GeoDataFrame and display it on a map.
if uploaded_file is not None:

    search_area = None  
    run_buffer = False  

    # Read the uploaded GeoJSON file into a GeoDataFrame.
    project_boundary_gdf = gpd.read_file(uploaded_file)

    # Set CRS to WGS84 (EPSG:4326) if not already set, and reproject if necessary.
    if project_boundary_gdf.crs is None:
        project_boundary_gdf = project_boundary_gdf.set_crs(epsg=4326)
    else:
        project_boundary_gdf = project_boundary_gdf.to_crs(epsg=4326)

    # Convert boundary GeoDataFrame to GeoJSON format for pydeck.
    geojson_data = json.loads(project_boundary_gdf.to_json())

    # Calculate the center of the boundary for initial map view.
    minx, miny, maxx, maxy = project_boundary_gdf.total_bounds
    center_lat = (miny + maxy) / 2
    center_lon = (minx + maxx) / 2

    # Create a pydeck layer to display the boundary.
    project_boundary_layer = pdk.Layer(
    type='GeoJsonLayer',
    data=geojson_data,
    pickable=True,
    stroked=True,
    filled=False,                
    get_line_color="'#B22222'",  # FIND A BETTER COLOR OR A WAY TO IMPLEMENT A COLOR
    line_width_min_pixels=2)     # Ensures line is visible at any zoom.)

    # Set the initial view state of the map to center on the boundary.
    view_state = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=12,
    pitch=0)

    # Render the map with the boundary layer.
    st.pydeck_chart(pdk.Deck(
    layers=[project_boundary_layer],    # Map the project boundary layer.
    initial_view_state=view_state,      # Set initial view to center on the boundary.
    map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"))  # Add a basemap.

    # # View project boundary with an applied buffer.
    # st.title("Applying Buffer Search")

    # # Define buffer search options for `st.radio()`.
    # buffer_option_names = ['2-Mile', '5-Mile', '10-Mile', '9-Quad']

    # # Create a radio button for buffer search options.
    # # buffer_choice = st.radio("Select a buffer search option:", buffer_option_names)

    # # search_area = None

#     buffer_choice = st.radio("Select a buffer search option:", buffer_option_names, key="buffer_radio")
#     run_buffer = st.button("Apply Buffer")  # ADD THIS

#     if run_buffer:  # only runs when clicked
#         if buffer_choice == '2-Mile':
#             distance = 4828.03
#             search_area = create_buffer(project_boundary_gdf, distance)
#         elif buffer_choice == '5-Mile':
#             distance = 8046.72
#             search_area = create_buffer(project_boundary_gdf, distance)
#         elif buffer_choice == '10-Mile':
#             distance = 16093.4
#             search_area = create_buffer(project_boundary_gdf, distance)
#         elif buffer_choice == '9-Quad':
#             all_quads = all_quads.to_crs(project_boundary_gdf.crs)
#             quad_ids = get_quads(project_boundary_gdf, all_quads)
#             buffer_quad_search = get_neighbors(quad_ids, all_quads)
#             search_area = all_quads[all_quads['CELL_MAPCODE'].apply(_cell_map_code).isin(buffer_quad_search)]

#     # Display the search area on a map using pydeck.
#     if search_area is not None:

#         # Reproject search area to WGS84 for mapping.
#         search_area_wgs = search_area.to_crs(epsg=4326)

#         # Convert search area GeoDataFrame to GeoJSON format for pydeck.
#         geojson_search = json.loads(search_area.to_json())

#         # Calculate the center of the search area for initial map view.
#         minx, miny, maxx, maxy = search_area_wgs.total_bounds
#         center_lat = (miny + maxy) / 2
#         center_lon = (minx + maxx) / 2

#         # Create a pydeck layer to display the buffered project boundary.
#         buffer_layer = pdk.Layer(
#             type="GeoJsonLayer",
#             data=geojson_search,
#             stroked=True,                           # Display the boundary of the buffer.
#             filled=True,
#             get_fill_color=[0, 140, 255, 80],       # Fill color of the buffer.
#             get_line_color=[0, 0, 255],             # Line color of the buffer boundary.
#             line_width_min_pixels=1,                # Minimum line width to ensure visibility at all zoom levels.
#         )

#         # Set the initial view state of the map to center on the search area.
#         view_state = pdk.ViewState(
#             latitude=center_lat,
#             longitude=center_lon,
#             zoom=10,
#             pitch=0
#         )

#         # Render the map with buffer and project boundary layers.
#         st.pydeck_chart(pdk.Deck(
#             layers=[buffer_layer, project_boundary_layer],      # `project_boundary_layer` is defined in the previous cell and will be rendered on top of the buffer layer.
#             initial_view_state=view_state,
#             map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
#         ))


#     # After defining the search area, query the CNDDB and CNPS datasets.
#     if run_buffer and search_area is not None:

#         # Extract the quad IDs from the search area. (IS THIS WHAT ITS DOING)
#         if buffer_choice == '9-Quad':
#             # `Search_area` is already quads, extract IDs directly.
#             search_quad_ids = set(search_area['CELL_MAPCODE'].apply(_cell_map_code).tolist())
#         else:
#             # Reproject quads to match the search area CRS for accurate spatial intersection.
#             all_quads_reproj = all_quads.to_crs(search_area.crs)
#             # `Search_area` is a buffered polygon, find which quads intersect it.
#             search_quad_ids = get_quads(search_area, all_quads_reproj)

#         # Query CNDDB dataset using the extracted quad IDs.
#         cnddb_species = get_species_cnddb(cnddb_path, search_quad_ids)

#         # Query CNPS dataset using the extracted quad IDs.    
#         cnps_species = get_species_cnps(cnps, search_quad_ids)

#         # Display the results in tables.
#         st.subheader("CNDDB Species Results")
#         st.write(f"Found {len(cnddb_species)} species occurrences")
#         st.dataframe(cnddb_species.drop(columns='geometry'))

#         # Display the results in tables.
#         st.subheader("CNPS Species Results")
#         st.write(f"Found {len(cnps_species)} species occurrences")
#         st.dataframe(cnps_species)

#         # Map CNDDB species occurrences within the project boundary.
#         st.subheader("CNDDB Species Map")
#         plot_species_map_streamlit(cnddb_species, search_area, project_boundary_gdf) 

#         # Graph the number of CNDDB species occurrences .
#         st.subheader("CNDDB Species Occurrence Date Range")
#         plot_cnddb_species_distribution_streamlit(cnddb_species)







# # # Load sample boundary.
# # boundary_path = Path("data/sample_boundary.geojson")
# # boundary = load_boundary(boundary_path)

# # # Create a 5-mile buffer and bounding box.
# # buffered = create_buffer(boundary, distance=5)
# # bbox = get_bounding_box(buffered)

# # # Load in all quads in California.
# # all_quads_path = Path("data/california_statewide_index_of_usgs_24k_7_5_minute_quad_topo_maps.geojson")
# # all_quads = load_all_quads(all_quads_path)

# # # Get the list of quads that intersect with the boundary.
# # quad_ids = get_quads(boundary, all_quads)

# # # 9-quad buffer search.
# # buffer_quad_search = get_neighbors(quad_ids, all_quads)

# # # Refactor CNPS Quad list.
# # cnps_path = Path("data/CNPS_RAW.csv")
# # cnps = refactor_cnps(cnps_path)

# # # Get the CNPS species that are found within the intersecting quads.
# # cnps_species = get_species_cnps(cnps, quad_ids)

# # # edit cnps and cnddb filtered dataframe to add empty columns fo integration to platform

# # edited_cnps = st.data_editor(cnps_species[["ScientificName", "CommonName", "FESA"]],
# #                num_rows="fixed",
# #                disabled=["ScientificName", "CommonName"],)

# # # download button
# # st.download_button(
# #     label="Download PTO Assessment",
# #     data=edited_cnps.to_docx(index=False),
# #     file_name='pto_assessment.docx',
# #     mime='text/docx',
# # )


# # from docx import Document
# # from io import BytesIO

# # def df_to_docx(df):
# #     doc = Document()
# #     doc.add_heading('PTO Assessment', 0)

# #     table = doc.add_table(rows=1, cols=len(df.columns))
    
# #     # header row
# #     for i, col in enumerate(df.columns):
# #         table.rows[0].cells[i].text = str(col)

# #     # data rows
# #     for _, row in df.iterrows():
# #         cells = table.add_row().cells
# #         for i, val in enumerate(row):
# #             cells[i].text = str(val)

# #     buffer = BytesIO()
# #     doc.save(buffer)
# #     buffer.seek(0)
    
# #     return buffer

# # # create docx
# # docx_file = df_to_docx(edited_cnps)

# # # download button
# # st.download_button(
# #     label="Download PTO Assessment",
# #     data=docx_file,
# #     file_name="pto_assessment.docx",
# #     mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
# # )


