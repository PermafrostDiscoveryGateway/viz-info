# PDG visualization workflow overview

- The goal of the workflow is to input geospatial files and prepare them for archiving in DataONE repositories as well as for viewing in online, interactive maps.
- We need to prepare the data in this way because:
  - Our input files are usually much too large in extent and has much too high resolution to display directly on the web without tiling. A user visiting our website would first need to download all of the data, which would take days in some cases. The browser would not be able to render such large files either (in fact, some files are also too large to render in desktop software such as ArcGIS).
  - Some input formats are not supported by most browsers - e.g. GeoTIFF (many GeoTIFFs also don't have a built in color scale)
  - Some data layers are made up of multiple files that vary in size and have unpredictable bounding boxes. As it is, it would be difficult for a researcher to download only the spatial portion or temporal slice of data that they are interested in.
  - Some files overlap with one another and so we need to "deduplicate" these sections of overlap. The stage of the workflow at which we do this and which deduplication approach is applied may depend on the researcher's preference.
- To prepare data for visualization and archival, we do the following:
  - combine input files that are part of the same layer 
  - convert them to files of a standard size and geospatial extent
  - convert them to formats that are efficient for archiving (geopackage and GeoTIFF) and good for the web (PNG images and Cesium 3D tiles) 
- See [these slides](https://docs.google.com/presentation/d/13CSV7w8Ew7XoD0YrCcgGNvuh9DrLSsF-6fL16hJBWiE) for a visual overview of the workflow

## Input formats

Currently our visualization pipeline is designed to take vector files as input, such as shapefiles, GeoPackages, or GeoJSON files. With a little work, we can extend it to also take raster files (geoTIFF) as input.

## Output formats

There are four output formats for the same data in standardized tilesets.
- Two of these tilesets, the GeoPackages and GeoTIFFS, allow data to be used for further analysis and pair well with other PDG datasets since they are standardized.
- The third  tileset of PNG images is only for visualization and does not contain actual data for users to utilize, so that tileset is not archived. This tileset helps us visualize the data quickly on the portal (as it is pre-rendered for all zoom-levels and statistics) and helps the users understand what regions and layers they are interested in, as well as trends in the data with a palette.
- The fourth tileset of 3D tiles is in vector format and allows for users to select individual polygons in the user interface and view that polygons specific attribute values in a pop-up window.

See details for these four formats below.

### GeoPackages (vector data)

A tileset of the data for the highest resolution only. This data is the first output from the viz-workflow, so the standardization of extent and the polygons, and the deduplication, are both done in the staging step. Vector data is more precise than raster data. This data is not aggregated to lower resolutions. All existing attributes for geometries in the input data are retained, plus extra attributes are added that are helpful for later steps in the viz pipeline.

### GeoTIFFs (raster data)

A tileset of the data for all resolutions, starting at the highest resolution. Lower resolution rasters are created by resampling the higher resolution rasters. This tileset is the second output from the viz pipeline. In the rasterization step, the statistics are calculated that are specified in the config. A band is created in every raster for every statistic.

### Web tiles (raster data, lightweight and with a pre-defined palette)

To display raster data on the web, we convert the GeoTIFF tileset to a web tile tileset: PNG or jpeg image files that are of a standard size, cover a known geospatial area, and are of a known resolution. This is the third product from the viz pipeline, which applies a palette to each stat (band) in the GeoTIFFs. Each web tile tileset becomes a layer on the portal.

Here is quick little introduction to web tiles and why we use them: - [Learn how zoomable maps works, what coordinate systems are, and how to convert between them](https://www.maptiler.com/google-maps-coordinates-tile-bounds-projection/#3/-28.58/66.58)

### Cesium 3D tiles (vector data)

Cesium 3D Tiles is a specification for displaying vector data in 3D. It allows for breaking large vector datasets into smaller pieces which can be downloaded as need in the browser, so it's also great for displaying very large 2D vector data.

A 3D tile comprises two parts: The tile content (the spatial information about the structure of the 3D object), and metadata about that content. In the Cesium 3D Tile specification, tile content can be represented in three different formats: Batched 3D Models, Instanced 3D Model, and Point Clouds. For our purposes thus far, we are creating **Batched 3D Models** (files with the extension `.B3DM`). The metadata is always represented with JSON that is referred to as the "Tileset".

We create a a hierarchy of Tileset JSON, so that the browser can download information incrementally as the user zooms into the area with 3D tiles. The 3D tiles are not rendered until the user is sufficiently zoomed in (how zoomed in they must be to render tiles is defined in the Tileset JSON by the "geometricError").

Here are some resources to learn more about Cesium 3D Tiles:

- [Introductory info about 3D tiles](https://cesium.com/why-cesium/3d-tiles/)
- [Reference card](https://github.com/CesiumGS/3d-tiles/blob/main/3d-tiles-reference-card.pdf) - A great place to start learning about the structure of 3D tiles. 
- [The complete specification](https://github.com/CesiumGS/3d-tiles) - For in-depth details about the spec. See it in [HTML](https://docs.opengeospatial.org/cs/18-053r2/18-053r2.html).

## General Terminology

**Tile** 
- a rectangular pictorial representation of geographic data which can be uniquely defined by a pair of indices for the column and row (x & y) along with an identifier for the tile matrix.

**Tile Matrix**  
- a collection of tiles for a fixed scale (z)

**Tile Matrix Set** ("TMS")
- a collection of tile matrices defined at different scales (z-indices)

**Open Geospatial Consortium Two-Dimensional Tile Matrix Set**
- a collection of standardized tile matrix sets, see [the docs](https://docs.opengeospatial.org/is/17-083r2/17-083r2.html)

**WGS1984Quad**
- the Open Geospatial Consortium 2D Tile Matrix Set that we use for the tiles we create because it is supported by Cesium. Defined [here](https://docs.ogc.org/is/17-083r2/17-083r2.html#65). 