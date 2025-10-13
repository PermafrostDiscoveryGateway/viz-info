# Running viz-workflow with custom TMS

With the [v1.0.0 release](https://github.com/PermafrostDiscoveryGateway/viz-workflow/releases/tag/1.0.0), we introduced support for defining **custom TileMatrixSets (TMS)** beyond those included in [morecantile](https://developmentseed.org/morecantile/).  
This allows generating tiles in projections like **EPSG:3413 (Arctic)** or **EPSG:5041 (Antarctic)** instead of the default Web Mercator grid.


## Overview

PDG Workflow can now load user-defined TMS JSON files created with `morecantile custom`.  
This is useful for **polar projections**, **regional grids**, or any CRS not included in [morecantile's standard TMS list](https://developmentseed.org/morecantile/usage/#list-supported-grids).


### Step 1: Create a Custom TMS JSON
#### Example for EPSG:3413 (UPS Arctic)

```bash
morecantile custom \
  --epsg 3413 \
  --extent -4194304 -4194304 4194304 4194304 \
  --minzoom 0 --maxzoom 15 \
  --tile-width 256 --tile-height 256 \
  > UPSArctic3413Quad.json
```

### Step 2: Register the Custom TMS
PDG Workflow will detect custom TMS files through the environment variable:

```bash
export TILEMATRIXSET_DIRECTORY=/path/to/tms/
```

In your config, set:
```json
"tms_id": "UPSArctic3413Quad"
```
to match the `id` inside the TMS JSON.

### Step 3: Run the Workflow
Run the workflow as normal, see the example in [first run](https://github.com/PermafrostDiscoveryGateway/viz-info/blob/main/11_first-run.md)

