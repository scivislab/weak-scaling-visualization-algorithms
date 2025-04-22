#!/bin/bash

set -e

module load openmpi/4.1.6

CONTAINER="docker://wsods/weak-scaling-vis:review"
COMMAND="mpirun apptainer run -H "${PWD}:/example" ${CONTAINER} "
TASKS=(1 3 6 9 12 15 18)
TASK_STRING=${TASKS[*]}

./scripts/distributed/contour_benchmark_distributed.sh "${CONTAINER}" "${COMMAND}" "${TASK_STRING}" 'resampling' data/ctBones512.vti 'Scalars_' 'flyingedges'
./scripts/distributed/contour_benchmark_distributed.sh "${CONTAINER}" "${COMMAND}" "${TASK_STRING}" 'replication' data/ctBones512_copy.vti 'Scalars_' 'flyingedges'
./scripts/distributed/contour_benchmark_distributed.sh "${CONTAINER}" "${COMMAND}" "${TASK_STRING}" 'extent' data/ctBones512Large.vti 'Scalars_' 'flyingedges'

./scripts/distributed/contour_benchmark_distributed.sh "${CONTAINER}" "${COMMAND}" "${TASK_STRING}" 'resampling' data/aneurism512.vti 'ImageFile' 'flyingedges'
./scripts/distributed/contour_benchmark_distributed.sh "${CONTAINER}" "${COMMAND}" "${TASK_STRING}" 'replication' data/aneurism512_copy.vti 'ImageFile' 'flyingedges'
./scripts/distributed/contour_benchmark_distributed.sh "${CONTAINER}" "${COMMAND}" "${TASK_STRING}" 'extent' data/aneurism512Large.vti 'ImageFile' 'flyingedges'

./scripts/distributed/contour_benchmark_distributed.sh "${CONTAINER}" "${COMMAND}" "${TASK_STRING}" 'resampling' data/perlinNoise512.vti 'PerlinNoise' 'flyingedges'
./scripts/distributed/contour_benchmark_distributed.sh "${CONTAINER}" "${COMMAND}" "${TASK_STRING}" 'replication' data/perlinNoise512_copy.vti 'PerlinNoise' 'flyingedges'
./scripts/distributed/contour_benchmark_distributed.sh "${CONTAINER}" "${COMMAND}" "${TASK_STRING}" 'extent' data/perlinNoise512Large.vti 'PerlinNoise' 'flyingedges'
