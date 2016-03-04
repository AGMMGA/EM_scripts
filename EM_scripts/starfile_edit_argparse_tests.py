import sys
import unittest
import shlex
import os
from unittest.mock import patch, MagicMock

import starfile_edit_argparse as s

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

class test_args_check(unittest.TestCase):
         
    def setUp(self):
        sys.argv = shlex.split('test.py -i /tmp/in.star -o /tmp/out.star -k 1 2 3 -filename=123_BRCA1_001.mrc -digits 4 -f')
        self.star_in = open('/tmp/in.star', 'w+b')
        self.star_out = open('/tmp/out.star', 'w+b')
        self.parsed = s.parse(sys.argv)
        os.mkdir('/tmp/test')
        
    def tearDown(self):
        if os.path.isfile('/tmp/in.star'):
            os.remove('/tmp/in.star')
        if os.path.isfile('/tmp/out.star'):
            os.remove('/tmp/out.star')
        if os.path.isdir('/tmp/test'):
            os.rmdir('/tmp/test/')

    def test_input_file_not_exists(self):
        if os.path.isfile('/tmp/in.star'):
            os.remove('/tmp/in.star')
        with self.assertRaises(IOError):
            s._args_check(self.parsed)
    
    def test_starfile_out_exists_no_overwrite(self):
        self.parsed.f = False
        # out file exists from setup
        with self.assertRaises(SystemExit):
            with patch('sys.stdout', new=MagicMock()):
                s._args_check(self.parsed)
    
    def test_starfile_out_exists_and_overwrite(self):
        self.parsed.f=True
        self.assertTrue(s._args_check(self.parsed))
        
    def test_list_in_parsed_arguments(self):
        self.assertEqual([1,2,3], self.parsed.k)
    
    def test_move_nonexisting_folder(self):
        self.parsed.move = '/nonexisting/folder/'
        self.parsed.mode = 'r'
        with self.assertRaises(IOError):
            s._args_check(self.parsed)
    
    def test_move_not_remove_mode(self):
        self.parsed.move = '/tmp/test'
        self.parsed.mode = 'k'
        with self.assertRaises(ValueError):
            s._args_check(self.parsed)
        
class test_get_filename_from_star(unittest.TestCase):
    
    def setUp(self):
        with open('/tmp/star1.star', 'w') as f:
            f.write(normal_starfile)        
        with open('/tmp/star2.star', 'w') as f:
            f.write(ctf_starfile)
        with open('/tmp/bad.star', 'w') as f:
            f.write(bad_starfile)
        
    def tearDown(self):
        if os.path.isfile('/tmp/star1.star'):
            os.remove('/tmp/star1.star')
        if os.path.isfile('/tmp/star2.star'):
            os.remove('/tmp/star2.star')
        if os.path.isfile('/tmp/bad.star'):
            os.remove('/tmp/bad.star')
        
    def test_normal_starfile(self):
        self.assertEqual('20160126_BRCA1_GO_0001.mrc', 
             s.get_filename_from_star('/tmp/star1.star'))
    
    def test_ctf_starfile(self):
        self.assertEqual('20160126_BRCA1_GO_0001.mrc', 
             s.get_filename_from_star('/tmp/star2.star'))
        
    def test_bad_starfile(self):
        with self.assertRaises(ValueError): 
            s.get_filename_from_star('/tmp/bad.star')

class test_run_as_module(unittest.TestCase):
    
    def setUp(self):
        self.starfile_in = '/tmp/in.star'
        self.starfile_out = '/tmp/out.star'
        self.filename = '123_BRCA1_001.mrc'
        self.digits = 4
        self.star_in = open('/tmp/in.star', 'w+b')
        self.star_out = open('/tmp/out.star', 'w+b')
        
    def tearDown(self):
        if os.path.isfile('/tmp/in.star'):
            os.remove('/tmp/in.star')
        if os.path.isfile('/tmp/out.star'):
            os.remove('/tmp/out.star')
        
    def test_no_mode(self):
        with self.assertRaises(ValueError):
            s.run_as_module(self.starfile_in, self.starfile_out,
                self.filename, self.digits, [1,2,3], None, force=True)
    
    def test_no_lst(self):
        with self.assertRaises(ValueError):
            s.run_as_module(self.starfile_in, self.starfile_out,
                self.filename, self.digits, [], mode='k', force=True)
            
    def test_class_setup(self):
        _, self.argv = s.run_as_module(self.starfile_in, self.starfile_out,
                self.filename, self.digits, [1,2,3], mode='k', force=True)
        self.assertTrue(hasattr(self.argv, 'i'))
        self.assertTrue(hasattr(self.argv, 'o'))
        self.assertTrue(hasattr(self.argv, 'filename'))
        self.assertTrue(hasattr(self.argv, 'digits'))
        self.assertTrue(hasattr(self.argv, 'f'))
        self.assertTrue(hasattr(self.argv, 'k'))
        self.assertEqual(self.argv.k, [1,2,3])
        _, self.argv2 = s.run_as_module(self.starfile_in, self.starfile_out,
                self.filename, self.digits, [1,2,3], mode='r', force=True)
        self.assertEqual(self.argv2.r, [1,2,3])
        
class test_zerofill(unittest.TestCase):
    
    def test_string_list(self):
        lst = ['1','2','3']
        digits = 3
        self.assertEqual(['001','002','003'], s.zerofill(lst, digits))
    
    def test_integer_list(self):
        lst = [1,2,3]
        digits = 3
        self.assertEqual(['001','002','003'], s.zerofill(lst, digits))
    
    def test_empty_list(self):
        lst = []
        digits = 3
        self.assertEqual([], s.zerofill(lst, digits))

class test_write_file(unittest.TestCase):
    
    def setUp(self):
        self.normal_starfile_in = '/tmp/star1.star'
        self.ctf_starfile_in = '/tmp/star2.star'
        self.starfile_out = '/tmp/out.star'
        self.filename = '20160126_BRCA1_GO_0001.mrc'
        self.digits = 4
        with open('/tmp/star1.star', 'w') as f:
            f.write(normal_starfile)        
        with open('/tmp/star2.star', 'w') as f:
            f.write(ctf_starfile)
        self.exp_normal_starfile = '''
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
'''
        
        self.exp_ctf_starfile = '''
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
'''

    def tearDown(self):
        if os.path.isfile('/tmp/star1.star'):
            os.remove('/tmp/star1.star')
        if os.path.isfile('/tmp/star2.star'):
            os.remove('/tmp/star2.star')
        if os.path.isfile('/tmp/out.star'):
            os.remove('/tmp/out.star')
        
    def test_keep_mode_normal_starfile(self):
        add = ['1','2']
        s.write_file(self.normal_starfile_in, self.starfile_out, 
                     self.filename, self.digits, add, mode='k')
        with open(self.starfile_out, 'r') as f:
            self.assertMultiLineEqual(f.read(), self.exp_normal_starfile)
    
    def test_remove_mode_normal_starfile(self):
        remove = s.zerofill(['91','092'], 4)
        s.write_file(self.normal_starfile_in, self.starfile_out, 
                     self.filename, self.digits, remove, mode='r')
        with open(self.starfile_out, 'r') as f:
            self.assertMultiLineEqual(f.read(), self.exp_normal_starfile)
            
    def test_keep_mode_ctf_starfile(self):
        add = ['1','2']
        s.write_file(self.ctf_starfile_in, self.starfile_out, 
                     self.filename, self.digits, add, mode='k')
        with open(self.starfile_out, 'r') as f:
            self.assertMultiLineEqual(f.read(), self.exp_ctf_starfile)
            
    def test_remove_mode_ctf_starfile(self):
        remove = s.zerofill(['91','092'], 4)
        s.write_file(self.ctf_starfile_in, self.starfile_out, 
                     self.filename, self.digits, remove, mode='r')
        with open(self.starfile_out, 'r') as f:
            self.assertMultiLineEqual(f.read(), self.exp_ctf_starfile)
    
    def test_moving(self):
        self.assertEqual(0,1)
        
class test_get_file_parts(unittest.TestCase):
    
    def test_normal_starfile_line(self):
        line =  'Micrographs/20160126_BRCA1_GO_0001.mrc Micrographs/20160126_BRCA1_GO_0001.ctf ... 6911'
        self.assertEqual(s.get_file_parts(line), ('20160126_BRCA1_GO_0001',
                                                  '20160126_BRCA1_GO_', '0001'))
    def test_ctf_starfile_line(self):
        line = '300 ... 0.2 Micrographs/20160126_BRCA1_GO_0001.ctf:mrc 1 2 Micrographs/20160126_BRCA1_GO_0001.mrc'
        self.assertEqual(s.get_file_parts(line), ('20160126_BRCA1_GO_0001',
                                                  '20160126_BRCA1_GO_', '0001'))
    def header_line(self):
        line = '_rlnMicrographName #1\m'
        self.assertEqual((0,0,0), s.get_file_parts(line))

class test_check_all_exist(unittest.TestCase):
    
    def setUp(self):
        #star1 = normal starfile #star2 = ctf corrected starfile
        with open('/tmp/star1.star', 'w') as f:
            f.write(normal_starfile)        
        with open('/tmp/star2.star', 'w') as f:
            f.write(ctf_starfile)
        with open('/tmp/bad.star', 'w') as f:
            f.write(bad_starfile)
        
    def tearDown(self):
        if os.path.isfile('/tmp/star1.star'):
            os.remove('/tmp/star1.star')
        if os.path.isfile('/tmp/star2.star'):
            os.remove('/tmp/star2.star')
        if os.path.isfile('/tmp/bad.star'):
            os.remove('/tmp/bad.star')
    
    def test_yes_normal_starfile(self):
        self.assertTrue(s.check_all_exist('/tmp/star1.star', 
            '20160126_BRCA1_GO_0001.mrc', s.zerofill([1,2,91,92], 4)))
    
    def test_no_normal_starfile(self):
        self.assertFalse(s.check_all_exist('/tmp/star1.star', 
            '20160126_BRCA1_GO_0001.mrc', s.zerofill([1,2,91,93], 4)))
    
    def test_yes_ctf_starfile(self):
        self.assertTrue(s.check_all_exist('/tmp/star1.star', 
            '20160126_BRCA1_GO_0001.mrc', s.zerofill([1,2,91,92], 4)))
    
    def test_no_ctf_starfile(self):
        self.assertFalse(s.check_all_exist('/tmp/star1.star', 
            '20160126_BRCA1_GO_0001.mrc', s.zerofill([1,2,91,93], 4)))
    
    def test_bad_starfile(self):
        self.assertFalse(s.check_all_exist('/tmp/star1.star', 
            '20160126_BRCA1_GO_0001.mrc', s.zerofill([1,2,91,93], 4)))

class test_get_filenumbers(unittest.TestCase):
    
    def setUp(self):
        with open('/tmp/digits', 'w') as f:
            f.write('1,2,3')
        with open('/tmp/range', 'w') as f:
            f.write('1-3')
        with open('/tmp/mix', 'w') as f:
            f.write('1,2,3-5,blabla')
    
    def tearDown(self):
        files = ['digits', 'ranges', 'mix']
        for f in files:
            name = '/tmp/{}'.format(f)
            if os.path.isfile(name):
                os.remove(name)
    
    def test_range(self):
        self.assertEqual(['1','2','3'], 
                         s.get_filenumbers('/tmp/range'))
    
    def test_digits(self):
        self.assertEqual(['1','2','3'],
                         s.get_filenumbers('/tmp/digits'))
        
    def test_mix(self):
        self.assertEqual(['1','2','3','4','5'],
                         s.get_filenumbers('/tmp/mix'))

class test_move_file(unittest.TestCase):
    
    def setUp(self):
        with open('/tmp/star1.star', 'w') as f:
            f.write(normal_starfile)
        
    def tearDown(self):
        if os.path.isfile('/tmp/star1.star'):
            os.remove('/tmp/star1.star')
            