'''
Created on Apr 20, 2016

@author: maechlin
'''
import unittest
import os

class Test(unittest.TestCase):


    def testName(self):
        os.system("../src/create_highf.py LaHabra")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()