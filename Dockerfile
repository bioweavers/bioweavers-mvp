# Use the official micromamba image.
FROM mambaorg/micromamba:2.6.0

# Set the working directory in the container.
WORKDIR .

# Copy the environment.yml file to the container.
COPY environment.yml .

# Create the mamba environment and install dependencies.
RUN micromamba env create -f environment.yml 

# Copy the entire application code into the container.
COPY . .

# Expose teh port that the app runs on.
EXPOSE 3009

# Command to run the application with the mamba environment activated.
CMD ["micromamba", "run", "-n", "bioweavers-gdf", \
     "streamlit", "run", "Home.py", \
     "--server.port=3009", "--server.address=0.0.0.0"]