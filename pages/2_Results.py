# import streamlit as st
# import pandas as pd
# import folium
# from streamlit_folium import st_folium

# # Set the page configuration
# st.set_page_config(page_title='Results', layout='wide')

# st.title('Results')

# # Retrieve results from session state
# results = st.session_state.get('results')

# # If no results are available, show a warning and stop execution
# if results is None:
#     st.warning('No results available yet. Please go to the Input page and run the analysis first.')
#     st.stop()

# # Display results
# st.success(results.get('message', 'Analysis complete.'))

# # Display preview map again of uploaded boundary
# minx, miny, maxx, maxy = results["bounding_box"]

# m = folium.Map()

# # Fit map to boundary
# m.fit_bounds([[miny, minx], [maxy, maxx]])

# # Draw bounding box
# folium.Rectangle(
#     bounds=[[miny, minx], [maxy, maxx]],
#     color="blue",
#     weight=2,
#     fill=True,
#     fill_opacity=0.2
# ).add_to(m) # Add bounding box to map

# # Display map
# st_folium(m, width=700, height=500)

# # Summary metrics
# col1, col2, col3 = st.columns(3)
# col1.metric('CNPS Records', results['summary']['cnps_count'])
# col2.metric('CNDDB Records', results['summary']['cnddb_count'])
# col3.metric('Total Records', results['summary']['total_records'])

# st.subheader('Run Details')
# st.write(f'**Uploaded file:** {results.get('uploaded_filename', 'Unknown')}')
# st.write(f'**Search mode:** {results.get('search_mode', 'Unknown')}')
# st.write(f'**Bounding box:** {results.get('bounding_box', [])}')

# st.subheader('Quad IDs')
# st.write(results.get('quad_ids', []))

# # Display CNPS results in a table
# st.subheader('CNPS Results')
# cnps_df = pd.DataFrame(results.get('cnps_results', []))
# if cnps_df.empty:
#     st.info('No CNPS results returned.')
# else:
#     st.dataframe(cnps_df, use_container_width=True)

# # Button to download CNPS results as Excel
# #cnps_excel = cnps_df.to_excel(index=False)
# #st.download_button(label='Download CNPS Results (Excel)', data=cnps_excel, file_name='cnps_results.xlsx', excel_writer='xlsxwriter')

# # Display CNDDB results in a table
# st.subheader('CNDDB Results')
# cnddb_df = pd.DataFrame(results.get('cnddb_results', []))

# if cnddb_df.empty:
#     st.info('No CNDDB results returned.')
# else:
#     st.dataframe(cnddb_df, use_container_width=True)

# if not cnddb_df.empty:
#     st.subheader("Total Number of Occurrences per Species")

#     occurrence_counts = (
#         cnddb_df.groupby("scientific_name")
#         .size()
#         .reset_index(name="occurrence_count")
#         .sort_values("occurrence_count", ascending=False)
#     )

#     st.bar_chart(
#         occurrence_counts.set_index("scientific_name")
#     )

# if not cnddb_df.empty:
#     st.subheader("Total Number of Occurrences per Species")

#     occurrence_counts = (
#         cnddb_df.groupby("scientific_name")
#         .size()
#         .reset_index(name="occurrence_count")
#         .sort_values("occurrence_count", ascending=False)
#     )

#     st.bar_chart(
#         occurrence_counts.set_index("scientific_name")
#     )

# # Calculate date ranges for each species
# if not cnddb_df.empty and "observation_date" in cnddb_df.columns:
#     cnddb_df["observation_date"] = pd.to_datetime(
#         cnddb_df["observation_date"], errors="coerce"
#     )

#     date_ranges = (
#         cnddb_df.groupby("scientific_name")["observation_date"]
#         .agg(["min", "max"])
#         .reset_index()
#         .rename(columns={
#             "min": "earliest_date",
#             "max": "latest_date"
#         })
#     )

# # Date range table
# st.subheader("Date Range of Occurrences by Species")
# st.dataframe(date_ranges, use_container_width=True)
