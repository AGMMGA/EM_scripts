from pprint import pprint
import unittest

from scripts_EM import stats_handler as sh


class test_bin_procedure(unittest.TestCase):
    
    def setUp(self):
        self.header, self.body = sh.read_starfile(
            '/processing/andrea/20160713_NCP_GO_Talos/relion/Micrographs/micrographs_all_gctf.star')
    
    def test_select_from_star(self):
        img_list = [('20160713_NCP_GO_Talos_002.mrc', 'irrelevant')]
        exp = ['20160713_NCP_GO_Talos_002.mrc 20160713_NCP_GO_Talos_002.ctf:mrc'
               ' 18861.341797 19810.572266    40.059990   300.000000     2.700000'
               '     0.100000 122807.015625    14.000000     0.150301'
               '     3.899599\n']
        result = sh.select_from_star(img_list, self.body)
        self.assertEqual(result, exp)

    def test_calculate_too_many_bins(self):
        img_list = ['a','b']
        with self.assertRaises(AssertionError):
            sh.calculate_bins(img_list, self.body, 20)
        
    def test_calculate_bins_4bins(self):
        '''
        >>> a = np.array([0,1,2,3,4,5,6,7,8,9,10])
        >>> for i in [0,25,50,75,100]:
        ...     print(np.percentile(a, i))
        ... 
        0.0
        2.5
        5.0
        7.5
        10.0
        '''
        star_body = ['{}.mrc {}'.format(str(i),str(i)) for i in [0,3,6,9]] 
        img_list = [('{}.mrc'.format(i), float(i)) for i in [0,3,6,9]]
        exp_4bins = {0:['0.mrc 0'], 1:['3.mrc 3'], 2:['6.mrc 6'], 3:['9.mrc 9']}
        result_4bins = sh.calculate_bins(img_list, star_body, 4)
        self.assertEqual(exp_4bins, result_4bins)
    def test_calculate_bins_empty_bins(self):
        '''
        >>> a = [0,3,6,6.1,9]            
        >>> for i in [0,20,40,60,80,100]:
        ...     print(np.percentile(np.array(a),i))
        ... 
        0.0
        2.4
        4.8
        6.04
        6.68
        9.0
        '''
        star_body = ['{}.mrc {}'.format(str(i),str(i)) for i in [0,3,6,6.0,9]] 
        img_list = [('{}.mrc'.format(i), float(i)) for i in [0,3,6,6.0,9]]
        exp_5bins = {0:['0.mrc 0'], 1:['3.mrc 3'], 2:['6.mrc 6', '6.0.mrc 6.0'], 3:[],
                     4:['9.mrc 9']}
        result_5bins = sh.calculate_bins(img_list, star_body, 5)
        self.assertEqual(exp_5bins, result_5bins)