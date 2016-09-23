import logging
import numpy as np
import matplotlib.pyplot as plt
import datetime
from subprocess import Popen, PIPE
from multiprocessing import Process, Queue

#suppress stupid matplotlib warning
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)


class Monitor(object):
    
    def __init__(self, logfile='logfile.txt'):
        logging.basicConfig(filename=logfile,level=logging.INFO)
        self.data_queue = Queue()

    def start_monitoring(self):
        with Popen(["nvidia-smi", "dmon", "-d", "1"], stdout=PIPE, bufsize=1, 
                                           universal_newlines=True) as p:
            i=0
            for line in p.stdout:
                if line.split()[4].isdigit():
                    i+=1
                    l = tuple([int(i) for i in line.split()])
                    self.data_queue.put((i, l[3], l[4], l[5], l[6], l[7]))
                logging.info(line)
    
    def plot_controller(self):
        sm = np.array([])
        mem = np.array([])
        enc = np.array([])
        dec = np.array([])
        x = np.array([])
#         p = plt.axis()
        _, axarr = plt.subplots(4)
        plt.ion()
        while True:
            data = (self.data_queue.get(block=True))
            x = np.append(x, data[0])
            sm = np.append(sm, data[1])
            mem = np.append(mem, data[2])
            enc = np.append(enc, data[3])
            dec = np.append(dec, data[4])
            if len(x):
                axarr[0].scatter(x, sm, c='r', marker='o')
                axarr[0].set_title('Sm')
                axarr[0].set_ylim([0,100])
                axarr[1].scatter(x, mem, c='g', marker = 'o')
                axarr[1].set_title('Memory Usage')
                axarr[2].scatter(x, enc, c='b', marker = '^')
                axarr[2].set_title('Encoding')
                axarr[3].scatter(x, dec, c='k', marker ='^')
                axarr[3].set_title('Decoding')
            plt.pause(0.05)
            
    def run_parallel(self, f1, f2):
        p1 = Process(target=f1)
        p1.start()
        p2 = Process(target=f2)
        p2.start()
        p1.join()
        p2.join()
        
        

# plt.axis([0, 10, 0, 1])
# plt.ion()
# 
# for i in range(10):
#     y = np.random.random()
#     plt.scatter(i, y)
#     plt.pause(0.05)
# 
# while True:
#     plt.pause(0.05)

if __name__ == '__main__':
    logfile_name = '{}.txt'.format(str(datetime.datetime.now().strftime('%Y_%m_%d_%H:%M')))
    user_input = input('Logfile name? [{}]'.format(logfile_name))
    if user_input:
        logfile_name = user_input
    monitor = Monitor(logfile_name)
    monitor.run_parallel(monitor.start_monitoring, monitor.plot_controller)