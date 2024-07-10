# Record the duplicate polygons in the staged tiles
# created from UTM zones 32617 and 32618 on 6/6/24
# so we can check the validity of branch to re-integrating 
# the option to return intersections in the neighbor dedup approach
# issue: https://github.com/PermafrostDiscoveryGateway/viz-staging/issues/44


import geopandas as gpd
from pathlib import Path
import os


# collect all staged filepaths 
base_dir = Path('/home/jcohen/check_dedup_forIN/parsl_workflow/staged/')
ext = ".gpkg"
input = [p.as_posix() for p in base_dir.glob('**/*' + ext)]
print(f"Collected {len(input)} staged filepaths.")

# 1. import each filepath as a gdf
# 2. check for any True values for staging_duplicated attribute
# 3. if any True values exist, append the True rows to a new gdf
# 4. for the original gdf read in, remove all atts that start with "staging"
#   and save the subset gdf to a directory

# Directory to save the modified files
output_dir = "/home/jcohen/check_dedup_forIN/tiles_with_dups"
os.makedirs(output_dir, exist_ok = True)

# Initialize an empty GeoDataFrame for storing rows with True in staging_duplicated
dup_rows = gpd.GeoDataFrame()

# Loop through each GeoPackage file
for filepath in input:
    
    gdf = gpd.read_file(filepath)
    
    # Check for rows where staging_duplicated is True and subset to dup_rows
    true_rows = gdf[gdf['staging_duplicated'] == True]
    dup_rows = dup_rows.append(true_rows, ignore_index = True)
    
    # Remove any columns that start with "staging" and save tile to new dir for testing branch
    gdf.drop(columns = [col for col in gdf.columns if col.startswith('staging')], inplace = True)
    filename = os.path.basename(filepath)
    output_path = os.path.join(output_dir, filename)
    gdf.to_file(output_path, driver = "GPKG")

# Save the dup_rows to a new GeoPackage file
print ("Saving duplicated_rows.gpkg.")
dup_rows.to_file(output_dir + '/duplicated_rows.gpkg', driver = 'GPKG')

print("Script complete")

    


