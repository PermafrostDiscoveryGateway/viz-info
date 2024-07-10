## `helpful-code`

This directory contains notebooks, python scripts, and documentation to run the Permafrost Discovery Gateway visualization workflow, update the Arctic Data Center portal in R, guidance for exploring new datasets, and execute preprocessing for datasets. 

### Where to start?

1. Once you have read through the documentation files labeled 01-08 in the repository homepage, then you're ready to start reviewing some code and running the workflow yourself on the Datateam server. Start by creating a python environment. Any python environment manager works with the PDG python pacakges, but use `conda` for consistency in the code. This is helpful to run the  code in parallel later on. The evironment should be built with Python 3.9 or 3.10. Create a new `conda` environment called `vizworkflow` with the following steps: (1) run `conda create -n vizworkflow python=3.9`, (2) run `conda activate vizworkflow`, and (3) run `pip install -r requirements.txt` in the command line.

2. Run through the simple version of the workflow as a notebook with your new environment: `simple-workflow/workflow.ipynb`

3. Start a new `tmux` session and run the simple version of the workflow as a script: `simple-workflow/workflow.py`

4. In a `tmux` session, run the workflow in parallel: `parsl-workflow/parsl-workflow.py`

5. Check out the subdirectory `preprocessing` to get a better understanding of common checks, plots, and cleaning for new PDG datasets.

6. Once you produce your first data layer for the demo PDG, download the `update-PDG-portal.Rmd` and upload it using your Arctic Data Center credentials!


### Contents:

| File | Contents |
| ------ | ---------------------| 
| `requirements.txt` | Installs all dependencies for the workflow into a Python environment. To use this script, see instructions in step 1 above, under the section "Where to start?" |
| `simple-workflow/workflow.ipynb` | Code and documentation for executing staging, rasterization, and web-tiling for a small input dataset (3 adjacent ice-wedge polygon files that contain detections from an island in Russia) for all z-levels. Config for the visualization is included in the notebook, along with expected number of output files and time for each step to check your work. |
| `simple-workflow/workflow.py` | Runs the same workflow as the `workflow.ipynb` notebook, but as a script. This is an opportunity to practice running the workflow as a background job within a `tmux` session. |
| `parsl-workflow/parsl-workflow.py` | Runs the workflow in parallel with the `parsl` package. This script uses Ingmar Nitze's lake change dataset as input because this dataset is larger than the sample of ice-wedge polygon data used in the simple workflow, and the lake change data demonstrates a different deduplication approach available in the `pdgstaging` package. |
| `parsl-workflow/config.py` | Visualization workflow config for the `parsl-workflow.py` script. |
| `preprocessing` | Common checks, plots, and cleaning for PDG datasets that will eventually be integrated into the python packages as automated steps. See this directory's README for more details: `preprocessing/README.md` |
| `update-PDG-portal.Rmd` | Contains functions to simplify downloading the most recent version of the Permafrost Discovery Gateway portal from the Arctic Data Center and updating the XML document to add a new layer or make any other changes. |

## Current Developments and Future Steps

The most recent progress to optimize and containerize in the visualization workflow has been though development of the kubernetes, docker, and parsl workflow in a branch called [enhancement-1-k8s](https://github.com/PermafrostDiscoveryGateway/viz-workflow/tree/enhancement-1-k8s/docker-parsl-workflow) of the `viz-workflow` repository. This workflow is currently under development but can already be deployed on the Google Kubernetes Engine platform to successfully run the workflow and write output files. By improving the workflow to be more portable and containerized, we increase our reproducibility and can take advantage of our own hardware infrastructure at UCSB and the Arctic Data Center. We already heavily rely on our own software by writing and maintaining our own python packages, so we are on our way to total independence.

There are distinct differences between deploying the kubernetes, docker, and parsl workflow through:

(1) our own Arctic Data Center **kubernetes cluster**, or

(2) **Google Kubernetes Engine**

For example, the Dockerfile and other setup files are separate because deploying this workflow on the Arctic Data Center kubernetes cluster requires us to create a _new user account_ within the container, with specific permissions, and creating a _python environment_ within the container as well. Deploying the kubernetes, docker, and parsl workflow on the Google Kubernetes Engine lacks these steps and therefore has a simpler Dockerfile, but this workflow includes several `yaml` files for the persistent volume and service account that can be confusing to wrap one's head around.