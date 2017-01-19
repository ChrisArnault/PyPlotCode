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


def tests():

    ''' Unit tests '''

    import lib_wcs
    filename = '../../data/fits/dss.19.59.54.3+09.59.20.9 10x10.fits'
    header, _ = lib_fits.read_first_image(filename)
    wcs = lib_wcs.get_cws(header)
    xy = { 'x' : 0, 'y' : 0 }
    radec = w.xy_to_radec(wcs,xy)
    if abs(ra - 300.060983768) > 1e-5: print('error')
    if abs(dec - 9.90624639801) > 1e5: print('error')

    return 0


if __name__ == '__main__':
    
    sys.exit(tests())


