import pandas as pd
import streamlit as st
from io import BytesIO
from docxtpl import DocxTemplate

from src.format_data import format_cnps, format_cnddb
from src.make_buffer import make_buffer

# Add title to the page
st.title('Export Results as a Word Document')

# Add header
st.header('Potential to Occur Table', divider=True)

# ---------------------------------------------------------
# REQUIRE QUERIED RESULTS FROM LANDING PAGE
# ---------------------------------------------------------
if "results_ready" not in st.session_state or not st.session_state.results_ready:
    st.warning("No queried results yet. Please go to the Landing Page, upload a boundary, select a search radius, and click Apply Buffer.")
    st.stop()

if "cnps_raw" not in st.session_state or "cnddb_raw" not in st.session_state:
    st.error("Queried species results are missing. Please rerun the buffer search from the Landing Page.")
    st.stop()

if "editor_version" not in st.session_state:
    st.session_state.editor_version = 0

# for key in ["combined_pto", "_latest_editor", "pto_editor_form_table"]:
#     if key in st.session_state:
#         del st.session_state[key]

cnps_queried = st.session_state.cnps_raw.copy()
cnddb_queried = st.session_state.cnddb_raw.copy()

# ---------------------------------------------------------
# TRANSFORM RAW DATA INTO CLIENT-FACING FORMAT
# ---------------------------------------------------------
formatted_cnps = format_cnps(cnps_queried).copy()
formatted_cnddb = format_cnddb(cnddb_queried).copy()

if "Taxon_Category" not in formatted_cnps.columns:
    formatted_cnps["Taxon_Category"] = "Plants"

if "Taxon_Category" not in formatted_cnddb.columns:
    st.error("CNDDB formatted table is missing Taxon_Category. Check format_cnddb().")
    st.stop()


# ---------------------------------------------------------
# COMBINE FOR DISPLAY/EDITING IN ONE EDITOR
# ---------------------------------------------------------
combined_display = pd.concat(
    [formatted_cnps, formatted_cnddb],
    ignore_index=True
)

combined_display = combined_display[
    combined_display["Taxon_Category"] != "Community"
].copy()

if "_row_id" not in combined_display.columns:
    combined_display["_row_id"] = range(len(combined_display))

if "combined_pto" not in st.session_state:
    st.session_state.combined_pto = combined_display

if "combined_pto" not in st.session_state:
    combined_display = pd.concat(
        [formatted_cnps, formatted_cnddb],
        ignore_index=True
    )

    combined_display = combined_display[
        combined_display["Taxon_Category"] != "Community"
    ].copy()

    if "_row_id" not in combined_display.columns:
        combined_display["_row_id"] = range(len(combined_display))

    st.session_state.combined_pto = combined_display

editable_columns = [
    "Source",
    "Taxon_Category",
    "SpeciesDisplay",
    "StatusDisplay",
    "HabitatRequirements",
    "PotentialtoOccur",
    "HabitatSuitabilityObservations",
]

with st.form("pto_editor_form"):
    edited_combined = st.data_editor(
        st.session_state.combined_pto[["_row_id"] + editable_columns],
        column_config={
            "_row_id": None,
            "Source": None,
            "Taxon_Category": None,

            "SpeciesDisplay": st.column_config.TextColumn("Species Name", pinned=True),

            "StatusDisplay": st.column_config.TextColumn("Status", width="medium"),

            "HabitatRequirements": st.column_config.TextColumn("Habitat Requirements", width="large"),

            "PotentialtoOccur": st.column_config.SelectboxColumn("Potential to Occur",

            help = "Determination of the presence of a species in the project area.",

            options=["Not Expected", "Low", "Moderate", "High", "Present"],

            required=False),

            "HabitatSuitabilityObservations": st.column_config.TextColumn(
                "Habitat Suitability / Observations",
                width="large"
            ),
        },
        num_rows="fixed",
        width="stretch",
        disabled=["_row_id", "Taxon_Category", "Source", "SpeciesDisplay", "StatusDisplay", "HabitatRequirements"],
        hide_index=True,
        key="pto_editor_form_table",
    )

    save_clicked = st.form_submit_button("Save Edits")


    # Store the latest edited table before saving
    st.session_state._latest_editor = edited_combined



if save_clicked:
    st.session_state.combined_pto = edited_combined.copy()
    st.success("Edits saved.")

# ---------------------------------------------------------
# EXPORT TO WORD
# ---------------------------------------------------------

docx_bytes = make_buffer()

if docx_bytes is not None:
    base_name = st.text_input(
        "Report file name",
        value="pto_report"
    ).strip()

    file_name = f"{base_name or 'pto_report'}.docx"

    st.download_button(
        label="Export to Word",
        data=docx_bytes,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )