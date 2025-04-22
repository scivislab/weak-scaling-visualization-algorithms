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

COMMAND="${COMMAND} ${CONTAINER} "

${COMMAND} python3 src/plots.py 'output/contour_flyingedges/' 'contour' 'aneurism'
${COMMAND} python3 src/plots.py 'output/contour_flyingedges/' 'contour' 'ctBones'
${COMMAND} python3 src/plots.py 'output/contour_flyingedges/' 'contour' 'perlinNoise'

${COMMAND} python3 src/plots.py 'output/volumerender/' 'volumerender' 'aneurism'
${COMMAND} python3 src/plots.py 'output/volumerender/' 'volumerender' 'ctBones'
${COMMAND} python3 src/plots.py 'output/volumerender/' 'volumerender' 'perlinNoise'

${COMMAND} python3 src/plots.py 'output/contourtree_vtkm/' 'contourtree' 'aneurism128'
${COMMAND} python3 src/plots.py 'output/contourtree_vtkm/' 'contourtree' 'ctBones128'
${COMMAND} python3 src/plots.py 'output/contourtree_vtkm/' 'contourtree' 'perlinNoise128'

${COMMAND} python3 src/plots.py 'output/contour_marchingcubes/' 'contour' 'aneurism'
${COMMAND} python3 src/plots.py 'output/contour_marchingcubes/' 'contour' 'ctBones'
${COMMAND} python3 src/plots.py 'output/contour_marchingcubes/' 'contour' 'perlinNoise'

${COMMAND} python3 src/plots.py 'output/contourtree_ttk/' 'contourtree' 'aneurism128'
${COMMAND} python3 src/plots.py 'output/contourtree_ttk/' 'contourtree' 'ctBones128'
${COMMAND} python3 src/plots.py 'output/contourtree_ttk/' 'contourtree' 'perlinNoise128'