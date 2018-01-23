#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
sys.path.append('../skeletons')
import lib_args, lib_fits, lib_background, lib_cluster
import lib_wcs
import lib_stars


def get_celestial_objects( wcs, cluster ):
    pxy = lib_wcs.PixelXY(cluster.column, cluster.row)
    radec = lib_wcs.xy_to_radec(wcs, pxy)
    return lib_stars.get_celestial_objects(radec)

def show_cluster(wcs, i, cluster):
    print('DEBUG: {} cluster={} {} {}'.format(i, cluster.integral, cluster.column, cluster.row))

    pxy = lib_wcs.PixelXY(cluster.column, cluster.row)
    radec = lib_wcs.xy_to_radec(wcs, pxy)

    print('RESULT: right_ascension = {:.3f}'.format(radec.ra))
    print('RESULT: declination = {:.3f}'.format(radec.dec))

    os, _, _ = get_celestial_objects(wcs, cluster)
    for cobj in os.keys():
        print('RESULT: celestial_object = {}'.format(cobj))


def main():

    file_name, interactive = lib_args.get_args()
    header, pixels = lib_fits.read_first_image(file_name)
    background, dispersion, _ = lib_background.compute_background(pixels)
    clustering = lib_cluster.Clustering()
    clusters = clustering(pixels, background, dispersion)
    max_cluster = clusters[0]

    # coordinates ra dec
    wcs = lib_wcs.get_wcs(header)

    for i, c in enumerate(clusters):
        show_cluster(wcs, i, c)
        break

    return 0


if __name__ == '__main__':

    sys.exit(main())
