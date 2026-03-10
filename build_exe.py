# build_exe.py
import PyInstaller.__main__
import os

APP_NAME = "Omni_HUD"

print(f"--- INICIANDO PODA QUIRÚRGICA DE BINARIOS (<60MB TARGET) ---")

params = [
    'main.py',
    f'--name={APP_NAME}',
    '--onefile',
    '--noconsole',
    '--clean',
    
    # Exclusiones de Python Core (Agresivas)
    '--exclude-module', 'tzdata',
    '--exclude-module', 'numpy',
    '--exclude-module', 'pandas',
    '--exclude-module', 'matplotlib',
    '--exclude-module', 'PIL',
    '--exclude-module', 'tkinter',
    '--exclude-module', 'unittest',
    '--exclude-module', 'pydoc',
    '--exclude-module', 'email',
    '--exclude-module', 'http',
    '--exclude-module', 'html',
    '--exclude-module', 'xml',
    '--exclude-module', 'sqlite3',
    '--exclude-module', 'logging',
    '--exclude-module', 'distutils',
    '--exclude-module', 'setuptools',
    
    # EXCLUSIÓN MANUAL DE DLLS DE QT (El gran ahorro)
    '--exclude-module', 'PyQt6.QtWebEngine',
    '--exclude-module', 'PyQt6.QtWebEngineCore',
    '--exclude-module', 'PyQt6.QtWebEngineWidgets',
    '--exclude-module', 'PyQt6.QtQml',
    '--exclude-module', 'PyQt6.QtQuick',
    '--exclude-module', 'PyQt6.QtNetwork',
    '--exclude-module', 'PyQt6.QtSql',
    '--exclude-module', 'PyQt6.QtXml',
    '--exclude-module', 'PyQt6.QtTest',
    '--exclude-module', 'PyQt6.QtDBus',
    '--exclude-module', 'PyQt6.QtDesigner',
    '--exclude-module', 'PyQt6.QtHelp',
    '--exclude-module', 'PyQt6.QtBluetooth',
    '--exclude-module', 'PyQt6.QtMultimedia',
    '--exclude-module', 'PyQt6.QtPositioning',
    '--exclude-module', 'PyQt6.QtSensors',
    '--exclude-module', 'PyQt6.QtSvg',
    '--exclude-module', 'PyQt6.QtPdf',
    '--exclude-module', 'PyQt6.QtPrintSupport',
    '--exclude-module', 'PyQt6.QtQuickWidgets',
    '--exclude-module', 'PyQt6.QtRemoteObjects',
    '--exclude-module', 'PyQt6.QtSerialPort',
    '--exclude-module', 'PyQt6.QtSpatialAudio',
]

# Optimización máxima de Python
os.environ["PYTHONOPTIMIZE"] = "2"

PyInstaller.__main__.run(params)

print(f"\n--- PODA FINALIZADA ---")
