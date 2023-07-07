# Running the Ice Wedge Polygon Visualization Workflow on Delta

The ice wedge polygons dataset is very large, so we use `ray` to run the workflow in parallel on the Delta server. Because this is not an NCEAS server, it is important to pay attention to how many Delta credits are being utilized as each allocation's funding is finite. 

## Steps:

- ssh into the Delta server in VScode.

-  Pull updates from the `main` branch for each of the 4 PDG repositories:
    - [`PermafrostDiscoveryGateway/viz-workflow`](https://github.com/PermafrostDiscoveryGateway/viz-workflow/tree/main)
    - [`PermafrostDiscoveryGateway/viz-staging`](https://github.com/PermafrostDiscoveryGateway/viz-staging)
    - [`PermafrostDiscoveryGateway/viz-raster`](https://github.com/PermafrostDiscoveryGateway/viz-raster)
    - [`PermafrostDiscoveryGateway/viz-3dtiles`](https://github.com/PermafrostDiscoveryGateway/viz-3dtiles)

- Create a virtual environment (recommended for the root of the environment to be in `/scratch/{username}`) with `python=3.9` and install __local__ versions of the 3 PDG packages (using `pip install -e {LOCAL PACKAGE}`). Within `setup.py` for `viz-raster`, remember to comment out the GitHub install of `viz-staging` to ensure the local version is installed. Also install the packages:
    - `ray`
    - `glances`
    - `pyfastcopy`
    - Changes integrated with pulls or saved manual changes will __automatically__ be implemented into that virtual environment if the local package was installed with `-e` (stands for "editable") and you are running a script from the terminal.
    - When the `ray` workflow and `parsl` workflows are finalized and designed as `poetry` packages, this manual creation of an environment won't be necessary because the `.toml` file will be present.

- Prepare one of the two `slurm` scripts to claim some worker nodes on which we will launch a job.
    - By default, you are logged into the head node (login01, 02, or 03) which should __not__ be the node that executes the bulk of the computation (you actually cannot be charged for work on this node). 
    - Run `squeue | grep {USERNAME}` (a `slurm` command) to display info about the jobs in the scheduling queue and which nodes each are running on. This list will be empty of you haven't launched any jobs yet. 
        - **Important note:** do not type in your _full_ username, just the first half, because the query will not work if your username is too long. For example, for the username 'julietcohen', run `squeue | grep juliet` to see all jobs.
    - Open the appropriate script that will soon be run to claim the nodes: either `viz-workflow/slurm/BEST-v2_gpu_ray.slurm` if you're using GPU, or `BEST_cpu_ray_double_srun.slurm` for CPU.
    - **Note:** lines at the top of this `slurm` script that start with `#SBATCH` are __not__ regular comments, they are settings. Other lines in the script that start with just `#` are regular comments. 
    - **Change the line `#SBATCH --nodes={NUMBER}`** which represents the number of nodes that will process the IWP data.
        - For the IWP workflow run in May 2023, 20 nodes were used to stage 17,039 input shapefiles. This was to avoid out-of-memory errors, and to process the data within 24 hours (increasing the number of nodes decreases the execution time). The data processing finished with just a few minutes to spare, so make sure you allocate enough nodes. Rsyncing the files took about an hour and the first rsync was initiated when just 80% of the tiles were complete, in order to ensure that at least that many files were stored safely off `/tmp`. Subsequent `rsync` runs were faster as there were fewer files to write or re-write. 
        - In a past run, Robyn rasterized 95% of the staged tiles with 10 nodes.
        - A future to-do is to set up a special `rsync` script that will continuously check for new geotiff files in the `/tmp` folder and sync them to `/scratch` _without needing to manually run an `rsync` script at intervals_.   
    - **Change the line `#SBATCH --time=48:00:00`** which represents the total amount of time a job is allowed to run (and charge credits based on minutes and cores) before it is cancelled. The full 48 hours should be set if doing a full IWP run. If doing a test run, decrease this.
        - To calculate the number of CPU hours that will be charged: multiply the amount of _cores_ in each node (128 CPU cores per node) by the number of nodes and hours. So if you're using 2 nodes for 3 hours and CPU cores, you multiply 128 cores x 3 hours x 2 nodes = ~768 CPU hours will be charged.
        - To calulate the number of GPU hours that will be charged: multiply the number of nodes by the number of minutes by 0.05. 
    - **Change the line `#SBATCH --account={ACCOUNT NAME}`** and enter the account name for the appropriate allocation. Note that our allocations come with GPU and CPU counterparts that are billed separately. Use CPU when ample hours are available. CPU has smaller `/tmp` local SSD (about half as much as GPU `/tmp`) which is a downside. If we need more space on `/tmp` than normal or are running low on compute hours, use GPU. Note that we do __not__ store these private account names on GitHub, so pay attention to this line when you are pushing. 
    - **Find the `# global settings section` and change `conda activate {ENVIRONMENT}` or `source path/to/{ENVIRONMENT}/bin/activate`** by entering your virtual environment for this workflow.
        - This part will be hard-coded once we make this workflow into a package with a pre-configured environment in the `.toml` file.

- Open a new terminal, start a `tmux` session, then activate your virtual environment. (It's important to do this before ssh'ing into a node because we want the `tmux` session to persist regardless of the job's runtime).
    - Using `tmux` is helpful because it runs in a separate terminal in the background, which will continue the job even if the ssh connection to the server is lost. Best practice is to use the `tmux` feature to open multiple terminals at once with different panes so they are all visible in synchrony. Naming the terminals is very helpful.

- **Switch into the slurm dir by running `cd viz-workflow/slurm`**. Then run `sbatch BEST-v2_gpu_ray.slurm` or `sbatch BEST_cpu_ray_double_srun.slurm` to launch the job on the number of nodes you specified within that file.
    - At this point, credits are being charged to the allocation. The terminal will print something like "Submitted batch job #######", a unique ID for that job. This script writes the file `slurm/nodes_array.txt` that identifies the active nodes. This file is used in several other scripts.
    - Other team members' `nodes_array.txt` are saved to their local `viz-worflow/slurm` directory, and this file is not pushed to GitHub (it is listed in `.gitignore`), so there will not be issues with your run.

-  Run `squeue | grep {USERNAME}` to see the new job that has appeared at the top of the list.
    - Check here for clues in parenthesis to troubleshoot an error in starting a job.
        - `(Priority)` means that your job is queued but all of Delta's nodes are being used by others at the moment. Continue checking if your job starts every few minutes by running the `squeue` command.
        - `(Resources)` means you do not have enough credits to complete the job you requested. Cancel it (`scancel {JOB ID}`), change the resources you are requesting, and run the `sbatch` command again.
        - `QOSGrpBillingMinutes` means you tried to charge too many hours to your allcoation, similar to (`Resources`). Cancel it (`scancel {JOB ID}`), change the resources you are requesting, and run the `sbatch` command again.
    - When there is no issue starting the job, there will be a node code such as `gpub059` if you're using GPU, or `cn059` if you're using CPU. You'll need that to ssh into that specific node. If the number of nodes specified in the `slurm` script is greater than 1 (likely the case!), then the code will show a __range__ of numbers for that one job, such as `gpub[059-060]` or `cn[059-060]`. The smallest number in this range is the "head node" for that job, meaning that is the number you will want to ssh into in your `tmux` terminal.
    - The current runtime for each job is also noted in this output, which helps you track how much time you have left to finish your job.

- Check that each node has activated the same environment by running `which python` in a few nodes. It should return the Python subdirectory your environment's folder! The `slurm` job will not run on the nodes that don't have the environment successfully activated.

- Sync the most recent footprints from `/scratch` to all relevant nodes' `/tmp` dirs on Delta: 
    - Since Juliet is running this workflow, this script copies footprints from her `/scratch` dir to the `/tmp` dirs on the nodes.
    - Good practice to first check the size of the footprint source directory, so you know how large the destination directory should be when it's all transferred.
    - Within a `tmux` session, switch into the correct environment, and ssh into the head node (e.g. `ssh gpub059`) and run `python viz-workflow/rsync_footprints_to_nodes.py`.
    
    Running this script is necessary to do before each job because at the end of the last job, the `/tmp` dirs on the active nodes are wiped. We do not just pull directly from the `/scratch` dir for every step because the workflow runs much slower that way (a very low % CPU usage) since the `/scratch` dir is not directly on each node like the `/tmp` dirs are, and because the footprint files are very small and very numerous. Similarly, when we write files we do so to the `/tmp` dir then `rsync` them back to `/scratch` after to save time. One of our to-do's is to automate this step.

- Continue to check the size of the footprints dir within `/tmp` in a separate terminal:
    - To see the footprints that you are syncing to the `/tmp` dir of a node, open a new terminal and ssh into any of the active nodes. Then run `cd /tmp` & don't forget the prefix slash.
    - Run `ds staged_footprints -d0` every few minutes. When the MB stops growing (usually just takes 5-10 min with the whole high ice dataset), you know the sync is complete.
    - Alternatively, you could run `find staged_footprints -type f | wc -l` and check when the number of files stops growing.
    
    Kastan and Robyn suggested that this step could be adjusted to be faster since Delta works faster moving a few large files than it does working with many small files. These files could be consolidated by "tarring" the files together before the transfer, then un-tar the files in the `/tmp` dir.

- Adjust `viz-workflow/PRODUCTION_IWP_CONFIG.py` as needed:
    - Change the variable `head_node` to the head node.
        - This step should eventually be automated to define the head node similarly to how other scripts read the `nodes_array.txt` file. 
    - With the newest batch of data as of January 2023, the `INPUT` path and `FOOTPRINTS_REMOTE` paths have already been updated to Juliet's `/scratch` dir. Moving forward, these will need to be changed only when the IWP data pre-processing is updated and therefore new files have been transferred.
    - The output dirs will __always__ need to be different than the last run since we retain the outputs of past runs and do not overwrite them. So the `OUTPUT` path (which serves as the _start_ of the path for all output files) includes a variable `output_subdir` in this script which should be changed to something unique, such as any subfolders the user wants the data to be written to, with the last subfolder representing the date. Create this folder manually.
        - Note for automation: `subprocess` could be used to automatically name a folder with the date, but since runs will likely go overnight, using `subprocess` would split the output of one run into 2 folders.
        - Note: subfolders in the paths will automatically be created if they do not already exist in `/tmp` when `rsync` is used to transfer the footprints there, and when the `staged`, `geotiff`, and `web_tile` directories are written by their respective steps. Subfolders in `/scratch` will _not_ automatically be created. As a result, it is important to go into your `/scratch` directory and manually create that unique subdirectory you included as the variable `output_subdir`.
    - Within the subdir just created, created a subdirectory called `staged`.

- Adjust `viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py` as needed:
    - Within the `try:` part of the first function `main()`, comment out / uncomment out steps depending on your stage in the workflow:

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
            
    ```
    - In the future, when we run the whole workflow from start to finish, this system of uncommenting steps and running manual steps in between scripts won't be necessary, but this workflow is not yet automated. The way the workflow is structured now:
    - The first step reminds you to manually run the script to `rsync` the footprints (already covered in an above step).
    - In the code chunk above, only uncomment the first step, `step0_staging()`, then save the script. _After_ we run this script and transfer the tiles to `/scratch` and merge them, _then_ we can return to this script and uncomment the next step: `step2_raster_highest()`.
    - Kastan noted that steps 1-4 should run one after another but this has not happened yet due to the workflow not yet being able to execute 3d-tiling (because we do not have a step built into the way workflow to build the 3D tileset hierarchy, which means that we create the b3dm tiles, but not the json we need to view them correctly on the map), errors, and very slow processing in geotiff creation especially. 

-  Within the `tmux` session with your virtual environment activated, ssh into the head node associated with that job by running `ssh gpub059` or `ssh cn059`. Then run the script that we to import the config, define all custom functions necessary for the workflow, and execute the staging step on all nodes: `python viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py`.
    - The script takes a few seconds to start (the terminal looks like it's hanging), then rapidly prints statements throughout the entire process, so when that stops and there is a summary of the staging in the last print statement, you know the step is complete. You can also monitor CPU usage on glances and see that it has returned to a very low % again (like 0.2%).

-  In a separate terminal, while ssh'ed into any of the nodes running the job, and with your virtual environment activated, run `glances` to track memory usage and such as the script runs. This helps troubleshoot things like memory leaks. You can determine if issues are related to the network connection and `iowait`, or the code itself.
    - If using CPU script: CPU usage should be around 80-100% for optimal performance, but it has fluctuated around 40% before, indicating a bottleneck. This could be the result of other users reading and writing to `/scratch, which slows down your netowrk speed but is out of your control.
    - If using GPU script: In May 2023 during staging with 20 nodes and 17,039 input files, memory % increased to ~55% within the fist 16 hours of the run, then stabilized and did not fluctuate the rest of the run.

-  Once staging is complete, run `python viz-workflow/rsync_staging_to_scratch.py`.
    - In order to know when this step is done, check the size of the destination directory in `/scratch` until it stops changing. A to-do is to find a better way to monitor this process with `rsync`.

-  Adjust the file `merge_staged_vector_tiles.py` as needed:
    - Set the variables `staged_dir_path_list` and `merged_dir_path`:
      - Change the last string part of `merged_dir_path` (where merged staged files will live) to the lowest number node of the nodes you're using (the head node).
      - Change the hard-coded nodes specified in `staged_dir_paths_list` to the list of nodes you're using for this job, except **do not include the head node in this list** because it was already assigned to `merged_dir_path`.
    - Within a `tmux` session, with your virtual environment activated, and ssh'd into the head node, run `python viz-workflow/merge_staged_vector_tiles.py` to consolidate all staged files to the node you specified.
    - You know when this is complete by looking for the last print statement: 'Done, exiting...'. Check the size of the staged directories in `/scratch`. The head node's directory size should be much larger than all other nodes' directories, because all the nodes' staged files have been consolidated there.
    - When merging a few TB of data, the merging step slows down after several hours. It may be necessary to execute multiple merging jobs, being careful to never merge the same workser node into the head node in 2 different jobs.

- Once the merge is complete, transfer the `log.log` in each nodes' `/tmp` dir to that respective nodes' subdir within `staging` dir: run `python viz-workflow/rsync_log_to_scratch.py`
    - The logs are transferred to their respective nodes' dir instead of being named after their node, because all logs need to be named the same thing so all logs receive all statements from the PDG packages throughout processing.
    - This only needs to be done immeditely after merging if you are concluding the job before moving onto the raster higher step with a fresh job (which would be the case if there is not enough time left in the current job to execute raster highest before the 48 hours are up).

- Pre-populate your `/scratch` with a `geotiff` dir with the merged staged internal file hierarchy.
    - Replace the variables in {} appropriately.
        1. `cd /scratch/bbou/{user}/{output_subdir}/staged/{head_node}`
        2. `find . -type d > /scratch/bbou/{user}/{output_subdir}/dirs.txt`
        3. `mkdir /scratch/bbou/{user}/{output_subdir}/geotiff`
        4. `cd /scratch/bbou/{user}/{output_subdir}/geotiff`
        5. `xargs mkdir -p < /scratch/bbou/{user}/{output_subdir}/dirs.txt`

-  Return to the file `viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py` and comment out `step0_staging()`, and uncomment out the next step: `step2_raster_highest(batch_size=100)` (skipping 3d-tiling). Run `python viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py` in a `tmux` session with the virtual environment activated and ssh'd into the head node, as usual.
    - You know this step is complete when the destination directory size in `/tmp` stops growing, and the summary of the step is printed.

- Transfer all highest z-level geotiff files from `/tmp` to `/scratch` by running `python viz-workflow/rsync_step2_raster_highest_to_scratch.py`.

-  Return to the file `viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py` and comment out `step2_raster_highest(batch_size=100)`, and uncomment out the next step: `step3_raster_lower(batch_size_geotiffs=100)`. Run `python viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py`.
    - The raster lower files are written directly to `/scratch` so no need to `rsync` them afterwards.

- Check that the file `rasters_summary.csv` was written to `/scratch`. Download this file locally. Usually the top few lines look oddly fomatted. Delete these few lines and re-upload the file to the same directory (overwriting the misformatted one there).
    - This is necessary in order to use it to update ranges in the web tiling step so the color scale in the web tiles to make sense.

- Create a new directory called `web_tiles` in your `/scratch` dir.
    - This is necessary because the web tiling step writes directly to `/scratch` rather than `/tmp` first, and directories cannot be created in `/scratch` while writing files there. But subdirectories will be created as needed within the `web_tiles` dir because `viz-staging` is configured that way.

-  Return to `IN_PROGRESS_VIZ_WORKFLOW.py` and comment out the last step: `step4_webtiles(batch_size_web_tiles=250)`. Run `python viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py`.
    - These tiles are written directly to `/scratch`

- Transfer the `log.log` in each nodes' `/tmp` dir to that respective nodes' subdir within `staging` dir: run `python viz-workflow/rsync_log_to_scratch.py`
    - If you are in the same job as when you started the first staging step, this is will be the only time you transfer the logs. If you already did this in a previous job that just executed the staging step, you will have to pay attention to the directories that these logs are transferred to. Make sure they exist in `/scratch` before you run the script.

- Cancel the job: `scancel {JOB ID}`. The job ID can be found on the left column of the output from `squeue | grep {USERNAME}`. No more credits are being used. Recall that the job will automatically be cancelled after 24 hours even if this command is not run.

- Remember to remove the `{ACCOUNT NAME}` for the allocation in the slurm script before pushing to GitHub.

- Move output data from Delta to the Arctic Data Center as soon as possible via Globus.

# Transfering Output Data for Archival and Visualization

## Steps:

- Use `globus` to transfer all output files from Delta's `/scratch` dir to Datateam. 

- The output files should have their own directory within: `datateam:/home/pdg/data/ice-wedge-polygon-data/`

- Navigate to the Rmd document to update the PDG portal. Run through the code to download the latest version of the portal (paying attention to staging or production, we need to update demo first so we make sure it looks good before putting it on production). Once the .xml file has been written locally, open it and edit the filepath for the IWP data to point to the web_tiles folder just populated with the new data. Save the file. Update the portal using the appropriate function.

- Check that the web tiles look good on demo, and update the production .xml too.

Congratulations! You're done.


