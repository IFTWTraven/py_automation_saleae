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

        > 230304\20230103_Varcolac_NoCharge_OCI1.0.4.16.0_Fail.sal
                No 100W: 1       [763]
        > 230304\20230103_Varcolac_NoCharge_OCI1.0.4.16.0_Pass.sal
                HP  LPS: 1       [795]
        > 230304\20230110_Varcolac_NoChargeIssue_PD_bootleg2.3.00.08_Fail.sal
                No 100W: 1       [763]
        > 230304\20230110_Varcolac_NoChargeIssue_PD_bootleg2.3.00.08_Pass.sal
                HP  LPS: 1       [795]
        > 230304\230303_110934_hard_reset.sal
                No result, could be wrong CC channel assignment
        > 230304\230304_074727_100Wseveral times.sal
                No result, could be wrong CC channel assignment
        > 230304\230310_082610_corrupt.sal
                File might be corrupted
        > 230304\230312_010125.sal
                No result, could be wrong CC channel assignment
        > 230304\230312_010250.sal
                No result, could be wrong CC channel assignment
        > 230304\230312_010530.sal
                No result, could be wrong CC channel assignment
        > 230304\230312_010654.sal
                No result, could be wrong CC channel assignment
        > 230304\230312_010934.sal
                No result, could be wrong CC channel assignment
        > 230304\230312_011059.sal
                No result, could be wrong CC channel assignment

Total Pass: 2
Total Fail: 2 ( Not 75W x 0 ; No 100W x 2 )
Total 12 logs, 4 test cycles
========================================================================

```

# How to generate standalone executable application (for Windows)
```
nuitka --standalone auto_saleae.py
```
