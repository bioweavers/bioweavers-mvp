import pandas as pd
import streamlit as st
from io import BytesIO
from docxtpl import DocxTemplate

from src.format_data import format_cnps, format_cnddb
from src.export_data import make_buffer

# Add title to the page.
st.title('Export Results as a Word Document')

# Add header.
st.header('Project Potential to Occur Table', divider=True)

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

cnps_queried = st.session_state.cnps_raw.copy()
cnddb_queried = st.session_state.cnddb_raw.copy()

# ---------------------------------------------------------
# TRANSFORM RAW DATA INTO CLIENT-FACING FORMAT
# ---------------------------------------------------------
formatted_cnps = format_cnps(cnps_queried).copy()
formatted_cnddb = format_cnddb(cnddb_queried).copy()

# ---------------------------------------------------------
# COMBINE FOR DISPLAY/EDITING IN ONE EDITOR
# ---------------------------------------------------------
if "combined_pto" not in st.session_state:
    combined_display = pd.concat(
        [formatted_cnps, formatted_cnddb],
        ignore_index=True
    )

    if "_row_id" not in combined_display.columns:
        combined_display = combined_display.copy()
        combined_display["_row_id"] = range(len(combined_display))

    st.session_state.combined_pto = combined_display


editable_columns = [
    "Source",
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
            "SpeciesDisplay": st.column_config.TextColumn("Species Name", pinned=True),
            "StatusDisplay": st.column_config.TextColumn("Status", width="medium"),
            "HabitatRequirements": st.column_config.TextColumn("Habitat Requirements", width="large"),
            "PotentialtoOccur": st.column_config.TextColumn("Potential to Occur", width="medium"),
            "HabitatSuitabilityObservations": st.column_config.TextColumn(
                "Habitat Suitability / Observations",
                width="large"
            ),
        },
        num_rows="fixed",
        width="stretch",
        disabled=["_row_id", "Source", "SpeciesDisplay", "StatusDisplay", "HabitatRequirements"],
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
    st.download_button(
        label="Export to Word",
        data=docx_bytes,
        file_name="pto_report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )