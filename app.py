import streamlit as st

st.set_page_config(
    # Title and icon for the browser's tab bar:
    page_title="Bio Weaver Tool",
    page_icon="🌦️",
    # Make the content take up the width of the page:
    layout="wide",
)

from pathlib import Path

from src.geometry import load_boundary, create_buffer, get_bounding_box, load_all_quads, get_quads, get_species_cnps, get_species_cnddb
from src.species import refactor_cnps

# Load sample boundary
boundary_path = Path("data/palisades.geojson")
boundary = load_boundary(boundary_path)


# Create a 5-mile buffer and bounding box
buffered = create_buffer(boundary, distance=5)
bbox = get_bounding_box(buffered)

all_quads_path = Path("data/california_statewide_index_of_usgs_24k_7_5_minute_quad_topo_maps.geojson")
all_quads = load_all_quads(all_quads_path)

quad_ids = get_quads(boundary, all_quads)

# Refactor CNPS Quad list.
cnps_path = Path("data/CNPS_RAW.csv")
cnps = refactor_cnps(cnps_path)

cnps_species = get_species_cnps(cnps, quad_ids)

st.dataframe(cnps_species)
