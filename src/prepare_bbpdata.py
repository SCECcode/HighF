#!/usr/bin/env python
"""
Utility to pre-process a BBP file for comparison in SAC
$Id$
"""

# Import python modules
import os
#import sys
import numpy as np
from scipy import signal, interpolate
#import matplotlib.pyplot as plt
import sys

def read_bbp_file(bbp_file):
    """
    This function reads a BBP file and returns an array of arrays
    containing the timestamps, and the three components
    """
    times = []
    comp1 = []
    comp2 = []
    comp3 = []
    in_file = open(bbp_file, 'r')
    for line in in_file:
        line = line.strip()
        # Skip comments
        if line.startswith('#') or line.startswith('%'):
            continue
        pieces = line.split()
        pieces = [float(piece) for piece in pieces]
        times.append(pieces[0])
        comp1.append(pieces[1])
        comp2.append(pieces[2])
        comp3.append(pieces[3])
    in_file.close()

    return times, comp1, comp2, comp3

def write_bbp_file(output_file, bbp_out_data):
    """
    This function writes a bbp file
    """

    ofile = open(output_file, 'w')
    for i in range(0, len(bbp_out_data[0])):
        ofile.write("%1.9E %1.9E %1.9E %1.9E\n" %
                    (bbp_out_data[0][i], bbp_out_data[1][i],
                     bbp_out_data[2][i], bbp_out_data[3][i]))

    # All done, close everything
    ofile.close()

def get_dt(times):
    """
    This function returns the DT for a given timeseries
    """
    return (times[1] - times[0])

def bbpfilter(times, data, freq):
    """
    This function applies a low-pass filter to the data
    """
    poles = 4
    cutoff = freq
    sample_rate = 1.0 / get_dt(times)
    nyq = 0.5 * sample_rate
    normal_cutoff = cutoff / nyq

    b, a = signal.butter(poles, normal_cutoff)
    out_data = signal.filtfilt(b, a, data)

    return out_data

def interp_data(cur_times, cur_data, new_dt):
    """
    This function uses the cur_times and cur_data to interpolate
    values for new_times using the interpolate module from scipy
    """
    f = interpolate.interp1d(cur_times, cur_data)

    # Figure out new times
    new_times = []
    last_time = cur_times[-1]
    cur_time = 0.0
    while True:
        new_times.append(round(cur_time,8))
        cur_time = cur_time + new_dt
        if round(cur_time,8) > last_time:
            break
    
    new_data = []
    for new_time in new_times:
        new_data.append(float(f(new_time)))

    return new_times, new_data

def find_shortest_bbp_file(bbp_files):
    """
    This function reads a number of bbp_files and returns the largest
    timestamp of the shortest file
    """
    shortest = -1

    print "find shortest file list",bbp_files
    for bbp_file in bbp_files:
        bbp_data = read_bbp_file(bbp_file)
        bbp_times = bbp_data[0]
        if shortest == -1:
            shortest = bbp_times[-1]
            continue
        if bbp_times[-1] < shortest:
            shortest = bbp_times[-1]
            continue

    return shortest

def trim_bbp_data(input_times, input_data, seconds):
    """
    This function trims input_data so that it ends at the time specified
    """
    # Check if trimming is needed
    if input_times[-1] <= seconds:
        return input_times, input_data

    idx = next(x[0] for x in enumerate(input_times) if x[1] > seconds)
    new_times = input_times[0:idx]
    new_data = input_data[0:idx]

    return new_times, new_data

def taper_bbp_data(input_data, dt, seconds):
    """
    This function tapers the last n seconds of the input data using a hanning
    window.
    """
    npts = int(2 * seconds / dt + 1)
    window = np.hanning(npts)[-int(seconds / dt + 1):]

    # Make copy of input data
    output_data = input_data[:]

    # Taper data according to the hanning window
    for i in range(0, len(window)):
        output_data[-len(window)+i] = input_data[-len(window)+i] * window[i]

    return output_data
    
def pad_bbp_data(input_times, input_data, seconds):
    """
    This function pads bbp_data with N seconds of zeroes at the end
    """
    dt = get_dt(input_times)
    
    output_times = input_times[:]
    output_data = list(input_data[:])

    npts = int(seconds / dt)
    cur_time = input_times[-1]
    for i in range(0, npts):
        cur_time = cur_time + dt
        output_times.append(cur_time)
        output_data.append(0.0)

    return output_times, output_data

def prepare_bbpdata(n_dt,f_freq,inputfile_list):
    """
    Input 3 or more files to be included in the output plot
    new_dt filter_frequency input_file1 [input_file2 ... input_filen]
    """
    new_dt = float(n_dt)
    filter_freq = float(f_freq)
    bbp_files = inputfile_list
    for fs in bbp_files:
        print fs
            
    new_bbp_len = find_shortest_bbp_file(bbp_files)
    
    # Process all BBP files provided
    outputfilelist = []
    for bbp_file in bbp_files:
        print "preparing bbpfile",bbp_file
        # Figure out output filename
        input_base, input_ext = os.path.splitext(bbp_file)
        output_file = "%s-%.2f%s" % (input_base, filter_freq, input_ext)
        #print "outputfilename",output_file
        # Read input file
        #sys.exit(0)
        bbp_data = read_bbp_file(bbp_file)
        bbp_out_data = [[], [], [], []]
        cur_dt = get_dt(bbp_data[0])
        
        # Process each component separately
        for comp in range(1, 4):
            bbp_out_data[comp] = bbpfilter(bbp_data[0], bbp_data[comp], 10.0)
            if cur_dt != new_dt:
                # Need to interpolate
                (bbp_out_times,
                 bbp_out_data[comp]) = interp_data(bbp_data[0],
                                                   bbp_out_data[comp], new_dt)
            else:
                # Just copy current times
                bbp_out_times = bbp_data[0]
            
            # Trim bbp file to match shortest dataset
            bbp_out_times, bbp_out_data[comp] = trim_bbp_data(bbp_out_times,
                                                              bbp_out_data[comp],
                                                              new_bbp_len)
    
            # Taper timeseries
            bbp_out_data[comp] = taper_bbp_data(bbp_out_data[comp],
                                                new_dt, 2)
    
            # Pad last 5 seconds with zeroes
            bbp_out_times, bbp_out_data[comp] = pad_bbp_data(bbp_out_times,
                                                             bbp_out_data[comp], 5)
    
            bbp_out_data[comp] = bbpfilter(bbp_out_times,
                                        bbp_out_data[comp], filter_freq)
    
        bbp_out_data[0] = bbp_out_times
        write_bbp_file(output_file, bbp_out_data)
        outputfilelist.append(output_file)
    #
    # return list of new files
    return outputfilelist