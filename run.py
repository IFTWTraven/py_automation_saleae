# Import libraries
#from saleae import automation
#from datetime import datetime

from dev_saleae import *
from dev_ellisys import *
from dev_cysniffer import *
from save import *

#import os
#import os.path
#import sys
#import time
import psutil
#import subprocess
#import openpyxl

def run_StartCapture(self):
    if self.recorddevice == String_SALEAE:

        CySniffer_StartCapture()

        # check if saleae is running or not
        # self.saleae_is_running = chk_LogApplicationRunning("Logic.exe")
        
        # if self.saleae_is_running:
            # self.apistr = 'connect'         # run automation.Manager.connect()
        # else:
            # search_and_run_saleae(self)
# #            self.apistr = 'launch'          # run automation.Manager.launch()
            # self.apistr = 'connect'         # run automation.Manager.connect()
            # self.saleae_is_running = True
        
        if not chk_LogApplicationRunning("Logic.exe"):
            search_and_run_saleae(self)
        self.apistr = 'connect'         # run automation.Manager.connect()
            
        # init saleae
        self.manager, self.sdevice, self.config, self.capture_settings, \
        self.enabled_ch, self.enabled_ch_i2c, self.enabled_ch_cc = Saleae_Setup(self)
        self.capture = Saleae_StartCapture(self)
        
    elif self.recorddevice == String_Ellisys:
        self.ellisys_configstr = Ellisys_Setup(self)
        if not chk_LogApplicationRunning("Ellisys.TypeCTrackerAnalyzer.exe"):
            search_and_run_ellisys(self)
        Ellisys_StartCapture(self)

def run_StopCapture(self):
    if self.recorddevice == String_SALEAE:
        Saleae_StopCapture(self)      
        CySniffer_StopCapture(self)
    elif self.recorddevice == String_Ellisys:
        Ellisys_StopCapture(self)

def chk_LogApplicationRunning(app_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == app_name.lower():
            return True
    return False
