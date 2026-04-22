import pandas as pd
import streamlit as st
from io import BytesIO
from docxtpl import DocxTemplate

# ---------------------------------------------------------
# INITIALIZE SESSION STATE / load raw data
# ---------------------------------------------------------
if "cnps_raw" not in st.session_state:
    st.session_state.cnps_raw = pd.read_csv("app/data/CNPS_raw.csv")

if "cnddb_raw" not in st.session_state:
    st.session_state.cnddb_raw = pd.read_csv("app/data/cnddb_test_data.csv")

if "combined" not in st.session_state:
    st.session_state.combined = None

# ----------------------------------------------------------
# PROCESS CNPS + CNDDB DATA WITH BACKEND FUNCTIONS
#-----------------------------------------------------------

# insert modular workflow with source functions

# ---------------------------------------------------------
# FILTER CNPS FOR BOULDER PEAK
# ---------------------------------------------------------
cnps_filtered = st.session_state.cnps_raw.loc[:, [
    "ScientificName", "CommonName", "Lifeform", "Quads", "Habitat"
]]

cnps_boulder = cnps_filtered[
    cnps_filtered["Quads"].str.contains(
        "Boulder Peak (4112351)",
        case=False,
        na=False,
        regex=False
    )
].copy()

# ---------------------------------------------------------
# PREPARE CNDDB TO MATCH CNPS COLUMNS
# ---------------------------------------------------------
cnddb_filtered = st.session_state.cnddb_raw.loc[:, [
    "SNAME", "CNAME", "TAXONGROUP", "KEYQUAD", "ECOLOGICAL"
]]

cnddb_renamed = cnddb_filtered.rename(columns={
    "SNAME": "ScientificName",
    "CNAME": "CommonName",
    "TAXONGROUP": "Lifeform",
    "KEYQUAD": "Quads",
    "ECOLOGICAL": "Habitat"
}).copy()

# ---------------------------------------------------------
# ADD USER-EDITABLE COLUMNS
# ---------------------------------------------------------
for df in [cnps_boulder, cnddb_renamed]:
    df["PotentialtoOccur"] = ""
    df["HabitatSuitabilityObservations"] = ""

# ---------------------------------------------------------
# ADD CATEGORY COLUMN
# ---------------------------------------------------------
cnps_boulder["Category"] = "CNPS"
cnddb_renamed["Category"] = "CNDDB"

# ---------------------------------------------------------
# COMBINE FOR EDITING + EXPORT
# ---------------------------------------------------------
combined = pd.concat([cnps_boulder, cnddb_renamed], ignore_index=True)

# Store in session state
st.session_state.combined = combined

# ---------------------------------------------------------
# STREAMLIT EDITOR (COMBINED DATAFRAME)
# ---------------------------------------------------------
edited_combined = st.data_editor(
    st.session_state.combined,
    num_rows="dynamic",
    width='stretch',
    disabled=["ScientificName", "CommonName", "Lifeform", "Quads", "Habitat", "Category"]
)

# Update session state with edited version
st.session_state.combined = edited_combined

# ---------------------------------------------------------
# EXPORT BUTTON
# ---------------------------------------------------------
buffer = BytesIO()

doc = DocxTemplate("app/utils/pto_template.docx")
context = {"rows": st.session_state.combined.to_dict(orient="records")}
doc.render(context)
doc.save(buffer)
buffer.seek(0)

st.download_button(
    label="Export to Word",
    data=buffer,
    file_name="pto_report.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
