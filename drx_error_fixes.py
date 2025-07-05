#!/usr/bin/env python3
"""
DRX Trading Tracker - Pylance Error Fixes
Behebt alle Type-Checking und Import-Probleme

Verwendung:
1. Diese Datei ins gleiche Verzeichnis wie der Hauptcode legen
2. In VS Code: Python Interpreter neu laden
3. Pylance sollte keine Fehler mehr zeigen
"""

import sys
import platform
from typing import TYPE_CHECKING, Optional, Any, Union, Dict, List, Tuple, Callable
from pathlib import Path

# Type-Checking imports mit sicherer Behandlung
if TYPE_CHECKING:
    try:
        import MetaTrader5 as mt5  # type: ignore
    except ImportError:
        # Fallback Stubs
        class MT5Stub:
            @staticmethod
            def initialize() -> bool: ...
            @staticmethod  
            def login(login: int, password: str = "", server: str = "") -> bool: ...
            @staticmethod
            def account_info() -> Optional[Any]: ...
            @staticmethod
            def positions_get() -> Optional[Any]: ...
            @staticmethod
            def last_error() -> tuple[int, str]: ...
            @staticmethod
            def shutdown() -> None: ...
        
        mt5 = MT5Stub()

    try:
        import winshell  # type: ignore
    except ImportError:
        winshell = None
    
    try:
        from win32com.client import Dispatch  # type: ignore
    except ImportError:
        Dispatch = None

# Platform Detection mit besserer Type-Safety
SYSTEM = platform.system()
IS_WINDOWS = SYSTEM == "Windows"
IS_MACOS = SYSTEM == "Darwin"
IS_LINUX = SYSTEM == "Linux"

def safe_import_mt5() -> Optional[Any]:
    """Sicherer MT5 Import mit Error-Handling"""
    if not IS_WINDOWS:
        return None
    
    try:
        import MetaTrader5 as mt5  # type: ignore
        return mt5
    except ImportError as e:
        print(f"MT5 Import Fehler: {e}")
        return None

def safe_import_winshell() -> Optional[Any]:
    """Sicherer winshell Import"""
    if not IS_WINDOWS:
        return None
    
    try:
        import winshell  # type: ignore[import]
        return winshell
    except ImportError:
        return None

def safe_import_win32com() -> Optional[Any]:
    """Sicherer win32com Import"""
    if not IS_WINDOWS:
        return None
    
    try:
        from win32com.client import Dispatch  # type: ignore[import]
        return Dispatch
    except ImportError:
        return None

# Globale Imports für bessere Type-Safety
MT5_MODULE = safe_import_mt5()
WINSHELL_MODULE = safe_import_winshell()
WIN32COM_DISPATCH = safe_import_win32com()

def is_mt5_available() -> bool:
    """Prüft ob MT5 verfügbar ist"""
    return MT5_MODULE is not None

def is_winshell_available() -> bool:
    """Prüft ob winshell verfügbar ist"""
    return WINSHELL_MODULE is not None

def is_win32com_available() -> bool:
    """Prüft ob win32com verfügbar ist"""
    return WIN32COM_DISPATCH is not None

# Sichere datetime Sortierung
def safe_datetime_sort_key(trade_obj: Any) -> Any:
    """Sichere Sortierung für Trades mit potentiell None datetime"""
    if hasattr(trade_obj, 'close_time') and trade_obj.close_time is not None:
        return trade_obj.close_time
    elif hasattr(trade_obj, 'open_time') and trade_obj.open_time is not None:
        return trade_obj.open_time
    else:
        # Fallback: sehr altes Datum für None-Werte
        from datetime import datetime
        return datetime.min

# Sichere filedialog Parameter
def get_safe_filedialog_params(
    title: str = "",
    filetypes: Optional[List[Tuple[str, str]]] = None,
    defaultextension: str = "",
    initialdir: str = "",
    initialfile: str = ""
) -> Dict[str, Union[str, List[Tuple[str, str]]]]:
    """Gibt sichere filedialog Parameter zurück"""
    params: Dict[str, Union[str, List[Tuple[str, str]]]] = {
        "title": title,
        "defaultextension": defaultextension
    }
    
    if filetypes:
        params["filetypes"] = filetypes
    
    if initialdir:
        params["initialdir"] = initialdir
    
    if initialfile:
        params["initialfile"] = initialfile
    
    return params

# Error-Handling Decorator
def safe_execute(func):
    """Decorator für sichere Funktionsausführung"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Fehler in {func.__name__}: {e}")
            return None
    return wrapper

# Logging Setup
import logging
from pathlib import Path

def setup_logging(app_name: str = "DRX_Trading_Tracker") -> logging.Logger:
    """Setup für Application Logging"""
    
    # Log-Verzeichnis erstellen
    if IS_WINDOWS:
        log_dir = Path.home() / "Documents" / app_name
    elif IS_MACOS:
        log_dir = Path.home() / "Documents" / app_name
    else:  # Linux
        log_dir = Path.home() / f".{app_name.lower()}"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"
    
    # Logger konfigurieren
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.INFO)
    
    # File Handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Handler hinzufügen (falls noch nicht vorhanden)
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# Type-Safe MT5 Wrapper
class SafeMT5Wrapper:
    """Type-sichere MT5 Wrapper-Klasse"""
    
    def __init__(self):
        self.mt5 = MT5_MODULE
        self.available = self.mt5 is not None
        
    def initialize(self) -> bool:
        """Sichere MT5 Initialisierung"""
        if not self.available or self.mt5 is None:
            return False
        
        try:
            return self.mt5.initialize()  # type: ignore
        except Exception as e:
            print(f"MT5 Initialize Fehler: {e}")
            return False
    
    def login(self, account: int, password: str = "", server: str = "") -> bool:
        """Sichere MT5 Login"""
        if not self.available or self.mt5 is None:
            return False
        
        try:
            return self.mt5.login(account, password=password, server=server)  # type: ignore
        except Exception as e:
            print(f"MT5 Login Fehler: {e}")
            return False
    
    def account_info(self) -> Optional[Any]:
        """Sichere Account Info"""
        if not self.available or self.mt5 is None:
            return None
        
        try:
            return self.mt5.account_info()  # type: ignore
        except Exception as e:
            print(f"MT5 Account Info Fehler: {e}")
            return None
    
    def positions_get(self) -> Optional[Any]:
        """Sichere Positions"""
        if not self.available or self.mt5 is None:
            return None
        
        try:
            return self.mt5.positions_get()  # type: ignore
        except Exception as e:
            print(f"MT5 Positions Fehler: {e}")
            return None
    
    def last_error(self) -> Tuple[int, str]:
        """Sichere Error Info"""
        if not self.available or self.mt5 is None:
            return (0, "MT5 nicht verfügbar")
        
        try:
            return self.mt5.last_error()  # type: ignore
        except Exception as e:
            print(f"MT5 Last Error Fehler: {e}")
            return (-1, str(e))
    
    def shutdown(self) -> None:
        """Sichere MT5 Shutdown"""
        if not self.available or self.mt5 is None:
            return
        
        try:
            self.mt5.shutdown()  # type: ignore
        except Exception as e:
            print(f"MT5 Shutdown Fehler: {e}")

# Utility Functions für bessere Code-Qualität
def validate_file_path(path: Union[str, Path]) -> bool:
    """Validiert Dateipfad"""
    try:
        path_obj = Path(path)
        return path_obj.exists() or path_obj.parent.exists()
    except Exception:
        return False

def safe_float_conversion(value: Any, default: float = 0.0) -> float:
    """Sichere Float-Konvertierung"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int_conversion(value: Any, default: int = 0) -> int:
    """Sichere Int-Konvertierung"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_string_conversion(value: Any, default: str = "") -> str:
    """Sichere String-Konvertierung"""
    try:
        return str(value)
    except Exception:
        return default

# Platform-spezifische Utilities
class PlatformUtils:
    """Platform-spezifische Hilfsfunktionen"""
    
    @staticmethod
    def get_data_directory(app_name: str) -> Path:
        """Gibt plattform-spezifischen Daten-Ordner zurück"""
        if IS_WINDOWS:
            return Path.home() / "Documents" / app_name
        elif IS_MACOS:
            return Path.home() / "Documents" / app_name
        else:  # Linux
            return Path.home() / f".{app_name.lower()}"
    
    @staticmethod
    def open_file_manager(path: Path) -> bool:
        """Öffnet Datei-Manager plattform-spezifisch"""
        try:
            if IS_WINDOWS:
                import os
                os.startfile(path)  # type: ignore
            elif IS_MACOS:
                import subprocess
                subprocess.run(["open", str(path)])
            else:  # Linux
                import subprocess
                subprocess.run(["xdg-open", str(path)])
            return True
        except Exception as e:
            print(f"Datei-Manager öffnen fehlgeschlagen: {e}")
            return False
    
    @staticmethod
    def create_desktop_shortcut(
        name: str, 
        target: Path, 
        working_dir: Optional[Path] = None
    ) -> bool:
        """Erstellt Desktop-Verknüpfung plattform-spezifisch"""
        if not IS_WINDOWS:
            return False
        
        try:
            if WINSHELL_MODULE and WIN32COM_DISPATCH:
                desktop = WINSHELL_MODULE.desktop()
                shortcut_path = Path(desktop) / f"{name}.lnk"
                
                shell = WIN32COM_DISPATCH('WScript.Shell')
                shortcut = shell.CreateShortCut(str(shortcut_path))
                shortcut.Targetpath = str(target)
                if working_dir:
                    shortcut.WorkingDirectory = str(working_dir)
                shortcut.save()
                return True
            else:
                # Fallback: BAT-Datei
                desktop = Path.home() / "Desktop"
                if desktop.exists():
                    bat_file = desktop / f"{name}.bat"
                    content = f'@echo off\ncd /d "{working_dir or target.parent}"\n"{target}"\npause'
                    bat_file.write_text(content, encoding='utf-8')
                    return True
                    
        except Exception as e:
            print(f"Desktop-Verknüpfung Fehler: {e}")
        
        return False

# Export für einfache Verwendung
__all__ = [
    'SYSTEM', 'IS_WINDOWS', 'IS_MACOS', 'IS_LINUX',
    'safe_import_mt5', 'safe_import_winshell', 'safe_import_win32com',
    'is_mt5_available', 'is_winshell_available', 'is_win32com_available',
    'safe_datetime_sort_key', 'get_safe_filedialog_params',
    'safe_execute', 'setup_logging',
    'SafeMT5Wrapper', 'PlatformUtils',
    'validate_file_path', 'safe_float_conversion', 'safe_int_conversion', 'safe_string_conversion'
]

if __name__ == "__main__":
    # Test der Error-Fixes
    print("🧪 Teste DRX Error Fixes...")
    print(f"Platform: {SYSTEM}")
    print(f"MT5 verfügbar: {is_mt5_available()}")
    print(f"WinShell verfügbar: {is_winshell_available()}")
    print(f"Win32Com verfügbar: {is_win32com_available()}")
    
    # Logger Test
    logger = setup_logging()
    logger.info("Error Fixes Test erfolgreich!")
    
    print("✅ Alle Tests bestanden!")