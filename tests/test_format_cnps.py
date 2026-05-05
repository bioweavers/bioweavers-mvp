#%%
import pandas as pd

from utils.format_data import format_cnps

# %%

'''
These are the lists of columns required to display each field in the PTO table

Species

Scientific Name /   | CNPS: ScientificName, CommonName
Common Name         | CNDDB: SNAME, CNAME

Status

Status              | CNPS: CRPR, OtherStatus, CESA, FESA
                    | CNDDB: FEDLIST, CALLIST, RPLANTRANK, CDFWSTATUS, OTHRSTATUS

Habitat Requirements

Habitat             | CNPS: BloomingPeriod, Habitat, MicrohabitatDetails, Microhabitat, ElevationLow_ft, ElevationHigh_ft, ElevationLow_m, ElevationHigh_m
Requirements        | CNDDB: ECOLOGICAL (as of now, only that column seems to relate to habitat reqs.)

'''

# %%

# Create a tiny test dataframe
df = pd.DataFrame([
    {
        "ScientificName": "Arctostaphylos morroensis",
        "CommonName": "Morro manzanita",
        "FederalStatus": "Threatened",
        "StateStatus": None,
        "CRPR": "1B.1",
        "CESA": pd.NA,
        "FESA": "FE",
        "OtherStatus": "SB_CalBG/RSABG; USFS_S",
        "ElevationLow_ft": 100,
        "ElevationHigh_ft": 600,
        "BloomingPeriod": "Jan–Mar",
        "Habitat": "Chaparral",
        "MicrohabitatDetails": "Sandy soils",
        "Microhabitat": pd.NA
    }
])

# %%

# Run the function
out = format_cnps(df)

print(out)
print()
print(out.loc[0, "HabitatRequirements"])
print()
print(out.loc[0, "StatusDisplay"])

# %%
# Check the output
out

# %%
# Check that the newline works
print(out.loc[0, "StatusDisplay"])
