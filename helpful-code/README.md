## `helpful-code`

This directory contains notebooks, python scripts, and documentation for the following goals:

- explore new datasets submitted for visualization on the Permafrost Discovery Gateway
- execute cleaning and necessary preprocessing steps
- run the Permafrost Discovery Gateway visualization workflow
- finally update the Arctic Data Center portal in R so the data is available to the public!

### Where to start?

1. Once you have read through the documentation files labeled 01-08 in the repository homepage, then you're ready to start reviewing some code and running the workflow yourself on the Datateam server. Start by creating a python environment. Any python environment manager works with the PDG python pacakges, but use `conda` for consistency in the code. The evironment should be built with Python 3.9 or 3.10. Create a new `conda` environment called `vizworkflow` with the following steps: (1) run `conda create -n vizworkflow python=3.9`, (2) run `conda activate vizworkflow`, and (3) run `pip install -r requirements.txt` in the command line.

2. Run through the simple version of the workflow as a notebook with your new environment. See `simple-workflow/workflow.ipynb`

3. Start a new `tmux` session and run the simple version of the workflow as a script. See `simple-workflow/workflow.py`

4. In a `tmux` session, run the workflow in parallel. See `parsl-workflow/parsl-workflow.py`

5. Check out the subdirectory `preprocessing` to get a better understanding of common checks, plots, and cleaning for new PDG datasets. That directory has its own README as well.

6. Choose a new dataset to process from the [Data Layers project board](https://github.com/orgs/PermafrostDiscoveryGateway/projects/18/views/2).

7. Once you produce your first data layer for the demo PDG, download the `update-PDG-portal.Rmd` and upload it using your Arctic Data Center credentials!


### Contents:

| File | Contents |
| ------ | ---------------------| 
| `requirements.txt` | Includes all dependencies for the workflow that should be installed into a new Python environment. To use this script, see instructions in step 1 above, under the section "Where to start?" |
| `simple-workflow/workflow.ipynb` | Code and documentation for executing staging, rasterization, and web-tiling for a small input dataset (three adjacent ice-wedge polygon files that contain detections from an island in Russia) for all z-levels. Config for the visualization is included in the notebook, along with expected number of output files to check your work. |
| `simple-workflow/workflow.py` | Runs the same workflow as the `workflow.ipynb` notebook, but as a script. This is an opportunity to practice running the workflow as a background job within a `tmux` session. |
| `parsl-workflow/parsl-workflow.py` | Runs the workflow in parallel with the `parsl` package. This script uses Ingmar Nitze's lake change dataset as input because this dataset is larger than the sample of ice-wedge polygon data used in the simple workflow, and the lake change data demonstrates a different deduplication approach available in the `pdgstaging` package. |
| `parsl-workflow/config.py` | Visualization workflow config for the `parsl-workflow.py` script. |
| `preprocessing` | A subdirectory that contains code for data quality checks, plots, and cleaning for PDG datasets. These quality checks and cleaning operations will eventually be integrated into the Python packages as automated steps. See this directory's `README` for more details. |
| `update-PDG-portal.Rmd` | A R markdown document that contains functions to simplify downloading the most recent version of the Permafrost Discovery Gateway portal from the Arctic Data Center and updating the XML document to add a new layer or make other front-end portal changes. |

## Current Development

The most recent progress to optimize and containerize in the visualization workflow has been though development of the kubernetes, docker, and parsl workflow in a branch called [enhancement-1-k8s](https://github.com/PermafrostDiscoveryGateway/viz-workflow/tree/enhancement-1-k8s/docker-parsl-workflow) of the `viz-workflow` repository. This workflow is currently under development but can already be deployed on the Google Kubernetes Engine platform to successfully run the workflow and write output files. By improving the workflow to be more portable and containerized, we increase our reproducibility and can take advantage of our own hardware infrastructure at UCSB and the Arctic Data Center. We already heavily rely on our own software by writing and maintaining our own python packages, so we are on our way to total independence.

### How do we deploy the workflow with kubernetes?

There are distinct differences between how we deploy the kubernetes, docker, and parsl workflow through:

(1) our own Arctic Data Center **kubernetes cluster**, or

(2) **Google Kubernetes Engine**

For example, the Dockerfile and other setup files, like the `yaml` files, are different because deploying this workflow on the Arctic Data Center kubernetes cluster requires us to create a _new user account_ within the container, with specific permissions, and creating a _python environment_ within the container as well. On the other hand, deploying the kubernetes, docker, and parsl workflow on the Google Kubernetes Engine lacks these steps and therefore has a simpler Dockerfile. However, this workflow includes several `yaml` files for mounting the persistent volume and service account.

## Future Steps

Our end-goal is for all Permafrost Discovery Gateway datasets to be automatically run through this kubernetes workflow using the UCSB/Arctic Data Center cluster, and subseqeuntly archived at the Arctic Data Center. When new satellite imagery is released, our exisitng feature detection workflows will run and output a new dataset to be visualized. This will hopefully occur several times a month, resulting in several long-term time series datasets. These will include the ice-wedge polygons, lake size change, lake drainage, retrogressive thaw slumps, and more! 