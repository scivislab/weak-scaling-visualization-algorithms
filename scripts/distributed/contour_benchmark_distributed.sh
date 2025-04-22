#!/bin/bash

set -e

PARTITION="skylake-96"
CORES_PER_RANK=8

CONTAINER=${1}
COMMAND=${2}
TASKS=(${3})
SCALING=${4}
DATA=${5}
FIELD=${6}
ALGO=${7}

declare -a jobids

echo "Scaling data..."
for ((i=0; i<${#TASKS[@]}; i++)) ;
do
    t=${TASKS[$i]}
    echo "Start scaling for ${t} cores"

    currenttask=''

    if [ ${ALGO} = 'marchingcubes' ];
    then
        currenttask=$(sbatch -n ${CORES_PER_RANK} -c 1 --parsable -p ${PARTITION} --time=10:0:0 --mem=0 -o logs/csd%4j.out -e logs/csd%4j.err --wrap="${COMMAND} pvbatch src/contour_prepare_scaled_data.py ${t} ${SCALING} ${DATA} ${FIELD} ${ALGO}")
    elif [ ${ALGO} = 'flyingedges' ] || [ ${ALGO} = 'vtkm' ];
    then
        currenttask=$(sbatch -n 1 -c ${CORES_PER_RANK} --parsable -p ${PARTITION} --time=10:0:0 --mem=0 -o logs/csd%4j.out -e logs/csd%4j.err --wrap="${COMMAND} pvbatch src/contour_prepare_scaled_data.py ${t} ${SCALING} ${DATA} ${FIELD} ${ALGO}")
    fi

    echo "Start experiment for ${t} cores"
    if [ ${ALGO} = 'marchingcubes' ];
    then
        ranks=$((${CORES_PER_RANK}*${t}))
        jobids[i]=$(sbatch -n ${ranks} -c 1 --parsable -d aftercorr:${currenttask} -p ${PARTITION} --time=2:0:0 --mem-per-cpu=3500M -o logs/cws%4j.out -e logs/cws%4j.err --wrap="${COMMAND} pvbatch src/contour_benchmark.py ${t} ${SCALING} ${DATA} ${FIELD} ${ALGO}")
    elif [ ${ALGO} = 'flyingedges' ] || [ ${ALGO} = 'vtkm' ];
    then
        jobids[i]=$(sbatch -n ${t} -c ${CORES_PER_RANK} --parsable -d aftercorr:${currenttask} -p ${PARTITION} --time=2:0:0 --mem-per-cpu=3500M -o logs/cws%4j.out -e logs/cws%4j.err --wrap="${COMMAND} pvbatch src/contour_benchmark.py ${t} ${SCALING} ${DATA} ${FIELD} ${ALGO}")
    fi
done

