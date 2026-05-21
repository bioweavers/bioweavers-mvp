import streamlit as st
from io import BytesIO
from docxtpl import DocxTemplate
import pandas as pd

def make_buffer():
    """
    Generate a Word document export from the current Potential to Occur table.

    This function pulls the most recent editable PTO table from Streamlit's session state,
    organizes the records by taxon category, renders those records into a Words template
    using docxtpl, and returns the completed document as bytes.

    The returned bytes can be passed directly into st.download_button().

    Session State Priority
    -------
    the function cheks Streamlit session state in this order:

    1. st.session-state._latest_editor
        - Used when the user has edited the table and clicked save.
        - This should represent the most recent user-edited version.

    2. st.session_state.combined_pto
        - Used as a fallback if no saved editor version exists.
        - This usually represents the original generated PTO table.

    If neither key exists, the function displays a Streamlit error message
    and returns None.

    Word Template Requirements
    -------
    The function expects a Word template at

        src/pto_template.docx

    The template must be compatible with a context dictionary containing:

    {
            "taxon_groups": [
                {
                    "TaxonGroup": "Birds",
                    "rows": [
                        {"SpeciesDisplay": "...", "Potential_to_Occur": "..."},
                        ...
                    ]
                },
                ...
            ]
        }

    Each taxon group contains:
        - TaxonGroup: the taxon category name shown as a group heading
        - rows: a list of dictionaries representing species rows

    Returns
    -------
    bytes or None
        Returns the generated Word document as bytes if successful.
        Returns None of no table is available or if rendering/export fails.

    Notes
    -------
    The internal '_row_id' column is removed before export because it is only
    used to track rows inside the Streamlit app and should not appear in the
    final report.
    """

    # Create an in-memory binary buffer.
    # This avoids saving the exported document to disk.
    buffer = BytesIO()

    # Load the Word template used for the PTO report.
    doc = DocxTemplate("src/pto_template.docx")

    # Use the latest saved version of the editable table, if available
    # This makes sure user edits are included in the exported Word document.
    if "_latest_editor" in st.session_state:
        edited_combined = st.session_state._latest_editor.copy()

    # If neither table exists, the app cannot generate the report.
    elif "combined_pto" in st.session_state:
        edited_combined = st.session_state.combined_pto.copy()
    else:
        st.error("No PTO table found. Please generate the table before exporting.")
        return None

    # Build a list of taxon groups for the Word template
    taxon_groups = []

    # Group species by taxon category
    # dropna=False keeps rows with missing Taxon_Category values instead of excluding them
    for taxon, group_df in edited_combined.groupby("Taxon_Category", dropna=False):

        # Append one taxon section to the template context
        taxon_groups.append({
            # Use "Uncategorized" if the taxon category is missing or blank
            "TaxonGroup": taxon if pd.notna(taxon) and str(taxon).strip() else "Uncategorized",
            "rows": group_df.drop(columns=["_row_id"], errors="ignore").to_dict(orient="records")
            })

    # Context dictionary passed into the Word template
    context = {"taxon_groups": taxon_groups}


    try:
        # Render the Word template with the grouped taxon data
        # autoescape=True helps prevent special characters from breaking
        # the Word template rendering
        doc.render(context, autoescape=True)

        # Save the rendered document into the in-memory buffer
        doc.save(buffer)
    except Exception as e:
        # Show an error in Streamlit app if export fails
        st.error(f"Word export failed: {e}")
        return None

    # Move the buffer position back to the beginning before reading it
    buffer.seek(0)

    # Return the final Word document as bytes
    return buffer.getvalue()
