@echo off
setlocal
cd /d "%~dp0"

echo [1/4] Descargando motor de IA (Python)...
powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip -OutFile python_core.zip"

echo [2/4] Configurando componentes...
powershell -Command "Expand-Archive -Path python_core.zip -DestinationPath . -Force"
del python_core.zip
echo import site >> python311._pth

echo [3/4] Instalando gestor de librerias...
powershell -Command "Invoke-WebRequest -Uri https://bootstrap.pypa.io/get-pip.py -OutFile get-pip.py"
python.exe get-pip.py --no-warn-script-location
del get-pip.py

echo [4/4] Instalando librerias de IA (Esto tardara 1 minuto)...
python.exe -m pip install --no-warn-script-location pyqt6 groq supabase keyboard markdown openpyxl python-docx PyPDF2 speechrecognition pyaudiowpatch python-dotenv

:: Crear lanzador final
echo @echo off > run_omni.bat
echo start "" "%%~dp0pythonw.exe" "%%~dp0src\main.py" >> run_omni.bat

exit
