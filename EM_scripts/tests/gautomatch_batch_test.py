import glob
import multiprocessing
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts_EM import gautomatch_batch as m

class test_args_check(unittest.TestCase):
    
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.tempdir, ignore_errors=True)
       
    def test_mrc_folder_default(self):
        with patch('sys.argv', ['foo.py']):
            a = m.Gautomatcher()
        self.assertEqual(os.getcwd(), a.mrc_folder)
     
    def test_mrc_folder_given(self):
        self.tempdir = tempfile.mkdtemp()
        testargs = 'foo.py -mrc_folder {} '.format(self.tempdir)
        with patch('sys.argv', testargs.split()):
            a = m.Gautomatcher()
            self.assertEqual(a.mrc_folder, self.tempdir)
    
    def test_mrc_folder_missing(self):
        testargs = 'foo.py -mrc_folder {} '.format('not_a_folder')
        with patch('sys.argv', testargs.split()):
            with patch('os.mkdir') as mock_mkdir:
                a = m.Gautomatcher()
                mock_mkdir.assert_called_once_with('not_a_folder')
    
    def test_jpg_folder_default(self):
        with patch('sys.argv', ['foo.py']):
            a = m.Gautomatcher()
        exp = os.path.join(os.getcwd(), 'jpgs')
        self.assertEqual(exp, a.jpg_folder)
     
    def test_jpg_folder_given(self):
        self.tempdir = tempfile.mkdtemp()
        testargs = 'foo.py -jpg_folder {} '.format(self.tempdir)
        with patch('sys.argv', testargs.split()):
            a = m.Gautomatcher()
            self.assertEqual(a.jpg_folder, self.tempdir)
            
    def test_jpg_folder_missing(self):
        testargs = 'foo.py -jpg_folder {} '.format('not_a_folder')
        with patch('sys.argv', testargs.split()):
            with patch('os.mkdir') as mock_mkdir:
                a = m.Gautomatcher()
                mock_mkdir.assert_called_once_with('not_a_folder')
'''    
    def test_jpg_folder_default(self):
        with patch('sys.argv', ['foo.py']):
            a = m.Gautomatcher()
        exp = os.path.join(os.getcwd(), 'jpgs')
        self.assertEqual(exp, a.jpg_folder)
     
    def test_jpg_folder_given(self):
        self.tempdir = tempfile.mkdtemp()
        testargs = 'foo.py -jpg_folder {} '.format(self.tempdir)
        with patch('sys.argv', testargs.split()):
            a = m.Gautomatcher()
            self.assertEqual(a.jpg_folder, self.tempdir)
            
    def test_jpg_folder_missing(self):
        testargs = 'foo.py -jpg_folder {} '.format('not_a_folder')
        with patch('sys.argv', testargs.split()):
            with self.assertRaises(SystemExit):
                a = m.Gautomatcher()
                
                
                
    
    def test_o_given_nonexisting_no_force(self):
        testargs = 'foo.py -o /nonexisting/path'
        with patch('sys.argv', testargs.split()):
            with patch('os.makedirs'):
                with self.assertRaises(SystemExit):
                    m.Gautomatcher() 
    
    def test_process_default(self):
        with patch('sys.argv', ['foo.py']):
            a = m.Gautomatcher()
        self.assertEqual(a.lowpass, '')
         
    def test_process_given(self):
        testargs = 'foo.py --lowpass 40'
        with patch('sys.argv', testargs.split()):
            a = m.Gautomatcher()
            i = 1/40
            exp = '--process filter.lowpass.gauss:cutoff_freq={}'.format(i)
            self.assertAlmostEqual(a.lowpass, exp, 3, 0.001)
    
    def test_process_given_with_A(self):
        testargs = 'foo.py --lowpass 40A'
        with patch('sys.argv', testargs.split()):
            a = m.Gautomatcher()
            i = 1/40
            exp = '--process filter.lowpass.gauss:cutoff_freq={}'.format(i)
            self.assertAlmostEqual(a.lowpass, exp, 7, 0.001)
    
    def test_process_given_malformed(self):
        testargs = 'foo.py --lowpass forty'
        with patch('sys.argv', testargs.split()):
            with self.assertRaises(SystemExit):
                m.Gautomatcher()
            
    def test_scale_default(self):
        with patch('sys.argv', ['foo.py']):
            a = m.Gautomatcher()
        self.assertEqual(a.scale, '')
         
    def test_scale_given(self):
        testargs = 'foo.py --scale 4'
        with patch('sys.argv', testargs.split()):
            a = m.Gautomatcher()
            self.assertEqual(a.scale, '--meanshrink 4')
            
    def test_ncpus_default(self):
        testargs = 'foo.py'
        cpus = multiprocessing.cpu_count() -1
        with patch('sys.argv', testargs.split()):
            a = m.Gautomatcher()
            self.assertEqual(a.n_cpus, cpus)   
            
    def test_ncpus_given_and_ok(self):
        testargs = 'foo.py --n_cpus 4'
        with patch('sys.argv', testargs.split()):
            a = m.Gautomatcher()
            self.assertEqual(a.n_cpus, 4)   
            
    def test_ncpus_too_many(self):
        testargs = 'foo.py --n_cpus 200000000'
        with patch('sys.argv', testargs.split()):
            with self.assertRaises(SystemExit):
                m.Gautomatcher()   '''