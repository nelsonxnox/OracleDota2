# -*- mode: python ; coding: utf-8 -*-
# OracleNeuralLink.spec — Build optimizado SIN voz/micrófono

block_cipher = None

a = Analysis(
    ['oracle_bridge.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Imágenes para la UI
        ('assets/*', 'assets'),
    ],
    hiddenimports=[
        # pyttsx3 (TTS — solo salida de voz del coach)
        'pyttsx3',
        'pyttsx3.drivers',
        'pyttsx3.drivers.sapi5',
        # WebSockets
        'websockets',
        'websockets.legacy',
        'websockets.legacy.client',
        # Tkinter extra
        'tkinter.scrolledtext',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Librerías científicas/ML pesadas — no usadas
        'numpy', 'pandas', 'scipy', 'matplotlib',
        'sklearn', 'tensorflow', 'torch', 'cv2',
        'IPython', 'notebook', 'jupyter',
        # Audio de entrada (voz) — eliminada
        'sounddevice', 'pyaudio', 'vosk',
        # Input de teclado — eliminado
        'keyboard',
        # Test frameworks
        'pytest', 'unittest', 'doctest',
        # Otros innecesarios
        'xml', 'xmlrpc', 'pydoc',
        'tkinter.test', 'lib2to3',
        'distutils', 'setuptools',
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
    strip=True,    # Eliminar símbolos de debug
    upx=True,      # Comprimir con UPX
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Sin consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
