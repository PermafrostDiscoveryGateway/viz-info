## `dedup-before-viz`

For some datasets, applying the neighbor deduplication method would be helpful so that users can access deduplicated, clean data outside of the tiled format. This means that the neighbor deduplication approach that can be applied withint the viz workflow for the satged tilesets should instead be applied to the input data before it is tiled. The script `dedup_before_viz_example.py` shows an example of this process for 2 adjacent UTM zones of lake change data from Ingmar Nitze. 

### Notes:

- This script’s output file is a geopackage that has the same geometries as the input files (concatenated), but the output file also has a boolean attribute `staging_duplicated` where `True` represents the row is a duplicate lake, and `False` represents the lake we should retain in the data. 
- The script reads in two adjacent UTM zones (parquet files) that Ingmar passed on for testing the deduplication method. One important pre-processing step included here is adding a new attribute called `source_file` before executing the deduplication. This is relevant because our deduplication labeling only executes if the input data contains polygons from 2 different source files.
- You may test this approach yourself with different parameters for `deduplicate_neighbors`, but remember the following:
  - `return_intersections` must be `False` for the current version of the `viz-staging` package
  -  include double brackets around the value of `keep_rules`
  - The value of `prop_area` needs to be None because the units of area in your data attributes may not be in the same units as the CRS
  - The units of the CRS of the input data are important because the proportion of the overlap of two geometries is used to determine if they are duplicates, an optionally the distance between the centroids can be used as well, so make sure to double check that the CRS is what you expect (projected or not) before you execute this deduplication on your files.
