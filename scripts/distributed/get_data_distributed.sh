#!/bin/bash

set -e

CORES_PER_RANK=8
PARTITION="skylake-96"
MAX_SCALING_FACTOR=22

mkdir -p data
cd data
wget "https://raw.githubusercontent.com/topology-tool-kit/ttk-data/dev/ctBones.vti"
 
wget "https://klacansky.com/open-scivis-datasets/aneurism/aneurism.nhdr"
wget "https://klacansky.com/open-scivis-datasets/aneurism/aneurism_256x256x256_uint8.raw"
cd ..

# create data
CONTAINER="docker://wsods/weak-scaling-vis:review"
COMMAND="apptainer run -H ${PWD}:/exp "
${COMMAND} ${CONTAINER} pvpython src/get_data.py

# remove temp data
rm data/aneurism.nhdr
rm data/aneurism_256x256x256_uint8.raw

cp data/ctBones512.vti data/ctBones512_copy.vti
cp data/aneurism512.vti data/aneurism512_copy.vti
cp data/perlinNoise512.vti data/perlinNoise512_copy.vti

cp data/ctBones.vti data/ctBones_copy.vti
cp data/aneurism.vti data/aneurism_copy.vti
cp data/perlinNoise.vti data/perlinNoise_copy.vti

# create larger data for extent scaling, MAX_SCALING_FACTOR determines the largest upsampling so that extent scaling has a larger data set to get subvolumes from 
echo 'creating large data for extent scaling'
sbatch -n 1 -c ${CORES_PER_RANK} -p ${PARTITION} --time=1:0:0 --mem=0 --wrap="${COMMAND} ${CONTAINER} pvpython src/enlarge.py ${MAX_SCALING_FACTOR} 'data/ctBones512.vti' 'Scalars_' 'data/aneurism512.vti' 'ImageFile' 'data/perlinNoise512.vti' 'PerlinNoise'"

sbatch -n 1 -c ${CORES_PER_RANK} -p ${PARTITION} --time=1:0:0 --mem=0 --wrap="${COMMAND} ${CONTAINER} pvpython src/enlarge.py ${MAX_SCALING_FACTOR} 'data/ctBones.vti' 'Scalars_' 'data/aneurism.vti' 'ImageFile' 'data/perlinNoise.vti' 'PerlinNoise'"
