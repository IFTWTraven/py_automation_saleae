# Import libraries
from pymata4 import pymata4
from saleae import automation
from datetime import datetime

import os
import os.path
import time

LED_OUTPUT_PIN = 13
IO_OUTPUT_PIN22 = 48
IO_OUTPUT_PIN24 = 50
IO_OUTPUT_PIN26 = 52

def RunSaleaeAutomation(self):
        
    digital_channels_i2c = [
        self.ch_idx_i2c_sda1, self.ch_idx_i2c_slk1, self.ch_idx_i2c_sda2, self.ch_idx_i2c_slk2,\
        self.ch_idx_i2c_sda3, self.ch_idx_i2c_slk3, self.ch_idx_i2c_sda4, self.ch_idx_i2c_slk4\
    ]
    
    digital_channels_uart = [
        self.ch_idx_uart1, self.ch_idx_uart2, self.ch_idx_uart3, self.ch_idx_uart4\
    ]
    
    digital_channels_cc = [
        self.ch_idx_cc1, self.ch_idx_cc2, self.ch_idx_cc3, self.ch_idx_cc4\
    ]
    
#    print(self.ch_idx_i2c_sda1, self.ch_idx_i2c_sda2, self.ch_idx_i2c_sda3, self.ch_idx_i2c_sda4)
#    print(self.ch_idx_i2c_slk1, self.ch_idx_i2c_slk2, self.ch_idx_i2c_slk3, self.ch_idx_i2c_slk4)
#    print(self.ch_idx_uart1, self.ch_idx_uart2, self.ch_idx_uart3, self.ch_idx_uart4)
#    print(self.ch_idx_cc1, self.ch_idx_cc2, self.ch_idx_cc3, self.ch_idx_cc4)
    
    enabled_channels_i2c = [ch for ch in digital_channels_i2c if ch < 16]    
    enabled_channels_uart = [ch for ch in digital_channels_uart if ch < 16]    
    enabled_channels_cc = [ch for ch in digital_channels_cc if ch < 16]    
    enabled_channels = enabled_channels_i2c + enabled_channels_uart + enabled_channels_cc
    
    print(enabled_channels_i2c)
    print(enabled_channels_uart)
    print(enabled_channels_cc)
    
    device_serial = '6DE5AD1541661AFB'
    config = automation.LogicDeviceConfiguration(
        enabled_digital_channels=enabled_channels,
        digital_sample_rate=6_250_000,
        digital_threshold_volts=1.2,
    )

    capture_settings = automation.CaptureConfiguration(
        capture_mode=automation.TimedCaptureMode(duration_seconds=150.0)
    )

    analyzers = []

    manager = automation.Manager.launch()

    # Blink the LED while checking keyboard interrupts
    try:
        with manager.start_capture(
            device_id=device_serial,
            device_configuration=config,
            capture_configuration=capture_settings) as capture:               
            
            time.sleep(1)
            
            capture.stop()
            
            # Store output in a timestamped directory
            output_dir = os.path.join(os.getcwd(), f'{datetime.now().strftime("%Y_%m_%d")}')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            #output_dir = os.getcwd()
            output_prefix = f'{datetime.now().strftime("%Y_%m_%d_%H_%M_%S_")}'
            
            # Export analyzer data to a CSV file
            analyzer_export_filepath = os.path.join(output_dir, output_prefix +'.csv')
                   
            for i in range(0, len(enabled_channels_i2c), 2):
                settings = {
                    'SDA': enabled_channels_i2c[i],
                    'SCL': enabled_channels_i2c[i+1],
                    'Significant Byte': 'Most Significant Byte Sent First',
                    'Bytes per Frame': '4 Bytes per Frame (Default)'
                }

                analyzer = capture.add_analyzer('HPI_I2CBurst', settings=settings)
                analyzers.append(analyzer)
                
            for i in range(len(enabled_channels_uart)):
                settings = {
                    'Input Channel': enabled_channels_uart[i],
                    'Bit Rate (Bits/s)': 115200,
                    'Bits per Frame': '8 Bits per Transfer (Standard)',
                    'Stop Bits': '1 Stop Bit (Standard)',
                    'Parity Bit': 'No Parity Bit (Standard)',
                    'Significant Bit': 'Least Significant Bit Sent First (Standard)',
                    'Signal inversion': 'Non Inverted (Standard)',
                    'Mode': 'Normal'
                }

                analyzer = capture.add_analyzer('Async Serial', settings=settings)
                analyzers.append(analyzer)

            for i in range(len(enabled_channels_cc)):
                settings = {
                    'Manchester': enabled_channels_cc[i]
                }

                analyzer = capture.add_analyzer('Manchester_PD_CC', settings=settings)
                analyzers.append(analyzer)

            capture.export_data_table(filepath=analyzer_export_filepath, analyzers=analyzers)
            
            # Finally, save the capture to a file
            capture_filepath = os.path.join(output_dir, output_prefix +'.sal')
            capture.save_capture(filepath=capture_filepath)

        manager.close()
        
    except KeyboardInterrupt:
        # Cleanup before terminate
        board.shutdown()
        exit()
    
def SetupControlBoard(self):
    os.system('cls')

    try:
        board = pymata4.Pymata4(arduino_wait=1)
        board.set_pin_mode_digital_output(LED_OUTPUT_PIN)
        board.set_pin_mode_digital_output(IO_OUTPUT_PIN22)
        board.set_pin_mode_digital_output(IO_OUTPUT_PIN24)
        board.set_pin_mode_digital_output(IO_OUTPUT_PIN26)       
        return board
        
    except RuntimeError:
        print('demo mode')
        return 0

def ConnectControl(self):

    if self.board:
        self.board.digital_write(LED_OUTPUT_PIN, not self.boardconnection)
        self.board.digital_write(IO_OUTPUT_PIN22, self.boardconnection)
        self.board.digital_write(IO_OUTPUT_PIN24, self.boardconnection)
        self.board.digital_write(IO_OUTPUT_PIN26, self.boardconnection)
    
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
    output_prefix = f'{datetime.now().strftime("%Y_%m_%d_%H_%M_%S_")}'
    
    # Export analyzer data to a CSV file
    analyzer_export_filepath = os.path.join(output_dir, output_prefix +'.csv')
    
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
            analyzer = capture.add_analyzer('I2C', settings=settings)

        analyzers.append(analyzer)
        
    for i in range(len(self.enabled_ch_uart)):
        settings = {
            'Input Channel': self.enabled_ch_uart[i],
            'Bit Rate (Bits/s)': 115200,
            'Bits per Frame': '8 Bits per Transfer (Standard)',
            'Stop Bits': '1 Stop Bit (Standard)',
            'Parity Bit': 'No Parity Bit (Standard)',
            'Significant Bit': 'Least Significant Bit Sent First (Standard)',
            'Signal inversion': 'Non Inverted (Standard)',
            'Mode': 'Normal'
        }

        try:
            analyzer = capture.add_analyzer('Async Serial', settings=settings)
            analyzers.append(analyzer)
        except:
            pass

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

    try:
        capture.export_data_table(filepath=analyzer_export_filepath, analyzers=analyzers)
    except:
        # do not export to .csv file if no analyser is attached
        pass
    
    # Finally, save the capture to a file
    capture_filepath = os.path.join(output_dir, output_prefix +'.sal')
    capture.save_capture(filepath=capture_filepath)
    
    # close captured session to release memory consumption
    capture.close()

def Saleae_Close(self):
    manager = self.manager

    manager.close()
    
    return manager
       
def Saleae_Setup(self):

    digital_ch_i2c = [
        self.ch_idx_i2c_sda1, self.ch_idx_i2c_slk1, self.ch_idx_i2c_sda2, self.ch_idx_i2c_slk2,\
        self.ch_idx_i2c_sda3, self.ch_idx_i2c_slk3, self.ch_idx_i2c_sda4, self.ch_idx_i2c_slk4\
    ]
    
    digital_ch_uart = [
        self.ch_idx_uart1, self.ch_idx_uart2, self.ch_idx_uart3, self.ch_idx_uart4\
    ]
    
    digital_ch_cc = [
        self.ch_idx_cc1, self.ch_idx_cc2, self.ch_idx_cc3, self.ch_idx_cc4\
    ]
    
#    print(self.ch_idx_i2c_sda1, self.ch_idx_i2c_sda2, self.ch_idx_i2c_sda3, self.ch_idx_i2c_sda4)
#    print(self.ch_idx_i2c_slk1, self.ch_idx_i2c_slk2, self.ch_idx_i2c_slk3, self.ch_idx_i2c_slk4)
#    print(self.ch_idx_uart1, self.ch_idx_uart2, self.ch_idx_uart3, self.ch_idx_uart4)
#    print(self.ch_idx_cc1, self.ch_idx_cc2, self.ch_idx_cc3, self.ch_idx_cc4)
    
    enabled_ch_i2c = [ch for ch in digital_ch_i2c if ch < 16]    
    enabled_ch_uart = [ch for ch in digital_ch_uart if ch < 16]    
    enabled_ch_cc = [ch for ch in digital_ch_cc if ch < 16]    
    enabled_ch = enabled_ch_i2c + enabled_ch_uart + enabled_ch_cc
    
    manager = automation.Manager.launch()
    sdevice = manager.get_devices()
    
    if not len(sdevice):
        demo_device = automation.DeviceDesc(device_id='F4241', device_type='Demo', is_simulation=True)
        sdevice = [demo_device]
    
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
    
    
    duration_seconds = (self.ui.sB_disconnect.value() + 1) * self.ui.sB_cycle.value()
    capture_settings = automation.CaptureConfiguration(
        capture_mode = automation.TimedCaptureMode(duration_seconds)
    )

    return manager, sdevice, config, capture_settings, enabled_ch_i2c, enabled_ch_uart, enabled_ch_cc

