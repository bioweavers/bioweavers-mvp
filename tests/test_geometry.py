import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
import pytest

from src.geometry import get_bounding_box, _cell_map_code, get_quads, get_species_cnps, get_species_cnddb

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


# def test_load_boundary(tmp_path):
#     _make_box
#     # Arrange
#     # Create a temporary GeoJSON file with a simple boundary geometry
#     boundary_gdf = _make_boundary()
#     boundary_gdf.to_file("data/boundary.geojson", driver="GeoJSON")

#     # Act
#     gdf = load_boundary("data/boundary.geojson")

#     # Assert
#     # Check that the loaded GeoDataFrame is a GeoDataFrame.
#     assert isinstance(gdf, gpd.GeoDataFrame)

#     # Check that the crs is set to WGS84 (EPSG:4326).
#     assert gdf.crs == gpd.crs.from_epsg(4326)
    

def test_get_bounding_box():
    # Arrange
    boundary_gdf = _make_boundary()

    # Act
    bbox = get_bounding_box(boundary_gdf)

    # Assert
    # Check that the bounding box is a tuple of (minx, miny, maxx, maxy).
    assert isinstance(bbox, np.ndarray)
    assert len(bbox) == 4


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
        'split_quad': [{3411728, 3411814, 3311776, 3411826}, {3411814, 3411922, 3411934, 3411932},  {8888888, 7777777}] # is this how we would create a list of quads
        #'geometry': [box(-120.1, 34.1, -119.9, 34.3), box(-119.8, 34.0, -119.6, 34.2), box(-120.5, 35.0, -120.3, 35.2)]
    })

def test_get_species_cnps():  # THIS TEST REQUIRES MAKING A MOCK CNPS AND CNDDB DATAFRAME, WHICH IS A LOT OF WORK. MAYBE WE CAN DO THIS LATER.
    
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
    # cnddb_df = _make_cnddb()
    quad_ids = {3411814, 3411824}

    # Act
    species_in_quads = get_species_cnddb("tests/fixtures/test_cnddb_data.csv", quad_ids)

    # Assert
    # Check that the result is a DataFrame.
    assert isinstance(species_in_quads, pd.DataFrame)

    # Check that the correct species are returned.
    expected_species = ['Species X', 'Species Y']
    assert set(species_in_quads['SNAME']) == set(expected_species)