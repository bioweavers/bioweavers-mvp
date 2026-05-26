# Import necessary libraries
import streamlit as st

bioweaver_logo = 'images/Bioweaver_logo.png'

st.set_page_config(layout="wide", page_title="Bio Weaver Tool", page_icon=bioweaver_logo)

# Add Bio Weaver Tool logo (can be changed)
col1, col2, col3 = st.columns([1.4, 1, 1.4])
with col2:
    st.image(bioweaver_logo, width='stretch')

# Add the Rincon logo to the top left of the page.
rincon_logo = 'images/Rincon_Logo_Color.png'
st.logo(rincon_logo, size='large')

# Add page title.
st.title("Welcome to the Bio Weaver Tool!", 
         width='stretch', 
         text_alignment='center')

# Add page header.
st.header("Explore California wildlife species occurrences within your project area.", 
          width='stretch', 
          text_alignment='center')

# Add text to describe the Bio Weaver Tool.
st.text("This dashboard extracts data from the California Native Plant Society and California Natural Diversity Database to generate a project-specific map and Potential to Occur Table.",
        width='stretch',
        text_alignment='center')

# Add page divider.
st.divider()

# Add page header.
st.header("Navigate through the dashboard...", 
            width='stretch', 
            text_alignment='center')

# Add page navigation text.
st.markdown("<p style='font-size:20px'><strong>Spatial Search Page:</strong> Upload your project boundary and apply a buffer.</p>", 
            unsafe_allow_html=True, text_alignment='center')
st.markdown("<p style='font-size:20px'><strong>Results Page:</strong> View species found in your project area.</p>", 
            unsafe_allow_html=True, text_alignment='center')
st.markdown("<p style='font-size:20px'><strong>Table Page:</strong> Review the Potential to Occur Table and export to Word.</p>", 
            unsafe_allow_html=True, text_alignment='center')

# Styling for the page link button.
st.markdown("""
    <style>
    [data-testid="stPageLink"] a {
        background-color: #375673;
        color: var(--primary-foreground-color) !important;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 16px;
    }
    [data-testid="stPageLink"] a p {
    color: #FFFFFF !important;
    }
    [data-testid="stPageLink"] a:hover {
        background-color: #375673;
        opacity: 0.85;
        color: #FFFFFF !important;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 16px;
        opacity: 0.6
    }
    </style>
""", unsafe_allow_html=True)

with st.container(horizontal=True):
    st.space("stretch")
    # Add a button to navigate to the Results page, once steps on Landing page are completed.
    st.page_link("pages/1_Search.py", label="Start Your Analysis", width='content', icon_position="right")
    st.space("stretch")

