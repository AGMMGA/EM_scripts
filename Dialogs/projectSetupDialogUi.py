# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ProjectSetupDialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(497, 156)
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(31, 14, 445, 131))
        self.widget.setObjectName("widget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.userNameLabel = QtWidgets.QLabel(self.widget)
        self.userNameLabel.setObjectName("userNameLabel")
        self.gridLayout.addWidget(self.userNameLabel, 0, 0, 1, 1)
        self.userLineEdit = QtWidgets.QLineEdit(self.widget)
        self.userLineEdit.setObjectName("userLineEdit")
        self.gridLayout.addWidget(self.userLineEdit, 0, 1, 1, 1)
        self.projectNameLabel = QtWidgets.QLabel(self.widget)
        self.projectNameLabel.setObjectName("projectNameLabel")
        self.gridLayout.addWidget(self.projectNameLabel, 1, 0, 1, 1)
        self.projectLineEdit = QtWidgets.QLineEdit(self.widget)
        self.projectLineEdit.setObjectName("projectLineEdit")
        self.gridLayout.addWidget(self.projectLineEdit, 1, 1, 1, 1)
        self.dateLabel = QtWidgets.QLabel(self.widget)
        self.dateLabel.setObjectName("dateLabel")
        self.gridLayout.addWidget(self.dateLabel, 2, 0, 1, 1)
        self.dateLineEdit = QtWidgets.QLineEdit(self.widget)
        self.dateLineEdit.setObjectName("dateLineEdit")
        self.gridLayout.addWidget(self.dateLineEdit, 2, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.folderLayout = QtWidgets.QGridLayout()
        self.folderLayout.setObjectName("folderLayout")
        self.relionLabel = QtWidgets.QLabel(self.widget)
        self.relionLabel.setObjectName("relionLabel")
        self.folderLayout.addWidget(self.relionLabel, 0, 0, 1, 1)
        self.relionLineEdit = QtWidgets.QLineEdit(self.widget)
        self.relionLineEdit.setInputMask("")
        self.relionLineEdit.setObjectName("relionLineEdit")
        self.folderLayout.addWidget(self.relionLineEdit, 0, 1, 1, 1)
        self.emanLabel = QtWidgets.QLabel(self.widget)
        self.emanLabel.setObjectName("emanLabel")
        self.folderLayout.addWidget(self.emanLabel, 1, 0, 1, 1)
        self.emanLineEdit = QtWidgets.QLineEdit(self.widget)
        self.emanLineEdit.setObjectName("emanLineEdit")
        self.folderLayout.addWidget(self.emanLineEdit, 1, 1, 1, 1)
        self.scipionLabel = QtWidgets.QLabel(self.widget)
        self.scipionLabel.setObjectName("scipionLabel")
        self.folderLayout.addWidget(self.scipionLabel, 2, 0, 1, 1)
        self.scipionLineEdit = QtWidgets.QLineEdit(self.widget)
        self.scipionLineEdit.setObjectName("scipionLineEdit")
        self.folderLayout.addWidget(self.scipionLineEdit, 2, 1, 1, 1)
        self.gridLayout_2.addLayout(self.folderLayout, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 18, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 1, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(198, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.widget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Reset)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout_2.addWidget(self.buttonBox)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 2, 0, 1, 2)
        spacerItem2 = QtWidgets.QSpacerItem(20, 18, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem2, 1, 1, 1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.userNameLabel.setText(_translate("Dialog", "User name"))
        self.projectNameLabel.setText(_translate("Dialog", "Project name"))
        self.dateLabel.setText(_translate("Dialog", "Date"))
        self.relionLabel.setText(_translate("Dialog", "Relion folder"))
        self.relionLineEdit.setText(_translate("Dialog", "relion"))
        self.emanLabel.setText(_translate("Dialog", "Eman folder"))
        self.emanLineEdit.setText(_translate("Dialog", "eman2"))
        self.scipionLabel.setText(_translate("Dialog", "Scipion folder"))
        self.scipionLineEdit.setText(_translate("Dialog", "scipion"))

