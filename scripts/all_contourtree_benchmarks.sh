#!/bin/bash

set -e

CONTAINER=wsods/weak-scaling-vis:review

case $1 in 
    'docker')
        if ! command -v docker 2>&1 >/dev/null;
        then 
            echo "Apptainer is not installed"
            exit 1
        fi
        COMMAND="docker run --rm -v .:/exp -w /exp"
        ;;
    'apptainer')
        if ! command -v apptainer 2>&1 >/dev/null;
        then 
            echo "Apptainer is not installed"
            exit 1
        fi
        CONTAINER="docker://${CONTAINER}"
        COMMAND="apptainer run -H "${PWD}:/exp" "
        ;;
    *)
        echo "No argument supplied, trying docker then apptainer"
        if command -v docker 2>&1 >/dev/null; 
        then
            echo "docker found, using docker"
            COMMAND="docker run --rm -v .:/exp -w /exp"
        elif command -v apptainer 2>&1 >/dev/null; 
        then
            echo "apptainer found, using apptainer"
            COMMAND="apptainer run -H "${PWD}:/exp" "
            CONTAINER="docker://${CONTAINER}"
        else
            echo "Docker or Apptainer are required for running the benchmarks"
            exit 1
        fi
        ;;
esac

# THREADS=(1 4 8 12 16 20 24 28)
THREADS=(1 2 3 4)
THREAD_STRING=${THREADS[*]}

./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'resampling' 'data/ctBones128.vti' 'Scalars_' 'vtkm'
./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'replication' data/ctBones128_copy.vti 'Scalars_' 'vtkm'
./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'extent' data/ctBones128Large.vti 'Scalars_' 'vtkm'

./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'resampling' data/aneurism128.vti 'ImageFile' 'vtkm'
./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'replication' data/aneurism128_copy.vti 'ImageFile' 'vtkm'
./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'extent' data/aneurism128Large.vti 'ImageFile' 'vtkm'

./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'resampling' data/perlinNoise128.vti 'PerlinNoise' 'vtkm'
./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'replication' data/perlinNoise128_copy.vti 'PerlinNoise' 'vtkm'
./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'extent' data/perlinNoise128Large.vti 'PerlinNoise' 'vtkm'

./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'resampling' 'data/ctBones128.vti' 'Scalars_' 'ttk'
./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'replication' data/ctBones128_copy.vti 'Scalars_' 'ttk'
./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'extent' data/ctBones128Large.vti 'Scalars_' 'ttk'

./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'resampling' data/aneurism128.vti 'ImageFile' 'ttk'
./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'replication' data/aneurism128_copy.vti 'ImageFile' 'ttk'
./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'extent' data/aneurism128Large.vti 'ImageFile' 'ttk'

./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'resampling' data/perlinNoise128.vti 'PerlinNoise' 'ttk'
./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'replication' data/perlinNoise128_copy.vti 'PerlinNoise' 'ttk'
./scripts/contourtree_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'extent' data/perlinNoise128Large.vti 'PerlinNoise' 'ttk'

${COMMAND} ${CONTAINER} rm -rf ./data/*_scaled*