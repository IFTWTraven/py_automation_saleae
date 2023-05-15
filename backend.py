from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QProgressBar
from PyQt5.QtCore import QTimer, QObject

from ui import Ui_MainWindow
from run import *
from enum import IntEnum
from pymata4 import pymata4
from saleae import automation
from datetime import datetime

import os
import os.path
import time
import re

LED_OUTPUT_PIN = 13
IO_OUTPUT_PIN22 = 48
IO_OUTPUT_PIN24 = 50
IO_OUTPUT_PIN26 = 52

GinitValue = 1
OptionEnabled = "background-color: rgb(192, 192, 192);"
OptionGroupBox = "background-color: rgb(204, 204, 204);"
OptionDisabled = ""

OneSecond = 1000

class Channel(IntEnum):
    idx_i2c_sda1 = 16
    idx_i2c_sda2 = 17
    idx_i2c_sda3 = 18
    idx_i2c_sda4 = 19
    idx_i2c_slk1 = 20
    idx_i2c_slk2 = 21
    idx_i2c_slk3 = 22
    idx_i2c_slk4 = 23
    idx_uart1 = 24
    idx_uart2 = 25
    idx_uart3 = 26
    idx_uart4 = 27
    idx_cc1 = 28
    idx_cc2 = 29
    idx_cc3 = 30
    idx_cc4 = 31

class MainWindow_controller(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__() # in python3, super(Class, self).xxx = super().xxx
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_control()
        
        self.ch_idx_i2c_sda1 = Channel.idx_i2c_sda1
        self.ch_idx_i2c_sda2 = Channel.idx_i2c_sda2
        self.ch_idx_i2c_sda3 = Channel.idx_i2c_sda3
        self.ch_idx_i2c_sda4 = Channel.idx_i2c_sda4
        self.ch_idx_i2c_slk1 = Channel.idx_i2c_slk1
        self.ch_idx_i2c_slk2 = Channel.idx_i2c_slk2
        self.ch_idx_i2c_slk3 = Channel.idx_i2c_slk3
        self.ch_idx_i2c_slk4 = Channel.idx_i2c_slk4
            
        self.ch_idx_uart1 = Channel.idx_uart1
        self.ch_idx_uart2 = Channel.idx_uart2
        self.ch_idx_uart3 = Channel.idx_uart3
        self.ch_idx_uart4 = Channel.idx_uart4
    
        self.ch_idx_cc1 = Channel.idx_cc1
        self.ch_idx_cc2 = Channel.idx_cc2
        self.ch_idx_cc3 = Channel.idx_cc3
        self.ch_idx_cc4 = Channel.idx_cc4

        self.enabled_ch_i2c = self.enabled_ch_uart = self.enabled_ch_cc = []

        self.is_running = False
        self.counter_runs = 0
        self.counter_cycle = 0
        self.board = SetupControlBoard(self)
        # make relay in connection stage for USB list download
        self.boardconnection = True
        ConnectControl(self)
        
        #saleae parameters
        self.manager = 0
        self.sdevice = 0
        self.config = 0
        self.capture_setting = 0
        
        # system usbtree
        self.usbinit = []
        self.usbdev = []
        self.usbmiss = []
        self.logsuffix = ''
        
        self.refresh_gB()
        
    def setup_control(self):
        for prefix in ['i2c', 'uart', 'cc']:
            for widget in ['sB', 'dL']:
                getattr(self.ui, f"{widget}_{prefix}").valueChanged.connect(getattr(self, f"on_{widget}_ch_valueChanged"))
            getattr(self.ui, f"kB_{prefix}").stateChanged.connect(self.on_stateChanged)

        for prefix in ['runs', 'cycle', 'connect', 'disconnect']:
            for widget in ['hSB', 'sB']:
                getattr(self.ui, f"{widget}_{prefix}").valueChanged.connect(getattr(self, f"on_{widget}_seq_valueChanged"))

        for widget in ['kB']:
            getattr(self.ui, f"{widget}_cc").stateChanged.connect(self.on_stateChanged)

        for i in range(1, 5):
            for cb_name in ["i2c_sda", "i2c_slk"]:
                cb = getattr(self.ui, f"cB_{cb_name}{i}")
                cb.currentIndexChanged.connect(self.refresh_CHValue)
            
            for cb_name in ["uart", "cc"]:
                cb = getattr(self.ui, f"cB_{cb_name}{i}")
                cb.currentIndexChanged.connect(self.refresh_CHValue)

        self.ui.sB_runs.valueChanged.connect(self.on_sB_runs_valueChanged)

        self.ui.pB_exec.clicked.connect(self.on_pB_exec_RunSaleaeApp)
        
        self.timerInitBoard = QTimer()
        self.timerConnect = QTimer()
        self.timerDisconnect = QTimer()
        self.timerChkEnum = QTimer()
        self.timerInitBoard.timeout.connect(self.BoardInit)
        self.timerConnect.timeout.connect(self.BoardConnected)
        self.timerDisconnect.timeout.connect(self.BoardDisconnected)
        self.timerChkEnum.timeout.connect(self.ChkSystemUSBEnum)

        self.ui.lcdNum_total.display(self.ui.sB_runs.value() * self.ui.sB_cycle.value())
        
    def chkSetupParameters(self):
        # one of checkbox is checked
        if self.ui.kB_i2c.isChecked() or self.ui.kB_uart.isChecked() or self.ui.kB_cc.isChecked():
            # no duplication in channel selection
            if len(set([self.ch_idx_i2c_sda1, self.ch_idx_i2c_sda2, self.ch_idx_i2c_sda3, self.ch_idx_i2c_sda4,\
                    self.ch_idx_i2c_slk1, self.ch_idx_i2c_slk2, self.ch_idx_i2c_slk3, self.ch_idx_i2c_slk4,\
                    self.ch_idx_uart1, self.ch_idx_uart2, self.ch_idx_uart3, self.ch_idx_uart4,\
                    self.ch_idx_cc1, self.ch_idx_cc2, self.ch_idx_cc3, self.ch_idx_cc4])) == 16:
                # disconnect timeframe is 5 seconds or later than connect timeframe
                if (self.ui.sB_disconnect.value() - self.ui.sB_connect.value()) > 5:
                    self.ui.pB_exec.setEnabled(True)
                else:
                    self.ui.pB_exec.setEnabled(False)
            # channel selection duplication
            else:
                self.ui.pB_exec.setEnabled(False)
        else:
            self.ui.pB_exec.setEnabled(False)

    def updateSaleaeModel(self):
        device_type = self.sdevice[0].device_type
               
        if str(device_type) == 'DeviceType.LOGIC_PRO_16':
            model_string = 'Saleae Logic Pro 16'
        elif str(device_type) == 'DeviceType.LOGIC_PRO_8':
            model_string = 'Saleae Logic Pro 8'
        elif str(device_type) == 'DeviceType.LOGIC_16':
            model_string = 'Saleae Logic 16'
        elif str(device_type) == 'DeviceType.LOGIC_8':
            model_string = 'Saleae Logic 8'
        elif str(device_type) == 'DeviceType.LOGIC_4':
            model_string = 'Saleae Logic 4'
        elif str(device_type) == 'DeviceType.LOGIC':
            model_string = 'Saleae Logic'
        else:
            model_string = 'Demo'
        
        self.ui.label_saleae.setText(model_string + '\n' + self.sdevice[0].device_id)

    """
    # for test use
    def on_pB_exec_RunSaleaeApp(self):
        RunSaleaeAutomation(self)

    """
    def on_pB_exec_RunSaleaeApp(self):
        self.is_running = not self.is_running

        # connect to controll board and start test
        if self.is_running:
        
            self.logsuffix = ''
            self.usbmiss = []

            # get USB list then disconnect relay and ready for test start            
            self.usbinit = GetCurrentUSBTree(self)
            self.boardconnection = False       
            ConnectControl(self)
            
            # init saleae
            self.manager, self.sdevice, self.config, self.capture_settings,\
            self.enabled_ch_i2c, self.enabled_ch_uart, self.enabled_ch_cc = Saleae_Setup(self)

            self.updateSaleaeModel()

            self.timerInitBoard.start(10)
            self.ui.pB_exec.setText("Stop")
            self.ui.gB_setupch.setEnabled(False)
            self.ui.gB_setupseq.setEnabled(False)
            
        else:
            # force to reach limit and stop 
            self.counter_runs = self.ui.sB_runs.value()
            self.timerInitBoard.start(10)
#    """
    def BoardInit(self):
        self.timerInitBoard.stop()

        if self.counter_runs < (self.ui.sB_runs.value()):       
            if self.counter_cycle < (self.ui.sB_cycle.value()):
                if self.counter_cycle == 0:
                
                    # saleae capture start
                    self.capture = Saleae_StartCapture(self)

                self.timerConnect.start(OneSecond*self.ui.sB_connect.value())
                self.timerDisconnect.start(OneSecond*self.ui.sB_disconnect.value())
                # check usb enumeration 1 second ahead of disconnection
                self.timerChkEnum.start(OneSecond*(self.ui.sB_disconnect.value() - 1))
                                
                self.counter_cycle += 1
            else:
                # cycle per run limit is reached. stop saleae recording and pack to a log file
                Saleae_StopCapture(self)

                # restart for next run
                self.counter_runs += 1
                self.counter_cycle = 0

                self.logsuffix = ''
                self.usbmiss = []
                self.timerInitBoard.start(10)
        else:
            self.is_running = False
            self.ui.pB_exec.setText("Run")
            self.counter_cycle = self.counter_runs = 0
            self.ui.gB_setupch.setEnabled(True)
            self.ui.gB_setupseq.setEnabled(True)
            
            self.manager = Saleae_Close(self)

    def BoardConnected(self):
        self.timerConnect.stop()
        self.boardconnection = True
        ConnectControl(self)

        if self.is_running:
            self.ui.lcdNum_now.display((self.counter_runs * self.ui.sB_cycle.value()) + self.counter_cycle)
               
    def BoardDisconnected(self):
        self.timerDisconnect.stop()
        self.boardconnection = False       
        ConnectControl(self)

        if self.is_running:
            self.timerInitBoard.start(10)

    def ChkSystemUSBEnum(self):
        self.timerChkEnum.stop()
        self.usbdev = GetCurrentUSBTree(self)
        self.usbmiss = CompareUSBTree(self)

        if len(self.usbmiss):
            self.logsuffix += '_r' + str(self.counter_runs) + 'c' + str(self.counter_cycle) + '_'
            self.logsuffix +=  '_'.join(self.usbmiss)
            print(self.logsuffix)

    def on_sB_runs_valueChanged(self):
        self.ui.hSB_runs.setValue(self.ui.sB_runs.value())

    def on_sB_seq_valueChanged(self):
        self.ui.hSB_runs.setValue(self.ui.sB_runs.value())
        self.ui.hSB_cycle.setValue(self.ui.sB_cycle.value())
        self.ui.hSB_connect.setValue(self.ui.sB_connect.value())
        self.ui.hSB_disconnect.setValue(self.ui.sB_disconnect.value())
        self.ui.lcdNum_total.display(self.ui.sB_runs.value() * self.ui.sB_cycle.value())
        
        self.chkSetupParameters()

    def on_hSB_seq_valueChanged(self):
        self.ui.sB_runs.setValue(self.ui.hSB_runs.value())
        self.ui.sB_cycle.setValue(self.ui.hSB_cycle.value())
        self.ui.sB_connect.setValue(self.ui.hSB_connect.value())
        self.ui.sB_disconnect.setValue(self.ui.hSB_disconnect.value())
        self.ui.lcdNum_total.display(self.ui.sB_runs.value() * self.ui.sB_cycle.value())
        self.chkSetupParameters()

    def on_sB_ch_valueChanged(self):
        self.ui.dL_i2c.setValue(self.ui.sB_i2c.value())
        self.ui.dL_uart.setValue(self.ui.sB_uart.value())
        self.ui.dL_cc.setValue(self.ui.sB_cc.value())
        self.refresh_gB()

    def on_dL_ch_valueChanged(self):
        self.ui.sB_i2c.setValue(self.ui.dL_i2c.value())
        self.ui.sB_uart.setValue(self.ui.dL_uart.value())
        self.ui.sB_cc.setValue(self.ui.dL_cc.value())
        self.refresh_gB()

    def on_stateChanged(self):
        for name, sB_name, dL_name, gB_name in [('i2c', 'sB_i2c', 'dL_i2c', 'gB_i2c1'), \
                                                ('uart', 'sB_uart', 'dL_uart', 'gB_uart1'), \
                                                ('cc', 'sB_cc', 'dL_cc', 'gB_cc1')]:
            sB_widget = getattr(self.ui, sB_name)
            dL_widget = getattr(self.ui, dL_name)
            gB_widget = getattr(self.ui, gB_name)

            dL_widget.setEnabled(getattr(self.ui, f"kB_{name}").isChecked())
            sB_widget.setEnabled(getattr(self.ui, f"kB_{name}").isChecked())
            gB_widget.setEnabled(getattr(self.ui, f"kB_{name}").isChecked())

            if not getattr(self.ui, f"kB_{name}").isChecked():
                sB_widget.setValue(GinitValue)
                dL_widget.setStyleSheet(OptionDisabled)
                #gB_widget.setStyleSheet(OptionDisabled)
            else:
                dL_widget.setStyleSheet(OptionEnabled)
                #gB_widget.setStyleSheet(OptionGroupBox)

        self.refresh_gB()

    def refresh_gB(self):
        for i, widget_name in enumerate(["gB_i2c2", "gB_i2c3", "gB_i2c4"], 2):
            getattr(self.ui, widget_name).setVisible(self.ui.sB_i2c.value() >= i)
            getattr(self.ui, widget_name).setEnabled(self.ui.sB_i2c.value() >= i)

        for i, widget_name in enumerate(["gB_uart2", "gB_uart3", "gB_uart4"], 2):
            getattr(self.ui, widget_name).setVisible(self.ui.sB_uart.value() >= i)
            getattr(self.ui, widget_name).setEnabled(self.ui.sB_uart.value() >= i)

        for i, widget_name in enumerate(["gB_cc2", "gB_cc3", "gB_cc4"], 2):
            getattr(self.ui, widget_name).setVisible(self.ui.sB_cc.value() >= i)
            getattr(self.ui, widget_name).setEnabled(self.ui.sB_cc.value() >= i)

        self.refresh_CHValue()

    def refresh_CHValue(self):       
        for i in range(1, 5):
            i2c_gb = getattr(self.ui, f"gB_i2c{i}")
            uart_gb = getattr(self.ui, f"gB_uart{i}")
            cc_gb = getattr(self.ui, f"gB_cc{i}")
            
            if i2c_gb.isEnabled():
                setattr(self, f"ch_idx_i2c_sda{i}", getattr(self.ui, f"cB_i2c_sda{i}").currentIndex())
                setattr(self, f"ch_idx_i2c_slk{i}", getattr(self.ui, f"cB_i2c_slk{i}").currentIndex())
            else:
                setattr(self, f"ch_idx_i2c_sda{i}", int(getattr(Channel, f"idx_i2c_sda{i}")))
                setattr(self, f"ch_idx_i2c_slk{i}", int(getattr(Channel, f"idx_i2c_slk{i}")))
            
            if uart_gb.isEnabled():
                setattr(self, f"ch_idx_uart{i}", getattr(self.ui, f"cB_uart{i}").currentIndex())
            else:
                setattr(self, f"ch_idx_uart{i}", int(getattr(Channel, f"idx_uart{i}")))
            
            if cc_gb.isEnabled():
                setattr(self, f"ch_idx_cc{i}", getattr(self.ui, f"cB_cc{i}").currentIndex())
            else:
                setattr(self, f"ch_idx_cc{i}", int(getattr(Channel, f"idx_cc{i}")))
        
        self.chkSetupParameters()