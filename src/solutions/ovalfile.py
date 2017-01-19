
# targets

targets = [

    { "name" : "ex1_read_image" , "command" : "python ex1_read_image.py -b ../../data/fits/NPAC.fits"  },
    { "name" : "ex2_background" , "command" : "python ex2_background.py -b ../../data/fits/NPAC.fits"  },
    { "name" : "ex3_clusters"   , "command" : "python ex3_clusters.py -b ../../data/fits/NPAC.fits"    },
    { "name" : "ex4_coordinates", "command" : "python ex4_coordinates.py -b ../../data/fits/NPAC.fits" },
    { "name" : "ex5_find_stars" , "command" : "python ex5_find_stars.py -b ../../data/fits/NPAC.fits"  },
    
]

# filters

run_filters_out = [ {"name": "wcs", "re": "^(WARNING:|warning:|Defunct|this form of).*$", "apply": "ex(4|5)%"}, ]
diff_filters_in = [ {"name": "all", "re": "^(.+)$", "apply": "ex%"} ]

