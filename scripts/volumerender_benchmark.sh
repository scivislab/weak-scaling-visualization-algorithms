#!/bin/bash

set -e

CONTAINER=${1}
COMMAND=${2}
THREADS=(${3})
SCALING=${4}
DATA=${5}
FIELD=${6}

echo "Scaling data..."
for ((i=0; i<${#THREADS[@]}; i++)) ;
do
    t=${THREADS[$i]}
    echo "Start scaling for ${t} cores"
    ${COMMAND} --env VTK_SMP_MAX_THREADS=1 --cpuset-cpus=0 ${CONTAINER} pvpython --force-offscreen-rendering src/volumerender_prepare_scaled_data.py ${t} ${SCALING} ${DATA} ${FIELD} 
done

echo "Executing experiments..."
for ((i=0; i<${#THREADS[@]}; i++)) ;
do
    t=${THREADS[$i]}
    CPUSET=$(seq -s, 0 1 $((${t}-1)))
    echo "Start experiment with ${t} cores"
    ${COMMAND} --cpuset-cpus=${CPUSET} ${CONTAINER} pvbatch --force-offscreen-rendering src/volumerender_benchmark.py ${t} ${SCALING} ${DATA} ${FIELD}
done
