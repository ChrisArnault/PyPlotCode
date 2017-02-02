#!/usr/bin/env python
# -*- coding: utf-8 -*-


''' Reading  fits file '''


import sys
from astropy.io import fits


def read_first_image( file_name ):
    header, pixels = None, None
    with fits.open(file_name) as data_fits:
        data_fits.verify('silentfix')
        header = data_fits[0].header
        pixels = data_fits[0].data
    return header, pixels


# =====
# Unit tests
# =====

if __name__ == '__main__':
    
    filename = '../../data/fits/NPAC.fits'
    header, pixels = read_first_image(filename)
    print('shape:',pixels.shape)
    print('cd1_1: {:.10f}'.format(header['CD1_1']))
    print('cd1_2: {:.10f}'.format(header['CD1_2']))
    print('cd2_1: {:.10f}'.format(header['CD2_1']))
    print('cd2_2: {:.10f}'.format(header['CD2_2']))

    sys.exit(0)


