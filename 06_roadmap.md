# Roadmap

Here are a few things that we still have left to do, as well as some ideas on future developments.

## Planned developments

- See issues in each of the python package repos
- Create a standardized workflow for raster data: We need to be able to tile large raster data, not just large vector data. Robyn has been doing this manually so far. You can checkout some of my examples on the datateam server (warning: some code here is a bit messy):
	- Under the directory `/home/thiessenbock/PDG-test/exploratory/`, see the directories:
		- `dai-2022`
		- `webb-2022`
		- `circumpolar_arctic_vegetation`
- Some changes need to be made to the geopackage files for publishing. Methods are built for this in the [supplementary steps dir](https://github.com/PermafrostDiscoveryGateway/viz-staging/blob/main/supplementary_steps/archive_vector_tiles.py), but we still need to build this last step into the workflow

## Possible developments

- Auto-generate some parts of the EML metadata for the input data
- Add testing to the python packages (e.g. using `pytest`)
- Build a documentation website for the python packages (autogenerate from doc strings)
	- may want to convert python doc strings to the "REst" format, the most common format. [Here is a package](https://github.com/dadadel/pyment) you can do that with.
- Cerate a dynamic tiling server
  - see [titiler](https://developmentseed.org/titiler/dynamic_tiling/), [ways to use Cloud Optimized GeoTIFF](https://medium.com/devseed/cog-talk-part-2-mosaics-bbbf474e66df), [lambda-tiler](https://github.com/vincentsarago/lambda-tiler)
  - This would allow for some features that have been requested, namely:
    - recolor web tiles on the fly (e.g. a user viewing a map could set their own color scale for all of the raster layers)
    - point information for raster layers (e.g. a user could click a raster layer, and the server could send back information about that layer at the given lat/lon)
    - we would no longer have to pre-create all the PNG tiles either
    - would make it easier for a user to download a given area of data at a given resolution
- Use [STAC](https://stacspec.org/en) to catalog our spatial assets
	- See also https://github.nceas.ucsb.edu/KNB/arctic-data/pull/368#issuecomment-27640