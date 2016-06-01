'''
Created on Oct 20, 2012

@author: maechlin
'''
import os
import sys


def make_index_html(a_indir):
    """
    Input the absolute path to a bbp output data directory. 
    There should be no subdirectories in the output data directory.
    The method outputs an index.html file that has a relative link to each file
 
     Limitations:
     This will write a hardcoded file name (index.html) to the output
     data directory, so the user must have write permission to that 
     directory of it will fail.
 
    """
    lstFiles = []
    
    #
    # Process input directory which should end in simid
    rootdir = a_indir
    #print "List of directory: %s"%(rootdir)
    
    #
    # Extract sim id from path name
    simid = os.path.basename(rootdir)
    #print simid
    #
    # Create list of files in directory
    for x in os.listdir(rootdir):
        lstFiles.append("./" + x)
    #
    #
    for path, dirs, files in os.walk(rootdir):
        #print path
        #print dirs
        #print files
        #
        # This is an alterative way to build up urls for each file
        # but is not needed for the relative paths needed for bbp
        #for file in files:
        #    lstFiles.append(os.path.join(path, file))
        pass
    #
    # Confirm there are not subdirectories. This is non-fatal but unexpected result
    #
    if len(dirs) > 0:
        print "Found at least one unexpected subdirectory in output directory: %s"%(rootdir)
        for x in dirs:
            print x
    #
    # The files in the output directory are summarized below, but
    # the correct list may change. Both the default names and the
    # type and number of files may change.
    #     
    index_file = "%s/index.html"%(rootdir)
    f = open(index_file, "w")
    f.write("<html>\n")
    f.write("<ul>")
    
    for item in lstFiles:
        splitfile = os.path.split(item)
        webpyPath = splitfile[0]
        itemName = splitfile[1]
        if item.endswith("/"):
            f.write('<li><a href=\"' + webpyPath + "/" + itemName + '\" id=\"directory\" alt=\"' + itemName + '\" target=\"viewer\">' + itemName + '</a></li>\n')
        else:
            f.write('<li><a href=\"' + webpyPath + "/" + itemName + '\" id=\"file\" alt=\"' + itemName + '\" target=\"viewer\">' + itemName + '</a></li>\n')
    
    f.write("</ul>")
    f.write("</html>\n")
    f.close()

if __name__ == '__main__':
    if len(sys.argv) < 1:
        print "Usage: directory_list.py pathname"
    #print "Testing Module: %s"%(sys.argv[0])
    sl =  "/Users/maechlin/Desktop/scec_20160522/FiniteFault-Wei2014_SmallReg/LaHabra_0.3Hz"
    make_index_html(sl)