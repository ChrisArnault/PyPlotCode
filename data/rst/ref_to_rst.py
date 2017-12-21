#!/usr/bin/env python

import sys

ifilename = "{}.ref".format(sys.argv[1])
ofilename = "{}.rst".format(sys.argv[1])


with open(ofilename, 'w') as ofile:

    ofile.write(".. code-block:: python"+'\n')
    ofile.write('\n')

    with open(ifilename, 'r') as ifile:
        for line in ifile.readlines():
            ofile.write("  "+line)

    ofile.write('\n')

print('done')

