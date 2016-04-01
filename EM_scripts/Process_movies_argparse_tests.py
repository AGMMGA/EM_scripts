import unittest
import os
import sys
from unittest.mock import patch
from testfixtures import TempDirectory
from Process_movies_argparse import movie_processor as m

class test_check_args(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_default_frames_dir(self):
        testargs = 'foo.py -filename 1_a_#.mrc'.split()
        with patch('sys.argv', testargs):
            obj = m()
            self.assertEqual(os.getcwd(), obj.frames_dir)
    
    def test_nonexisting_input_dir(self):
        testargs = 'foo.py -filename 1_a_#.mrc -frames_dir /not/exists'.split()
        with patch('sys.argv', testargs):
            with self.assertRaises(SystemExit):
                obj = m()
    
    def test_default_output_dir(self):
        testargs = 'foo.py -filename 1_a_#.mrc'.split()
        with patch('sys.argv', testargs):
            obj = m()
            exp = os.path.join(os.getcwd(), 'integrated')
            self.assertEqual(exp, obj.output_dir)
           
    def test_output_dir_creation(self):
        testargs = 'foo.py -filename 1_a_#.mrc -output_dir /tmp/tmp'.split()
        with patch('sys.argv', testargs):
            with patch('os.makedirs') as mock:
                obj = m()
                self.assertTrue(mock.called)
        
    def test_default_frame_suffix(self):
        testargs = 'foo.py -filename 1_a_#.mrc'.split()
        with patch('sys.argv', testargs):
            obj = m()
            exp = 'frames_n{}'
            self.assertEqual(exp, obj.frames_suffix)
    
    def test_non_default_frames_suffix(self):
        testargs = 'foo.py -filename 1_a_#.mrc -frames_suffix _n#'.split()
        with patch('sys.argv', testargs):
            obj = m()
            exp = '_n{}'
            self.assertEqual(exp, obj.frames_suffix)
            
    def test_no_hash_in_frame_suffix(self):
        testargs = 'foo.py -filename 1_a_#.mrc -frames_suffix _n'.split()
        with patch('sys.argv', testargs):
            with self.assertRaises(SystemExit):
                obj = m()
                
    def test_no_frame_specification_default(self):
        testargs = 'foo.py -filename 1_a_#.mrc'.split()
        with patch('sys.argv', testargs):
            obj = m()
            self.assertEqual(0, obj.first_frame)
            self.assertEqual(6, obj.last_frame)
    
    def test_first_last_frame(self):
        testargs = 'foo.py -filename 1_a_#.mrc -first_last 1,2'.split()
        with patch('sys.argv', testargs):
            obj = m()
            self.assertEqual(1, obj.first_frame)
            self.assertEqual(2, obj.last_frame)
    
    def test_first_last_frame_number_no_comma(self):
        testargs = 'foo.py -filename 1_a_#.mrc -first_last 1 2'.split()
        with patch('sys.argv', testargs):
            with self.assertRaises(SystemExit):
                obj = m()
                
    def test_n_frames(self):
        testargs = 'foo.py -filename 1_a_#.mrc -n_frames 12'.split()
        with patch('sys.argv', testargs):
            obj = m()
            self.assertEqual(0, obj.first_frame)
            self.assertEqual(11, obj.last_frame)
    
    def test_first_last_not_a_number(self):
        testargs = 'foo.py -filename 1_a_#.mrc -first_last a,b'.split()
        with patch('sys.argv', testargs):
            with self.assertRaises(ValueError):
                obj = m()
    
    def test_digits_count(self):
        testargs = 'foo.py -filename 1_a_###.mrc'.split()
        with patch('sys.argv', testargs):
            obj = m()
            self.assertEqual(3, obj.digits)
    def test_no_hash_in_filename(self):
        testargs = 'foo.py -filename 1_a_.mrc'.split()
        with patch('sys.argv', testargs):
            with self.assertRaises(SystemExit):
                obj = m()
                
class test_init(unittest.TestCase):
    
    def test_micrograph_name(self):
        testargs = 'foo.py -filename 1_a_###.mrc'.split()
        with patch('sys.argv', testargs):
            obj = m()
            self.assertEqual('1_a_{}', obj.micrograph_name) 
            
    def test_frame_name(self):
        testargs = 'foo.py -filename 1_a_###.mrc'.split()
        with patch('sys.argv', testargs):
            obj = m()
            self.assertEqual('1_a_{}_frames_n{}', obj.frame_name)
    
    