**High-F Seismogram Processing Tools**
* Overview of System *

These scripts implement a simple processing system intended to create plots for our high-f activity.
The current collection of scripts are python-based. 
However, they also include a C language code that must be compiled (currently used GNU compilers). 
Also, SAC libraries available from IRIS are also required.

* How-To Operate *

The operator should put the synthetics and observations into separate directories. The directories
can have subdirectories. Each type of file Observation, RWG synthetic, SDSU syntghetic, and hercules 
synthetics should be in their own subdirectories.

Then, the user calls the top level script:
./create_comparison_plots.py


The observations directories will be searched and all occurances of .V2 files will be added
to a list of input files. During this processing stage, the code creates a dictionary with a key, that is based on the station name used
in the CESMD file name. The key can be used to find the absolute path to the input file. The CESMD file names, 
and the authoriative station in the .V2 file header may not match, especially with regards to how spaces are handled.
Spaces are removed from station names in this processing system, that is, CE_DLA will be treated as CEDLA.

The synthetics directories are searched based on the way the modelers name their files.
The sdsu scan creates a list of .dat files in it's directory path
The rwg scan creates a list of .bbp files in its directory path
The hercules scan is not currently working, but presumably the code will look for files ending in ".[integer]".
Hercules group has provided a lookup table that maps [integer] to specific station names.This lookup table is
included in the readme. However, a mapping is given to lat/lon, not to station name. A station integer, to lat/lon,
to station name is needed.

For the two working cases, SDSU and RWG, the code creates a list for which both observations and synthetics are found.
Then the system finds the intersection of stations for which observations, and synthetics are found for all cases.

Once a list of stations for which we have observations, sdsu, and rwg files, processing and plots routines are called.

First, a routine is called to convert the observations and synthetics into bbp format.
cc2b.convert_cesmd2bbp
ca2b.convert_awp2bbp
ca2b.convert_rwg2bbp

These methods accept event information as inputs so that the bbp files can be trimmed to origin time.
If the observations start after the origin time, that station generates an exception, and that station
is added to a bad_file list, and is skipped in further processing.

The code builds a good file list. This is where the modifications to add more synthetics must be made.
The code builds an array of good files, starting with the observation_data, sdsu_data, rwg_data, then
creates a dictionary with station_id as key, and path to array of the good files.
To add the hercules code, this array will be expanded to have four files in it, not three.

At this point, the code has the files ready for processing and SAC processing will be invoked.

One stage of the processing is to rotate the observation data. It is assumed that the synthetics are rotated 
off of n-s, e-w. The observation are converted into SAC and rotated using SAC to match the synthetics.
Also, the bbp files are converted to SAC format for plotting and filtering.

The code currently defines for processing for five frequencies [4,3,2,1,0.5]. 
The code loops through each frequency and re-process the bbp files for each seperately. 
This leads to duplicate processing, but avoids the need to identify the dependencies between processing stages. 
The processing will produce many files, on  the order of 10K or more if all available observations for a
event are used.
The array of processing frequencies can be reduced, down to one frequency if needed, 
to reduce to the number of files output, and for testing.

The processing of the bbp files to prepare for comparison and processing was largely defined by the group
early in highf development.  Basically both the observations, and the 
synthetics velocity files are low-passed filtered.

A summary posted was here:

1. Read all seismograms for a given station, find out largest dt, it becomes new_dt
2. Filter at 10Hz back and forward, 4 poles, using filtfilt
3. Interpolate using 1D linear to new_dt (in this case, AWP's 0.025 dt)
4. Trim longest seismograms to match the shortest one
5. Taper at the last 2 seconds: hanning with 161 points, then take 81 last values and apply this to last 81 points of each time series
6. Pad last 5 seconds with zeroes
7. Filter at 4Hz 4 poles back and forward with filtfilt
8. Plot time series and FFT using 1.25 filter frequency
9. Repeat last 2 steps with filter frequency set to 3, 2, 1, 0.5 Hz

Various aspects of the sac processing are hard coded. One example is that the length of the plots is fixed
from 0 to 60 seconds. For more detail, starting the distant plots later, might show more useful info.

* create_index_html.py *
This script inputs a path to a directory that contains files, usually the output files created above,
and it formats and outputs an html page with a relative path link to each file. 
The html file is added to the directory of files being processed. Then the directory
can be uploaded to an web-based directory, and users can view files by full file name, and click
on links to see the contents of the file. Without this index.html file, ftp clients will trucate file names.

* Limitations *
Plenty of limitations in the current distribution. Most of these limits are found in the top level
script create_comparison_plots.py. This file is being modified for new events, and when new synthetics are 
added. The subroutines are fairly stable.
Limitations include:
* The outputs files are written to the source file directory. This leads to a very large number of
files in the src directory.
* the rotation angle is hard coded into the code
* Paths to input files are hard coded. Should be moved to input configuration file
* Event parameters are hard coded in the scripts. Should be moved to external files
* Number of input synthetics is hard coded. This may be the most significant limitation. Current version,
is hard coded to process two types of synthetics. Requires a code modification to process
* The code has a hard code path to the sac executable

* Improvements *
Each time a bbp file is created, we should add a standard bbp file header with useful information.
RWG has an example of BBP files with metdata in the header, and we can expand on this, and make
it routine part of creating bbp files.

A station object might be created for each event. The station, location, obser start time, time range to plot etc
might be tracked in this single object rather than scattered through the code.

* Known problems *
RWG reports that the CE files are not correctly rotated, for the 130 