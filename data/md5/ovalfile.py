
'''
Configuration file for the tool oval.
'''

# simple targets

targets = []

# generated targets

exercices = (
    "ex1_read_image",
    "ex2_background",
    "ex3_new_clusters",
    "ex4_coordinates",
    "ex5_find_stars",
)

import os
for exercice in exercices:
    for filename in os.listdir('../fits'):
        if filename.endswith('.fits'):
            token = filename[:-5]
            target = "{}.{}".format(exercice,token)
            command = "../../src/{}.py -b ../fits/{}.fits".\
                format(exercice,token,exercice,target)
            targets.append({"name": target, "command": command})

# filters

run_filters_out = [ {"name": "wcs", "re": "^(WARNING:|warning:|Defunct|this form of).*$", "apply": "ex(4|5)%"}, ]
diff_filters_in = [ {"name": "all", "re": "^(.+)$", "apply": "ex%"} ]
