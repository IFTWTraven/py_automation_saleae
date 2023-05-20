# Gadget - Infineon HOST PD Logger

## Screenshot

# ![logger](/docs/logger.png)

## Code members

- main.py: main entry
- ui.py: created via QT Designer and contains all UI objects
- backend.py: automation flow control
- run.py: Saleae Logic2 application

## Pre-requisite

- A 16ch Saleae unit
- Install Python: https://www.python.org/ (Python 3.8+)
- Install QT Designer: https://build-system.fman.io/qt-designer-download
- Install SALEAE Logic2 (2.4.0+): https://www.saleae.com/downloads/
- Install SALEAE Python Automation package:
  ```
  pip install logic2-automation
  ```
- (Optional) Install CC analyser plugin “Manchester_PD_CC” (binary/manchester_analyzer.dll) (support Saleae Pro only)
- (Optional) Install HPI I2C analyser plugin “HPI_I2CBurst” (binary/saleae_pd_analyser.dll)
- (Optional) Enable “Automation Server” in SALEAE application UI: Preference-> Automation. (SALEAE software 2.4.0+) 
  # ![automation](/docs/saleae_automation.png)

## How to use

- Connect Saleae 16 / 16 Pro to PC (will enter Demo mode if no Saleae unit is attached)
- Fill all information and platform type in Version Information
- Mapping Saleae pins with pre-defined channel number, or change to preferred ones.
- Exectue python command
  ```
  py main.py
  ```
- Click "Run" button
- This app will 
  - Scenario A: Saleae Logic applcation is not running
    1. Launch Saleae Logic application with automation supportive.
    2. Hit "Run" and start log capturing per setup. 
    3. Assign analysers to captured log after clicking "Stop".
    4. Create a folder using current time and save log filename with Version Information data.
    5. Ready for another capture cycle.
    6. Will shutdown Saleae Logic application while quit python app.
  - Scenario B: Saleae Logic application is running
    1. Hit "Run" and start log capturing per setup.
    2. Assign analysers to captured log after clicking "Stop".
    3. Create a folder using current time and save log filename with Version Information data.
    4. Ready for another capture cycle.
    5. Will ***NOT*** shutdown Saleae Logic application while quit

## Limitation

- App might crash if PC doesn't install Saleae Logic2 application
- App will crash if Saleae Logic applcation doesn't enable "Automation Server" at Scenario B.
- Doesn't support Saleae 8ch

---
# Build UI

## QT Designer

- add/modify QT objects in QT Designer and save to .ui file
  # ![QT Designer](/docs/qt_designer.png)
- translate to python script:
  ```
  pyuic5 ui.ui -o ui.py
  ```

---
# Build Standalone Application

```
pyinstaller -F --noconsole main.py
```
or
```
nuitka --standalone --enable-plugin=pyqt5 --disable-console --onefile main.py
```
