''' Checks for the search queries applied to the databases by 9-quad filtering and spatial queries.
Functions that involve obtaining species information based on queries are tested here.'''

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
import pytest

from src.geometry import _cell_map_code, get_quads, get_species_cnps, get_species_cnddb

def _make_boundary():
    boundary_geom = box(-120.0, 34.0, -119.5, 34.5)
    return gpd.GeoDataFrame({"geometry": [boundary_geom]}, crs=4326)

def _make_quads():
    return gpd.GeoDataFrame(
        {
            "CELL_MAPCODE": ['12344-A1', '12345-B1', '12346-C1'],
            # "id": ['1234411', '1234521', '1234631'],
            "quad_name": ["Alpha", "Bravo", "Charlie"],
            "geometry": [
                box(-120.2, 34.2, -119.9, 34.6),  # intersects
                box(-119.7, 33.8, -119.3, 34.1),  # intersects
                box(-121.0, 35.0, -120.5, 35.5),  # no
            ],
        },
        crs=4326,
    )

def test_get_quads():
    # Arrange
    boundary_gdf = _make_boundary()
    quads_gdf = _make_quads()

    # Act
    intersecting_quads = get_quads(boundary_gdf, quads_gdf)

    # Assert
    # Check that the result is a set.
    assert isinstance(intersecting_quads, set)

    # Check that the correct quads are returned.
    expected_quad_ids = {1234411, 1234521}
    assert intersecting_quads == expected_quad_ids

def _make_cnps():
    return pd.DataFrame({
        'ScientificName': ['Species A', 'Species B', 'Species C'],
        'split_quad': [{3411728, 3411814, 3311776, 3411826}, {3411814, 3411922, 3411934, 3411932},  {8888888, 7777777}] 
    })

def test_get_species_cnps():  
    
    # Arrange
    cnps_df = _make_cnps()
    quad_ids = {3411728, 3411814}

    # Act
    species_in_quads = get_species_cnps(cnps_df, quad_ids)

    # Assert
    # Check that the result is a DataFrame.
    assert isinstance(species_in_quads, pd.DataFrame)

    # Check that the correct species are returned.
    expected_species = ['Species A', 'Species B']
    assert set(species_in_quads['ScientificName']) == set(expected_species)

def _make_cnddb():
    return pd.DataFrame({
        'SNAME': ['Species X', 'Species Y', 'Species Z'],
        'KEYQUAD': [3411814, 3411824, 3712151]
    })


def test_get_species_cnddb():
    # Arrange 
    # Create a boundary polygon that intersects test data.
    boundary = gpd.GeoDataFrame(
        geometry=[box(-120.0, 34.0, -119.0, 35.0)], 
        crs="EPSG:4326"
    )

    # Act
    species_in_quads = get_species_cnddb("tests/fixtures/test_cnddb_data.geojson", boundary)

    # Assert
    assert isinstance(species_in_quads, gpd.GeoDataFrame)

    expected_species = ['Species X', 'Species Y']
    assert set(species_in_quads['SNAME']) == set(expected_species)