from saleae import automation
import argparse
import sys
import os
import os.path
import glob
import time
import csv

export_path = os.getcwd()
args=None

# use Manchester_PD_CC for parsing timestamp
DEFINE_ORI_ANALYSER=1

# strings defination for strings
DEFINE_75W =           ["| Fix [ 20000mV | 3750mA ]", "Fix supply [Volt =  20000mV | Curr =  3750mA"]
DEFINE_100W =          ["| Fix [ 20000mV | 5000mA ]", "Fix supply [Volt =  20000mV | Curr =  5000mA"]
DEFINE_SNK_CAP_EXT =   ["Snk_Cap_Ext	   SNK", "Sink_Capabilities_Extended"]
DEFINE_HARD_RESET =    ["HARD_RESET"]

# output timestamp length 
DEFINE_TIMESTAMP_LENGTH = 7

def parseArguments ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', required=True, help="", metavar="<input dir>",dest='input_dir')
    parser.add_argument('-c', required=True, help="", metavar="<analyser channel>",dest='channel')
    #parser.add_argument('-t', dest='define_timestamp', action='store_true', help="use -t to print results with timestamp")
    #parser.add_argument('-l', dest='define_linenumber', action='store_true', help="use -l to print results with line number")

    return parser.parse_args()
    # ...

def channel_autoscan(output_file,success_count,no_100w_count,not_75w_count):
    start_channel_no = 0
    while success_count+no_100w_count+not_75w_count == 0:
        # re-scan all channels if assigned channel is incorrect
        for chk_channel in range(start_channel_no, 16):
            try:
                if DEFINE_ORI_ANALYSER:
                    cc_analyzer = capture.add_analyzer('Manchester_PD_CC', settings={
                        'Manchester': chk_channel,
                    })
                else:
                    cc_analyzer = capture.add_analyzer('Saleae_PD_CC', settings={
                        'Manchester': chk_channel,
                        'Bit Rate (Bits/s)': 1,
                    })
                capture.export_data_table(filepath=export_filepath, analyzers=[cc_analyzer], columns=['Start','value'])
            
                #parse HP LPS flow
                success_count, success_seconds, no_100w_count,\
                no_100w_seconds, not_75w_count, not_75w_seconds = check_file(output_file)
                
                # break and return channel number which is CC one
                if success_count+no_100w_count+not_75w_count !=0:
                    new_valid_channel = chk_channel
                    break
            except:
                # channel doesn't exist, skip to next one
                start_channel_no = chk_channel+1
                break

    return success_count, success_seconds, no_100w_count, no_100w_seconds, not_75w_count, not_75w_seconds, new_valid_channel

def check_file(filepath):
    success_count = 0
    not_75w_count = 0
    no_100w_count = 0
    success_seconds = []
    not_75w_seconds = []
    no_100w_seconds = []
    snk_cap_ext_seconds = []

    with open(filepath, 'r') as file:
        lines = file.readlines()
        i = 0

        while i < len(lines):
            start_as_75w = False
            rise_to_100w = False
            sent_snk_cap_ext = False
            another_round = False
            
            if any(s in lines[i] for s in DEFINE_75W):
                start_as_75w = True

                for j in range(i+1, len(lines)):
                    if any(s in lines[j] for s in DEFINE_75W):
                        i = j - 5
                        break
                    if any(s in lines[j] for s in DEFINE_HARD_RESET):
                        i = j - 1
                        break
                    else:
                        if any(s in lines[j] for s in DEFINE_100W):
                            rise_to_100w = True
                            # finish check in this range. add 1 to avoid repeatedly check
                            i = j + 1
                            break
                        if any(s in lines[j] for s in DEFINE_SNK_CAP_EXT):
                            sent_snk_cap_ext = True
                        if any(s in lines[j] for s in DEFINE_75W):
                            another_round = True
                            i = j
                            break
                            
            elif any(s in lines[i] for s in DEFINE_100W):
                start_as_75w = False
                for j in range(i+1, len(lines)):
                    if any(s in lines[j] for s in DEFINE_75W):
                        another_round = True
                        i = j
                        break
                    if any(s in lines[j] for s in DEFINE_100W):
                        another_round = True
                        i = j
                        break
                    if any(s in lines[j] for s in DEFINE_HARD_RESET):
                        another_round = True
                        i = j
                        break
            
            # start with 75W, complete LPS check flow and rise to 100W
            if start_as_75w and sent_snk_cap_ext and rise_to_100w:
                success_count +=1
                # found target and record time value at previous csv column 
                success_seconds.append(lines[i-1].split(',')[1].strip())
            elif start_as_75w and sent_snk_cap_ext and rise_to_100w and not file.readlines():
                success_count +=1
                success_seconds.append(lines[i-1].split(',')[1].strip())
            elif start_as_75w and sent_snk_cap_ext and not rise_to_100w and another_round:
                no_100w_count +=1
                no_100w_seconds.append(lines[i-1].split(',')[1].strip())
            elif start_as_75w and sent_snk_cap_ext and not rise_to_100w and not file.readlines():
                no_100w_count +=1
                no_100w_seconds.append(lines[i-1].split(',')[1].strip())
                
            elif not start_as_75w and another_round:
                not_75w_count +=1
                not_75w_seconds.append(lines[i-1].split(',')[1].strip())
                
            i += 1

    return success_count, success_seconds, no_100w_count, no_100w_seconds, not_75w_count, not_75w_seconds

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
        output_file = salfile_path+'.csv'
        export_filepath = os.path.join(export_path, output_file)
        
        try:
            with manager.load_capture(salfile_path) as capture:
                print("\t>",file_path)
                # Add an analyzer to the capture
                try:
                    if DEFINE_ORI_ANALYSER:
                        cc_analyzer = capture.add_analyzer('Manchester_PD_CC', settings={
                            'Manchester': last_valid_channel,
                        })
                    else:
                        cc_analyzer = capture.add_analyzer('Saleae_PD_CC', settings={
                            'Manchester': last_valid_channel,
                            'Bit Rate (Bits/s)': 1,
                        })
                    # export to csv
                    capture.export_data_table(filepath=export_filepath, analyzers=[cc_analyzer], columns=['Start','value'])
                
                    # parse HP LPS flow
                    success_count, success_seconds, no_100w_count,\
                    no_100w_seconds, not_75w_count, not_75w_seconds = check_file(output_file)
                    
                    # no result, maybe assign wrong CC channel
                    if success_count+no_100w_count+not_75w_count == 0:
                        #print("\t  Channel",last_valid_channel,"is not CC, scan others....", end='')
                        # search correct CC channel
                        success_count, success_seconds, no_100w_count,\
                        no_100w_seconds, not_75w_count, not_75w_seconds,\
                        last_valid_channel = channel_autoscan(output_file,success_count,no_100w_count,not_75w_count)
                        #print("found at channel", last_valid_channel)
                except:
                    # assigned channel doesn't exist in log file.
                    #print("\t  Channel",last_valid_channel,"doesn't exist, scan others....", end='')
                    # search other channels
                    success_count, success_seconds, no_100w_count,\
                    no_100w_seconds, not_75w_count, not_75w_seconds,\
                    last_valid_channel = channel_autoscan(output_file,success_count,no_100w_count,not_75w_count)
                    #print("found at channel", last_valid_channel)
                
                # all pass in log
                if success_count > 0 and no_100w_count == 0 and not_75w_count == 0:
                    # re-format success_seconds array into fixed string length, add ',' and print
                    print("\t  HP  LPS:",success_count,"\t ["+", ".join([s[:DEFINE_TIMESTAMP_LENGTH]+'s' for s in success_seconds])+"]")
                else:
                    if success_count != 0:
                        print("\t  HP  LPS:", success_count,"\t ["+", ".join([s[:DEFINE_TIMESTAMP_LENGTH]+'s' for s in success_seconds])+"]")
                    if no_100w_count !=0:
                        print("\t  No 100W:", no_100w_count,"\t ["+", ".join([s[:DEFINE_TIMESTAMP_LENGTH]+'s' for s in no_100w_seconds])+"]")
                    if not_75w_count !=0:
                        print("\t  Not 75W:", not_75w_count,"\t ["+", ".join([s[:DEFINE_TIMESTAMP_LENGTH]+'s' for s in not_75w_seconds])+"]")
                        
                total_pass_count += success_count
                total_not_75w += not_75w_count
                total_not_100w += no_100w_count
                total_parse_files += 1
                # delete exported csv file after parsing files
                os.remove(output_file)
        except:
            # fail in assigning analyser in log file. 
            print("\t>",file_path,"\r\n\t\tFile might be corrupted")
        
    manager.close()
    end_time = time.time()    
    
    #print summary
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
