
'''
Configuration file for the tool oval.
'''

# simple targets

targets = []

# generated targets

exercices = (
    "ex1_read_image",
    "ex2_background",
    "ex3_clusters",
    "ex4_coordinates",
    "ex5_find_stars",
)

import os, re
exp = re.compile('^NPAC..\.fits$')
for exercice in exercices:
    for filename in os.listdir('../fits'):
        if exp.match(filename):
            token = filename[:-5]
            target = "end.{}.{}".format(exercice,token)
            command = "../../src/end/{}.py -b ../fits/{}.fits".\
                format(exercice,token,exercice,target)
            targets.append({"name": target, "command": command})
for exercice in exercices:
    for filename in os.listdir('../fits'):
        if exp.match(filename):
            token = filename[:-5]
            target = "all.{}.{}".format(exercice,token)
            command = "../../src/all/{}.py -b ../fits/{}.fits".\
                format(exercice,token,exercice,target)
            targets.append({"name": target, "command": command})

# filters

run_filters_out = [ {"name": "wcs", "re": "^(WARNING:|warning:|Defunct|this form of).*$", "apply": "(begin|end|all).ex(4|5)%"}, ]
diff_filters_in = [ {"name": "all", "re": "^(.+)$", "apply": "(begin|end|all).ex%"} ]
