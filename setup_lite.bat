@echo off
setlocal
cd /d "%~dp0"

echo [1/2] Instalando librerias de IA...
python -m pip install --no-warn-script-location pyqt6 groq supabase keyboard markdown openpyxl python-docx PyPDF2 speechrecognition pyaudiowpatch python-dotenv duckduckgo-search easyocr Pillow

:: Crear lanzador final
echo @echo off > run_omni.bat
echo start "" "pythonw" "%%~dp0src\main.py" >> run_omni.bat

exit
