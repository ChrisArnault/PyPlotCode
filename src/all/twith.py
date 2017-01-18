#!/usr/bin/env python
# -*- coding: utf-8 -*-


import threading


class ContextLock(object):

    def __init__(self, lock):

        self.lock = threading.Lock()

    def __enter__(self):

        self.lock.acquire()
        return self.lock

    def __exit__(self, type, value, traceback):

        self.lock.release()


if __name__ == '__main__':

    mylock = threading.Lock()
    with ContextLock(mylock):
        print('ok')

