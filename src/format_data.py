import pandas as pd


def join_lines(*parts):
    """
    Combine multiple text fields into one newline-separated string.

    This helper removes missing values, blank strings, and extra whitespace
    before joining the remaining values with line breaks.

    Parameters
    ----------
    *parts : any
        Text-like values to combine. Values may come from dataframe columns.

    Returns
    -------
    str
        A newline-separated string containing only non-empty values.

    Example
    -------
    join_lines("ScientificName","", "CommonName")
    returns:
        "Scientific name\\nCommon name"
    """
    cleaned = [str(p).strip() for p in parts if pd.notna(p) and str(p).strip()]
    return "\n".join(cleaned)

# Format CNPS data for Potential to Occur output
def format_cnps(df):
    """
    Format raw CNPS data for the Potential to Occur editable table.

    This function convers CNPS source columns into the standardized columns
    used by the Streamlit PTO table and Word export.

    Expected Input Columns
    ----------
    ScientificName
    CommonName
    CRPR
    CESA
    FESA
    OtherStatus
    ElevationLow_ft
    ElevationHigh_ft
    MicrohabitatDetails
    Microhabitat
    Habitat
    BloomingPeriod

    Output Columns
    ----------
    SpeciesDisplay
        Scientific and common name combined into one display field.

    StatusDisplay
        CNPS and regulatory status fields combined into one display field.

    PotentialtoOccur
        Blank editable field for user-entered PTO determination.

    HabitatSuitabilityObservations
        Blank editable field for user-entered habitat observations.

    Source
        Tracking column identifying the row as coming from CNPS.

    Taxon_Category
        Fixed as "Plants and Lichens" because CNPS records are plant-focused.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw CNPS dataframe.

    Returns
    -------
    pandas.DataFrame
        Formatted CNPS dataframe ready to combine with formatted CNDDB data.
    """
    out = pd.DataFrame()
    
    def build_species_display(r):
        """
        Build the species display field from the scientific and common names
        """
        return join_lines(r['ScientificName'], r['CommonName'])

    def build_status_display(r):
        """
        Build a compact status summary from CNPS status fields
        """

        status_cols = [
            'CRPR',
            'CESA',
            'FESA',
            'OtherStatus'
        ]

        parts = [
            str(r[col]).strip()
            for col in status_cols
            if pd.notna(r.get(col)) and str(r.get(col)).strip()
        ]

        return join_lines(*parts)

    def build_habitat_requirements(r):
        """
        Build a readable habitat requirements summary for one CNPS row.

        Includes elevation range, microhabitat fields, general habitat,
        and blooming period when available.
        """
        parts = []

        # Add elevation range if low and/or high elevation values exist
        low = r.get('ElevationLow_ft')
        high = r.get('ElevationHigh_ft')

        if pd.notna(low) and pd.notna(high):
            parts.append(f"Elevation: {int(low)}–{int(high)} ft")
        elif pd.notna(low):
            parts.append(f"Elevation: ≥ {int(low)} ft")
        elif pd.notna(high):
            parts.append(f"Elevation: ≤ {int(high)} ft")

        # Combine the two microhabitat fields when available
        micro_parts = [
            str(r[col]).strip()
            for col in ["MicrohabitatDetails", "Microhabitat"]
            if pd.notna(r.get(col)) and str(r.get(col)).strip()
        ]
        if micro_parts:
            parts.append(f"Microhabitat: {'; '.join(micro_parts)}")

        # Add other habitat-related fields
        mapping = {
            "Habitat": "Habitat",
            "BloomingPeriod": "Blooming Period"
        }
        parts.extend(
            f"{label}: {r[col]}"
            for col, label in mapping.items()
            if pd.notna(r.get(col))
        )

        return join_lines(*parts)

    # Build standardized PTO display columns
    out["SpeciesDisplay"] = df.apply(build_species_display, axis=1)
    out["StatusDisplay"] = df.apply(build_status_display, axis=1)
    out["HabitatRequirements"] = df.apply(build_habitat_requirements, axis=1)

    # Add blank user-editable fields
    out["PotentialtoOccur"] = ""
    out["HabitatSuitabilityObservations"] = ""

    # Add metadata/tracking fields
    out["Source"] = "CNPS"
    out["Taxon_Category"] = "Plants and Lichens"

    return out

# Format CNDDB for Potential to Occur table
def format_cnddb(df):
    """
    Format raw CNDDB data for the Potential to Occur editable table.

    This function converts CNDDB source columns into the standardized columns
    used by the Streamlit PTO table and Word export.

    Expected Input Columns
    ----------
    SNAME
    CNAME
    FEDLIST
    CALLIST
    RPLANTRANK
    CDFWSTATUS
    OTHRSTATUS
    ECOLOGICAL
    TAXONGROUP

    Output Columns
    ----------
    SpeciesDisplay
        Scientific and common name combined into one display field.

    StatusDisplay
        Federal, state, plant rank, CDFW, and other status fields combined
        into one display field.

    HabitatRequirements
        Ecological description from CNDDB.

    PotentialtoOccur
        Blank editable field for user-entered PTO determination.

    HabitatSuitabilityObservations
        Blank editable field for user-entered habitat observations.

    Source
        Tracking column identifying the row as coming from CNDDB.

    Taxon_Category
        Standardized taxon category used for table grouping and Word export.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw CNDDB dataframe.

    Returns
    -------
    pandas.DataFrame
        Formatted CNDDB dataframe ready to combine with formatted CNPS data.

    """
    out = pd.DataFrame()

    def build_species_display(r):
        """
        Build the species display field from scientific and common names.
        """
        return join_lines(r['SNAME'], r['CNAME'])

    def build_status_display(r):
        """
        Build a readable regulatory status summary for one CNDDB row.
        """
        mapping = {
            'FEDLIST': 'Federal',
            'CALLIST': 'State',
            'RPLANTRANK': 'RPLANTRANK',
            'CDFWSTATUS': 'CDFW',
            'OTHRSTATUS': 'Other'
        }
        parts = [
            f"{label}: {r[col]}"
            for col, label in mapping.items()
            if pd.notna(r.get(col))
        ]
        return join_lines(*parts)
    
    def build_habitat_requirements(r):
        """
        Build the habitat requirements field from the CNDDB ecological text.
        """
        return join_lines(r['ECOLOGICAL'])
    
    def map_taxon_category(taxon_group):
        """
        Convert CNDDB taxon groups into standardized categories.

        CNDDB uses more detailed taxon group labels than the Streamlit table
        needs. This helper maps those detailed labels into broader categories
        used for grouping, filtering, display, and export.

        Any unrecognized taxon group is labeled as "Other".
        """
        mapping = {

            
            'Amphibians': 'Amphibians',
            'Birds': 'Birds',
            'Fish': 'Fish',
            'Mammals': 'Mammals',
            'Reptiles': 'Reptiles',

            'Bryophytes': 'Plants and Lichens',
            'Dicots': 'Plants and Lichens',
            'Ferns': 'Plants and Lichens',
            'Gymnosperms': 'Plants and Lichens',
            'Lichens': 'Plants and Lichens',
            'Monocots': 'Plants and Lichens',

            'Arachnids': 'Invertebrates',
            'Crustaceans': 'Invertebrates',
            'Insects': 'Invertebrates',
            'Mollusks': 'Invertebrates',

            'Dune': 'Community',
            'Forest': 'Community',
            'Herbaceous': 'Community',
            'Inland Waters': 'Community',
            'Marsh': 'Community',
            'Riparian':  'Community',
            'Scrub': 'Community',
            'Woodland': 'Community'
        }

        return mapping.get(str(taxon_group).strip(), "Other")

    # Build standardized PTO display columns
    out["SpeciesDisplay"] = df.apply(build_species_display, axis=1)
    out["StatusDisplay"] = df.apply(build_status_display, axis=1)
    out["HabitatRequirements"] = df.apply(build_habitat_requirements, axis=1)
    
    # Add blank user-editable fields
    out["PotentialtoOccur"] = ""
    out["HabitatSuitabilityObservations"] = ""

    # Add metadata/tracking fields
    out["Source"] = "CNDDB"
    out["Taxon_Category"] = df["TAXONGROUP"].apply(map_taxon_category)

    return out
