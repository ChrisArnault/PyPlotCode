#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
sys.path.append('../skeletons')
sys.path.append('../solutions')


# =====
# Unit tests
# =====

if __name__ == '__main__':

    import lib_args
    file_name, batch = lib_args.get_args()
    print('name of file: {}'.format(file_name))
    print('batch: {}'.format(batch))

