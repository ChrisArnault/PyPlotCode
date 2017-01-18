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

    return 0


if __name__ == '__main__':
    
    sys.exit(tests())


