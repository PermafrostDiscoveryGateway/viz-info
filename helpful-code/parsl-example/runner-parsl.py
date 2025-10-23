from pdgworkflow import WorkflowManager
import json
from pathlib import Path


config_parsl = Path("conf-parsl.json")
with config_parsl.open() as f:
    config_parsl = json.load(f) 

import logging

import parsl
from parsl import python_app
from parsl.config import Config
from parsl.executors import HighThroughputExecutor
from parsl.providers import LocalProvider


def run_stage_raster_parallel(
        wf,
        batch_size=300
):
    """
    Run the main PDG workflow for the following steps:
    1. staging
    2. rasterizing
    3. 3dtiling
    4. WMTS construction

    Parameters
    ----------
    wf : WorkflowManager
        WorkflowManager defined by config file
    batch_size: int
        How many staged files, geotiffs, or web tiles should be included in a single creation
        task? (each task is run in parallel) Default: 300
    """

    if wf.config.is_stager_enabled():
        logging.info("Staging initiated.")

        print(wf.config.get("dir_input"))
        input_paths = wf.tiles.get_filenames_from_dir("input")

        input_batches = make_batch(input_paths, batch_size=1)

        # Stage all the input files (each batch in parallel)
        app_futures = []
        for i, batch in enumerate(input_batches):
            app_future = stage(batch, wf)
            app_futures.append(app_future)

            logging.info(f'Started job for batch {i} of {len(input_batches)}')

            # Don't continue to next step until all files have been staged
        [a.result() for a in app_futures]

        logging.info("Staging complete.")

        # ---------------------------------------------------------------------------------------

    if wf.config.is_raster_enabled():
        logging.info("Rasterizing initiated.")

        logging.info("Collecting staged file paths to process...")
        staged_paths = wf.tiles.get_filenames_from_dir("staged")

        logging.info(f'Found {len(staged_paths)} staged files to process.')
        staged_batches = make_batch(staged_paths, batch_size=150)

        app_futures = []
        for i, batch in enumerate(staged_batches):
            app_future = raster(batch, wf)
            app_futures.append(app_future)

            logging.info(f'Started job for batch {i} of {len(staged_batches)}')

        [a.result() for a in app_futures]

        logging.info("Rasterization complete.")



@python_app
def stage(paths, wf_manager):
    for path in paths:
        wf_manager.stage(path)

@python_app
def raster(paths, wf_manager):
    wf_manager.rasterize_vectors(paths)

def make_batch(items, batch_size):
    """
    Create batches of a given size from a list of items.
    """
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

activate_env = "pyenv activate 3dt_fix"
htex_local = Config(
    executors=[
        HighThroughputExecutor(
            label="htex_local",
            worker_debug=False,
            max_workers_per_node=11,
            provider=LocalProvider(
                init_blocks=1,
                max_blocks=1,
                worker_init=activate_env
            ),
        )
    ],
)
parsl.clear()
parsl.load(htex_local)

workflow_config = config_parsl
wf = WorkflowManager(workflow_config)

run_stage_raster_parallel(wf)

htex_local.executors[0].shutdown()
parsl.clear()
