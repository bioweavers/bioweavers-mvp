# Import necessary libraries.
import pandas as pd
import streamlit as st
from io import BytesIO
from docxtpl import DocxTemplate

#from ..app.utils.format_data import format_cnps, format_cnddb

# Add title to the page.
st.title('Export Results to Word')

# Add header.
st.header('Project Potential to Occur Table', divider="blue")

# Join non empty lines
def join_lines(*parts):
    cleaned = [str(p).strip() for p in parts if pd.notna(p) and str(p).strip()]
    return "\n".join(cleaned)

# Format CNPS data for Potential to Occur output
def format_cnps(df):
    out = pd.DataFrame()
    
    def build_species_display(r):
        return join_lines(r['ScientificName'], r['CommonName'])

    def build_status_display(r):
        # Left: Label
        # Right: Column Name
        mapping = {
            'CRPR': 'CRPR',
            'CESA': 'CESA',
            'FESA': 'FESA',
            'Other Status': 'OtherStatus'
        }
        parts = [
            f"{label}: {r[col]}"
            for col, label in mapping.items()
            if pd.notna(r.get(col))
        ]
        return join_lines(*parts)

    def build_habitat_requirements(r):
        parts = []

        # Elevation range
        low = r.get('ElevationLow_ft')
        high = r.get('ElevationHigh_ft')

        if pd.notna(low) and pd.notna(high):
            parts.append(f"Elevation: {int(low)}–{int(high)} ft")
        elif pd.notna(low):
            parts.append(f"Elevation: ≥ {int(low)} ft")
        elif pd.notna(high):
            parts.append(f"Elevation: ≤ {int(high)} ft")

        # Microhabitat (two columns)
        micro_parts = [
            str(r[col]).strip()
            for col in ["MicrohabitatDetails", "Microhabitat"]
            if pd.notna(r.get(col)) and str(r.get(col)).strip()
        ]
        if micro_parts:
            parts.append(f"Microhabitat: {'; '.join(micro_parts)}")

        # Other habitat fields
        mapping = {
            "BloomingPeriod": "Blooming Period", 
            "Habitat": "Habitat"
        }
        parts.extend(
            f"{label}: {r[col]}"
            for col, label in mapping.items()
            if pd.notna(r.get(col))
        )

        return join_lines(*parts)
    
    out["SpeciesDisplay"] = df.apply(build_species_display, axis=1)
    out["StatusDisplay"] = df.apply(build_status_display, axis=1)
    out["HabitatRequirements"] = df.apply(build_habitat_requirements, axis=1)

    out["PotentialtoOccur"] = ""
    out["HabitatSuitabilityObservations"] = ""
    out["Source"] = "CNPS" # 

    return out

# Format CNDDB for Potential to Occur table
def format_cnddb(df):
    out = pd.DataFrame()

    def build_species_display(r):
        return join_lines(r['SNAME'], r['CNAME'])

    def build_status_display(r):
        mapping = {
            'FEDLIST': 'Federal',
            'CALLIST': 'State',
            'RPLANTRANK': 'RPLANTRANK',
            'CDFWSTATUS': 'CDFW',
            'OTHRSTATUS': 'Other'
        }
        parts = [
            f"{label}: {r[col]}"
            for col, label in mapping.items()
            if pd.notna(r.get(col))
        ]
        return join_lines(*parts)
    
    def build_habitat_requirements(r):
        return join_lines(r['ECOLOGICAL'])

    out["SpeciesDisplay"] = df.apply(build_species_display, axis=1)
    out["StatusDisplay"] = df.apply(build_status_display, axis=1)
    out["HabitatRequirements"] = df.apply(build_habitat_requirements, axis=1)
    

    out["PotentialtoOccur"] = ""
    out["HabitatSuitabilityObservations"] = ""
    out["Source"] = "CNDDB" # tracking column, will be removed from final product

    return out

# ---------------------------------------------------------
# INITIALIZE SESSION STATE / LOAD RAW DATA
# ---------------------------------------------------------
# if "cnps_raw" not in st.session_state:
#     st.session_state.cnps_raw = pd.read_csv("app/data/CNPS_RAW.csv")

# if "cnddb_raw" not in st.session_state:
#     st.session_state.cnddb_raw = pd.read_csv("app/data/cnddb_test_data.csv")

# if "editor_version" not in st.session_state:
#     st.session_state.editor_version = 0
    

# ---------------------------------------------------------
# FILTER / QUERY SOURCE DATA
# ---------------------------------------------------------

# cnps_queried = st.session_state.cnps_raw.copy()

# # For now, use full CNDDB test data as queried result
# cnddb_queried = st.session_state.cnddb_raw.copy()

# Guard: stop the page from loading if the user hasn't run a search yet on the Landing Page.
# `results_ready` is set to True in page 1 after the buffer is applied and data is queried.
if not st.session_state.get("results_ready", False):
    st.warning("Please upload a boundary and apply a buffer on Page 1 first.")
    st.stop() # Halts execution of the rest of the page.

# Safety check: ensure `editor_version` exists in session state before reading it.
# This key is normally set by page 1, but this prevents a KeyError if page 3 is accessed unexpectedly.
if "editor_version" not in st.session_state:
    st.session_state.editor_version = 0

# Retrieve the editor version that page 3 last processed.
# Defaults to -1 so it never matches a real version on first load, forcing a format on first visit.
last_seen = st.session_state.get("last_editor_version", -1)

# Retrieve the current editor version, which page 1 increments every time a new search is run.
current_version = st.session_state.editor_version

# Only reformat the tables if the search has been updated since page 3 last ran.
# If versions match, the user just navigated back — preserve their edits to PotentialtoOccur etc.
# If versions differ, a new search was run — rebuild the table from the fresh filtered data.
if last_seen != current_version:
     # Reformat CNPS data from the filtered results saved by page 1.
    st.session_state.formatted_cnps = format_cnps(st.session_state.cnps_raw.copy())
    # Reformat CNDDB data from the filtered results saved by page 1.
    st.session_state.formatted_cnddb = format_cnddb(st.session_state.cnddb_raw.copy())
    # Update the last seen version so we don't reformat again until the next new search.
    st.session_state.last_editor_version = current_version

# ---------------------------------------------------------
# TRANSFORM RAW DATA INTO CLIENT-FACING FORMAT
# ---------------------------------------------------------
# formatted_cnps = format_cnps(cnps_queried).copy()
# formatted_cnddb = format_cnddb(cnddb_queried).copy()

# ---------------------------------------------------------
# STORE FORMATTED TABLES IN SESSION STATE
# ---------------------------------------------------------
# if "formatted_cnps" not in st.session_state:
#     st.session_state.formatted_cnps = formatted_cnps

# if "formatted_cnddb" not in st.session_state:
#     st.session_state.formatted_cnddb = formatted_cnddb

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
    key=st.session_state.editor_version
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
def make_buffer():
    
    buffer = BytesIO()

    doc = DocxTemplate("app/utils/pto_template.docx")

    edited_cnps = edited_combined[edited_combined["Source"] == "CNPS"].drop(columns=["_row_id"]).reset_index(drop=True)
    edited_cnddb = edited_combined[edited_combined["Source"] == "CNDDB"].drop(columns=["_row_id"]).reset_index(drop=True)

    st.session_state.formatted_cnps = edited_cnps
    st.session_state.formatted_cnddb = edited_cnddb

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

    return buffer


st.download_button(
    label="Export to Word",
    data=make_buffer,
    file_name="pto_report.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
)

