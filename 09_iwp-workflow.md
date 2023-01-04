# Running the IWP workflow on Delta

The ice wedge polygons dataset is very large, so we use `ray` to run the workflow in parallel on the Delta server. Because this is not an NCEAS server, it is important to pay attention to how many Delta credits are being utilized as each allocation's funding is finite. 

## Steps:

1. ssh into the Delta server
2. Clone (for first time) or pull (if not first time) from `PermafrostDiscoveryGateway/viz-workflow` repositiory [here](https://github.com/PermafrostDiscoveryGateway/viz-workflow/tree/main) to your home directory and swtich into the `ray-workflow` branch.
3. Clone (for first time) or pull (if not first time) the 3 PDG packages ([`viz-staging`](https://github.com/PermafrostDiscoveryGateway/viz-staging), [`viz-raster`](https://github.com/PermafrostDiscoveryGateway/viz-raster/tree/main), [`viz-3dtiles`](https://github.com/PermafrostDiscoveryGateway/viz-3dtiles)) and switch into the develop branch of each.
4. Create a virtual environment with `python=3.9` and install __local__ versions of the 3 PDG packages (using `pip install -e {LOCAL PACKAGE}`), `ray` with pip, and `glances` with conda forge instead of pip. This way, changes integrated with pulls or saved manual changes will __automatically__ be implemented into that virtual environment if the local package was installed with `-e` (stands for "editable") and you are running a script from the terminal. If you are running a jupyter notebook, you will need to restart the kernel too to integrate the changes. A to-do improvement is to create a requirements file for all these installations, or hard-code a file path to a pre-made conda environment in the `scratch` dir on Delta that can be activated by any user running `/scratch/{ALLOCATION ID}/{SUBFOLDER}/{ENVIRONMENT}` in a terminal.
5. Make sure the most recent footprints and IWP data files have been synced from the `scratch` to `/tmp` dir on Delta. In a new terminal, run `python viz-workflow/utilities/rsync_footprints_to_nodes.py`. You do __not__ want to change the filepath for the source directory for the `rsync` command in this script, because the footprints are stored in Kastan's directory. However, if a new set of footprints are created from the pre-processing team, they might transfer them elsewhere on Delta, in which case the source directory __will__ need to be changed. Overall, running this script is necessary to do before each job because at the end of the last job, the `/tmp` dirs on the active nodes are wiped. We do not just pull directly from the `scratch` dir because the workflow runs much slower that way (a very low % CPU usage) since the `scratch` dir is not directly on the node like the `/tmp` dir is. Similarly, when we write files we do so to the `/tmp` dir then `rsync` them back to scratch after to save time. This step is manually done, but one of our to-do's is to automate this step.
6. After running that script, continue to check the size of the `/tmp` dir in a separate terminal. From the `/tmp` dir, you can run `ds staged_footprints -d0`. When the MB stops growing (usually just takes 5-10 min), you know the sync is complete. Alternatively, you could run `find staged_footprints -type f | wc -l` and check when the number of files stops growing. Kastan and Robyn suggested that this step be automated, which would inlcude either doing this file transfer in parallel, then consolidating the synced files to the same dir, or "tarring" the files together before the transfer, transfer that consolidated file, then un-tar the files in the `/tmp` dir. 
7. Adjust `viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py` as needed:
    - Change any hard-coded filepaths so they represent your username rather than Kastan's. I think a good approach is just to cmd + f "kastan" to locate the relevant paths. Kastan ensured that subfolders in the path will automatically be created if they do not already exist. These filepaths may have already been taken care of with Kastan's recent improvements to this file, such as his inclusion of a variable for one's username rather than a hard-coded username, but just give the script a quick glance to make sure. 
    - Within the `try:` part of the first function def (`main()`), there are a few lines that need to be commented/uncommented out depedning on your stage in the workflow:
    ```python
        try:
            ########## MAIN STEPS ##########
            print("Starting main...")
            
            # (optionally) Comment out steps you don't need 😁
            # todo: sync footprints to nodes.
            # step0_staging()                                     # Good staging. Simple & reliable. 
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
            step2_raster_highest(batch_size=100, cmd_line_args = args)                # rasterize highest Z level only 
            # step3_raster_lower(batch_size_geotiffs=100)         # rasterize all LOWER Z levels
            # step4_webtiles(batch_size_web_tiles=250)            # convert to web tiles.
    ```
    The first comment reminds you to `rsync` the footprints. All lines including and following `step0_staging()` should be uncommented if you are just starting the workflow, and intend to run it start to finish, which is likely the case. This system of commenting out certain steps was designed to help pick up the workflow halfway if there was an error. Perhaps Robyn or Kastan have a preference to only uncomment the first step, `step0_staging()`, then do a manual check to make sure all went well and merge the staged tiles, __then__ move onto the next steps with those steps now commented out.
As noted by Kastan and Robyn, this script could be improved by integrating the logging system Robyn utilizes in the PDG packages. These should be integrated __inside__ the `@ray.remote` functions. Another to-do! 
8. Optional: check jobs that are already in progress by opening `nodes_array.txt`, but note that output files from other team members' jobs should be saved to their own home directory, so there should not be issues with your run.
9. Claim some worker nodes to eventually launch a job. By default, you are logged into the head node (login 1, 2, or 3) which should __not__ be the node that executes the bulk of the computation (you actually cannot be charged money for this node). In the same terminal, run `squeue | grep {USERNAME}` (a slurm command) to display info about the jobs in the scheduling queue and which node(s) each are running on. This list will be empty of you haven't launched any jobs yet. Then take a look at the script that will soon be run for the IWP data, within the dir `viz-workflow/slurm/BEST-v2_gpu_ray.slurm`. In order to open this from the terminal, run `cat BEST-v2_gpu_ray.slurm`. (If the most up-to-date script changes from this one moving forward, open that script instead.) The lines at the top of this slurm script that start with `#SBATCH` are __not__ regular comments, they are settings. Other lines in the script that start with just `#` are regular comments. 
    - Look at the line `#SBATCH --nodes={NUMBER}` which represetns the number of nodes that will process the IWP data. Increase this if desired, 5 is a good number. 
    - Look at the line `#SBATCH --time=24:00:00` which represents the total amount of time a job is allowed to run (and charge credits based on minutes and cores) before it is halted. Decrease this if desired.
    - Look at the line `#SBATCH --account={ACCOUNT NAME}` and enter the account name for the appropriate allocation. Note that our allocations come with gpu and cpu counterparts that are billed separately. We do __not__ store these private account names on GitHub, so pay attention to this line when you are pushing.
    - Find the `# global settings section` with the line `conda activate {ENVIRONMENT}`, and enter the name of your virtual environment for this workflow. This is an opportinuty for automation if we specify a path to a pre-made environment that lives in scratch that any user can activate using the full filepath. 
10. Navigate to the file `viz-workflow/PRODUCTION_IWP_CONFIG.py` and change filepaths as needed.
    - The input path will rarely need to be changed (only if the IWP data pre-processing is updated and therefore new files have been transferred elsewhere on Delta).
    - The output path will __always__ need to be changed, as we retain the putputs of past runs and do not overwrite them. Change the path following `/scratch/{ALLOCATION}/`.
    - Kastan already has implemented some improvements to filepath structures in this file, that need to be pushed to GitHub perhaps?
11. Open a new terminal, start a `tmux` session, then activate your virtual environment. Switch into `viz-workflow/slurm` dir.
    - Using `tmux` is helpful because it runs in a separate terminal in the background, which will continue the job even if the ssh connection to the server is lost. Best practice is to use the `tmux` feature to open multiple terminals at once with different panes so they are all visible in synchrony. 
12. In that `tmux` terminal, run `sbatch BEST-v2_gpu_ray.slurm` to launch the job on the number of nodes you specified within that file. At this point, credits are being charged to the allocation. The terminal will print something along the lines of "Submitted batch job #######", a unique ID for that job.
13. Run this script to import the config, define all custom functions necessary for the workflow, and execute the steps: `python viz-workflow/IN_PROGRESS_VIZ_WORKFLOW.py` (Robyn or Kastan can correct this step if it is in the wrong order or needs to be adjusted)
    - could this be automated by adding the command to run the script to the end of the slurm script? Maybe not because a slurm script is different than a py script? Alternatively, could we remove the manual step of running the `sbatch` command by adding it into the start of the `IN_PROGRESS_VIZ_WORKFLOW.py` script?
14. Run `squeue | grep {USERNAME}` again to see the new job that has appeared at the top of the list. This job may be momentarily noted that it is a `(Priority)` or something else within parenthesis that specifies why it has not been started. For example, it may show `(Resources)` which means the allocation's resources are already being utilized by other jobs. Check here for clues to troubleshoot an error in starting a job. When there is no issue starting the job (there is nothing noted in parenthesis), there will be a node code composed of letters and numbers that you will need to ssh into that specific node. If the number of nodes specified in the `.slurm` script is greater than 1, then the code will show a __range__ of numbers for that one job: `{node prefix}[node#-node#]`. The smallest number in this range is the "head node" for that job, meaning that is the number you will want to ssh into.
    - The current runtime for each job is also noted in this output, which helps you track how much time you have left to finish your job.
15. Still within the `viz-workflow/slurm` dir, ssh into the node associated with that job by running `ssh {code}`. Recall that you are already in a `tmux` session, which you switched into before running the `sbatch` command to start the workflow script.
16. In a separate terminal, run `glances` to track memory usage and such as the script runs. This helps troubleshoot things like memory leaks. You can determine if issues are related to the network connection and `iowait`, or the code itself.
    - CPU usage should be at 100% for optimal performance, but it has fluctuated around 40% before, indicating a bottleneck. This could be the result of other users heavily utilziing the cluster you're working on, which slows down your processing but is out of your control.
17. After the script is done, merge the files processed on different nodes with the function `merge_staging()`, which consolidates all files to the first (lowest #) node.
18. To purposefully cancel a job, run `scancel {JOB ID}`. The job ID can be found on the left column of the output from `squeue | grep {USERNAME}`. This closes all terminals related to that job. No more credits are being used.




