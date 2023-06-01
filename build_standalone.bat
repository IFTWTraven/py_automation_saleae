rem pyinstaller -F --noconsole main.py --splash docs/background.png -i docs/IFX_Logo.ico --name main_auto_logger.exe
pyinstaller -F --noconsole main.py -i docs/IFX_Logo.ico --name main_auto_logger.exe
copy dist\main_auto_logger.exe binary\.
PAUSE