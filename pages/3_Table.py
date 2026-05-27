# Import required packages
import pandas as pd
import streamlit as st

# Import project-specific functions for formatting source data and exporting reports
from src.format_data import format_cnddb, format_cnps
from src.make_buffer import make_buffer

# Import Bio Weaver logo
bioweaver_logo = 'images/Bioweaver_logo.png'

# Configure Streamlit page settings
st.set_page_config(page_title = "Bio Weaver Tool",
                   layout="wide",
                    page_icon=bioweaver_logo)

# Display the Rincon logo in the sidebar and page area
rincon_logo = 'images/Rincon_Logo_Color.png'
st.logo(rincon_logo,
        size='large')

# Display page heading
st.header("Potential to Occur Report Builder", divider=True)

# Explain the purpose of the page
st.caption(
    "Review queried CNPS and CNDDB species results, edit potential-to-occur determinations, "
    "and export the finalized table to a Word document."
)

# ---------------------------------------------------------
# REQUIRE QUERIED RESULTS FROM LANDING PAGE
# ---------------------------------------------------------

# This page depends on species query results generated on the Landing Page.
# If the user has not uploaded a boundary, selected a radius, and applied
# the buffer search, the PTO table cannot be built yet.

if "results_ready" not in st.session_state or not st.session_state.results_ready:
    st.warning(
        "No queried results yet. Please go to the Landing Page, upload a boundary, select a search radius, and click Apply Buffer."
    )
    st.stop()

# Confirm that both raw CNPS and CNDDB query results are available.
# These datasets are required before formatting, combining, editing, and exporting
# the Potential to Occur table.

if "cnps_raw" not in st.session_state or "cnddb_raw" not in st.session_state:
    st.error(
        "Queried species results are missing. Please rerun the buffer search from the Landing Page."
    )
    st.stop()

# ---------------------------------------------------------
# TRANSFORM RAW QUERY RESULTS INTO CLIENT-FACING TABLES
# ---------------------------------------------------------

# Copy the raw CNPS and CNDDB results from session state
# so the original data remains unchanged while this page
# formats it for display and export.

cnps_queried = st.session_state.cnps_raw.copy()
cnddb_queried = st.session_state.cnddb_raw.copy()

# Convert raw source-specific outputs into standardized
# PTO table formats.
# The formatting functions rename fields, clean text, and
# prepare columns needed for the editable Potential to
# Occur table.

formatted_cnps = format_cnps(cnps_queried).copy()
formatted_cnddb = format_cnddb(cnddb_queried).copy()

# Assign plant records from CNPS as Plants and Lichens
# when the field is missing.

if "Taxon_Category" not in formatted_cnps.columns:
    formatted_cnps["Taxon_Category"] = "Plants and Lichens"

# CNDDB records should already include Taxon_Cateogry from
# format_cnddb(). Stop the page if it is missing since the
# table cannot be grouped or exported correctly wihtout this field.

if "Taxon_Category" not in formatted_cnddb.columns:
    st.error("CNDDB formatted table is missing Taxon_Category. Check format_cnddb().")
    st.stop()


# ---------------------------------------------------------
# COMBINE FOR DISPLAY AND EDITING IN ONE EDITOR
# ---------------------------------------------------------

# List the standard taxon categories used for PTO reporting
allowed_taxa = [
    "Birds",
    "Fish",
    "Invertebrates",
    "Mammals",
    "Plants and Lichens",
    "Reptiles",
]

# Combine formatted CNPS and CNDDB tables into one editable PTO table
combined_display = pd.concat([formatted_cnps, formatted_cnddb], ignore_index=True)

# Keep only the standard taxonomic groups used in the PTO report
combined_display = combined_display[
    combined_display["Taxon_Category"]
    .fillna("")
    .str.strip()
    .isin(allowed_taxa)
].copy()

# Remove duplicate species entries within each taxonomic group
combined_display = (combined_display.drop_duplicates(
    subset=["Taxon_Category", "SpeciesDisplay"],
    keep="first"
))

# Organize rows alphabetically by taxonomic group
combined_display = (combined_display
                    .sort_values(by='Taxon_Category')
                    .reset_index(drop=True)
                    )

# Create a stable internal row identifier for the editable table
combined_display["_row_id"] = range(len(combined_display))

if "combined_pto" not in st.session_state:
    st.session_state.combined_pto = combined_display

# Display summary metrics for the editable PTO table
col1, col2, col3 = st.columns(3)

# Count the total number of species currently shown in
# the PTO table
total_species = len(st.session_state.combined_pto)

# Count species with a completed Potential to Occur determination.
# Blank strings and whitespace values are treated as missing.
pto_assigned = (
    st.session_state.combined_pto["PotentialtoOccur"]
    .fillna("")
    .astype(str)
    .str.strip()
    .ne("")
    .sum()
)

# Count the species that still need a Potential to Occur determination
missing_pto = total_species - pto_assigned

# Show the table completion status as dashboard metrics
col1.metric("Total Species", total_species)
col2.metric("PTO Assigned", pto_assigned)
col3.metric("Missing PTO", missing_pto)

# List the columns used to build the PTO table editor
table_columns = [
    "Source",
    "Taxon_Category",
    "SpeciesDisplay",
    "StatusDisplay",
    "HabitatRequirements",
    "PotentialtoOccur",
    "HabitatSuitabilityObservations",
]

# Group the table and save button in one form
with st.form("pto_editor_form"):
    edited_combined = st.data_editor(

        # Select which columns appear in the editor
        st.session_state.combined_pto[["_row_id"] + table_columns],

        # Configure column display settings and dropdown options
        column_config={
            "_row_id": None,
            "Source": None,
            "Taxon_Category": None,
            "SpeciesDisplay": st.column_config.TextColumn("Species Name", pinned=True),
            "StatusDisplay": st.column_config.TextColumn("Status", width="medium"),
            "HabitatRequirements": st.column_config.TextColumn(
                "Habitat Requirements", width="large"
            ),
            "PotentialtoOccur": st.column_config.SelectboxColumn(
                "Potential to Occur",
                help="Determination of the presence of a species in the project area.",
                options=["Not Expected", "Low", "Moderate", "High", "Present"],
                required=False,
            ),
            "HabitatSuitabilityObservations": st.column_config.TextColumn(
                "Habitat Suitability / Observations", width="large"
            ),
        },
        num_rows="fixed",
        width="stretch",

        # Select which columns are read-only
        disabled=[
            "_row_id",
            "Taxon_Category",
            "Source",
            "SpeciesDisplay",
            "StatusDisplay",
            "HabitatRequirements",
        ],
        hide_index=True,
        key="pto_editor_form_table",
    )

    st.markdown("""
    <style>
    [data-testid="stFormSubmitButton"] button {
        background-color: #5b7e95;
        color: #FFFFFF;
        border-radius: 8px;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        background-color: #5b7e95;
        color: #FFFFFF;
        border-radius: 8px;
        opacity: 0.6;
    }
    </style>
    """, unsafe_allow_html=True)    

    # Display a submit button to save edits
    save_clicked = st.form_submit_button("Please click to save edits before exporting",
                                         shortcut="Enter",
                                         width="stretch")

    # Store the latest table state so exports reflect current edits
    # even before the user clicks "Save Edits"
    st.session_state._latest_editor = edited_combined

# Update the main saved table once the user clicks "Save Edits"
if save_clicked:
    st.session_state.combined_pto = edited_combined.copy()
    st.session_state._latest_editor = edited_combined.copy()
    st.success("Edits saved.")
    st.rerun()

# ---------------------------------------------------------
# EXPORT TO WORD
# ---------------------------------------------------------

# Create Word document from PTO template and store as downloadable bytes
docx_bytes = make_buffer()

# Only show export controls if document was created successfully
if docx_bytes is not None:

    # Create a text box where user can rename the file
    base_name = st.text_input("Report file name", value="pto_report").strip()

    # Build the final downloadable .docx file name
    file_name = f"{base_name or 'pto_report'}.docx"

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

    # Display the download button
    st.download_button(
        label="Export to Word",
        data=docx_bytes,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

with st.container(horizontal=True):
    st.page_link("pages/2_Results.py", label="Go to Previous Page: Potential to Occur Table Page", width='content', icon_position="right")
    st.space("stretch")
    st.page_link("Home.py", label="Go to Home Page", width='content', icon_position="left")

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
