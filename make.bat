python -m pip install virtualenv
cd src
python -m virtualenv venv
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install mysql-connector-python
venv\Scripts\python.exe -m pip install falcon
venv\Scripts\python.exe -m pip install uvicorn