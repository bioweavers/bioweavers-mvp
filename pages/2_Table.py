import pandas as pd
import streamlit as st
from io import BytesIO
from docxtpl import DocxTemplate
#added library
import zipfile

#from ..app.utils.format_data import format_cnps, format_cnddb

# Add title to the page.
st.title('Export Results as a Word Document')

# Add header.
st.header('Project Potential to Occur Table', divider=True)

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

        status_cols = [
            'CRPR',
            'CESA',
            'FESA',
            'OtherStatus'
        ]

        parts = [
            str(r[col]).strip()
            for col in status_cols
            if pd.notna(r.get(col)) and str(r.get(col)).strip()
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
            "Habitat": "Habitat",
            "BloomingPeriod": "Blooming Period"
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
    out["Source"] = "CNPS" # tracking column, will be removed from final product
    out["TaxonGroup"] = "Plants and Lichens"

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
    #out["TaxonGroup"] = df.TAXONGROUP

    return out

# ---------------------------------------------------------
# EDITOR CALLBACK
# ---------------------------------------------------------
def update_pto_table():
    edits = st.session_state.pto_editor.get("edited_rows", {})

    for row_idx, changes in edits.items():
        for col_name, new_value in changes.items():
            if col_name in ["PotentialtoOccur", "HabitatSuitabilityObservations"]:
                st.session_state.combined_pto.loc[row_idx, col_name] = new_value

# ---------------------------------------------------------
# INITIALIZE SESSION STATE / LOAD RAW DATA
# ---------------------------------------------------------
if "cnps_raw" not in st.session_state:
    st.session_state.cnps_raw = pd.read_csv("app/data/CNPS_RAW.csv")

if "cnddb_raw" not in st.session_state:
    st.session_state.cnddb_raw = pd.read_csv("app/data/cnddb_test_data.csv")

if "editor_version" not in st.session_state:
    st.session_state.editor_version = 0


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
# COMBINE FOR DISPLAY/EDITING IN ONE EDITOR
# ---------------------------------------------------------
if "combined_pto" not in st.session_state:
    combined_display = pd.concat(
        [st.session_state.formatted_cnps, st.session_state.formatted_cnddb],
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
        num_rows="dynamic",
        width="stretch",
        disabled=["_row_id", "Source", "SpeciesDisplay", "StatusDisplay", "HabitatRequirements"],
        hide_index=True,
        key="pto_editor_form_table",
    )

    save_clicked = st.form_submit_button("Save Edits")

if save_clicked:
    st.session_state.combined_pto = edited_combined.copy()
    st.success("Edits saved.")

# ---------------------------------------------------------
# EXPORT TO WORD
# ---------------------------------------------------------
def make_buffer():
    buffer = BytesIO()

    doc = DocxTemplate("app/utils/pto_template.docx")

    edited_combined = st.session_state.combined_pto.copy()

    edited_cnps = edited_combined[
        edited_combined["Source"] == "CNPS"
    ].drop(columns=["_row_id"]).reset_index(drop=True)

    edited_cnddb = edited_combined[
        edited_combined["Source"] == "CNDDB"
    ].drop(columns=["_row_id"]).reset_index(drop=True)

    context = {
        "cnps_rows": edited_cnps.to_dict(orient="records"),
        "cnddb_rows": edited_cnddb.to_dict(orient="records"),
    }

    try:
        doc.render(context, autoescape=True)
        doc.save(buffer)
    except Exception as e:
        st.error(f"Word export failed: {e}")
        return None

    buffer.seek(0)
    
    return buffer.getvalue()


# st.download_button(
#     label="Export to Word",
#     data=make_buffer(),
#     file_name="pto_report.docx",
#     mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
# )

docx_bytes = make_buffer()

if docx_bytes is not None:
    st.download_button(
        label="Export to Word",
        data=docx_bytes,
        file_name="pto_report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )