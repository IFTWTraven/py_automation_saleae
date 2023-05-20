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
- ***IMPORTANT*** Enable “Automation Server” in SALEAE application UI: Preference-> Automation. (SALEAE software 2.4.0+ )
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
  1. Launch Saleae Logic application if it is not running. It will jump to step 2 if Saleae Logic is already running. 
  2. Start log capturing per setup. 
  3. Assign analysers to captured log after clicking "Stop".
  4. Create a folder using current time and save log filename with Version Information data.
  5. Close Saleae Logic application if it was launched by this script.
  6. Ready for another capture cycle.

## Limitation

- App might crash if PC doesn't install Saleae Logic2 application
- App will crash if automation option is not enabled
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
