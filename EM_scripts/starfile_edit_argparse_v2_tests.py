import sys
import unittest
import shlex
import os
from unittest.mock import patch, MagicMock
import starfile_edit_argparse_v2 as s

g = s.starfleet_master.get_file_parts
z = s.starfleet_master.zerofill
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

class test_init(unittest.TestCase):
    
    def setup(self):
        sys.argv = shlex.split('test.py -i /tmp/in.star -o /tmp/out.star -k 1 2 3'+
                               ' -digits 3 -filename DMY_ABC_0001.mrc')
        with open('/tmp/in.star', 'w+b'):
            pass
        with open('/tmp/out.star', 'w+b'):
            pass
        if not os.path.isdir('/tmp/test'):
                os.mkdir('/tmp/test')
        if os.path.isdir('/tmp/nonexisting'):
                os.rmdir('/tmp/nonexisting')
                
    def tearDown(self):
        for i in ['/tmp/in.star','/tmp/out.star']:
            if os.path.isfile(i):
                os.remove(i)
        if os.path.isdir('/tmp/test'):
            os.rmdir('/tmp/test')
                    
    def test_nonexist_microg_folder_and_not_force(self):
        sys.argv += shlex.split('-image_folder nonexisting/')
        with self.assertRaises(IOError):
            s.starfleet_master(sys.argv)
    
    def test_nonexist_microg_folder_and_force(self):
        sys.argv += shlex.split('-image_folder nonexisting/ -f')
        with open('/tmp/in.star', 'w+b'):
            pass
        obj = s.starfleet_master(sys.argv)
        self.assertEqual(1, obj.check)
    
class test_args_check(unittest.TestCase):
         
    def setUp(self):
        sys.argv = shlex.split('test.py -i /tmp/in.star -o /tmp/out.star -k 1 2 3'+
                               ' -digits 3 -filename DMY_ABC_0001.mrc')
        with open('/tmp/in.star', 'w+b'):
            pass
        with open('/tmp/out.star', 'w+b'):
            pass
        if not os.path.isdir('/tmp/test'):
            os.mkdir('/tmp/test')
        if os.path.isdir('/tmp/nonexisting'):
            os.rmdir('/tmp/nonexisting')
             
    def tearDown(self):
        for i in ['/tmp/in.star','/tmp/out.star']:
            if os.path.isfile(i):
                os.remove(i)
        if os.path.isdir('/tmp/test'):
            os.rmdir('/tmp/test/')
        
    def test_input_file_not_exists(self):
        if os.path.isfile('/tmp/in.star'):
            os.remove('/tmp/in.star')
        with self.assertRaises(IOError):
            s.starfleet_master(sys.argv)
     
    def test_starfile_out_exists_no_overwrite(self):
        class _starfleet_mocked(s.starfleet_master):
            def __init__(self, *args, **kwargs):
                self.f = False #injecting the -f flag
                super().__init__(*args, **kwargs)
        with self.assertRaises(SystemExit):
            with patch('sys.stdout', new=MagicMock()):
                _starfleet_mocked(sys.argv)
     
    def test_starfile_out_exists_and_overwrite(self):
        class _starfleet_mocked(s.starfleet_master):
            def __init__(self, *args, **kwargs):
                self.f = True #injecting the -f flag
                super().__init__(*args, **kwargs)
        self.assertTrue(_starfleet_mocked(sys.argv).check)
         
    def test_move_no_destination(self):
        os.remove('/tmp/out.star')
        class _starfleet_mocked(s.starfleet_master):
            def __init__(self, *args, **kwargs):
                self.move = '/tmp/nonexisting'
                self.f = False
                super().__init__(*args, **kwargs)
        pos = sys.argv.index('-k') #hard patching remove mode for this test
        sys.argv[pos] = '-r'
        with self.assertRaises(IOError):
            with patch('sys.stdout', new=MagicMock()):
                _starfleet_mocked(sys.argv)
    
    def test_move_no_destination_force(self):
        os.remove('/tmp/out.star')
        class _starfleet_mocked(s.starfleet_master):
            def __init__(self, *args, **kwargs):
                self.move = '/tmp/nonexisting'
                self.f = True 
                super().__init__(*args, **kwargs)
        pos = sys.argv.index('-k') #hard patching remove mode for this test
        sys.argv[pos] = '-r'
        _ = _starfleet_mocked(sys.argv)
        self.assertTrue(os.path.isdir(_.move))

    def test_move_wrong_mode(self):
        os.remove('/tmp/out.star')
        class _starfleet_mocked(s.starfleet_master):
            def __init__(self, *args, **kwargs):
                self.move = '/tmp/nonexisting'
                self.f = True 
                super().__init__(*args, **kwargs)
        #mode is 'k' from setUp()
        with self.assertRaises(ValueError):
            with patch('sys.stdout', new=MagicMock()):
                _starfleet_mocked(sys.argv)
    
    def test_list_in_parsed_arguments(self):
        os.remove('/tmp/out.star')
        self.assertEqual(['001','002','003'], 
                         s.starfleet_master(sys.argv).lst)
        
class test_get_file_parts(unittest.TestCase):
     
    def test_normal_starfile_line(self):
        line =  'Micrographs/20160126_BRCA1_GO_0001.mrc Micrographs/20160126_BRCA1_GO_0001.ctf ... 6911'
        self.assertEqual(g(line), ('20160126_BRCA1_GO_0001',
                                                  '20160126_BRCA1_GO_', '0001'))
    def test_ctf_starfile_line(self):
        line = '300 ... 0.2 Micrographs/20160126_BRCA1_GO_0001.ctf:mrc 1 2 Micrographs/20160126_BRCA1_GO_0001.mrc'
        self.assertEqual(g(line), ('20160126_BRCA1_GO_0001',
                                                  '20160126_BRCA1_GO_', '0001'))
    def test_header_line(self):
        line = '_rlnMicrographName #1\m'
        self.assertEqual((0,0,0), g(line))
 
class test_zerofill(unittest.TestCase):
         
    def test_string_list(self):
        lst = [1,2,3]
        digits = 3
        self.assertEqual(['001','002','003'], z(lst, digits))
     
    def test_integer_list(self):
        lst = [1,2,3]
        digits = 3
        self.assertEqual(['001','002','003'], z(lst, digits))
        
    def test_empty_list(self):
        lst = []
        digits = 3
        self.assertEqual([], z(lst, digits))

class test_read_star(unittest.TestCase):
    
    def setUp(self):
        self.normal_header = '''
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
'''
        self.ctf_header = '''
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
'''
        self.ctf_files = {'0001': '300.000000 33532.214844 30835.105469    36.591629     0.010000    14.000000     0.221757 Micrographs/20160126_BRCA1_GO_0001.ctf:mrc 1.346154e+05     0.100000 Micrographs/20160126_BRCA1_GO_0001.mrc\n',
                      '0002': '300.000000 20969.539062 18283.351562    34.964935     0.010000    14.000000     0.171006 Micrographs/20160126_BRCA1_GO_0002.ctf:mrc 1.346154e+05     0.100000 Micrographs/20160126_BRCA1_GO_0002.mrc\n',
                      '0091': '300.000000 29635.697266 26948.326172    37.578705     0.010000    14.000000     0.088152 Micrographs/20160126_BRCA1_GO_0091.ctf:mrc 1.346154e+05     0.100000 Micrographs/20160126_BRCA1_GO_0091.mrc\n',
                      '0092': '300.000000 24767.728516 21505.787109   217.509583     0.010000    14.000000     0.169482 Micrographs/20160126_BRCA1_GO_0092.ctf:mrc 1.346154e+05     0.100000 Micrographs/20160126_BRCA1_GO_0092.mrc\n'}
        self.normal_files = {'0001':'Micrographs/20160126_BRCA1_GO_0001.mrc Micrographs/20160126_BRCA1_GO_0012.ctf:mrc 28820.160156 25398.894531    48.369400   300.000000     0.010000     0.100000 134615.390625    14.000000     0.086911\n',
                             '0002':'Micrographs/20160126_BRCA1_GO_0002.mrc Micrographs/20160126_BRCA1_GO_0018.ctf:mrc 24631.863281 25399.445312    40.226494   300.000000     0.010000     0.100000 134615.390625    14.000000     0.070064\n',
                             '0091':'Micrographs/20160126_BRCA1_GO_0091.mrc Micrographs/20160126_BRCA1_GO_2006.ctf:mrc 31646.394531 29142.769531    37.075066   300.000000     0.010000     0.100000 134615.390625    14.000000     0.188908\n',
                             '0092':'Micrographs/20160126_BRCA1_GO_0092.mrc Micrographs/20160126_BRCA1_GO_2007.ctf:mrc 23659.125000 21141.820312    34.844643   300.000000     0.010000     0.100000 134615.390625    14.000000     0.121156\n'}     
    
    def tearDown(self):
            files = ['/tmp/in.star', '/tmp/out.star']
            for i in files:
                if os.path.isfile(i):
                    os.remove(i)
    
    def test_normal_starfile_in(self):
        self.maxDiff = None
        sys.argv = shlex.split('test.py -i /tmp/in.star -o /tmp/out.star -k 1'+
                               ' -digits 3 -filename 20160126_BRCA1_GO_0001.mrc')
        with open('/tmp/in.star', 'w') as f:
            f.write(normal_starfile)
        obj = s.starfleet_master(sys.argv)
        h,f = obj.read_star()
        self.assertEqual(self.normal_header, ''.join(obj.header))
        self.assertEqual(self.normal_header, ''.join(h))
        self.assertEqual(self.normal_files, obj.files_in)
        self.assertEqual(self.normal_files, f)
    
    def test_ctf_starfile_in(self):
        
        sys.argv = shlex.split('test.py -i /tmp/in.star -o /tmp/out.star -k 1'+
                               ' -digits 4 -filename 20160126_BRCA1_GO_0001.mrc')
        with open('/tmp/in.star', 'w') as f:
            f.write(ctf_starfile)
        obj = s.starfleet_master(sys.argv)
        h,f = obj.read_star()
        self.assertEqual(self.ctf_header, ''.join(obj.header))
        self.assertEqual(self.ctf_header, ''.join(h))
        self.assertEqual(self.ctf_files, obj.files_in)
        self.assertEqual(self.ctf_files, f)
        
    def test_malformed_starfile(self):
        sys.argv = shlex.split('test.py -i /tmp/in.star -o /tmp/out.star -k 1'+
                               ' -digits 3 -filename 20160126_BRCA1_GO_0001.mrc')
        with open('/tmp/in.star', 'w') as f:
            f.write(ctf_starfile)
            f.write('This is a wrong line')
        obj = s.starfleet_master(sys.argv)
        with self.assertRaises(ValueError):
            obj.read_star()

class test_write_file(unittest.TestCase):
     
    def setUp(self):
        self.maxDiff = None
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
        l = ['/tmp/in.star','/tmp/out.star']
        for file in l:
            if os.path.isfile(file):
                os.remove(file)
         
    def test_keep_mode_normal_starfile(self):
        sys.argv = shlex.split('test.py -i /tmp/in.star -o /tmp/out.star -k 1 2'+
                               ' -digits 4 -filename 20160126_BRCA1_GO_0001.mrc')
        with open('/tmp/in.star', 'w') as f:
            f.write(normal_starfile)
        obj = s.starfleet_master(sys.argv)
        obj.read_star()
        obj.write_star()
        with open (obj.o, 'r') as f:
            self.assertMultiLineEqual(f.read(), self.exp_normal_starfile)
     
    def test_remove_mode_normal_starfile(self):
        sys.argv = shlex.split('test.py -i /tmp/in.star -o /tmp/out.star -r 91 92'+
                               ' -digits 4 -filename 20160126_BRCA1_GO_0001.mrc')
        with open('/tmp/in.star', 'w') as f:
            f.write(normal_starfile)
        obj = s.starfleet_master(sys.argv)
        obj.read_star()
        obj.write_star()
        with open(obj.o, 'r') as f:
            self.assertMultiLineEqual(f.read(), self.exp_normal_starfile)
    
    def test_keep_mode_ctf_starfile(self):
        sys.argv = shlex.split('test.py -i /tmp/in.star -o /tmp/out.star -k 1 2'+
                               ' -digits 4 -filename 20160126_BRCA1_GO_0001.mrc')
        with open('/tmp/in.star', 'w') as f:
            f.write(ctf_starfile)
        obj = s.starfleet_master(sys.argv)
        obj.read_star()
        obj.write_star()
        with open (obj.o, 'r') as f:
            self.assertMultiLineEqual(f.read(), self.exp_ctf_starfile)
     
    def test_remove_mode_ctf_starfile(self):
        sys.argv = shlex.split('test.py -i /tmp/in.star -o /tmp/out.star -r 91 92'+
                               ' -digits 4 -filename 20160126_BRCA1_GO_0001.mrc')
        with open('/tmp/in.star', 'w') as f:
            f.write(ctf_starfile)
        obj = s.starfleet_master(sys.argv)
        obj.read_star()
        obj.write_star()
        with open(obj.o, 'r') as f:
            self.assertMultiLineEqual(f.read(), self.exp_ctf_starfile)
#             
#     def test_keep_mode_ctf_starfile(self):
#         add = ['1','2']
#         s.write_file(self.ctf_starfile_in, self.starfile_out, 
#                      self.filename, self.digits, add, mode='k')
#         with open(self.starfile_out, 'r') as f:
#             self.assertMultiLineEqual(f.read(), self.exp_ctf_starfile)
#             
#     def test_remove_mode_ctf_starfile(self):
#         remove = s.zerofill(['91','092'], 4)
#         s.write_file(self.ctf_starfile_in, self.starfile_out, 
#                      self.filename, self.digits, remove, mode='r')
#         with open(self.starfile_out, 'r') as f:
#             self.assertMultiLineEqual(f.read(), self.exp_ctf_starfile)
#     
#     def test_moving(self):
#         self.assertEqual(0,1)
#
        
# class test_run_as_module(unittest.TestCase):
#     
#     def setUp(self):
#         self.starfile_in = '/tmp/in.star'
#         self.starfile_out = '/tmp/out.star'
#         self.filename = '123_BRCA1_001.mrc'
#         self.digits = 4
#         self.star_in = open('/tmp/in.star', 'w+b')
#         self.star_out = open('/tmp/out.star', 'w+b')
#         
#     def tearDown(self):
#         if os.path.isfile('/tmp/in.star'):
#             os.remove('/tmp/in.star')
#         if os.path.isfile('/tmp/out.star'):
#             os.remove('/tmp/out.star')
#         
#     def test_no_mode(self):
#         with self.assertRaises(ValueError):
#             s.run_as_module(self.starfile_in, self.starfile_out,
#                 self.filename, self.digits, [1,2,3], None, force=True)
#     
#     def test_no_lst(self):
#         with self.assertRaises(ValueError):
#             s.run_as_module(self.starfile_in, self.starfile_out,
#                 self.filename, self.digits, [], mode='k', force=True)
#             
#     def test_class_setup(self):
#         _, self.argv = s.run_as_module(self.starfile_in, self.starfile_out,
#                 self.filename, self.digits, [1,2,3], mode='k', force=True)
#         self.assertTrue(hasattr(self.argv, 'i'))
#         self.assertTrue(hasattr(self.argv, 'o'))
#         self.assertTrue(hasattr(self.argv, 'filename'))
#         self.assertTrue(hasattr(self.argv, 'digits'))
#         self.assertTrue(hasattr(self.argv, 'f'))
#         self.assertTrue(hasattr(self.argv, 'k'))
#         self.assertEqual(self.argv.k, [1,2,3])
#         _, self.argv2 = s.run_as_module(self.starfile_in, self.starfile_out,
#                 self.filename, self.digits, [1,2,3], mode='r', force=True)
#         self.assertEqual(self.argv2.r, [1,2,3])
#         

         

# 
# class test_check_all_exist(unittest.TestCase):
#     
#     def setUp(self):
#         #star1 = normal starfile #star2 = ctf corrected starfile
#         with open('/tmp/star1.star', 'w') as f:
#             f.write(normal_starfile)        
#         with open('/tmp/star2.star', 'w') as f:
#             f.write(ctf_starfile)
#         with open('/tmp/bad.star', 'w') as f:
#             f.write(bad_starfile)
#         
#     def tearDown(self):
#         if os.path.isfile('/tmp/star1.star'):
#             os.remove('/tmp/star1.star')
#         if os.path.isfile('/tmp/star2.star'):
#             os.remove('/tmp/star2.star')
#         if os.path.isfile('/tmp/bad.star'):
#             os.remove('/tmp/bad.star')
#     
#     def test_yes_normal_starfile(self):
#         self.assertTrue(s.check_all_exist('/tmp/star1.star', 
#             '20160126_BRCA1_GO_0001.mrc', s.zerofill([1,2,91,92], 4)))
#     
#     def test_no_normal_starfile(self):
#         self.assertFalse(s.check_all_exist('/tmp/star1.star', 
#             '20160126_BRCA1_GO_0001.mrc', s.zerofill([1,2,91,93], 4)))
#     
#     def test_yes_ctf_starfile(self):
#         self.assertTrue(s.check_all_exist('/tmp/star1.star', 
#             '20160126_BRCA1_GO_0001.mrc', s.zerofill([1,2,91,92], 4)))
#     
#     def test_no_ctf_starfile(self):
#         self.assertFalse(s.check_all_exist('/tmp/star1.star', 
#             '20160126_BRCA1_GO_0001.mrc', s.zerofill([1,2,91,93], 4)))
#     
#     def test_bad_starfile(self):
#         self.assertFalse(s.check_all_exist('/tmp/star1.star', 
#             '20160126_BRCA1_GO_0001.mrc', s.zerofill([1,2,91,93], 4)))
# 
# class test_get_filenumbers(unittest.TestCase):
#     
#     def setUp(self):
#         with open('/tmp/digits', 'w') as f:
#             f.write('1,2,3')
#         with open('/tmp/range', 'w') as f:
#             f.write('1-3')
#         with open('/tmp/mix', 'w') as f:
#             f.write('1,2,3-5,blabla')
#     
#     def tearDown(self):
#         files = ['digits', 'ranges', 'mix']
#         for f in files:
#             name = '/tmp/{}'.format(f)
#             if os.path.isfile(name):
#                 os.remove(name)
#     
#     def test_range(self):
#         self.assertEqual(['1','2','3'], 
#                          s.get_filenumbers('/tmp/range'))
#     
#     def test_digits(self):
#         self.assertEqual(['1','2','3'],
#                          s.get_filenumbers('/tmp/digits'))
#         
#     def test_mix(self):
#         self.assertEqual(['1','2','3','4','5'],
#                          s.get_filenumbers('/tmp/mix'))
# 
# class test_move_file(unittest.TestCase):
#     
#     def setUp(self):
#         with open('/tmp/star1.star', 'w') as f:
#             f.write(normal_starfile)
#         
#     def tearDown(self):
#         if os.path.isfile('/tmp/star1.star'):
#             os.remove('/tmp/star1.star')
    
            