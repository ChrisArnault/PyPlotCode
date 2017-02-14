
# targets

targets = [

    {"name": "find_stars", "command": "python find_stars.py -b ../../data/fits/NPAC.fits"},

    {"name": "lib_config", "command": "python lib_config.py -b" },
    {"name": "lib_logging", "command": "python lib_logging.py"},

]

# filters

run_filters_out = [ {"name": "wcs", "re": "^(WARNING:|warning:|Defunct|this form of).*$", "apply": "%"}, ]
diff_filters_in = [ {"name": "all", "re": "^(.+)$", "apply": "%"} ]

