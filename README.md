# Gadget - Infineon HOST PD Logger

## Screenshot

# ![logger](/docs/logger.png)

## Code members

- `main.py`: main entry
- `ui.py`: created via QT Designer and contains all UI objects
- `backend.py`: SALEAE automation flow control
- `run.py`: assign analysers in captured logs and generate issue tracker forms.
- `ui_rc.py`: resources 
- `logo.py`: splash window

## Pre-requisite

- A 16ch Saleae unit
- Install Python: https://www.python.org/ (Python 3.8+)
- Install QT Designer: https://build-system.fman.io/qt-designer-download
- Install SALEAE Logic2 (2.4.0+): https://www.saleae.com/downloads/
- Install SALEAE Python Automation package:
  ```
  pip install logic2-automation
  ```
- (Optional) Install CC analyser plugin “Manchester_PD_CC” (binary/manchester_analyzer_dist.dll) (support Saleae Pro only)
- (Optional) Install HPI I2C analyser plugin “I2CHPI” (binary/i2c_analyzer_for_HPI.dll)
- (Optional) Enable “Automation Server” in SALEAE application UI: Preference-> Automation. (SALEAE software 2.4.0+) 
  # ![automation](/docs/saleae_automation.png)

## How to use

- Connect Saleae 16 / 16 Pro to PC (will enter Demo mode if no Saleae unit is attached)
- Fill all information and platform type in Version Information
- Mapping Saleae pins with pre-defined channel number, or change to preferred ones.
- Enable "Analogue Mode" will add analogue traces on CC/SBU/VBUS pins and ends up a huge size log file. Use it only when it is necessary.
- Exectue python command
  ```
  py main.py
  ```
- This app will 
  - Scenario A: Saleae Logic2 applcation is not running (***recommended***)
    1. Launch Saleae Logic2 application with automation supportive.
    2. Hit "Start Recording" and start log capturing per setup. 
    3. Assign analysers to captured log after clicking "Pass Case" or "Fail Case".
    4. Create a folder using current time and save log filename with Issue Information data.
    5. Ready for another capture cycle.
    6. Will shutdown Saleae Logic2 application while quit python app.
  - Scenario B: Saleae Logic2 application is running
    1. Hit "Start Recording" and start log capturing per setup.
    2. Assign analysers to captured log after clicking "Pass Case" or "Fail Case".
    3. Create a folder using current time and save log filename with Issue Information data.
    4. Ready for another capture cycle.
    5. Will NOT shutdown Saleae Logic2 application while quit

## Limitation

- App might crash if PC doesn't install Saleae Logic2 application.
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