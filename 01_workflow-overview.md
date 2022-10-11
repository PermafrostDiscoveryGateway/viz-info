# PDG visualization workflow overview

- The goal of the workflow is to input geospatial files and prepare them for archiving in DataONE repositories as well as for viewing in online, interactive maps.
- We need to prepare the data in this way because:
  - Our input files are much too large to display on the web. A user visiting our website would first need to download all of the data, which would take days in some cases. The browser would not be able to render such large files either (in fact, some files are also too large to render in Desktop software)
  - Some input formats are not supported by most browsers - e.g. GeoTIFF (many GeoTIFFs also don't have a built in color scale)
  - Some data layers are made up of multiple files that vary in size and have unpredictable bounding boxes. As it is, it would be difficult for a researcher to download the section of data that they are interested in.
  - Some files overlap with one another and so we need to "deduplicate" these sections of overlap
- To prepare data we:
  - combine input files that are part of the same layer
  - convert them to files of a standard size and geospatial extent
  - convert them to formats that are good for archiving (geopackage and GeoTIFF) and good for the web (png images and Cesium 3D tiles) 
- See [these slides](https://docs.google.com/presentation/d/13CSV7w8Ew7XoD0YrCcgGNvuh9DrLSsF-6fL16hJBWiE) for a visual overview of the workflow

## Input formats

Currently our visualization pipeline is designed to take vector files (shapefiles, geopackage, geojson) as input. With a little work, we can extend it to also take raster files (geoTIFF) as input.

## Output formats

### Cesium 3D tiles

TODO

### Web tiles

To display raster data on the web, we convert them to web tiles: png or jpeg image files that are of a standard size, cover a known geospatial area, and are of a known resolution.

Here is quick little introduction to web tiles and why we use them: - [Learn how zoomable maps works, what coordinate systems are, and how to convert between them](https://www.maptiler.com/google-maps-coordinates-tile-bounds-projection/#3/-28.58/66.58)

**tile** 
a rectangular pictorial representation of geographic data which can be uniquely defined by a pair of indices for the column and row (x & y) along with an identifier for the tile matrix.

**tile matrix**  
a collection of tiles for a fixed scale (z)

**tile matrix set** ("TMS")
a collection of tile matrices defined at different scales (z-indices)

**OGC Two Dimensional Tile Matrix Set**
a collection of standardized tile matrix sets, see [the docs](https://docs.opengeospatial.org/is/17-083r2/17-083r2.html)

**WorldCRS84Quad**
the OCG 2D TMS that we have generally been using for the tiles we create because it is supported by Cesium. Defined [here](https://docs.opengeospatial.org/is/17-083r2/17-083r2.html#64).