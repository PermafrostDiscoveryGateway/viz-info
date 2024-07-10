# Roadmap

We have a lot of ideas for new features and data layers! See our [Project Boards](https://github.com/orgs/PermafrostDiscoveryGateway/projects) for documented features, bug fixes, and enhancements organized by priority:

- [Data Layers Project Board](https://github.com/orgs/PermafrostDiscoveryGateway/projects/18/views/2)
  - all data layers that we have added or will add have their own ticket with information about the dataset itself and any techincal blockers
- [Visualization Workflow Project Board](https://github.com/orgs/PermafrostDiscoveryGateway/projects/16/views/2)
  - tickets related to the following viz-packages: `viz-staging`, `viz-raster`, `viz-workflow`, & `viz-3dtiles`
- [Overall Visualization and Front-end Development Project Board](https://github.com/orgs/PermafrostDiscoveryGateway/projects/3)
  - tickets related to MetacatUI that will enable new tools and visualization options in the PDG portal as well as other Arctic Data Center Portals

In these project boards, the `P0` category is the highest priority and all the tickets should be resolved before tackling `P1`, `P2`, and `P3`. There are technical blockers that inhibit some higher priority tickets from being resolved, and sometimes lower-priority tickets are moved up in the queue if they are "low hanging fruit." An example would be a small vector dataset that can easily be processed with a simple workflow run with minimal preprocessing. More recently, the PDG project has emphasized the goal of publishing data layers in sync with the publication of the associated scientific paper, so it's good practice to keep track of those details in the data layer tickets. 

## Planned developments

- See issues in each of the Python package repos. Some are tagged "good first issue"
  - See [here](https://github.com/PermafrostDiscoveryGateway/viz-staging/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) for simpler `viz-staging` tickets that focus on automated checks and corrections for the GeoPackage files.
- Create a standardized workflow for raster data: We need to be able to tile large raster data, not just large vector data.
- Add automated testing to the python packages using `pytest`
  - Note that scripts for this have been started in `viz-staging` and `viz-raster`

## Possible developments

- Auto-generate some parts of the EML metadata for the input data
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
