#%%
import pandas as pd

cnddb = pd.read_csv('data/cnddb_test_data.csv')
cnps = pd.read_csv('data/CNPS_RAW.csv')

# %%
cnddb.columns.to_list
# %%
cnddb.TAXONGROUP.unique()
# %%
