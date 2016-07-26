import os
import glob
import unittest
import tempfile
import shutil
import shlex
import sys
from pprint import pprint
from unittest.mock import patch
from Mass_rename_micrographs_argparse import Micrograph_renamer as m

class test_rename_files(unittest.TestCase):
    
    def setUp(self):
        self.files  = ['badname_1.mrc', 'badname_2.mrc', 'badname_3.mrc']
        self.frames = ['{}_frame{}.mrc'.format(i.split('.mrc')[0], str(j)) 
                       for i in self.files
                       for j in range(2)]
        self.tempdir = tempfile.mkdtemp()
        #expected results
        self.frame_suffix = '_frame#'
        self.exp_integrated = [os.path.join(self.tempdir, 'integrated', i) for i in self.files]
        self.exp_frames = [os.path.join(self.tempdir, 'frames', (i + self.frame_suffix)) 
                           for i in self.files]
        for f in (self.files + self.frames):
            with open(os.path.join(self.tempdir,f),'w') as f:
                pass
    
    def tearDown(self):
        shutil.rmtree(self.tempdir,ignore_errors=True)
        
        
    def test_normal_operations(self):
        testargs = ('foo.py -input_dir {temp} -output_dir {temp} -filename new_#.mrc'
                    ' -frames_suffix {frame} -EPU_image_pattern * -n_frames 2')
        testargs = testargs.format(temp = self.tempdir, frame = self.frame_suffix)
        with patch('sys.argv', testargs.split()):
            obj = m()
            frames, integrated = obj.find_mrc_files(obj.input_dir, obj.EPU_image_pattern,
                                                obj.frames_suffix)
        self.assertEqual(integrated.sort(), self.exp_integrated.sort())
        self.assertEqual(frames.sort(), self.exp_frames.sort())
        obj.rename_files(frames, integrated)
        
    def test_missing_frames(self):
        '''
        removing one frame for image 1 
        the remaining frame should end up in missing frames;
        the corresponding image in orphan images
        '''
        os.remove(os.path.join(self.tempdir, ('badname_1_frame0.mrc')))
        # adding one orphan frame (no parent image)
        with open(os.path.join(self.tempdir, 'badname_5_frame0.mrc'), 'w'):
            pass
        testargs = ('foo.py -input_dir {temp} -output_dir {temp} -filename new_#.mrc'
                    ' -frames_suffix {frame} -EPU_image_pattern * -n_frames 2')
        testargs = testargs.format(temp = self.tempdir, frame = self.frame_suffix)
        with patch('sys.argv', testargs.split()):
            obj = m()
            frames, integrated = obj.find_mrc_files(obj.input_dir, obj.EPU_image_pattern,
                                                obj.frames_suffix)
        
            obj.rename_files(frames, integrated)
        missing_frames = len(glob.glob(os.path.join(self.tempdir, 'missing_frames', '*.mrc')))
        orphan_frames = len(glob.glob(os.path.join(self.tempdir, 'orphan_frames', '*.mrc')))
        orphan_images = len(glob.glob(os.path.join(self.tempdir, 'orphan_integrated', '*.mrc')))
        frames = len(glob.glob(os.path.join(self.tempdir, 'frames', '*.mrc')))
        integrated = len(glob.glob(os.path.join(self.tempdir, 'integrated', '*.mrc')))
        self.assertEqual(missing_frames, 1)
        self.assertEqual(orphan_frames, 1)
        self.assertEqual(orphan_images, 1)
        self.assertEqual(frames, 4)
        self.assertEqual(integrated, 2)
                                  
class test_find_files(unittest.TestCase):
    
    def setUp(self):
        self.files  = ['badname_1.mrc', 'badname_2.mrc', 'badname_3.mrc']
        self.frames = ['{}_frame{}.mrc'.format(i.split('.mrc')[0], str(j)) 
                       for i in self.files
                       for j in range(7)]
        self.tempdir = tempfile.mkdtemp()
        #expected results
        self.frame_suffix = '_frame#'
        self.exp_integrated = [os.path.join(self.tempdir, i) for i in self.files]
        self.exp_frames = [os.path.join(self.tempdir, (i + self.frame_suffix)) 
                           for i in self.files]
        for f in (self.files + self.frames):
            with open(os.path.join(self.tempdir,f),'w') as f:
                pass
    
    def tearDown(self):
        shutil.rmtree(self.tempdir,ignore_errors=True)
        
    def test_find_files(self):
        testargs = ('foo.py -input_dir {temp} -output_dir {temp} -filename #.mrc'
                    ' -frames_suffix {frame} -EPU_image_pattern *')
        testargs = testargs.format(temp = self.tempdir, frame = self.frame_suffix)
        with patch('sys.argv', testargs.split()):
            obj = m()
            frames, integrated = obj.find_mrc_files(obj.input_dir, obj.EPU_image_pattern,
                                                obj.frames_suffix)
        self.assertEqual(integrated.sort(), self.exp_integrated.sort())
        self.assertEqual(frames.sort(), self.exp_frames.sort())
        
    def test_find_files_scans_subfolders(self):
        #creating an extra file in a subfolder
        os.makedirs(os.path.join(self.tempdir, 'subfolder'))
        with open(os.path.join(self.tempdir, 'subfolder/4.mrc'),'w') as f:
            self.exp_integrated += [f.name]
        testargs = ('foo.py -input_dir {temp} -output_dir {temp} -filename #.mrc'
                    ' -frames_suffix {frame} -EPU_image_pattern *')
        testargs = testargs.format(temp = self.tempdir, frame = self.frame_suffix)
        with patch('sys.argv', testargs.split()):
            obj = m()
            frames, integrated = obj.find_mrc_files(obj.input_dir, obj.EPU_image_pattern,
                                                obj.frames_suffix)
        self.assertEqual(integrated.sort(), self.exp_integrated.sort())
        self.assertEqual(frames.sort(), self.exp_frames.sort())
        
    def test_find_files_non_EPU_discarded(self):
        #only the newly created file matches the EPU pattern
        os.makedirs(os.path.join(self.tempdir, 'subfolder'))
        with open(os.path.join(self.tempdir, 'subfolder/4.mrc'),'w') as f:
            self.exp_integrated = [f.name]
            self.exp_frames = []
        EPU_image_pattern = '/subfolder/'
        testargs = ('foo.py -input_dir {temp} -output_dir {temp} -filename #.mrc'
                    ' -frames_suffix {frame} -EPU_image_pattern {EPU}')
        testargs = testargs.format(temp = self.tempdir, frame = self.frame_suffix,
                                   EPU = EPU_image_pattern)
        with patch('sys.argv', testargs.split()):
            obj = m()
            frames, integrated = obj.find_mrc_files(obj.input_dir, obj.EPU_image_pattern,
                                                obj.frames_suffix)
        self.assertEqual(integrated.sort(), self.exp_integrated.sort())
        self.assertEqual(frames.sort(), self.exp_frames.sort())
        
class test_check_args(unittest.TestCase):

    def test_default_data_dir(self):
        testargs = 'foo.py -output_dir /tmp -filename 1_a_#.mrc'.split()
        with patch('sys.argv', testargs):
            obj = m()
            self.assertTrue(obj.check)
            self.assertEqual(os.getcwd(), obj.input_dir)
    
    def test_nonexisting_input_dir(self):
        testargs = 'foo.py -filename 1_a_#.mrc -input_dir /not/exists ' + \
                   '-output_dir /tmp'
        with patch('sys.argv', testargs.split()):
            with self.assertRaises(SystemExit):
                obj = m()
    
    def test_existing_input_dir(self):
        testargs = 'foo.py -filename 1_a_#.mrc -input_dir /tmp -output_dir /tmp'
        with patch('sys.argv', testargs.split()):
            obj = m()
            self.assertTrue(obj.check)
            self.assertEqual('/tmp', obj.input_dir)
                
           
    def test_output_dir_creation(self):
        testargs = 'foo.py -filename 1_a_#.mrc -output_dir /tmp/tmp'.split()
        with patch('sys.argv', testargs):
            with patch('os.mkdir') as mock:
                obj = m()
                self.assertTrue(obj.check)
                self.assertTrue(mock.called)
    
    def test_digits_count(self):
        testargs = 'foo.py -output_dir /tmp -filename 1_a_###.mrc'.split()
        with patch('sys.argv', testargs):
            obj = m()
            self.assertTrue(obj.check)
            self.assertEqual(3, obj.digits)
            
    def test_jpg_dir_creation(self):
        testargs = 'foo.py -filename 1_a_#.mrc -output_dir /tmp -jpg_dir nonexist'.split()
        with patch('sys.argv', testargs):
            with patch('os.mkdir') as mock:
                obj = m()
                self.assertTrue(obj.check)
                self.assertTrue(mock.called)
                            
    def test_default_frame_suffix(self):
        testargs = 'foo.py -filename 1_a_#.mrc -output_dir /tmp'.split()
        with patch('sys.argv', testargs):
            obj = m()
            exp = 'frames_n{}'
            self.assertTrue(obj.check)
            self.assertEqual(exp, obj.frames_suffix)
    
    def test_non_default_frames_suffix(self):
        testargs = 'foo.py -filename 1_a_#.mrc -output_dir /tmp -frames_suffix _n#'.split()
        with patch('sys.argv', testargs):
            obj = m()
            exp = 'n{}'
            self.assertTrue(obj.check)
            self.assertEqual(exp, obj.frames_suffix)
            
    def test_no_hash_in_frame_suffix(self):
        testargs = 'foo.py -filename 1_a_#.mrc -output_dir /tmp -frames_suffix _n'.split()
        with patch('sys.argv', testargs):
            with self.assertRaises(SystemExit):
                obj = m()
                
    def test_non_frames_suffix_starting_underscore(self):
        testargs = 'foo.py -filename 1_a_#.mrc -output_dir /tmp -frames_suffix _n#'.split()
        with patch('sys.argv', testargs):
            obj = m()
            exp = 'n{}'
            self.assertTrue(obj.check)
            self.assertEqual(exp, obj.frames_suffix)
    
    def test_no_frame_specification_default(self):
        testargs = 'foo.py -filename 1_a_#.mrc -output_dir /tmp'.split()
        with patch('sys.argv', testargs):
            obj = m()
            self.assertTrue(obj.check)
            self.assertEqual(0, obj.first_frame)
            self.assertEqual(6, obj.last_frame)
    
    def test_first_last_frame(self):
        testargs = 'foo.py -filename 1_a_#.mrc -first_last 1,2 -output_dir /tmp'.split()
        with patch('sys.argv', testargs):
            obj = m()
            self.assertTrue(obj.check)
            self.assertEqual(1, obj.first_frame)
            self.assertEqual(2, obj.last_frame)
    
    def test_first_last_frame_number_no_comma(self):
        testargs = 'foo.py -filename 1_a_#.mrc -first_last 1-2 -output_dir /tmp'.split()
        with patch('sys.argv', testargs):
            with self.assertRaises(SystemExit):
                obj = m()
                
    def test_n_frames(self):
        testargs = 'foo.py -filename 1_a_#.mrc -n_frames 12 -output_dir /tmp'.split()
        with patch('sys.argv', testargs):
            obj = m()
            self.assertTrue(obj.check)
            self.assertEqual(0, obj.first_frame)
            self.assertEqual(11, obj.last_frame)
    
    def test_first_last_not_a_number(self):
        testargs = 'foo.py -filename 1_a_#.mrc -first_last a,b -output_dir /tmp'.split()
        with patch('sys.argv', testargs):
            with self.assertRaises(ValueError):
                obj = m()
                
    def test_no_EPU_pattern(self):
        testargs = 'foo.py -filename 1_a_#.mrc -output_dir /tmp'.split()
        with patch('sys.argv', testargs):
            obj = m()
            self.assertEqual(obj.EPU_image_pattern, '/Data/FoilHole')
            
    def test_EPU_pattern(self):
        testargs = 'foo.py -filename 1_a_#.mrc -output_dir /tmp -EPU_image_pattern foo'.split()
        with patch('sys.argv', testargs):
            obj = m()
            self.assertEqual(obj.EPU_image_pattern, 'foo')
    
    def test_EPU_pattern_is_asterisk(self):
        testargs = 'foo.py -filename 1_a_#.mrc -output_dir /tmp -EPU_image_pattern *'.split()
        with patch('sys.argv', testargs):
            obj = m()
            self.assertEqual(obj.EPU_image_pattern, '')