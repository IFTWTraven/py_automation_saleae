from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMessageBox
from backend import *
from logo import Ui_Dlg_logo

import sys
import time
import os

def showLogo():
    applogo = QtWidgets.QApplication(sys.argv)
    logo = QtWidgets.QMainWindow()
    ui = Ui_Dlg_logo()
    ui.setupUi(logo)
    logo.setWindowFlags(Qt.FramelessWindowHint)
    logo.show()

    logotimer = QtCore.QTimer()
    logotimer.timeout.connect(applogo.quit)
    logotimer.start(1000)

    applogo.exec_()

def runMainWindow():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow_controller()
    
    if not is_usb_device_present(SALEAE_VID, SALEAE_PID) and not is_usb_device_present(ELLISYS_VID, ELLISYS_PID):
        message = 'Please attach Saleae Logic 16 Pro or Ellisys C-Tracker and try again.'
        QMessageBox.warning(None, "No Device", message)
        sys.exit(1)

    # Saleae is being attached, and CY4500 is also required 
    if is_usb_device_present(SALEAE_VID, SALEAE_PID) and not is_usb_device_present(CY4500_VID, CY4500_PID):
        message = 'Please attach CY4500 EZ-PD Protocol Analyzer and try again.'
        QMessageBox.warning(None, "No Device", message)
        sys.exit(1)

    # Both Saleae and CY4500 are being attached, check application installation status
    elif is_usb_device_present(SALEAE_VID, SALEAE_PID) and is_usb_device_present(CY4500_VID, CY4500_PID):
        # check if EZ-PD Protocol Analyzer Utility is installed or not (check default only)
        cy4500_path = os.path.expanduser("~")  
        cy4500_bin = os.path.join(cy4500_path, 'Cypress\EZ-PD Protocol Analyzer Utility', 'CY4500_EZ_PD_Protocol_Analyzer_Utility.exe')
        if not os.path.exists(cy4500_bin):
            message = 'EZ-PD Protocol Analyzer Utility v3.0 install not found. Go to https://www.infineon.com/ to download the installer.'
            QMessageBox.warning(None, "Not Install", message)
            sys.exit(1)
        # check if SALEAE Logic2 is installed or not
        saleae_path = os.environ.get('programw6432')
        saleae_bin = os.path.join(saleae_path, 'Logic', 'Logic.exe')   
        if not os.path.exists(saleae_bin):
            message = 'Saleae Logic2 install not found. Go to https://www.saleae.com/downloads/ to download the installer.'
            QMessageBox.warning(None, "Not Install", message)
            sys.exit(1)

    # Ellisys is being attached
    if is_usb_device_present(ELLISYS_VID, ELLISYS_PID):
        # check if Ellisys Type-C Tracker Analyzer is installed or not
        ellisys_path = os.environ.get('ProgramFiles(x86)')
        ellisys_bin = os.path.join(ellisys_path, 'Ellisys\Ellisys Type-C Tracker Analyzer', 'Ellisys.TypeCTrackerAnalyzer.exe')   
        if not os.path.exists(ellisys_bin):
            message = 'Ellisys Type-C Tracker Analyzer install not found.\r\nGo to https://www.ellisys.com/better_analysis/ctra_latest.htm to download the installer.'
            QMessageBox.warning(None, "Not Install", message)   
            sys.exit(1)
        else:
            ellisys_path = os.environ.get('ProgramFiles(x86)')
            ellisys_remote1 = os.path.join(ellisys_path, 'Ellisys\Ellisys Type-C Tracker Analyzer\RemoteControl', 'EllisysAnalyzerRemoteControlPlugin.dll')
            ellisys_remote2 = os.path.join(ellisys_path, 'Ellisys\Ellisys Type-C Tracker Analyzer\RemoteControl', 'Ice.dll')
            if not os.path.exists(ellisys_remote1) or not os.path.exists(ellisys_remote2):
                message = 'Ellisys Type-C Tracker Analyzer RemoteControl plugin does not exist.'
                QMessageBox.warning(None, "Not Install", message)
                sys.exit(1)
    # All checked. 
    # Set the window flags to always stay on top
    window.setWindowFlags(window.windowFlags() | Qt.WindowStaysOnTopHint)   
    window.setWindowFlags(window.windowFlags() & ~Qt.WindowMaximizeButtonHint)
    window.show()
    
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    showLogo()
    runMainWindow()