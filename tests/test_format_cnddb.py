#%%
import pandas as pd

from utils.format_data import format_cnddb

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
        "SNAME": "Haul pafa",
        "CNAME": "marsh trout",
        "FEDLIST": "Candidate",
        "CALLIST": "Candidate Endangered",
        "RPLANTRANK": None,
        "CDFWSTATUS": pd.NA,
        "OTHRSTATUS": "IUCN_LC",
        "ECOLOGICAL": "",
    }
])

# %%

# Run the function
out = format_cnddb(df)

print(out)
print()
print(out.loc[0, "HabitatRequirements"])
print()
print(out.loc[0, "StatusDisplay"])

# %%
# Check the output without print()
out

# %%
# Check that the newline works
print(out.loc[0, "StatusDisplay"])
