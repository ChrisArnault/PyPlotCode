#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
Utilities for SIMBAD access
'''


import sys, time
import urllib.request, urllib.error, urllib.parse
import numpy as np


def get_celestial_objects(ra, dec, radius):

    def make_req(ra, dec, radius):
        """
        Build a request to the Simbad server
        :param ra: floating point value of the RA coordinate
        :param dec: floating point value of the DEC coordinate
        :param radius: floting value of the acceptance radius (degrees)
        :return: request text
        """
        def crep(text, char):
            '''
            :param text: string which must be modified
            :param char: character to be replaced
            :return:
            '''
            text = text.replace(char, '%%%02X' % ord(char))
            return text

        host_simbad = 'simbad.u-strasbg.fr'

        # WGET with the "request" string built as below :

        script = ''
        # output format (for what comes from SIMBAD)
        script += 'format object f1 "'
        script += '%COO(A)'            # hour:minute:second
        script += '\t%COO(D)'          # degree:arcmin:arcsec
        script += '\t%OTYPE(S)'
        script += '\t%IDLIST(1)'
        script += '"\n'

        script += 'query coo '
        script += '%f' % ra           # append "a_ra" (decimal degree)
        script += ' '
        script += '%f' % dec          # append "a_dec" (decimal degree)
        script += ' radius='
        script += '%f' % radius       # append "a_radius" (decimal degree)
        script += 'd'                  # d,m,s
        script += ' frame=FK5 epoch=J2000 equinox=2000' # fk5
        script += '\n'

        # "special characters" converted to "%02X" format :
        script = crep(script, '%')
        script = crep(script, '+')
        script = crep(script, '=')
        script = crep(script, ';')
        script = crep(script, '"')
        script = crep(script, ' ')                # same as upper line.

        script = script.replace('\n', '%0D%0A')    # CR+LF
        script = crep(script, '\t')

        request = 'http://' + host_simbad + '/simbad/sim-script?'
        request += 'script=' + script + '&'

        return request

    def wget(req):
        """
        :param req:
        :return:
        """

        def send(url):
            '''
            :param url:
            :return:
            '''
            retry = 0
            while retry < 10:
                # pylint: disable=broad-except
                try:
                    req = urllib.request.urlopen(url)

                    try:
                        text = req.read()
                        text = text.decode("utf-8")
                        lines = text.split('<BR>\n')
                        return lines[0]
                    except Exception:
                        print('cannot read')
                    except:
                        raise

                except urllib.error.HTTPError:

                    retry += 1
                    time.sleep(0.2)
                except:
                    raise
            print(retry)

        out = send(req)

        return out

    req = make_req(ra, dec, radius)

    out = wget(req)
    if out is None:
        return '', out, req

    out = out.split('\n')

    in_data = False

    objects = dict()

    for line in out:
        line = line.strip()
        if line == '':
            continue
        if not in_data:
            if line == '::data::'+'::'*36:
                in_data = True
            continue

        data = line.split('\t')
        obj_name = data[3].strip()
        obj_type = data[2].strip()
        if  obj_type!='Unknown' and obj_type!='HII':
            objects[obj_name] = obj_type

    return objects, out, req


if __name__ == '__main__':

    ''' Unit tests '''

    for object in get_celestial_objects(1.0, 1.0, 0.1): 
        print('{} ({})'.format(object, objects[object]))
    if len(objects) != 14: print('error')

