import sys
import unittest
import shlex
import os
from unittest.mock import patch, MagicMock
import remove_lowres as r

epa_0008 = '''
Cycle: 12
            24401.23   21649.58      34.52 736.376770
Cycle: 13
**************************************   LAST CYCLE    ************************************************************ *

   Defocus_U   Defocus_V       Angle         CCC
    24401.23    21649.58       34.52    0.180863  Final Values

Resolution limit estimated by EPA: 3.464 

......................................  VALIDATION  ......................................
Differences from Original Values:
  RESOLUTION   Defocus_U   Defocus_V     Angle       CCC      CONVERGENCE  
  20-08A       124.42       -0.95        0.38        0.19     PERFECT        
  15-06A       128.82      -40.14        0.00        0.17     PERFECT        
  12-05A        82.43      -43.00        0.00        0.14     PERFECT        
  10-04A         4.07       -3.51       -0.37        0.09     PERFECT        
  08-03A       -45.44      -62.36        0.00        0.04     GOOD           
Processing done successfully.
'''
epa_0005 = '''
Cycle: 10
            25981.46   23524.46      37.39 717.223145
            25981.46   23524.46      37.39 717.223145
Cycle: 11
**************************************   LAST CYCLE    ************************************************************ *

   Defocus_U   Defocus_V       Angle         CCC
    25981.46    23524.46       37.39    0.176541  Final Values

Resolution limit estimated by EPA: 3.445 

......................................  VALIDATION  ......................................
Differences from Original Values:
  RESOLUTION   Defocus_U   Defocus_V     Angle       CCC      CONVERGENCE  
  20-08A        33.63       97.63        0.02        0.19     PERFECT        
  15-06A        82.03       63.89       -0.35        0.17     PERFECT        
  12-05A        50.79       36.80       -0.37        0.13     PERFECT        
  10-04A        -6.99       -5.22       -0.37        0.09     PERFECT        
  08-03A       -33.44       -6.99       -0.75        0.04     PERFECT        
Processing done successfully.
'''
ctf_starfile = '''
data_
loop_ 
_rlnVoltage #1 
_rlnDefocusU #2 
_rlnDefocusV #3 
_rlnDefocusAngle #4 
_rlnSphericalAberration #5 
_rlnDetectorPixelSize #6 
_rlnCtfFigureOfMerit #7 
_rlnCtfImage #8 
_rlnMagnification #9 
_rlnAmplitudeContrast #10 
_rlnMicrographName #11 
300.000000 33532.214844 30835.105469    36.591629     0.010000    14.000000     0.221757 Micrographs/20160126_BRCA1_GO_0001.ctf:mrc 1.346154e+05     0.100000 Micrographs/20160126_BRCA1_GO_0001.mrc
300.000000 20969.539062 18283.351562    34.964935     0.010000    14.000000     0.171006 Micrographs/20160126_BRCA1_GO_0002.ctf:mrc 1.346154e+05     0.100000 Micrographs/20160126_BRCA1_GO_0002.mrc
300.000000 29635.697266 26948.326172    37.578705     0.010000    14.000000     0.088152 Micrographs/20160126_BRCA1_GO_0091.ctf:mrc 1.346154e+05     0.100000 Micrographs/20160126_BRCA1_GO_0091.mrc 
300.000000 24767.728516 21505.787109   217.509583     0.010000    14.000000     0.169482 Micrographs/20160126_BRCA1_GO_0092.ctf:mrc 1.346154e+05     0.100000 Micrographs/20160126_BRCA1_GO_0092.mrc
'''
normal_starfile = '''
data_
loop_
_rlnMicrographName #1
_rlnCtfImage #2
_rlnDefocusU #3
_rlnDefocusV #4
_rlnDefocusAngle #5
_rlnVoltage #6
_rlnSphericalAberration #7
_rlnAmplitudeContrast #8
_rlnMagnification #9
_rlnDetectorPixelSize #10
_rlnCtfFigureOfMerit #11
Micrographs/20160126_BRCA1_GO_0001.mrc Micrographs/20160126_BRCA1_GO_0012.ctf:mrc 28820.160156 25398.894531    48.369400   300.000000     0.010000     0.100000 134615.390625    14.000000     0.086911
Micrographs/20160126_BRCA1_GO_0002.mrc Micrographs/20160126_BRCA1_GO_0018.ctf:mrc 24631.863281 25399.445312    40.226494   300.000000     0.010000     0.100000 134615.390625    14.000000     0.070064
Micrographs/20160126_BRCA1_GO_0091.mrc Micrographs/20160126_BRCA1_GO_2006.ctf:mrc 31646.394531 29142.769531    37.075066   300.000000     0.010000     0.100000 134615.390625    14.000000     0.188908
Micrographs/20160126_BRCA1_GO_0092.mrc Micrographs/20160126_BRCA1_GO_2007.ctf:mrc 23659.125000 21141.820312    34.844643   300.000000     0.010000     0.100000 134615.390625    14.000000     0.121156
'''
bad_starfile = '''
 data_

loop_
_rlnMicrographName #1
_rlnCtfImage #2
_rlnDefocusU #3
_rlnDefocusV #4
_rlnDefocusAngle #5
_rlnVoltage #6

'''

class test_get_resolution(unittest.TestCase):
    
    def setUp(self):
        with open('/tmp/name_0008_ctffind3.log', 'w') as f:
            f.write(epa_0008)
        with open('/tmp/name_0005_ctffind3.log', 'w') as f:
            f.write(epa_0005)
            
    def tearDown(self):
        if os.path.isfile('/tmp/name_0008_ctffind3.log'):
            os.remove('/tmp/name_0008_ctffind3.log')
        if os.path.isfile('/tmp/name_0005_ctffind3.log'):
            os.remove('/tmp/name_0005_ctffind3.log')
    
    def test_resolution(self):
        self.assertEqual(3.464, r.get_resolution('/tmp/name_0008_ctffind3.log'))
        self.assertEqual(3.445, r.get_resolution('/tmp/name_0005_ctffind3.log'))

class test_get_defocus(unittest.TestCase):
    
    def setUp(self):
        with open('/tmp/name_0008_ctffind3.log', 'w') as f:
            f.write(epa_0008)
        with open('/tmp/name_0005_ctffind3.log', 'w') as f:
            f.write(epa_0005)
        class container(object):
            def __init__(self, defu, defv, shells):
                self.defu = defu
                self.defv = defv
                self.shells = shells
            
    def tearDown(self):
        if os.path.isfile('/tmp/name_0008_ctffind3.log'):
            os.remove('/tmp/name_0008_ctffind3.log')
        if os.path.isfile('/tmp/name_0005_ctffind3.log'):
            os.remove('/tmp/name_0005_ctffind3.log')
            
    def test_defocus(self):
        defu, defv, out_shells = r.get_defocus('/tmp/name_0008_ctffind3.log')
        self.assertEqual(24401.23, defu)
        self.assertEqual(21649.58, defv)
        exp_shells = {'20-08A':'PERFECT', '15-06A':'PERFECT', '12-05A':'PERFECT', 
                '10-04A' : 'PERFECT', '08-03A':'GOOD'}
        self.assertEqual(exp_shells, out_shells)

class test_get_file_names(unittest.TestCase):
    
    def setUp(self):
        with open('/tmp/normal.star', 'w') as f:
            f.write(normal_starfile)        
        with open('/tmp/ctf.star', 'w') as f:
            f.write(ctf_starfile)
        with open('/tmp/bad.star', 'w') as f:
            f.write(bad_starfile)
        
    def tearDown(self):
        if os.path.isfile('/tmp/normal.star'):
            os.remove('/tmp/normal.star')
        if os.path.isfile('/tmp/ctf.star'):
            os.remove('/tmp/ctf.star')
        if os.path.isfile('/tmp/bad.star'):
            os.remove('/tmp/bad.star')
    
    def test_file_not_exists(self):
        with self.assertRaises(SystemExit):
            with patch('sys.stdout', new=MagicMock()):
                r.get_file_names('nonexistant.star')
    
    def test_normal_starfile(self):
        files = r.get_file_names('/tmp/normal.star')
        self.assertEqual(files[0],'20160126_BRCA1_GO_0001')
        self.assertEqual(files[-1],'20160126_BRCA1_GO_0092')
    
    def test_ctf_starfile(self):
        files = r.get_file_names('/tmp/ctf.star')
        self.assertEqual(files[0],'20160126_BRCA1_GO_0001')
        self.assertEqual(files[-1],'20160126_BRCA1_GO_0092')
        
    def test_bad_starfile(self):
        with self.assertRaises(TypeError):
            with patch('sys.stdout', new=MagicMock()):
                r.get_file_names('/tmp/bad.star')

class test_write_starfile(unittest.TestCase):
    
    def setUp(self):
        with open('/tmp/normal.star', 'w') as f:
            f.write(normal_starfile)        
        with open('/tmp/ctf.star', 'w') as f:
            f.write(ctf_starfile)
    
    def tearDown(self):
        if os.path.isfile('/tmp/normal.star'):
            os.remove('/tmp/normal.star')
        if os.path.isfile('/tmp/ctf.star'):
            os.remove('/tmp/ctf.star')
        if os.path.isfile('/tmp/out.star'):
            os.remove('/tmp/out.star')
    
    
    def test_no_threshold(self):
        with self.assertRaises(ValueError):
            with patch('sys.stdout', new=MagicMock()):
                r.write_starfile([], '/tmp/normal.star', '/tmp/out.star',
                                mode='resolution')
    def test_no_mode(self):
        with self.assertRaises(ValueError):
            with patch('sys.stdout', new=MagicMock()):
                r.write_starfile([], '', '', mode='', threshold = 6)
    
    def test_output(self):
        pass # to test star file output we need to run main(). Spoofing data is hard

    