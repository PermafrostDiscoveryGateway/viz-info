# workflow.ipynb as a script
# see workflow.ipynb for documentation and plots

# Create a fresh Python environment and install 
# the requirements with `pip install -r requirements.txt`
# run this script in a `tmux` terminal 

# filepaths
from pathlib import Path
import os

# visual checks & vector data wrangling
import geopandas as gpd

# staging
import pdgstaging
from pdgstaging import TileStager

# rasterization & web-tiling
import pdgraster
from pdgraster import RasterTiler

# logging
from datetime import datetime
import logging
import logging.handlers
from pdgstaging import logging_config

# for transferring the log to workdir
import subprocess
from subprocess import Popen

# --------------------------------------------------------------

# import 3 input data files
data_dir = '/home/jcohen/iwp_russia_subset_clipToFP_PR/'
base_dir = Path(data_dir + 'iwp')
filename = '*.shp'
# To define each .shp file within each subdir as a string representation with forward slashes, use as_posix()
# The ** represents that any subdir string can be present between the base_dir and the filename
input = [p.as_posix() for p in base_dir.glob('**/' + filename)]

# pull filepaths for footprints in the same way we pulled IWP shp file paths
base_dir_fp = Path(data_dir + 'footprints')
fps = [p.as_posix() for p in base_dir_fp.glob('**/' + filename)]

# define workflow configuration
config = {
  "deduplicate_clip_to_footprint": True, 
  "dir_input": data_dir + "iwp/", 
  "ext_input": ".shp",
  "ext_footprints": ".shp",
  "dir_footprints": data_dir + "footprints/", 
  "dir_staged": "staged/",
  "dir_geotiff": "geotiff/", 
  "dir_web_tiles": "web_tiles/", 
  "filename_staging_summary": "staging_summary.csv",
  "filename_rasterization_events": "raster_events.csv",
  "filename_rasters_summary": "raster_summary.csv",
  "filename_config": "config",
  "simplify_tolerance": 0.1,
  "tms_id": "WGS1984Quad",
  "z_range": [
    0,
    15
  ],
  "geometricError": 57,
  "z_coord": 0,
  "statistics": [
    {
      "name": "iwp_coverage",
      "weight_by": "area",
      "property": "area_per_pixel_area",
      "aggregation_method": "sum",
      "resampling_method": "average",
      "val_range": [
        0,
        1
      ],
      "palette": [
        "#66339952",
        "#ffcc00"
      ],
      "nodata_val": 0,
      "nodata_color": "#ffffff00"
    },
  ],
  "deduplicate_at": [
    "raster"
  ],
  "deduplicate_keep_rules": [
    [
      "Date",
      "larger"
    ]
  ],
  "deduplicate_method": "footprints"
}

# --------------------------------------------------------------

print("Staging initiated.")
# stage the tiles
stager = TileStager(config)
stager.stage_all()

# --------------------------------------------------------------

print("Rasterizing and Web-tiling initiated.")
# rasterize all staged tiles, resample to lower resolutions,
# and produce web tiles
RasterTiler(config).rasterize_all()

# transfer log from /tmp to user dir
# add subdirectories as needed
user = subprocess.check_output("whoami").strip().decode("ascii") 
cmd = ['mv', '/tmp/log.log', f'/home/{user}/viz-info/helpful-code/']
# initiate the process to run that command
process = Popen(cmd)

print("Script complete.")

