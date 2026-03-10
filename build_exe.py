# build_exe.py
import PyInstaller.__main__
import os

# Nombre de la aplicación final
APP_NAME = "Omni_HUD"

print(f"--- Iniciando Compilación ULTRA-Optimizada de {APP_NAME} ---")

params = [
    'main.py',              # Punto de entrada
    f'--name={APP_NAME}',   # Nombre del .exe
    '--onedir',             # Carpeta en lugar de un solo archivo
    '--noconsole',          # Ocultar terminal
    '--clean',              # Limpiar caché
    
    # Exclusiones PESADAS (El secreto para bajar de 100MB)
    '--exclude-module', 'tzdata',           # Zonas horarias (pesadísimo)
    '--exclude-module', 'numpy',            # Por si acaso se cuela
    '--exclude-module', 'pandas',
    '--exclude-module', 'matplotlib',
    '--exclude-module', 'PIL',               # Si no usas imágenes pesadas
    '--exclude-module', 'jedi',              # Autocompletado (no se usa en EXE)
    
    # Exclusiones agresivas de PyQt6
    '--exclude-module', 'PyQt6.QtWebEngine',
    '--exclude-module', 'PyQt6.QtWebEngineCore',
    '--exclude-module', 'PyQt6.QtWebEngineWidgets',
    '--exclude-module', 'PyQt6.QtQml',
    '--exclude-module', 'PyQt6.QtQuick',
    '--exclude-module', 'PyQt6.QtSql',
    '--exclude-module', 'PyQt6.QtNetwork',   # Si no usas sockets directos (Groq usa requests/httpx)
    '--exclude-module', 'PyQt6.QtXml',
    
    # Exclusiones de Python Core
    '--exclude-module', 'tkinter',
    '--exclude-module', 'unittest',
    '--exclude-module', 'pydoc',
    '--exclude-module', 'email',
    '--exclude-module', 'html',
    '--exclude-module', 'http',
    
    # Recolección manual de lo necesario
    '--collect-all', 'SpeechRecognition',
    '--collect-all', 'groq',
    '--collect-submodules', 'PyQt6',
]

# Ejecutar compilación con optimización máxima
os.environ["PYTHONOPTIMIZE"] = "2"
PyInstaller.__main__.run(params)

print(f"\n--- Compilación ULTRA-Finalizada ---")
print(f"Tu ejecutable optimizado está en: {os.getcwd()}/dist/{APP_NAME}")
