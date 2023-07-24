from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from backend import MainWindow_controller
from logo import Ui_Dlg_logo

import time
import os
import win32com.client

# Define the Vendor ID (VID) of the USB device you want to check
TARGET_VID = "VID_21A9"  # Replace with the desired VID (in the format "VID_xxxx")

def check_attached_usb_device(vid):
    # Create a WMI object to access the Win32_USBHub class
    wmi = win32com.client.GetObject("winmgmts:\\\\.\\root\\cimv2")

    # Query for connected USB devices with the specified Vendor ID (VID)
    query = f"SELECT * FROM Win32_USBHub WHERE DeviceID LIKE '%{vid}%'"
    usb_devices = wmi.ExecQuery(query)

    return len(usb_devices) > 0
    
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow_controller()

    logo = QtWidgets.QMainWindow()
    ui = Ui_Dlg_logo()
    ui.setupUi(logo)
    logo.setWindowFlags(Qt.FramelessWindowHint)
#    logo.setWindowFlags(logo.windowFlags() | Qt.WindowStaysOnTopHint)   
    logo.show()

    time.sleep(1)

    # check if SALEAE Logic2 application is installed or not
    program_files_path = os.environ.get('programw6432')
#    if program_files_path is None:
#        print('"Program Files" not found')
    if program_files_path is None:
        logo.hide()
        message = '"Program Files" not found'
        QMessageBox.critical(None, "Error", message)
        sys.exit(1)

    logic2_bin = os.path.join(program_files_path, 'Logic', 'Logic.exe')
    if not os.path.exists(logic2_bin):
        message = 'Logic2 install not found. Go to https://www.saleae.com/downloads/ to download the installer.'
        QMessageBox.warning(None, "Warning", message)
    elif not check_attached_usb_device(TARGET_VID):
        message = 'Please attach Saleae Logic and try again.'
        QMessageBox.warning(None, "Warning", message)
    else:
        # Set the window flags to always stay on top
        window.setWindowFlags(window.windowFlags() | Qt.WindowStaysOnTopHint)   
        window.setWindowFlags(window.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        window.show()
        
        logo.hide()
        
        sys.exit(app.exec_())
