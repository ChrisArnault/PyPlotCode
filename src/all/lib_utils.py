#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
def dms(angle):
    """ Convert a floating point angle into textual representation
        Degree:Minute:Second (-> DEC coordinate) """
    degree = int(angle)
    minute = (angle - degree) * 60.0
    second = (minute - int(minute)) * 60.0
    return '[%d:%d:%f]' % (int(degree), int(minute), second)


def hms(angle):
    """ Convert a floating point angle into textual representation
        Hour:Minute:Second (-> RA coordinate) """
    hour = angle*24.0/360.0
    hour2 = int(hour)
    minute = (hour - hour2) * 60.0
    second = (minute - int(minute)) * 60.0
    return '[%d:%d:%f]' % (int(hour2), int(minute), second)


def radec(coord):
    """ Convert a floating point coordinates into textual representation
        Hour:Minute:Second (-> RA/DEC coordinates) """
    return 'RA=%s DEC=%s' % (hms(coord[0]), dms(coord[1]))
'''

def tests():
    'Unit tests'
    return 0

if __name__ == '__main__':
    sys.exit(tests())

