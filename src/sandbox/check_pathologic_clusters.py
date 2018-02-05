#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
sys.path.append('../skeletons')
sys.path.append('../solutions')
import lib_args
import lib_fits
import lib_background
import lib_cluster
import lib_wcs
import lib_stars


# prepare clusters
file_name, interactive = lib_args.get_args()
header, pixels = lib_fits.read_first_image(file_name)
print('image shape is {}'.format(pixels.shape))
background, dispersion, _ = lib_background.compute_background(pixels)
pattern_radius = 4
clustering = lib_cluster.Clustering(pattern_radius)
clusters = clustering(pixels, background, dispersion)
nb_patho = 0

# print clusters details
for icl, cl in enumerate(clusters):
    print('cluster {:d}: {}'.format(icl, cl))

# check no cluster
if len(clusters) == 0:
    print('no cluster')
    nb_patho += 1

# check single cluster (too simple)
if len(clusters) == 1:
    print('single cluster')
    nb_patho += 1

# check clusters in border
for icl, cl in enumerate(clusters):
    pattern_diameter = pattern_radius*2 + 1
    if ((cl.row < pattern_diameter) or
            (cl.row >= (pixels.shape[0]-pattern_diameter)) or
            (cl.column < pattern_diameter) or
            (cl.column >= (pixels.shape[1]-pattern_diameter))):
        print('cluster {:d} is in the border'.format(icl, cl))
        nb_patho += 1

# check max integral clusters are not too similar
if len(clusters) > 1 and ((clusters[0].integral - clusters[1].integral) < 10.):
    print('clusters 0 and 1 are too similar')
    nb_patho += 1

# check lacking or multiple celestial objects for max cluster
wcs = lib_wcs.get_wcs(header)
pxy = lib_wcs.PixelXY(clusters[0].column, clusters[0].row)
radec = lib_wcs.xy_to_radec(wcs, pxy)
cobjects, _, _ = lib_stars.get_celestial_objects(radec)
if len(cobjects) < 1:
    print('clusters 0 is associated with no celestial object')
    nb_patho += 1
if len(cobjects) > 1:
    print('clusters 0 is associated with multiple celestial objects')
    for icobj, cobj in enumerate(sorted(cobjects.keys())):
        print('celestial object {}: {}'.format(icobj, cobj))
    nb_patho += 1

# conclusion
print('{} pathologic clusters'.format(nb_patho))
sys.exit(nb_patho)
