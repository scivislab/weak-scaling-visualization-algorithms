# Evaluating and Improving Weak Scalability Analysis of Visualization Algorithms

This is a short description on how to use the accompanying code to replicate the experiments.
The default values are chosen s.t. it should be able to run on a smaller machine. 
Thus, scaling is done only up to 4 cores, but this can be changed. 
Instructions are written below.
This example was tested on a machine running Ubuntu 22.04 and the execution environment, available via docker container, is built for amd64 platforms.

## Prerequisites

1. You have to be able to execute docker containers - apptainer works too but may require CPU and CPUSET delegation for non-root users.
2. You have to be able to execute bash scripts
3. Disable hyperthreading/SMT

## Running the experiment

1. Execute the following command in this directory `bash scripts/get_data.sh` to download/create the data necessary for the experiments.
2. Run your desired experiments e.g.\
    `bash scripts/all_contour_benchmarks.sh`,\
    `bash scripts/all_contourtree_benchmarks.sh`,\
    `bash scripts/all_volumerender_benchmarks.sh`
3. Run the following command to generate the plots:\
    `bash scripts/all_plots.sh`

The plots and experiment data are in the `output` directory.

### Changing the number of cores

You can change this in the `scripts/all_<algorithm>_benchmark.sh` files. 
There you need to change the threads list.

For extent scaling you need a larger data set if you increase the number of cores.
This data set is generated in `scripts/get_data.sh`.
You can adjust the `MAX_SCALING_FACTOR` parameter to a value equal or larger than the maximum number of cores in your experiments.


## Distributed experiment

The scripts provided here use modules, slurm and require a specific version of openmpi (4.1.6).

1. Execute the following command in this directory `bash scripts/distributed/get_data_distributed.sh` to download/create the data necessary for the experiments.
2. Change the partition that is given in `scripts/distributed/<algorithm>_benchmark_distributed.sh` files to one of your system.
3. Run your desired experiments e.g.\
    `bash scripts/distributed/all_contour_benchmarks_distributed.sh`
4. Run the following command to generate the plots:\
    `bash scripts/distributed/all_plots_distributed.sh`

The plots and experiment data are in the `output_distributed` directory.


### Changing the number of ranks and or cores-per-rank

You can change this in the `scripts/distributed/all_<algorithm>_benchmark_distributed.sh` files.
There you need to change the threads list.

For extent scaling you need a larger data set if you increase the number of cores.
This data set is generated in `scripts/distributed/get_data_distributed.sh`.
You can adjust the `MAX_SCALING_FACTOR` parameter to a value equal or larger than the maximum number of cores in the experiments.

For the distributed experiments you can also change the cores per rank via `CORES_PER_RANK` in `scripts/distributed/<algorithm>_benchmark_distributed.sh`.
