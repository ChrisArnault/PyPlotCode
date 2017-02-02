#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import lib_args
import lib_wcs
import lib_stars


def main():

    # analyse command line arguments
    file_name, batch = lib_args.get_args()

    # main tasks
    # ...

    # example of console output
    # ...
    print('file: {}, batch: {}'.format(file_name, batch))

    # graphic output
    if not batch:
        # ...
        pass

    # end
    return 0
    

if __name__ == '__main__':

    sys.exit(main())
