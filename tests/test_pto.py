"""Tests for the PTO (Potential to Occur) Word-document export pipeline.

Covers:
  * build_cnps_records / build_cnddb_records — DataFrame row -> template dict.
  * generate_pto_document — record list -> rendered .docx via docxtpl.
  * An end-to-end integration test that mirrors the original demo script,
    skipping gracefully when fixture data or templates are missing.

Also runnable as a script (``python tests/test_pto.py``) to regenerate
the demo document into the repo's outputs directory.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest
from docxtpl import DocxTemplate

from src.geometry import get_species_cnps, get_species_cnddb
from src.species import refactor_cnps


# --- repo paths ------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
TEMPLATE_PATH = REPO_ROOT / "src" / "pto_template2.docx"
CNPS_CSV = DATA_DIR / "CNPS_RAW.csv"
CNDDB_CSV = DATA_DIR / "cnddb_test_data.csv"


# --- module under test (keep these here so the demo still runs as a script) ---

def build_cnps_records(df: pd.DataFrame) -> list[dict]:
    """Convert CNPS DataFrame rows into template-ready dicts."""
    records = []
    for _, row in df.iterrows():
        def safe(col):
            val = row.get(col)
            return str(val) if pd.notna(val) and val != "" else ""

        fesa = safe("FESA") or "None"
        cesa = safe("CESA") or "None"
        status = f"{fesa}/{cesa}\n{safe('GRank')}/{safe('SRank')}\nCRPR: {safe('CRPR')}"

        elev_low = row.get("ElevationLow_ft")
        elev_high = row.get("ElevationHigh_ft")
        elev_str = (
            f"Elevations: {float(elev_low):.0f}-{float(elev_high):.0f} ft. "
            if pd.notna(elev_low) and pd.notna(elev_high)
            else ""
        )
        bloom = safe("BloomingPeriod")
        bloom_str = f"Blooms {bloom}." if bloom else ""
        habitat = f"{safe('Habitat')} {elev_str}{bloom_str}".strip()

        records.append({
            "name": safe("ScientificName"),
            "common_name": safe("CommonName"),
            "status": status,
            "habitat": habitat,
            "pto": "",
            "observations": "",
        })
    return records


def build_cnddb_records(df: pd.DataFrame) -> list[dict]:
    """Convert CNDDB DataFrame rows into the same template-ready dict shape."""
    records = []
    for _, row in df.iterrows():
        def safe(col):
            val = row.get(col)
            return str(val) if pd.notna(val) and val != "" else ""

        fed = safe("FEDLIST") or "None"
        state = safe("STLIST") or "None"
        status = f"{fed}/{state}\n{safe('GRANK')}/{safe('SRANK')}"

        records.append({
            "name": safe("SNAME"),
            "common_name": safe("CNAME"),
            "status": status,
            "habitat": safe("ELMTYPE"),
            "pto": "",
            "observations": "",
        })
    return records


def generate_pto_document(
    records: list[dict],
    template_path: str | Path,
    output_path: str | Path,
    project_name: str = "Sample Project",
    project_location: str = "Santa Barbara County, CA",
) -> Path:
    doc = DocxTemplate(str(template_path))
    context = {
        "project_name": project_name,
        "project_location": project_location,
        "assessment_date": date.today().strftime("%B %d, %Y"),
        "species_data": records,
        "total_species": len(records),
    }
    doc.render(context)
    out = Path(output_path)
    doc.save(out)
    return out


# --- fixtures --------------------------------------------------------------

@pytest.fixture
def cnps_row_df() -> pd.DataFrame:
    """A single CNPS row exercising every field build_cnps_records reads."""
    return pd.DataFrame([{
        "ScientificName": "Arctostaphylos refugioensis",
        "CommonName": "Refugio manzanita",
        "FESA": "Threatened",
        "CESA": "Endangered",
        "GRank": "G2",
        "SRank": "S2",
        "CRPR": "1B.2",
        "Habitat": "Chaparral, sandstone outcrops.",
        "ElevationLow_ft": 500.0,
        "ElevationHigh_ft": 2400.0,
        "BloomingPeriod": "Dec-Mar",
    }])


@pytest.fixture
def cnps_minimal_df() -> pd.DataFrame:
    """A row with most optional fields blank, to exercise the fallback paths."""
    return pd.DataFrame([{
        "ScientificName": "Mystery plantus",
        "CommonName": "",
        "FESA": "",
        "CESA": "",
        "GRank": "",
        "SRank": "",
        "CRPR": "",
        "Habitat": "Grassland.",
        "ElevationLow_ft": pd.NA,
        "ElevationHigh_ft": pd.NA,
        "BloomingPeriod": "",
    }])


@pytest.fixture
def cnddb_row_df() -> pd.DataFrame:
    return pd.DataFrame([{
        "SNAME": "Quercus dumosa",
        "CNAME": "Nuttall's scrub oak",
        "FEDLIST": "None",
        "STLIST": "None",
        "GRANK": "G3",
        "SRANK": "S3",
        "ELMTYPE": "Plant",
    }])


@pytest.fixture
def template_path() -> Path:
    if not TEMPLATE_PATH.exists():
        pytest.skip(f"PTO template not found at {TEMPLATE_PATH}")
    return TEMPLATE_PATH


# --- unit tests: record builders -------------------------------------------

def test_build_cnps_records_full_row(cnps_row_df):
    [rec] = build_cnps_records(cnps_row_df)

    assert rec["name"] == "Arctostaphylos refugioensis"
    assert rec["common_name"] == "Refugio manzanita"
    # status combines federal/state listings, ranks, and CRPR
    assert "Threatened/Endangered" in rec["status"]
    assert "G2/S2" in rec["status"]
    assert "CRPR: 1B.2" in rec["status"]
    # habitat combines text + elevations + bloom
    assert "Chaparral" in rec["habitat"]
    assert "500-2400 ft" in rec["habitat"]
    assert "Blooms Dec-Mar" in rec["habitat"]
    # template placeholders left empty for manual fill
    assert rec["pto"] == ""
    assert rec["observations"] == ""


def test_build_cnps_records_falls_back_on_missing_fields(cnps_minimal_df):
    [rec] = build_cnps_records(cnps_minimal_df)

    assert rec["name"] == "Mystery plantus"
    assert rec["common_name"] == ""
    # Empty FESA/CESA become "None" so the document never shows blank slashes
    assert rec["status"].startswith("None/None")
    # No elevation -> no elevation string; no bloom -> no bloom string
    assert "Elevations" not in rec["habitat"]
    assert "Blooms" not in rec["habitat"]
    assert rec["habitat"] == "Grassland."


def test_build_cnddb_records(cnddb_row_df):
    [rec] = build_cnddb_records(cnddb_row_df)

    assert rec["name"] == "Quercus dumosa"
    assert rec["common_name"] == "Nuttall's scrub oak"
    assert "None/None" in rec["status"]
    assert "G3/S3" in rec["status"]
    assert rec["habitat"] == "Plant"


def test_record_shapes_match_between_sources(cnps_row_df, cnddb_row_df):
    """CNPS and CNDDB records must have the same keys so docxtpl can render
    them through a single {%tr for ...%} loop in the template."""
    cnps_keys = set(build_cnps_records(cnps_row_df)[0])
    cnddb_keys = set(build_cnddb_records(cnddb_row_df)[0])
    assert cnps_keys == cnddb_keys


# --- unit test: document generation ----------------------------------------

def test_generate_pto_document_writes_nonempty_docx(template_path, tmp_path, cnps_row_df):
    records = build_cnps_records(cnps_row_df)
    out = generate_pto_document(
        records=records,
        template_path=template_path,
        output_path=tmp_path / "test_pto.docx",
        project_name="Test Project",
        project_location="Test County, CA",
    )

    assert out.exists()
    # docxtpl should produce a non-trivial .docx (zip header + content)
    assert out.stat().st_size > 1000
    assert out.suffix == ".docx"


# --- integration test: the full demo flow ----------------------------------

def test_end_to_end_pto_generation_from_real_data(template_path, tmp_path):
    """Mirror the original demo's main() but write to tmp_path and skip if
    fixture CSVs are missing."""
    if not CNPS_CSV.exists():
        pytest.skip(f"CNPS data not found at {CNPS_CSV}")
    if not CNDDB_CSV.exists():
        pytest.skip(f"CNDDB data not found at {CNDDB_CSV}")

    quad_ids = {3411814, 3411815, 3411816, 3411824, 3411825, 3411826}

    cnps_df = refactor_cnps(CNPS_CSV)
    cnps_filtered = get_species_cnps(cnps_df, quad_ids)
    cnddb_filtered = get_species_cnddb(CNDDB_CSV, quad_ids)

    records = build_cnps_records(cnps_filtered) + build_cnddb_records(cnddb_filtered)
    assert len(records) > 0, "expected at least one species across both sources"

    out = generate_pto_document(
        records=records,
        template_path=template_path,
        output_path=tmp_path / "gigi_output_pto_report.docx",
        project_name="Palisades Fire Boundary",
        project_location="Los Angeles County, CA",
    )

    assert out.exists()
    assert out.stat().st_size > 1000


# --- script entry point (kept so the file still works as a demo) -----------

def main():
    """Regenerate the demo document into the repo's output/ directory."""
    output_dir = REPO_ROOT / "output"
    output_dir.mkdir(exist_ok=True)

    quad_ids = {3411814, 3411815, 3411816, 3411824, 3411825, 3411826}

    cnps_df = refactor_cnps(CNPS_CSV)
    cnps_filtered = get_species_cnps(cnps_df, quad_ids)
    cnddb_filtered = get_species_cnddb(CNDDB_CSV, quad_ids)

    records = build_cnps_records(cnps_filtered) + build_cnddb_records(cnddb_filtered)
    print(f"Found {len(records)} species in quads")

    out = generate_pto_document(
        records=records,
        template_path=TEMPLATE_PATH,
        output_path=output_dir / "gigi_output_pto_report.docx",
        project_name="Palisades Fire Boundary",
        project_location="Los Angeles County, CA",
    )
    print(f"Generated: {out}")


if __name__ == "__main__":
    main()
