
'''
Configuration file for the tool oval.
'''

# simple targets

targets = [

    {"name": "oval_test_diff_dict" , "command" : "python oval_test_diff_dict.py"  },

]

# filters

run_filters_out = [ {"name": "wcs", "re": "^(WARNING:|warning:|Defunct|this form of).*$", "apply": "%"}, ]
diff_filters_in = [ {"name": "exercices", "re": "^\s*RESULT\s*:\s*(.+?)\s*=\s*(.+?)\s*$", "apply": "%"}, ]
