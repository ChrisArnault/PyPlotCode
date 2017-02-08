#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time
import concurrent.futures

def add(value1, value2):
    time.sleep(2)
    return (value1+value2)

exes = concurrent.futures.ProcessPoolExecutor()

time0 = time.time()

future_res1 = exes.submit(add, 10, 1)
future_res2 = exes.submit(add, 20, 2)

print("res1:",future_res1.result())
print("res2:",future_res2.result())

time1 = time.time()

print("time:",time1-time0,"seconds")
