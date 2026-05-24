# Using pdgworkflow/WMTSCapabilitiesGenerator.py

This document explains how to generate a `WMTSCapabilities.xml` file for a viz-workflow dataset using the [`WMTSCapabilitiesGenerator`](https://github.com/PermafrostDiscoveryGateway/viz-workflow/blob/main/pdgworkflow/WMTSCapabilitiesGenerator.py) helper class.

The `WMTSCapabilities.xml` file describes the available tile layers, supported formats, TileMatrixSet, zoom levels, bounding box, and REST tile URL templates. It is used by tools such as QGIS and other WMTS clients to load all available products from a dataset without manually constructing URLs. Example for [Ice Wedge Polydon](https://arcticdata.io/data/tiles/10.18739/A2KW57K57/WMTSCapabilities.xml)

When loaded to QGIS, you will see the option to load available layers.

<img width="473" height="357" alt="WMTSCapabailitiesin QGIS" src="https://github.com/user-attachments/assets/f481c1c5-1f30-4c5e-b091-55563cec6237" />

## Where this fits in `viz-workflow`

The WMTS capabilities generation step runs at the end of the workflow, after the all of the data outputs have already been created.

Usual workflow order:

1. Stage input data.
2. Rasterize data, if enabled.
3. Generate web tiles, if enabled.
4. Generate 3D tiles, if enabled.
5. Generate `WMTSCapabilities.xml`, if enabled.

In `WorkflowManager`, this  means calling `generate_wmts_capabilities()` at the end of `run_workflow()`.

```python
def run_workflow(self) -> None:
    if self.config.is_stager_enabled():
        logger.info("Staging enabled, starting tile staging...")
        self.run_staging()

    if self.config.is_raster_enabled():
        logger.info("Rasterization enabled, starting rasterization process...")
        self.run_rasterization()

    if self.config.is_3dtiles_enabled():
        logger.info("3D tiles enabled, starting 3D tile generation...")
        self.run_3d_tiling()

    if self.config.is_generate_wmtsCapabilities_enabled():
        logger.info("Generating WMTSCapabilities.xml")
        self.generate_wmts_capabilities()
```

### Constructor parameters

| Parameter | Meaning |
|---|---|
| `title` | Human-readable dataset title shown in the WMTSCapabilities.xml service metadata. |
| `base_url` | Base publication URL used to build the capabilities URL and tile URL templates. |
| `doi` | Dataset DOI or dataset path segment used in generated URLs. |
| `tile_matrix_set_id` | ID of the TileMatrixSet to use. Must be available from `morecantile.tms.get(...)`. |
| `max_z_level` | Highest zoom level to include in the capabilities document. Must be within the TMS Zoom range. |
| `bounding_box` | Optional dataset bounding box with `left`, `bottom`, `right`, and `top`. If None, the full TMS bounds are used. |

Example:

```python
from pdgworkflow.WMTSCapabilitiesGenerator import WMTSCapabilitiesGenerator

generator = WMTSCapabilitiesGenerator(
    title="Ice-Wedge Polygons",
    base_url="https://arcticdata.io/data/",
    doi="10.18739/A2KW57K57",
    tile_matrix_set_id="WGS1984Quad",
    max_z_level=15,
    bounding_box={
        "left": -179.0,
        "bottom": -87.0,
        "right": 176.0,
        "top": 90.0,
    },
)
```

---
