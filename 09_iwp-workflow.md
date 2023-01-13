# Running the IWP workflow on Delta

The ice wedge polygons dataset is very large, so we use `ray` to run the workflow in parallel on the Delta server. Because this is not an NCEAS server, it is important to pay attention to how many Delta credits are being utilized as each allocation's funding is finite. 

## Steps:

1. ssh into the Delta server in VScode.

2.  Pull updates from `PermafrostDiscoveryGateway/viz-workflow` repository [here](https://github.com/PermafrostDiscoveryGateway/viz-workflow/tree/main) to your home directory and switch into the `ray_workflow` branch.

3. Pull updates from the 3 PDG packages ([`viz-staging`](https://github.com/PermafrostDiscoveryGateway/viz-staging), [`viz-raster`](https://github.com/PermafrostDiscoveryGateway/viz-raster/tree/main), [`viz-3dtiles`](https://github.com/PermafrostDiscoveryGateway/viz-3dtiles)) and ensure you're in the main branch of each.

4. Create a virtual environment (recommended to use `venv` as package manager instead of `conda`) with `python=3.9` and install __local__ versions of the 3 PDG packages (using `pip install -e {LOCAL PACKAGE}`), `ray` with pip, and `glances`.
    - Changes integrated with pulls or saved manual changes will __automatically__ be implemented into that virtual environment if the local package was installed with `-e` (stands for "editable") and you are running a script from the terminal.
    - When the `ray` workflow and `parsl` workflows are finalized and designed as `poetry` packages, this manual creation of an environment won't be necessary because the `.toml` file will be present. 

5. Sync the most recent footprints and IWP data files from the `scratch` to `/tmp` dir on Delta: 
    - Open the file `viz-workflow/utilities/rsync_footprints_to_nodes.py` and check the filepaths in the `rsync` command are correct. Since Juliet is taking over this workflow, this will include syncing footprints from her scratch dir to the `/tmp` dirs on the nodes. 
    - In a new terminal, switch into the correct updated environment and run `python viz-workflow/utilities/rsync_footprints_to_nodes.py`.
    
    Overall, running this script is necessary to do before each job because at the end of the last job, the `/tmp` dirs on the active nodes are wiped. We do not just pull directly from the `/scratch` dir because the workflow runs much slower that way (a very low % CPU usage) since the `/scratch` dir is not directly on each node like the `/tmp` dirs are. Similarly, when we write files we do so to the `/tmp` dir then `rsync` them back to scratch after to save time. This step is manually done, but one of our to-do's is to automate this step.

6. Continue to check the size of the `/tmp` dir in a separate terminal:
    - From the `/tmp` dir, you can run `ds staged_footprints -d0`. When the MB stops growing (usually just takes 5-10 min), you know the sync is complete.
    - Alternatively, you could run `find staged_footprints -type f | wc -l` and check when the number of files stops growing.
    
    Kastan and Robyn suggested that this step be automated, which would also include either doing this file transfer in parallel, then consolidating the synced files to the same dir, or "tarring" the files together before the transfer, transfer that consolidated file, then un-tar the files in the `/tmp` dir.

7. Adjust `viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py` as needed:
    - Change any hard-coded filepaths so they represent your username rather than Kastan's, and the desired subfolder you want for these files. Remember it is good practice to have the highest folder in the structure represent the date of the workflow run. I think a good approach is just to `cmd + f` "kastan" to locate the relevant paths (those that aren't commented out). Subfolders in the path will automatically be created if they do not already exist. These filepaths may have already been taken care of with improvements to this file that avoid hard-coding usernames and filepaths and rather using `subprocess` to pull that info in to apply to whatever user is running the workflow.
    - Within the `try:` part of the first function def (`main()`), there are a few lines that need to be commented/uncommented out depending on your stage in the workflow:

    ```python
        try:
            ########## MAIN STEPS ##########
            print("Starting main...")
            
            # (optionally) Comment out steps you don't need 😁
            # todo: sync footprints to nodes.
            step0_staging()                                     # Good staging. Simple & reliable. 
            # todo: merge_staging()
            # step1_3d_tiles()
            
            # mem_testing = False        
            # if mem_testing:
            #     from pympler import tracker
            #     tr = tracker.SummaryTracker()
            #     tr.print_diff()
            #     step2_raster_highest(batch_size=100)                # rasterize highest Z level only 
            #     tr.print_diff()
            
            # args = 
            # step2_raster_highest(batch_size=100, cmd_line_args = args)                # rasterize highest Z level only 
            # step3_raster_lower(batch_size_geotiffs=100)         # rasterize all LOWER Z levels
            # step4_webtiles(batch_size_web_tiles=250)            # convert to web tiles.
    ```
    In the future, when we run the whole workflow from start to finish, this system of uncommenting each step one by one won't be necessary, but this workflow cannot be run that way yet becuase it is not yet automated. This system of uncommenting out one step at a time was designed to run manual steps in between scripts and help pick up the workflow if there was an error, which there usually is. The way the workflow is structured now:
    - The first step reminds you to manually run the script to `rsync` the footprints (already covered in above step).
    - In the code chunk above, only uncomment the first step, `step0_staging()`, then save the script. We will return to it _after_ we run the slurm script to launch workers and ran this script for staging.

As noted by Kastan and Robyn, this script could be improved by integrating the logging system Robyn utilizes in the PDG packages. These should be integrated __inside__ the `@ray.remote` functions. Another to-do! 

8. Claim some worker nodes on which we will launch a job in a later step. By default, you are logged into the head node (login 1, 2, or 3) which should __not__ be the node that executes the bulk of the computation (you actually cannot be charged money for this node). In the same terminal as before, run `squeue | grep {USERNAME}` (a slurm command) to display info about the jobs in the scheduling queue and which node(s) each are running on. This list will be empty of you haven't launched any jobs yet. Then take a look at the script that will soon be run for the IWP data, within the dir `viz-workflow/slurm/BEST-v2_gpu_ray.slurm`. In order to open this from the terminal, run `cat BEST-v2_gpu_ray.slurm`. (If the most up-to-date script changes from this one moving forward, open that script instead. This needs to be renamed for clairty.) Note: lines at the top of this slurm script that start with `#SBATCH` are __not__ regular comments, they are settings. Other lines in the script that start with just `#` are regular comments. 
    - Look at the line `#SBATCH --nodes={NUMBER}` which represetns the number of nodes that will process the IWP data. Increase this if desired, 5 is a good number. 
    - Look at the line `#SBATCH --time=24:00:00` which represents the total amount of time a job is allowed to run (and charge credits based on minutes and cores) before it is halted. Decrease this if desired.
    - Look at the line `#SBATCH --account={ACCOUNT NAME}` and enter the account name for the appropriate allocation. Note that our allocations come with gpu and cpu counterparts that are billed separately. We do __not__ store these private account names on GitHub, so pay attention to this line when you are pushing.
    - Find the `# global settings section` with the line `conda activate {ENVIRONMENT}`, and enter the name of your virtual environment for this workflow. This part can be hard-coded once we make this workflow into a package with a pre-configured environment in the `.toml` file. 

9. Navigate to the file `viz-workflow/PRODUCTION_IWP_CONFIG.py` and change filepaths as needed:
    - With the new batch of data, this will need to be updated to Juliet's scratch dir. After this, the input path will rarely need to be changed (only if the IWP data pre-processing is updated and therefore new files have been transferred elsewhere on Delta).
    - The output path will __always__ need to be changed, as we retain the putputs of past runs and do not overwrite them. Change the path following `/scratch/{ALLOCATION}/`. There is an opportunity for automation here: use an f-string for the dir name, with a variable that is the date pulled from the command line, or something similar, so it is always different than the last run.

10. Open a new terminal, start a `tmux` session, then activate your virtual environment. Switch into `viz-workflow/slurm` dir.
    - Using `tmux` is helpful because it runs in a separate terminal in the background, which will continue the job even if the ssh connection to the server is lost. Best practice is to use the `tmux` feature to open multiple terminals at once with different panes so they are all visible in synchrony. 

11. In that `tmux` terminal, run `sbatch BEST-v2_gpu_ray.slurm` to launch the job on the number of nodes you specified within that file. At this point, credits are being charged to the allocation. The terminal will print something along the lines of "Submitted batch job #######", a unique ID for that job.
    - Optional: check jobs that are in progress by opening `nodes_array.txt`, but note that output files from other team members' jobs should be saved to their own home directory, so there should not be issues with your run. This file is not pushed to GitHub, it is written by the `slurm` script and only applies to the current run. 

12. Run the script that we edited earlier to import the config, define all custom functions necessary for the workflow, and execute the steps: `python viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py`. This will only run the staging step, on all nodes, since the staging step was the only one we uncommented in that script.

13. Run `squeue | grep {USERNAME}` again to see the new job that has appeared at the top of the list.
    - This job may be momentarily noted that it is a `(Priority)` or something else within parenthesis that specifies why it has not been started. For example, it may show `(Resources)` which means the allocation's resources are already being utilized by other jobs. Check here for clues to troubleshoot an error in starting a job.
    - When there is no issue starting the job (there is nothing noted in parenthesis), there will be a node code composed of letters and numbers that you will need to ssh into that specific node. If the number of nodes specified in the `slurm` script is greater than 1, then the code will show a __range__ of numbers for that one job: `{node prefix}[node#-node#]`. The smallest number in this range is the "head node" for that job, meaning that is the number you will want to ssh into.
    - The current runtime for each job is also noted in this output, which helps you track how much time you have left to finish your job.

14. Still within the `viz-workflow/slurm` dir, ssh into the node associated with that job by running `ssh {code}`. Recall that you are already in a `tmux` session, which you switched into before running the `sbatch` command to start the workflow script.
    - **To ask Robyn/Kastan: I am not sure I fully understand how to ssh into a node, would like to see quick example**

15. In a separate terminal, within your virtual environment, run `glances` to track memory usage and such as the script runs. This helps troubleshoot things like memory leaks. You can determine if issues are related to the network connection and `iowait`, or the code itself.
    - CPU usage should be at 100% for optimal performance, but it has fluctuated around 40% before, indicating a bottleneck. This could be the result of other users heavily utilziing the cluster you're working on, which slows down your processing but is out of your control.
    - **To ask Robyn/Kastan: do you need to add an additional step before running `glances` in order to only view the memory usage and such for this job?**

16. Open the file [merge_staged_vector_tiles.py](https://github.com/PermafrostDiscoveryGateway/viz-workflow/blob/8e68894b522faa619a4a7cb2dc2e10affc652c44/utilities/merge_staged_vector_tiles.py), then:
    - There are instructions at the top of this script that the following bullet points walk through ([`Usage Instructions in main()`](https://github.com/PermafrostDiscoveryGateway/viz-workflow/blob/8e68894b522faa619a4a7cb2dc2e10affc652c44/utilities/merge_staged_vector_tiles.py#L79)) to set the variables `RAY_ADDRESS`, `staged_dir_path_list`, and `merged_dir_path`.
    - **Question for Robyn/Kastan: Do I set the `RAY_ADDRESS` variable as the instructions say or is that documentation outdated, and this step was already automated with [this line](https://github.com/PermafrostDiscoveryGateway/viz-workflow/blob/0db036329c2046593983e5cd8450c9eb5c212b41/utilities/merge_staged_vector_tiles.py#L52)?**
    - Change hard-coded filepath for `BASE_DIR` (should be Juliet's `/scratch` dir, and the subdir for staged files) for all staged files) 
    - Change the string part of `merged_dir_path` (where merged staged files will live) to the lowest number node of the nodes you're using. 
    - Remove this node from the `staged_dir_paths_list`
    - Run this script to consolidate all staged files to the node you specified with the function `merge_all_staged_dirs()` (defined in the script itself [here](https://github.com/PermafrostDiscoveryGateway/viz-workflow/blob/8e68894b522faa619a4a7cb2dc2e10affc652c44/utilities/merge_staged_vector_tiles.py#L132)).
    - **To ask Robyn/Kastan: For the filepaths in this scripts, does it matter if they have a trailing `/`? Some do, some don't.**
    - **To ask Robyn/Kastan: What is best practice to know when this consolidation is complete?**

17. Return to the file `viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py` and comment out `step0_staging()` (because we just did that and merged the staged output), and uncomment out the next step: `step1_3d_tiles()`. Run `viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py`

18. Transfer all files from `/tmp` to scratch using `rsync`.
    - **To do: insert example rsync command, need to think about this because the /tmp files are all on different nodes, just like the staged ones were.**

19. Repeat for the rest of the steps in the workflow, and manually transfer the files from `/tmp` to `/scratch` in between each step. Pay attention to the 24 hours limit!
    - For raster files, utilize the script `/utilities/rsync_merge_raster_to_scratch.py`

**To do: run commans to `rsync` files from /tmp to /scratch as they are processed (like at regular time intervals) so none are lost at 24 hrs**

20. To purposefully cancel a job, run `scancel {JOB ID}`. The job ID can be found on the left column of the output from `squeue | grep {USERNAME}`. This closes all terminals related to that job. No more credits are being used. This should be executed after all files are generated and moved off the node (from `/tmp` to the user's dir). Recall that the job will automatically be cancelled after 24 hours even if this command is not run.

21. Remember to remove the `{ACCOUNT NAME}` for the allocation in the slurm script before pushing to GitHub.




