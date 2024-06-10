# Example of applying the neighbor deduplication method to
# adjacent geosaptial files before inputting data into the
# visualization workflow.

# Created in response to request from Ingmar Nitze
# See issue: Issue: https://github.com/PermafrostDiscoveryGateway/viz-staging/issues/36

# Documention for this script can be found in the README for this directory
# (helpful-code/dedup_before_viz/README.md)

# Check Neighbor deduplication for Ingmar
# Issue: https://github.com/PermafrostDiscoveryGateway/viz-staging/issues/36

# visual checks & vector data wrangling
import geopandas as gpd
import pandas as pd

# staging
import pdgstaging
from pdgstaging.Deduplicator import deduplicate_neighbors
from pdgstaging import ConfigManager, TilePathManager, TMSGrid

# logging
from datetime import datetime
import logging
import logging.handlers
from pdgstaging import logging_config


gdf_1 = gpd.read_parquet("/var/data/submission/pdg/nitze_lake_change/identify_dups_sample_20240605/32617_river.parquet")
gdf_2 = gpd.read_parquet("/var/data/submission/pdg/nitze_lake_change/identify_dups_sample_20240605/32618_river.parquet")

print("Cleaning files for NA values.")
# remove rows with NA values from the attribute of interest
gdf_1.dropna(subset = ['ChangeRateNet_myr-1'], inplace = True)
gdf_2.dropna(subset = ['ChangeRateNet_myr-1'], inplace = True)

# add source_file attribute
gdf_1["source_file"] = '32617_river'
gdf_2["source_file"] = '32618_river'

files = [gdf_1, gdf_2]

print("Concatenating data.")
gdf_combined = gpd.GeoDataFrame(pd.concat(files, ignore_index = True))

print(f"CRS of input data: {gdf_combined.crs}\nStarting duplicate flagging.")

gdf_dups_flagged = deduplicate_neighbors(
    gdf = gdf_combined,
    split_by = 'source_file',
    prop_area = None,
    prop_centroid_x = None,
    prop_centroid_y = None,
    keep_rules = [["Perimeter_meter", "larger"]],
    overlap_tolerance = 0.1,
    overlap_both = False,
    centroid_tolerance = None,
    distance_crs = 'EPSG:3857',
    return_intersections = False,
    prop_duplicated = 'staging_duplicated'
    )

sum_dups = gdf_dups_flagged['staging_duplicated'].sum()
print(f"Number of duplicate lakes: {sum_dups}")

print("Saving deduplicated data to a single file.")
gdf_dups_flagged.to_file("/var/data/submission/pdg/nitze_lake_change/identify_dups_sample_20240605/32617-32618_dups_flagged.gpkg", drive = "GPKG")

print("Script complete.")