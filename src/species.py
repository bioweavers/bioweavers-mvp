#%%
# Import necessary libraries.
from pathlib import Path
import requests
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
import pydeck as pdk
import json
import streamlit as st
#%%
# Create function to refactor the CNPS 'Quads' column
def refactor_cnps(file_path: str | Path) -> pd.DataFrame:
    '''
    Refactor the 'Quads' column in a CNPS CSV file to extract quad IDs as a list of integers.

    Parameters
    ----------
    file_path : str | Path
        Path to the California Native Plant Society CSV file

    Returns 
    ----------
    pd.DataFrame
        DataFrame with the 'Quads' column refactored to a new column 'split_quad' to extract quad IDs as a list of integers.

    Notes
    ----------
    Returns a DataFrame with an additional column 'split_quad' that contains the extracted quad IDs as lists of integers. 
    The original 'Quads' column is left unchanged.
    '''

    # Read the CNPS csv file
    file_path = Path(file_path)    

    cnps = pd.read_csv(file_path)

    # Refactor the 'Quads' column to extract the quad IDs as a list of integers
    cnps["split_quad"] = (cnps["Quads"].str.findall(r'\d+')).apply(
    lambda lst: [int(x) for x in lst] if isinstance(lst, list) else []
    )
    return cnps  
#%%
# Create a function to plot the distribution of CNDDB species occurrences.
def plot_cnddb_species_distribution(df):
    fig, ax = plt.subplots()
    ax.bar(df["OCCNUMBER"], df["SNAME"])
    ax.set_title("Species Distribution")
    ax.set_xlabel("Species Name")
    ax.set_ylabel("Number of Occurrences")
    return fig
# %%
# Create a function to plot the distribution of CNDDB species occurrences in Streamlit.
def plot_cnddb_species_distribution_streamlit(df):
    '''
        Plot the distribution of CNDDB species occurrences as a horizontal bar chart in Streamlit.
        
        Parameters
        -----------
        df : pd.DataFrame
            DataFrame containing the queried project specific CNDDB species occurrence data with at least 'SNAME' and 'OCCNUMBER' columns.
        
        Returns
        -----------
        Displays a horizontal bar chart in Streamlit showing the distribution of species occurrences, with species names on the y-axis and occurrence counts on the x-axis.
    '''
    
    # Drop geometry column for plotting.
    chart_data = df.drop(columns='geometry')
    
    # Group by ELMCODE, keep SNAME for display, calculate occurrence count.
    chart_data = (
        chart_data.groupby('ELMCODE', as_index=False)
        .agg(
            SNAME=('SNAME', 'first'),               # one name per species
            occurrence_count=('ELMCODE', 'count')   # how many occurrences in query
        )
        .sort_values('occurrence_count', ascending=False)
    )
    
    # Plot a horizontal bar chart of species occurrence counts.
    fig = px.bar(
        chart_data,
        x='occurrence_count',
        y='SNAME',
        category_orders={'SNAME': chart_data['SNAME'].tolist()},
        color_discrete_sequence=['#375673'],
        labels={
            'occurrence_count': 'Occurrence Count',
            'SNAME': 'Scientific Name'
        }
    )
    
    # Customize the layout for better aesthetics.
    fig.update_layout(
        height=600,
        font_family='Roboto',
        font_color='#333333',
        plot_bgcolor='white',
        yaxis=dict(gridcolor='#eeeeee'),
    )
    
    st.plotly_chart(fig, width='stretch')

#%%
# def plot_cnddb_species_date_range(df):
#     df = df.copy()
#     df["ELMDATE"] = pd.to_datetime(df["ELMDATE"], format="%Y%m%d")
#     df["LASTUPDATE"] = pd.to_datetime(df["LASTUPDATE"], format="%Y%m%d")
    
#     fig = px.timeline(df, 
#                       x_start="ELMDATE", 
#                       x_end="LASTUPDATE", 
#                       y="SNAME", 
#                       title="Species Occurrence Date Range")
    
#     fig.update_layout(xaxis_range=["1950-01-01", "2025-01-01"])

#     fig.show()
#     return fig
# %%

# def plot_species_map(cnddb_map_data: gpd.GeoDataFrame, boundary: gpd.GeoDataFrame, output_path: str = None):
    
#     # Reproject to WGS84
#     cnddb_wgs = cnddb_map_data.to_crs(epsg=4326)
#     boundary_wgs = boundary.to_crs(epsg=4326)
    
#     fig, ax = plt.subplots(figsize=(10, 10))
    
#     boundary_wgs.plot(ax=ax, 
#                       color="none", 
#                       edgecolor="black", 
#                       linewidth=2)
    
#     cnddb_wgs.plot(ax=ax, 
#                    column="SNAME", 
#                    legend=True, 
#                    alpha=0.6)

#     minx, miny, maxx, maxy = cnddb_wgs.total_bounds
#     padding = 0.1
#     ax.set_xlim(minx - padding, maxx + padding)
#     ax.set_ylim(miny - padding, maxy + padding)

#     ax.set_title("Species Occurrences in Project Area")
#     ax.set_xlabel("Longitude")
#     ax.set_ylabel("Latitude")
    
#     plt.tight_layout()
    
#     plt.show()

#%%
# def plot_species_map(cnddb_map_data: gpd.GeoDataFrame, boundary: gpd.GeoDataFrame, project_boundary_gdf: gpd.GeoDataFrame = None, output_path: str = None):
    
#     cnddb_wgs = cnddb_map_data.to_crs(epsg=3857)
#     boundary_wgs = boundary.to_crs(epsg=3857)

#     cnddb_clipped = gpd.clip(cnddb_wgs, boundary_wgs)
    
#     fig, ax = plt.subplots(figsize=(10, 10))

#     cnddb_clipped.plot(ax=ax, column="SNAME", legend=True, alpha=0.6, zorder=2)
#     boundary_wgs.plot(ax=ax, facecolor="none", edgecolor="blue", linewidth=2, zorder=3)  # buffer in blue

#     # Optionally overlay the original project boundary in red
#     if project_boundary_gdf is not None:
#         project_boundary_gdf.to_crs(epsg=3857).plot(ax=ax, facecolor="none", edgecolor="red", linewidth=2, zorder=4)

#     minx, miny, maxx, maxy = boundary_wgs.total_bounds
#     padding = 5000
#     ax.set_xlim(minx - padding, maxx + padding)
#     ax.set_ylim(miny - padding, maxy + padding)

#     ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zorder=1)

#     ax.set_title("Species Occurrences in Project Area")
#     ax.set_xlabel("Longitude")
#     ax.set_ylabel("Latitude")
    
#     plt.tight_layout()
#     st.pyplot(fig)

#%%
# Create a function to plot the species occurrences on an interactive map using PyDeck.
def plot_species_map_streamlit(cnddb_map_data: gpd.GeoDataFrame, boundary: gpd.GeoDataFrame, project_boundary_gdf: gpd.GeoDataFrame = None, output_path: str = None):
    '''
    Plot the species occurrences on an interactive map using PyDeck in Streamlit.
    
    Parameters
    -----------
    
    cnddb_map_data : gpd.GeoDataFrame
        GeoDataFrame containing the queried project specific CNDDB species occurrence data with geometry data.
    boundary : gpd.GeoDataFrame
        GeoDataFrame containing the buffered boundary geometry.
    project_boundary_gdf : gpd.GeoDataFrame, optional
        GeoDataFrame containing the original uploaded project boundary geometry, default is None.
    
    Returns
    -----------
    Displays an interactive map in Streamlit showing the species occurrences within the buffered search area, with the original project boundary overlaid if provided. 
    The map includes tooltips with species information.
    '''

    TAXONGROUP_COLORS = {
    'Amphibians': [253, 161, 106], 'Birds': [253, 161, 106], 'Fish': [253, 161, 106],
    'Mammals': [253, 161, 106], 'Reptiles': [253, 161, 106], 'Arachnids': [253, 161, 106],
    'Crustaceans': [253, 161, 106], 'Insects': [253, 161, 106], 'Mollusks': [253, 161, 106],
    'Bryophytes': [168, 204, 131], 'Dicots': [168, 204, 131], 'Ferns': [168, 204, 131],
    'Gymnosperms': [168, 204, 131], 'Lichens': [168, 204, 131], 'Monocots': [168, 204, 131],
    }

    # Reproject to WGS84 for PyDeck.
    cnddb_wgs = cnddb_map_data.to_crs(epsg=4326)
    boundary_wgs = boundary.to_crs(epsg=4326)

    # Reproject to projected CRS for buffering (California Albers)
    clip_mask = boundary.to_crs(epsg=3310) 

    # Buffer the boundary by 100 meters to ensure we capture nearby occurrences.
    clip_mask['geometry'] = clip_mask.geometry.buffer(100) 

    # Reproject the buffered mask back to WGS84 for clipping and mapping.
    clip_mask = clip_mask.to_crs(epsg=4326)  

    # Clip the species occurrences to the buffered boundary.
    cnddb_clipped = gpd.clip(cnddb_wgs, clip_mask)

    # Convert GeoDataFrames to GeoJSON format for PyDeck.
    def to_geojson(gdf):
        gdf = gdf.copy()
        for col in gdf.select_dtypes(include=['datetime64', 'datetimetz']).columns:
            gdf[col] = gdf[col].astype(str)
        return json.loads(gdf.to_json())

    # Add color columns based on TAXONGROUP
    default_color = [150, 150, 150]
    cnddb_clipped = cnddb_clipped.copy()
    cnddb_clipped['fill_color'] = cnddb_clipped['TAXONGROUP'].map(
    lambda x: TAXONGROUP_COLORS.get(x, default_color) + [150]  
    )
    cnddb_clipped['line_color'] = cnddb_clipped['TAXONGROUP'].map(
    lambda x: TAXONGROUP_COLORS.get(x, default_color)
    )

    # Create species layer. 
    species_layer = pdk.Layer(
        type="GeoJsonLayer",
        data=cnddb_clipped, 
        stroked=True,
        filled=True,
        get_fill_color='fill_color',    
        get_line_color='line_color',
        line_width_min_pixels=1,
        pickable=True,
    )

    # Create buffer layer to visualize the search area boundary.
    buffer_layer = pdk.Layer(
        type="GeoJsonLayer",
        data=boundary_wgs,
        stroked=True,
        filled=True,
        get_fill_color=[108, 173, 191, 80],
        get_line_color=[108, 173, 191],
        line_width_min_pixels=2,
    )

    # Add the original project boundary layer on top of the buffer and species layers.
    boundary_layer = pdk.Layer(
            type="GeoJsonLayer",
            data=project_boundary_gdf.to_crs(epsg=4326),
            stroked=True,
            filled=False,
            get_line_color="'#B22222'",
            line_width_min_pixels=2,
        )

    # Center the map on the project area.
    minx, miny, maxx, maxy = boundary_wgs.total_bounds
    center_lat = (miny + maxy) / 2
    center_lon = (minx + maxx) / 2

    # Set the initial view state of the map to center on the search area.
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11,
        pitch=0
    )

    # Define the layers.
    layers = [buffer_layer, species_layer, boundary_layer]

    # Map species, project boundary, and buffered search area layers using PyDeck.
    st.pydeck_chart(pdk.Deck(
        layers=layers,                                                                 # Map the defined layers to the map.
        initial_view_state=view_state,                                                 # Set the initial view state to center on the search area.
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",     # Add a basemap.
        # Configure tooltip to show species information on hover.
        tooltip={
    "html": "<b>{SNAME}</b> ({CNAME})<br/>"
            "<b>ELMCODE:</b> {ELMCODE}<br/>"
            "<b>OCCNUMBER:</b> {OCCNUMBER}<br/>"
            "<b>ELEVATION:</b> {ELEVATION}<br/>"
            "<b>PRESENCE:</b> {PRESENCE}<br/>"
            "<b>ELMDATE:</b> {ELMDATE}<br/>"
            "<b>LOCATION:</b> {LOCATION}<br/>"
            "<b>LOCDETAILS:</b> {LOCDETAILS}<br/>"
            "<b>ECOLOGICAL:</b> {ECOLOGICAL}<br/>"
            "<b>GENERAL:</b> {GENERAL}<br/>"
            "<b>LASTUPDATE:</b> {LASTUPDATE}",
    "style": {
        "fontSize": "11px",
        "maxWidth": "300px",
        "backgroundColor": "rgba(52,61,78,0.75)",
        "color": "white",
        "padding": "8px",
        "borderRadius": "4px",
    }
} 
    ))
#%%
# Create a function to plot the taxon group distribution as a pie chart in Streamlit.
def plot_taxon_pie_streamlit(cnddb_species):
    '''
    Plot the taxon group distribution of CNDDB species occurrences as a pie chart in Streamlit.
    
    Parameters
    -----------
    cnddb_species : pd.DataFrame
        DataFrame containing the queried project specific CNDDB species occurrence data.
        
    Returns
    -----------
    Displays a pie chart in Streamlit showing the distribution of species occurrences by taxon group.
    '''

    # Count the number of species in each taxon group.
    counts = cnddb_species['TAXONGROUP'].value_counts().reset_index()
    counts.columns = ['TAXONGROUP', 'count']
    
    # Create a pie chart of taxon group distributions.
    fig = px.pie(counts, names='TAXONGROUP', values='count', color_discrete_sequence=px.colors.qualitative.Set2)
    
    # Customize the layout for better aesthetics.
    fig.update_layout(
        height=600,
        font_family='Roboto',
        font_color='#333333',
    )
    
    st.plotly_chart(fig, width='stretch')