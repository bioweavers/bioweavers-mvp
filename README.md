# Bio Weavers MVP

Proof-of-life pipeline for querying iNaturalist observations around a project boundary, buffering the area, and exporting species lists.

## Goals (Session 1)
1. Get dev environments working
2. Establish repo structure
3. Implement core geometry/species/export functions
4. Add tests for core logic (no network required)

## Project Structure
```
bioweavers-mvp/
├── README.md
├── environment.yml          # Supported install (conda-forge)
├── conda-lock.yml           # Pinned cross-platform lockfile (optional)
├── src/
│   ├── __init__.py
│   ├── geometry.py
│   ├── species.py
│   └── export.py
├── tests/
│   ├── test_geometry.py
│   └── test_species.py
├── data/
│   └── sample_boundary.geojson
├── examples/
│   └── word_export/         # DataFrame → Word document demo
├── output/
├── notebooks/
└── docs/
    └── PLAN.md
```

## Quickstart

This project uses **conda-forge** for reproducible geospatial dependencies across macOS, Windows, and Linux.

> [!IMPORTANT]
> **Do not use `pip install` for geopandas, shapely, or pyproj.** On Windows, pip-installed binaries for the geospatial C stack (GDAL / GEOS / PROJ) frequently mismatch and produce hard segfaults during reprojection or file I/O. The conda-forge channel ships consistent binaries for all three platforms.

### One-time setup

1. **Install a conda-compatible package manager.** [Miniforge](https://github.com/conda-forge/miniforge) is recommended — it ships with `conda` preconfigured for conda-forge and includes the fast `mamba` solver. Anaconda Distribution and Miniconda also work.

2. **Create the environment** from the project root:

   ```bash
   conda env create -f environment.yml
   conda activate bioweavers-mvp
   ```

   If you have `mamba` (much faster solver, especially on Windows):

   ```bash
   mamba env create -f environment.yml
   conda activate bioweavers-mvp
   ```

3. **Verify the install:**

   ```bash
   python -c "import geopandas, shapely, pyproj, pyogrio; \
       print(f'geopandas {geopandas.__version__}, shapely {shapely.__version__}, pyproj {pyproj.__version__}, pyogrio {pyogrio.__version__}')"
   ```

   You should see geopandas ≥ 1.0, shapely ≥ 2.0, pyproj ≥ 3.6, pyogrio ≥ 0.7. If any import fails, see [Troubleshooting](#troubleshooting).

### Run

```bash
streamlit run app.py
pytest
```

## Reproducible installs (recommended for class use)

`environment.yml` pins major versions, but the conda solver can still resolve to different patch versions on different machines or different days. For bit-for-bit reproducibility — every student on every OS gets the same versions — use the lockfile:

```bash
# install once
pip install conda-lock

# regenerate the lockfile after editing environment.yml
conda-lock -f environment.yml -p osx-64 -p osx-arm64 -p linux-64 -p win-64

# students install from the lockfile, not the env file
conda-lock install --name bioweavers-mvp conda-lock.yml
```

Commit `conda-lock.yml` to the repo and have students install from it.

## Updating the environment

After `environment.yml` changes (e.g., a new dependency is added):

```bash
conda env update -f environment.yml --prune
```

The `--prune` flag removes packages that are no longer listed.

If anything seems off after an update, the safest move is always to recreate from scratch:

```bash
conda deactivate
conda env remove -n bioweavers-mvp
conda env create -f environment.yml
```

## Jupyter kernel

The environment already includes `ipykernel`, so Jupyter inside the env "just works." If you need the kernel to be visible from a Jupyter install *outside* this env (e.g., your global JupyterLab):

```bash
conda activate bioweavers-mvp
python -m ipykernel install --user --name bioweavers-mvp --display-name "Bio Weavers"
```

Then select the **Bio Weavers** kernel in Jupyter.

## Core Pipeline (Proof-of-Life)
1. Load GeoJSON/KML boundary
2. Create buffer (2 / 5 / 10 miles)
3. Query iNaturalist API with bounding box
4. Build species list + filter federally listed
5. Export CSV / Excel

### Notes
- Buffering reprojects to **EPSG:5070 (NAD83 / Conus Albers)** for meter-accurate buffers across the western US, then returns to EPSG:4326 for API usage.
- iNaturalist requests are not executed in tests; network tests can be added later.

## Examples

### Word Document Export (`examples/word_export/`)

Demonstrates generating Word documents with dynamic tables from pandas DataFrames using **docxtpl** (Jinja2 templating for Word).

```bash
cd examples/word_export
python demo_pto_export.py
open output_pto_report.docx     # macOS — use `start` on Windows
```

**How it works:**
1. Create a Word template with Jinja2 placeholders (e.g., `{{ species.name }}`)
2. Use `{%tr for item in list %}` to mark table rows that should repeat
3. docxtpl clones the template row for each item in your DataFrame

**Files:**

| File | Purpose |
|------|---------|
| `create_template.py` | Programmatically creates a Word template (bootstrap helper) |
| `demo_pto_export.py` | Main demo: DataFrame → Word document |
| `pto_template.docx` | The Word template with Jinja2 placeholders |
| `README.md` | Detailed documentation |

**Why this approach:**
- Pure Python, no external binaries like pandoc
- Template is a real Word doc — non-programmers can edit formatting
- Preserves fonts, styles, company branding from the template

## Troubleshooting

### Segfault on `to_crs()`, `buffer()`, or `read_file()`

Almost always a binary mismatch in the geospatial C stack (GEOS / GDAL / PROJ). Common causes:
- A `pip install` got mixed into a conda env (or vice versa)
- Shapely 1.x and a geopandas that expects 2.x ended up in the same env
- An old fiona is shadowing pyogrio

**Fix:** rebuild the env from scratch.

```bash
conda deactivate
conda env remove -n bioweavers-mvp
conda env create -f environment.yml
conda activate bioweavers-mvp
```

Then **never** `pip install` geopandas, shapely, pyproj, fiona, pyogrio, or gdal into this env. If you need to add a pure-Python package that isn't on conda-forge, prefer adding it to `environment.yml` under a `pip:` block rather than running pip ad-hoc.

### `PROJ: proj_create_from_database: Cannot find proj.db`

PROJ can't locate its data directory. This shouldn't happen in a clean conda-forge env, but if it does:

```bash
python -c "import pyproj; print(pyproj.datadir.get_data_dir())"
```

The path it prints should exist and contain `proj.db`. If not, the env is broken — recreate it (see above).

### Empty geometries after reprojection

Two possibilities:
- The source CRS is mislabeled. `set_crs()` only labels; it does not transform. If you `set_crs(4326)` on data that was actually in UTM meters, downstream reprojections will produce empty geometries.
- The target CRS's area of use doesn't cover your data. EPSG:3310 only covers California; a boundary in Nevada will reproject to invalid coordinates. Use EPSG:5070 (Conus Albers) for the western US more generally.

### Streamlit doesn't see file changes / kernel won't reload

The Streamlit file watcher on Windows can be flaky inside long Anaconda paths. Either move the project to a shorter path (e.g., `C:\dev\bioweavers-mvp`) or disable the watcher:

```bash
streamlit run app.py --server.fileWatcherType none
```

### "Solving environment" hangs forever

Use `mamba` instead of `conda`:

```bash
conda install -n base -c conda-forge mamba
mamba env create -f environment.yml
```

## Contributing to the environment

When adding a dependency:

1. Add it to `environment.yml` under `dependencies:` (prefer conda-forge packages).
2. If the package isn't on conda-forge, add a nested `pip:` section:

   ```yaml
   dependencies:
     - python=3.11
     - geopandas>=1.0
     - pip
     - pip:
       - some-pure-python-package
   ```

3. Regenerate the lockfile (`conda-lock -f environment.yml ...`).
4. Commit both `environment.yml` and `conda-lock.yml`.

Do not add geospatial-stack packages (geopandas, shapely, pyproj, fiona, pyogrio, gdal, rasterio) to the `pip:` section — they must come from conda-forge.
