#!/usr/bin/env python
"""
Utility to convert Hercules time history files to BBP format
$Id$
"""
import sys

def convert_hercules2bbp(eventid_str,station_id,infilepath,origin_time,datatype):
    input_file = infilepath
    output_file = "./%s_%s_%s_herc.bbp"%(eventid_str,station_id,datatype)
    val1 = None
    
    # Covert from Hercules to BBP format by selecting the velocity data
    ifile = open(input_file)
    ofile = open(output_file, 'w')
    ofile.write("# BBP file from Hercules\n")
    for line in ifile:
        # Skip comments
        if line.startswith("#") or line.startswith("%"):
            pieces = line.split()[1:]
            # Write header
            ofile.write("# %s %s %s %s\n" %
                        (pieces[0], pieces[4], pieces[5], pieces[6]))
            continue
        pieces = line.split()
        pieces = [float(piece) for piece in pieces]
        ofile.write("%1.9E %1.9E %1.9E %1.9E\n" %
                    (pieces[0], pieces[4], pieces[5], -1 * pieces[6]))
    
    # All done, close everything
    ifile.close()
    ofile.close()
