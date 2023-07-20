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

class MainWindow_controller(QtWidgets.QMainWindow):
    def closeEvent(self, event):
        # if accendentically close app while running
        if self.is_running:
            self.on_timerStopCapture()
    
        if self.need_close_saleae_while_exit:
            try:
                self.manager = Saleae_Close(self)
                # only kill saleae if it was opened by this script
                close_saleae_thread(self)
            except:
                pass

    def __init__(self):
        super().__init__() # in python3, super(Class, self).xxx = super().xxx
        self.ui = Ui_Dg_Main()
        self.ui.setupUi(self)

        self.cBset = ['cB_ICC1', 'cB_ICC2', 'cB_ISBU1', 'cB_ISBU2', 'cB_IVBUS',\
                    'cB_ECINT', 'cB_ECSDA', 'cB_ECCLK', 'cB_PDUART',\
                    'cB_AINT', 'cB_ARST', 'cB_ASDA', 'cB_ACLK', 'cB_MPWR', 'cB_MSDA', 'cB_MCLK',\
                    'cB_RINT', 'cB_RSDA', 'cB_RCLK', 'cB_BPWR', 'cB_BRST', 'cB_BSDA', 'cB_BCLK',\
                    'cB_OtherDevSel', 'cB_OtherPortSel', 'cB_DiffStepSel',\
                    'cB_Platform'\
                    ]
        self.lineEset = ['lineE_Project', 'lineE_PDver','lineE_ECver', 'lineE_Ticket', 'lineE_Port', 'lineE_FR']
        self.textEset = ['textE_Issue', 'textE_Device', 'textE_Replication', 'textE_Recovery', 'textE_OtherDev', 'textE_DiffStep']
#        self.cBvars = [self.icc1, self.icc2, self.isbu1, self.isbu2, self.ivbus,\
#                    self.aint, self.arst, self.asda, self.aclk, self.ahpd, self.mpwr, self.mrst, self.msda, self.mclk,\
#                    self.rint, self.rsda, self.rclk, self.bpwr, self.brst, self.bsda, self.bclk,\
#                    self.platform\
#                    ]
#        self.lineEvars = [self.pdver, self.ecver, self.pchver, self.hwver, self.ticket, self.project]

        self.setup_control()

        self.cB_SelectionChanged()
        
        self.ui.gB_INTEL.setVisible(False)
        self.ui.gB_AMD.setVisible(True)

        self.is_running = False
        self.saleae_is_running = False
        self.need_close_saleae_while_exit = False
        self.apistr = ""
        self.savetofile = False

        #saleae parameters
        self.manager = 0
        self.sdevice = 0
        self.config = 0
        self.capture = 0
        self.capture_setting = 0
        self.enabled_ch = self.enabled_ch_i2c = self.enabled_ch_cc = []
        
        self.logsuffix = ''
        self.allrecords = ''
        self.sheetname = ''
       
    def setup_control(self):
        for element_name in self.cBset:
            hdr = getattr(self.ui, element_name)
            hdr.currentIndexChanged.connect(self.on_stateChanged)

        for element_name in self.lineEset:
            hdr = getattr(self.ui, element_name)
            hdr.textChanged.connect(self.on_stateChanged)
        
        for element_name in self.textEset:
            hdr = getattr(self.ui, element_name)
            hdr.textChanged.connect(self.on_stateChanged)

        self.ui.chkB_HighRes.stateChanged.connect(self.on_stateChanged)
        self.ui.pB_Run.clicked.connect(self.on_pB_Run)
        self.ui.pB_Pass.clicked.connect(self.on_pB_Pass)
        self.ui.pB_Fail.clicked.connect(self.on_pB_Fail)

        self.timerStartCapture = QTimer()
        self.timerStartCapture.timeout.connect(self.on_timerStartCapture)
        self.timerStopCapture = QTimer()
        self.timerStopCapture.timeout.connect(self.on_timerStopCapture)
        self.timerSaveCapture = QTimer()
        self.timerSaveCapture.timeout.connect(self.on_timerSaveCapture)

    def on_stateChanged(self):
    
        self.cB_SelectionChanged()

        self.ui.gB_INTEL.setVisible(self.ui.cB_Platform.currentIndex())
        self.ui.gB_AMD.setVisible(not self.ui.cB_Platform.currentIndex())
        self.ui.textE_OtherDev.setEnabled(self.ui.cB_OtherDevSel.currentIndex())
        self.ui.textE_DiffStep.setEnabled(self.ui.cB_DiffStepSel.currentIndex())

        if self.otherdevsel and self.diffstepsel:
            ifcondition = ((self.otherdev != '') and (self.diffstep != ''))
        
        if not self.otherdevsel and self.diffstepsel:
            ifcondition = (self.diffstep != '')
        
        if self.otherdevsel and not self.diffstepsel:
            ifcondition = (self.otherdev != '')
                        
        if not self.otherdevsel and not self.diffstepsel:
            ifcondition = True
            
        if((self.project != '') and (self.pdver != '') and (self.ecver != '') and (self.port != '') and (self.failrate != '')\
                        and (self.issue != '') and (self.device != '') and (self.replication != '') and (self.recovery != '')\
                        and ifcondition):
# for test only
#        if ifcondition:
            if self.ui.cB_Platform.currentText() == 'INTEL':      # INTEL platform
                if len(set([self.icc1, self.icc2, self.isbu1, self.isbu2, self.ivbus,\
                            self.ecint, self.ecsda, self.ecclk, self.pduart,\
                            self.rint, self.rsda, self.rclk, self.bpwr, self.brst, self.bsda, self.bclk\
                            ])) == 16:
                    self.ui.pB_Run.setEnabled(True)
                else:
                    self.ui.pB_Run.setEnabled(False)
            elif self.ui.cB_Platform.currentText() == 'AMD':      # AMD platform
                if len(set([self.icc1, self.icc2, self.isbu1, self.isbu2, self.ivbus,\
                            self.ecint, self.ecsda, self.ecclk, self.pduart,\
                            self.aint, self.arst, self.asda, self.aclk, self.mpwr, self.msda, self.mclk\
                            ])) == 16:
                    self.ui.pB_Run.setEnabled(True)
                else:
                    self.ui.pB_Run.setEnabled(False)
            self.platform = self.ui.cB_Platform.currentText()
        else:
            self.ui.pB_Run.setEnabled(False)
        
    def cB_SelectionChanged(self):
        self.platform = self.ui.cB_Platform.currentText()
        self.project = self.ui.lineE_Project.text()
        self.pdver = self.ui.lineE_PDver.text()
        self.ecver = self.ui.lineE_ECver.text()
        self.ticket = self.ui.lineE_Ticket.text()
        self.port = self.ui.lineE_Port.text()
        self.failrate = self.ui.lineE_FR.text()
        
        self.issue = self.ui.textE_Issue.toPlainText()
        self.device = self.ui.textE_Device.toPlainText()
        self.replication = self.ui.textE_Replication.toPlainText()
        self.recovery = self.ui.textE_Recovery.toPlainText()
        self.otherdevsel = self.ui.cB_OtherDevSel.currentIndex()
        self.otherdev = self.ui.textE_OtherDev.toPlainText()
        self.otherportsel = self.ui.cB_OtherPortSel.currentIndex()
        self.diffstepsel = self.ui.cB_DiffStepSel.currentIndex()
        self.diffstep = self.ui.textE_DiffStep.toPlainText()
        
        self.icc1 = self.ui.cB_ICC1.currentIndex()
        self.icc2 = self.ui.cB_ICC2.currentIndex()
        self.isbu1 = self.ui.cB_ISBU1.currentIndex()
        self.isbu2 = self.ui.cB_ISBU2.currentIndex()
        self.ivbus = self.ui.cB_IVBUS.currentIndex()
        self.ecint = self.ui.cB_ECINT.currentIndex()
        self.ecsda = self.ui.cB_ECSDA.currentIndex()
        self.ecclk = self.ui.cB_ECCLK.currentIndex()
        self.pduart = self.ui.cB_PDUART.currentIndex()

        self.aint = self.ui.cB_AINT.currentIndex()
        self.arst = self.ui.cB_ARST.currentIndex()
        self.asda = self.ui.cB_ASDA.currentIndex()
        self.aclk = self.ui.cB_ACLK.currentIndex()
        self.mpwr = self.ui.cB_MPWR.currentIndex()
        self.msda = self.ui.cB_MSDA.currentIndex()
        self.mclk = self.ui.cB_MCLK.currentIndex()
               
        self.rint = self.ui.cB_RINT.currentIndex()
        self.rsda = self.ui.cB_RSDA.currentIndex()
        self.rclk = self.ui.cB_RCLK.currentIndex()
        self.bpwr = self.ui.cB_BPWR.currentIndex()
        self.brst = self.ui.cB_BRST.currentIndex()
        self.bsda = self.ui.cB_BSDA.currentIndex()
        self.bclk = self.ui.cB_BCLK.currentIndex()
    
        self.HighRes = self.ui.chkB_HighRes.isChecked()
        
        self.sheetname = ''

    def on_pB_Run(self):
        self.is_running = not self.is_running

        if self.is_running:
#            self.logsuffix += self.project + '_' + self.platform + '_PD' + self.pdver + '_EC' + self.ecver + '_Ticket' + self.ticket
            
            self.ui.pB_Run.setText("Starting...")
            self.ui.pB_Run.setEnabled(False)
            self.ui.gB_Generic.setEnabled(False)
            self.ui.gB_Info.setEnabled(False)
            self.ui.gB_AMD.setEnabled(False)
            self.ui.gB_INTEL.setEnabled(False)
            self.ui.chkB_HighRes.setEnabled(False)

            self.timerStartCapture.start(10)
        else:
            self.savetofile = False
            self.timerStopCapture.start(10)

    def on_pB_Pass(self):
        self.is_running = not self.is_running
        self.logsuffix += 'Pass_' + self.project + '_' + self.platform + '_PD' + self.pdver + '_EC' + self.ecver + '_Ticket' + self.ticket

        self.savetofile = True
        self.timerStopCapture.start(10)

    def on_pB_Fail(self):
        self.is_running = not self.is_running
        self.logsuffix += 'Fail_' + self.project + '_' + self.platform + '_PD' + self.pdver + '_EC' + self.ecver + '_Ticket' + self.ticket

        self.savetofile = True
        self.timerStopCapture.start(10)
            
    def on_timerStartCapture(self):
        self.timerStartCapture.stop()
        
        # check if saleae is running or not
        self.saleae_is_running = chk_SaleaeLogicRunning(self)
        
        if self.saleae_is_running:
            self.apistr = 'connect'         # run automation.Manager.connect()
        else:
            search_and_run_saleae(self)
#            self.apistr = 'launch'          # run automation.Manager.launch()
            self.apistr = 'connect'         # run automation.Manager.connect()
            self.saleae_is_running = True

#        if not self.saleae_is_running:                  # saleae is not running
#            search_and_run_saleae(self)                 # execute saleae logic2 with --automation argument
            
        # init saleae
        self.manager, self.sdevice, self.config, self.capture_settings, \
        self.enabled_ch, self.enabled_ch_i2c, self.enabled_ch_cc = Saleae_Setup(self)
        self.capture = Saleae_StartCapture(self)

        self.ui.pB_Run.setEnabled(True)
        self.ui.pB_Pass.setEnabled(True)
        self.ui.pB_Fail.setEnabled(True)
        self.ui.pB_Run.setText("Abort Recording")
        
    def on_timerStopCapture(self):
        self.timerStopCapture.stop()
        self.ui.pB_Run.setText("Stoping...")
        self.ui.pB_Run.setEnabled(False)
        self.ui.pB_Pass.setEnabled(False)
        self.ui.pB_Fail.setEnabled(False)
        self.timerSaveCapture.start(10)

    def on_timerSaveCapture(self):
        self.timerSaveCapture.stop()
        Saleae_StopCapture(self)      
        self.logsuffix = ''
        self.ui.pB_Run.setText("Start Recording")
        self.ui.pB_Run.setEnabled(True)
        self.ui.pB_Pass.setEnabled(False)
        self.ui.pB_Fail.setEnabled(False)
        self.ui.gB_Generic.setEnabled(True)
        self.ui.gB_Info.setEnabled(True)
        self.ui.gB_INTEL.setEnabled(True)
        self.ui.gB_AMD.setEnabled(True)
        self.ui.chkB_HighRes.setEnabled(True)
