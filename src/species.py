#%%
import requests
import pandas as pd

INATURALIST_API_URL = "https://api.inaturalist.org/v1/observations"

# Example bounding box for Santa Barbara, CA
# array([-119.85,   34.42, -119.82,   34.45])

def query_inaturalist(bounding_box, limit=100) -> pd.DataFrame:
    (min_lng, min_lat, max_lng, max_lat) = bounding_box
    params = {
    "nelat": max_lat,
    "nelng": max_lng,
    "swlat": min_lat,
    "swlng": min_lng,
    "quality_grade": "research",
    "per_page": limit,
    "order": "desc",
    "order_by": "observed_on",
    }
    response = requests.get(INATURALIST_API_URL, params=params)
    response.raise_for_status()
    data = response.json()
    records = []
    for obs in data.get("results", []):
        taxon = obs.get("taxon", {})
        records.append({
            "observation_id": obs.get("id"),
            "observed_on": obs.get("observed_on"),
            "scientific_name": taxon.get("name"),
            "common_name": taxon.get("preferred_common_name"),
            "taxon_id": taxon.get("id"),
            "iconic_taxon": taxon.get("iconic_taxon_name"),
            "conservation_status": taxon.get("conservation_status", {}).get("status"),
            "latitude": obs.get("geojson", {}).get("coordinates", [None, None])[1],
            "longitude": obs.get("geojson", {}).get("coordinates", [None, None])[0],
            "place_guess": obs.get("place_guess"),
        })

    df = pd.DataFrame(records)
    return df


#%%