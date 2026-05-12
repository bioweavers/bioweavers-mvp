import pandas as pd

# Join non empty lines
def join_lines(*parts):
    cleaned = [str(p).strip() for p in parts if pd.notna(p) and str(p).strip()]
    return "\n".join(cleaned)

# Format CNPS data for Potential to Occur output
def format_cnps(df):
    out = pd.DataFrame()

    def build_species_display(r):
        return join_lines(r['ScientificName'], r['CommonName'])

    def build_status_display(r):

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
            "Habitat": "Habitat",
            "BloomingPeriod": "Blooming Period"
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
    out["Source"] = "CNPS" # tracking column, will be removed from final product
    out["Taxon_Category"] = "Plants and Lichens"

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

    def map_taxon_category(taxon_group):
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

    out["SpeciesDisplay"] = df.apply(build_species_display, axis=1)
    out["StatusDisplay"] = df.apply(build_status_display, axis=1)
    out["HabitatRequirements"] = df.apply(build_habitat_requirements, axis=1)


    out["PotentialtoOccur"] = ""
    out["HabitatSuitabilityObservations"] = ""
    out["Source"] = "CNDDB" # tracking column, will be removed from final product
    out["Taxon_Category"] = df["TAXONGROUP"].apply(map_taxon_category)

    return out