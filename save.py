#from saleae import automation
from datetime import datetime

#from dev_saleae import Saleae_Setup, Saleae_StartCapture, Saleae_StopCapture
#from dev_ellisys import Ellisys_Setup, Ellisys_StartCapture, Ellisys_StopCapture

import os
import os.path
import sys
import time
#import psutil
#import subprocess
import openpyxl
import Ice
from pywinauto.keyboard import send_keys

# Define the Vendor ID (VID) of the USB device you want to check
SALEAE_VID = "21A9"
SALEAE_PID = "1006"
ELLISYS_VID = "1500"
ELLISYS_PID = "0600"
CY4500_VID = "04B4"
CY4500_PID = "F67E"
String_Ellisys = 'Ellisys C-Tracker'
String_SALEAE = 'Saleae Logic'

Ice.loadSlice("--all -I. AnalyzerRemoteControl.ice")

import Ellisys.Platform.NetworkRemoteControl.Analyzer
        
def SaveToFile(self, main_window):
    currentdate = datetime.now().strftime("%Y%m%d")  # Format the current date as desired
    precisetime = datetime.now().strftime("%Y%m%d_%H%M%S")
#    sheetname = precisetime
    
    # Store output in a timestamped directory
    output_dir = os.path.join(os.getcwd(), f'{currentdate}')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    #output_dir = os.getcwd()
    output_prefix = f'{datetime.now().strftime("%Y%m%d_%H%M%S_")+ self.logsuffix}'

    # # we are in a new case log collecting process. the self.sheetname will be cleared if any change at information
    # if self.sheetname == '':
        # output_prefix = precisetime + '_' + self.logsuffix
    # else:
        # output_prefix = self.sheetname + '_' + self.logsuffix
        
    if self.recorddevice == String_SALEAE:
        if main_window != None:
            capture_filepath = os.path.join(output_dir, output_prefix + '.ccgx3')
# #            main_window.set_focus()
            # main_window.type_keys('^q')
            # time.sleep(0.5)
            # main_window.type_keys('^s')
            # time.sleep(0.5)

            # child_window = main_window.child_window(title="Save", control_type="Window")
            # child_window.type_keys(capture_filepath)
# #            send_keys(capture_filepath, pause=0.01)  # Type the desired file name into the Save dialog
            # # Send Enter to save the file
# #            send_keys("{ENTER}")
            # child_window.type_keys("{ENTER}")

# # Click ENTER again as hit OK in Save confirmation dialog
# #            time.sleep(3)
# #            send_keys("{ENTER}")
            # check_for_child_window(10, main_window)
            
            Logger_CaptureSettings(self, output_prefix + '.ccgx3', False)
            
            return capture_filepath
        else:
            capture = self.capture

            # # Export analyzer data to a CSV file
            # analyzer_export_filepath = os.path.join(output_dir, output_prefix +'.csv')
            
            analyzers = []
            
            for i in range(0, len(self.enabled_ch_i2c), 2):
                settings = {
                    'SDA': self.enabled_ch_i2c[i],
                    'SCL': self.enabled_ch_i2c[i+1],
                    'Significant Byte': 'Most Significant Byte Sent First',
                    'Bytes per Frame': '4 Bytes per Frame (Default)'
                }

                try:
                    analyzer = capture.add_analyzer('I2C_HPI', settings=settings)
                except:
                    # use standard I2C analyzer if customised one is not installed
                    settings = {
                        'SDA': self.enabled_ch_i2c[i],
                        'SCL': self.enabled_ch_i2c[i+1]
                    }
                    analyzer = capture.add_analyzer('I2C', settings=settings)

                analyzers.append(analyzer)

            for i in range(len(self.enabled_ch_cc)):
                settings = {
#                    'Manchester': self.enabled_ch_cc[i]
                    'CC Channel': self.enabled_ch_cc[i]
                }

                try:
#                    analyzer = capture.add_analyzer('Manchester_PD_CC', settings=settings)
                    analyzer = capture.add_analyzer('Saleae_PDCC_Release', settings=settings)
                    analyzers.append(analyzer)
                except:
                    # do not add cc analyser if CC analyser is not installed
                    pass

            # try:
                # capture.export_data_table(filepath=analyzer_export_filepath, analyzers=analyzers)
            # except:
                # # do not export to .csv file if no analyser is attached
                # pass
                
            # Finally, save the capture to a file
            capture_filepath = os.path.join(output_dir, output_prefix + '.sal')
            capture.save_capture(filepath=capture_filepath)

            Logger_CaptureSettings(self, output_prefix + '.sal', True)

    elif self.recorddevice == String_Ellisys:
    
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
        
        capture_filepath = os.path.join(output_dir, output_prefix + '.ctrt')
        remoteControl.StopRecordingAndSaveTraceFile(capture_filepath, True)
        Logger_CaptureSettings(self, output_prefix + '.ctrt', False)


    if self.recorddevice == String_SALEAE:
        if main_window != None:
            str_suffix = '.ccgx3\r\n'
        else:
            str_suffix = '.sal\r\n'
    elif self.recorddevice == String_Ellisys:
        str_suffix = '.ctrt\r\n'
    
#    self.allrecords += output_prefix + '.sal\r\n'
    trackerformhdr = currentdate + '_' + self.project + '.xlsx'
    tracker_filepath = os.path.join(output_dir, trackerformhdr)
    
    # a tracker form with same project name is already existed
    if os.path.exists(tracker_filepath):
        # Load the workbook
        workbook = openpyxl.load_workbook(tracker_filepath)      

        # we are in a new case log collecting process. the self.sheetname will be cleared if any change at information
        if self.sheetname == '':
            # Select the sheet you want to duplicate
            original_sheet = workbook['Blank']
            self.allrecords = output_prefix + str_suffix
            # Create a new sheet
            new_sheet = workbook.copy_worksheet(original_sheet)
            # Rename the new sheet using the current date
            new_sheet.title = precisetime
            self.sheetname = precisetime
        # we are in the same case process
        else:
            new_sheet = workbook[self.sheetname]
            self.allrecords += output_prefix + str_suffix
            
    # tracker form doesn't exist
    else:
        self.allrecords = output_prefix + str_suffix
       # Load the workbook
        workbook = openpyxl.load_workbook('tracker_form.xlsx')
        # Select the sheet you want to duplicate
        original_sheet = workbook['Blank']
        # Create a new sheet
        new_sheet = workbook.copy_worksheet(original_sheet)
        # Rename the new sheet using the current date
        new_sheet.title = precisetime
        self.sheetname = precisetime

    if self.otherportsel:
        additionalInfo = '\r\nSame failure on other port(s)'
    else:
        additionalInfo = '\r\nNot see the same symptom on other port(s)'

    # Update cells value
    new_sheet['B1'] = self.project
    new_sheet['B2'] = self.ecver
    new_sheet['B3'] = self.pdver
    new_sheet['B4'] = self.ticket
    new_sheet['B5'] = self.port + additionalInfo
    new_sheet['B6'] = self.issue
    new_sheet['B7'] = self.failrate
    new_sheet['B8'] = self.device
    new_sheet['B9'] = self.replication
    new_sheet['B10'] = self.ui.cB_OtherDevSel.currentText() + '\r\n' + self.otherdev
    new_sheet['B11'] = self.recovery
    new_sheet['B12'] = self.ui.cB_DiffStepSel.currentText() + '\r\n' + self.diffstep
    new_sheet['B13'] = self.allrecords
    new_sheet['B14'] = 'as above'
    new_sheet['B15'] = 'n/a'
        
    workbook.active = workbook.index(workbook[self.sheetname])
    # Save the changes
    workbook.save(tracker_filepath)

def Logger_CaptureSettings(self, log_name, ch_details):
    # Store output in a timestamped directory
    output_dir = os.path.join(os.getcwd(), f'{datetime.now().strftime("%Y%m%d")}')
    logfile = os.path.join(output_dir, f'{datetime.now().strftime("%Y%m%d")}' + '.txt')

    if os.path.exists(logfile):
        oper = 'a'
    else:
        oper = 'w'
    
    with open(logfile, oper) as f:
        sys.stdout = f
        print(log_name)

        if self.recorddevice == String_SALEAE and ch_details:
            if self.platform == 'INTEL':               # INTEL 
                print(' CC1:', self.icc1, '\tRIDGE INT:', self.rint, '\tBBR PWR:', self.bpwr)
                print(' CC2:', self.icc2, '\tRIDGE SDA:', self.rsda, '\tBBR RST:', self.brst)
                print('SBU1:', self.isbu1, '\tRIDGE CLK:', self.rclk, '\tBBR SDA:', self.bsda)
                print('SBU2:', self.isbu2, '\t\t\t\t\tBBR CLK:', self.bclk)
                print('VBUS:', self.ivbus),
                print(' INT:', self.ecint),
                print(' SDA:', self.ecsda),
                print(' CLK:', self.ecclk),
                print('UART:', self.pduart)
            elif self.platform == 'AMD':                # AMD
                print(' CC1:', self.icc1, '\t  APU INT:', self.aint, '\tMUX PWR:', self.mpwr)
                print(' CC2:', self.icc2, '\t  APU RST:', self.arst, '\tMUX SDA:', self.msda)
                print('SBU1:', self.isbu1, '\t  APU SDA:', self.asda, '\tMUX CLK:', self.mclk)
                print('SBU2:', self.isbu2, '\t  APU CLK:', self.aclk)
                print('VBUS:', self.ivbus)
                print(' INT:', self.ecint),
                print(' SDA:', self.ecsda),
                print(' CLK:', self.ecclk),
                print('UART:', self.pduart)
        print('')
        sys.stdout = sys.__stdout__
    