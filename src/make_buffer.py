import streamlit as st
from io import BytesIO
from docxtpl import DocxTemplate
import pandas as pd

def make_buffer():
    buffer = BytesIO()

    doc = DocxTemplate("src/pto_template.docx")

    # edited_combined = st.session_state.combined_pto.copy()

    if "_latest_editor" in st.session_state:
        edited_combined = st.session_state._latest_editor.copy()
<<<<<<< HEAD
    
=======

>>>>>>> 4803462ce6584d69bdc8082f99271a653c11f38b
    elif "combined_pto" in st.session_state:
        edited_combined = st.session_state.combined_pto.copy()
    else:
        st.error("No PTO table found. Please generate the table before exporting.")
        return None

    taxon_groups = []
<<<<<<< HEAD
    
=======

>>>>>>> 4803462ce6584d69bdc8082f99271a653c11f38b
    for taxon, group_df in edited_combined.groupby("Taxon_Category", dropna=False):
        taxon_groups.append({
            "TaxonGroup": taxon if pd.notna(taxon) and str(taxon).strip() else "Uncategorized",
            "rows": group_df.drop(columns=["_row_id"], errors="ignore").to_dict(orient="records")
            })

    context = {"taxon_groups": taxon_groups}


    try:
        doc.render(context, autoescape=True)
        doc.save(buffer)
    except Exception as e:
        st.error(f"Word export failed: {e}")
        return None

    buffer.seek(0)
<<<<<<< HEAD
    
=======

>>>>>>> 4803462ce6584d69bdc8082f99271a653c11f38b
    return buffer.getvalue()