import labrad
import os
import sys
import numpy as np
from csv import *
from PyQt4 import QtGui, QtCore
from random import *
from time import *
from keithley_helper import voltage_conversion as VC
from keithley_helper import resistance_conversion as RC
from twisted.internet.defer import inlineCallbacks, returnValue

vc=VC()
rc=RC()

run_time = strftime("%d%m%Y_%H%M")
initial_time = time()
Thermometers = ["Cold Finger","Inside Heat Shield","C1","C2", "Cernox"]
    
class tempWidget(QtGui.QWidget):
    cxn_dmm = labrad.connect("192.168.169.30")
    cxn_pulser = labrad.connect()
    dmmServer = cxn_dmm.keithley_2110_dmm
    dmmServer.select_device()
    pulserServer =  cxn_pulser.pulser

    def __init__(self, parent, thermometerName):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.thermometerName = thermometerName
        self.fileDirectory = "/home/resonator/Desktop/test/"+str(self.thermometerName)+"_"+run_time+"_keithley_DMM.csv"
        self.initializeFiles()
        self.setupUI()

    def initializeFiles(self):
        numThermometers = len(Thermometers)
        for i in range(numThermometers):
            fileDirectory = "/home/resonator/Desktop/test/"+str(self.thermometerName)+"_"+run_time+"_keithley_DMM.csv"
            openFile = open(fileDirectory, "wb")
            openFile.close()

    def setupUI(self):
        tempLabel = QtGui.QLabel()
        tempLabel.setText(tempLabel.tr("Temperature (K)"))
        thermometerName = QtGui.QLabel(self.thermometerName)
        thermometerName.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))
        
        self.tempBox = QtGui.QLCDNumber(parent=self)
        self.tempBox.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=24))
        self.tempBox.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        self.tempBox.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.tempBox.setDigitCount(7)

        self.connect(self.tempBox, QtCore.SIGNAL('valueChanged(int)'), self.tempBox, QtCore.SLOT('display(int)'))

        voltageLabel = QtGui.QLabel()
        voltageLabel.setText(voltageLabel.tr("Voltage (V)"))
        self.voltageBox = QtGui.QLCDNumber(parent=self)
        self.voltageBox.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=24))
        self.voltageBox.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        self.voltageBox.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.voltageBox.setDigitCount(7)

        self.connect(self.voltageBox, QtCore.SIGNAL('valueChanged(int)'), self.voltageBox, QtCore.SLOT('display(int)'))

        self.button = QtGui.QPushButton("Get New Data", parent=self)
        self.button.clicked.connect(self.saveValues)

        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(5)
        self.grid.addWidget(tempLabel, 2, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(thermometerName, 1, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.tempBox, 2, 1, QtCore.Qt.AlignCenter)
        self.grid.addWidget(voltageLabel, 3, 0,  QtCore.Qt.AlignCenter)        
        self.grid.addWidget(self.voltageBox, 3, 1,  QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.button, 4,1, QtCore.Qt.AlignCenter)

        self.setLayout(self.grid)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.show()

    def newValue(self):
        thermometer = ""
        numThermometers = len(Thermometers)
        for i in range(numThermometers):
            thermometer = "Thermometer"+str(i+1)
            if (self.thermometerName == Thermometers[i]):
                self.pulserServer.switch_manual(thermometer, True)
            else:
                self.pulserServer.switch_manual(thermometer, False)
        self.dataSet = [0, 0]
        self.dataSet[0] = self.dmmServer.get_dc_volts()
        self.dataSet[1] =  vc.conversion(self.dataSet[0])
        self.tempBox.display(self.dataSet[1])
        self.tempBox.update()
        self.voltageBox.display(self.dataSet[0])
        self.voltageBox.update()
        for i in range (numThermometers):
            thermometer = "Thermometer"+str(i+1)
            self.pulserServer.switch_manual(thermometer, False)

        return self.dataSet

    def saveValues(self):
        openFile = open(self.fileDirectory, "ab")
        csvFile = writer(openFile, lineterminator="\n")
        elapsed_time = (time() - (initial_time))/60
        dataSet = self.newValue()
        csvFile.writerow([round(elapsed_time,4), strftime("%H"+"%M"), dataSet[0], dataSet[1]])
        print str(self.thermometerName)+": Temp = "+ str(dataSet[1]) + "(K) , Voltage = " + str(dataSet[0]) + "(V)"
        openFile.close()

class Layout(QtGui.QWidget):
    def __init__(self, reactor):
        QtGui.QWidget.__init__(self)
        self.reactor = reactor
        self.tempLayout()
    
    def tempLayout(self):
        Thermometers = ["Cold Finger","Inside Heat Shield","C1","C2", "Cernox"]
        self.setWindowTitle("Resonator Temperature")
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        self.setLayout(grid)
        numThermometers = len(Thermometers)
        for i in range(numThermometers):
            tempUI = tempWidget(self, Thermometers[i])
            if (i % 2 == 0): #even
                grid.addWidget(tempUI, (i / 2) , 0)
            else:
                grid.addWidget(tempUI, ((i - 1) / 2) , 1)
        self.setLayout(grid)
        self.show()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from twisted.internet import reactor
    mainPanel = Layout(reactor)
    mainPanel.show()
    a.exec_()
