# First-run: viz-workflow 

### Prerequisites
- Python **3.9+**
- Geospatial libs (GDAL/GEOS/PROJ).

## 1) Clone & install

```bash
git clone git@github.com:PermafrostDiscoveryGateway/viz-workflow.git
cd viz-workflow

# create a local venv with uv
uv venv
source .venv/bin/activate

# install dependencies
uv pip install
```

---

## 2) Prepare a workspace

```bash
mkdir -p first_run/input
# Put a vector file here
# Example: first_run/input/ArcticRTSVolLatLong.gpkg
```
[Download ArcticRTSVolLatLong.gpkg](https://github.com/PermafrostDiscoveryGateway/viz-info/tree/main/helpful-code/first_run/input)

## 3) Minimal runner

Create `runner.py` at the repo root:

```python
# runner.py
from pdgworkflow import WorkflowManager

# Minimum config:
config = {
    "dir_input": "first_run/input",
    "ext_input": ".gpkg", 
    "z_range": (0, 2), 
    "overwrite": True, 
    # You can flip features on/off (for more, see the feature flags table below)
    # "enable_3dtiles": False,
    # "enable_raster_parents": False,
    # "enable_web_tiles_parents": False,
}

workflow = WorkflowManager(config)
workflow.run_workflow()

```

Run it:

```bash
python runner.py
```
## 4) What gets created

By default (unless overridden), outputs are written next to your repo:

```
staged/                      # tiled vectors at max z in your z_range (default .gpkg)
geotiff/                     # GeoTIFFs for each z in your z_range
web_tiles/                   # PNG tiles for each statistic & z
3dtiles/                     # 3D Tiles (tileset.json, etc.)
staging_summary.csv
staging_summary.parquet
rasterization_events.csv
rasterization_events.parquet
rasters_summary.csv
rasters_summary.parquet
WMTSCapablities.xml
```
---

## 5) Feature flags

These control which parts of the pipeline execute and how existing outputs are handled. All flags shown below default to the values given in `ConfigManager.defaults`.

| Key                         | Type  | Default | What it does                                                                                           | When to change it |
|------------------------------|-------|----------|---------------------------------------------------------------------------------------------------------|-------------------|
| `enable_stager`              | bool  | `True`   | Runs **vector staging/tiling** (produces `.gpkg` tiles under `staged/`).                                | Turn **off** if you already staged and only want to rasterize or build web tiles. |
| `enable_raster`              | bool  | `True`   | Runs **rasterization** to GeoTIFFs (writes to `geotiff/`).                                              | Turn **off** for a vectors-only run. |
| `enable_web_tiles`           | bool  | `True`   | Produces **web tiles** (PNG/JPG) per statistic & zoom (writes to `web_tiles/`).                         | Turn **off** for GeoTIFF-only runs. |
| `enable_3dtiles`             | bool  | `True`   | Produces **Cesium 3D Tiles** (writes to `3dtiles/`).                                                    | Turn **off** to skip 3D on day one. |
| `enable_raster_parents`      | bool  | `True`   | Builds **parent GeoTIFF tiles** by resampling children (pyramids).                                      | Turn **off** to speed up early tests. |
| `enable_web_tiles_parents`   | bool  | `True`   | Builds **parent web tiles** by resampling children (pyramids).                                          | Turn **off** to speed up early tests. |
| `generate_wmtsCapabilities`  | bool  | `True`   | Generates **WMTSCapabilities.xml** for clients that read WMTS metadata.                                 | Turn **off** if you don’t need capabilities yet. |
| `overwrite`                  | bool  | `False`  | If **True**, allows the workflow to overwrite existing outputs.                                         | Set **True** while iterating. |


Other commonly config options:

- `tms_id`: Default is `"WGS1984Quad"`. For most web maps, use `"WebMercatorQuad"`.
- `statistics`: If omitted, two defaults run: `polygon_count` and `coverage`. You can supply your own to reduce work.

---

## 6) Quick troubleshooting

- **No outputs?**  
  Ensure `dir_input` exists and contains files whose extension matches `ext_input` (e.g., `.gpkg` or `.shp`).

- **Rasterio/GDAL/PROJ errors**  
  Re-create the venv and reinstall; verify GDAL/PROJ are available to Python (platform packages frequently solve this).

- **Too slow**  
  Shrink `z_range`, disable parent tile generation, and temporarily disable 3D.

- **Maps look blank**  
  Check your statistics and palettes, confirm your input CRS is set (or provide `input_crs`), and verify `tms_id` matches your intended tiling scheme.

---

## 8) Explicit config example

```python
config = {
  "dir_input": "first_run/input",
  "dir_staged": "first_run/staged",
  "dir_geotiff": "first_run/geotiff",
  "dir_web_tiles": "first_run/web_tiles",
  "dir_3dtiles": "first_run/3dtiles",
  "ext_input": ".gpkg",
  "tms_id": "WebMercatorQuad", 
  "z_range": (0, 2),
  "overwrite": True,
  # Feature flags:
  "enable_stager": True,
  "enable_raster": True,
  "enable_web_tiles": True,
  "enable_3dtiles": False,  
  "enable_raster_parents": False,
  "enable_web_tiles_parents": False,
  "generate_wmtsCapabilities": True,
}
```
