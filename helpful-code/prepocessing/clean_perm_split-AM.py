# Clean permafrost and groundice data from Brown et al. 2002
# Data source: https://nsidc.org/data/ggd318/versions/2
# issue: https://github.com/PermafrostDiscoveryGateway/pdg-portal/issues/41
# Author: Juliet Cohen
# Date: 2024-05-01

# Cleaning steps include:
# 1. remove NA values from "extent" attribute
# 2. add attribute for numerical coding for the "extent" attribute
# 3. split polygons that intersect the antimeridian

# conda env: viz_3-10_local

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import LineString


input = "/home/jcohen/permafrost_ground_layer/data/permaice.shp"
perm = gpd.read_file(input)

# drop rows that have missing value for extent attribute
# since this is the attribute to visualize
perm.dropna(subset = ['EXTENT'], inplace = True)

# create new gdf of just the polygons that have a neg min longitude and a pos max longitude 
# this indicates that the polygon crosses the antimeridian or prime meridian (7 polygons)
meridian_polys = (perm['geometry'].bounds['minx'] < 0 ) & (perm['geometry'].bounds['maxx'] > 0)

# subset the data to just polygons that cross either of the merdidians
# and retain all attributes by appending `.copy()`
prob_polys = perm[meridian_polys].copy()

# subset the prob_polys to those that cross antimeridian, not prime meridian
# the only polygon that crosses the prime meridian is at index 60
polys_AM = prob_polys.drop([60], inplace = False)

# remove the antimeridian polygons from the original gdf 
# so when the split ones are appeneded later, there won't be duplicates
perm.drop(polys_AM.index, inplace = True)

# Split polygons that cross the antimeridian
# Step 1. create a line gdf at the 180th longitude,
#       that's where the center is in this dataset according to metadata,
#       the units are meters, not degrees, so use 20,000,000 instead of 180
am = gpd.GeoSeries(LineString([(0, -20000000), (0, 20000000)]))
am.set_crs(perm.crs, inplace = True)
# buffer the line with 1 meter (units of CRS) to convert it to a polygon
am_buffered = am.buffer(distance = 1, 
                        cap_style = 2, 
                        join_style = 0, 
                        mitre_limit = 2)

# create empty lists to store the split polygons and their attributes
all_data = []

# iterate over each geometry that crosses the antimeridian
for index, row in polys_AM.iterrows():
    # define the geometry and attributes separately
    geom = row['geometry']
    atts = gpd.GeoDataFrame(row.drop('geometry').to_frame().T)
    # split the single geometry with the buffered antimeridian GeoSeries,
    # outputing multiple geoms stored within a MultiPolygon
    split_geoms_MP = geom.difference(am_buffered)
    # make the index match the atts to concat correctly
    split_geoms_MP.index = atts.index
    # convert to GDF to define the geometry col
    split_geoms_MP_gdf = gpd.GeoDataFrame(geometry = split_geoms_MP)
    split_geoms_MP_gdf.set_crs(perm.crs, inplace = True)
    MP_with_atts = pd.concat([split_geoms_MP_gdf, atts], axis = 1)
    # MP_with_atts.reset_index(inplace = True) # not sure if i need this
    P_with_atts = MP_with_atts.explode(ignore_index = False,
                                       index_parts = False)
    # concatenate the exploded geometries with their attributes
    all_data.append(P_with_atts)

# create empty gdf to store final result
all_data_concat = gpd.GeoDataFrame()

# iterate over each gdf in all_data, concatenate into single gdf
for gdf in all_data:
    all_data_concat = pd.concat([all_data_concat, gdf], 
                                ignore_index = True)

all_data_concat.reset_index(drop = True, inplace = True)

# append the split polygons to the same gdf as other polygons
perm = pd.concat([perm, all_data_concat], ignore_index = True)

# add column that codes the categorical extent strings into numbers 
# in order to do stats with the workflow and assign palette to this
# first, define the conditions and choices for new extent_code attribute
conditions = [
    (perm['EXTENT'] == "C"),
    (perm['EXTENT'] == "D"),
    (perm['EXTENT'] == "S"),
    (perm['EXTENT'] == "I")
]
choices = [4, 3, 2, 1]

# assign extent_code based on the conditions and choices
perm['extent_code'] = np.select(conditions, choices)

# save as a cleaned input file for the viz workflow
output_file = "/home/jcohen/permafrost_ground_layer/split_AM_polys/cleaned/permaice_clean_split.gpkg"
perm.to_file(output_file, driver = "GPKG")

print("Cleaning complete.")
