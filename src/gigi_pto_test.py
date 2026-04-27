# demo_pto_export.py
import os
import pandas as pd
from pathlib import Path
from datetime import date
from docxtpl import DocxTemplate

from geometry import get_species_cnps, get_species_cnddb
from species import refactor_cnps


def build_cnps_records(df: pd.DataFrame) -> list[dict]:
    """Convert CNPS DataFrame rows into template-ready dicts."""
    records = []
    for _, row in df.iterrows():
        def safe(col):
            val = row.get(col)
            return str(val) if pd.notna(val) and val != "" else ""

        # Status block
        fesa = safe("FESA") or "None"
        cesa = safe("CESA") or "None"
        status = f"{fesa}/{cesa}\n{safe('GRank')}/{safe('SRank')}\nCRPR: {safe('CRPR')}"

        # Habitat block
        elev_low  = row.get("ElevationLow_ft")
        elev_high = row.get("ElevationHigh_ft")
        elev_str  = (f"Elevations: {float(elev_low):.0f}-{float(elev_high):.0f} ft. "
                     if pd.notna(elev_low) and pd.notna(elev_high) else "")
        bloom     = safe("BloomingPeriod")
        bloom_str = f"Blooms {bloom}." if bloom else ""
        habitat   = f"{safe('Habitat')} {elev_str}{bloom_str}".strip()

        records.append({
            "name":         safe("ScientificName"),
            "common_name":  safe("CommonName"),
            "status":       status,
            "habitat":      habitat,
            "pto":          "",   # filled in manually
            "observations": "",  # filled in manually
        })
    return records


def build_cnddb_records(df: pd.DataFrame) -> list[dict]:
    """Convert CNDDB DataFrame rows into the same template-ready dict shape."""
    records = []
    for _, row in df.iterrows():
        def safe(col):
            val = row.get(col)
            return str(val) if pd.notna(val) and val != "" else ""

        fed  = safe("FEDLIST") or "None"
        state = safe("STLIST") or "None"
        status = f"{fed}/{state}\n{safe('GRANK')}/{safe('SRANK')}"

        records.append({
            "name":         safe("SNAME"),
            "common_name":  safe("CNAME"),
            "status":       status,
            "habitat":      safe("ELMTYPE"),
            "pto":          "",
            "observations": "",
        })
    return records


def generate_pto_document(
    records: list[dict],
    template_path: str,
    output_path: str,
    project_name: str = "Sample Project",
    project_location: str = "Santa Barbara County, CA",
) -> Path:
    doc = DocxTemplate(template_path)
    context = {
        "project_name":     project_name,
        "project_location": project_location,
        "assessment_date":  date.today().strftime("%B %d, %Y"),
        "species_data":     records,
        "total_species":    len(records),
    }
    doc.render(context)
    out = Path(output_path)
    doc.save(out)
    return out


def main():
    base = Path(__file__).parent

    # Load & filter CNPS
    cnps_df  = refactor_cnps(base / ".." / "data" / "CNPS_RAW.csv")
    quad_ids = {3411814, 3411815, 3411816, 3411824, 3411825, 3411826}
    cnps_filtered = get_species_cnps(cnps_df, quad_ids)  # note: function is get_species in geometry.py

    # Load & filter CNDDB (uncomment when ready)
    cnddb_filtered = get_species_cnddb(base / ".." / "data" / "cnddb_test_data.csv", quad_ids)

    # Build records — combine if using both sources
    records = build_cnps_records(cnps_filtered)
    records += build_cnddb_records(cnddb_filtered)

    print(f"Found {len(records)} species in quads")

    output_path = base / "gigi_output_pto_report.docx"
    result = generate_pto_document(
        records=records,
        template_path=str(base / "pto_template2.docx"),
        output_path=str(output_path),
        project_name="Palisades Fire Boundary",
        project_location="Los Angeles County, CA",
    )
    print(f"✓ Generated: {result}")


if __name__ == "__main__":
    main()