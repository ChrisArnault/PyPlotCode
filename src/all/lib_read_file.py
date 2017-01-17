#!/usr/bin/env python
# -*- coding: utf-8 -*-

'Reading  fits file'

import sys

from astropy.io import fits
from lib_logging import logging

def read_first_image(fitsfile):
    header = None
    pixels = None
    try:
        with fits.open(fitsfile) as data_fits:
            try:
                data_fits.verify('silentfix')
                header = data_fits[0].header
                pixels = data_fits[0].data
            except ValueError as err:
                logging.error('Error: %s', err)
    except EnvironmentError as err:
        logging.error('Cannot open the data fits file. - %s', err)
    return header, pixels

def read_pixels(fitsfile):
    """Get pixels from FITS file

    cf http://stsdas.stsci.edu/stsci_python_epydoc/pyfits/api_hdulists.html

    Return a HDUList()
    """
    pixels = None
    try:
        with fits.open(fitsfile) as data_fits:
            try:
                data_fits.verify('silentfix')
                pixels = data_fits[0].data
            except ValueError as err:
                logging.error('Error: %s', err)
    except EnvironmentError as err:
        logging.error('Cannot open the data fits file. - %s', err)
    return pixels


def read_header(fitsfile):
    """Get pixels from FITS file

    cf http://stsdas.stsci.edu/stsci_python_epydoc/pyfits/api_hdulists.html

    Return a HDUList()
    """

    header = None
    try:
        with fits.open(fitsfile) as data_fits:
            try:
                data_fits.verify('silentfix')
                header = data_fits[0].header
            except ValueError as err:
                logging.error('Error: %s', err)
    except EnvironmentError as err:
        logging.error('Cannot open the data fits file. - %s', err)
    return header

def tests():
    'Unit tests'
    return 0

if __name__ == '__main__':
    sys.exit(tests())


