import glob
import shutil
import unittest
import os
import tempfile
from unittest import mock
from unittest.mock import patch
import remove_from_jpg as r

class test_check_args(unittest.TestCase):
    
    def test_no_jpg_directory_default(self):
        testargs = 'foo.py'
        with patch('sys.argv', testargs.split()):
            obj = r.Micrograph_remover()
            self.assertEqual(obj.j, os.getcwd())
    
    def test_jpg_directory_not_exist(self):
        testargs = 'foo.py -j nonexisting'
        with patch('sys.argv', testargs.split()):
            with self.assertRaises(SystemExit):
                obj = r.Micrograph_remover()
    
    def test_jpg_directory(self):
        testargs = 'foo.py -j /tmp'
        with patch('sys.argv', testargs.split()):
            obj = r.Micrograph_remover()
            self.assertEqual(obj.j, '/tmp')
            
    def test_jpg_dir_as_dot(self):
        testargs = 'foo.py -j .'
        with patch('sys.argv', testargs.split()):
            obj = r.Micrograph_remover()
            self.assertEqual(obj.j, '.')
    
    def test_no_micrograph_directory_default_with_j(self):
        try:
            tempdir = tempfile.mkdtemp()
            tempjpg = os.path.join(tempdir, 'jpgs')
            os.mkdir(tempjpg)
            testargs = 'foo.py -j {}'.format(tempjpg)
            with patch('sys.argv', testargs.split()):
                obj = r.Micrograph_remover()
                self.assertEqual(obj.m, tempdir)
        finally:
            os.rmdir(tempjpg)
            os.rmdir(tempdir)
            
    def test_no_micrograph_directory_default_without_j(self):
        testargs = 'foo.py'
        with patch('sys.argv', testargs.split()):
            obj = r.Micrograph_remover()
            self.assertEqual(obj.m, os.path.abspath(os.getcwd() + '/..'))
    
    def test_micrograph_directory_not_exist(self):
        testargs = 'foo.py -m nonexisting'
        with patch('sys.argv', testargs.split()):
            with self.assertRaises(SystemExit):
                obj = r.Micrograph_remover()
    
    def test_micrograph_directory(self):
        testargs = 'foo.py -m /tmp'
        with patch('sys.argv', testargs.split()):
            obj = r.Micrograph_remover()
            self.assertEqual(obj.m, '/tmp')       
    
    def test_delete_mode(self):
        testargs = 'foo.py -d'
        with patch('sys.argv', testargs.split()):
            obj = r.Micrograph_remover()
            self.assertTrue(obj.d)
            self.assertFalse(obj.r)
            
    def test_rename_mode(self):
        testargs = 'foo.py -r'
        with patch('sys.argv', testargs.split()):
            obj = r.Micrograph_remover()
            self.assertTrue(obj.r)
            self.assertFalse(obj.d)
            
class test_get_jpg_and_get_mrc_list(unittest.TestCase):
    
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        for f in ['1.jpg', '2.jpg', '3.mrc', '4.mrc']:
            with open(os.path.join(self.tempdir, f), 'w'):
                pass
    
    def tearDown(self):
        try:
            for f in ['1.jpg', '2.jpg', '3.mrc', '4.mrc']:
                os.remove(os.path.join(self.tempdir, f))
            os.rmdir(self.tempdir)
        except FileNotFoundError:
            pass
    
    def test_normal_jpg_files(self):
        testargs = 'foo.py -j {}'.format(str(self.tempdir))
        with patch('sys.argv', testargs.split()):
            obj = r.Micrograph_remover()
            exp = [os.path.join(self.tempdir, i) for i in ['1.jpg', '2.jpg']]
            self.assertEqual(obj.get_jpg_list().sort(), exp.sort())
    
    def test_normal_mrc_files(self):
        testargs = 'foo.py -j {}'.format(str(self.tempdir))
        with patch('sys.argv', testargs.split()):
            obj = r.Micrograph_remover()
            exp = [os.path.join(self.tempdir, i) for i in ['1.mrc', '2.mrc']]
            res = obj.get_mrc_list().sort()
            self.assertEqual(obj.get_jpg_list().sort(), exp.sort())
    
    @mock.patch('remove_from_jpg.glob.glob')
    def test_no_mrc_files(self, mock_glob):
        testargs = 'foo.py'
        with patch('sys.argv', testargs.split()):
            mock_glob.return_value = []
            obj = r.Micrograph_remover()
            res = obj.get_mrc_list().sort()
            self.assertEqual([], obj.get_mrc_list())
    
    def test_no_jpgs(self):
        testargs = 'foo.py -j {}'.format(self.tempdir)
        for f in glob.glob(os.path.join(self.tempdir, '*.jpg')):
            os.remove(f)
        with patch('sys.argv', testargs.split()):
            obj = r.Micrograph_remover()
            with self.assertRaises(SystemExit):
                obj.get_jpg_list()
            
class test_find_extra_mrcs(unittest.TestCase):
    
    def test_empty_lists(self):
        jpgs = []
        mrcs = []
        testargs = 'foo.py'
        with patch('sys.argv', testargs.split()):
            obj = r.Micrograph_remover()
            self.assertEqual([], obj.find_extra_mrcs(jpgs, mrcs))
            
    def test_no_extras_no_path(self):
        jpgs = ['1.jpg', '2.jpg']
        mrcs = ['1.mrc', '2.mrc']
        testargs = 'foo.py'
        with patch('sys.argv', testargs.split()):
            obj = r.Micrograph_remover()
            self.assertEqual([], obj.find_extra_mrcs(jpgs, mrcs))
    
    def test_extra_mrc_no_path(self):
        jpgs = ['1.jpg', '2.jpg']
        mrcs = ['1.mrc', '2.mrc', '3.mrc']
        testargs = 'foo.py'
        with patch('sys.argv', testargs.split()):
            obj = r.Micrograph_remover()
            self.assertEqual(['3.mrc'], obj.find_extra_mrcs(jpgs, mrcs))
            
    def test_extra_jpg_no_path(self):
        jpgs = ['1.jpg', '2.jpg', '3,jpg']
        mrcs = ['1.mrc', '2.mrc']
        testargs = 'foo.py'
        with patch('sys.argv', testargs.split()):
            obj = r.Micrograph_remover()
            self.assertEqual([], obj.find_extra_mrcs(jpgs, mrcs))
            
    def test_extra_mrc_with_path(self):
        jpgs = ['/tmp/jpg/1.jpg', '/tmp/jpg/2.jpg']
        mrcs = ['/tmp/1.mrc', '/tmp/2.mrc', '/tmp/3.mrc']
        testargs = 'foo.py'
        with patch('sys.argv', testargs.split()):
            obj = r.Micrograph_remover()
            self.assertEqual(['/tmp/3.mrc'], obj.find_extra_mrcs(jpgs, mrcs))
    
    def test_extra_mrc_with_windows_path(self):
        self.assertTrue(False, 'Implement Windows path compliance?')
            
class test_remove_and_rename(unittest.TestCase):
    
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        os.mkdir(self.tempdir + '/jpgs')
        self.jpgs = ['1.jpg', '2.jpg']
        self.mrcs = ['1.mrc', '2.mrc', '3.mrc']
        for f in self.jpgs:
            with open(os.path.join(self.tempdir, 'jpgs', f), 'w'):
                pass
        for f in self.mrcs:
            with open(os.path.join(self.tempdir, f), 'w'):
                pass
            
    def tearDown(self):
        try:
            shutil.rmtree(self.tempdir)
        except FileNotFoundError:
            pass
        
    def test_rename(self):
        testargs = 'foo.py -j {jpgs} -m {mrcs} -r'.format(
                            jpgs = os.path.join(self.tempdir, 'jpgs'),
                            mrcs = self.tempdir)
        with patch('sys.argv', testargs.split()):
            obj = r.Micrograph_remover()
            jpgs = obj.get_jpg_list()
            mrcs = obj.get_mrc_list()
            extra = obj.find_extra_mrcs(jpgs, mrcs)
            obj.rename_unwanted(extra)
        self.assertEqual([os.path.join(self.tempdir, '3.mrc_bad')], 
                         glob.glob(os.path.join(self.tempdir, '*.mrc_bad')))
        exp = [os.path.join(self.tempdir, i) for i in ['1.mrc','2.mrc']]
        self.assertEqual(exp,
                         glob.glob(os.path.join(self.tempdir, '*.mrc')))
    
    def test_remove(self):
        testargs = 'foo.py -j {jpgs} -m {mrcs} -d'.format(
                            jpgs = os.path.join(self.tempdir, 'jpgs'),
                            mrcs = self.tempdir)
        with patch('sys.argv', testargs.split()):
            obj = r.Micrograph_remover()
            jpgs = obj.get_jpg_list()
            mrcs = obj.get_mrc_list()
            extra = obj.find_extra_mrcs(jpgs, mrcs)
            obj.delete_unwanted(extra)
        self.assertEqual([], 
                         glob.glob(os.path.join(self.tempdir, '*.mrc_bad')))
        exp = [os.path.join(self.tempdir, i) for i in ['1.mrc','2.mrc']]
        self.assertEqual(exp,
                         glob.glob(os.path.join(self.tempdir, '*.mrc')))
     
    
    