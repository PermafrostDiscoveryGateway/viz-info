from pdgworkflow import WorkflowManager 

config = {
    "dir_input": " put your dir path here/input",
    "ext_input": ".gpkg",
    "z_range": (0, 2),            # keep it small for a faster test run
    "overwrite": True,   
  
# Optional: disable features if you want a smoke test
  
    # "enable_3dtiles": False,
    # "enable_raster_parents": False,
    # "enable_web_tiles_parents": False,
    # "generate_wmtsCapabilities": False,
  
}

workflow = WorkflowManager(config)
workflow.run_workflow()

print("Finished the first run.")
