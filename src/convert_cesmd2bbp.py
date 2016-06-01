#!/usr/bin/env python
'''
Created on Nov 25, 2015

@author: maechlin
'''
import sys
import os
import argparse
import datetime
import math

CM_PER_METER = 100.0
USECS_PER_SEC = 1000000.0

#
# Define processing to convert two time formats into datetime objects. 
# The following are examples of the input formats.
# (1) observed seismogram start time from COSMOS data
# " 3/29/14, 04:09:39.0 UTC"
# (2) earthquake origin time from 
# "2014:03:29:04:09:42.0"
# Confirm that obs starts before the origin time
# Figure out how much time needs to be trimmed from obs to start it at origin = 0.0
# Figure out how many samples need to be dropped from start of obs
# Update number of samples to write
# Write trimmed seismograms
#
#
# Example Usage:
# ./convert_smo2bbp.py -e LaHabra -o 2014:03:29:04:09:42.31 -f ./smo_files/CE13873.V2 -d v
#

def origin_time_2_datetime(origin_time):
    """
    Extract origin time into datetime
    Time format is : 2014-03-29T04:09:42.170Z
    ISO 8601 datetime standard for UTC times.
    """
    #vals = origin_time.split(":")
    #datevals = vals[0].split("-")
    #year = int(datevals[0])
    #month = int(datevals[1])
    #day = int(datevals[2])
    
    #hr = int(vals[3])
    #mints = int(vals[4])
    #secs = float(vals[5])
    #vals = math.modf(secs) # (0.5678000000000338, 1234.0)
    #usecs = vals[0] * USECS_PER_SEC
    # odate = dateutil.parser.parse(origin_time)
    odate = datetime.datetime.strptime(origin_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    #print "Origin time:",year,month,day,hr,mints,secs,int(vals[1]),int(usecs)
    #return datetime.datetime(year,month,day,hr,mints,int(vals[1]),int(usecs))
    return odate


def cosmos_time_2_datetime(cm_timestring):
    """
    Extract odd cosmos time UTC
    """
    month = int(cm_timestring[0:2])
    day = int(cm_timestring[3:5])
    year_short = int (cm_timestring[6:8])
    year = 0
    if year_short < 20:
        year =  2000 + year_short
    else:
        year = 1900 + year_short
    hr = int(cm_timestring[10:12])
    mints = int(cm_timestring[13:15])
    secs = float(cm_timestring[16:20])
    
    vals = math.modf(secs) # (0.5678000000000338, 1234.0)
    usecs = vals[0] * USECS_PER_SEC
    print "Start time:",year,month,day,hr,mints,secs,int(vals[1]),int(usecs)
    return datetime.datetime(year,month,day,hr,mints,int(vals[1]),int(usecs))

def samples_to_trim(origin_time,start_time,sps):
    """
    returns integer number of samples to drop
    """
    tdelta = origin_time - start_time # This returns the fractional second part
    samples_to_trim = int(tdelta.total_seconds() / sps)
    return samples_to_trim

def find_pgms(filetxt,datatype):
    """
    Returns a array of two component results with 
    value - = peak motion and value 2 = time of peak motion
    """
    chan1_start = 0
    chan2_start = 0
    chan3_start = 0
    pgms = []
    
    for i,l in enumerate(filetxt):
        res = l.find("Chan  1:")
        if res > 0:
            chan1_start = i
            break
        
    for i,l in enumerate(filetxt):
        res = l.find("Chan  2:")
        if res > 0:
            chan2_start = i
            break
    
    for i,l in enumerate(filetxt):
        res = l.find("Chan  3:")
        if res > 0:
            chan3_start = i
            break

    #print chan1_start,chan2_start, chan3_start
    
    match_phrase = ""

    if datatype == "d":
        match_phrase = "Peak displacement"
    elif datatype == "v":
        match_phrase = "Peak   velocity"
    elif datatype == "a":
        match_phrase = "Peak acceleration"
    else:
        raise "Unexpected datatype requested from V2 file %s" % (datatype)

    #print "pgms chans",chan1_start, chan2_start, chan3_start
    #print "Using match_phrase- :%s:" % (match_phrase)

    for i,l in enumerate(filetxt[chan1_start:chan2_start-1]):
        res = l.find(match_phrase)
        #print l,res
        if res > -1:
            res_array = []
            pgmstr = float(l[19:29])
            tstr = float(l[47:56])
            res_array.append(pgmstr)
            res_array.append(tstr)
            pgms.append(res_array)
            break
            
    for i,l in enumerate(filetxt[chan2_start:chan3_start-1]):
        res = l.find(match_phrase)
        if res > -1:
            res_array = []
            pgmstr = float(l[19:29])
            tstr = float(l[47:56])
            res_array.append(pgmstr)
            res_array.append(tstr)
            pgms.append(res_array)
            break

    for i,l in enumerate(filetxt[chan3_start:len(filetxt)]):
        res = l.find(match_phrase)
        if res > -1:
            res_array = []
            pgmstr = float(l[19:29])
            tstr = float(l[47:56])
            res_array.append(pgmstr)
            res_array.append(tstr)
            pgms.append(res_array)
            break
        
    return pgms


def find_starttimes(filetxt):
    ret_str = ""
    chan1_start = 0
    chan2_start = 0
    chan3_start = 0
    starttimes = []
    
    for i,l in enumerate(filetxt):
        if l.find("Chan  1:"):
            chan1_start = i
            break
        
    for i,l in enumerate(filetxt):
        if l.find("Chan  2:"):
            chan2_start = i
            break
    
    for i,l in enumerate(filetxt):
        if l.find("Chan  3:"):
            chan3_start = i
            break
    
    match_phrase = "Start time:"
    
    for i,l in enumerate(filetxt[chan1_start:chan2_start-1]):
        res = l.find(match_phrase)
        if res > 0:
            ret_str = l[49:73]
            starttimes.append(ret_str)
            break
            
    for i,l in enumerate(filetxt[chan2_start:chan3_start-1]):
        res = l.find(match_phrase)
        if res > 0:
            ret_str = l[49:73]
            starttimes.append(ret_str)
            break

    for i,l in enumerate(filetxt[chan3_start:len(filetxt)-1]):
        res = l.find(match_phrase)
        if res > 0:
            ret_str = l[49:73]
            starttimes.append(ret_str)
            break
        
    return starttimes

def convert_cesmd2bbp(eventid,filepath,origin_time,datatype):
    """
    Input: command line parameters in a collection from argparse
    Output: bbp file with contents of smo file in it. Writes the file into
        the runtime directory of the program. File naming convention is
        EventID_InputFile_Datatype.bbp
    Returns: No return value
    
    Notes:
    The SMO convention is data in cm/sec. The 3D simulations are in m/s, so this
    routine converts outputs velocity and writes bbp velocity data in m/sec
    This could eventually be an user option, but currently we will hard code this.
    """
    #
    # Construct input and output file names
    #
    data_file_name = filepath
    smo_file = os.path.basename(filepath)
    vals = smo_file.split(".")
    outfile_name = "%s_%s_%s_obs.bbp" % (eventid,
                                     vals[0],
                                     datatype)

    # Read lines from input file into memory
    f_near = open(data_file_name, "r")
    lines = f_near.readlines()
    f_near.close()


    n_start = 0
    n_lines = 0
    n_samples = 0

    e_start = 0
    e_lines = 0
    e_samples = 0

    z_start = 0
    z_lines = 0
    z_samples = 0

    min_duration = 0.0
    common_dt = 0.0
    
    #
    # Start times returns an array of three times as chan1 (e) chan2(n) chan 3(z)
    #
    starttimes = []
    starttimes = find_starttimes(lines)
    if len(starttimes) != 3:
        print "Empty start time found"
        raise "No start time found in file %s and component n" % (filepath)
    if ((starttimes[0] != starttimes[1]) or (starttimes[1] != starttimes[2])):
        raise "Components start at different times - exiting...."
    # Find PG Motions for the selected data type
    # Assume a 0.0 means values not found in file ane exit
    #
    pgms = []
    pgms = find_pgms(lines,datatype)
    if len(pgms) != 3:
        print "Empty peak ground motion found"
        raise "No start time found in file %s and component n" % (filepath)
    
    #
    # Based on the cmd line input, define the search criteria for 
    # the three types of data in smo: accel, vel, or display
    #
    match_phrase = ""
    if datatype == "d":
        match_phrase = "points of displ data equally spaced at"
    elif datatype == "v":
        match_phrase = "points of veloc data equally spaced at"
    elif datatype == "a":
        match_phrase = "points of accel data equally spaced at"
    else:
        raise "Unexpected datatype requested from V2 file %s" % (datatype)
    
    #
    # Scan Key Values from Header
    # Start with dt
    # npts
    # duration
    #
    #
    # The following processing may drop a few data points from the V2 file, so the bbp seismograms may be
    # slightly shorter. This is because this conversion script drops samples in the last line of each V2
    # seismogram if there are less than 8 samples in line. Also, the min samples between the 
    # three components are moved into the bbp, so no padding of missing samples is needed in the bbp
    #
    comps_found = 0
    for i,l in enumerate(lines):
        res = l.find(match_phrase)
        if res > 0:
            #print "found matching datatype at line: %d"%(i)
            number_of_samples = int(l[0:7])
            print "Number of samples :",number_of_samples
            common_dt = float(l[46:52])
            print "Common dt:",common_dt
            number_of_lines = number_of_samples/8
            print "Number of datalines:",number_of_lines
            
            #
            # SMO Format has Chan 1 - E/W - Chan 2 - N/S Chan 3 - E/W
            #
            if comps_found == 0:
                e_start = i
                e_lines = number_of_lines
                e_samples = number_of_samples
            elif comps_found == 1:
                n_start = i
                n_lines = number_of_lines
                n_samples = number_of_samples
            elif comps_found == 2:
                z_start = i
                z_lines = number_of_lines
                z_samples = number_of_samples
            else:
                print "Error in case statement"
                break
            
            comps_found = comps_found + 1

    e_pts = []
    n_pts = []
    z_pts = []

    #
    # Extract the data points
    #
    for myline in lines[e_start+1:(e_start+e_lines-1)]:
        vals = []
        vals.append(float(myline[0:9]))
        vals.append(float(myline[10:19]))
        vals.append(float(myline[20:29]))
        vals.append(float(myline[30:39]))
        vals.append(float(myline[40:49]))
        vals.append(float(myline[50:59]))
        vals.append(float(myline[60:69]))
        vals.append(float(myline[70:79]))
        if len(vals) != 8:
            print "unexpected number of values in line"
            sys.exit(0)
        for e in vals:
            e_pts.append(e)

    for myline in lines[n_start+1:(n_start+n_lines-1)]:
        vals = []
        vals.append(float(myline[0:9]))
        vals.append(float(myline[10:19]))
        vals.append(float(myline[20:29]))
        vals.append(float(myline[30:39]))
        vals.append(float(myline[40:49]))
        vals.append(float(myline[50:59]))
        vals.append(float(myline[60:69]))
        vals.append(float(myline[70:79]))
        if len(vals) != 8:
            print "unexpected number of values in line"
            sys.exit(0)
        for n in vals:
            n_pts.append(n)


    for myline in lines[z_start+1:(z_start+z_lines-1)]:
        vals = []
        vals.append(float(myline[0:9]))
        vals.append(float(myline[10:19]))
        vals.append(float(myline[20:29]))
        vals.append(float(myline[30:39]))
        vals.append(float(myline[40:49]))
        vals.append(float(myline[50:59]))
        vals.append(float(myline[60:69]))
        vals.append(float(myline[70:79]))
        if len(vals) != 8:
            print "unexpected number of values in line"
            sys.exit(0)
        for z in vals:
            z_pts.append(z)
    
    #
    # Create a standard header for files
    min_points = min(len(n_pts),len(z_pts),len(e_pts))

    h5_pgm_n = 0.0
    h5_pgm_v = 0.0
    h5_pgm_e = 0.0
    
    #
    # Do calculations needed to trim data to event time
    #
    obs_start = cosmos_time_2_datetime(starttimes[0])
    eq_start = origin_time_2_datetime(origin_time)
    tdelta = eq_start - obs_start
    if tdelta.total_seconds() > 0:
        npts = samples_to_trim(eq_start,obs_start,common_dt)
        print "Time to trim from obs:",tdelta.total_seconds()
        print "Trim data in SAC Files:",npts
    else:
        raise "Too few data points to trim ..."
    
    if datatype == 'd':
        h1 = "# 3 component displacement data from CESMD file\n"
        h3_1 = " Units: meters\n"
        pg_vals = pgms[0]
        h5_pgm_e = "# E/W PGD: %f (m) at %f secs.\n" % (pg_vals[0]/CM_PER_METER,
                                                        pg_vals[1]-tdelta.total_seconds())
        pg_vals = pgms[1]
        h5_pgm_n = "# N/S PGD: %f (m) at %f secs.\n" % (pg_vals[0]/CM_PER_METER,
                                                        pg_vals[1]-tdelta.total_seconds())
        pg_vals = pgms[2]
        h5_pgm_v = "# U/D PGD: %f (m) at %f secs.\n" % (pg_vals[0]/CM_PER_METER,
                                                        pg_vals[1]-tdelta.total_seconds())

    elif datatype == 'v':
        h1 = "# 3 component velocity data from CESMD file\n"
        h3_1 = "# Units: meters/sec\n"
        pg_vals = pgms[0]
        h5_pgm_e = "# E/W PGV: %f (m/sec) at %f secs.\n" % (pg_vals[0]/CM_PER_METER,
                                                            pg_vals[1]-tdelta.total_seconds())
        pg_vals = pgms[1]
        h5_pgm_n = "# N/W PGV: %f (m/sec) at %f secs.\n" % (pg_vals[0]/CM_PER_METER,
                                                            pg_vals[1]-tdelta.total_seconds())
        pg_vals = pgms[2]
        h5_pgm_v = "# U/D PGV: %f (m/sec) at %f secs.\n" % (pg_vals[0]/CM_PER_METER,
                                                            pg_vals[1]-tdelta.total_seconds())
     
    elif datatype == 'a':
        h1 = "# 3 component acceleration data from CESMD file\n"
        h3_1 = "# Units: meters/sec2\n"
        pg_vals = pgms[0]
        h5_pgm_e = "# E/W PGA: %f (m/sec/sec) at %f secs.\n" % (pg_vals[0]/CM_PER_METER,
                                                                pg_vals[1]-tdelta.total_seconds())
        pg_vals = pgms[1]
        h5_pgm_n = "# N/S PGA: %f (m/sec/sec) at %f secs.\n" % (pg_vals[0]/CM_PER_METER,
                                                                pg_vals[1]-tdelta.total_seconds())
        pg_vals = pgms[2]
        h5_pgm_v = "# U/D PGA: %f (m/sec/sec) at %f secs.\n" % (pg_vals[0]/CM_PER_METER,
                                                                pg_vals[1]-tdelta.total_seconds())

    else:
        raise "Invalid datatype requested %s"%(datatype)
    
    #
    # write header info
    #
    
    h2 = "# Input COSMOS V2 format file name: %s\n"%(smo_file)
    h2_1 = "# Output BBP format file name: %s\n"%(outfile_name)
    h3 = "# dt : %f\n" %(common_dt)
    h4 = "# npts : %d\n"%(min_points - npts)
    h5 = "# duration : %f\n"%(common_dt * (min_points - npts))
    h5_o = "# Event Origin time : %s\n"%(origin_time)
    h5_N = "# Data Start time: : %s\n"%(origin_time) # Previously checked that all component start
    h6 = "# Secs_After_Origin      N-S      E-W     Up-Down\n"

    f= open(outfile_name,"w")
    #print h1
    f.write(h1)
    #print h2
    f.write(h2)
    f.write(h2_1)
    f.write(h3)
    f.write(h3_1)
    f.write(h4)
    f.write(h5)
    f.write(h5_o)
    f.write(h5_N)
    f.write(h5_pgm_n)
    f.write(h5_pgm_e)
    f.write(h5_pgm_v)
    f.write(h6)

    cur_secs = 0.0
    for i in range((npts-1),min_points):
        filestr = "%f    %f    %f    %f"%(cur_secs, n_pts[i]/CM_PER_METER,
                                      e_pts[i]/CM_PER_METER, z_pts[i]/CM_PER_METER)
        #
        # This avoids writing a newline into file after last data point
        #
        if i > (npts-1):
            f.write("\n")
        f.write(filestr)
        cur_secs = cur_secs + common_dt
    f.close()
    print "File completed. Wrote BBP seismograms with samples: ",(min_points - npts)
    return outfile_name


def define_params():
    """
    Inputs: None
    Outputs: a parser configured for smo2bbp input parameters params:
    -f input smo file name:
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-e', action='store', 
                        dest='eventid', 
                        help='EventID (string - no spaces) - The earthquake observed in this input record')

    parser.add_argument('-f', action='store', 
                        dest='input_file', 
                        help='Path to input file in SMO V2 format (e.g. CE13873.V2)')

    parser.add_argument('-o', action='store', 
                        dest='origin_time', 
                        help='Earthquake Origin Time Format: YYYY:MM:DD:HH:MM:SS.S')

    parser.add_argument('-d', action='store', 
                        dest='datatype', 
                        help='Type of data output by plotter. Allowed values are a,v,d (Accel, Vel, Disp)')

    parser.add_argument('--version', action='version', version='%(prog)s 15.12.15')

    return parser


if __name__ == '__main__':
    params = define_params()
    results = params.parse_args()
    print 'input_file     =', results.input_file
    print 'event_id       =',results.eventid
    convert_cesmd2bbp(results)
    sys.exit(0)
#
# Example Usage:
# ./convert_smo2bbp.py -e LaHabra -o 2014:03:29:04:09:42.31 -f ./smo_files/CE13873.V2 -d v
#
