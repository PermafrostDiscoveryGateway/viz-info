# Running the IWP workflow on Delta

The ice wedge polygons dataset is very large, so we use `ray` to run the workflow in parallel on the Delta server. Because this is not an NCEAS server, it is important to pay attention to how many Delta credits are being utilized as each allocation's funding is finite. 

## Steps:

- ssh into the Delta server in VScode.

-  Pull updates from [`PermafrostDiscoveryGateway/viz-workflow`](https://github.com/PermafrostDiscoveryGateway/viz-workflow/tree/main) to your local repo and switch into the `ray_workflow_juliet` branch.

- Pull updates from the 3 PDG packages ([`viz-staging`](https://github.com/PermafrostDiscoveryGateway/viz-staging), [`viz-raster`](https://github.com/PermafrostDiscoveryGateway/viz-raster/tree/main), [`viz-3dtiles`](https://github.com/PermafrostDiscoveryGateway/viz-3dtiles)) and ensure you're in the main branch of each.

- Create a virtual environment (recommended for root of env to be in `/scratch/username`) with `python=3.9` and install __local__ versions of the 3 PDG packages (using `pip install -e {LOCAL PACKAGE}`). Within `setup.py` for `viz-raster`, remember to comment out the GitHub install of `viz-staging` to ensure the local version is installed. Also install the packages:
    - `ray`
    - `glances`
    - `pyfastcopy`
    - Changes integrated with pulls or saved manual changes will __automatically__ be implemented into that virtual environment if the local package was installed with `-e` (stands for "editable") and you are running a script from the terminal.
    - When the `ray` workflow and `parsl` workflows are finalized and designed as `poetry` packages, this manual creation of an environment won't be necessary because the `.toml` file will be present.

- Prepare the `slurm` script to claim some worker nodes on which we will launch a job. By default, you are logged into the head node (login01, 02, or 03) which should __not__ be the node that executes the bulk of the computation (you actually cannot be charged money for this node). Run `squeue | grep {USERNAME}` (a `slurm` command) to display info about the jobs in the scheduling queue and which nodes each are running on. This list will be empty of you haven't launched any jobs yet. Then take a look at the script that will soon be run to claim the nodes: `viz-workflow/slurm/BEST-v2_gpu_ray.slurm`. (Rename this soon for clarity. Note from Robyn: We may also want to switch to the `cpu` version since we are not making use of the GPUs?) Note: lines at the top of this `slurm` script that start with `#SBATCH` are __not__ regular comments, they are settings. Other lines in the script that start with just `#` are regular comments. 
    - Look at the line `#SBATCH --nodes={NUMBER}` which represents the number of nodes that will process the IWP data. Increase this if desired, 5 is a good number with sufficient CPU usage, but for the idnividual job for geotiff creation, Robyn used 10 because CPU usage was inefficient. 
    We are not sure how much increasing the nodes decreases the time, she only got through 95% of the staged files. Because of this node efficiency uncertainty, it is important to set up a special `rsync` script _before running the geotiff creation step_  that will continuously check for new geotiff files in the `/tmp` folder and sync them to `/scratch` _without needing to manually run an `rsync` script at intervals_. 
    - **To ask Kastan: any tips for increasing CPU usage?**
        - It's a hard problem. It usually means there's a networking bottleneck from `/scratch`, i.e. pulling data (including footprints) from `/scratch`. The "easiest" workaround is to copy data to each node's /tmp directory. But there's not that much space on /tmp (750G on CPU nodes, and 1.5T on GPU nodes) so it can pretty easily fill up.  
    - Look at the line `#SBATCH --time=24:00:00` which represents the total amount of time a job is allowed to run (and charge credits based on minutes and cores) before it is halted. Decrease this if desired. This number of hours is multiplied by each node and the sum of all those values is the total number of CPU or GPU hours that is charged to your allocation. Do not use a full 24 hours if not needed, such as for an IWP test run on a small data sample.
    - Look at the line `#SBATCH --account={ACCOUNT NAME}` and enter the account name for the appropriate allocation. Note that our allocations come with GPU and CPU counterparts that are billed separately. Use CPU when ample hours are available. CPU has smaller `/tmp` local SSD (about half as much as GPU `/tmp`) which is a downside. If we need more space on `/tmp` than normal or are running low on compute hours, use GPU. Note that we do __not__ store these private account names on GitHub, so pay attention to this line when you are pushing. 
    - Find the `# global settings section` with the line `conda activate {ENVIRONMENT}`, and enter the name of your virtual environment for this workflow. Also change the whole command if you are using a different package manager of course. This part will be hard-coded once we make this workflow into a package with a pre-configured environment in the `.toml` file.

- Open a new terminal, start a `tmux` session, then activate your virtual environment. (It's important to do this before ssh'ing into a node because we want the `tmux` session to persist regardless of the job's runtime). Run `cd viz-workflow/slurm` then `sbatch BEST-v2_gpu_ray.slurm` to launch the job on the number of nodes you specified within that file. At this point, credits are being charged to the allocation. The terminal will print something along the lines of "Submitted batch job #######", a unique ID for that job. This script writes the file `nodes_array.txt` that identifies the active nodes used in later scripts.
    - Other team members' `nodes_array.txt` are saved to their local directory, and this file is not pushed to GitHub (it is listed in `.gitignore`), so there will not be issues with your run.
    - Using `tmux` is helpful because it runs in a separate terminal in the background, which will continue the job even if the ssh connection to the server is lost. Best practice is to use the `tmux` feature to open multiple terminals at once with different panes so they are all visible in synchrony.

-  Run `squeue | grep {USERNAME}` to see the new job that has appeared at the top of the list.
    - This job may be momentarily noted that it is a `(Priority)` or something else within parenthesis that specifies why it has not been started. For example, it may show `(Resources)` which means the allocation's resources are already being utilized by other jobs. Check here for clues to troubleshoot an error in starting a job.
    - When there is no issue starting the job (there is nothing noted in parenthesis), there will be a node code such as `gpub059` that you will need to ssh into that specific node. If the number of nodes specified in the `slurm` script is greater than 1, then the code will show a __range__ of numbers for that one job, such as `gpub[059-060]`. The smallest number in this range is the "head node" for that job, meaning that is the number you will want to ssh into.
    - The current runtime for each job is also noted in this output, which helps you track how much time you have left to finish your job.

- Sync the most recent footprints from `/scratch` to all relevant nodes' `/tmp` dirs on Delta: 
    - Open the file `viz-workflow/utilities/rsync_footprints_to_nodes.py` and check the filepaths in the `rsync` command are correct. Since Juliet is running this workflow, sync footprints from her `/scratch` dir to the `/tmp` dirs on the nodes.
    - Within a `tmux` session, switch into the correct environment and run `python viz-workflow/utilities/rsync_footprints_to_nodes.py`.
    
    Overall, running this script is necessary to do before each job because at the end of the last job, the `/tmp` dirs on the active nodes are wiped. We do not just pull directly from the `/scratch` dir because the workflow runs much slower that way (a very low % CPU usage) since the `/scratch` dir is not directly on each node like the `/tmp` dirs are, and because the footprint files are very small and very numerous. Similarly, when we write files we do so to the `/tmp` dir then `rsync` them back to `/scratch` after to save time. One of our to-do's is to automate this step.

- Continue to check the size of the `/tmp` dir in a separate terminal:
    - To see the footprints that you are syncing to the tmp dir of a node, first you will need to ssh into that node (e.g. `ssh gpub059`) and go to the tmp dir (e.g. `cd /tmp/`)
    - From the `/tmp` dir, you can run `ds staged_footprints -d0`. When the MB stops growing (usually just takes 5-10 min), you know the sync is complete.
    - Alternatively, you could run `find staged_footprints -type f | wc -l` and check when the number of files stops growing.
    
    Kastan and Robyn suggested that this step could be adjusted to be faster since Delta works faster moving a few large files than it does working with many small files. These files could be consolidated by "tarring" the files together before the transfer, then un-tar the files in the `/tmp` dir.

- Adjust `viz-workflow/PRODUCTION_IWP_CONFIG.py` as needed:
    - With the newest batch of data as of January, the `BASE_DIR_OF_INPUT` path and `FOOTPRINTS_PATH` have been updated to Juliet's `/scratch` dir. Moving forward, these will need to be changed only when the IWP data pre-processing is updated and therefore new files have been transferred.
    - The output dirs will __always__ need to be different than the last run since we retain the outputs of past runs and do not overwrite them. So the `OUTPUT` path (which serves as the _start_ of the path for all output files) includes a variable `output_subdir` which should be changed to something unique like the date. `subprocess` could be used to automatically name the folder with the date, but since runs will likely go overnight, using `subprocess` would split the output of one run into 2 folders. 
    - Subfolders in the paths will automatically be created if they do not already exist.

- Adjust `viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py` as needed:
    - Within the `try:` part of the first function `main()`, commented out / uncomment out steps depending on your stage in the workflow:

    ```python
        try:
            ########## MAIN STEPS ##########
            print("Starting main...")
            
            # (optionally) Comment out steps you don't need 😁
            # todo: sync footprints to nodes.
            step0_staging()        
            # todo: merge_staging()
            # DO NOT RUN step1 UNTIL WORKFLOW CAN ACCOMODATE 3DTILING: step1_3d_tiles() # default parameter batch_size = 300
            # step2_raster_highest() # rasterize highest Z level only, default batch_size = 100, default cmd_line_args = None 
            # todo: immediately after initiating above step, start rsync script to continuously sync geotiff files
            # step3_raster_lower(batch_size_geotiffs=100) # rasterize all LOWER Z levels
            # step4_webtiles(batch_size_web_tiles=250) # convert to web tiles.
            
            # mem_testing = False        
            # if mem_testing:
            #     from pympler import tracker
            #     tr = tracker.SummaryTracker()
            #     tr.print_diff()
            #     step2_raster_highest(batch_size=100)                # rasterize highest Z level only 
            #     tr.print_diff()
    ```
    In the future, when we run the whole workflow from start to finish, this system of uncommenting steps and running manual steps in between scripts won't be necessary, but this workflow is not yet automated. The way the workflow is structured now:
    - The first step reminds you to manually run the script to `rsync` the footprints (already covered in an above step).
    - In the code chunk above, only uncomment the first step, `step0_staging()`, then save the script. _After_ we run this script and transfer those to `/scratch` and merge them, then update the IWP config to change the staging path from `/tmp/` to `/scratch/`, _then_ we can return to this script and uncomment the next step: `step2_raster_highest()`. Kastan noted that steps 1-4 should run one after another but this has not happened yet due to the workflow not yet being able to execute 3d-tiling (because we do not have a step built into the way workflow to build the 3D tileset hierarchy, which means that we create the b3dm tiles, but not the json we need to view them correctly on the map), errors, and very slow processing in geotiff creation especially.
    - As noted by Kastan and Robyn, this script could be improved by integrating the logging system Robyn utilizes in the PDG packages. These should be integrated __inside__ the `@ray.remote` functions. Another to-do! 

-  Within the `viz-workflow/slurm` dir and a `tmux` session, ssh into the head node associated with that job by running `ssh gpub059`. The head node is the one with the smallest number.

-  Run the script that we edited earlier to import the config, define all custom functions necessary for the workflow, and execute the staging step on all nodes: `python viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py`.
    - The script prints statements throughout the entire process, so when that stops and the last statement is '😁 step 1 success', you know the staging step is complete. You can also monitor CPU usage on glances and see that it has returned to a very low % again.

-  In a separate terminal, while ssh'ed into the node you want to monitor (any of the nodes running the job), and with your python virtual environment activated, run `glances` to track memory usage and such as the script runs. This helps troubleshoot things like memory leaks. You can determine if issues are related to the network connection and `iowait`, or the code itself.
    - CPU usage should be around 80-100% for optimal performance, but it has fluctuated around 40% before, indicating a bottleneck. This could be the result of other users heavily utilizing the cluster you're working on, which slows down your processing but is out of your control if that is the reason.
      - Note from Robyn: Is this true? I thought we have the slurm script set up to reserve entire nodes to ourselves? But maybe other users can impact the network speed, i.e. reading and writing files.
      - Note from Kastan: Robyn is exactly correct. I think the network speed (reading from /scratch) flucuates a lot. 

-  Once staging is complete, open `viz-workflow/utilities/rsync_staging_to_scratch.py` and change the variable `output_subdir` so it matches that variable in `PRODUCTION_IWP_CONFIG.py`. Run `python viz-workflow/utilities/rsync_staging_to_scratch.py`.
    - In order to know when this step is done, check the size of the destination directory until it stops changing. A to-do is to find a better way to monitor this process with `rsync`.

-  Adjust the file `merge_staged_vector_tiles.py` as needed:
    - Change hard-coded filepath for `BASE_DIR` (should be changed to Juliet's `/scratch` dir, and the subdir that houses all subdirs for staged files on different nodes)
    - There are instructions within `main()` to set the variables `staged_dir_path_list` and `merged_dir_path`:
      - Change the hard-coded nodes specified in `staged_dir_paths_list` to the list of nodes you're using for this job.
      - Change the string part of `merged_dir_path` (where merged staged files will live) to the lowest number node of the nodes you're using. 
      - Remove this node from the `staged_dir_paths_list`
    - Run this script to consolidate all staged files to the node you specified. This script first defines the function `merge_all_staged_dirs()`, then executes it.
    - You know when this is complete by looking for the last print statement: 'Done, exiting...'

-  Return to the file `viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py` and comment out `step0_staging()`, and uncomment out the next step: `step2_raster_highest(batch_size=100)` (skipping 3d-tiling). Then open the config and change the staging path from `/tmp` to the `/scratch` dir where all the staged files were moved to and merged.

- Run `python viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py`.
    - You know this step is complete when the destination directory size stops growing, and the final print statement is generated: 'Done rasterize all only highest z level'

- Transfer all geotiff files from `/tmp` to `/scratch` with `rsync_merge_raster_to_scratch.py`, but before running this script, open it to update the variable `output_dir` to the correct string.
    - **To ask Kastan: Rasterization is also executed on multiple nodes, but we do not merge the outputs of each node within the script `rsync_merge_raster_to_scratch.py`, so is it correct we do not need to consolidate these files? Is there a reason 'merge' is in the name of the script?**  
        - This script _does_ "merge" the rasterization outputs, in the sense that it moves all of them to the same output directory, following the Z-level Tile Hierarchy format. So the idividual files do not need to be merged, but all of them need to exist in the same tile hierarchy on disk, on /scratch.

-  Return to the file `viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py` and comment out `step2_raster_highest(batch_size=100, cmd_line_args = args)`, and uncomment out the next step: `step3_raster_lower(batch_size_geotiffs=100)`. Run `python viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py`. Once complete, change hard-coded paths in `utilities/rsync_merge_raster_to_scratch.py`, and run it.

-  Return to the file and comment out the last step: `step4_webtiles(batch_size_web_tiles=250)`
    - These files are written directly to `/scratch` so no need to transfer from `/tmp`.
    - Pay attention to how long this step takes. If it is slow, switch to writing the files to `/tmp` before transferring to scratch, like staging and rasterization.

-  To purposefully cancel a job, run `scancel {JOB ID}`. The job ID can be found on the left column of the output from `squeue | grep {USERNAME}`. This closes all terminals related to that job, so no more credits are being used. This should be executed after all files are generated and moved off the node (from `/tmp` to the user's dir). Recall that the job will automatically be cancelled after 24 hours even if this command is not run.

- Remember to remove the `{ACCOUNT NAME}` for the allocation in the slurm script before pushing to GitHub. Move data off Delta before March or work with Delta team to ensure data won't be wiped.


