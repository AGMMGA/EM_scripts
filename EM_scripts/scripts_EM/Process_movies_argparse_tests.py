#!/usr/bin/python2.7

#python2 compatibility - needed to make python3 compatible with python 2.7
#otherwise e2proc2d will refuse to run
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import glob
import os
import sys
import tempfile
import unittest
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
            self.assertEqual(obj.frames_dir, obj.output_dir)
           
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
            exp = 'n{}'
            self.assertEqual(exp, obj.frames_suffix)
            
    def test_no_hash_in_frame_suffix(self):
        testargs = 'foo.py -filename 1_a_#.mrc -frames_suffix _n'.split()
        with patch('sys.argv', testargs):
            with self.assertRaises(SystemExit):
                obj = m()
                
    def test_non_frames_suffix_starting_underscore(self):
        testargs = 'foo.py -filename 1_a_#.mrc -frames_suffix _n#'.split()
        with patch('sys.argv', testargs):
            obj = m()
            exp = 'n{}'
            self.assertEqual(exp, obj.frames_suffix)
                
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
    
class test_get_file_list(unittest.TestCase):
    
    def setUp(self):
        self.testfiles = ['1_a_001_frames_n{}.mrc'.format(str(i)) \
                          for i in range (7)]
        self.tempdir = tempfile.mkdtemp()
        for i in self.testfiles:
            f= open(os.path.join(self.tempdir, i), 'w')
        
    def tearDown(self):
        for i in self.testfiles:
            f = os.path.join(self.tempdir, i)
            if os.path.isfile(f):
                os.remove(f)
        if os.path.isdir(self.tempdir):
            os.rmdir(self.tempdir)
            
    def test(self):
        testargs = 'foo.py -filename 1_a_###.mrc'.split()
        exp = [os.path.join(self.tempdir, i) for i in self.testfiles].sort()
        with patch('sys.argv', testargs):
            obj = m()
            obj.frames_dir = self.tempdir
        self.assertEqual(exp, obj.get_minimal_set(obj.get_file_list()).sort())

class test_check_all_present(unittest.TestCase):
    
    def setUp(self):
        self.testfiles = ['1_a_001_frames_n{}.mrc'.format(str(i)) \
                          for i in range (7)]
        self.testfiles_missing = ['1_a_002_frames_n{}.mrc'.format(str(i)) \
                          for i in range (5)]
        self.tempdir = tempfile.mkdtemp()
        for i in (self.testfiles):
            f= open(os.path.join(self.tempdir, i), 'w')
        
    def tearDown(self):
        for i in glob.glob(os.path.join(self.tempdir, '*')):
            f = os.path.join(self.tempdir, i)
            if os.path.isfile(f):
                os.remove(f)
        if os.path.isdir(self.tempdir):
            os.rmdir(self.tempdir)
            
    def test_all_present(self):
        testargs = 'foo.py -filename 1_a_###.mrc -frames_dir {}'.format(self.tempdir)
        testargs = testargs.split()
        with patch('sys.argv', testargs):                
            obj = m()
            l = obj.get_minimal_set(obj.get_file_list())
            self.assertTrue(obj.check_all_present(l))
    
    def test_missing_frames_no_force(self):
        testargs = 'foo.py -filename 1_a_###.mrc -frames_dir {}'.format(self.tempdir)
        testargs = testargs.split()
        for i in (self.testfiles_missing):
            f= open(os.path.join(self.tempdir, i), 'w')
        with patch('sys.argv', testargs):                
            obj = m()
            l = obj.get_minimal_set(obj.get_file_list())
            with self.assertRaises(SystemExit):
                obj.check_all_present(l)    
                
    def test_missing_frames_with_force(self):
        testargs = 'foo.py -filename 1_a_###.mrc -frames_dir {} -f'.format(self.tempdir)
        testargs = testargs.split()
        for i in (self.testfiles_missing):
            f= open(os.path.join(self.tempdir, i), 'w')
        exp = [os.path.join(self.tempdir, '1_a_002_frames_n6.mrc'),
               os.path.join(self.tempdir, '1_a_002_frames_n5.mrc')]
        with patch('sys.argv', testargs):                
            obj = m()
            l = obj.get_minimal_set(obj.get_file_list())
            self.assertFalse(obj.check_all_present(l))
            self.assertEqual(exp.sort(), obj.missing.sort())
            
    def test_all_present_with_custom_frames(self):
        testargs = 'foo.py -filename 1_a_###.mrc  -frames_dir {} -first_last 1,2'
        testargs = testargs.format(self.tempdir).split()
        with patch('sys.argv', testargs):                
            obj = m()
            l = obj.get_minimal_set(obj.get_file_list())
            self.assertTrue(obj.check_all_present(l))
    
    def test_missing_frames_with_custom_frames_and_force(self):
        testargs = 'foo.py -filename 1_a_###.mrc -frames_dir {} -first_last 4,6 -f'
        testargs = testargs.format(self.tempdir).split()
        for i in ['1_a_002_frames_n6.mrc','1_a_002_frames_n5.mrc']:
            open(i,'w')
            f= open(os.path.join(self.tempdir, i), 'w')
        exp = [os.path.join(self.tempdir, '1_a_002_frames_n4.mrc')]
        with patch('sys.argv', testargs):                
            obj = m()
            l = obj.get_minimal_set(obj.get_file_list())
            self.assertFalse(obj.check_all_present(l))
            self.assertEqual(exp.sort(), obj.missing.sort())
            
    def test_missing_frames_with_custom_frames_no_force(self):
        testargs = 'foo.py -filename 1_a_###.mrc -frames_dir {} -first_last 4,6'
        testargs = testargs.format(self.tempdir).split()
        for i in ['1_a_002_frames_n6.mrc','1_a_002_frames_n5.mrc']:
            open(i,'w')
            f= open(os.path.join(self.tempdir, i), 'w')
        with patch('sys.argv', testargs):                
            obj = m()
            l = obj.get_minimal_set(obj.get_file_list())
            with self.assertRaises(SystemExit):
                obj.check_all_present(l)

class test_make_stack(unittest.TestCase):
    pass
    # implement this I am tired

    