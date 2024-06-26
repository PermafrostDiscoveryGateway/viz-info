# Roadmap

We have a lot of ideas for new features!

## Planned developments

- See issues in each of the Python package repos. Some are tagged "good first issue"
- Create a standardized workflow for raster data: We need to be able to tile large raster data, not just large vector data.
- Some changes need to be made to the GeoPackage files for processing and publishing. The [viz-staging issues](https://github.com/PermafrostDiscoveryGateway/viz-staging/issues) describe some pre-processing steps to add to `viz-staging`. Also, some methods are built for geopackage processing in the [supplementary steps dir](https://github.com/PermafrostDiscoveryGateway/viz-staging/blob/main/supplementary_steps/archive_vector_tiles.py).

## Possible developments

- Issues in the repos for `viz-staging`, `viz-raster`, and `viz-workflow` are the highest priority.
Auto-generate some parts of the EML metadata for the input data
- Add testing to the python packages (e.g. using `pytest`)
  - note that scripts for this have been started in `viz-staging` and `viz-raster`
- Build a documentation website for the python packages (autogenerate from doc strings)
	- may want to convert python doc strings to the "REst" format, the most common format. [Here is a package](https://github.com/dadadel/pyment) you can do that with.
- Create a dynamic tiling server
  - see [titiler](https://developmentseed.org/titiler/dynamic_tiling/), [ways to use Cloud Optimized GeoTIFF](https://medium.com/devseed/cog-talk-part-2-mosaics-bbbf474e66df), [lambda-tiler](https://github.com/vincentsarago/lambda-tiler)
  - This would allow for some features that have been requested, namely:
    - recolor web tiles on the fly (e.g. a user viewing a map could set their own color scale for all of the raster layers)
    - point information for raster layers (e.g. a user could click a raster layer, and the server could send back information about that layer at the given lat/lon)
    - we would no longer have to pre-create all the PNG tiles either
    - would make it easier for a user to download a given area of data at a given resolution
- Use [STAC](https://stacspec.org/en) to catalog our spatial assets
	- See also https://github.nceas.ucsb.edu/KNB/arctic-data/pull/368#issuecomment-27640
