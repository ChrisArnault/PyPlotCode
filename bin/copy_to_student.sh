#!/usr/bin/env bash

student=${NPAC_ROOT}/student
pyplotcode=${NPAC_ROOT}/PyPlotCode

cp -f ${pyplotcode}/data/fits/NPAC00.fits ${student}/data/common.fits

#for ex in ex1_read_image ex2_background ex3_clusters ex4_coordinates ex5_find_stars
#do
    for txt in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20
    do
        
        cp -f ${pyplotcode}/data/fits/NPAC${txt}.fits ${student}/data/NPAC${txt}/specific.fits

        #cp -f ${pyplotcode}/data/md5/ex1_read_image.NPAC${txt}.md5 ${student}/data/NPAC${txt}/ex1.md5
        #cp -f ${pyplotcode}/data/md5/ex2_background.NPAC${txt}.md5 ${student}/data/NPAC${txt}/ex2.md5
        #cp -f ${pyplotcode}/data/md5/ex3_clusters.NPAC${txt}.md5 ${student}/data/NPAC${txt}/ex3.md5
        #cp -f ${pyplotcode}/data/md5/ex4_coordinates.NPAC${txt}.md5 ${student}/data/NPAC${txt}/ex4.md5
        #cp -f ${pyplotcode}/data/md5/ex5_find_stars.NPAC${txt}.md5 ${student}/data/NPAC${txt}/ex5.md5

    done
#done

#cp -f ${pyplotcode}/bin/md5check.py ${student}/src

