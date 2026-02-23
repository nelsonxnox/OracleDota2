# -*- mode: python ; coding: utf-8 -*-
# OracleNeuralLink.spec — Versión Completa (Pillow + Requests)

block_cipher = None

a = Analysis(
    ['oracle_bridge.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/*', 'assets'),
    ],
    hiddenimports=[
        'pyttsx3',
        'pyttsx3.drivers',
        'pyttsx3.drivers.sapi5',
        'websockets',
        'websockets.legacy',
        'websockets.legacy.client',
        'tkinter.scrolledtext',
        'PIL',
        'PIL._tkinter_finder',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'numpy', 'pandas', 'scipy', 'matplotlib',
        'sklearn', 'tensorflow', 'torch', 'cv2',
        'sounddevice', 'pyaudio', 'vosk', 'keyboard',
    ],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='OracleNeuralLink',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
