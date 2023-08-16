# Import libraries
from saleae import automation
#from datetime import datetime

import os
import os.path
#import sys
#import time
import psutil
import subprocess
#import openpyxl
from save import SaveToFile
   
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

    if self.savetofile:
        SaveToFile(self, None)

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
