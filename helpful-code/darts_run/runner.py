from pdgworkflow import WorkflowManager

import config as config

wf_config = config.config

wManager = WorkflowManager(wf_config)

wManager.run_workflow()

