import pandas as pd
import streamlit as st
from io import BytesIO
from docxtpl import DocxTemplate

from utils.format_data import format_cnps, format_cnddb

# ---------------------------------------------------------
# INITIALIZE SESSION STATE / LOAD RAW DATA
# ---------------------------------------------------------
if "cnps_raw" not in st.session_state:
    st.session_state.cnps_raw = pd.read_csv("app/data/CNPS_RAW.csv")

if "cnddb_raw" not in st.session_state:
    st.session_state.cnddb_raw = pd.read_csv("app/data/cnddb_test_data.csv")

# ---------------------------------------------------------
# FILTER / QUERY SOURCE DATA
# ---------------------------------------------------------
cnps_queried = st.session_state.cnps_raw[
    st.session_state.cnps_raw["Quads"].str.contains(
        "Boulder Peak (4112351)",
        case=False,
        na=False,
        regex=False
    )
].copy()

# For now, use full CNDDB test data as queried result
cnddb_queried = st.session_state.cnddb_raw.copy()

# ---------------------------------------------------------
# TRANSFORM RAW DATA INTO CLIENT-FACING FORMAT
# ---------------------------------------------------------
formatted_cnps = format_cnps(cnps_queried).copy()
formatted_cnddb = format_cnddb(cnddb_queried).copy()

# ---------------------------------------------------------
# STORE FORMATTED TABLES IN SESSION STATE
# ---------------------------------------------------------
if "formatted_cnps" not in st.session_state:
    st.session_state.formatted_cnps = formatted_cnps

if "formatted_cnddb" not in st.session_state:
    st.session_state.formatted_cnddb = formatted_cnddb

# ---------------------------------------------------------
# OPTIONAL: COMBINE FOR DISPLAY/EDITING IN ONE EDITOR
# ---------------------------------------------------------
combined_display = pd.concat(
    [st.session_state.formatted_cnps, st.session_state.formatted_cnddb],
    ignore_index=True
)

# Add stable row ids if needed
if "_row_id" not in combined_display.columns:
    combined_display = combined_display.copy()
    combined_display["_row_id"] = range(len(combined_display))

# Keep source visible so you know which section each row belongs to
editable_columns = [
    "Source",
    "SpeciesDisplay",
    "StatusDisplay",
    "HabitatRequirements",
    "PotentialtoOccur",
    "HabitatSuitabilityObservations",
]

edited_combined = st.data_editor(
    combined_display[["_row_id"] + editable_columns],
    num_rows="dynamic",
    width="stretch",
    disabled=["_row_id", "Source", "SpeciesDisplay", "StatusDisplay", "HabitatRequirements"],
    hide_index=True,
)

# ---------------------------------------------------------
# SAVE EDITED VALUES BACK TO SESSION STATE
# ---------------------------------------------------------
edited_cnps = edited_combined[edited_combined["Source"] == "CNPS"].drop(columns=["_row_id"]).reset_index(drop=True)
edited_cnddb = edited_combined[edited_combined["Source"] == "CNDDB"].drop(columns=["_row_id"]).reset_index(drop=True)

st.session_state.formatted_cnps = edited_cnps
st.session_state.formatted_cnddb = edited_cnddb

# ---------------------------------------------------------
# EXPORT TO WORD
# ---------------------------------------------------------
buffer = BytesIO()

doc = DocxTemplate("app/utils/pto_template.docx")
context = {
    #"project_name": "Boulder Peak Project",
    #"project_location": "Boulder Peak",
    #"buffer_radius": "TBD",
    #"assessment_date": pd.Timestamp.today().strftime("%Y-%m-%d"),
    "cnps_rows": st.session_state.formatted_cnps.to_dict(orient="records"),
    "cnddb_rows": st.session_state.formatted_cnddb.to_dict(orient="records"),
}
doc.render(context)
doc.save(buffer)
buffer.seek(0)

st.download_button(
    label="Export to Word",
    data=buffer,
    file_name="pto_report.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
)

