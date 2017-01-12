#!/usr/bin/env bash

npac=../../../..

for txt in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20
do

    rm -rf ${npac}/NPAC${txt}
    mkdir -p ${npac}/NPAC${txt}/data
    mkdir -p ${npac}/NPAC${txt}/src

    cp -f data/student/NPAC.fits ${npac}/NPAC${txt}/data/common.fits
    cp -f data/student/NPAC${txt}.fits ${npac}/NPAC${txt}/data/specific.fits

    cp -f check.py pylintrc ${npac}/NPAC${txt}/src
    cp -f lib*.py ${npac}/NPAC${txt}/src
    
    #for ex in ex1_read_image ex2_background ex3_clusters ex4_coordinates ex5_find_stars
    #do
    #    cp -f data/student/${ex}.NPAC${txt}.md5 ${npac}/NPAC${txt}/data/${ex}.md5
    #    cp -f data/student/${ex}.NPAC${txt}.out ${npac}/NPAC${txt}/src/${ex}.txt

    cp -f data/student/ex1_read_image.NPAC${txt}.md5 ${npac}/NPAC${txt}/data/ex1.md5
    cp -f data/student/ex1_read_image.NPAC${txt}.out ${npac}/NPAC${txt}/src/ex1.txt

    cp -f data/student/ex2_background.NPAC${txt}.md5 ${npac}/NPAC${txt}/data/ex2.md5
    cp -f data/student/ex2_background.NPAC${txt}.out ${npac}/NPAC${txt}/src/ex2.txt

    cp -f data/student/ex3_clusters.NPAC${txt}.md5 ${npac}/NPAC${txt}/data/ex3.md5
    cp -f data/student/ex3_clusters.NPAC${txt}.out ${npac}/NPAC${txt}/src/ex3.txt

    cp -f data/student/ex4_coordinates.NPAC${txt}.md5 ${npac}/NPAC${txt}/data/ex4.md5
    cp -f data/student/ex4_coordinates.NPAC${txt}.out ${npac}/NPAC${txt}/src/ex4.txt

    cp -f data/student/ex5_find_stars.NPAC${txt}.md5 ${npac}/NPAC${txt}/data/ex5.md5
    cp -f data/student/ex5_find_stars.NPAC${txt}.out ${npac}/NPAC${txt}/src/ex5.txt

    #done

done

