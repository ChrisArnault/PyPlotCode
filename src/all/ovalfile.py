
'''
Configuration file for the tool oval.
'''

# simple targets

targets = [

    {"name": "analyze_ex0", "command": "pylint ex0_hello_loops.py"},
    {"name": "analyze_ex1", "command": "pylint ex1_read_image.py"},
    {"name": "analyze_ex2", "command": "pylint ex2_background.py"},
    {"name": "analyze_ex3", "command": "pylint ex3_clusters.py"},
    {"name": "analyze_ex4", "command": "pylint ex4_coordinates.py"},
    {"name": "analyze_ex5", "command": "pylint ex5_find_stars.py"},

    {"name": "analyze_lib_background", "command": "pylint lib_background.py"},
    {"name": "analyze_lib_cluster", "command": "pylint lib_cluster.py"},
    {"name": "analyze_lib_logging", "command": "pylint lib_logging.py"},
    {"name": "analyze_lib_model", "command": "pylint lib_model.py"},
    {"name": "analyze_lib_read_file", "command": "pylint lib_read_file.py"},
    {"name": "analyze_lib_wcs", "command": "pylint lib_wcs.py"},

    {"name": "oval", "command": "pylint oval"},
    {"name": "ovalfile", "command": "pylint ovalfile"},

    {"name": "lib_logging", "command": "python lib_logging.py"},
]

# generated targets

exercices = (
    "ex1_read_image",
    "ex2_background",
    "ex3_clusters",
    "ex4_coordinates",
    "ex5_find_stars",
)

import os
for exercice in exercices:
    for index, img in enumerate(os.listdir('data')):
        token = "data{}".format(index)
        target = "{}.{}".format(exercice,token)
        command = "./{}.py -b data/{}".\
            format(exercice,img,exercice,exercice,token)
        targets.append({"name": target, "command": command})

# Filters

run_filters_out = [ {"name": "wcs", "re": "^(WARNING:|warning:|Defunct|this form of).*$", "apply": "ex(4|5)%"}, ]

diff_filters_in = [
    {"name": "pylint1", "re": "%rated at%", "apply": "(analyze%)|(oval%)"},
    {"name": "pylint2", "re": "[CEWIDR]:%", "apply": "(analyze%)|(oval%)"},
    {"name": "info", "re": "^(.+)$", "apply": "ex%"},
]
