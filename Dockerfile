# Use the official ContinuumIO Miniconda3 image
FROM continuumio/miniconda3

# Set the working directory in the container
WORKDIR .

# Copy the environment.yml file into the container
COPY environment.yml .

# Create the conda environment
RUN conda env create -f environment.yml

# Initialize conda in bash
RUN conda init bash

# Add conda environment activation to bash script
SHELL ["/bin/bash", "-c"]

# Make RUN commands use the new environment
RUN echo "conda activate bioweavers-gdf" >> ~/.bashrc

# Copy the entire application code into the container
COPY . .

# Expose the port that the app runs on
EXPOSE 3009

# Set SHELL to bash with conda environment activated
SHELL ["/bin/bash", "-c"]


CMD ["conda", "run", "--no-capture-output", "-n", "bioweavers-gdf", "streamlit", "run", "./Landing.py", "--server.port=3009", "--server.address=0.0.0.0"]