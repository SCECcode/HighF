'''
Created on Oct 20, 2012

@author: maechlin

This method is designed to 
(1) scan a directory of cesmo observation files, and create a list of
all the .V2 files found

(2) scan a directory of synthetic files from KBO group and create a list of
all the stations for which we have matching syn and obs

(3)


'''
import os
import sys
import convert_awp2bbp as ca2b
import convert_cesmd2bbp as cc2b
import convert_gp2bbp as cgp2b
import prepare_bbpdata
import convert_bbp2sac
import subprocess

if __name__ == '__main__':
    if len(sys.argv) < 1:
        print "Usage: ./create_comparison_plots.py"
    obs_dir =  "/Users/maechlin/Desktop/LaHabra_Obs_copy"
    syn_dir = "/Users/maechlin/Desktop/sdsu_20160516_copy"
    rwg_dir = "/Users/maechlin/Desktop/rwg_20160519_copy/PntSrc_SmallReg"
    
    obs_file_list = []
    syn_file_list = []
    rwg_file_list = []
    
    obs_file_dict = {}
    combined_awp_file_dict =  {}
    combined_rwg_file_dict =  {}
    
    file_count = 0
    # Build a list of station_key, path to .V2 files
    for root, _, filenames in os.walk(obs_dir): 
        for filename in filenames:            
            if ".V2" in filename and "CHAN" not in filename:
                obs_file_list.append(os.path.join(root, filename))
                file_count = file_count + 1
                obs_file_dict[filename] = os.path.join(root,filename)
    print "Total Obs Files:",len(obs_file_list), len(obs_file_dict), file_count
    
    # Build a list of station_key, path to sdsu files, and path to obs file
    for root,_,filenames in os.walk(syn_dir):
        for filename in filenames:
            if ".dat" in filename:
                pts = os.path.splitext(filename)
                fstring = pts[0]
                no_uscore = fstring.split("_")         
                newfstring = no_uscore[0] + no_uscore[1] + ".V2"
                if newfstring in obs_file_dict:
                    matched_pair = []
                    matched_pair.append(obs_file_dict[newfstring])
                    matched_pair.append(os.path.join(root,filename))
                    combined_awp_file_dict[newfstring] = matched_pair
    
    # Build a list of station_key, rwg files
    for root,_,filenames in os.walk(rwg_dir):
        for filename in filenames:
            if ".bbp" in filename:
                pts = os.path.splitext(filename)
                fstring = pts[0]
                no_uscore = fstring.split("_")         
                newfstring = no_uscore[0] + no_uscore[1] + ".V2"
                if newfstring in obs_file_dict:
                    matched_pair = []
                    matched_pair.append(obs_file_dict[newfstring])
                    matched_pair.append(os.path.join(root,filename))
                    combined_rwg_file_dict[newfstring] = matched_pair

    #
    # Find the intersection of two dictionaries, sdsu, and rwg.
    # obs file comes from awp dict, assuming it is the same as the obs file in the rwg dataset
    # Might eliminate possiblity of error by checking that awp, and rwg obs files are the same
    intersect_dict = {}
    for item in combined_awp_file_dict.keys():
        if combined_rwg_file_dict.has_key(item):
            files_list = []
            files_list.append(combined_awp_file_dict[item][0]) # Reference the obs file in awp dict
            files_list.append(combined_awp_file_dict[item][1]) # Reference the awp file in awp dict
            files_list.append(combined_rwg_file_dict[item][1]) # Reference the rwg file in rwg dict
            intersect_dict[item] = files_list
  

    print "Total AWP Files with Matching OBS:", len(combined_awp_file_dict)
    print "Total RWG Files with Matching OBS:", len(combined_rwg_file_dict)
    print "Number of Intersects:", len(intersect_dict)

    err_file_list = []
    good_file_dict  = {}
    for key,value in intersect_dict.iteritems():
        print key,value[0],value[1],value[2]
        print "Total Syn Files with Matching Obs:", len(intersect_dict)
    
        #
        # Prepare to process these files
        # Import event information
        #
        eventid_str = "LaHabra"
        station_parts = key.split(".")
        station_id = station_parts[0]
        synfilepath = value[1]
        gpfilepath = value[2]
        origin_time = "2014-03-29T04:09:42.170Z"
        datatype = "v"
        try:
            print "Success with:",eventid_str,station_id,synfilepath,origin_time,datatype
            obsfilepath = value[0]
            out_obs_bbp = cc2b.convert_cesmd2bbp(eventid_str,obsfilepath,origin_time,datatype)
            out_awp_bbp = ca2b.convert_awp2bbp(eventid_str,station_id,synfilepath,origin_time,datatype)
            out_rwg_bbp = cgp2b.convert_gp2bbp(eventid_str,station_id,gpfilepath,origin_time,datatype)
            print out_obs_bbp,out_awp_bbp,out_rwg_bbp
            good_file_list = []
            good_file_list.append(out_obs_bbp)
            good_file_list.append(out_awp_bbp)
            good_file_list.append(out_rwg_bbp)
            good_file_dict[key] = good_file_list
        except Exception,e:
            print e
            err_file_list.append(obsfilepath)
            print "Exception with:",eventid_str,station_id,synfilepath,origin_time,datatype
            continue
        
    print "Number of good file pairs:", len(good_file_dict)
    print "Number of bad obs files:", len(err_file_list)
    for key,values in good_file_dict.iteritems():
        print key,values[0],values[1],values[2]
    #sys.exit(0)
    #
    # Setenv before calling SAC
    #
    os.environ["SACHOME"] = "/Users/maechlin/sac"
    os.environ["SACAUX"] = "/Users/maechlin/sac/aux"
    os.environ["SAC_DISPLAY_COPYRIGHT"] = "0"

    freqs = [0.5]
    #freqs = [4,3,2,1,0.5]
    
    for key,values in good_file_dict.iteritems():
        for freq in freqs:
            dt = 0.01
            f_freq = freq
            rotation_angle = 40
            file_names = []
            #
            # This first loop through the stations, converts all methods including
            # the observations to sac format.
            # Also processing is done in prepare to seismogram by filtering them
            #
            file_names.append(values[0])
            file_names.append(values[1])
            file_names.append(values[2])
            print "Preparing BBP with trim, taper, and 4 pole filter",file_names
            outfileslist = prepare_bbpdata.prepare_bbpdata(dt,f_freq,file_names)
            for newfile in outfileslist:
                print "converting bbp to sac",newfile
                convert_bbp2sac.convert_bbp2sac(newfile)
            file_names = []
            #
            # Now rotate the observed seismograms
            # This routine assumes the observations are oriented 360 and 90 degrees
            # This currently will translate each obser file into a rotated seismogram
            # at each frequency. Then the SAC files are processed like the simulation data.
            # in the future, we can rotate the observations only once, not for each freq.
            #
            # SAC Header values are:
            # IDEL IVEL - velocity in nm/sec velocity
            # CMPAZ 0 - component azimth degree clockwise frm north
            # CMPINC 90 - comoponent incident angle degrees from vertical
            obs_filename_parts = values[0].split(".")
            gram_to_rotate360 = "%s-%.2f.040.sac"%(obs_filename_parts[0],f_freq)
            print "rotating",gram_to_rotate360
            p = subprocess.Popen(['/Users/maechlin/sac/bin/sac'],
                           stdout = subprocess.PIPE,
                           stdin  = subprocess.PIPE,
                           stderr = subprocess.STDOUT )
       
            cmd = "read %s\n" % (gram_to_rotate360) 
            cmd = cmd + "chnhdr IDEP IVEL\n"
            cmd = cmd + "chnhdr CMPAZ 0\n"
            cmd = cmd + "chnhdr CMPINC 0\n"
            cmd = cmd + "writehdr\n"
            cmd = cmd + "quit\n"
            print cmd
            out = p.communicate(cmd)
            p.wait()
              
            gram_to_rotate090 = "%s-%.2f.130.sac"%(obs_filename_parts[0],f_freq)
            p = subprocess.Popen(['/Users/maechlin/sac/bin/sac'],
                          stdout = subprocess.PIPE,
                          stdin  = subprocess.PIPE,
                          stderr = subprocess.STDOUT )
            cmd = "read %s\n" % (gram_to_rotate090) 
            cmd = cmd + "chnhdr IDEP IVEL\n"
            cmd = cmd + "chnhdr CMPAZ 90\n"
            cmd = cmd + "chnhdr CMPINC 0\n"
            cmd = cmd + "writehdr\n"
            cmd = cmd + "quit\n"
            print cmd
            out = p.communicate(cmd)
            p.wait()
            print out[0]
      
            p = subprocess.Popen(['/Users/maechlin/sac/bin/sac'],
                          stdout = subprocess.PIPE,
                          stdin  = subprocess.PIPE,
                          stderr = subprocess.STDOUT )
      
            cmd = "read %s %s\n" % (gram_to_rotate360,gram_to_rotate090) 
            cmd = cmd + "rotate through %f\n" % (rotation_angle)
            cmd = cmd + "write %s %s\n" % (gram_to_rotate360,gram_to_rotate090)
            cmd = cmd + "quit\n"
            print cmd
            out = p.communicate(cmd)
            print out[0]
            p.wait()
        
            #
            # All data processing completed prior to plotting.
            # The following SAC command create final set of plots at this frequency]
            #
            print "Ready to plot station:",obs_filename_parts[0]
    
            p = subprocess.Popen(['/Users/maechlin/sac/bin/sac'],
                                     stdout = subprocess.PIPE,
                                     stdin  = subprocess.PIPE,
                                     stderr = subprocess.STDOUT )
    
            #
            # Define some station specific plotting. move externally
            # in some future version
            ##                     
            XLIM ="0 60"
            FREQ = "%f"%(f_freq)
            XLIM_FQ="5"
      
            #             if sta == "FUL":
            #                     XLIM ="0 30"
            #                     FREQ = "%f"%(f_freq)
            #                     XLIM_FQ="5"
            #             elif sta == "DLA":
            #                     XLIM ="2 30"
            #                     FREQ = "%f"%(f_freq)
            #                     XLIM_FQ="5"
            #             elif sta == "BRE":
            #                     XLIM ="2 30"
            #                     FREQ = "%f"%(f_freq)
            #                     XLIM_FQ="5"
            #             else:
            #                     raise Exception("Unknown station found %s"%(sta))
    
            #
            # remove _obs_ from filename so wildcard plots both _obs_ and _awp_
            #
            subfile_parts = obs_filename_parts[0].split("_")
            gram_to_plot040 = "%s_%s_%s_*-%.2f.040.sac"%(subfile_parts[0],subfile_parts[1],subfile_parts[2],f_freq)
            gram_to_plot130 = "%s_%s_%s_*-%.2f.130.sac"%(subfile_parts[0],subfile_parts[1],subfile_parts[2],f_freq)
            gram_to_plotver = "%s_%s_%s_*-%.2f.ver.sac"%(subfile_parts[0],subfile_parts[1],subfile_parts[2],f_freq)
    
            gram_out_plot040 = "%s-%.2f.040.pdf"%(obs_filename_parts[0],f_freq)
            gram_out_plot130 = "%s-%.2f.130.pdf"%(obs_filename_parts[0],f_freq)
            gram_out_plotver = "%s-%.2f.ver.pdf"%(obs_filename_parts[0],f_freq)
                
            fft_filename040 = "%s-%.2f.040-FFT.pdf"%(obs_filename_parts[0],f_freq)
            fft_filename130 = "%s-%.2f.130-FFT.pdf"%(obs_filename_parts[0],f_freq)
            fft_filenamever = "%s-%.2f.ver-FFT.pdf"%(obs_filename_parts[0],f_freq)            
            #
            # Read and plot 130 component FFT
            cmd = "read ./%s\n"%(gram_to_plot130)
            cmd = cmd + "color r increment list red blue black magenta\n"
            cmd = cmd + "xlim 0.1 %s\n"%(XLIM_FQ)
            cmd = cmd + "xlabel \"Frequency\"\n"
            cmd = cmd + "\"FAS\"\n"
            cmd = cmd + "loglog\n"
            cmd = cmd + "grid on\n"
            cmd = cmd + "fft\n"
            cmd = cmd + "title \"STATION %s - 130 Component\"\n"%(obs_filename_parts[0])
            cmd = cmd + "p2\n"
            cmd = cmd + "saveimg ./%s\n"%(fft_filename130)
            # Read and plot 040 component FFT
            cmd = cmd + "r ./%s\n"%(gram_to_plot040)
            cmd = cmd + "fft\n"
            cmd = cmd + "title \"STATION %s - 040 Component\"\n"%(obs_filename_parts[0])
            cmd = cmd + "p2\n"
            cmd = cmd + "saveimg ./%s\n"%(fft_filename040)
            # Read and plot ver component FFT
            cmd = cmd + "r ./%s\n"%(gram_to_plotver)
            cmd = cmd + "fft\n"
            cmd = cmd + "title \"STATION %s - VER Component\"\n"%(obs_filename_parts[0])
            cmd = cmd + "p2\n"
            cmd = cmd + "saveimg ./%s\n"%(fft_filenamever)
            # Plot 130 grams
            cmd = cmd + "read ./%s\n" % (gram_to_plot130) 
            cmd = cmd + "xlim %s\n"%(XLIM)
            cmd = cmd + "ylim ALL ALL ALL ALL\n"
            cmd = cmd + "xlabel \"Time (s)\"\n"
            cmd = cmd + "ylabel \"m/s\"\n"
            cmd = cmd + "color r\n"
            cmd = cmd + "linlin\n"
            cmd = cmd + "grid on\n"
            cmd = cmd + "title \"STATION %s - 130 component\"\n"%(obs_filename_parts[0])
            cmd = cmd + "p1\n"
            cmd = cmd + "saveimg %s\n"%(gram_out_plot130)
            cmd = cmd + "p2\n"
            cmd = cmd + "saveimg %s-%.2f-130-OVER.pdf\n"%(obs_filename_parts[0],f_freq)
            # Plot 040 grams
            cmd = cmd + "read ./%s\n" % (gram_to_plot040) 
            cmd = cmd + "title \"STATION %s - 040 component\"\n"%(obs_filename_parts[0])
            cmd = cmd + "ylim ALL ALL ALL ALL\n"
            cmd = cmd + "p1\n"
            cmd = cmd + "saveimg %s\n"%(gram_out_plot040)
            cmd = cmd + "p2\n"
            cmd = cmd + "saveimg %s-%.2f-040-OVER.pdf\n"%(obs_filename_parts[0],f_freq)
            # Plot ver grams
            cmd = cmd + "read ./%s\n"%(gram_to_plotver)
            cmd = cmd + "title \"STATION %s - VER component\"\n"%(obs_filename_parts[0])
            cmd = cmd + "ylim ALL ALL ALL ALL\n"
            cmd = cmd + "p1\n"
            cmd = cmd + "saveimg %s\n"%(gram_out_plotver)
            cmd = cmd + "p2\n"
            cmd = cmd + "saveimg %s-%.2f-VER-OVER.pdf\n"%(obs_filename_parts[0],f_freq)
            cmd = cmd + "quit\n"
            print cmd
            out = p.communicate(cmd)
            print out[0]
            p.wait()
        print "Completed all frequencies"
    print "Completed all stations"