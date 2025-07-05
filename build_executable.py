#!/usr/bin/env python3
"""
DRX Trading Tracker - Build Script
Erstellt ausführbare Dateien für Windows, macOS und Linux
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

SYSTEM = platform.system()
APP_NAME = "DRX_Trading_Tracker"
VERSION = "1.2.0"

def install_build_dependencies():
    """Build-Abhängigkeiten installieren"""
    print("📦 Installiere Build-Abhängigkeiten...")
    
    dependencies = ["pyinstaller"]
    
    if SYSTEM == "Windows":
        dependencies.extend(["pywin32", "winshell"])
    elif SYSTEM == "Darwin":  # macOS
        dependencies.append("py2app")
    
    for dep in dependencies:
        print(f"   Installing {dep}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                          check=True, capture_output=True)
            print(f"   ✅ {dep} installiert")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ {dep} Installation fehlgeschlagen: {e}")
            return False
    
    print("✅ Build-Abhängigkeiten installiert")
    return True

def create_spec_file():
    """PyInstaller .spec Datei erstellen"""
    print("📝 Erstelle PyInstaller .spec Datei...")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Daten und Assets
datas = [
    ('requirements.txt', '.'),
]

# Versteckte Imports (platform-spezifisch)
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'pandas',
    'matplotlib',
    'matplotlib.backends.backend_tkagg',
    'seaborn',
    'sqlite3',
    'json',
    'datetime',
    'pathlib',
    'threading',
    'webbrowser',
    'subprocess',
    'platform',
]

# Platform-spezifische Imports
import platform
if platform.system() == "Windows":
    hiddenimports.extend([
        'MetaTrader5',
        'winshell',
        'win32com.client'
    ])

a = Analysis(
    ['drx_trading_tracker_improved.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI App - kein Console-Fenster
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if platform.system() == "Windows" else 'icon.icns',
)

# macOS App Bundle
if platform.system() == "Darwin":
    app = BUNDLE(
        exe,
        name='{APP_NAME}.app',
        icon='icon.icns',
        bundle_identifier='com.drx.trading.tracker',
        info_plist={{
            'CFBundleName': 'DRX Trading Tracker',
            'CFBundleDisplayName': 'DRX Trading Tracker',
            'CFBundleVersion': '{VERSION}',
            'CFBundleShortVersionString': '{VERSION}',
            'NSHighResolutionCapable': True,
        }}
    )
'''
    
    spec_file = f"{APP_NAME}.spec"
    with open(spec_file, 'w') as f:
        f.write(spec_content)
    
    print(f"✅ {spec_file} erstellt")
    return spec_file

def create_icon():
    """Standard-Icon erstellen (falls nicht vorhanden)"""
    print("🎨 Prüfe Icon-Dateien...")
    
    # Einfaches Text-basiertes Icon (Fallback)
    if SYSTEM == "Windows" and not Path("icon.ico").exists():
        print("ℹ️ Kein icon.ico gefunden - verwende Standard-Icon")
    elif SYSTEM == "Darwin" and not Path("icon.icns").exists():
        print("ℹ️ Kein icon.icns gefunden - verwende Standard-Icon")

def build_executable():
    """Ausführbare Datei erstellen"""
    print(f"🔨 Baue {APP_NAME} für {SYSTEM}...")
    
    # PyInstaller ausführen
    spec_file = f"{APP_NAME}.spec"
    
    try:
        cmd = [
            "pyinstaller",
            "--clean",
            "--noconfirm", 
            spec_file
        ]
        
        print(f"Ausführe: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Build erfolgreich!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build fehlgeschlagen!")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def create_installer_package():
    """Installer-Paket erstellen"""
    print("📦 Erstelle Installer-Paket...")
    
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ Dist-Ordner nicht gefunden!")
        return False
    
    package_dir = Path("package")
    package_dir.mkdir(exist_ok=True)
    
    if SYSTEM == "Windows":
        # Windows: ZIP mit .exe und Installer
        exe_file = dist_dir / f"{APP_NAME}.exe"
        if exe_file.exists():
            
            # Kopiere EXE
            shutil.copy2(exe_file, package_dir)
            
            # Erstelle Installer-Script
            installer_script = package_dir / "install.bat"
            installer_content = f'''@echo off
echo 🎯 DRX Trading Tracker - Windows Installer
echo.

mkdir "%USERPROFILE%\\Documents\\DRX Trading Tracker" 2>nul
copy "{APP_NAME}.exe" "%USERPROFILE%\\Documents\\DRX Trading Tracker\\"

echo ✅ Installation abgeschlossen!
echo.
echo Programm wurde installiert in:
echo %USERPROFILE%\\Documents\\DRX Trading Tracker\\
echo.
echo Drücke Enter zum Starten...
pause >nul

start "" "%USERPROFILE%\\Documents\\DRX Trading Tracker\\{APP_NAME}.exe"
'''
            
            with open(installer_script, 'w') as f:
                f.write(installer_content)
            
            # README
            readme_file = package_dir / "README.txt"
            readme_content = f'''DRX Trading Tracker v{VERSION} - Windows
=============================================

Installation:
1. Führe install.bat aus (als Administrator falls nötig)
2. Das Programm wird nach Documents/DRX Trading Tracker installiert
3. Du kannst die .exe auch direkt ausführen

Alternativ:
- Kopiere {APP_NAME}.exe an beliebigen Ort
- Starte per Doppelklick

System-Anforderungen:
- Windows 7/8/10/11
- Keine weiteren Abhängigkeiten nötig

Support: info@drx-trading.com
'''
            
            with open(readme_file, 'w') as f:
                f.write(readme_content)
            
            print(f"✅ Windows-Paket erstellt in: {package_dir}")
    
    elif SYSTEM == "Darwin":  # macOS
        # macOS: .app Bundle und DMG
        app_bundle = dist_dir / f"{APP_NAME}.app"
        if app_bundle.exists():
            
            # Kopiere App Bundle
            shutil.copytree(app_bundle, package_dir / f"{APP_NAME}.app")
            
            # Installer-Script für macOS
            installer_script = package_dir / "install.sh"
            installer_content = f'''#!/bin/bash
echo "🎯 DRX Trading Tracker - macOS Installer"
echo

mkdir -p "$HOME/Applications"
cp -R "{APP_NAME}.app" "$HOME/Applications/"

echo "✅ Installation abgeschlossen!"
echo
echo "App wurde installiert in: $HOME/Applications/{APP_NAME}.app"
echo
echo "Du kannst die App jetzt über Launchpad oder Finder starten."

read -p "Drücke Enter zum Öffnen der App..." 
open "$HOME/Applications/{APP_NAME}.app"
'''
            
            with open(installer_script, 'w') as f:
                f.write(installer_content)
            
            os.chmod(installer_script, 0o755)
            
            print(f"✅ macOS-Paket erstellt in: {package_dir}")
    
    else:  # Linux
        # Linux: AppImage oder .tar.gz
        exe_file = dist_dir / APP_NAME
        if exe_file.exists():
            
            shutil.copy2(exe_file, package_dir)
            
            # Installer-Script für Linux
            installer_script = package_dir / "install.sh"
            installer_content = f'''#!/bin/bash
echo "🎯 DRX Trading Tracker - Linux Installer"
echo

mkdir -p "$HOME/.local/bin"
cp "{APP_NAME}" "$HOME/.local/bin/"
chmod +x "$HOME/.local/bin/{APP_NAME}"

mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/drx-trading-tracker.desktop" << EOF
[Desktop Entry]
Name=DRX Trading Tracker
Comment=Professional Trading Journal
Exec=$HOME/.local/bin/{APP_NAME}
Icon=application-default-icon
Terminal=false
Type=Application
Categories=Office;Finance;
EOF

echo "✅ Installation abgeschlossen!"
echo
echo "App wurde installiert und ist über das Anwendungsmenü verfügbar."
echo "Oder direkt ausführen mit: ~/.local/bin/{APP_NAME}"

read -p "Drücke Enter zum Starten..." 
"$HOME/.local/bin/{APP_NAME}" &
'''
            
            with open(installer_script, 'w') as f:
                f.write(installer_content)
            
            os.chmod(installer_script, 0o755)
            
            print(f"✅ Linux-Paket erstellt in: {package_dir}")
    
    return True

def create_download_package():
    """Download-bereites Paket erstellen"""
    print("📥 Erstelle Download-Paket...")
    
    package_dir = Path("package")
    if not package_dir.exists():
        print("❌ Package-Ordner nicht gefunden!")
        return False
    
    # ZIP für Download erstellen
    import zipfile
    
    zip_name = f"DRX_Trading_Tracker_v{VERSION}_{SYSTEM}"
    zip_file = f"{zip_name}.zip"
    
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    file_size = Path(zip_file).stat().st_size / (1024 * 1024)  # MB
    
    print(f"✅ Download-Paket erstellt: {zip_file}")
    print(f"📊 Größe: {file_size:.1f} MB")
    
    return zip_file

def main():
    """Haupt-Build-Prozess"""
    print(f"🏗️ DRX Trading Tracker - Build Script")
    print(f"Platform: {SYSTEM}")
    print("=" * 50)
    
    # Prüfe ob Haupt-App existiert
    main_app = "drx_trading_tracker_improved.py"
    if not Path(main_app).exists():
        print(f"❌ Haupt-App nicht gefunden: {main_app}")
        print("Stelle sicher, dass die Python-Datei im gleichen Ordner ist!")
        return False
    
    # Build-Schritte
    steps = [
        ("📦 Build-Abhängigkeiten installieren", install_build_dependencies),
        ("🎨 Icon vorbereiten", create_icon),
        ("📝 Spec-Datei erstellen", create_spec_file),
        ("🔨 Executable bauen", build_executable),
        ("📦 Installer-Paket erstellen", create_installer_package),
        ("📥 Download-Paket erstellen", create_download_package)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        try:
            result = step_func()
            if result is False:
                print(f"❌ Schritt fehlgeschlagen: {step_name}")
                return False
        except Exception as e:
            print(f"❌ Fehler in {step_name}: {e}")
            return False
    
    print("\n🎉 BUILD ERFOLGREICH ABGESCHLOSSEN!")
    print("\nDateien erstellt:")
    print(f"  📁 dist/{APP_NAME}{'exe' if SYSTEM == 'Windows' else ''}")
    print(f"  📦 package/ (Installer)")
    print(f"  📥 DRX_Trading_Tracker_v{VERSION}_{SYSTEM}.zip (Download)")
    
    print(f"\n🚀 Bereit für Download von deiner Website!")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n❌ Build fehlgeschlagen!")
        input("Drücke Enter zum Beenden...")
        sys.exit(1)
    else:
        print("\n✅ Build erfolgreich!")
        input("Drücke Enter zum Beenden...")