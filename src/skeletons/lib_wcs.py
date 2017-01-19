#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
Utilities for the world coordinate system
'''


import collections
import numpy as np
import astropy.wcs



# =====
# Information for a given image
#=====

def get_wcs(fits_header):

    ''' Parse the WCS keywords from a FITS image header '''

    return astropy.wcs.WCS(fits_header)


# =====
# Coordinate systems
# * x/y position in an image : PixelXY(x,y)
# * ra/dec position in the sky : RaDec(ra,dec)
#=====

PixelXY = collections.namedtuple('PixelXY',['x','y'])

RaDec = collections.namedtuple('RaDec',['ra','dec'])


# =====
# Converters
#=====


def xy_to_radec(wcs, pxy):

    '''
    Convert the x/y coordinates of an image pixel
    into the ra/dec coordinates of a celestial body
    :param wcs: a wcs object, as returned by get_wcs()
    :param pxy: an instance of PixelXY
    :return: an instance of RaDec
    '''

    pixel = np.array([[pxy.x, pxy.y],], np.float_)
    sky = wcs.wcs_pix2world(pixel, 0)
    return RaDec(ra=sky[0][0], dec=sky[0][1])


def radec_to_xy(wcs, rd):

    '''
    Convert the ra/dec coordinates of a celestial body
    into the x/y coordinates of an image pixel.
    :param wcs: a wcs object, as returned by get_wcs()
    :param rd: an instance of RaDec
    :return: an instance of PixelXL
    '''

    coord = np.array([[rd.ra, rd.dec],], np.float_)
    result = wcs.wcs_world2pix(coord, 0)
    return PixelXY(x=result[0][0], y=result[0][1])


# =====
# Unit tests
#
# It uses a fake wcs which is just swapping first and second coordinates. This avoid
# the need for a real fits image so to test our two functions.
#=====

if __name__ == '__main__':
    
    class FakeWcs():
        def wcs_pix2world(self, xy, fake):
            return ((xy[0][1],xy[0][0]),)
        def wcs_world2pix(self, radec, fake):
            return ((radec[0][1],radec[0][0]),)

    wcs = FakeWcs()
    pxy = PixelXY(1,2)
    rd = RaDec(2,1)
    print(xy_to_radec(wcs,pxy)==rd)
    print(radec_to_xy(wcs,rd)==pxy)

