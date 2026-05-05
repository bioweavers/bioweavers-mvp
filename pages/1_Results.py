# Import necessary libraries.
import streamlit as st

# Import necessary functions from src modules.
from src.species import plot_species_map_streamlit, refactor_cnps, plot_cnddb_species_distribution_streamlit, plot_cnddb_species_date_range

# Title of the page.
st.title("Project Species Occurrences Results")

# Guard: stop the page from loading if the user hasn't run a search yet on the Landing Page.
# `results_ready` is set to True in page 1 after the buffer is applied and data is queried.
if not st.session_state.get("results_ready"):
    st.info("Run a search on the main page first.")
    st.stop()   # Halts execution of the rest of the page.

# Retrieve the filtered CNDDB species occurrences queried by page 1.
cnddb_species = st.session_state.cnddb_raw

# Retrieve the filtered CNPS species occurrences queried by page 1.
cnps_species = st.session_state.cnps_raw

# Retrieve the search area geometry (buffered boundary or 9-quad selection) from page 1.
search_area = st.session_state.search_area

# Retrieve the original uploaded project boundary GeoDataFrame from page 1.
project_boundary_gdf = st.session_state.project_boundary_gdf

# Map CNDDB species occurrences within the project boundary.
st.header("CNDDB Species Map", divider="blue")
plot_species_map_streamlit(cnddb_species, search_area, project_boundary_gdf) 

# Page header.
st.header("CNDDB Analysis Output", divider='blue')

# Graph the number of CNDDB species occurrences .
st.subheader("CNDDB Species Occurrence")
plot_cnddb_species_distribution_streamlit(cnddb_species)

# Page header.
st.header("Species Occurrence Raw Data", divider='blue')

# Display the results in tables.
st.subheader("California Natural Diversity Database Species Results")
st.write(f"Found {len(cnddb_species)} species occurrences")
st.dataframe(cnddb_species.drop(columns='geometry'))

# Display the results in tables.
st.subheader("California Native Plant Society Species Results")
st.write(f"Found {len(cnps_species)} species occurrences")
st.dataframe(cnps_species)

# Include page link button.
st.page_link("pages/2_Table.py", label="Go to PTO Table Page", width='stretch')