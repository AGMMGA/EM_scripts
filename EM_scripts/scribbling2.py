import sys
import unittest
import shlex
import os
from unittest.mock import patch, MagicMock

import starfile_edit_argparse as s

 
class test_args_check(unittest.TestCase):
         
    def setUp(self):
        sys.argv = shlex.split('test.py -i /tmp/in.star -o /tmp/out.star -k 1 2 3 -filename=123_BRCA1_001.mrc -digits 4 --numbers')
        self.star_in = open('/tmp/in.star', 'w+b')
        self.star_out = open('/tmp/out.star', 'w+b')
        self.parsed = s.parse(sys.argv)
        
    def tearDown(self):
        if os.path.isfile('/tmp/in.star'):
            os.remove('/tmp/in.star')
        if os.path.isfile('/tmp/out.star'):
            os.remove('/tmp/out.star')

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
        
        
        
        
        