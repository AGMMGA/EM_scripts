import os
import matplotlib.pyplot as plt 
import numpy as npy
from matplotlib.backends.backend_pdf import PdfPages
   
  
def on_pick(event):
#     allows clicking of points in the figure
    print ('{button} {x} {y} {xdata} {ydata}'.format( \
        button=event.button, x=event.x, y=event.y, \
        xdata=event.xdata, ydata=event.ydata))
#     annotation.set_visible(True)    
      
from starfile_edit import main
  
# x = [1,2,3]
# y = [2,4,6]
# x2 = [i+1 for i in x]
# x3 = [i+3 for i in x]
# y2 = [j+1 for j in y]
# y3 = [j+3 for j in y]
# colors = ['red', 'green', 'blue']
# labels = ['1','2','3']
#  
# fig1 = plt.figure(1)
# ax1 = fig1.add_subplot(211) 
# line1 = ax1.scatter(x,y, c='red', marker='p', s=100)
# line2 = ax1.scatter(x2,y2, c='blue', marker='o', s=100)
# line3 = ax1.scatter(x3,y3, c='green', marker='*', s=150)
#  
# for i,j in zip(x,y):
#     annotation = ax1.annotate('Coord: {x}{y}'.format(x=i, y=j), xy=(i,j), xycoords='data')
#     annotation.set_visible(True)
# fig1.canvas.mpl_connect('button_press_event', on_pick)
#  
# plt.show()

keep = [1,2,3]
remove = [4,5]
processing_dir = '/processing/andrea/20160126_BRCA1_GO/relion'
digits = 4
main(remove = [1], processing_dir=processing_dir, digits=digits)