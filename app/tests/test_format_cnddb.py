"""Tests for utils.format_data.format_cnddb.

format_cnddb takes a raw CNDDB DataFrame and produces a display DataFrame for
the PTO (Potential to Occur) table with these columns:
    SpeciesDisplay, StatusDisplay, HabitatRequirements,
    PotentialtoOccur, HabitatSuitabilityObservations, Source
"""

import pandas as pd
import pytest

from utils.format_data import format_cnddb


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
    """One row with every field populated."""
    return pd.DataFrame([{
        "SNAME": "Quercus dumosa",
        "CNAME": "Nuttall's scrub oak",
        "FEDLIST": "Candidate",
        "CALLIST": "Candidate Endangered",
        "RPLANTRANK": "1B.1",
        "CDFWSTATUS": "SSC",
        "OTHRSTATUS": "IUCN_LC",
        "ECOLOGICAL": "Coastal scrub on sandstone outcrops.",
    }])


@pytest.fixture
def sparse_row_df():
    """Row with all optional fields blank/NA."""
    return pd.DataFrame([{
        "SNAME": "Mystery animalus",
        "CNAME": pd.NA,
        "FEDLIST": pd.NA,
        "CALLIST": pd.NA,
        "RPLANTRANK": pd.NA,
        "CDFWSTATUS": pd.NA,
        "OTHRSTATUS": pd.NA,
        "ECOLOGICAL": pd.NA,
    }])


# --- structural tests ------------------------------------------------------

def test_returns_dataframe_with_expected_columns(full_row_df):
    out = format_cnddb(full_row_df)
    assert isinstance(out, pd.DataFrame)
    assert list(out.columns) == EXPECTED_COLUMNS


def test_one_row_in_one_row_out(full_row_df):
    assert len(format_cnddb(full_row_df)) == 1


def test_source_marker_is_cnddb(full_row_df):
    out = format_cnddb(full_row_df)
    assert (out["Source"] == "CNDDB").all()


def test_potential_to_occur_columns_start_empty(full_row_df):
    out = format_cnddb(full_row_df)
    assert (out["PotentialtoOccur"] == "").all()
    assert (out["HabitatSuitabilityObservations"] == "").all()


# --- SpeciesDisplay --------------------------------------------------------

def test_species_display_combines_sname_and_cname(full_row_df):
    out = format_cnddb(full_row_df)
    assert out.loc[0, "SpeciesDisplay"] == "Quercus dumosa\nNuttall's scrub oak"


def test_species_display_omits_missing_common_name(sparse_row_df):
    out = format_cnddb(sparse_row_df)
    assert out.loc[0, "SpeciesDisplay"] == "Mystery animalus"


# --- StatusDisplay ---------------------------------------------------------

def test_status_display_uses_friendly_labels(full_row_df):
    """Internal column names get human-readable labels in the rendered output."""
    out = format_cnddb(full_row_df)
    status = out.loc[0, "StatusDisplay"]
    assert "Federal: Candidate" in status
    assert "State: Candidate Endangered" in status
    assert "RPLANTRANK: 1B.1" in status
    assert "CDFW: SSC" in status
    assert "Other: IUCN_LC" in status


def test_status_display_omits_missing_listings():
    df = pd.DataFrame([{
        "SNAME": "x", "CNAME": "y",
        "FEDLIST": "Candidate",
        "CALLIST": pd.NA,
        "RPLANTRANK": pd.NA,
        "CDFWSTATUS": "SSC",
        "OTHRSTATUS": pd.NA,
        "ECOLOGICAL": "",
    }])
    out = format_cnddb(df)
    status = out.loc[0, "StatusDisplay"]
    assert status == "Federal: Candidate\nCDFW: SSC"
    # Make sure the missing fields didn't sneak in as "nan" or empty entries
    assert "nan" not in status.lower()
    assert "RPLANTRANK" not in status
    assert "Other" not in status


def test_status_display_blank_when_all_listings_missing(sparse_row_df):
    out = format_cnddb(sparse_row_df)
    assert out.loc[0, "StatusDisplay"] == ""


def test_status_display_lines_are_newline_separated(full_row_df):
    out = format_cnddb(full_row_df)
    lines = out.loc[0, "StatusDisplay"].split("\n")
    assert len(lines) == 5
    assert all(":" in line for line in lines)


# --- HabitatRequirements ---------------------------------------------------

def test_habitat_uses_ecological_field(full_row_df):
    out = format_cnddb(full_row_df)
    assert out.loc[0, "HabitatRequirements"] == "Coastal scrub on sandstone outcrops."


def test_habitat_blank_when_ecological_missing(sparse_row_df):
    out = format_cnddb(sparse_row_df)
    assert out.loc[0, "HabitatRequirements"] == ""


def test_habitat_blank_when_ecological_empty_string():
    df = pd.DataFrame([{
        "SNAME": "x", "CNAME": "y",
        "FEDLIST": pd.NA, "CALLIST": pd.NA, "RPLANTRANK": pd.NA,
        "CDFWSTATUS": pd.NA, "OTHRSTATUS": pd.NA,
        "ECOLOGICAL": "",
    }])
    out = format_cnddb(df)
    assert out.loc[0, "HabitatRequirements"] == ""


# --- multi-row handling ----------------------------------------------------

def test_handles_multiple_rows(full_row_df, sparse_row_df):
    df = pd.concat([full_row_df, sparse_row_df], ignore_index=True)
    out = format_cnddb(df)
    assert len(out) == 2
    assert out.loc[0, "SpeciesDisplay"].startswith("Quercus")
    assert out.loc[1, "SpeciesDisplay"] == "Mystery animalus"
    # Source marker should be uniform across rows
    assert (out["Source"] == "CNDDB").all()
