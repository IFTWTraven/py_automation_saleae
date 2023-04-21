from collections import defaultdict
from typing import List
from saleae import automation

import argparse
import ctypes
import sys
import os
import os.path
import glob
import time

export_path = os.getcwd()
args=None

def parseArguments ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', required=True, help="",
            metavar="<input dir>",dest='input_dir')
    parser.add_argument('-c', required=True, help="",
            metavar="<analyser channel>",dest='channel')

    return parser.parse_args()
    # ...

def channel_autoscan(output_file,success_count,no_100w_count,not_75w_count):
    #re-scan all channels if assigned channel is incorrect
    start_channel_no = 0
    while success_count+no_100w_count+not_75w_count == 0:
        #print("\t>",file_path,"\r\n\t\tNo result, could be wrong CC channel assignment, retrying....")
        
        for chk_channel in range(start_channel_no, 16):
            try:
                cc_analyzer = capture.add_analyzer('Saleae_PD_CC', settings={
                    'Manchester': chk_channel,
                    'Bit Rate (Bits/s)': 1,
                })
                capture.export_data_table(filepath=export_filepath, analyzers=[cc_analyzer], columns=['Start','value'])
            
                #parse HP LPS flow
                success_count, success_lines, no_100w_count, no_100w_lines, not_75w_count, not_75w_lines = check_file(output_file)
                
                if success_count+no_100w_count+not_75w_count !=0:
                    new_valid_channel = chk_channel
                    break
            except:
                start_channel_no = chk_channel+1
                break

    return success_count, success_lines, no_100w_count, no_100w_lines, not_75w_count, not_75w_lines, new_valid_channel

def check_file(filepath):
    success_count = 0
    success_lines = []
    not_75w_count = 0
    not_75w_lines = []
    no_100w_count = 0
    no_100w_lines = []
    snk_cap_ext_line = 0

    with open(filepath, 'r') as file:
        lines = file.readlines()
        i = 0

        while i < len(lines):
            start_as_75w = False
            rise_to_100w = False
            sent_snk_cap_ext = False
            another_round = False
            
            if "| Fix [ 20000mV | 3750mA ]" in lines[i]:
                start_as_75w = True

                for j in range(i+1, len(lines)):
                    if "| Fix [ 20000mV | 3750mA ]" in lines[j]:
                        i = j - 5
                        break
                    if "HARD_RESET" in lines[j]:
                        i = j - 1
                        break
                    else:
                        if "| Fix [ 20000mV | 5000mA ]" in lines[j]:
                            rise_to_100w = True
                            rise_to_100w_line = j + 1
                            # finish check in this range. add 1 to avoid repeatedly check
                            i = j + 1
                            break
                        if "Snk_Cap_Ext	" in lines[j]:
                            sent_snk_cap_ext = True
                            snk_cap_ext_line = j + 1
                        if "| Fix [ 20000mV | 3750mA ]" in lines[j]:
                            another_round = True
                            another_round_line = j + 1
                            i = j
                            break
                            
            elif "| Fix [ 20000mV | 5000mA ]" in lines[i]:
                start_as_75w = False
                not_75w_start_line = i + 1
                for j in range(i+1, len(lines)):
                    if "| Fix [ 20000mV | 3750mA ]" in lines[j]:
                        another_round = True
                        i = j
                        break
                    if "| Fix [ 20000mV | 5000mA ]" in lines[j]:
                        another_round = True
                        i = j
                        break
                    if "HARD_RESET" in lines[j]:
                        another_round = True
                        i = j
                        break
                         
            if start_as_75w and sent_snk_cap_ext and rise_to_100w:
                success_count +=1
                success_lines.append(rise_to_100w_line)
            elif start_as_75w and sent_snk_cap_ext and rise_to_100w and not file.readlines():
                success_count +=1
                success_lines.append(rise_to_100w_line)
            elif start_as_75w and sent_snk_cap_ext and not rise_to_100w and another_round:
                no_100w_count +=1
                no_100w_lines.append(snk_cap_ext_line)
            elif start_as_75w and sent_snk_cap_ext and not rise_to_100w and not file.readlines():
                no_100w_count +=1
                no_100w_lines.append(snk_cap_ext_line)
                
            elif not start_as_75w and another_round:
                not_75w_count +=1
                not_75w_lines.append(not_75w_start_line)
                
            i += 1

    return success_count, success_lines, no_100w_count, no_100w_lines, not_75w_count, not_75w_lines

if __name__ == "__main__":

    total_pass_count = 0
    total_not_75w = 0
    total_not_100w = 0
    total_parse_files = 0
    success_count = 0
    no_100w_count = 0
    not_75w_count = 0
    
    start_time = time.time()
    
    args = parseArguments()
    last_valid_channel = int(args.channel)

    directory_path = args.input_dir
    sal_files = glob.glob(os.path.join(directory_path, "*.sal"))
    manager = automation.Manager.launch()
    # clear console 
    os.system('cls')
    
    print("========================================================================")
    print("Parsing....\r\n")

    for file_path in sal_files: 
        salfile_path = os.path.join(os.getcwd(), args.input_dir)
        salfile_path = os.path.join(salfile_path, os.path.basename(file_path))
        output_file = salfile_path+'.txt'
        export_filepath = os.path.join(export_path, output_file)
        
        try:
            with manager.load_capture(salfile_path) as capture:
                print("\t>",file_path)
                # Add an analyzer to the capture
                try:
                    cc_analyzer = capture.add_analyzer('Saleae_PD_CC', settings={
                        'Manchester': last_valid_channel,
                        'Bit Rate (Bits/s)': 1,
                    })
                    capture.export_data_table(filepath=export_filepath, analyzers=[cc_analyzer], columns=['Start','value'])
                
                    #parse HP LPS flow
                    success_count, success_lines, no_100w_count, no_100w_lines, not_75w_count, not_75w_lines = check_file(output_file)
                    
                    if success_count+no_100w_count+not_75w_count == 0:
                        print("\t  Channel",last_valid_channel,"is not CC, scan others....")
                        success_count, success_lines, no_100w_count, no_100w_lines, not_75w_count, not_75w_lines, last_valid_channel = channel_autoscan(output_file,success_count,no_100w_count,not_75w_count)
                    
                except:
                    print("\t  Channel",last_valid_channel,"doesn't exist, scan others....")
                    success_count, success_lines, no_100w_count, no_100w_lines, not_75w_count, not_75w_lines, last_valid_channel = channel_autoscan(output_file,success_count,no_100w_count,not_75w_count)

                if success_count > 0 and no_100w_count == 0 and not_75w_count == 0:
                    print("\t\tHP  LPS:",success_count,"\t", success_lines)
                
                else:
                    if success_count != 0:
                        print("\t\tHP  LPS:", success_count,"\t",success_lines)
                    #else:
                        #print("\t>",file_path)
                    if no_100w_count !=0:
                        print("\t\tNo 100W:", no_100w_count,"\t",no_100w_lines)
                    if not_75w_count !=0:
                        print("\t\tNot 75W:",not_75w_count,"\t",not_75w_lines)
                
                total_pass_count += success_count
                total_not_75w += not_75w_count
                total_not_100w += no_100w_count
                total_parse_files += 1
        except:
            print("\t>",file_path,"\r\n\t  File might be corrupted")
        
    manager.close()
    end_time = time.time()    
    
    print("\r\nTotal Pass:", total_pass_count)
    if total_not_75w+total_not_100w == 0:
        print("Total Fail:", total_not_75w+total_not_100w)
    else:
        print("Total Fail:", total_not_75w+total_not_100w, "( Not 75W x",total_not_75w,"; No 100W x",total_not_100w,")")
    print("Total", total_parse_files, "logs,", total_pass_count+total_not_75w+total_not_100w, "test cycles")

    # Calculate elapsed time in seconds
    elapsed_time = end_time - start_time
    # Convert elapsed time to minutes and seconds
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    # Output elapsed time in minutes and seconds
    print("Total Time {} min(s) {} sec(s)".format(minutes, seconds))
    print("========================================================================")

#    with open(args.input_dir+'.txt', 'w') as f:
#        sys.stdout = f
#        # all print() will re-route to file
#        sys.stdout = sys.__stdout__