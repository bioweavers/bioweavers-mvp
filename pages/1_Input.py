# import streamlit as st
# import requests
# import folium
# from streamlit_folium import st_folium
# import tempfile
# from pathlib import Path
# import geopandas as gpd


# # had to install python-multipart to get this to work
# st.set_page_config(page_title='Input', layout='wide')

# st.title('Input')
# st.write('Upload a project boundary GeoJSON and run the analysis.')
# st.header('Upload Project Boundary')

# # Initialize session state
# if 'results' not in st.session_state:
#     st.session_state['results'] = None

# # File uploader
# uploaded_file = st.file_uploader(
#     'At the moment only accepts a GeoJSON file',
#     type=['geojson'],
#     accept_multiple_files=False,
#     help='Drag and drop a .geojson file here, or click to browse.'
# )

# # Display uploaded GeoJSON on a map
# st.header('Boundary Preview')

# if uploaded_file is not None:
#     try:
#         # Save uploaded file temporarily
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".geojson") as tmp:
#             tmp.write(uploaded_file.getvalue())
#             temp_path = Path(tmp.name)

#         # Read into GeoDataFrame
#         gdf = gpd.read_file(temp_path)

#         # Ensure CRS
#         if gdf.crs is None:
#             gdf.set_crs(epsg=4326, inplace=True)
#         else:
#             gdf = gdf.to_crs(epsg=4326)

#         if gdf.empty:
#             st.error("The uploaded GeoJSON contains no features.")
#         else:
#             # Create folium map without fixed zoom
#             m = folium.Map()

#             # Add GeoJSON
#             geojson_layer = folium.GeoJson(
#                 gdf,
#                 name="Boundary",
#                 style_function=lambda x: {
#                     "fillColor": "blue",
#                     "color": "black",
#                     "weight": 2,
#                     "fillOpacity": 0.3,
#                 },
#             )
#             geojson_layer.add_to(m)

#             # Fit map to uploaded boundary
#             m.fit_bounds(geojson_layer.get_bounds())

#             # Optional layer control
#             folium.LayerControl().add_to(m)

#             # Display map
#             st_folium(m, width=700, height=500)

#     except Exception as exc:
#         st.error("Could not read the uploaded GeoJSON.")
#         st.exception(exc)

# # Selection box for search radius
# st.header('Search Radius Criteria')

# search_mode = st.radio(
#     'Only one box may be selected:',
#     options=['9-quad search'],
#     help='Current MVP supports only 9-quad search.'
# )

# # API endpoint input
# api_url = st.text_input(
#     'FastAPI endpoint',
#     value='http://localhost:8000/analyze',
#     help='Change this only if the FastAPI server is running elsewhere.'
# )

# # Run analysis button
# if st.button('Run Analysis'):
#     if uploaded_file is None:
#         st.error('Please upload a GeoJSON file before running the analysis.')
#     else:
#         try:
#             files = {
#                 'boundary_file': (
#                     uploaded_file.name,
#                     uploaded_file.getvalue(),
#                     'application/geo+json'
#                 )
#             }

#             data = {
#                 'search_mode': search_mode
#             }

#             with st.spinner('Sending request to API...'):
#                 response = requests.post(
#                     api_url,
#                     files=files,
#                     data=data,
#                     timeout=60
#                 )

#             if response.status_code == 200:
#                 st.session_state['results'] = response.json()
#                 st.success('Analysis completed successfully. Go to the Results page.')
#             else:
#                 st.error(f'API request failed with status code {response.status_code}.')
#                 try:
#                     st.json(response.json())
#                 except Exception:
#                     st.text(response.text)

#         except requests.exceptions.RequestException as exc:
#             st.error('Could not connect to the FastAPI service.')
#             st.exception(exc)
