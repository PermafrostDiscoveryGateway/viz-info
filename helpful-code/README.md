## `helpful-code`

This directory contains files and documentation to run a simple version of the Permafrost Discovery Gateway visualization workflow in Python, update the Arctic Data Center portal in R, and deduplicate data outside of the workflow if desired.

### Contents:

| File | Contents |
| ------ | ---------------------| 
| `workflow.ipynb` | Code and documentation for executing staging, rasterization, and web-tiling for a small input dataset (3 adjacent ice-wedge polygon files that contain detections from an island in Russia) for all z-levels. Config for the visualization is included in the notebook, along with expected number of output files and time for each step to check your work. |
| `workflow.py` | Runs the same workflow as the `workflow.ipynb` notebook, but as a script. |
| `requirements.txt` | Installs all dependencies for the workflow into a Python environment. Environment should be built with Python 3.9 or 3.10. If errors arise, default to 3.9. Create a new environment with `conda` or `venv` and run `pip install -r requirements.txt` in the command line. |
| `update-PDG-portal.Rmd` | Contains functions to simplify finding and downloading the most recent version of the Arctic Data Center portal and updating the XML document to add a new layer or make any other changes. Note that it uses the deprecated `arcticdatautils` R package and should probably be updated to use `datapack` (See [datateam docs](https://nceas.github.io/datateam-training/reference/customizing-data-portals.html#updating-portals)) |
| `dedup_before_viz/dedup_before_viz_example.py` | See `dedup_before_viz/README.md` |