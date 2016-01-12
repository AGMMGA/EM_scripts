from PySide5 import QtGui
import os

class projectSetupDialog (projectSetupDialogUi, QtGui.QMainWindow):
    
    def __init__(self):
        super().__init__()
        
    def initializeUi(self):
        self.userNameLabel.setText()
        