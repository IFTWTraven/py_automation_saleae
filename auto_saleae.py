from saleae import automation

import argparse
import sys
import os
import os.path
import glob

export_path = os.getcwd()
args=None

def parseArguments ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-cc', action='store_true', help="")
    parser.add_argument('-i2c', action='store_true', help="")
    parser.add_argument('-uart', action='store_true', help="")
    parser.add_argument('-f', type=str, help="", dest='input_dir')
    parser.add_argument('-c', type=str, help="", dest='channel')
    parser.add_argument('-sda', type=str, help="", dest='sda_ch')
    parser.add_argument('-slk', type=str, help="", dest='slk_ch')

    return parser.parse_args()
    # ...

if __name__ == "__main__":

    args = parseArguments()

    directory_path = args.input_dir
    sal_files = glob.glob(os.path.join(directory_path, "*.sal"))
    manager = automation.Manager.launch()

    for file_path in sal_files: 
        salfile_path = os.path.join(os.getcwd(), args.input_dir)
        salfile_path = os.path.join(salfile_path, os.path.basename(file_path))
        output_file = salfile_path+'.csv'
        export_filepath = os.path.join(export_path, output_file)
        
        with manager.load_capture(salfile_path) as capture:
            if args.cc:
                # Add an analyzer to the capture
                cc_analyzer = capture.add_analyzer('Manchester_PD_CC', settings={
                    'Manchester': int(args.channel),
                })
                capture.export_data_table(filepath=export_filepath, analyzers=[cc_analyzer], columns=['Start','value'])
            
            if args.i2c:
                i2cb_analyzer = capture.add_analyzer('HPI_I2CBurst', settings={
                    'SDA': int(args.sda_ch),
                    'SCL': int(args.slk_ch),
                    'Significant Byte': 'Most Significant Byte Sent First',
                    'Bytes per Frame': '4 Bytes per Frame (Default)'
                })
                
                for type in automation.RadixType:
                    capture.legacy_export_analyzer(filepath=export_filepath, analyzer=i2cb_analyzer, radix=type)
            
            if args.uart:
                uart_analyzer = capture.add_analyzer('Async Serial', settings={
                    'Input Channel': int(args.channel),
                    'Bit Rate (Bits/s)': 115200,
                    'Bits per Frame': '8 Bits per Transfer (Standard)',
                    'Stop Bits': '1 Stop Bit (Standard)',
                    'Parity Bit': 'No Parity Bit (Standard)',
                    'Significant Bit': 'Least Significant Bit Sent First (Standard)',
                    'Signal inversion': 'Non Inverted (Standard)',
                    'Mode': 'Normal'
                })
                capture.export_data_table(filepath=export_filepath, analyzers=[uart_analyzer], columns=['Start','data'])
        
    manager.close()
        