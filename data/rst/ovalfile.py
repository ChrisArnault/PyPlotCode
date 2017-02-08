

'''
Configuration file for the tool oval.
'''


# simple targets

targets = []


# exercices names

exercices = (
    "ex1_read_image",
    "ex2_background",
    "ex3_clusters",
    "ex4_coordinates",
    "ex5_find_stars",
)


# exercices targets

for exname in exercices:
    tname = exname
    tcommand = "python ../../src/solutions/{}.py -b ../fits/NPAC.fits".format(exname)
    targets.append({"name": tname, "command": tcommand})


# rst targets

for exnum, exname in enumerate(exercices):
    tname = "rst{}".format(exnum)
    tcommand = "python ref_to_rst.py {}".format(exname)
    targets.append({"name": tname, "command": tcommand})


# filters

run_filters_out = [ {"name": "wcs", "re": "^(WARNING:|warning:|Defunct|this form of).*$", "apply": "%"}, ]
diff_filters_in = [ {"name": "all", "re": "^(.+)$", "apply": "%"} ]
