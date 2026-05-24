# Import necessary libraries.
import streamlit as st

# Import necessary functions from src modules.
from src.species import plot_species_map_streamlit, plot_taxon_pie_streamlit, refactor_cnps, plot_cnddb_species_distribution_streamlit

# Import Bioweaver logo
bioweaver_logo = 'images/Bioweaver_logo.png'

# Configure Streamlit page settings
st.set_page_config(page_title = "Bio Weaver Tool",
                   layout="wide",
                    page_icon=bioweaver_logo)

# Add the Rincon logo to the top left of the page.
rincon_logo = 'images/Rincon_Logo_Color.png'
st.logo(rincon_logo, size='large')

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

# 
st.caption("Plant species colored in green. Wildlife species colored in orange.")

# Page header.
st.header("CNDDB Analysis Output", divider='blue')

# Example of side by side visualizations.

# col1, col2 = st.columns(2)

# with col1:
#     st.subheader("CNDDB Species Occurrence")
#     plot_cnddb_species_distribution_streamlit(cnddb_species)

# with col2:
#     st.subheader("CNDDB Taxon Group Distribution")
#     plot_taxon_pie_streamlit(cnddb_species)

# Graph the number of CNDDB species occurrences.
st.subheader("CNDDB Species Occurrence")
plot_cnddb_species_distribution_streamlit(cnddb_species)

# # Graph the taxon group distribution.
# st.subheader("CNDDB Taxon Group Distribution")
# plot_taxon_pie_streamlit(cnddb_species)

# Add additional analysis and visualizations here as needed!

# Page header.
st.header("Species Occurrence Raw Data", divider='blue')

# Display the results in tables.
st.subheader("California Natural Diversity Database Species Results")
st.write(f"Found {len(cnddb_species)} species occurrences")
st.dataframe(cnddb_species.drop(columns='geometry'), column_order=['SNAME', 'CNAME', 'OCCNUMBER', 'TAXONGROUP', 'ACCURACY', 'PRESENCE', 'OCCTYPE', 'SITEDATE', 'ELMDATE', 'FEDLIST', 'CALLIST','GRANK', 'SRANK', 'RPLANTRANK', 'CDFWSTATUS', 'OTHRSTATUS', 'LOCDETAILS', 'ECOLOGICAL', 'GENERAL', 'LASTUPDATE'])

# Convert CNDDB results to CSV for download.
cnddb_csv = cnddb_species.drop(columns='Symbology').to_csv(index=False)

# Allow user to customize the file name.
custom_cnddb_file_name = st.text_input(label="Rename the CNDDB species results CSV file (optional)",
                                 value="cnddb_species").strip()

# Add a download button for the CNDDB results CSV.
st.download_button(
    label="Download CSV",
    data=cnddb_csv,
    file_name=f"{custom_cnddb_file_name or 'cnddb_species_results'}.csv",
    mime="text/csv",
    icon=":material/download:")

st.markdown("""
    <style>
    [data-testid="stDownloadButton"] button {
        background-color: #5b7e95;
        color: #FFFFFF;
        border-radius: 8px;
    }
    [data-testid="stDownloadButton"] button:hover {
        background-color: #5b7e95;
        color: #FFFFFF;
        border-radius: 8px;
        opacity: 0.6;
    }
    </style>
""", unsafe_allow_html=True)

# Display the results in tables.
st.subheader("California Native Plant Society Species Results")
st.write(f"Found {len(cnps_species)} species occurrences")
st.dataframe(cnps_species.drop(columns='split_quad'))

# Convert CNPS results to CSV for download.
cnps_csv = cnps_species.drop(columns='split_quad').to_csv(index=False)

# Allow user to customize the file name
custom_cnps_file_name = st.text_input(label="Rename the CNPS species results CSV file (optional)",
                                 value="cnps_species").strip()

# Add a download button for the CNPS results CSV.
st.download_button(
    label="Download CSV",
    data=cnps_csv,
    file_name=f"{custom_cnps_file_name or 'cnps_species_results'}.csv",
    mime="text/csv",
    icon=":material/download:")

# Add page link buttons to navigate to the previous and next pages.
with st.container(horizontal=True):
    st.page_link("pages/1_Landing.py", label="Go to Previous Page: Landing Page", width='content', icon_position="left")
    st.space("stretch")
    st.page_link("pages/3_Table.py", label="Go to Next Page: Potential to Occur Table Page", width='content', icon_position="right")

# Styling for the page link button.
st.markdown("""
    <style>
    [data-testid="stPageLink"] a {
        background-color: #375673;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 16px;
    }
    [data-testid="stPageLink"] a p {
        color: #FFFFFF !important;
    }
    [data-testid="stPageLink"] a:hover {
        background-color: #375673;
        color: #FFFFFF !important;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 16px;
        opacity: 0.6
    }
    </style>
""", unsafe_allow_html=True)
