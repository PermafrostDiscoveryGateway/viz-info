TODO

- Create a standardized workflow for raster data
	- TODO: link to examples on datateam
- Add an "archiving" step to the workflow that prepares geopackage files for publishing, using [these methods in the supplementary steps dir](https://github.com/PermafrostDiscoveryGateway/viz-staging/blob/main/supplementary_steps/archive_vector_tiles.py)
- Auto-generate some metadata
- Add testing: `pytest`
- documentation website
	- autogenerate from doc strings
	- may want to convert python doc strings to the "REst" format, the most common format. [Here is a package](https://github.com/dadadel/pyment) you can do that with.
- dynamic tiling server
	- from [titiler](https://developmentseed.org/titiler/dynamic_tiling/)
		- can recolor on the fly
		- don't need to pre-create PNG tiles
	- mosaicing
		- rio-tiler-mosaic takes a list of image files (assets), a tiler handler(customor from rio-tiler) and Web Mercator XYZ indices as input. -> https://medium.com/devseed/cog-talk-part-2-mosaics-bbbf474e66df, returns tile (and mask)
- [lambda-tiler](https://github.com/vincentsarago/lambda-tiler)
- Use STAC?
	- See https://github.nceas.ucsb.edu/KNB/arctic-data/pull/368#issuecomment-27640