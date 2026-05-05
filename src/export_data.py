import streamlit as st
from io import BytesIO
from docxtpl import DocxTemplate

def make_buffer():
    buffer = BytesIO()

    doc = DocxTemplate("src/pto_template.docx")

    # edited_combined = st.session_state.combined_pto.copy()

    if "_latest_editor" in st.session_state:
        edited_combined = st.session_state._latest_editor.copy()
    
    elif "combined_pto" in st.session_state:
        edited_combined = st.session_state.combined_pto.copy()
    else:
        st.error("No PTO table found. Please generate the table before exporting.")
        return None

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