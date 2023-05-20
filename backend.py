from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer, QObject

from ui import Ui_Dg_Main
from run import *
from saleae import automation
from datetime import datetime

import os
import os.path
import time
#import re

class MainWindow_controller(QtWidgets.QMainWindow):
    def closeEvent(self, event):
        # if accendentically close app while running
        if self.is_running:
            self.on_timerStopCapture()
        
    def __init__(self):
        super().__init__() # in python3, super(Class, self).xxx = super().xxx
        self.ui = Ui_Dg_Main()
        self.ui.setupUi(self)

        self.cBset = ['cB_ICC1', 'cB_ICC2', 'cB_ISBU1', 'cB_ISBU2', 'cB_IVBUS',\
                    'cB_AINT', 'cB_ARST', 'cB_ASDA', 'cB_ACLK', 'cB_AHPD', 'cB_MPWR', 'cB_MRST', 'cB_MSDA', 'cB_MCLK',\
                    'cB_RINT', 'cB_RSDA', 'cB_RCLK', 'cB_BPWR', 'cB_BRST', 'cB_BSDA', 'cB_BCLK',\
                    'cB_Platform'\
                    ]
        self.lineEset = ['lineE_PDver','lineE_ECver', 'lineE_PCHver', 'lineE_HWver', 'lineE_Ticket', 'lineE_Project']
#        self.cBvars = [self.icc1, self.icc2, self.isbu1, self.isbu2, self.ivbus,\
#                    self.aint, self.arst, self.asda, self.aclk, self.ahpd, self.mpwr, self.mrst, self.msda, self.mclk,\
#                    self.rint, self.rsda, self.rclk, self.bpwr, self.brst, self.bsda, self.bclk,\
#                    self.platform\
#                    ]
#        self.lineEvars = [self.pdver, self.ecver, self.pchver, self.hwver, self.ticket, self.project]

        self.setup_control()

        self.cB_SelectionChanged()
        
        self.is_running = False
        self.saleae_is_running = False
        self.apistr = ""

        #saleae parameters
        self.manager = 0
        self.sdevice = 0
        self.config = 0
        self.capture = 0
        self.capture_setting = 0
        self.enabled_ch = self.enabled_ch_i2c = self.enabled_ch_cc = []
        
        self.logsuffix = ''
       
    def setup_control(self):
        for element_name in self.cBset:
            hdr = getattr(self.ui, element_name)
            hdr.currentIndexChanged.connect(self.on_stateChanged)

        for element_name in self.lineEset:
            hdr = getattr(self.ui, element_name)
            hdr.textChanged.connect(self.on_stateChanged)
        
        self.ui.pB_Run.clicked.connect(self.on_pB_Run)

        self.timerStartCapture = QTimer()
        self.timerStartCapture.timeout.connect(self.on_timerStartCapture)
        self.timerStopCapture = QTimer()
        self.timerStopCapture.timeout.connect(self.on_timerStopCapture)
        
    def on_stateChanged(self):
        self.ui.gB_INTEL.setEnabled(self.ui.cB_Platform.currentIndex())
        self.ui.gB_AMD.setEnabled(not self.ui.cB_Platform.currentIndex())
    
        self.cB_SelectionChanged()
    
        if (self.pdver != '') and (self.ecver != '') and (self.pchver != '') and (self.hwver != '') and (self.project != ''):
            if self.ui.cB_Platform.currentText() == 'INTEL':      # INTEL platform
                if len(set([self.icc1, self.icc2, self.isbu1, self.isbu2, self.ivbus,\
                            self.rint, self.rsda, self.rclk, self.bpwr, self.brst, self.bsda, self.bclk\
                            ])) == 12:
                    self.ui.pB_Run.setEnabled(True)
                else:
                    self.ui.pB_Run.setEnabled(False)
            elif self.ui.cB_Platform.currentText() == 'AMD':      # AMD platform
                if len(set([self.icc1, self.icc2, self.isbu1, self.isbu2, self.ivbus,\
                            self.aint, self.arst, self.asda, self.aclk, self.ahpd, self.mpwr, self.mrst, self.msda, self.mclk\
                            ])) == 14:
                    self.ui.pB_Run.setEnabled(True)
                else:
                    self.ui.pB_Run.setEnabled(False)
            self.platform = self.ui.cB_Platform.currentText()
        else:
            self.ui.pB_Run.setEnabled(False)
        
    def cB_SelectionChanged(self):
    
        self.icc1 = self.ui.cB_ICC1.currentIndex()
        self.icc2 = self.ui.cB_ICC2.currentIndex()
        self.isbu1 = self.ui.cB_ISBU1.currentIndex()
        self.isbu2 = self.ui.cB_ISBU2.currentIndex()
        self.ivbus = self.ui.cB_IVBUS.currentIndex()

        self.platform = self.ui.cB_Platform.currentText()
        
        self.aint = self.ui.cB_AINT.currentIndex()
        self.arst = self.ui.cB_ARST.currentIndex()
        self.asda = self.ui.cB_ASDA.currentIndex()
        self.aclk = self.ui.cB_ACLK.currentIndex()
        self.ahpd = self.ui.cB_AHPD.currentIndex()
        self.mpwr = self.ui.cB_MPWR.currentIndex()
        self.mrst = self.ui.cB_MRST.currentIndex()
        self.msda = self.ui.cB_MSDA.currentIndex()
        self.mclk = self.ui.cB_MCLK.currentIndex()
               
        self.rint = self.ui.cB_RINT.currentIndex()
        self.rsda = self.ui.cB_RSDA.currentIndex()
        self.rclk = self.ui.cB_RCLK.currentIndex()
        self.bpwr = self.ui.cB_BPWR.currentIndex()
        self.brst = self.ui.cB_BRST.currentIndex()
        self.bsda = self.ui.cB_BSDA.currentIndex()
        self.bclk = self.ui.cB_BCLK.currentIndex()
    
        self.pdver = self.ui.lineE_PDver.text()
        self.ecver = self.ui.lineE_ECver.text()
        self.pchver = self.ui.lineE_PCHver.text()
        self.hwver = self.ui.lineE_HWver.text()
        self.ticket = self.ui.lineE_Ticket.text()
        self.project = self.ui.lineE_Project.text()

    def on_pB_Run(self):
        self.is_running = not self.is_running

        if self.is_running:
            self.logsuffix += self.project + '_' \
                            + self.platform \
                            + '_PD' + self.pdver \
                            + '_EC' + self.ecver \
                            + '_PCH' + self.pchver \
                            + '_HW' + self.hwver \
                            + '_Ticket' + self.ticket
            
            self.ui.pB_Run.setText("Stop")
            self.ui.pB_Run.setEnabled(False)
            self.ui.gB_Generic.setEnabled(False)
            self.ui.gB_AMD.setEnabled(False)
            self.ui.gB_INTEL.setEnabled(False)

            self.timerStartCapture.start(10)
        else:
            self.timerStopCapture.start(10)

    def on_timerStartCapture(self):
        self.timerStartCapture.stop()
        
        # check if saleae is running or not
        self.saleae_is_running = chk_SaleaeLogicRunning(self)
        
        if self.saleae_is_running:
            self.apistr = 'connect'         # run automation.Manager.connect()
        else:
            self.apistr = 'launch'          # run automation.Manager.launch()
            
        # init saleae
        self.manager, self.sdevice, self.config, self.capture_settings, \
        self.enabled_ch, self.enabled_ch_i2c, self.enabled_ch_cc = Saleae_Setup(self)
        self.capture = Saleae_StartCapture(self)

        self.ui.pB_Run.setEnabled(True)
        
    def on_timerStopCapture(self):
        self.timerStopCapture.stop()
        Saleae_StopCapture(self)      
        
        if not self.saleae_is_running:
            self.manager = Saleae_Close(self)
        
        self.logsuffix = ''
        self.ui.pB_Run.setText("Run")
        self.ui.gB_Generic.setEnabled(True)
        self.ui.gB_INTEL.setEnabled(self.ui.cB_Platform.currentIndex())
        self.ui.gB_AMD.setEnabled(not self.ui.cB_Platform.currentIndex())
