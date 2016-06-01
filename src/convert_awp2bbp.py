#!/usr/bin/env python
"""
Utility to convert AWP time history files to BBP format
$Id$
"""

# Import python modules
import sys

def convert_awp2bbp(eventid_str,station_id,infilepath,origin_time,datatype):
    input_file = infilepath
    output_file = "%s_%s_%s_awp.bbp"%(eventid_str,station_id,datatype)
    val1 = None
    val2 = None
#    file_dt = None
    
    # Figure out dt first, we need it later
    ifile = open(input_file)
    for line in ifile:
        # Skip comments
        if line.startswith("#") or line.startswith("%"):
            continue
        pieces = line.split()
        pieces = [float(piece) for piece in pieces]
        if val1 is None:
            val1 = pieces[0]
            continue
        if val2 is None:
            val2 = pieces[0]
            break
    ifile.close()
    
    # Quit if cannot figure out dt
    if val1 is None or val2 is None:
        print "Cannot determine dt from AWP file! Exiting..."
        sys.exit(1)
        
    # Calculate dt
    file_dt = val2 - val1
    
    # Covert from AWP to BBP format by swapping X and Y columns
    ifile = open(input_file)
    ofile = open(output_file, 'w')
    #
    # Write BBP header
    #
    #
    ofile.write("# BBP file from AWP simulation\n")
    # ofile.write("# Input file : %s")
    # Write first line of zeroes
    ofile.write("%1.9E %1.9E %1.9E %1.9E\n"%(0.0, 0.0, 0.0, 0.0))
    for line in ifile:
        # Skip comments
        if line.startswith("#") or line.startswith("%"):
            line = line.strip()
            # Write header
            ofile.write("%s\n" % (line))
            continue
        pieces = line.split()
        pieces = [float(piece) for piece in pieces]
        ofile.write("%1.9E %1.9E %1.9E %1.9E\n" %
                    (pieces[0]+file_dt, pieces[2], pieces[1], pieces[3]))
    
    # All done, close everything
    ifile.close()
    ofile.close()
    return output_file