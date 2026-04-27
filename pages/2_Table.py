import pandas as pd
import streamlit as st
from io import BytesIO
from docxtpl import DocxTemplate

#from ..app.utils.format_data import format_cnps, format_cnddb

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
if "cnps_raw" not in st.session_state:
    st.session_state.cnps_raw = pd.read_csv("app/data/CNPS_RAW.csv")

if "cnddb_raw" not in st.session_state:
    st.session_state.cnddb_raw = pd.read_csv("app/data/cnddb_test_data.csv")

if "editor_version" not in st.session_state:
    st.session_state.editor_version = 0
    

# ---------------------------------------------------------
# FILTER / QUERY SOURCE DATA
# ---------------------------------------------------------
# cnps_queried = st.session_state.cnps_raw[
#     st.session_state.cnps_raw["Quads"].str.contains(
#         "Boulder Peak (4112351)",
#         case=False,
#         na=False,
#         regex=False
#     )
# ].copy()

cnps_queried = st.session_state.cnps_raw.copy()

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

