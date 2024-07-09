## `helpful-code`

This directory contains files and documentation to run the Permafrost Discovery Gateway visualization workflow in Python, update the Arctic Data Center portal in R, and deduplicate data outside of the workflow if desired. There is code provided to run a simple version of the workflow, or run the workflow in parallel with `parsl`. Best practice is to start with the simple version of the workflow as a notebook, then move on to running the simple version as a scrript, and finally run the parsl workflow in parallel.

### Contents:

| File | Contents |
| ------ | ---------------------| 
| `requirements.txt` | Installs all dependencies for the workflow into a Python environment. Environment should be built with Python 3.9 or 3.10. Create a new environment with `conda` with the following steps: (1) run `conda create -n vizworkflow python=3.9`, (2) run `conda activate vizworkflow`, and (3) run `pip install -r requirements.txt` in the command line. |
| `simple-workflow/workflow.ipynb` | Code and documentation for executing staging, rasterization, and web-tiling for a small input dataset (3 adjacent ice-wedge polygon files that contain detections from an island in Russia) for all z-levels. Config for the visualization is included in the notebook, along with expected number of output files and time for each step to check your work. |
| `simple-workflow/workflow.py` | Runs the same workflow as the `workflow.ipynb` notebook, but as a script. This is an opportunity to practice running the workflow as a background job within a `tmux` session. |
| `parsl-workflow/parsl-workflow.py` | Runs the workflow in parallel with the `parsl` package. This script uses Ingmar Nitze's lake change dataset as input because this dataset is larger than the sample of ice-wedge polygon data used in the simple workflow, and the lake change data demonstrates a different deduplication approach available in the `pdgstaging` package. |
| `parsl-workflow/config.py` | Visualization workflow config for the `parsl-workflow.py` script. |
| `update-PDG-portal.Rmd` | Contains functions to simplify downloading the most recent version of the Permafrost Discovery Gateway portal from the Arctic Data Center and updating the XML document to add a new layer or make any other changes. |
| `dedup_before_viz/dedup_before_viz_example.py` | See `dedup_before_viz/README.md` |