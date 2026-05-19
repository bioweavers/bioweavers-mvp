FROM mambaorg/micromamba:2.6.0

WORKDIR .

COPY environment.yml .

# Force conda-forge priority before creating the env
RUN micromamba env create -f environment.yml 
    

COPY . .

EXPOSE 3009

CMD ["micromamba", "run", "-n", "bioweavers-gdf", \
     "streamlit", "run", "./Landing.py", \
     "--server.port=3009", "--server.address=0.0.0.0"]