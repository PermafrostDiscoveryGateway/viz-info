# Python packages created for PDG
We have created five repos that contain python code for preparing data for displaying in Cesium and for archiving.

## viz-staging (pdgstaging)
[**GitHub link**](https://github.com/PermafrostDiscoveryGateway/viz-staging)

This package was designed to prepare vector data for future converstion steps. Mainly, it "slices" large vector files into smaller files that each have a bounding box corresponding to a tile in a given TMS. It also adds properties, re-projects the data, does deduplication flagging, removes duplicates if specified to do so in the config, deals with filepaths, and all the configuration options.

## viz-raster (pdgraster)
[**GitHub link**](https://github.com/PermafrostDiscoveryGateway/viz-raster)

This package deals with the conversion of vector data into rasters - both GeoTIFFs for archiving and PNGs for displaying in Cesium. Though it has generic classes and methods in it that could be used flexibly, at this point it depends on `pdgstaging` and assumes that input has already gone through the staging step.

## viz-workflow (pdg_workflow)
[**GitHub link**](https://github.com/PermafrostDiscoveryGateway/viz-workflow)

The viz-workflow repo deals with running methods from the above packages in parallel. It has a couple of branches under active development:
- [main](https://github.com/PermafrostDiscoveryGateway/viz-workflow/tree/main) - currently uses `ray` for parallelization on the Delta server hosted by the National Center for Supercomputing Applications
- [kubernetes, docker, and parsl workflow](https://github.com/PermafrostDiscoveryGateway/viz-workflow/tree/enhancement-1-k8s/docker-parsl-workflow) - converting the workflow to use Kubernetes, Docker, and parsl to take advantage of the UCSB high performance computing clusters and be interoperable across different platforms such as the Google Cloud Platform

## py3dtiles
[**GitHub link**](https://github.com/PermafrostDiscoveryGateway/py3dtiles)

The original `py3dtiles` python library was original created by an organization named Oslandia and is under active development and maintenance on Gitlab. It was designed to convert point data into Cesium 3D tiles. We have forked and extended it so that it can be used to convert polygons to Cesium 3D tiles.

We should try to keep our version of the package up-to-date with the gitlab/Oslandia version, so that we can include their fixes & enhancements. I watch follow changes on the Gitlab repo and pull them in every two weeks or as needed. Instructions on how to pull in changes from Gitlab to GitHub are [documented in the readme of the repo](https://github.com/PermafrostDiscoveryGateway/py3dtiles/blob/main/README.rst).

Eventually it would be awesome to do a merge request and give them the change to incorporate the changes we made back into their library.

## viz-3dtiles (viz_3dtiles)
[**GitHub link**](https://github.com/PermafrostDiscoveryGateway/viz-3dtiles)

The viz-3d tiles package is essentially a wrapper around the py3dtiles library. It adds classes & functions for building the heirachy of Cesium 3D tileset JSON files, and for reading in shapefiles

Since it was created, some of these classes were developed into the original `py3dtiles` library. We might want to eventually make use of those new classes instead. See [PermafrostDiscoveryGateway/py3dtiles issues#6](https://github.com/PermafrostDiscoveryGateway/py3dtiles/issues/6).

# Releases and EZID

Each time a viz repo's main branche is updated, we make a release with a version. See [here](https://github.com/PermafrostDiscoveryGateway/viz-staging/releases) for an example page of all the releases for one repo. The new release `version` should always be updated in the `pyproject.toml` file. Contributors (`authors`) should not be removed, but contributors should be appended. 

We also have to update  EZID so that the release can be cited. After making the release, here are the steps to update EZID:

- Go to the [EZID website](https://ezid.cdlib.org/search) and search for the most recent completed release of the package’s DOI, the one _prior_ to the release you are working on creating an XML for.
- Click the link to open the XML and copy it
- In VScode, paste the copied XML into a new xml file (name it anything, such as `release_new.XML`), and correct formatting if needed (you can use an online pretty XML formatter).
- Make all necessary changes to the XML:
  - Version number for the release itself
  - Date of release
  - Software heritage ID
    - To retrieve this, first navigate to the software heritage website for the repo (for viz-workflow it's [here](https://archive.softwareheritage.org/browse/origin/directory/?origin_url=https://github.com/PermafrostDiscoveryGateway/viz-workflow)) and click “save again” (button on thr right side of the page) then retrieve the Software heritage ID by copying the “Tip revision” string (bolded numbers and letters like `f39a3b7b53823e41ebae1d28136a95cdde5df716`)
  - Make sure the DOI “new version of” is the older version DOI and the new DOI is where it should be
- Use the UPDATE command, the last line in [these instructions](https://gist.github.com/rushirajnenuji/cd579fc1993396aaa8863295cd4a4111), making sure to replace the DOI and the name of the XML too

Link to this EZID page when referencing the package release in documentation.

# Other python packages
- Our packages rely heavily on some external packages that it would be good to become familiar with:
	- [GeoPandas](https://geopandas.org/en/stable/) (and [pandas](https://pandas.pydata.org/)) - for reading, manipulating, and writing vector data
	- [Rasterio](https://rasterio.readthedocs.io/en/latest/) - for reading, manipulating, and writing raster data
  - [ray](https://docs.ray.io/en/latest/ray-overview/getting-started.html) - for parallelization in the Delta server High Performance Computing environment 
  - [parsl](https://parsl.readthedocs.io/en/stable/) - for parallelization in the UCSB server High Performance Computing Environment Google Kubernetes Engine
	- [rio-tiler](https://github.com/cogeotiff/rio-tiler) - not used in the workflow yet, but we may want to incorporate it when our workflow is extended to allow raster data as input (it has functionality to deal with overlapping rasters, partial reading of raster data, categorical color palettes, and a lot more)

