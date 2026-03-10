"""
Demo: Generate PTO Word Document from DataFrame

This shows how to use docxtpl to generate a Word document
with a dynamic table from a pandas DataFrame.

Usage:
    python demo_pto_export.py

Requirements:
    pip install python-docx docxtpl pandas
"""

#%%

import pandas as pd
from pathlib import Path
from datetime import date
from docxtpl import DocxTemplate

#%%

# Sample species data (simulating query results)
SAMPLE_DATA = [
    {
        'scientific_name': 'Rana draytonii',
        'common_name': 'California red-legged frog',
        'status': 'FT',
        'pto': 'High',
        'rationale': 'Suitable aquatic habitat present; documented occurrences within 2 miles'
    },
    {
        'scientific_name': 'Polioptila californica californica',
        'common_name': 'Coastal California gnatcatcher',
        'status': 'FT',
        'pto': 'Moderate',
        'rationale': 'Coastal sage scrub habitat present; nearest occurrence 5 miles'
    },
    {
        'scientific_name': 'Empidonax traillii extimus',
        'common_name': 'Southwestern willow flycatcher',
        'status': 'FE',
        'pto': 'Not Expected',
        'rationale': 'Project site lacks riparian willow habitat required for nesting'
    },
    {
        'scientific_name': 'Athene cunicularia',
        'common_name': 'Burrowing owl',
        'status': 'SSC',
        'pto': 'Moderate',
        'rationale': 'Open grassland habitat suitable for foraging; ground squirrel burrows present'
    },
    {
        'scientific_name': 'Taricha torosa',
        'common_name': 'Coast Range newt',
        'status': 'SSC',
        'pto': 'Low',
        'rationale': 'Marginal upland habitat; no breeding ponds within 1 mile'
    },
]

#%%

def generate_pto_document(
    species_df: pd.DataFrame,
    template_path: str,
    output_path: str,
    project_name: str = "Sample Project",
    project_location: str = "Santa Barbara County, CA",
    buffer_radius: str = "5-mile"
) -> Path:
    """
    Generate a PTO assessment Word document from a species DataFrame.
    
    Parameters
    ----------
    species_df : pd.DataFrame
        DataFrame with columns: scientific_name, common_name, status, pto, rationale
    template_path : str
        Path to the Word template (.docx) with Jinja2 placeholders
    output_path : str
        Where to save the generated document
    project_name : str
        Project name for the header
    project_location : str
        Project location description
    buffer_radius : str
        Buffer radius used for analysis
        
    Returns
    -------
    Path
        Path to the generated document
    """
    # Load template
    doc = DocxTemplate(template_path)
    
    # Convert DataFrame to list of dicts for Jinja2
    species_data = species_df.to_dict('records')
    
    # Count species with potential
    not_expected_count = len(species_df[species_df['pto'] == 'Not Expected'])
    with_potential = len(species_df) - not_expected_count
    
    # Build context for template
    context = {
        'project_name': project_name,
        'project_location': project_location,
        'buffer_radius': buffer_radius,
        'assessment_date': date.today().strftime('%B %d, %Y'),
        'species_data': species_data,
        'total_species': len(species_df),
        'species_with_potential': with_potential,
    }
    
    # Render and save
    doc.render(context)
    output = Path(output_path)
    doc.save(output)
    
    return output

#%%

# Example usage:
# Commented out to avoid running it by default
''' 
template_path = Path(__file__).parent / 'pto_template.docx'
df = pd.DataFrame(SAMPLE_DATA)
output_path = Path(__file__).parent / 'output_pto_report.docx'
result = generate_pto_document(
    species_df=df,
    template_path=str(template_path),
    output_path=str(output_path),
    project_name="Coastal Development Project",
    project_location="Goleta, Santa Barbara County, CA",
    buffer_radius="5-mile"
)
'''

