from saleae import automation
from saleae.grpc import saleae_pb2, saleae_pb2_grpc

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
    parser.add_argument('-sda', required=True, help="", dest='sda_ch')
    parser.add_argument('-slk', required=True, help="", dest='slk_ch')

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
            i2cb_analyzer = capture.add_analyzer('HPI_I2CBurst', settings={
                'SDA': int(args.sda_ch),
                'SCL': int(args.slk_ch),
                'Significant Byte': 'Most Significant Byte Sent First',
                'Bytes per Frame': '4 Bytes per Frame (Default)'
            })
            
            for type in automation.RadixType:
                capture.legacy_export_analyzer(filepath=export_filepath, analyzer=i2cb_analyzer, radix=type)
        
    manager.close()
        