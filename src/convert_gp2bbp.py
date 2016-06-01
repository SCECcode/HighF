#!/usr/bin/env python
"""
Utility to convert BBP time history files to BBP format
$Id$
"""
from shutil import copyfile

def convert_gp2bbp(eventid_str,station_id,infilepath,origin_time,datatype):
    input_file = infilepath
    output_file = "%s_%s_%s_gp.bbp"%(eventid_str,station_id,datatype)
    copyfile(input_file, output_file)
    return output_file