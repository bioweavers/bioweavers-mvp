"""
Generate PTO Word Document from DataFrame

This shows how to use docxtpl to generate a Word document
with a dynamic table from a pandas DataFrame.

Usage:
    python demo_pto_export.py

Requirements:
    pip install python-docx docxtpl pandas
"""

import pandas as pd
import os
from pathlib import Path
from datetime import date
from docxtpl import DocxTemplate, RichText

from geometry import get_species_cnps
from species import refactor_cnps

# Query results- temporary for checking functionality 
# Read in CNPS data
#cnps_df = refactor_cnps(os.path.join(os.path.dirname(__file__), "..", "data", "CNPS_RAW.csv"))

# Define quad IDs
#quad_ids = {3211465}  

# Get filtered species
#tmp_df = get_species_cnps(cnps_df, quad_ids)


def generate_pto_document(
    species_df: pd.DataFrame, #would we need 2? for cnps and cnddb
    template_path: str,
    output_path: str,
    project_name: str = "Sample Project",
    project_location: str = "Santa Barbara County, CA",
) -> Path:
    """
    Generate a PTO assessment Word document from a CNPS species DataFrame.

    Parameters
    ----------
    species_df : pd.DataFrame
        DataFrame containing CNPS species data with columns: ScientificName, 
        CommonName, FESA, CESA, GRank, SRank, CRPR, Habitat, ElevationLow_ft,
        ElevationHigh_ft, BloomingPeriod.
    template_path : str
        Path to the Word template (.docx) with Jinja2 placeholders.
    output_path : str
        Where to save the generated document.
    project_name : str
        Project name for the document header.
    project_location : str
        Project location description.

    Returns
    -------
    Path
        Path to the generated document.
    """
    # Load template
    doc = DocxTemplate(template_path)

    # Build species records formatted for the template
    species_data = []
    for _, row in species_df.iterrows(): # works for CNPS not CNDDB
        # Format status block
        fesa = row.get("FESA", "None") if pd.notna(row.get("FESA")) else "None"
        cesa = row.get("CESA", "None") if pd.notna(row.get("CESA")) else "None"
        grank = row.get("GRank", "") if pd.notna(row.get("GRank")) else ""
        srank = row.get("SRank", "") if pd.notna(row.get("SRank")) else ""
        crpr = row.get("CRPR", "") if pd.notna(row.get("CRPR")) else ""

        status = f"{fesa}/{cesa}\n{grank}/{srank}\n{crpr}"

        # Format habitat block
        habitat = row.get("Habitat", "") if pd.notna(row.get("Habitat")) else ""
        elev_low = row.get("ElevationLow_ft", "") if pd.notna(row.get("ElevationLow_ft")) else ""
        elev_high = row.get("ElevationHigh_ft", "") if pd.notna(row.get("ElevationHigh_ft")) else ""
        bloom = row.get("BloomingPeriod", "") if pd.notna(row.get("BloomingPeriod")) else ""

        habitat_text = f"{habitat} Elevations: {elev_low:.0f}-{elev_high:.0f}ft. Blooms {bloom}."

        # Format scientific and common name
        name = row.get("ScientificName", "") # TODO: Do we want to let empty species names through?? Or error?
        #name.add("\n")
        #name.add(row.get("CommonName", ""))

        common_name = row.get("CommonName", "")
        species_data.append({
            "name": name,
            "common_name": common_name,
            "status": status,
            "habitat": habitat_text,
        })

    
    # Build context for template
    context = {
        "project_name": project_name,
        "project_location": project_location,
        "assessment_date": date.today().strftime("%B %d, %Y"),
        "species_data": species_data,
        "total_species": len(species_df),
    }

    # Render and save
    doc.render(context)
    output = Path(output_path)
    doc.save(output)
    return output


def main():
    """Run the demo."""
    
    # Check for template
    template_path = Path(__file__).parent / 'pto_template2.docx'
    #if not template_path.exists():
        #print("Template not found. Creating it first...")
        #print("Run: python create_template.py")
        #print("Or run this script again after creating the template.")
        
        # Auto-create template
        #import create_template
        #create_template.create_pto_template()
    
    # Create DataFrame from CNPS 
    # Load and filter CNPS data
    cnps_path = os.path.join(os.path.dirname(__file__), "..", "data", "CNPS_RAW.csv")
    cnps_df = refactor_cnps(cnps_path)

    # Load and filter CNDDB data
    cnddb_path = os.path.join(os.path.dirname(__file__), "..", "data", "cnddb_test_data.csv")

    # Define quad IDs
    quad_ids = {3411814, 3411815, 3411816, 3411824, 3411825, 3411826}  

    df = get_species_cnps(cnps_df, quad_ids)
    # df = get_species_cnddb(cnddb_path, quad_ids)
    # how to join/whether to join these? maybe create if else for formatting 

    print(f"Found {len(df)} species in quads")
    
    # Generate document
    output_path = Path(__file__).parent / 'output_pto_report.docx'
    
    result = generate_pto_document(
        species_df=df,
        template_path=str(template_path),
        output_path=str(output_path),
        project_name="Palisades Fire Boundary",
        project_location="Los Angeles County, CA"
    )
    
    print(f"✓ Generated: {result}")
    print(f"  • {len(df)} species in table")
    print(f"  • Open in Word to verify formatting")


if __name__ == '__main__':
    main()
