#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Utilities for the world coordinate system
'''

import numpy as np
import astropy.wcs

def get_wcs(fits_header):

    ''' Parse the WCS keywords from the primary HDU of an FITS image '''

    return astropy.wcs.WCS(fits_header)


def convert_to_radec(wcs, x, y):

    pixel = np.array([[x, y],], np.float_)
    sky = wcs.wcs_pix2world(pixel, 0)
    ra, dec = sky[0]
    return ra, dec


def convert_to_xy(wcs, ra, dec):

    coord = np.array([[ra, dec],], np.float_)
    result = wcs.wcs_world2pix(coord, 0)
    x, y = result[0]
    return x, y


if __name__ == '__main__':
    
    ''' Unit tests '''

    import lib_reader
    filename = '../data/dss.19.59.54.3+09.59.20.9 10x10.fits'
    header, _ = lib_reader.read_first_image(filename)
    wcs = library.WCS(header)
    ra, dec = w.convert_to_radec(0, 0)
    if abs(ra - 300.060983768) > 1e-5: print('error')
    if abs(dec - 9.90624639801) > 1e5: print('error')

