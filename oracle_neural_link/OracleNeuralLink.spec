# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_dynamic_libs

binaries = []
binaries += collect_dynamic_libs('vosk')
binaries += collect_dynamic_libs('sounddevice')


a = Analysis(
    ['oracle_bridge.py'],
    pathex=[],
    binaries=binaries,
    datas=[('vosk-model-small-es-0.42', 'vosk-model-small-es-0.42')],
    hiddenimports=['pyttsx3.drivers', 'pyttsx3.drivers.sapi5', 'win32com.client', 'pythoncom', 'sounddevice', 'vosk', 'websockets', 'tkinter', 'queue', 'winreg'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas'],
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
    name='OracleNeuralLink',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE',
)
