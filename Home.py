# Import libraries
import streamlit as st

st.set_page_config(page_title='Bio Weaver Dashboard', layout='wide')

# Title of Landing Page
st.title('Bio Weaver MVP Dashboard')

# Navigation Instructions
st.header('Navigation Instructions')

st.markdown("""
Welcome! This tool allows you to:

1. Go to the **Input** page and upload your project boundary GeoJSON file.
2. Select your input parameters.
3. Run the analysis.
4. View and export results.

Use the sidebar to navigate between pages.
""")

# Initialize session state
if "results" not in st.session_state:
    st.session_state["results"] = None
