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

import shutil

# for transferring the log to workdir
import subprocess
from subprocess import Popen

print("Removing old directories and files...")
old_filepaths = ["staging_summary.csv",
                 "raster_summary.csv",
                 "raster_events.csv",
                 "config__updated*",
                 "log.log"]
for old_file in old_filepaths:
  if os.path.exists(old_file):
      os.remove(old_file)

old_dirs = ["staged",
            "geotiff",
            "web_tiles"]
for old_dir in old_dirs:
  if os.path.exists(old_dir) and os.path.isdir(old_dir):
      shutil.rmtree(old_dir)

# --------------------------------------------------------------

# import 3 IWP input data files and footprints
data_dir = '/home/jcohen/testing/testing_datasets/iwp_fp_3_files/'

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
  "deduplicate_at": None,
  "deduplicate_keep_rules": None,
  "deduplicate_method": None
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

