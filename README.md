# FinanceRobotAssistantApp
Finance Robot Assistant alert app, which send signals to telegram bot

## Manual
### Install Python version 3.7.9

### Install and activate virtual environment
```
python -m venv venv
```
```
venv\Scripts\activate.bat
```

### Install packages
```
pip install -r requirements.txt
```
### Install TA_lib module
```
pip install lib/TA_lib-0.4.20-xxxx-xxxx-xxxx.whl
or
https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
```
### Config API token
```
telegram-send --configure
```
### Run app
run app background
```
pythonw app.py
```
