# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tzdata', 'numpy', 'pandas', 'matplotlib', 'PIL', 'tkinter', 'unittest', 'pydoc', 'email', 'http', 'html', 'xml', 'sqlite3', 'logging', 'distutils', 'setuptools', 'PyQt6.QtWebEngine', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebEngineWidgets', 'PyQt6.QtQml', 'PyQt6.QtQuick', 'PyQt6.QtNetwork', 'PyQt6.QtSql', 'PyQt6.QtXml', 'PyQt6.QtTest', 'PyQt6.QtDBus', 'PyQt6.QtDesigner', 'PyQt6.QtHelp', 'PyQt6.QtBluetooth', 'PyQt6.QtMultimedia', 'PyQt6.QtPositioning', 'PyQt6.QtSensors', 'PyQt6.QtSvg', 'PyQt6.QtPdf', 'PyQt6.QtPrintSupport', 'PyQt6.QtQuickWidgets', 'PyQt6.QtRemoteObjects', 'PyQt6.QtSerialPort', 'PyQt6.QtSpatialAudio'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Omni_HUD',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
