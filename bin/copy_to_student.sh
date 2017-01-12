#!/usr/bin/env bash

student=../../../../student

cp -f data/student/NPAC.fits ${student}/data/common.fits

#for ex in ex1_read_image ex2_background ex3_clusters ex4_coordinates ex5_find_stars
#do
    for txt in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20
    do
        #cp -f data/student/NPAC${txt}.fits ${student}/data/NPAC${txt}/specific.fits
        #cp -f data/student/${ex}.NPAC${txt}.md5 ${student}/data/NPAC${txt}/${ex}.md5

        cp -f data/student/NPAC${txt}.fits ${student}/data/NPAC${txt}/specific.fits

        cp -f data/student/ex1_read_image.NPAC${txt}.md5 ${student}/data/NPAC${txt}/ex1.md5
        cp -f data/student/ex2_background.NPAC${txt}.md5 ${student}/data/NPAC${txt}/ex2.md5
        cp -f data/student/ex3_clusters.NPAC${txt}.md5 ${student}/data/NPAC${txt}/ex3.md5
        cp -f data/student/ex4_coordinates.NPAC${txt}.md5 ${student}/data/NPAC${txt}/ex4.md5
        cp -f data/student/ex5_find_stars.NPAC${txt}.md5 ${student}/data/NPAC${txt}/ex5.md5

    done
#done

cp -f check.py ${student}/src

