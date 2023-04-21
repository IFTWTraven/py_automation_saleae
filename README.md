# Gadget - SALEAE automation 

# Screenshot
![in CSV](./docs/csv_cc.png)

# How to use
- [ ] capture CC in SALEAE Logic2 with 6.25Mbps, 1.2V digital mode
- [ ] enable Automation Server in SALEAE application, perference  
- [ ] add Manchester_PD_CC analyser (binary/manchester_analyzer.dll) in SALEAE extension library
- [ ] place all SALEAE logs into a folder
- [ ] ***CLOSE all running saleae logic2 applications
- [ ] exectue python command and this application will export SALEAE logs into .csv

```
C:\> py auto_saleae.exe -f <folder> -c <CC channel>
```

## Console Output
```
C:\> py auto_saleae.py -f test -c 0
INFO:saleae.automation.manager:sub ChannelConnectivity.IDLE
INFO:saleae.automation.manager:sub ChannelConnectivity.CONNECTING
INFO:saleae.automation.manager:sub ChannelConnectivity.TRANSIENT_FAILURE
INFO:saleae.automation.manager:sub ChannelConnectivity.READY

C:\>
```

# How to generate standalone executable application (for Windows)
```
nuitka --standalone auto_saleae.py
```
Command becomes
```
C:\auto_saleae.dist> auto_saleae.exe -f test -c 0
INFO:saleae.automation.manager:sub ChannelConnectivity.IDLE
INFO:saleae.automation.manager:sub ChannelConnectivity.CONNECTING
INFO:saleae.automation.manager:sub ChannelConnectivity.TRANSIENT_FAILURE
INFO:saleae.automation.manager:sub ChannelConnectivity.READY

C:\>
```