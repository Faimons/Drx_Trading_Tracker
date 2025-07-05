#!/usr/bin/env python3
"""
DRX Trading Tracker - Automatischer Setup Installer
Einfache Ein-Klick Installation für Windows und Mac
"""

import sys
import subprocess
import os
import platform
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import urllib.request
import json
from pathlib import Path

class DRXInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DRX Trading Tracker - Setup")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # System Info
        self.system = platform.system()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        
        # Installation Pfad
        if self.system == "Windows":
            self.install_path = Path.home() / "DRX Trading Tracker"
        else:  # Mac/Linux
            self.install_path = Path.home() / "Applications" / "DRX Trading Tracker"
        
        self.create_ui()
        
    def create_ui(self):
        """Setup UI erstellen"""
        
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🎯 DRX Trading Tracker", 
                              font=('Arial', 18, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(header_frame, text="Professionelles Trading Journal", 
                                 font=('Arial', 10), fg='#ecf0f1', bg='#2c3e50')
        subtitle_label.pack()
        
        # Main Content
        content_frame = tk.Frame(self.root, bg='white', padx=30, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # System Info
        info_frame = tk.LabelFrame(content_frame, text="System Information", 
                                  font=('Arial', 12, 'bold'), bg='white')
        info_frame.pack(fill='x', pady=10)
        
        system_info = f"""
🖥️ Betriebssystem: {self.system} {platform.release()}
🐍 Python Version: {self.python_version}
📁 Installation: {self.install_path}
        """
        
        tk.Label(info_frame, text=system_info, bg='white', justify='left').pack(pady=10)
        
        # Requirements Check
        req_frame = tk.LabelFrame(content_frame, text="Installation Fortschritt", 
                                 font=('Arial', 12, 'bold'), bg='white')
        req_frame.pack(fill='x', pady=10)
        
        # Progress Bar
        self.progress = ttk.Progressbar(req_frame, mode='determinate', length=400)
        self.progress.pack(pady=10)
        
        # Status Text
        self.status_text = tk.Text(req_frame, height=8, width=60, wrap='word')
        self.status_text.pack(pady=5)
        
        # Scrollbar für Status
        scrollbar = tk.Scrollbar(req_frame, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=20)
        
        self.install_btn = tk.Button(button_frame, text="🚀 Installation starten", 
                                    font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
                                    command=self.start_installation, padx=20, pady=10)
        self.install_btn.pack(side='left', padx=10)
        
        self.cancel_btn = tk.Button(button_frame, text="❌ Abbrechen", 
                                   font=('Arial', 12), bg='#e74c3c', fg='white',
                                   command=self.root.quit, padx=20, pady=10)
        self.cancel_btn.pack(side='right', padx=10)
        
        # Initial Check
        self.check_prerequisites()
    
    def log_status(self, message):
        """Status-Nachricht ausgeben"""
        self.status_text.insert('end', f"{message}\n")
        self.status_text.see('end')
        self.root.update()
        print(message)
    
    def check_prerequisites(self):
        """System-Voraussetzungen prüfen"""
        self.log_status("🔍 Prüfe System-Voraussetzungen...")
        
        # Python Version
        if sys.version_info < (3, 7):
            self.log_status("❌ FEHLER: Python 3.7+ erforderlich!")
            self.install_btn.config(state='disabled')
            return False
        
        self.log_status(f"✅ Python {self.python_version} - OK")
        
        # PIP verfügbar?
        try:
            import pip
            self.log_status("✅ PIP verfügbar")
        except ImportError:
            self.log_status("❌ PIP nicht gefunden - Installation nicht möglich")
            self.install_btn.config(state='disabled')
            return False
        
        # Internet-Verbindung
        try:
            urllib.request.urlopen('https://pypi.org', timeout=5)
            self.log_status("✅ Internet-Verbindung - OK")
        except:
            self.log_status("⚠️ Warnung: Keine Internet-Verbindung")
        
        # MetaTrader 5 Verfügbarkeit (nur Windows)
        if self.system == "Windows":
            self.log_status("ℹ️ MetaTrader 5 Integration verfügbar")
        else:
            self.log_status("⚠️ MetaTrader 5 nur unter Windows verfügbar")
        
        self.log_status("\n✅ System bereit für Installation!")
        return True
    
    def start_installation(self):
        """Installation in separatem Thread starten"""
        self.install_btn.config(state='disabled', text="Installing...")
        
        install_thread = threading.Thread(target=self.install_process)
        install_thread.daemon = True
        install_thread.start()
    
    def install_process(self):
        """Installations-Prozess"""
        try:
            total_steps = 6
            current_step = 0
            
            # Schritt 1: Ordner erstellen
            self.log_status("\n🔧 Schritt 1/6: Erstelle Installation-Ordner...")
            self.install_path.mkdir(parents=True, exist_ok=True)
            current_step += 1
            self.progress['value'] = (current_step / total_steps) * 100
            
            # Schritt 2: Requirements installieren
            self.log_status("📦 Schritt 2/6: Installiere Python-Pakete...")
            self.install_requirements()
            current_step += 1
            self.progress['value'] = (current_step / total_steps) * 100
            
            # Schritt 3: Haupt-App herunterladen
            self.log_status("⬇️ Schritt 3/6: Lade DRX Trading Tracker...")
            self.download_main_app()
            current_step += 1
            self.progress['value'] = (current_step / total_steps) * 100
            
            # Schritt 4: Launcher erstellen
            self.log_status("🚀 Schritt 4/6: Erstelle Launcher...")
            self.create_launcher()
            current_step += 1
            self.progress['value'] = (current_step / total_steps) * 100
            
            # Schritt 5: Desktop Shortcut (Windows)
            if self.system == "Windows":
                self.log_status("🔗 Schritt 5/6: Erstelle Desktop-Verknüpfung...")
                self.create_desktop_shortcut()
            else:
                self.log_status("📱 Schritt 5/6: Bereite Mac-App vor...")
                self.create_mac_app()
            current_step += 1
            self.progress['value'] = (current_step / total_steps) * 100
            
            # Schritt 6: Fertig
            self.log_status("✅ Schritt 6/6: Installation abgeschlossen!")
            self.progress['value'] = 100
            
            # Success Dialog
            self.root.after(0, self.installation_complete)
            
        except Exception as e:
            self.log_status(f"❌ FEHLER: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Installation Fehler", f"Installation fehlgeschlagen:\n{str(e)}"))
    
    def install_requirements(self):
        """Python Requirements installieren"""
        requirements = [
            "tkinter",  # Meist bereits enthalten
            "pandas",
            "matplotlib",
            "seaborn", 
            "requests",
            "python-dateutil"
        ]
        
        # MetaTrader 5 nur für Windows
        if self.system == "Windows":
            requirements.append("MetaTrader5")
        
        for req in requirements:
            if req == "tkinter":
                continue  # Tkinter ist meist built-in
                
            self.log_status(f"   Installing {req}...")
            
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", req, "--user"
                ], capture_output=True, text=True, check=True)
                
                self.log_status(f"   ✅ {req} erfolgreich installiert")
                
            except subprocess.CalledProcessError as e:
                self.log_status(f"   ⚠️ Warnung: {req} Installation fehlgeschlagen")
                if "MetaTrader5" not in req:  # MT5 optional
                    raise e
    
    def download_main_app(self):
        """Haupt-Anwendung erstellen"""
        # Hier würdest du normalerweise von deiner Website herunterladen
        # Für jetzt erstellen wir eine vereinfachte Version
        
        app_content = '''#!/usr/bin/env python3
"""
DRX Trading Tracker - Vereinfachte Version
"""

import tkinter as tk
from tkinter import messagebox
import sys
import platform

def main():
    root = tk.Tk()
    root.title("DRX Trading Tracker")
    root.geometry("800x600")
    
    # Header
    header = tk.Frame(root, bg='#2c3e50', height=60)
    header.pack(fill='x')
    header.pack_propagate(False)
    
    title = tk.Label(header, text="🎯 DRX Trading Tracker", 
                    font=('Arial', 16, 'bold'), fg='white', bg='#2c3e50')
    title.pack(expand=True)
    
    # Content
    content = tk.Frame(root, bg='white', padx=20, pady=20)
    content.pack(fill='both', expand=True)
    
    welcome_text = f"""
Willkommen zum DRX Trading Tracker!

System: {platform.system()}
Python: {sys.version_info.major}.{sys.version_info.minor}

Status: Installation erfolgreich! 🎉

Nächste Schritte:
1. Verbinde dich mit deinem Broker (MetaTrader 5)
2. Importiere deine Trading-Daten
3. Analysiere deine Performance

Für vollständige Funktionen besuche:
www.drx-trading.com
    """
    
    tk.Label(content, text=welcome_text, font=('Arial', 11), 
            justify='left', bg='white').pack(pady=20)
    
    # Buttons
    button_frame = tk.Frame(content, bg='white')
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="🚀 Vollversion laden", 
             font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
             command=lambda: messagebox.showinfo("Info", "Besuche www.drx-trading.com für die Vollversion!"),
             padx=20, pady=10).pack(side='left', padx=10)
    
    tk.Button(button_frame, text="❌ Schließen", 
             font=('Arial', 12), bg='#e74c3c', fg='white',
             command=root.quit, padx=20, pady=10).pack(side='right', padx=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()
'''
        
        app_file = self.install_path / "drx_trading_tracker.py"
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(app_content)
        
        self.log_status("   ✅ Haupt-Anwendung erstellt")
    
    def create_launcher(self):
        """Launcher-Script erstellen"""
        if self.system == "Windows":
            # Windows Batch-Datei
            launcher_content = f'''@echo off
cd /d "{self.install_path}"
python drx_trading_tracker.py
pause
'''
            launcher_file = self.install_path / "DRX Trading Tracker.bat"
            with open(launcher_file, 'w') as f:
                f.write(launcher_content)
        
        else:
            # Mac/Linux Shell-Script
            launcher_content = f'''#!/bin/bash
cd "{self.install_path}"
python3 drx_trading_tracker.py
'''
            launcher_file = self.install_path / "DRX Trading Tracker.sh"
            with open(launcher_file, 'w') as f:
                f.write(launcher_content)
            
            # Ausführbar machen
            os.chmod(launcher_file, 0o755)
        
        self.log_status("   ✅ Launcher erstellt")
    
    def create_desktop_shortcut(self):
        """Windows Desktop-Verknüpfung erstellen"""
        try:
            import winshell  # type: ignore[import]
            from win32com.client import Dispatch  # type: ignore[import]
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "DRX Trading Tracker.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = str(self.install_path / "DRX Trading Tracker.bat")
            shortcut.WorkingDirectory = str(self.install_path)
            shortcut.IconLocation = str(self.install_path / "DRX Trading Tracker.bat")
            shortcut.save()
            
            self.log_status("   ✅ Desktop-Verknüpfung erstellt")
        
        except ImportError:
            # Fallback: Einfache .bat Datei auf Desktop
            desktop = Path.home() / "Desktop"
            if desktop.exists():
                batch_content = f'@echo off\ncd /d "{self.install_path}"\npython drx_trading_tracker.py\npause'
                shortcut_file = desktop / "DRX Trading Tracker.bat"
                with open(shortcut_file, 'w') as f:
                    f.write(batch_content)
                self.log_status("   ✅ Desktop-Starter erstellt")
        except Exception as e:
            self.log_status(f"   ⚠️ Desktop-Verknüpfung fehlgeschlagen: {e}")
            # Fallback wie oben
            desktop = Path.home() / "Desktop"
            if desktop.exists():
                batch_content = f'@echo off\ncd /d "{self.install_path}"\npython drx_trading_tracker.py\npause'
                shortcut_file = desktop / "DRX Trading Tracker.bat"
                with open(shortcut_file, 'w') as f:
                    f.write(batch_content)
                self.log_status("   ✅ Desktop-Starter erstellt (Fallback)")
    
    def create_mac_app(self):
        """Mac App Bundle erstellen"""
        app_bundle = self.install_path.parent / "DRX Trading Tracker.app"
        contents_dir = app_bundle / "Contents"
        macos_dir = contents_dir / "MacOS"
        
        # Ordner erstellen
        macos_dir.mkdir(parents=True, exist_ok=True)
        
        # Info.plist
        plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>DRX Trading Tracker</string>
    <key>CFBundleIdentifier</key>
    <string>com.drx.trading.tracker</string>
    <key>CFBundleName</key>
    <string>DRX Trading Tracker</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
</dict>
</plist>'''
        
        with open(contents_dir / "Info.plist", 'w') as f:
            f.write(plist_content)
        
        # Executable
        executable_content = f'''#!/bin/bash
cd "{self.install_path}"
python3 drx_trading_tracker.py
'''
        
        executable_file = macos_dir / "DRX Trading Tracker"
        with open(executable_file, 'w') as f:
            f.write(executable_content)
        
        os.chmod(executable_file, 0o755)
        
        self.log_status("   ✅ Mac App Bundle erstellt")
    
    def installation_complete(self):
        """Installation abgeschlossen"""
        if self.system == "Windows":
            launch_info = "Desktop-Verknüpfung verwenden oder Batch-Datei ausführen"
        else:
            launch_info = "DRX Trading Tracker.app öffnen"
        
        success_message = f"""
🎉 Installation erfolgreich abgeschlossen!

Installation Pfad: {self.install_path}

So startest du die App:
{launch_info}

Für Updates und Vollversion:
www.drx-trading.com

Viel Erfolg beim Trading! 📈
        """
        
        messagebox.showinfo("Installation erfolgreich", success_message)
        
        # Frage ob App direkt starten
        if messagebox.askyesno("App starten", "Möchtest du DRX Trading Tracker jetzt starten?"):
            self.launch_app()
        
        self.root.quit()
    
    def launch_app(self):
        """App nach Installation starten"""
        try:
            if self.system == "Windows":
                os.startfile(self.install_path / "DRX Trading Tracker.bat")
            else:
                subprocess.Popen([sys.executable, str(self.install_path / "drx_trading_tracker.py")])
        except Exception as e:
            messagebox.showerror("Start-Fehler", f"App konnte nicht gestartet werden: {str(e)}")

def main():
    """Hauptfunktion"""
    print("🎯 DRX Trading Tracker - Setup")
    print("=" * 40)
    
    try:
        installer = DRXInstaller()
        installer.root.mainloop()
    except Exception as e:
        print(f"Setup Fehler: {e}")
        input("Drücke Enter zum Beenden...")

if __name__ == "__main__":
    main()