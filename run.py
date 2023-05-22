# Import libraries
from saleae import automation
from datetime import datetime

import os
import os.path
import sys
import time
import psutil
import subprocess

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
    output_dir = os.path.join(os.getcwd(), f'{datetime.now().strftime("%Y_%m_%d")}')
    logfile = os.path.join(output_dir, f'{datetime.now().strftime("%Y_%m_%d")}' + '.txt')

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
            print('VBUS:', self.ivbus)
        elif self.platform == 'AMD':                # AMD
            print(' CC1:', self.icc1, '\t  APU INT:', self.aint, '\tMUX PWR:', self.mpwr)
            print(' CC2:', self.icc2, '\t  APU RST:', self.arst, '\tMUX RST:', self.mrst)
            print('SBU1:', self.isbu1, '\t  APU SDA:', self.asda, '\tMUX SDA:', self.msda)
            print('SBU2:', self.isbu2, '\t  APU CLK:', self.aclk, '\tMUX CLK:', self.mclk)
            print('VBUS:', self.ivbus, '\t      HPD:', self.ahpd)
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

def Saleae_StopCapture(self):
    capture = self.capture
    capture.stop()
    
    # Store output in a timestamped directory
    output_dir = os.path.join(os.getcwd(), f'{datetime.now().strftime("%Y_%m_%d")}')
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
            analyzer = capture.add_analyzer('HPI_I2CBurst', settings=settings)
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
    
    # close captured session to release memory consumption
    capture.close()

def Saleae_Close(self):
    manager = self.manager

    manager.close()
    
    return manager
       
def Saleae_Setup(self):

    digital_ch_cc = [self.icc1, self.icc2, self.isbu1, self.isbu2, self.ivbus]
    digital_ch_amd = [self.aint, self.arst, self.asda, self.aclk, self.ahpd, self.mpwr, self.mrst, self.msda, self.mclk]
    digital_ch_intel = [self.rint, self.rsda, self.rclk, self.bpwr, self.brst, self.bsda, self.bclk]

    enabled_ch_cc = [self.icc1, self.icc2]

    if self.platform == 'INTEL':               # INTEL 
        enabled_ch = digital_ch_cc + digital_ch_intel
        enabled_ch_i2c = [self.rsda, self.rclk, self.bsda, self.bclk]
    elif self.platform == 'AMD':                # AMD
        enabled_ch = digital_ch_cc + digital_ch_amd
        enabled_ch_i2c = [self.asda, self.aclk, self.msda, self.mclk]

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
