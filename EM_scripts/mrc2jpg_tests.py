import sys
import unittest
import shlex
import os
from unittest import mock

import mrc2jpg as m

class test_get_mrc_files(unittest.TestCase):
    
    @mock.patch('mrc2jpg.glob.glob')
    def test_get_mrc_files(self, mock_glob):
        mock_glob.return_value = ['1.mrc', '2.mrc', '3.mrc']
        exp = [os.path.join(os.getcwd(), i) for i in mock_glob.return_value]
        print (exp)
        a = m.imageConverter()
        self.assertEqual(exp, a.get_mrc_files())
        
    