# Build Script for Oracle Neural Link
# Generates the executable file
# -*- coding: utf-8 -*-

import os
import subprocess
import shutil
import sys

# Force UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("ORACLE NEURAL LINK - BUILD SCRIPT")
print("="*60)

# 1. Clean previous builds
print("\n[1/4] Cleaning previous builds...")
if os.path.exists("build"):
    shutil.rmtree("build")
    print("  [OK] Removed build/ directory")

if os.path.exists("dist"):
    shutil.rmtree("dist")
    print("  [OK] Removed dist/ directory")

if os.path.exists("OracleNeuralLink.spec"):
    os.remove("OracleNeuralLink.spec")
    print("  [OK] Removed OracleNeuralLink.spec")

# 2. Build executable
print("\n[2/4] Building executable with PyInstaller...")
cmd = [
    "python", "-m", "PyInstaller",
    "--clean",
    "OracleNeuralLink.spec"
]

result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode != 0:
    print("  [ERROR] Build failed!")
    print(result.stderr)
    exit(1)
else:
    print("  [OK] Build successful!")

# 3. Copy to backend/dist for download
print("\n[3/4] Copying to backend/dist...")
backend_dist = os.path.join("..", "backend", "dist")
os.makedirs(backend_dist, exist_ok=True)

exe_source = os.path.join("dist", "OracleNeuralLink.exe")
exe_dest = os.path.join(backend_dist, "OracleNeuralLink.exe")

if os.path.exists(exe_source):
    shutil.copy2(exe_source, exe_dest)
    print(f"  [OK] Copied to {exe_dest}")
else:
    print(f"  [ERROR] Executable not found at {exe_source}")
    exit(1)

# 4. Display file size
file_size = os.path.getsize(exe_dest) / (1024 * 1024)  # MB
print(f"\n[4/4] Build complete!")
print(f"  File: {exe_dest}")
print(f"  Size: {file_size:.2f} MB")

print("\n" + "="*60)
print("SUCCESS: ORACLE NEURAL LINK BUILD COMPLETE")
print("="*60)
print("\nNext steps:")
print("1. Test the executable: backend/dist/OracleNeuralLink.exe")
print("2. Update CURRENT_VERSION in oracle_bridge.py if needed")
print("3. Update version in backend/main.py /api/version endpoint")
print("4. Commit and push to GitHub for deployment")
