# Author: Juliet Cohen

# Overview:
# identify, document, and remove rows with an invalid value in any column (Na, inf, or -inf)
# in lake change input data from Ingmar Nitze,
# and save the cleaned files to a new directory

# using conda env perm_ground

import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import os

# collect all lake_change.gpkg filepaths in Ingmar's data
base_dir = Path('/home/pdg/data/nitze_lake_change/data_2022-11-04/lake_change_GD/')
filename = 'lake_change.gpkg'
# To define each .gpkg file within each subdir as a string representation with forward slashes,
# use as_posix()
# The ** represents that any subdir string can be present between the base_dir and the filename
input = [p.as_posix() for p in base_dir.glob('**/' + filename)]
print(f"Collected {len(input)} lake_change.gpkg filepaths.")

# Overview of loop:
# 1. import each filepath as a gdf
# 2. document which rows have invalid value in any column (Na, inf, or -inf)
#    as a separate csv for each input gpkg
# 3. drop any row with an invalid value
# 4. save as new lake change file

for path in input:
    print(f"Checking file {path}.")
    gdf = gpd.read_file(path)

    # first identify any rows with invalid values
    # to document which will be dropped for data visualization
    error_rows = []
    # first convert any infinite values to NA
    gdf.replace([np.inf, -np.inf], np.nan, inplace = True)
    for index, row in gdf.iterrows():
        if row.isna().any():
            error_rows.append(row)
    error_rows_df = pd.DataFrame(error_rows)

    # hard-code the start of the path to directory for the erroneous data
    filepath_start = "/home/jcohen/lake_change_GD_workflow/workflow_cleaned/error_data_documentation/"
    # next, pull the last couple parts of filepath to ID which lake_change.gpkg
    # is being processed, following Ingmar's directory hierarchy
    directory, filename = os.path.split(path)
    filepath_sections = directory.split(os.sep)
    relevant_sections = filepath_sections[-2:]
    partial_filepath = relevant_sections[0] + "/" + relevant_sections[1]
    full_filepath = filepath_start + partial_filepath + "/error_rows.csv"
    # make the subdirectories if they do not yet exist
    directory_path = os.path.dirname(full_filepath)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    # save the df of rows with invalid values as a csv
    # save the index because communicates to Ingmar which rows in his original data
    # contain invalid values
    error_rows_df.to_csv(full_filepath, index = True)
    print(f"Saved rows with invalid values for lake change GDF:\n{path}\nto file:\n{full_filepath}")

    # drop the rows with NA values in any column
    gdf.dropna(axis = 0, inplace = True)

    # save cleaned lake change file to new directory
    # hard-code the start of the path to directory for the cleaned data
    filepath_start = "/home/jcohen/lake_change_GD_workflow/workflow_cleaned/cleaned_files/"
    # next, pull the last couple parts of filepath to ID which lake_change.gpkg
    # is being processed, following Ingmar's directory hierarchy
    directory, filename = os.path.split(path)
    filepath_sections = directory.split(os.sep)
    relevant_sections = filepath_sections[-2:] + ['lake_change_cleaned.gpkg']
    filepath_end = relevant_sections[0] + "/" + relevant_sections[1] + "/" + relevant_sections[2]
    full_filepath = filepath_start + filepath_end
    print(f"Saving file to {full_filepath}")
    # make the subdirectories if they do not yet exist
    directory_path = os.path.dirname(full_filepath)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    gdf.to_file(full_filepath, driver = "GPKG") 

print(f"Cleaning complete.")