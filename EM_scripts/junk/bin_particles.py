import os

os.chdir('/processing/michael/20160211_NucleoXlink/relion_gautomatch')

bin1 = open ('bin1.star', 'w')
bin2 = open ('bin2.star', 'w')
bin3 = open ('bin3.star', 'w')
bin4 = open ('bin4.star', 'w')

header = '''
data_

loop_ 
_rlnMicrographName #1 
_rlnCoordinateX #2 
_rlnCoordinateY #3 
_rlnImageName #4 
_rlnDefocusU #5 
_rlnDefocusV #6 
_rlnDefocusAngle #7 
_rlnVoltage #8 
_rlnSphericalAberration #9 
_rlnAmplitudeContrast #10 
_rlnMagnification #11 
_rlnDetectorPixelSize #12 
_rlnCtfFigureOfMerit #13 
_rlnAnglePsi #14 
_rlnAutopickFigureOfMerit #15 
_rlnClassNumber #16 
'''



with open ('ptcls_stats.star', 'r') as f, \
     open ('bin1.star', 'w') as bin1, \
     open ('bin2.star', 'w') as bin2, \
     open ('bin3.star', 'w') as bin3, \
     open ('bin4.star', 'w') as bin4:
    
    bin1.write(header)
    bin2.write(header)
    bin3.write(header)
    bin4.write(header)
    
    for line in f:
        t = line.split()
        k = ' '.join(t[:-2]) + '\n'
        if float(t[16])<-5400:
            bin1.write(k)
        if float(t[16])>=-5400 and float(t[16])<-5250:
            bin2.write(k)
        if float(t[16])>=-5250 and float(t[16])<-5100:
            bin3.write(k)
        if float(t[16])>-5100:
            bin4.write(k)    