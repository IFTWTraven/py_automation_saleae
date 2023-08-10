import os
import os.path
#import sys
import time
#import psutil
#import subprocess
#import openpyxl

import winreg
import re
from pywinauto import Application
from pywinauto.keyboard import send_keys
from save import SaveToFile
import psutil

# Function to send CTRL+R (refresh) keyboard shortcut
def send_ctrl_r(window):
    window.type_keys('^r')

# Function to send CTRL+Q (quit) keyboard shortcut
def send_ctrl_q(window):
    window.type_keys('^q')

# Function to send CTRL+Q (quit) keyboard shortcut
def send_ctrl_s(window):
    window.type_keys('^s')

def find_running_app(app_name):
    # Check if the application is already running
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == app_name:
            return proc
            
def check_for_child_window(max_waiting_time, main_window):
    # Launch the application
#    app = launch_app()
    # Get the main window
#    main_window = app.window(title="CY4500 EZ-PD™ Protocol Analyzer Utility")
#    child_window = app.window(title="CY4500 EZ-PD™ Protocol Analyzer Utility").child_window(title="Save", control_type="Window")
    child_window = main_window.child_window(title="OK")

    if max_waiting_time:
        start_time = time.time()
        while time.time() - start_time < max_waiting_time:
            try:           
                if child_window.is_visible():
    #                print("The child_window is already visible.")
                    child_window.type_keys("{ENTER}")
                    return True
            except Exception as e:
                pass

            # Add a small delay to avoid excessive CPU usage during the loop
            time.sleep(0.1)

    #    print("The child_window did not appear within the specified time limit.")
        return False
    else:
        try:           
            if child_window.is_visible():
#                print("The child_window is already visible.")
                child_window.type_keys("{ENTER}")
            return True
        except Exception as e:
            pass
            return False
   
# Function to launch the application
def search_and_run_cysniffer():
    app_name = "EZ-PD Protocol Analyzer Utility"  # Replace this with the name of the app you're searching for
    app_name2 = "CY4500_EZ_PD_Protocol_Analyzer_Utility.exe"  # Replace this with the name of the app you're searching for
    app_title = "CY4500 EZ-PD™ Protocol Analyzer Utility"
    # Check if the application is already running
    running_app = find_running_app(app_name2)
    if running_app:
#        print(f"{app_name} is already running (PID: {running_app.info['pid']}).")
        # You can return the information about the running app if needed
        app = Application(backend="uia").connect(process=running_app.info['pid'])
        main_window = app.window(title=app_title)
        main_window.set_focus()
        try:
            main_window.restore()
        except:
            pass
        return app

    # get current user's home directory and check if default installation is existed
    cy4500_path = os.path.expanduser("~")
    cy4500_bin = os.path.join(cy4500_path, 'Cypress\EZ-PD Protocol Analyzer Utility', app_name2)

    if os.path.exists(cy4500_bin):
        app = Application(backend="uia").start(cy4500_bin)
        main_window = app.window(title=app_title)
        main_window.set_focus()
        try:
            main_window.restore()
        except:
            pass
        return app
    else:
        installation_path = find_app_installation_path_suppress(app_name)
        if installation_path != None:
            app_path = installation_path + app_name2  # Replace with the actual path of your 3rd party application
            app = Application(backend="uia").start(app_path)
            main_window = app.window(title=app_title)
            main_window.set_focus()

            try:
                main_window.restore()
            except:
                pass
            return app
        else:
            return None       

def find_app_installation_path_suppress(app_name):
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall") as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                subkey_name = winreg.EnumKey(key, i)
                with winreg.OpenKey(key, subkey_name) as subkey:
                    try:
                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        # Remove numeric characters from the display name for comparison
                        cleaned_display_name = re.sub(r'\d+', '', display_name)
                        if app_name.lower() in cleaned_display_name.lower():
                            install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                            return install_location
                    except FileNotFoundError:
                        pass
    except OSError:
        pass

    return None

def CySniffer_StartCapture():
    app = search_and_run_cysniffer()

    if app != None:
        # Get the main window
        main_window = app.window(title="CY4500 EZ-PD™ Protocol Analyzer Utility")

#        send_keys("{ENTER}")
        # check if the save confirmation dialog is still running
        check_for_child_window(0, main_window)
        send_ctrl_r(main_window)

def CySniffer_StopCapture(self):
    app = search_and_run_cysniffer()

    if app != None:
        # Get the main window
        main_window = app.window(title="CY4500 EZ-PD™ Protocol Analyzer Utility")
           
        # Bring the window into focus (optional, only if it's not already focused)
    #    main_window.set_focus()
        #Send CTRL+Q
        send_ctrl_q(main_window)
        
        if self.savetofile:
            # Bring the window into focus (optional, only if it's not already focused)
            main_window.set_focus()
            capture_filepath = SaveToFile(self, main_window)

#            main_window.set_focus()
            main_window.type_keys('^q')
            time.sleep(0.5)
            main_window.type_keys('^s')
            time.sleep(0.5)

            child_window = main_window.child_window(title="Save", control_type="Window")
            child_window.type_keys(capture_filepath)
#            send_keys(capture_filepath, pause=0.01)  # Type the desired file name into the Save dialog
            # Send Enter to save the file
#            send_keys("{ENTER}")
            child_window.type_keys("{ENTER}")

# Click ENTER again as hit OK in Save confirmation dialog
#            time.sleep(3)
#            send_keys("{ENTER}")
            check_for_child_window(10, main_window)
