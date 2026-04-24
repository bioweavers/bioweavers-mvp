from utils.helper_functions import join_lines
import pandas as pd

# Format CNPS data for Potential to Occur output
def format_cnps(df):
    out = pd.DataFrame()
    
    def build_species_display(r):
        return join_lines(r['ScientificName'], r['CommonName'])

    def build_status_display(r):
        # Left: Label
        # Right: Column Name
        mapping = {
            'CRPR': 'CRPR',
            'CESA': 'CESA',
            'FESA': 'FESA',
            'Other Status': 'OtherStatus'
        }
        parts = [
            f"{label}: {r[col]}"
            for col, label in mapping.items()
            if pd.notna(r.get(col))
        ]
        return join_lines(*parts)

    def build_habitat_requirements(r):
        parts = []

        # Elevation range
        low = r.get('ElevationLow_ft')
        high = r.get('ElevationHigh_ft')

        if pd.notna(low) and pd.notna(high):
            parts.append(f"Elevation: {int(low)}–{int(high)} ft")
        elif pd.notna(low):
            parts.append(f"Elevation: ≥ {int(low)} ft")
        elif pd.notna(high):
            parts.append(f"Elevation: ≤ {int(high)} ft")

        # Microhabitat (two columns)
        micro_parts = [
            str(r[col]).strip()
            for col in ["MicrohabitatDetails", "Microhabitat"]
            if pd.notna(r.get(col)) and str(r.get(col)).strip()
        ]
        if micro_parts:
            parts.append(f"Microhabitat: {'; '.join(micro_parts)}")

        # Other habitat fields
        mapping = {
            "BloomingPeriod": "Blooming Period", 
            "Habitat": "Habitat"
        }
        parts.extend(
            f"{label}: {r[col]}"
            for col, label in mapping.items()
            if pd.notna(r.get(col))
        )

        return join_lines(*parts)
    
    out["SpeciesDisplay"] = df.apply(build_species_display, axis=1)
    out["StatusDisplay"] = df.apply(build_status_display, axis=1)
    out["HabitatRequirements"] = df.apply(build_habitat_requirements, axis=1)

    out["PotentialtoOccur"] = ""
    out["HabitatSuitabilityObservations"] = ""
    out["Source"] = "CNPS" # 

    return out

# Format CNDDB for Potential to Occur table
def format_cnddb(df):
    out = pd.DataFrame()

    def build_species_display(r):
        return join_lines(r['SNAME'], r['CNAME'])

    def build_status_display(r):
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
        return join_lines(r['ECOLOGICAL'])

    out["SpeciesDisplay"] = df.apply(build_species_display, axis=1)
    out["StatusDisplay"] = df.apply(build_status_display, axis=1)
    out["HabitatRequirements"] = df.apply(build_habitat_requirements, axis=1)
    

    out["PotentialtoOccur"] = ""
    out["HabitatSuitabilityObservations"] = ""
    out["Source"] = "CNDDB" # tracking column, will be removed from final product

    return out