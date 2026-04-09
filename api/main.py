from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import Any
from pathlib import Path
import tempfile
# had to install uvicorn
# had to run this in the command line: uvicorn api.main:app --reload
from src.geometry import load_boundary

# FastAPI app instance
app = FastAPI(title="Bioweavers Mock API")

# Root endpoint for health check
@app.get('/')
def root() -> dict[str, str]:
    return {'message': 'Bioweavers mock API is running.'}

# Analysis endpoint
@app.post('/analyze')
async def analyze_boundary(
    boundary_file: UploadFile = File(...),
    search_mode: str = Form(...)
) -> dict[str, Any]:
    """
    MVP analysis endpoint.
    Uses the load_boundary() function, while keeping the rest
    of the response mocked for now.
    """
# Validate search radius criteria
    if search_mode != '9-quad search':
        raise HTTPException(
            status_code=400,
            detail="Only '9-quad search' is supported right now."
        )

    try:
        # Save uploaded file to a temporary GeoJSON file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.geojson') as tmp:
            contents = await boundary_file.read()
            tmp.write(contents)
            temp_path = Path(tmp.name)

        # Use the load_boundary function
        boundary_gdf = load_boundary(temp_path)

        # Validate that the GeoDataframe is not empty
        if boundary_gdf.empty:
            raise HTTPException(
                status_code=400,
                detail="Uploaded boundary file contains no features."
            )
    # Catch and re-raise HTTPExceptions and convert other exceptions to HTTPExceptions with a 400 status code
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f'Could not process uploaded boundary file: {exc}'
        ) from exc

    # Mocked response for now, with the actual boundary loading as the only real processing step.
    response = {
        'status': 'success',
        'message': 'Boundary loaded successfully. Remaining analysis results are still mocked.',
        'uploaded_filename': boundary_file.filename,
        'search_mode': search_mode,
        'feature_count': len(boundary_gdf),
        'crs': str(boundary_gdf.crs),
        'bounding_box': [-119.85, 34.38, -119.70, 34.50],
        'quad_ids': [345611, 345612, 345613, 345621, 345622, 345623, 345631, 345632, 345633],
        'summary': {
            'cnps_count': 3,
            'cnddb_count': 4,
            'total_records': 7
        },
        'cnps_results': [
            {
                'scientific_name': 'Acmispon glaber',
                'common_name': 'deerweed',
                'rarity_rank': '1B.2',
                'habitat_desc': 'chaparral, coastal scrub, valley and foothill grassland',
                #'source': 'CNPS'
            },
            {
                'scientific_name': 'Arctostaphylos rudis',
                'common_name': 'shagbark manzanita',
                'rarity_rank': '1B.1',
                'habitat_desc': 'chaparral',
                #'source': 'CNPS'
            },
            {
                'scientific_name': 'Dudleya candelabrum',
                'common_name': 'candelabra liveforever',
                'rarity_rank': '1B.1',
                'habitat_desc': 'coastal scrub',
                #'source': 'CNPS'
            }
        ],
        "cnddb_results": [
            {
                'element_code': 'PDCAM08010',
                'scientific_name': 'Acmispon glaber',
                'common_name': 'deerweed',
                "observation_date": '2021-05-14',
                "distance_m": 120,
                "elevation_m": 310,
                'record_status': 'simulated',
                'habitat_desc': 'chaparral, coastal scrub, valley and foothill grassland',
                #'source': 'CNDDB'
            }, 
            
            {
                'element_code': 'PDCAM08011',
                'scientific_name': 'Acmispon glaber',
                'common_name': 'deerweed',
                'observation_date': '2020-08-22',
                'distance_m': 250,
                'elevation_m': 290,
                'record_status': 'simulated',
                'habitat_desc': 'chaparral, coastal scrub, valley and foothill grassland',
                #'source': 'CNDDB'
            }
            ,
            {
                'element_code': 'PDCAM08012',
                'scientific_name': 'Dudleya candelabrum',
                'common_name': 'candelabra liveforever',
                'observation_date': '2020-03-18',
                'distance_m': 90,
                'elevation_m': 150,
                'record_status': 'simulated',
                'habitat_desc': 'coastal scrub',
                #'source': 'CNDDB'
            },

            {
                'element_code': 'PDCAM08013',
                'scientific_name': 'Dudleya candelabrum',
                'common_name': 'candelabra liveforever',
                'observation_date': '2019-11-05',
                'distance_m': 300,
                'elevation_m': 200,
                'record_status': 'simulated',
                'habitat_desc': 'coastal scrub',
                #'source': 'CNDDB'
            }
        ]
    }

    return response
