# Gadget - SALEAE2 automation 

# How to use
- [ ] capture CC in SALEAE Logic2 with 6.25Mbps, 1.2V digital mode
- [ ] enable Automation Server in SALEAE application, perference  
- [ ] add Manchester_PD_CC analyser (binary/manchester_analyzer.dll) in SALEAE extension library
- [ ] place all SALEAE logs into a folder
- [ ] ***CLOSE all running saleae logic2 applications
- [ ] exectue python command and this application will export SALEAE logs into .csv

```
C:\> py chk_hp_lps_csv.py -f <folder> -c <CC channel>
```

## Console Output
```
========================================================================
Parsing....

        Pass: 5         Fail: 1         at 230304\230303_110934_hard_reset.sal : [763, 1828, 2851, 3901, 4924]
                        Not 75W at [4979]
        Pass: 5         Fail: 1         at 230304\230304_074727_100Wseveral times.sal : [830, 1812, 2903, 3952, 5601]
                        Not 75W at [4007]
        230304\230310_082610_corrupt.sal is currupted.

Total Pass: 10
Total Fail: 2 ( Not 75W x 2 ; No 100W x 0 )
Total 2 logs, 12 test cycles
========================================================================
```

# How to generate standalone executable application (for Windows)
```
nuitka --standalone auto_saleae.py
```
