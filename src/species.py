#%%
from pathlib import Path
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


#%%
# Create function to refactor the CNPS 'Quads' column
def refactor_cnps(file_path: str | Path) -> pd.DataFrame:
        '''
        Refactor the 'Quads' column in a CNPS CSV file to extract quad IDs as a list of integers.

        Parameters
        ----------
        file_path : str | Path
            Path to the California Native Plant Society CSV file

        Returns 
        ----------
        pd.DataFrame
            DataFrame with the 'Quads' column refactored toa new column 'split_quad' to extract quad IDs as a list of integers.

        Notes
        ----------
        Returns a DataFrame with an additional column 'split_quad' that contains the extracted quad IDs as lists of integers. 
        The original 'Quads' column is left unchanged.
        '''

        # Read the CNPS csv file
        file_path = Path(file_path)    
    
        cnps = pd.read_csv(file_path)

        # Refactor the 'Quads' column to extract the quad IDs as a list of integers
        cnps["split_quad"] = (cnps["Quads"].str.findall(r'\d+')).apply(
        lambda lst: [int(x) for x in lst] if isinstance(lst, list) else []
        )
        return cnps
        

# %%

def plot_cnddb_species_distribution(df):
    fig, ax = plt.subplots()
    ax.bar(df["SNAME"], df["OCCNUMBER"])
    ax.set_title("Species Distribution")
    ax.set_xlabel("Species Name")
    ax.set_ylabel("Number of Occurrences")
    return fig
# %%

def plot_cnddb_species_date_range(df):
    df = df.copy()
    df["ELMDATE"] = pd.to_datetime(df["ELMDATE"], format="%Y%m%d")
    df["LASTUPDATE"] = pd.to_datetime(df["LASTUPDATE"], format="%Y%m%d")
    
    fig = px.timeline(df, 
                      x_start="ELMDATE", 
                      x_end="LASTUPDATE", 
                      y="SNAME", 
                      title="Species Occurrence Date Range")
    
    fig.update_layout(xaxis_range=["1950-01-01", "2025-01-01"])

    fig.show()
    return fig
# %%
