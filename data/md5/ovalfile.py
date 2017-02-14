
'''
Configuration file for the tool oval.
'''

# simple targets

targets = []

# exercices targets

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
            target = "{}.{}".format(exercice,token)
            command = "../../src/solutions/{}.py -b ../fits/{}".format(exercice,filename)
            targets.append({"name": target, "command": command})

# find_stars target

for filename in os.listdir('../fits'):
    if exp.match(filename):
        token = filename[:-5]
        target = "find_stars.{}".format(token)
        command = "../../src/collective/find_stars.py -b ../fits/{}".format(filename)
        targets.append({"name": target, "command": command})


# filters

run_filters_out = [ {"name": "wcs", "re": "^(WARNING:|warning:|Defunct|this form of).*$", "apply": "%"}, ]
diff_filters_in = [ {"name": "all", "re": "^(.+)$", "apply": "%"} ]
