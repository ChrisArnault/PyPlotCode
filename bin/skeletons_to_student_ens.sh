#!/usr/bin/env bash

student=${NPAC_ROOT}/StudentEns
pyplotcode=${NPAC_ROOT}/PyPlotCode

cp -f ${pyplotcode}/src/skeletons/ex*.py ${student}/src
cp -f ${pyplotcode}/src/skeletons/lib*.py ${student}/src
cp -f ${pyplotcode}/src/skeletons/pj*.py ${student}/src


