# workflow.ipynb as a script - viz workflow steps
# staging, rasterization (all z-levels), web-tiling, and 3d-tiles
# see workflow.ipynb for more documentation of steps
# IMPORTANT: remember to change log.log outpath to your own home dir!

# using venv environment with installed:
# viz-staging
# viz-raster
# viz-3dtiles
# (a conda environment is also appropriate)

# input data import
from pathlib import Path

# staging
import pdgstaging
from pdgstaging import TileStager

# rasterization
import pdgraster
from pdgraster import RasterTiler

# 3D tiling
from viz_3dtiles import TreeGenerator, BoundingVolumeRegion
from shapely.geometry import box

# visual checks
import geopandas as gpd

# logging
from datetime import datetime
import logging
import logging.handlers
import os

# --------------------------------------------------------------

# import 3 input data files
base_dir = Path('/home/jcohen/iwp_russia_subset_clipToFP_PR/iwp')
filename = '*.shp'
# To define each .shp file within each subdir as a string representation with forward slashes, use as_posix()
# The ** represents that any subdir string can be present between the base_dir and the filename
input = [p.as_posix() for p in base_dir.glob('**/' + filename)]

# pull filepaths for footprints in the same way we pulled IWP shp file paths
base_dir_fp = Path('/home/jcohen/iwp_russia_subset_clipToFP_PR/footprints')
fps = [p.as_posix() for p in base_dir_fp.glob('**/' + filename)]

# logging config
# Juliet's log path: /home/jcohen/pdg-info/helpful-code/workflow_no_dedup/log.log
handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "/home/user/path/to/log.log")) # change path as needed to your home dir
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)

# --------------------------------------------------------------

print("staging files...")

# define stager and stage all input files
stager = TileStager({
  "deduplicate_clip_to_footprint": False, 
  "dir_input": "/home/jcohen/iwp_russia_subset_clipToFP_PR/iwp/", 
  "ext_input": ".shp",
  "ext_footprints": ".shp",
  "dir_footprints": "/home/jcohen/iwp_russia_subset_clipToFP_PR/footprints/", 
  "dir_staged": "staged/",
  "dir_geotiff": "geotiff/", 
  "dir_web_tiles": "web_tiles/", 
  "filename_staging_summary": "staging_summary.csv",
  "filename_rasterization_events": "raster_events.csv",
  "filename_rasters_summary": "raster_summary.csv",
  "filename_config": "config",
  "simplify_tolerance": 0.1,
  "tms_id": "WGS1984Quad",
  "z_range": [
    0,
    15
  ],
  "geometricError": 57,
  "z_coord": 0,
  "statistics": [
    {
      "name": "iwp_coverage",
      "weight_by": "area",
      "property": "area_per_pixel_area",
      "aggregation_method": "sum",
      "resampling_method": "average",
      "val_range": [
        0,
        1
      ],
      "palette": [
        "#66339952",
        "#ffcc00"
      ],
      "nodata_val": 0,
      "nodata_color": "#ffffff00"
    },
  ],
  "deduplicate_at": None,
  "deduplicate_keep_rules": [],
  "deduplicate_method": None
}).stage_all()

print("staging done. rasterizing and web tiling...")

# --------------------------------------------------------------

# rasterization and web-tiling
RasterTiler({
  "deduplicate_clip_to_footprint": False, 
  "dir_input": "/home/jcohen/iwp_russia_subset_clipToFP_PR/iwp/", 
  "ext_input": ".shp",
  "ext_footprints": ".shp",
  "dir_footprints": "/home/jcohen/iwp_russia_subset_clipToFP_PR/footprints/", 
  "dir_staged": "staged/",
  "dir_geotiff": "geotiff/", 
  "dir_web_tiles": "web_tiles/", 
  "filename_staging_summary": "staging_summary.csv",
  "filename_rasterization_events": "raster_events.csv",
  "filename_rasters_summary": "raster_summary.csv",
  "filename_config": "config",
  "simplify_tolerance": 0.1,
  "tms_id": "WGS1984Quad",
  "z_range": [
    0,
    15
  ],
  "geometricError": 57,
  "z_coord": 0,
  "statistics": [
    {
      "name": "iwp_coverage",
      "weight_by": "area",
      "property": "area_per_pixel_area",
      "aggregation_method": "sum",
      "resampling_method": "average",
      "val_range": [
        0,
        1
      ],
      "palette": [
        "#66339952",
        "#ffcc00"
      ],
      "nodata_val": 0,
      "nodata_color": "#ffffff00"
    },
  ],
  "deduplicate_at": None,
  "deduplicate_keep_rules": [],
  "deduplicate_method": None
}).rasterize_all()

print("rasterizing and web tiling done. creating 3d tiles...")

# --------------------------------------------------------------

# 3d-tiling

class StagedTo3DConverter():
    """
        Processes staged vector data into Cesium 3D tiles according to the
        settings in a config file or dict. This class acts as the orchestrator
        of the other viz-3dtiles classes, and coordinates the sending and
        receiving of information between them.
    """

    def __init__(
        self,
        config
    ):
        """
            Initialize the StagedTo3DConverter class.

            Parameters
            ----------

            config : dict or str
                A dictionary of configuration settings or a path to a config
                JSON file. (See help(pdgstaging.ConfigManager))
        """

        self.config = pdgstaging.ConfigManager(config)
        self.tiles = pdgstaging.TilePathManager(
            **self.config.get_path_manager_config())

    def all_staged_to_3dtiles(
        self
    ):
        """
            Process all staged vector tiles into 3D tiles.
        """

        # Get the list of staged vector tiles
        paths = self.tiles.get_filenames_from_dir('staged')
        # Process each tile
        for path in paths:
            self.staged_to_3dtile(path)

    def staged_to_3dtile(self, path):
        """
            Convert a staged vector tile into a B3DM tile file and a matching
            JSON tileset file.

            Parameters
            ----------
            path : str
                The path to the staged vector tile.

            Returns
            -------
            tile, tileset : Cesium3DTile, Tileset
                The Cesium3DTiles and Cesium3DTileset objects
        """

        try:

            # Get information about the tile from the path
            tile = self.tiles.tile_from_path(path)
            out_path = self.tiles.path_from_tile(tile, '3dtiles')

            tile_bv = self.bounding_region_for_tile(tile)

            # Get the filename of the tile WITHOUT the extension
            tile_filename = os.path.splitext(os.path.basename(out_path))[0]
            # Get the base of the path, without the filename
            tile_dir = os.path.dirname(out_path) + os.path.sep

            # Log the event
            root.info(
                f'Creating 3dtile from {path} for tile {tile} to {out_path}.')

            # Read in the staged vector tile
            gdf = gpd.read_file(path)

            # Check if the gdf is empty
            if len(gdf) == 0:
                root.warning(
                    f'Vector tile {path} is empty. 3D tile will not be'
                    ' created.')
                return

            # Remove polygons with centroids that are outside the tile boundary
            prop_cent_in_tile = self.config.polygon_prop(
                'centroid_within_tile')
            gdf = gdf[gdf[prop_cent_in_tile]]

            # Check if deduplication should be performed
            dedup_here = self.config.deduplicate_at('3dtiles')
            dedup_method = self.config.get_deduplication_method()

            # Deduplicate if required
            if dedup_here and (dedup_method is not None):
                dedup_config = self.config.get_deduplication_config(gdf)
                dedup = dedup_method(gdf, **dedup_config)
                gdf = dedup['keep']

                # The tile could theoretically be empty after deduplication
                if len(gdf) == 0:
                    root.warning(
                        f'Vector tile {path} is empty after deduplication.'
                        ' 3D Tile will not be created.')
                    return

            # Create & save the b3dm file
            ces_tile, ces_tileset = TreeGenerator.leaf_tile_from_gdf(
                gdf,
                dir=tile_dir,
                filename=tile_filename,
                z=self.config.get('z_coord'),
                geometricError=self.config.get('geometricError'),
                tilesetVersion=self.config.get('version'),
                boundingVolume=tile_bv
            )

            return ces_tile, ces_tileset

        except Exception as e:
            root.error(f'Error creating 3D Tile from {path}.')
            root.error(e)

    def parent_3dtiles_from_children(self, tiles, bv_limit=None):
        """
            Create parent Cesium 3D Tileset json files that point to
            of child JSON files in the tile tree hierarchy.

            Parameters
            ----------
            tiles : list of morecantile.Tile
                The list of tiles to create parent tiles for.
        """

        tile_manager = self.tiles
        config_manager = self.config

        tileset_objs = []

        # Make the next level of parent tiles
        for parent_tile in tiles:
            # Get the path to the parent tile
            parent_path = tile_manager.path_from_tile(parent_tile, '3dtiles')
            # Get just the base dir without the filename
            parent_dir = os.path.dirname(parent_path)
            # Get the filename of the parent tile, without the extension
            parent_filename = os.path.basename(parent_path)
            parent_filename = os.path.splitext(parent_filename)[0]
            # Get the children paths for this parent tile
            child_paths = tile_manager.get_child_paths(parent_tile, '3dtiles')
            # Remove paths that do not exist
            child_paths = tile_manager.remove_nonexistent_paths(child_paths)
            # Get the parent bounding volume
            parent_bv = self.bounding_region_for_tile(
                parent_tile, limit_to=bv_limit)
            # If the bounding region is outside t
            # Get the version
            version = config_manager.get('version')
            # Get the geometric error
            geometric_error = config_manager.get('geometricError')
            # Create the parent tile
            tileset_obj = TreeGenerator.parent_tile_from_children_json(
                child_paths,
                dir=parent_dir,
                filename=parent_filename,
                geometricError=geometric_error,
                tilesetVersion=version,
                boundingVolume=parent_bv
            )
            tileset_objs.append(tileset_obj)

        return tileset_objs

    def bounding_region_for_tile(self, tile, limit_to=None):
        """
        For a morecantile.Tile object, return a BoundingVolumeRegion object
        that represents the bounding region of the tile.

        Parameters
        ----------
        tile : morecantile.Tile
            The tile object.
        limit_to : list of float
            Optional list of west, south, east, north coordinates to limit
            the bounding region to.

        Returns
        -------
        bv : BoundingVolumeRegion
            The bounding region object.
        """
        tms = self.tiles.tms
        bounds = tms.bounds(tile)
        bounds = gpd.GeoSeries(
            box(bounds.left, bounds.bottom, bounds.right, bounds.top),
            crs=tms.crs)
        if limit_to is not None:
            bounds_limitor = gpd.GeoSeries(
                box(limit_to[0], limit_to[1], limit_to[2], limit_to[3]),
                crs=tms.crs)
            bounds = bounds.intersection(bounds_limitor)
        bounds = bounds.to_crs(BoundingVolumeRegion.CESIUM_EPSG)
        bounds = bounds.total_bounds

        region_bv = {
            'west': bounds[0], 'south': bounds[1],
            'east': bounds[2], 'north': bounds[3],
        }
        return region_bv

# define functions to execute 3dtiling

def create_leaf_3dtiles(staged_paths, config, logging_dict=None):
    """
    Create a batch of leaf 3d tiles from staged vector tiles
    """
    #from pdg_workflow import StagedTo3DConverter
    if logging_dict:
        import logging.config
        logging.config.dictConfig(logging_dict)
    converter3d = StagedTo3DConverter(config)
    tilesets = []
    for path in staged_paths:
        try:
            ces_tile, ces_tileset = converter3d.staged_to_3dtile(path)
            tilesets.append(ces_tileset)
        except Exception as e:
            root.error(f'Error creating 3d tile from {path}')
            root.error(e)
    return tilesets


def create_parent_3dtiles(tiles, config, limit_bv_to=None, logging_dict=None):
    """
    Create a batch of cesium 3d tileset parent files that point to child
    tilesets
    """
    #from pdg_workflow import StagedTo3DConverter # do not import this, defined below instead
    if logging_dict:
        import logging.config
        logging.config.dictConfig(logging_dict)
    logging.info(f'Creating parent 3d tiles for {len(tiles)} tiles')
    converter3d = StagedTo3DConverter(config)
    return converter3d.parent_3dtiles_from_children(tiles, limit_bv_to)


def make_batch(items, batch_size):
    """
    Create batches of a given size from a list of items.
    """
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

# define the same config as we did before, but assign to an object this time
workflow_config = {
  "deduplicate_clip_to_footprint": False, 
  "dir_input": "/home/jcohen/iwp_russia_subset_clipToFP_PR/iwp/", 
  "ext_input": ".shp",
  "ext_footprints": ".shp",
  "dir_footprints": "/home/jcohen/iwp_russia_subset_clipToFP_PR/footprints/", 
  "dir_staged": "staged/",
  "dir_geotiff": "geotiff/", 
  "dir_web_tiles": "web_tiles/", 
  "filename_staging_summary": "staging_summary.csv",
  "filename_rasterization_events": "raster_events.csv",
  "filename_rasters_summary": "raster_summary.csv",
  "filename_config": "config",
  "simplify_tolerance": 0.1,
  "tms_id": "WGS1984Quad",
  "z_range": [
    0,
    15
  ],
  "geometricError": 57,
  "z_coord": 0,
  "statistics": [
    {
      "name": "iwp_coverage",
      "weight_by": "area",
      "property": "area_per_pixel_area",
      "aggregation_method": "sum",
      "resampling_method": "average",
      "val_range": [
        0,
        1
      ],
      "palette": [
        "#66339952",
        "#ffcc00"
      ],
      "nodata_val": 0,
      "nodata_color": "#ffffff00"
    },
  ],
  "deduplicate_at": None,
  "deduplicate_keep_rules": [],
  "deduplicate_method": None
}

# define batch sizes for this step
batch_size_3dtiles = 20
batch_size_parent_3dtiles = 500

stager = pdgstaging.TileStager(workflow_config)
tiles3dmaker = StagedTo3DConverter(workflow_config)
tile_manager = stager.tiles
config_manager = stager.config
min_z = config_manager.get_min_z()
max_z = config_manager.get_max_z()
parent_zs = range(max_z - 1, min_z - 1, -1)

# Get paths to all the newly staged tiles
staged_paths = stager.tiles.get_filenames_from_dir('staged')
staged_batches = make_batch(staged_paths, batch_size_3dtiles)

print(f"Number of staged batches is: {len(staged_batches)}\nNumber of files in first staged batch is: {len(staged_batches[0])}")

# create first set of 3dtiles (we create parent 3d tiles below using create_parent_3dtiles())
for batch in staged_batches:
    create_leaf_3dtiles(batch, workflow_config) # no logging dict setup

# Create parent cesium 3d tilesets for all z-levels (except highest)

# For tiles in max-z-level, get the total bounds for all the tiles. We will
# limit parent tileset bounding volumes to this total bounds.
# convert the paths to tiles
max_z_tiles = [tile_manager.tile_from_path(path) for path in staged_paths]
# get the total bounds for all the tiles
max_z_bounds = [tile_manager.get_bounding_box(
    tile) for tile in max_z_tiles]
# get the total bounds for all the tiles
polygons = [box(bounds['left'],
                bounds['bottom'],
                bounds['right'],
                bounds['top']) for bounds in max_z_bounds]
max_z_bounds = gpd.GeoSeries(polygons, crs=tile_manager.tms.crs)

bound_volume_limit = max_z_bounds.total_bounds

# Can't start lower z-level until higher z-level is complete.
for z in parent_zs:

    # Determine which tiles we need to make for the next z-level based on the
    # path names of the files just created
    all_child_paths = tiles3dmaker.tiles.get_filenames_from_dir(
        '3dtiles', z=z + 1)
    parent_tiles = set()
    for child_path in all_child_paths:
        parent_tile = tile_manager.get_parent_tile(child_path)
        parent_tiles.add(parent_tile)
    parent_tiles = list(parent_tiles)

    # Break all parent tiles at level z into batches
    parent_tile_batches = make_batch(
        parent_tiles, batch_size_parent_3dtiles)

    # Make the next level of parent tiles
    for parent_tile_batch in parent_tile_batches:
        create_parent_3dtiles(
            parent_tile_batch,
            workflow_config,
            bound_volume_limit) # no logging dict
        
print("3d-tiling complete! Done.")
