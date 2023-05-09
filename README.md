# Gadget - SALEAE2 automation using PyQT5

## Screenshot

# ![arduino](/docs/pyduino.png)

## Code members

- main.py: main entry
- ui.py: created via QT Designer and contains all UI objects
- ui_rc.py: resource files
- backend.py: automation flow control
- run.py: controls to Arduino and Saleae Logic2 application

## Pre-requisite

- a Arduino board
  # ![arduino_mega](/docs/arduino_mega.png)
- a 5V 4 channels relay board
  # ![5V_4ch_relay](/docs/5V_4ch_Relay.png)
- a Infineon CC adapter
  # ![CC Adapter](/docs/cc_adapter.png)
- Install Python: https://www.python.org/ (Python 3.8+)
- Install QT Designer: https://build-system.fman.io/qt-designer-download
- Install SALEAE Logic2 (2.4.0+): https://www.saleae.com/downloads/
- Install SALEAE Python Automation package:
  ```
  pip install logic2-automation
  ```
- Install CC analyser plugin “Manchester_PD_CC” (binary/manchester_analyzer.dll) (support Saleae Pro only)
- Install HPI I2C analyser plugin “HPI_I2CBurst” (binary/saleae_pd_analyser.dll)
- Enable “Automation Server” in SALEAE application UI: Preference-> Automation. (SALEAE software 2.4.0+ )
  # ![automation](/docs/saleae_automation.png)

## How to use

- follow https://realpython.com/arduino-python/, “Hello, World!” With Arduino and Python section to setup arduino board
  # ![arduino](/docs/arduino.png)
- connect arduino board to PC
- connect Saleae Pro 8/16 to PC (will enter Demo mode if no Saleae unit is attached)
- assign I2C, UART or CC channels via Channel Setup section
- assign test conditions in Sequence Setup section
- ***IMPORTANT***: CLOSE all running saleae logic2 applications
- exectue python command
  ```
  py main.py
  ```
- This app will record Saleae logs and save to a sub-folder using current system time/date as its name

## Limitation

- Relay control IOs are fixed at Arduino MEGA pin 48, 50 and 52
- App might crash if multiple Arduino boards are attached
- App might crash if PC doesn't install Saleae Logic2 application

---
# Build UI

## QT Designer

- add/modify QT objects in QT Designer and save to .ui file
  # ![QT Designer](/docs/qt_designer.png)
- translate to python script:
  ```
  pyuic5 ui.ui -o ui.py
  pyrcc5 ui.qrc -o ui_rc.py
  ```


---
# Build Standalone Application

```
nuitka --standalone --enable-plugin=pyqt5 --disable-console --onefile main.py
```
