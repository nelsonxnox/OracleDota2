"""
Build script for Oracle Neural Link desktop application.

Requirements:
- PyInstaller: pip install pyinstaller
- All dependencies from oracle_bridge.py

Usage:
    python build_exe.py
    
Output:
    dist/OracleNeuralLink.exe
"""

import subprocess
import sys
import os
import shutil

def build_exe():
    print("[BUILD] Starting Oracle Neural Link compilation...")
    
    # Ensure dist folder exists and is clean
    dist_path = os.path.join(os.path.dirname(__file__), "dist")
    if os.path.exists(dist_path):
        print(f"[BUILD] Cleaning {dist_path}")
        shutil.rmtree(dist_path)
    
    os.makedirs(dist_path, exist_ok=True)
    
    # PyInstaller command - Optimized for size + Binaries
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "OracleNeuralLink",
        "--icon", "NONE",
        "--add-data", "vosk-model-small-es-0.42;vosk-model-small-es-0.42",
        
        # Collect binaries (DLLs) - CRITICAL for vosk/sounddevice
        "--collect-binaries", "vosk",
        "--collect-binaries", "sounddevice",
        
        # Specific hidden imports
        "--hidden-import", "pyttsx3.drivers",
        "--hidden-import", "pyttsx3.drivers.sapi5",
        "--hidden-import", "win32com.client",
        "--hidden-import", "pythoncom",
        "--hidden-import", "sounddevice",
        "--hidden-import", "vosk",
        "--hidden-import", "websockets",
        "--hidden-import", "tkinter",
        "--hidden-import", "queue",
        "--hidden-import", "winreg",
        
        # Exclude unnecessary heavy modules
        "--exclude-module", "matplotlib",
        "--exclude-module", "numpy",
        "--exclude-module", "pandas",
        
        "--noupx",
        "oracle_bridge.py"
    ]
    
    print(f"[BUILD] Running PyInstaller...")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        print(result.stdout)
        print("\n[BUILD] Compilation successful!")
        print(f"[BUILD] Executable created at: dist/OracleNeuralLink.exe")
        print("\n[BUILD] Upload this file to your backend's 'dist/' folder for download.")
        
    except subprocess.CalledProcessError as e:
        print(f"[BUILD] Error during compilation:")
        print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("[BUILD] PyInstaller not found. Install it with:")
        print("   python -m pip install pyinstaller")
        sys.exit(1)

if __name__ == "__main__":
    # Check if Vosk model exists
    vosk_path = "vosk-model-small-es-0.42"
    if not os.path.exists(vosk_path):
        print(f"[BUILD] WARNING: Vosk model not found at '{vosk_path}'")
        print("    The executable will work, but voice recognition won't function.")
        print("    Download from: https://alphacephei.com/vosk/models")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    build_exe()
