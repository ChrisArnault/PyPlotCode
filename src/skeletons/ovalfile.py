
# targets

targets = [
    { "name" : "ex1_read_image" , "command" : "python ex1_read_image.py -b ../../data/fits/common.fits"  },
    { "name" : "ex2_background" , "command" : "python ex2_background.py -b ../../data/fits/common.fits"  },
    { "name" : "ex3_clusters"   , "command" : "python ex3_clusters.py -b ../../data/fits/common.fits"    },
    { "name" : "ex4_coordinates", "command" : "python ex4_coordinates.py -b ../../data/fits/common.fits" },
    { "name" : "ex5_find_stars" , "command" : "python ex5_find_stars.py -b ../../data/fits/common.fits"  },

    { "name" : "lib_args1", "command" : "python lib_args.py -b"  },
    { "name" : "lib_args2", "command" : "python lib_args.py ../../data/fits/NPAC04.fits"  },
    { "name" : "lib_args3", "command" : "echo '' | python lib_args.py"  },
    { "name" : "lib_args4", "command" : "echo 'NPAC04' | python lib_args.py"},

    { "name" : "lib_wcs"  , "command" : "python lib_wcs.py"  },
    { "name" : "lib_stars", "command" : "python lib_stars.py"  },
    { "name" : "lib_pixels_set", "command" : "python lib_pixels_set.py"},

    # those ones should be executed within the student environment
    { "name" : "stud_lib_args5", "command" : "unset DATAPATH ; python lib_args.py -b"},
    { "name" : "stud_lib_args6", "command" : "unset DATAPATH ; python lib_args.py ../data/specific.fits"},
    { "name" : "stud_lib_args7", "command" : "unset DATAPATH ; echo '' | python lib_args.py"},
    { "name" : "stud_lib_args8", "command" : "unset DATAPATH ; echo 'specific' | python lib_args.py"},
]

# filters

run_filters_out = [ {"name": "wcs", "re": "^(WARNING:|warning:|Defunct|this form of).*$", "apply": "ex(4|5)%"}, ]
diff_filters_in = [ {"name": "all", "re": "^(.+)$", "apply": "%"} ]

