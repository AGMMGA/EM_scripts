import glob
import os
import sys
import tempfile
import unittest
from unittest.mock import patch
from testfixtures import TempDirectory
from Mass_rename_micrographs_argparse import Micrograph_renamer as m

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
           
    def test_output_dir_creation(self):
        testargs = 'foo.py -filename 1_a_#.mrc -output_dir /tmp/tmp'.split()
        with patch('sys.argv', testargs):
            with patch('os.mkdir') as mock:
                obj = m()
                self.assertTrue(obj.check)
                self.assertTrue(mock.called)
    
    def test_integrated_dir_creation(self):
        testargs = 'foo.py -filename 1_a_#.mrc -output_dir /tmp/tmp ' \
                   '-move_integrated nonexisiting'.split()
        with patch('sys.argv', testargs):
            with patch('os.mkdir') as mock:
                obj = m()
                self.assertTrue(obj.check)
                self.assertTrue(mock.called)
                
    def test_move_integrated_no_arg(self):
        testargs = 'foo.py -filename 1_a_#.mrc -output_dir /tmp/tmp ' \
                   '-move_integrated'.split()
        with patch('sys.argv', testargs):
            with patch('os.mkdir') as mock:
                obj = m()
                self.assertTrue(obj.check)
                self.assertEqual(obj.output_dir, obj.move_integrated)
                self.assertEqual('/tmp/tmp', obj.move_integrated)
    
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

class test_find_files(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    