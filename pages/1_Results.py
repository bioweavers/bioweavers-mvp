import streamlit as st
import time

from src.species import plot_species_map_streamlit, refactor_cnps, plot_cnddb_species_distribution_streamlit, plot_cnddb_species_date_range


st.title("Project Species Occurrences Results")


if not st.session_state.get("results_ready"):
    st.info("Run a search on the main page first.")
    st.stop()

cnddb_species = st.session_state.cnddb_raw
cnps_species = st.session_state.cnps_raw
search_area = st.session_state.search_area
project_boundary_gdf = st.session_state.project_boundary_gdf

# Map CNDDB species occurrences within the project boundary.
st.header("CNDDB Species Map", divider="grey")
plot_species_map_streamlit(cnddb_species, search_area, project_boundary_gdf) 

st.header("CNDDB Analysis Output", divider='grey')

# Graph the number of CNDDB species occurrences .
st.subheader("CNDDB Species Occurrence")
plot_cnddb_species_distribution_streamlit(cnddb_species)

st.header("Species Occurrence Raw Data", divider='grey')

# Display the results in tables.
st.subheader("California Natural Diversity Database Species Results")
st.write(f"Found {len(cnddb_species)} species occurrences")
st.dataframe(cnddb_species.drop(columns='geometry'))

# Display the results in tables.
st.subheader("California Native Plant Society Species Results")
st.write(f"Found {len(cnps_species)} species occurrences")
st.dataframe(cnps_species)

st.page_link("pages/2_Table.py", label="Go to PTO Table Page", width='stretch')