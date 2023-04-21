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
    parser.add_argument('-f', required=True, help="", dest='input_dir')
    parser.add_argument('-c', required=True, help="", dest='channel')

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
            # Add an analyzer to the capture
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
        