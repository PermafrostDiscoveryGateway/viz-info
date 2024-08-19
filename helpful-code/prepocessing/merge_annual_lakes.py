# Prepare Lake Area Time Series data for visualization workflow:
# 1. Remove NA values from the 2 attributes of interest
# 2. Merge the two lake area datasets from Ingmar Nitze
# 3. "explode" all multipolygons into single polygons
# 4. Parse the most recent 5 years into different geopackages 
#    to process into independent data layers in a loop, while 
#    documenting the percentiles for 2 attributes of interest, 
#    to use as max values in the range for the config of the 
#    vizualization workflow

# Author: Juliet Cohen
# Date: 12/20/23
# Server: Datateam
# Conda Environment: "geospatial"

import geopandas as gpd
import xarray as xar
import pandas as pd
import numpy as np

# Lake area time series data GeoPackage
gdf = gpd.read_file("/var/data/submission/pdg/nitze_lake_change/time_series_2023-04-05/INitze_Lakes_merged_v3_PDG_Testset.gpkg")
# Lake area time series data NetCDF
area = xar.open_dataset("/var/data/submission/pdg/nitze_lake_change/time_series_2023-04-05/Lakes_IngmarPDG_annual_area.nc")

# convert the NetCDF file into a dataframe, with columns for:
# ID_merged, year, permanent_water, seasonal_water
area_df = area.to_dataframe().reset_index()
# drop NA values (important to do for this file only bc these permanent_water and seasonal_water are what will be visualized)
area_df.dropna(subset=['permanent_water', 'seasonal_water'], inplace = True)

# merge the dataframe, retaining only ID_merged values that exist in both files
# the spatial dataframe must be the left argument to retain the geometries
merged_data = gdf.merge(right = area_df,
                        how = 'inner', # only retain lakes that also have data for permanent water and seasonal water 
                        on = 'ID_merged')

print("Merge complete. Parsing years.")
# Save the most recent 5 years separately as gpkg's for 
# input into the viz-workflow because each year will be a layer
last_5_yrs = [2017, 2018, 2019, 2020, 2021]
for yr in last_5_yrs:
    merged_data_annual = merged_data[merged_data['year']==yr]
    merged_data_annual_exploded = merged_data_annual.explode(index_parts = True)
    output_path = f"/var/data/submission/pdg/nitze_lake_change/time_series_2023-04-05/exploded_annual_2017-2021/yr{yr}/merged_lakes_{yr}_exploded.gpkg"
    merged_data_annual_exploded.to_file(output_path, driver = "GPKG")
    print(f"Saved combined and exploded data for {yr} to:\n{output_path}.")
    # calculate and document the 99.99th percentile for permanent_water for viz workflow config range max val
    pw_perc = np.percentile(merged_data_annual_exploded['permanent_water'], 99.99)
    print(f"{yr} permanent water 99.99th percentile: {pw_perc}")
    # calculate and document the 95th percentile for seasonal_water for viz workflow config range max val
    sw_perc = np.percentile(merged_data_annual_exploded['seasonal_water'], 95)
    print(f"{yr} seasonal water 95th percentile: {sw_perc}")

print("Script complete.")
