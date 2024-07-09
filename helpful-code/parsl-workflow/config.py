# Visualization workflow configuration for the parsl workflow

# Documentation for config options can be found here:
# https://github.com/PermafrostDiscoveryGateway/viz-staging/blob/main/pdgstaging/ConfigManager.py


workflow_config = {
  "dir_input": "/home/jcohen/testing/testing_datasets/lake_change_cleaned", 
  "ext_input": ".gpkg",
  "dir_staged": "staged/",
  "dir_geotiff": "geotiff/", 
  "dir_web_tiles": "web_tiles/",  
  "filename_staging_summary": "staging_summary.csv",
  "filename_rasterization_events": "raster_events.csv",
  "filename_rasters_summary": "raster_summary.csv",
  "simplify_tolerance": 0.1,
  "tms_id": "WGS1984Quad",
  "z_range": [
    0,
    12
  ],
  "geometricError": 57,
  "z_coord": 0,
  "statistics": [
    {
      "name": "change_rate", 
      "weight_by": "area",
      "property": "ChangeRateNet_myr-1", 
      "aggregation_method": "min", 
      "resampling_method": "mode",  
      "val_range": [
        -2,
        2
      ],
      "palette": ["#ff0000", # red
                  "#FF8C00", # DarkOrange
                  "#FFA07A", # LightSalmon
                  "#FFFF00", # yellow
                  "#66CDAA", # MediumAquaMarine
                  "#AFEEEE", # PaleTurquoise,
                  "#0000ff"], # blue
      "nodata_val": 0,
      "nodata_color": "#ffffff00" # fully transparent white
    },
  ],
  "deduplicate_at": ["raster"],
  "deduplicate_keep_rules": [["Perimeter_meter","larger"]],
  "deduplicate_method": "neighbor",
  "deduplicate_overlap_tolerance": 0.1,
  "deduplicate_overlap_both": False
}