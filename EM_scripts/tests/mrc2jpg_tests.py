import glob
import multiprocessing
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts_EM import mrc2jpg as m


class test_files_operations(unittest.TestCase):
    
    def setUp(self):
        self.files  = ['1.mrc', '2.mrc', '3.mrc']
        self.tempdir = tempfile.mkdtemp()
        for f in self.files:
            with open(os.path.join(self.tempdir,f),'w') as f:
                pass
        self.infiles = [os.path.join(self.tempdir, i) for i in self.files]
        self.outfiles = [os.path.join(self.tempdir, 'jpgs', i.replace('.mrc','.jpg'))
                    for i in self.files]
        self.calls = ['python2.7 /Xsoftware64/EM/EMAN2/bin/e2proc2d.py {} {}'.format(
                        self.infiles[i], self.outfiles[i]).split() for i in range(3)]
            
    def tearDown(self):
        shutil.rmtree(self.tempdir, ignore_errors=True)
        
    def test_get_mrc_files(self):
        #checking that the file is returned with the whole path
        testargs = 'foo.py -i {}'.format(self.tempdir)
        with patch('sys.argv', testargs.split()):
            a = m.imageConverter()
            res = a.get_mrc_files()
            exp = [os.path.join(self.tempdir, f) for f in self.files]
        self.assertEqual(exp.sort(), res.sort())
    
    def test_no_mrc_files(self):
        for f in glob.glob(os.path.join(self.tempdir, '*.mrc')):
            os.remove(f)
        testargs = 'foo.py -i {}'.format(self.tempdir)
        with patch('sys.argv', testargs.split()):
            with self .assertRaises(SystemExit):
                a = m.imageConverter()
                a.get_mrc_files()
    
    def test_normal_operation(self):
        testargs = 'foo.py -i {}'.format(self.tempdir)
        with patch('sys.argv', testargs.split()):
            with patch('subprocess.Popen') as mock_popen:
                #mocking subprocess.communicate to avoid exception in main()
                mock_popen.return_value.communicate.return_value = [0,1]
                a = m.imageConverter()
                with patch('sys.stdout'): #silent please
                    a.main()
                self.assertEqual(mock_popen.call_count, 3)
                #extract the calls to the mock, in sensible format
                call_args = []
                for i in range(3): 
                    call_args.append(mock_popen.call_args_list[i][0][0])
                call_args.sort()
                for i, value in enumerate(self.calls):
                    self.assertEqual(value, call_args[i])
                    
    def test_EMAN_fails(self):
        testargs = 'foo.py -i {}'.format(self.tempdir)
        with patch('sys.argv', testargs.split()):
            with patch('subprocess.Popen') as mock_popen:
                #mocking subprocess.communicate to avoid exception in main()
                mock_popen.return_value.communicate.return_value = [0,'Traceback']
                a = m.imageConverter()
                with self.assertRaises(SystemExit):
                    a.main()
            
    def test_jpg_exists_no_force(self):
        os.mkdir(os.path.join(self.tempdir, 'jpgs'))
        os.remove(os.path.join(self.tempdir, '2.mrc'))
        os.remove(os.path.join(self.tempdir, '3.mrc'))
        with open(os.path.join(self.tempdir, 'jpgs', '1.jpg'),'w'):
            pass
        testargs = 'foo.py -i {}'.format(self.tempdir)
        with patch('sys.argv', testargs.split()):
            with patch('sys.stdout'):
                with patch('builtins.print') as mock_print:
                    a = m.imageConverter()
                    a.main()
        #the IOError exception is caught and handled. Here I am testing that
        #the error message is actually printed as a proxy for the handling
                    msg = '{}/1.jpg exists. Skipped. Use -f to force overwrite'.format(
                                                self.tempdir)
                    mock_print.assert_called_with(msg)
    
    def test_jpg_exists_and_force(self):
        os.mkdir(os.path.join(self.tempdir, 'jpgs'))
        with open(os.path.join(self.tempdir, 'jpgs', '1.jpg'),'w'):
            pass
        testargs = 'foo.py -i {} -f'.format(self.tempdir)
        with patch('sys.argv', testargs.split()):
            with patch('os.remove') as mock_remove:
                a = m.imageConverter()
                with patch('sys.stdout'):
                    a.main()
                mock_remove.assert_called_with(self.outfiles[0])
        
class test_args_check(unittest.TestCase):
    
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.tempdir, ignore_errors=True)
       
    def test_i_default(self):
        with patch('sys.argv', ['foo.py']):
            a = m.imageConverter()
        self.assertEqual(os.getcwd(), a.i)
     
    def test_i_given(self):
        self.tempdir = tempfile.mkdtemp()
        testargs = 'foo.py -i {} '.format(self.tempdir)
        with patch('sys.argv', testargs.split()):
            a = m.imageConverter()
            self.assertEqual(a.i, self.tempdir)
     
    def test_o_default(self):
        testargs = 'foo.py -i {}'.format(self.tempdir)
        with patch('sys.argv', testargs.split()):
            with patch('os.makedirs') as mock:
                a = m.imageConverter()
                self.assertTrue(mock.called) #check it made the dir
        exp = os.path.join(self.tempdir, 'jpgs')
        self.assertEqual(exp, a.o)
         
    def test_o_given_and_existing(self):
        testargs = 'foo.py -o {}'.format(self.tempdir)
        with patch('sys.argv', testargs.split()):
            a = m.imageConverter()
            self.assertEqual(a.o, self.tempdir)
     
    def test_o_given_nonexisting_force(self):
        testargs = 'foo.py -o /nonexisting/dir/ -f'.format(self.tempdir)
        with patch('sys.argv', testargs.split()):
            with patch ('os.makedirs') as mock:
                m.imageConverter()
                self.assertTrue(mock.called)
    
    def test_o_given_nonexisting_no_force(self):
        testargs = 'foo.py -o /nonexisting/path'
        with patch('sys.argv', testargs.split()):
            with patch('os.makedirs'):
                with self.assertRaises(SystemExit):
                    m.imageConverter() 
    
    def test_process_default(self):
        with patch('sys.argv', ['foo.py']):
            a = m.imageConverter()
        self.assertEqual(a.lowpass, '')
         
    def test_process_given(self):
        testargs = 'foo.py --lowpass 40'
        with patch('sys.argv', testargs.split()):
            a = m.imageConverter()
            i = 1/40
            exp = '--process filter.lowpass.gauss:cutoff_freq={}'.format(i)
            self.assertAlmostEqual(a.lowpass, exp, 3, 0.001)
    
    def test_process_given_with_A(self):
        testargs = 'foo.py --lowpass 40A'
        with patch('sys.argv', testargs.split()):
            a = m.imageConverter()
            i = 1/40
            exp = '--process filter.lowpass.gauss:cutoff_freq={}'.format(i)
            self.assertAlmostEqual(a.lowpass, exp, 7, 0.001)
    
    def test_process_given_malformed(self):
        testargs = 'foo.py --lowpass forty'
        with patch('sys.argv', testargs.split()):
            with self.assertRaises(SystemExit):
                m.imageConverter()
            
    def test_scale_default(self):
        with patch('sys.argv', ['foo.py']):
            a = m.imageConverter()
        self.assertEqual(a.scale, '')
         
    def test_scale_given(self):
        testargs = 'foo.py --scale 4'
        with patch('sys.argv', testargs.split()):
            a = m.imageConverter()
            self.assertEqual(a.scale, '--meanshrink 4')
            
    def test_ncpus_default(self):
        testargs = 'foo.py'
        cpus = multiprocessing.cpu_count() -1
        with patch('sys.argv', testargs.split()):
            a = m.imageConverter()
            self.assertEqual(a.n_cpus, cpus)   
            
    def test_ncpus_given_and_ok(self):
        testargs = 'foo.py --n_cpus 4'
        with patch('sys.argv', testargs.split()):
            a = m.imageConverter()
            self.assertEqual(a.n_cpus, 4)   
            
    def test_ncpus_too_many(self):
        testargs = 'foo.py --n_cpus 200000000'
        with patch('sys.argv', testargs.split()):
            with self.assertRaises(SystemExit):
                m.imageConverter()   
                
                
if __name__ == '__main__':
    unittest.main()        