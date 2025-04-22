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


./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'resampling' data/ctBones.vti 'Scalars_' 'flyingedges'
./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'replication' data/ctBones.vti 'Scalars_' 'flyingedges'
./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'extent' data/ctBonesLarge.vti 'Scalars_' 'flyingedges'

./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'resampling' data/aneurism.vti 'ImageFile' 'flyingedges'
./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'replication' data/aneurism.vti 'ImageFile' 'flyingedges'
./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'extent' data/aneurismLarge.vti 'ImageFile' 'flyingedges'

./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'resampling' data/perlinNoise.vti 'PerlinNoise' 'flyingedges'
./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'replication' data/perlinNoise.vti 'PerlinNoise' 'flyingedges'
./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'extent' data/perlinNoiseLarge.vti 'PerlinNoise' 'flyingedges'

./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'resampling' data/ctBones.vti 'Scalars_' 'marchingcubes'
./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'replication' data/ctBones.vti 'Scalars_' 'marchingcubes'
./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'extent' data/ctBonesLarge.vti 'Scalars_' 'marchingcubes'

./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'resampling' data/aneurism.vti 'ImageFile' 'marchingcubes'
./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'replication' data/aneurism.vti 'ImageFile' 'marchingcubes'
./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'extent' data/aneurismLarge.vti 'ImageFile' 'marchingcubes'

./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'resampling' data/perlinNoise.vti 'PerlinNoise' 'marchingcubes'
./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'replication' data/perlinNoise.vti 'PerlinNoise' 'marchingcubes'
./scripts/contour_benchmark.sh "${CONTAINER}" "${COMMAND}" "${THREAD_STRING}" 'extent' data/perlinNoiseLarge.vti 'PerlinNoise' 'marchingcubes'

${COMMAND} ${CONTAINER} rm -rf ./data/*_scaled*