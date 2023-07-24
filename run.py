# Import libraries
from saleae import automation
from datetime import datetime

import os
import os.path
import sys
import time
import psutil
import subprocess
import openpyxl

def search_and_run_saleae(self):
    app_args = ['--automation']    # List of directories to search in

    program_files_path = os.environ.get('programw6432')
    logic2_bin = os.path.join(program_files_path, 'Logic', 'Logic.exe')
    process = subprocess.Popen([logic2_bin] + app_args)
    self.need_close_saleae_while_exit = True
    
def close_saleae_thread(self):
    # Provide the name of the application you want to close
    app_name = 'Logic.exe'

    # Iterate over all running processes
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == app_name:
            proc.kill()
#            print('Application terminated successfully.')
            self.need_close_saleae_while_exit = False
#            return

#    print('Application not found or already terminated.')
 
def Logger_CaptureSettings(self, log_name):
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

def chk_SaleaeLogicRunning(self):
    app_name = "Logic.exe"
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == app_name.lower():
            return True
    return False
    
def Saleae_StartCapture(self):
    manager = self.manager
   
    with manager.start_capture(
        device_id = self.sdevice[0].device_id,
        device_configuration = self.config,
        capture_configuration = self.capture_settings) as capture:               
            pass
            
    return capture

def SaveToFile(self):
    currentdate = datetime.now().strftime("%Y%m%d")  # Format the current date as desired
    precisetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    sheetname = precisetime
    
    capture = self.capture
    # Store output in a timestamped directory
    output_dir = os.path.join(os.getcwd(), f'{currentdate}')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    #output_dir = os.getcwd()
    output_prefix = f'{datetime.now().strftime("%Y%m%d_%H%M%S_")+ self.logsuffix}'
    
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
            'Manchester': self.enabled_ch_cc[i]
        }

        try:
            analyzer = capture.add_analyzer('Manchester_PD_CC', settings=settings)
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

    Logger_CaptureSettings(self, output_prefix + '.sal')

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
            self.allrecords = output_prefix + '.sal\r\n'
            # Create a new sheet
            new_sheet = workbook.copy_worksheet(original_sheet)
            # Rename the new sheet using the current date
            new_sheet.title = sheetname
            self.sheetname = sheetname
        # we are in the same case process
        else:
            new_sheet = workbook[self.sheetname]
            self.allrecords += output_prefix + '.sal\r\n'
            
    # tracker form doesn't exist
    else:
        self.allrecords = output_prefix + '.sal\r\n'
       # Load the workbook
        workbook = openpyxl.load_workbook('tracker_form.xlsx')
        # Select the sheet you want to duplicate
        original_sheet = workbook['Blank']
        # Create a new sheet
        new_sheet = workbook.copy_worksheet(original_sheet)
        # Rename the new sheet using the current date
        new_sheet.title = sheetname
        self.sheetname = sheetname

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
    
def Saleae_StopCapture(self):
    capture = self.capture
    capture.stop()

    if self.savetofile:
        SaveToFile(self)

    # close captured session to release memory consumption
    capture.close()    

def Saleae_Close(self):
    manager = self.manager

    manager.close()
    
    return manager
       
def Saleae_Setup(self):

    digital_ch_cc = [self.icc1, self.icc2, self.isbu1, self.isbu2, self.ivbus, self.ecint, self.ecsda, self.ecclk, self.pduart]
    digital_ch_amd = [self.aint, self.arst, self.asda, self.aclk, self.mpwr, self.msda, self.mclk]
    digital_ch_intel = [self.rint, self.rsda, self.rclk, self.bpwr, self.brst, self.bsda, self.bclk]

    analog_ch_cc = [self.icc1, self.icc2, self.isbu1, self.isbu2, self.ivbus]
#    analog_ch_amd = [self.mpwr, self.mrst]
#    analog_ch_intel = [self.bpwr, self.brst]

    enabled_ch_cc = [self.icc1, self.icc2]
    enabled_analog_ch = analog_ch_cc

    if self.platform == 'INTEL':                                        # INTEL 
        enabled_ch = digital_ch_cc + digital_ch_intel
        enabled_ch_i2c = [self.rsda, self.rclk, self.bsda, self.bclk]
#        enabled_analog_ch = analog_ch_cc + analog_ch_intel
    elif self.platform == 'AMD':                                        # AMD
        enabled_ch = digital_ch_cc + digital_ch_amd
        enabled_ch_i2c = [self.asda, self.aclk, self.msda, self.mclk]
#        enabled_analog_ch = analog_ch_cc + analog_ch_amd
    
    try:
        hdr = getattr(automation.Manager, self.apistr)
        manager = hdr()
#        manager = automation.Manager.connect()

        sdevice = manager.get_devices()
        device_type = sdevice[0].device_type

        if not len(sdevice):
            demo_device = automation.DeviceDesc(device_id='F4241', device_type='Demo', is_simulation=True)
            sdevice = [demo_device]
        else:
            # attached saleae is 8ch, fixed ch setting for test only
            if str(device_type) != 'DeviceType.LOGIC_PRO_16' and str(device_type) != 'DeviceType.LOGIC_16':
                enabled_ch = [0, 1, 6, 7]
                enabled_ch_i2c = [6, 7]
                enabled_ch_cc = [0, 1]
            
            if (self.analogmode):
                analogue_rate_setting = 781_250
                # only Pro skus support 1.2V
                if "Pro" in sdevice:
                    config = automation.LogicDeviceConfiguration(
                        enabled_digital_channels = enabled_ch,
                        enabled_analog_channels = enabled_analog_ch,
                        digital_sample_rate = 6_250_000,
                        digital_threshold_volts = 1.2,
                        analog_sample_rate = analogue_rate_setting
                    )
                else:
                    config = automation.LogicDeviceConfiguration(
                        enabled_digital_channels = enabled_ch,
                        enabled_analog_channels = enabled_analog_ch,
                        digital_sample_rate = 5_000_000,
                        analog_sample_rate = analogue_rate_setting
                    )
            else:
                # only Pro skus support 1.2V
                if "Pro" in sdevice:
                    config = automation.LogicDeviceConfiguration(
                        enabled_digital_channels = enabled_ch,
                        digital_sample_rate = 6_250_000,
                        digital_threshold_volts = 1.2,
                    )
                else:
                    config = automation.LogicDeviceConfiguration(
                        enabled_digital_channels = enabled_ch,
                        digital_sample_rate = 5_000_000,
                    )
       
        duration_seconds = 1200     # need a number for timer capture mode
        capture_settings = automation.CaptureConfiguration(
            capture_mode = automation.TimedCaptureMode(duration_seconds)
        )

        return manager, sdevice, config, capture_settings, enabled_ch, enabled_ch_i2c, enabled_ch_cc
    except:
        return 0, 0, 0, 0, 0, 0, 0
