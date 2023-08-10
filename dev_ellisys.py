from datetime import datetime

import os
import os.path
#import time
import psutil
import subprocess
#import openpyxl

#import sys, traceback
import traceback
import Ice

from save import SaveToFile

Ice.loadSlice("--all -I. AnalyzerRemoteControl.ice")

import Ellisys.Platform.NetworkRemoteControl.Analyzer
    
def trim_brackets(input_list):
    # Check if the input_list is a list with exactly one element
    if isinstance(input_list, list) and len(input_list) == 1 and isinstance(input_list[0], str):
        # Use replace() to remove [' and '] from the string element
        trimmed_string = input_list[0].replace("['", "").replace("']", "")
        return trimmed_string
    else:
        # If the input format is not as expected, return the original list
        return input_list    

def search_and_run_ellisys(self):
    app_args = ['/remote_control_port=54321']    # List of directories to search in

    program_files_path = os.environ.get('ProgramFiles(x86)')
    ellisys_bin = os.path.join(program_files_path, 'Ellisys\Ellisys Type-C Tracker Analyzer', 'Ellisys.TypeCTrackerAnalyzer.exe')
    process = subprocess.Popen([ellisys_bin] + app_args)
    self.need_close_ellisys_while_exit = True

def close_ellisys_thread(self):
    # Provide the name of the application you want to close
    app_name = 'Ellisys.TypeCTrackerAnalyzer.exe'

    # Iterate over all running processes
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == app_name:
            proc.kill()
#            print('Application terminated successfully.')
            self.need_close_ellisys_while_exit = False
#            return

#    print('Application not found or already terminated.')

def Ellisys_Setup(self):
    config_strings_1st = '{General: {RecordUsb20: true,RecordUsbCc: true,RecordSbu: true,RecordI2c: true,RecordI2cSecondary: true,RecordUart: true,RecordLogicPort: true,RecordStatistics: true,SbuProtocol: '

    if self.platform == 'AMD':
        config_strings_2nd = '"DpAux"'
    if self.platform == 'INTEL':
        config_strings_2nd = '"TbUart"'
        
    config_strings_3rd = ',UartBitRate: "Br115200",I2cAlertType: "ActiveLow",I2cSecondaryAlertType: "ActiveLow"    },'
    config_strings_4th = 'LogicPort: {Level: 3.3,Threshold: 1.2,GlitchFilterPeriodCount: 4,Signals: {I2cScl: { Signal: '
    config_strings_4th_ch = str(self.ecclk_ellisys)
    config_strings_4th_end = ', DisplayName: "EC SCL" },I2cSda: { Signal: '
    config_strings_5th_ch = str(self.ecsda_ellisys)
    config_strings_5th_end = ', DisplayName: "EC SDA" },I2cAlert: { Signal: '
    config_strings_6th_ch = str(self.ecint_ellisys)
    config_strings_6th_end = ', DisplayName: "EC INT" },I2cSecondaryScl: { Signal: '
    config_strings_7th_ch = str(self.ecclk2_ellisys)
    config_strings_7th_end = ', DisplayName: "PCH SCL" },I2cSecondarySda: { Signal: '
    config_strings_8th_ch = str(self.ecsda2_ellisys)
    config_strings_8th_end = ', DisplayName: "PCH SDA" },I2cSecondaryAlert: { Signal: '
    config_strings_9th_ch = str(self.ecint2_ellisys)
    config_strings_9th_end = ', DisplayName: "PCH INT" },UartOut: { Signal: '
    config_strings_10th_ch = str(self.pduart_ellisys)
    config_strings_10th_end = ', DisplayName: "Tx" },UartIn: { Signal: '
    config_strings_11th_ch = str(self.pduart_ellisys)
    config_strings_11th_end = ', DisplayName: "Rx" }        }    },BasicFilter.LimitDataPacketsPayloadSize: 32}'

    config_strings = config_strings_1st + config_strings_2nd + config_strings_3rd + config_strings_4th + config_strings_4th_ch + config_strings_4th_end +\
                        config_strings_5th_ch + config_strings_5th_end + config_strings_6th_ch + config_strings_6th_end + config_strings_7th_ch + config_strings_7th_end +\
                        config_strings_8th_ch + config_strings_8th_end + config_strings_9th_ch + config_strings_9th_end + config_strings_10th_ch + config_strings_10th_end +\
                        config_strings_11th_ch + config_strings_11th_end

    return config_strings

def Ellisys_StartCapture(self):
    Ice.loadSlice("--all -I. AnalyzerRemoteControl.ice")
    # TODO: Please adapt the following constants to your needs
    hostIp = "localhost"
    hostPort = 54321

    proxyString = "{0}:tcp -h {1} -p {2}".format(Ellisys.Platform.NetworkRemoteControl.Analyzer.AnalyzerRemoteControlIdentity, hostIp, hostPort)

    try:
        #
        # Initialize ICE
        #
        initData = Ice.InitializationData()
        initData.properties = Ice.createProperties([], initData.properties)
        initData.properties.setProperty("Ice.Default.EncodingVersion", "1.0")

        communicator = Ice.initialize(initData)
        proxy = communicator.stringToProxy(proxyString)

    #        if not (is_app_running("ellisys.typectrackeranaly")):
#        if not (chk_LogApplicationRunning("Ellisys.TypeCTrackerAnalyzer.exe")):
#            search_and_run_ellisys()

        remoteControl = Ellisys.Platform.NetworkRemoteControl.Analyzer.AnalyzerRemoteControlPrx.checkedCast(proxy)
    #        print(remoteControl)
        datasrc = remoteControl.GetAvailableDataSources()
    #        print(datasrc)
        devstr = trim_brackets(datasrc)
    #        print(devstr)
        remoteControl.SelectDataSource(devstr)

        if not remoteControl:
            sys.exit("Invalid proxy {0}".format(proxyString))

        remoteControl.ConfigureRecordingOptions(self.ellisys_configstr)
        remoteControl.StartRecording()

    except:
        traceback.print_exc()
        Ellisys_StartCapture(self)    
        # if communicator:
            # try:
                # communicator.destroy()
            # except:
                # traceback.print_exc()

def Ellisys_StopCapture(self):
#    print(self.ellisysremote)
#    remoteControl = self.ellisysremote

    Ice.loadSlice("--all -I. AnalyzerRemoteControl.ice")
    # TODO: Please adapt the following constants to your needs
    hostIp = "localhost"
    hostPort = 54321

    proxyString = "{0}:tcp -h {1} -p {2}".format(Ellisys.Platform.NetworkRemoteControl.Analyzer.AnalyzerRemoteControlIdentity, hostIp, hostPort)

    initData = Ice.InitializationData()
    initData.properties = Ice.createProperties([], initData.properties)
    initData.properties.setProperty("Ice.Default.EncodingVersion", "1.0")

    communicator = Ice.initialize(initData)
    proxy = communicator.stringToProxy(proxyString)

    remoteControl = Ellisys.Platform.NetworkRemoteControl.Analyzer.AnalyzerRemoteControlPrx.checkedCast(proxy)
    
    if self.savetofile:
        SaveToFile(self, None)
#    else:
    remoteControl.AbortRecordingAndDiscardTraceFile()