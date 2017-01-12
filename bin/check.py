#!/usr/bin/env python

'''
This script can compare line by line
a textual file with an md5 encrypted one.
'''

import argparse
import hashlib

# process command-line options
parser = argparse.ArgumentParser(
    description='Compare line by line a textual file with an encrypted one')
parser.add_argument('num', help='the exercice number')

'''
 parser.add_argument('txtfile', help='the not encrypted file')
 parser.add_argument('md5file', help='the encrypted file')
'''

args = parser.parse_args()

def compare_files(txtfile, md5file):

    # parse and encrypt txt file
    out_txt_lines = []
    out_md5_lines = []
    with open(txtfile) as out_txt_content:
        for out_txt_line in out_txt_content:
            line = out_txt_line.rstrip()
            if line:
              out_txt_lines.append(line)
              out_md5_lines.append(hashlib.md5(line).hexdigest())

    # parse md5 file
    ref_md5_lines = []
    with open(md5file) as ref_md5_content:
        for ref_md5_line in ref_md5_content:
            ref_md5_lines.append(ref_md5_line.rstrip())

    # complete lacking matches
    while len(out_md5_lines) < len(ref_md5_lines):
        out_txt_lines.append('EMPTY STRING')
        out_md5_lines.append('EMPTY STRING')
    while len(out_md5_lines) > len(ref_md5_lines):
        ref_md5_lines.append('EMPTY STRING')

    # compare
    zipped = list(zip(out_txt_lines, out_md5_lines, ref_md5_lines))
    diffs = []
    for tpl in zipped:
        if tpl[1] != tpl[2]:
            diffs.append('md5("{}") != {}'.format(tpl[0], tpl[2]))
    return diffs

txtfile = 'ex'+args.num+'.txt'
md5file = '../data/ex'+args.num+'.md5'
diffs = compare_files(txtfile, md5file)
if diffs:
    print("NOT OK (did you process specific.fits ?)")
else:
    print('You did it right !')
