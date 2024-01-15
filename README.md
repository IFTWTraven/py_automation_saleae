# Gadget - Infineon HOST PD Logger

## Youtube 

[![WCS Logger - The assistant in Infineon WCS USBC host applications](/docs/host_logger_yt.png)](https://www.youtube.com/watch?v=Zy7FzoSF6Ks)

## Screenshot

# ![logger](/docs/logger.png)

## Code members

- `main.py`: main entry
- `backend.py`: SALEAE automation flow control
- `run.py`: assign analysers in captured logs and generate issue tracker forms.
- `dev_cysniffer.py`: CY4500 control
- `dev_saleae.py`: Saleae automation control
- `dev_ellisys.py`: Ellisys C-Tracker control
- `ui.py`: created via QT Designer and contains all UI objects
- `logo.py`: splash window
- `ui_rc.py`: resources 

## Pre-requisite

- A CY4500 sniffer
- A 16ch Saleae unit
- A Ellisys C-Tracker (optional)
- Install Python: https://www.python.org/ (Python 3.8+)
- Install QT Designer: https://build-system.fman.io/qt-designer-download
- Install CY4500 EZ-PD Protocol Analyzer Utility: https://www.infineon.com
- Install SALEAE Logic2 (2.4.0+): https://www.saleae.com/downloads/
- Install SALEAE Python Automation package:
- Install Ellisys Type-C Tracker Analyzer: https://www.ellisys.com
  ```
  pip install logic2-automation
  ```
- (Optional) Install CC analyser plugin “Manchester_PD_CC” (binary/manchester_analyzer_dist.dll) (support Saleae Pro only)
- (Optional) Install HPI I2C analyser plugin “I2CHPI” (binary/i2c_analyzer_for_HPI.dll)
- (Optional) Enable “Automation Server” in SALEAE application UI: Preference-> Automation. (SALEAE software 2.4.0+) 
  # ![automation](/docs/saleae_automation.png)
- Copy "RemoteControl" folder to Ellisys installation directory and control via Menu->Tools->Options->Remote Control:
  # ![automation](/docs/ellisys_remotecontrol.png)

## How to use

- Connect CY4500 sniffer and Saleae 16 Pro and Ellisys C-Tracker (optional) to PC
- Fill all information and platform type in Issue Information
- Mapping pins with pre-defined channel number, or change to preferred ones.
- Enable "Analogue Mode" will add analogue traces on CC/SBU/VBUS pins and ends up a huge size log file. Use it only when it is necessary.
- Exectue python command
  ```
  py main.py
  ```
- This app will 
  - Check and confirm log applications (EZ-PD Protocol Analyzer Utility, Saleae Logic2, Ellisys Type-C Tracker Analyzer) installation status
  - Generate logs based on device selection (Saleae + CY4500 or Ellisys C-Tracker)
  - Scenario A: Log applcations are not running (***recommended***)
    1. Launch log applications with automation supportive.
    2. Hit "Start Recording" and start log capturing per setup.
    3. Assign analysers to captured logs (Saleae Mode) after clicking "Pass Case" or "Fail Case".
    4. Create a folder using current time and save log filename with Issue Information data.
    5. Ready for another capture cycle.
    6. Will shutdown log applications while quit python app.
  - Scenario B: Log applications are running
    1. Hit "Start Recording" and start log capturing per setup.
    2. Assign analysers to captured logs (Saleae Mode) after clicking "Pass Case" or "Fail Case".
    3. Create a folder using current time and save log filename with Issue Information data.
    4. Ready for another capture cycle.
    5. Will NOT shutdown log applications while quit

## Limitation

- App might halt if close SALEAE Logic2 application during log collecting.
- App will crash if Saleae Logic applcation doesn't enable "Automation Server" at Scenario B.
- Doesn't support Saleae 8ch.

---
# Build UI

## QT Designer

- add/modify QT objects in QT Designer and save to .ui file
  # ![QT Designer](/docs/qt_designer.png)
- translate to python script:
  ```
  pyrcc5 ui.qrc -o ui_rc.py
  pyuic5 ui.ui -o ui.py
  pyuic5 logo.ui -o logo.py
  ```

---
# Build Standalone Application

```
pyinstaller -F --noconsole main.py -i docs/IFX_Logo.ico --name wcs_logger.exe
```