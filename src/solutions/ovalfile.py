
# targets

targets = [

    {"name": "ex1_read_image" , "command" : "python ex1_read_image.py -b ../../data/fits/NPAC.fits"  },
    {"name": "ex2_background" , "command" : "python ex2_background.py -b ../../data/fits/NPAC.fits"  },
    {"name": "ex3_clusters"   , "command" : "python ex3_clusters.py -b ../../data/fits/NPAC.fits"    },
    {"name": "ex4_coordinates", "command" : "python ex4_coordinates.py -b ../../data/fits/NPAC.fits" },
    {"name": "ex5_find_stars" , "command" : "python ex5_find_stars.py -b ../../data/fits/NPAC.fits"  },
    
    {"name": "lib_cluster", "command" : "python lib_cluster.py"  },
    {"name": "lib_fits", "command" : "python lib_fits.py" },

    {"name": "pj1_background_suppress", "command": "python pj1_background_suppress.py -b ../../data/fits/NPAC.fits"},
    {"name": "pj2_cluster_slider", "command": "python pj2_cluster_slider.py -b ../../data/fits/NPAC.fits"},
    {"name": "pj3_file_selector", "command": "python pj3_file_selector.py -b ../../data"},
#    {"name": "pj4_recursive_clustering", "command": "python pj4_recursive_clustering.py -b ../../data/fits/NPAC.fits"},
    {"name": "pj5_concurrent_clustering", "command": "python pj5_concurrent_clustering.py -b ../../data/fits/NPAC.fits"},

]

# filters

run_filters_out = [
    {"name": "wcs", "re": "^(WARNING:|warning:|Defunct|this form of).*$", "apply": "ex(4|5)%"},
    {"name": "time", "re": "^.*execution time.*$", "apply": "%"},
]
diff_filters_in = [ {"name": "all", "re": "^(.+)$", "apply": "%"} ]

