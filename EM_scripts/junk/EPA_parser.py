class yadda(object):
    
    def __init__(self):
        super(yadda, self).__init__()
        self.epa_files = ['/processing/michael/20160308_nucleo_xlink_d2/relion/Micrographs/20160308_nucleo_xlink_d2_0278_corr_ctffind3.log',
                          '/processing/michael/20160308_nucleo_xlink_d2/relion/Micrographs/20160308_nucleo_xlink_d2_0279_corr_ctffind3.log']
    
    def parse_EPA(self):
        self.p_float = {}
        for i in self.epa_files:
            with open(i, 'r') as epa:
                p = {}
                while True:
                    line= epa.readline()
                    if not line:
                        break
                    if 'Input image file name' in line:
                        p['image_in'] = epa.readline().strip()
                    if 'Output diagnostic file name' in line:
                        p['ctf_out'] = epa.readline().strip()
                    if 'CS[mm], HT[kV], AmpCnst, XMAG, DStep[um]' in line:
                        p['Cs'], p['kV'], p['AC'], p['XMAG'], p['Dstep'] = epa.readline().split()
                    if 'Box, ResMin[A], ResMax[A]' in line:
                        p['box'], p['resmin'], p['resmax'], p['dfmin'], p['dfmax'], \
                        p['fstep'], p['dast'] = epa.readline().split()
                    if 'Defocus_U   Defocus_V       Angle         CCC' in line:
                        p['defU'], p['defV'], p['angle'], p['CCC'] = epa.readline().split()[:-2]
                    if 'Resolution limit estimated by EPA:' in line:
                        p['res'] = line.split()[-1]
                p_float = {}
                for key in p:
                    if key not in ['image_in', 'ctf_out']:
                        p_float[key]= float(p[key])
                    else:
                        p_float[key] = p[key]
                self.p_float[i] = p_float
        return self.p_float

    def make_ctf_line(self, i):
        line = '{image_in} {ctf_out}:mrc {defU:.6f} {defV:.6f}    {angle:.6f}   {kV:.6f}     {Cs:.6f}     {AC:.6f} {XMAG:.6f}    {Dstep:.6f}     {CCC:.6f}     {res:.6f}\n'.format(**self.p_float[i])
        return line
            
t278 = 'Micrographs/20160308_nucleo_xlink_d2_0278_corr.mrc Micrographs/20160308_nucleo_xlink_d2_0278_corr.ctf:mrc 34078.136719 34476.722656    65.307114   300.000000     2.700000     0.100000 125000.000000    14.000000     0.115909     4.354611\n'
t279 = 'Micrographs/20160308_nucleo_xlink_d2_0279_corr.mrc Micrographs/20160308_nucleo_xlink_d2_0279_corr.ctf:mrc 23189.490234 22929.724609    11.026253   300.000000     2.700000     0.100000 125000.000000    14.000000     0.117471     3.886334\n'                                                                           
y = yadda()
y.parse_EPA()
d0 = y.make_ctf_line(y.p_float.keys()[0])
d1 = y.make_ctf_line(y.p_float.keys()[1]) 
with open('/tmp/temp.txt','w') as l:
    l.write(d0)
    l.write(t278)
    l.write(d1)
    l.write(t279)
