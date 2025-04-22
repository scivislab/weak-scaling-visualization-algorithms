#!/bin/bash

set -e

CONTAINER=wsods/weak-scaling-vis:review
MAX_SCALING_FACTOR=6

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

mkdir -p data
cd data
wget "https://raw.githubusercontent.com/topology-tool-kit/ttk-data/dev/ctBones.vti"

wget "https://klacansky.com/open-scivis-datasets/aneurism/aneurism.nhdr"
wget "https://klacansky.com/open-scivis-datasets/aneurism/aneurism_256x256x256_uint8.raw"
cd ..

# create data
${COMMAND} ${CONTAINER} pvpython src/get_data.py

# remove temp data
rm data/aneurism.nhdr
rm data/aneurism_256x256x256_uint8.raw

cp data/ctBones.vti data/ctBones_copy.vti
cp data/aneurism.vti data/aneurism_copy.vti
cp data/perlinNoise.vti data/perlinNoise_copy.vti

cp data/ctBones128.vti data/ctBones128_copy.vti
cp data/aneurism128.vti data/aneurism128_copy.vti
cp data/perlinNoise128.vti data/perlinNoise128_copy.vti

# create larger data for extent scaling, MAX_SCALING_FACTOR determines the largest upsampling so that extent scaling has a larger data set to get subvolumes from
echo 'creating large data for extent scaling'
${COMMAND} ${CONTAINER} pvpython src/enlarge.py ${MAX_SCALING_FACTOR} 'data/ctBones.vti' 'Scalars_' 'data/aneurism.vti' 'ImageFile' 'data/perlinNoise.vti' 'PerlinNoise'
${COMMAND} ${CONTAINER} pvpython src/enlarge.py ${MAX_SCALING_FACTOR} 'data/ctBones128.vti' 'Scalars_' 'data/aneurism128.vti' 'ImageFile' 'data/perlinNoise128.vti' 'PerlinNoise'