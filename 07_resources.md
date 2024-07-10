# Links & resources

## Permafrost Discovery Gateway
- [PDG GitHub](https://github.com/PermafrostDiscoveryGateway)
- [PDG Google Drive](https://drive.google.com/drive/folders/0AHkz0WHYVzIUUk9PVA)

## National Center for Supercomputing Applications
- To register for access to Delta server via the PDG, navigate [here](https://identity.ncsa.illinois.edu/register/QNHI9LLRM2)
  - See section 09 in this repo for details about how to run jobs on this server
  - Only register for an account if you plan to process datasets on the Delta server. We do not use Delta for daily work like working through bug fixes, we use Datateam instead.
  - The available credits and resources are set to expire in January 2025.

## National Center for Ecological Analysis and Synthesis / DataONE
- The NCEAS datateam [reference guide](https://nceas.github.io/datateam-training/reference/) and [training materials](https://nceas.github.io/datateam-training/training/) - Great resource!
- [First Login on NCEAS server](https://help.nceas.ucsb.edu/NCEAS/Computing/first_login_to_nceas_analytical_server)
- [NCEAS High Performance Computing basic information](https://help.nceas.ucsb.edu/NCEAS/Computing/high_performance_computing)
- [EML](https://eml.ecoinformatics.org/)
- [Documentation on the DataONE Kubernetes cluster](https://github.com/DataONEorg/k8s-cluster/)

## UCSB High Performance Computing
- [Center for Scientific Computing](https://csc.cnsi.ucsb.edu/)
  - Registering for an account is very simple and fast, and the points of contact there are very quick to respond to questions via email. They also provide occasional presentations and post slides with documentation about how to run jobs. Overall, the documentation is unfortunately pretty sparse.
  - There are two available places to run SLURM jobs using either CPU or GPU:
    - [Braid 2](https://csc.cnsi.ucsb.edu/clusters/braid2) (has more restricted use, meaning shorter queue)
    - [Pod](https://csc.cnsi.ucsb.edu/clusters/pod)

## Google Kubernetes Engine and Google Cloud Platform
- The Google Fellowship that began in 2023 came with credits to use both of these resources for ~3 years.
- See the [pdg-tech](https://github.com/PermafrostDiscoveryGateway/pdg-tech/tree/master/gcloud) repository for information regarding running ray workflows with Google Cloud.
- See [here](https://github.com/PermafrostDiscoveryGateway/viz-workflow/pull/40) for the code to run the Docker Parsl Workflow on the Google Kubernetes Engine (in review)
