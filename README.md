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
          No 100W: 1     [2.45433s]
        > 230304\20230103_Varcolac_NoCharge_OCI1.0.4.16.0_Pass.sal
          All  OK: 1     [3.48341s]
        > 230304\20230110_Varcolac_NoChargeIssue_PD_bootleg2.3.00.08_Fail.sal
          No 100W: 1     [4.44714s]
        > 230304\20230110_Varcolac_NoChargeIssue_PD_bootleg2.3.00.08_Pass.sal
          All  OK: 1     [3.68401s]
        > 230304\230303_110934_hard_reset.sal
          HP  LPS: 5     [4.08425s, 39.1473s, 74.0997s, 109.193s, 144.395s]
          Not 75W: 1     [145.996s]
        > 230304\230304_074727_100Wseveral times.sal
          HP  LPS: 5     [3.81414s, 38.8838s, 74.0974s, 109.111s, 143.917s]
          Not 75W: 1     [110.714s]
        > 230304\230310_082610_corrupt.sal
          **File might be corrupted**
        > 230304\230312_010934.sal
          All  OK: 4     [50.5110s, 95.5775s, 140.480s, 185.404s]
        > 230304\230312_011059.sal
          All  OK: 4     [5.31648s, 95.2046s, 140.184s, 185.417s]

Total Logs: 8 files
Total Test: 24 cycles
Total Pass: 20 time
Total Fail: 4 time
        > Not 75W x 2
          145.996s      230304\230303_110934_hard_reset.sal
          110.714s      230304\230304_074727_100Wseveral times.sal
        > No 100W x 2
          2.45433s      230304\20230103_Varcolac_NoCharge_OCI1.0.4.16.0_Fail.sal
          4.44714s      230304\20230110_Varcolac_NoChargeIssue_PD_bootleg2.3.00.08_Fail.sal
Total Time: 0 min 53 sec
========================================================================
```

# How to generate standalone executable application (for Windows)
```
nuitka --standalone auto_saleae.py
```
