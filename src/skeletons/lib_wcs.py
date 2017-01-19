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


def xy_to_radec(wcs, xy):

    x, y = xy['x'], xy['y']
    pixel = np.array([[x, y],], np.float_)
    sky = wcs.wcs_pix2world(pixel, 0)
    ra, dec = sky[0]
    return { 'ra' : ra, 'dec' : dec }


def radec_to_xy(wcs, radec):

    ra, dec = radec['ra'], radec['dec']
    coord = np.array([[ra, dec],], np.float_)
    result = wcs.wcs_world2pix(coord, 0)
    x, y = result[0]
    return { 'x' : round(x), 'y' : round(y) }


if __name__ == '__main__':
    
    ''' Unit tests '''

    class FakeWcs():
        def wcs_pix2world(self, xy, fake):
            return ((xy[0][1],xy[0][0]),)
        def wcs_world2pix(self, radec, fake):
            return ((radec[0][1],radec[0][0]),)

    wcs = FakeWcs()
    pix = { 'x' : 1, 'y' : 2 }
    world = { 'ra' : 2, 'dec' : 1 }
    print(xy_to_radec(wcs,pix)==world)
    print(radec_to_xy(wcs,world)==pix)

