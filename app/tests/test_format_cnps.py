"""Tests for utils.format_data.format_cnps.

format_cnps takes a raw CNPS DataFrame and produces a display DataFrame for the
PTO (Potential to Occur) table with these columns:
    SpeciesDisplay, StatusDisplay, HabitatRequirements,
    PotentialtoOccur, HabitatSuitabilityObservations, Source
"""

import pandas as pd
import pytest

from utils.format_data import format_cnps


EXPECTED_COLUMNS = [
    "SpeciesDisplay",
    "StatusDisplay",
    "HabitatRequirements",
    "PotentialtoOccur",
    "HabitatSuitabilityObservations",
    "Source",
]


# --- fixtures --------------------------------------------------------------

@pytest.fixture
def full_row_df():
    """One row with every field populated — exercises every formatter branch."""
    return pd.DataFrame([{
        "ScientificName": "Arctostaphylos morroensis",
        "CommonName": "Morro manzanita",
        "CRPR": "1B.1",
        "CESA": "CE",
        "FESA": "FT",
        "OtherStatus": "SB_CalBG/RSABG; USFS_S",
        "ElevationLow_ft": 100,
        "ElevationHigh_ft": 600,
        "BloomingPeriod": "Jan–Mar",
        "Habitat": "Chaparral",
        "MicrohabitatDetails": "Sandy soils",
        "Microhabitat": pd.NA,
    }])


@pytest.fixture
def sparse_row_df():
    """Row with most optional fields blank/NA — exercises the fallback paths."""
    return pd.DataFrame([{
        "ScientificName": "Mystery plantus",
        "CommonName": "",
        "CRPR": pd.NA,
        "CESA": pd.NA,
        "FESA": pd.NA,
        "OtherStatus": pd.NA,
        "ElevationLow_ft": pd.NA,
        "ElevationHigh_ft": pd.NA,
        "BloomingPeriod": pd.NA,
        "Habitat": pd.NA,
        "MicrohabitatDetails": pd.NA,
        "Microhabitat": pd.NA,
    }])


# --- structural tests ------------------------------------------------------

def test_returns_dataframe_with_expected_columns(full_row_df):
    out = format_cnps(full_row_df)
    assert isinstance(out, pd.DataFrame)
    assert list(out.columns) == EXPECTED_COLUMNS


def test_one_row_in_one_row_out(full_row_df):
    assert len(format_cnps(full_row_df)) == 1


def test_source_marker_is_cnps(full_row_df):
    out = format_cnps(full_row_df)
    assert (out["Source"] == "CNPS").all()


def test_potential_to_occur_columns_start_empty(full_row_df):
    out = format_cnps(full_row_df)
    assert (out["PotentialtoOccur"] == "").all()
    assert (out["HabitatSuitabilityObservations"] == "").all()


# --- SpeciesDisplay --------------------------------------------------------

def test_species_display_combines_scientific_and_common(full_row_df):
    out = format_cnps(full_row_df)
    assert out.loc[0, "SpeciesDisplay"] == "Arctostaphylos morroensis\nMorro manzanita"


def test_species_display_omits_blank_common_name(sparse_row_df):
    """join_lines drops blank/NA parts, so a missing CommonName yields just the
    ScientificName with no trailing newline."""
    out = format_cnps(sparse_row_df)
    assert out.loc[0, "SpeciesDisplay"] == "Mystery plantus"


# --- StatusDisplay ---------------------------------------------------------

def test_status_display_includes_present_listings(full_row_df):
    out = format_cnps(full_row_df)
    status = out.loc[0, "StatusDisplay"]
    assert "CRPR: 1B.1" in status
    assert "CESA: CE" in status
    assert "FESA: FT" in status


def test_status_display_omits_missing_listings(sparse_row_df):
    out = format_cnps(sparse_row_df)
    assert out.loc[0, "StatusDisplay"] == ""


def test_status_display_lines_are_newline_separated(full_row_df):
    """The PTO template renders StatusDisplay as a multi-line cell. Each present
    field should be on its own line."""
    out = format_cnps(full_row_df)
    lines = out.loc[0, "StatusDisplay"].split("\n")
    # CRPR, CESA, FESA — OtherStatus is currently broken (see xfail below)
    assert len(lines) >= 3
    assert all(":" in line for line in lines)


@pytest.mark.xfail(
    reason="format_cnps mapping for OtherStatus is reversed: dict is "
           "{'Other Status': 'OtherStatus'} but the loop reads it as "
           "{column: label}, so it tries to look up r['Other Status'] "
           "instead of r['OtherStatus']. Fix the dict to "
           "{'OtherStatus': 'Other Status'}.",
    strict=True,
)
def test_status_display_includes_other_status(full_row_df):
    out = format_cnps(full_row_df)
    assert "Other Status: SB_CalBG/RSABG; USFS_S" in out.loc[0, "StatusDisplay"]


# --- HabitatRequirements ---------------------------------------------------

def test_habitat_includes_full_elevation_range(full_row_df):
    out = format_cnps(full_row_df)
    assert "Elevation: 100–600 ft" in out.loc[0, "HabitatRequirements"]


def test_habitat_handles_only_low_elevation():
    df = pd.DataFrame([{
        "ScientificName": "x", "CommonName": "y",
        "ElevationLow_ft": 200, "ElevationHigh_ft": pd.NA,
    }])
    out = format_cnps(df)
    assert "Elevation: ≥ 200 ft" in out.loc[0, "HabitatRequirements"]


def test_habitat_handles_only_high_elevation():
    df = pd.DataFrame([{
        "ScientificName": "x", "CommonName": "y",
        "ElevationLow_ft": pd.NA, "ElevationHigh_ft": 800,
    }])
    out = format_cnps(df)
    assert "Elevation: ≤ 800 ft" in out.loc[0, "HabitatRequirements"]


def test_habitat_omits_elevation_when_both_missing(sparse_row_df):
    out = format_cnps(sparse_row_df)
    assert "Elevation" not in out.loc[0, "HabitatRequirements"]


def test_habitat_includes_microhabitat_when_present(full_row_df):
    out = format_cnps(full_row_df)
    assert "Microhabitat: Sandy soils" in out.loc[0, "HabitatRequirements"]


def test_habitat_combines_both_microhabitat_columns():
    df = pd.DataFrame([{
        "ScientificName": "x", "CommonName": "y",
        "MicrohabitatDetails": "Sandy soils",
        "Microhabitat": "Coastal terraces",
    }])
    out = format_cnps(df)
    assert "Microhabitat: Sandy soils; Coastal terraces" in out.loc[0, "HabitatRequirements"]


def test_habitat_includes_blooming_and_habitat_text(full_row_df):
    out = format_cnps(full_row_df)
    habitat = out.loc[0, "HabitatRequirements"]
    assert "Blooming Period: Jan–Mar" in habitat
    assert "Habitat: Chaparral" in habitat


def test_habitat_blank_when_all_fields_missing(sparse_row_df):
    out = format_cnps(sparse_row_df)
    assert out.loc[0, "HabitatRequirements"] == ""


# --- multi-row handling ----------------------------------------------------

def test_handles_multiple_rows(full_row_df, sparse_row_df):
    df = pd.concat([full_row_df, sparse_row_df], ignore_index=True)
    out = format_cnps(df)
    assert len(out) == 2
    assert out.loc[0, "SpeciesDisplay"].startswith("Arctostaphylos")
    assert out.loc[1, "SpeciesDisplay"] == "Mystery plantus"
