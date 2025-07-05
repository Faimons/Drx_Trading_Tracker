#!/usr/bin/env python3
"""
DRX Trading Tracker - Cross-Platform Version
Professionelles Trading Journal mit automatischer Broker-Integration

Kompatibel mit Windows, macOS und Linux
Benutzerfreundliche Installation und Setup
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from datetime import datetime, timedelta
import requests
import threading
import time
import os
import platform
import webbrowser
import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional

# System-spezifische Imports (bedingt)
SYSTEM = platform.system()
winshell_available = False
mt5_available = False

if SYSTEM == "Windows":
    try:
        import winshell  # type: ignore[import]
        winshell_available = True
    except ImportError:
        winshell_available = False
    
    try:
        import MetaTrader5  # type: ignore[import]
        mt5_available = True
    except ImportError:
        mt5_available = False

# Konfiguration
APP_VERSION = "1.2.0"
APP_NAME = "DRX Trading Tracker"

# Platform-spezifische Pfade
if SYSTEM == "Windows":
    data_dir = Path.home() / "Documents" / "DRX Trading Tracker"
elif SYSTEM == "Darwin":  # macOS
    data_dir = Path.home() / "Documents" / "DRX Trading Tracker"
else:  # Linux
    data_dir = Path.home() / ".drx_trading_tracker"

data_dir.mkdir(parents=True, exist_ok=True)

DATABASE_FILE = str(data_dir / "drx_trades.db")
CONFIG_FILE = str(data_dir / "drx_config.json")
LOG_FILE = str(data_dir / "drx_log.txt")

@dataclass
class Trade:
    """Trade-Datenklasse"""
    id: str
    symbol: str
    type: str  # 'buy' oder 'sell'
    lots: float
    open_price: float
    close_price: Optional[float] = None
    open_time: Optional[datetime] = None
    close_time: Optional[datetime] = None
    profit: float = 0.0
    commission: float = 0.0
    swap: float = 0.0
    comment: str = ""
    magic: int = 0
    status: str = "open"  # 'open', 'closed', 'pending'

class DatabaseManager:
    """Cross-Platform Datenbank-Manager"""
    
    def __init__(self, db_file: str = DATABASE_FILE):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Datenbank initialisieren"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    type TEXT NOT NULL,
                    lots REAL NOT NULL,
                    open_price REAL NOT NULL,
                    close_price REAL,
                    open_time TEXT,
                    close_time TEXT,
                    profit REAL DEFAULT 0,
                    commission REAL DEFAULT 0,
                    swap REAL DEFAULT 0,
                    comment TEXT,
                    magic INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'open'
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS account_info (
                    id INTEGER PRIMARY KEY,
                    broker TEXT,
                    account_number TEXT,
                    balance REAL,
                    equity REAL,
                    margin REAL,
                    free_margin REAL,
                    last_update TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Datenbank-Initialisierung Fehler: {e}")
    
    def save_trade(self, trade: Trade):
        """Trade speichern"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO trades 
                (id, symbol, type, lots, open_price, close_price, open_time, close_time, 
                 profit, commission, swap, comment, magic, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade.id, trade.symbol, trade.type, trade.lots, trade.open_price,
                trade.close_price, 
                trade.open_time.isoformat() if trade.open_time else None,
                trade.close_time.isoformat() if trade.close_time else None,
                trade.profit, trade.commission, trade.swap, trade.comment, 
                trade.magic, trade.status
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Trade-Speicherung Fehler: {e}")
    
    def get_all_trades(self) -> List[Trade]:
        """Alle Trades laden"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM trades ORDER BY open_time DESC')
            rows = cursor.fetchall()
            conn.close()
            
            trades = []
            for row in rows:
                trade = Trade(
                    id=row[0], symbol=row[1], type=row[2], lots=row[3],
                    open_price=row[4], close_price=row[5],
                    open_time=datetime.fromisoformat(row[6]) if row[6] else None,
                    close_time=datetime.fromisoformat(row[7]) if row[7] else None,
                    profit=row[8], commission=row[9], swap=row[10],
                    comment=row[11], magic=row[12], status=row[13]
                )
                trades.append(trade)
            
            return trades
            
        except Exception as e:
            print(f"Trade-Laden Fehler: {e}")
            return []

class BrokerConnector:
    """Cross-Platform Basis-Klasse für Broker-Verbindungen"""
    
    def __init__(self, broker_name: str):
        self.broker_name = broker_name
        self.connected = False
        self.account_info = {}
        self.credentials = {}
        self.system = SYSTEM
    
    def connect(self, credentials: Dict) -> bool:
        """Verbindung zum Broker herstellen"""
        self.credentials = credentials
        return True
    
    def disconnect(self):
        """Verbindung trennen"""
        self.connected = False
        self.account_info = {}
    
    def get_account_info(self) -> Dict:
        """Account-Informationen abrufen"""
        return self.account_info
    
    def get_open_trades(self) -> List[Trade]:
        """Offene Trades abrufen"""
        return []
    
    def get_trade_history(self, days: int = 30) -> List[Trade]:
        """Trade-Historie abrufen"""
        return []

class MT5Connector(BrokerConnector):
    """MetaTrader 5 Connector - nur für Windows"""
    
    def __init__(self):
        super().__init__("MetaTrader 5")
        self.mt5_available = mt5_available
        self.mt5 = None
        
        if SYSTEM == "Windows" and mt5_available:
            try:
                import MetaTrader5 as mt5  # type: ignore[import]
                self.mt5 = mt5
                self.mt5_available = True
                print("✅ MT5 Modul erfolgreich geladen!")
            except ImportError as e:
                print(f"❌ MT5 Import Fehler: {e}")
                self.mt5_available = False
        else:
            print(f"ℹ️ MetaTrader 5 ist nur unter Windows verfügbar (aktuell: {SYSTEM})")
    
    def connect(self, credentials: Dict) -> bool:
        """MT5 Verbindung - nur Windows"""
        if not self.mt5_available or self.mt5 is None:
            print(f"❌ FEHLER: MT5 nicht verfügbar unter {SYSTEM}!")
            return False
        
        try:
            # MT5 Terminal initialisieren
            if not self.mt5.initialize():  # type: ignore
                error_code = self.mt5.last_error()  # type: ignore
                print(f"❌ FEHLER: MT5 Initialisierung fehlgeschlagen! Code: {error_code}")
                return False
            
            # Login Daten
            account = int(credentials.get('account', ''))
            password = credentials.get('password', '')
            server = credentials.get('server', '')
            
            print(f"🔄 Verbinde mit Account: {account}, Server: {server}")
            
            # Login
            if not self.mt5.login(account, password=password, server=server):  # type: ignore
                error_code = self.mt5.last_error()  # type: ignore
                print(f"❌ FEHLER: MT5 Login fehlgeschlagen! Code: {error_code}")
                return False
            
            # Account Info laden
            account_info = self.mt5.account_info()  # type: ignore
            if account_info is None:
                print("❌ FEHLER: Kontoinfo konnte nicht geladen werden!")
                return False
            
            self.connected = True
            self.account_info = account_info._asdict()
            
            print(f"✅ MT5 ERFOLGREICH VERBUNDEN!")
            print(f"   Account: {self.account_info.get('login')}")
            print(f"   Balance: €{self.account_info.get('balance', 0):.2f}")
            print(f"   Equity: €{self.account_info.get('equity', 0):.2f}")
            print(f"   Server: {self.account_info.get('server')}")
            
            return True
            
        except Exception as e:
            print(f"❌ FEHLER: MT5 Verbindung: {e}")
            return False
    
    def get_open_trades(self) -> List[Trade]:
        """Offene MT5 Trades"""
        if not self.connected or not self.mt5_available or self.mt5 is None:
            return []
        
        try:
            positions = self.mt5.positions_get()  # type: ignore
            if positions is None:
                return []
            
            trades = []
            for pos in positions:
                trade = Trade(
                    id=str(pos.ticket),
                    symbol=pos.symbol,
                    type='buy' if pos.type == 0 else 'sell',
                    lots=pos.volume,
                    open_price=pos.price_open,
                    open_time=datetime.fromtimestamp(pos.time),
                    profit=pos.profit,
                    commission=pos.commission,
                    swap=pos.swap,
                    comment=pos.comment,
                    magic=pos.magic,
                    status='open'
                )
                trades.append(trade)
            
            return trades
            
        except Exception as e:
            print(f"❌ FEHLER beim Laden der offenen Trades: {e}")
            return []

def open_file_manager(path: Path):
    """Cross-Platform Datei-Manager öffnen"""
    try:
        if SYSTEM == "Windows":
            os.startfile(path)
        elif SYSTEM == "Darwin":  # macOS
            subprocess.run(["open", str(path)])
        else:  # Linux
            subprocess.run(["xdg-open", str(path)])
    except Exception as e:
        print(f"Datei-Manager öffnen fehlgeschlagen: {e}")

def show_system_info():
    """System-Informationen anzeigen"""
    info = f"""
🖥️ System Information:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Betriebssystem: {platform.system()} {platform.release()}
Architektur: {platform.machine()}
Python Version: {sys.version}
DRX Tracker: v{APP_VERSION}

📁 Daten-Ordner: {DATA_DIR}
💾 Datenbank: {DATABASE_FILE}
⚙️ Konfiguration: {CONFIG_FILE}

🔌 MetaTrader 5: {'✅ Verfügbar' if SYSTEM == 'Windows' else '❌ Nur Windows'}
    """
    return info

class DRXTradingApp:
    """Cross-Platform DRX Trading Tracker"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{APP_VERSION} - {SYSTEM}")
        self.root.geometry("1400x900")
        
        # App Icon (falls verfügbar)
        try:
            icon_path = data_dir / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
        
        # Datenbank und Connector
        self.db = DatabaseManager()
        self.connector = None
        self.auto_sync = False
        self.sync_thread = None
        
        # UI-Setup
        self.setup_styles()
        self.create_widgets()
        self.load_config()
        
        # Auto-Sync für Windows mit MT5
        if SYSTEM == "Windows":
            self.start_auto_sync()
        
        # Welcome Dialog
        self.show_welcome_dialog()
    
    def show_welcome_dialog(self):
        """Willkommen-Dialog anzeigen"""
        welcome_msg = f"""
🎯 Willkommen zu DRX Trading Tracker v{APP_VERSION}!

Platform: {SYSTEM} {platform.release()}
Daten-Ordner: {DATA_DIR}

"""
        
        if SYSTEM == "Windows":
            welcome_msg += "✅ MetaTrader 5 Integration verfügbar\n"
        else:
            welcome_msg += "ℹ️ MetaTrader 5 nur unter Windows verfügbar\n"
            welcome_msg += "📊 CSV Import/Export weiterhin möglich\n"
        
        welcome_msg += """
Erste Schritte:
1. Gehe zum Tab 'Verbindung' für Broker-Setup
2. Importiere bestehende Trades über CSV
3. Analysiere deine Performance

Viel Erfolg! 📈
        """
        
        messagebox.showinfo("Willkommen", welcome_msg)
    
    def setup_styles(self):
        """Cross-Platform UI-Styles"""
        style = ttk.Style()
        
        # Platform-spezifische Themes
        if SYSTEM == "Windows":
            style.theme_use('winnative')
        elif SYSTEM == "Darwin":
            style.theme_use('aqua')
        else:
            style.theme_use('clam')
        
        # Custom Styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='#00C851')
        style.configure('Error.TLabel', foreground='#ff4444')
        style.configure('Info.TLabel', foreground='#33b5e5')
    
    def create_widgets(self):
        """Cross-Platform UI erstellen"""
        # Hauptframe
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_frame)
        
        # Notebook für Tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, pady=10)
        
        # Tabs erstellen
        self.create_connection_tab()
        self.create_dashboard_tab()
        self.create_trades_tab()
        self.create_analytics_tab()
        self.create_settings_tab()
    
    def create_header(self, parent):
        """Header mit System-Info"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Titel
        title_text = f"🎯 {APP_NAME} v{APP_VERSION}"
        title_label = ttk.Label(header_frame, text=title_text, style='Title.TLabel')
        title_label.pack(side='left')
        
        # System Info
        system_info = ttk.Label(header_frame, text=f"📱 {SYSTEM}", style='Info.TLabel')
        system_info.pack(side='right', padx=10)
        
        # Status
        self.status_frame = ttk.Frame(header_frame)
        self.status_frame.pack(side='right')
        
        self.connection_status = ttk.Label(self.status_frame, text="❌ Nicht verbunden", 
                                         style='Error.TLabel')
        self.connection_status.pack(side='right', padx=10)
    
    def create_connection_tab(self):
        """Cross-Platform Verbindungs-Tab"""
        conn_frame = ttk.Frame(self.notebook)
        self.notebook.add(conn_frame, text='🔗 Verbindung')
        
        # System-spezifische Hinweise
        info_frame = ttk.LabelFrame(conn_frame, text="System Information", padding=20)
        info_frame.pack(fill='x', padx=20, pady=20)
        
        system_text = show_system_info()
        ttk.Label(info_frame, text=system_text, justify='left', font=('Courier', 9)).pack()
        
        # Broker-Auswahl
        broker_frame = ttk.LabelFrame(conn_frame, text="Verfügbare Broker", padding=20)
        broker_frame.pack(fill='x', padx=20, pady=20)
        
        self.broker_var = tk.StringVar(value="mt5")
        
        # Platform-spezifische Broker-Liste
        if SYSTEM == "Windows":
            brokers = [
                ("✅ MetaTrader 5", "mt5"),
                ("🔧 MetaTrader 4", "mt4"),
                ("🔧 Andere Broker (Coming Soon)", "other")
            ]
        else:
            brokers = [
                ("❌ MetaTrader 5 (nur Windows)", "mt5"),
                ("📊 CSV Import/Export", "csv"),
                ("🔧 API Broker (Coming Soon)", "api")
            ]
        
        for text, value in brokers:
            btn = ttk.Radiobutton(broker_frame, text=text, variable=self.broker_var, 
                                 value=value, command=self.on_broker_change)
            btn.pack(anchor='w', pady=5)
            
            # Deaktivieren wenn nicht verfügbar
            if (value == "mt5" and SYSTEM != "Windows") or value in ["mt4", "other", "api"]:
                btn.config(state='disabled')
        
        # Verbindungs-Details
        self.details_frame = ttk.LabelFrame(conn_frame, text="Setup", padding=20)
        self.details_frame.pack(fill='x', padx=20, pady=20)
        
        self.create_connection_form()
        
        # Aktions-Buttons
        button_frame = ttk.Frame(conn_frame)
        button_frame.pack(fill='x', padx=20, pady=20)
        
        if SYSTEM == "Windows":
            self.connect_btn = ttk.Button(button_frame, text="🔗 MT5 Verbinden", 
                                         command=self.connect_broker)
            self.connect_btn.pack(side='left', padx=10)
        
        ttk.Button(button_frame, text="📁 CSV Import", 
                  command=self.import_trades).pack(side='left', padx=10)
        
        ttk.Button(button_frame, text="📊 Demo Daten", 
                  command=self.load_demo_data).pack(side='left', padx=10)
        
        ttk.Button(button_frame, text="ℹ️ System Info", 
                  command=lambda: messagebox.showinfo("System Info", show_system_info())).pack(side='right', padx=10)
    
    def create_connection_form(self):
        """Platform-spezifisches Verbindungsformular"""
        # Alte Widgets entfernen
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        broker = self.broker_var.get()
        
        if broker == "mt5" and SYSTEM == "Windows":
            # MetaTrader Felder
            fields_frame = ttk.Frame(self.details_frame)
            fields_frame.pack(fill='x')
            
            ttk.Label(fields_frame, text="Konto-Nummer:").grid(row=0, column=0, sticky='w', pady=5)
            self.account_entry = ttk.Entry(fields_frame, width=30)
            self.account_entry.grid(row=0, column=1, padx=10, pady=5)
            
            ttk.Label(fields_frame, text="Passwort:").grid(row=1, column=0, sticky='w', pady=5)
            self.password_entry = ttk.Entry(fields_frame, width=30, show='*')
            self.password_entry.grid(row=1, column=1, padx=10, pady=5)
            
            ttk.Label(fields_frame, text="Server:").grid(row=2, column=0, sticky='w', pady=5)
            self.server_entry = ttk.Entry(fields_frame, width=30)
            self.server_entry.grid(row=2, column=1, padx=10, pady=5)
            
            # Hilfe-Text
            help_text = ttk.Label(self.details_frame, 
                text="💡 Tipp: Starte zuerst MT5, logge dich dort ein, dann hier verbinden!", 
                foreground='blue')
            help_text.pack(pady=10)
        
        elif broker == "csv":
            # CSV Import
            csv_info = ttk.Label(self.details_frame, 
                text="📊 CSV Import/Export für alle Plattformen verfügbar!\n\n" +
                     "Unterstützte Formate:\n" +
                     "• Standard CSV mit Spalten: Symbol, Type, Lots, Entry, Exit, P&L\n" +
                     "• MetaTrader Export-Format\n" +
                     "• Eigene CSV-Dateien", 
                justify='left')
            csv_info.pack(pady=10)
        
        else:
            # Nicht verfügbar
            unavail_info = ttk.Label(self.details_frame, 
                text="🔧 Diese Integration wird noch entwickelt.\n\n" +
                     "Aktuell verfügbar:\n" +
                     f"• MetaTrader 5 (nur Windows)\n" +
                     "• CSV Import/Export (alle Plattformen)", 
                justify='left')
            unavail_info.pack(pady=10)
    
    def create_dashboard_tab(self):
        """Cross-Platform Dashboard"""
        dash_frame = ttk.Frame(self.notebook)
        self.notebook.add(dash_frame, text='📊 Dashboard')
        
        # Platform Info
        platform_frame = ttk.LabelFrame(dash_frame, text="Platform Status", padding=10)
        platform_frame.pack(fill='x', padx=20, pady=10)
        
        platform_info = f"🖥️ {SYSTEM} | 🐍 Python {sys.version_info.major}.{sys.version_info.minor} | 📁 {DATA_DIR}"
        ttk.Label(platform_frame, text=platform_info, font=('Courier', 9)).pack()
        
        # Kontoinfo
        account_frame = ttk.LabelFrame(dash_frame, text="Account Overview", padding=20)
        account_frame.pack(fill='x', padx=20, pady=20)
        
        info_frame = ttk.Frame(account_frame)
        info_frame.pack(fill='x')
        
        # Labels erstellen
        labels = [
            ("Trades gesamt:", "total_trades"),
            ("Offene Positionen:", "open_positions"),
            ("Gewinn-Rate:", "win_rate"),
            ("Gesamt P&L:", "total_pnl")
        ]
        
        self.info_labels = {}
        for i, (text, key) in enumerate(labels):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(info_frame, text=text, font=('Arial', 12, 'bold')).grid(
                row=row, column=col, sticky='w', padx=10, pady=5)
            
            label = ttk.Label(info_frame, text="0", font=('Arial', 12))
            label.grid(row=row, column=col+1, sticky='w', padx=10, pady=5)
            self.info_labels[key] = label
        
        # Performance Chart
        chart_frame = ttk.LabelFrame(dash_frame, text="Performance Übersicht", padding=20)
        chart_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.create_performance_chart(chart_frame)
        
        # Quick Actions
        actions_frame = ttk.Frame(dash_frame)
        actions_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(actions_frame, text="🔄 Aktualisieren", 
                  command=self.refresh_all_data).pack(side='left', padx=10)
        
        ttk.Button(actions_frame, text="📁 Daten-Ordner", 
                  command=lambda: open_file_manager(data_dir)).pack(side='left', padx=10)
        
        ttk.Button(actions_frame, text="📊 Export CSV", 
                  command=self.export_trades).pack(side='right', padx=10)
    
    def create_performance_chart(self, parent):
        """Performance Chart"""
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.fig.patch.set_facecolor('white')
        
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        self.update_performance_chart()
    
    def create_trades_tab(self):
        """Trades-Übersicht Tab"""
        trades_frame = ttk.Frame(self.notebook)
        self.notebook.add(trades_frame, text='📈 Trades')
        
        # Controls
        controls_frame = ttk.Frame(trades_frame)
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(controls_frame, text="🔄 Aktualisieren", 
                  command=self.refresh_trades).pack(side='left', padx=10)
        
        ttk.Button(controls_frame, text="📊 Export CSV", 
                  command=self.export_trades).pack(side='left', padx=10)
        
        ttk.Button(controls_frame, text="📁 Import CSV", 
                  command=self.import_trades).pack(side='left', padx=10)
        
        # Trades Table
        table_frame = ttk.Frame(trades_frame)
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('ID', 'Symbol', 'Typ', 'Lots', 'Entry', 'Exit', 'P&L', 'Zeit', 'Status')
        self.trades_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.trades_tree.heading(col, text=col)
            self.trades_tree.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.trades_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=self.trades_tree.xview)
        self.trades_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.trades_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
    
    def create_analytics_tab(self):
        """Analytics Tab"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text='📊 Analyse')
        
        ttk.Label(analytics_frame, text="🔧 Analytics werden implementiert...", 
                 style='Info.TLabel').pack(expand=True)
    
    def create_settings_tab(self):
        """Cross-Platform Settings"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text='⚙️ Einstellungen')
        
        # System Settings
        system_frame = ttk.LabelFrame(settings_frame, text="System", padding=20)
        system_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(system_frame, text="📁 Daten-Ordner öffnen", 
                  command=lambda: open_file_manager(data_dir)).pack(side='left', padx=10)
        
        ttk.Button(system_frame, text="💾 Backup erstellen", 
                  command=self.create_backup).pack(side='left', padx=10)
        
        ttk.Button(system_frame, text="ℹ️ System Info", 
                  command=lambda: messagebox.showinfo("System Info", show_system_info())).pack(side='left', padx=10)
        
        # About
        about_frame = ttk.LabelFrame(settings_frame, text="Über DRX Trading Tracker", padding=20)
        about_frame.pack(fill='x', padx=20, pady=20)
        
        about_text = f"""
{APP_NAME} v{APP_VERSION}
Cross-Platform Trading Journal

🖥️ Platform: {SYSTEM} {platform.release()}
🐍 Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
📁 Daten: {DATA_DIR}

Entwickelt für professionelle Trader
© 2024 DRX Trading - Alle Rechte vorbehalten

Support: info@drx-trading.com
        """
        
        ttk.Label(about_frame, text=about_text, justify='left').pack()
        
        ttk.Button(about_frame, text="🌐 Website besuchen", 
                  command=lambda: webbrowser.open("https://www.drx-trading.com")).pack(pady=10)
    
    # =============================================================================
    # EVENT HANDLERS & CORE METHODS
    # =============================================================================
    
    def on_broker_change(self):
        """Broker-Änderung"""
        self.create_connection_form()
    
    def connect_broker(self):
        """Broker verbinden - nur Windows MT5"""
        if SYSTEM != "Windows":
            messagebox.showwarning("Platform", "MetaTrader 5 ist nur unter Windows verfügbar!")
            return
        
        try:
            self.connector = MT5Connector()
            if not self.connector.mt5_available:
                messagebox.showerror("MT5 Fehler", 
                    "MetaTrader 5 ist nicht installiert!\n\n" +
                    "Installation:\n" +
                    "1. Lade MT5 von MetaQuotes herunter\n" +
                    "2. Installiere: pip install MetaTrader5\n" +
                    "3. Starte MT5 und logge dich ein")
                return
            
            credentials = {
                'account': self.account_entry.get(),
                'password': self.password_entry.get(),
                'server': self.server_entry.get()
            }
            
            if not all(credentials.values()):
                messagebox.showerror("Fehler", "Bitte alle Felder ausfüllen!")
                return
            
            if self.connector.connect(credentials):
                self.connection_status.config(text="✅ MT5 Verbunden", style='Success.TLabel')
                messagebox.showinfo("Erfolg", "Erfolgreich mit MetaTrader 5 verbunden!")
                self.refresh_all_data()
                self.notebook.select(1)  # Dashboard
            else:
                messagebox.showerror("Fehler", "MT5 Verbindung fehlgeschlagen!")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Verbindungsfehler: {str(e)}")
    
    def load_demo_data(self):
        """Demo-Trades laden"""
        demo_trades = [
            Trade(id="DEMO001", symbol="EURUSD", type="buy", lots=0.1, 
                  open_price=1.1850, close_price=1.1920, 
                  open_time=datetime.now() - timedelta(days=5),
                  close_time=datetime.now() - timedelta(days=4),
                  profit=70.0, status="closed"),
            
            Trade(id="DEMO002", symbol="GBPUSD", type="sell", lots=0.2, 
                  open_price=1.2150, close_price=1.2100, 
                  open_time=datetime.now() - timedelta(days=3),
                  close_time=datetime.now() - timedelta(days=2),
                  profit=100.0, status="closed"),
            
            Trade(id="DEMO003", symbol="USDJPY", type="buy", lots=0.15, 
                  open_price=149.50, close_price=150.20, 
                  open_time=datetime.now() - timedelta(days=1),
                  close_time=datetime.now(),
                  profit=105.0, status="closed")
        ]
        
        for trade in demo_trades:
            self.db.save_trade(trade)
        
        self.refresh_all_data()
        messagebox.showinfo("Demo Daten", f"{len(demo_trades)} Demo-Trades erfolgreich geladen!")
    
    def refresh_all_data(self):
        """Alle Daten aktualisieren"""
        self.refresh_trades()
        self.update_dashboard_info()
        self.update_performance_chart()
    
    def update_dashboard_info(self):
        """Dashboard Informationen aktualisieren"""
        trades = self.db.get_all_trades()
        
        total_trades = len(trades)
        open_trades = len([t for t in trades if t.status == 'open'])
        closed_trades = [t for t in trades if t.status == 'closed']
        
        win_trades = len([t for t in closed_trades if t.profit > 0])
        win_rate = (win_trades / len(closed_trades) * 100) if closed_trades else 0
        
        total_pnl = sum(t.profit for t in trades if t.profit is not None)
        
        # Labels aktualisieren
        self.info_labels['total_trades'].config(text=str(total_trades))
        self.info_labels['open_positions'].config(text=str(open_trades))
        self.info_labels['win_rate'].config(text=f"{win_rate:.1f}%")
        self.info_labels['total_pnl'].config(text=f"€{total_pnl:.2f}")
        
        # P&L Farbe
        if total_pnl > 0:
            self.info_labels['total_pnl'].config(foreground='#00C851')
        elif total_pnl < 0:
            self.info_labels['total_pnl'].config(foreground='#ff4444')
    
    def refresh_trades(self):
        """Trades-Tabelle aktualisieren"""
        for item in self.trades_tree.get_children():
            self.trades_tree.delete(item)
        
        trades = self.db.get_all_trades()
        
        for trade in trades:
            values = (
                trade.id[:8] + "..." if len(trade.id) > 8 else trade.id,
                trade.symbol,
                trade.type.upper(),
                f"{trade.lots:.2f}",
                f"{trade.open_price:.5f}",
                f"{trade.close_price:.5f}" if trade.close_price else "Open",
                f"€{trade.profit:.2f}",
                trade.open_time.strftime("%d.%m %H:%M") if trade.open_time else "",
                trade.status.upper()
            )
            
            tags = ()
            if trade.profit > 0:
                tags = ('profit',)
            elif trade.profit < 0:
                tags = ('loss',)
            
            self.trades_tree.insert('', 'end', values=values, tags=tags)
        
        self.trades_tree.tag_configure('profit', foreground='#00C851')
        self.trades_tree.tag_configure('loss', foreground='#ff4444')
    
    def update_performance_chart(self):
        """Performance Chart aktualisieren"""
        trades = self.db.get_all_trades()
        closed_trades = [t for t in trades if t.status == 'closed' and t.close_time is not None]
        
        self.ax.clear()
        
        if not closed_trades:
            self.ax.text(0.5, 0.5, 'Noch keine Daten verfügbar\n\nLade Demo-Daten oder importiere CSV', 
                        ha='center', va='center', transform=self.ax.transAxes, fontsize=12)
        else:
            # Sichere Sortierung - nur Trades mit close_time
            closed_trades.sort(key=lambda x: x.close_time or datetime.min)
            
            cumulative_pnl = []
            running_total = 0
            dates = []
            
            for trade in closed_trades:
                if trade.profit is not None and trade.close_time is not None:
                    running_total += trade.profit
                    cumulative_pnl.append(running_total)
                    dates.append(trade.close_time)
            
            if dates and cumulative_pnl:
                self.ax.plot(dates, cumulative_pnl, 'b-', linewidth=2, label='Equity Curve')
                self.ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
                self.ax.set_title('Performance Übersicht')
                self.ax.set_xlabel('Datum')
                self.ax.set_ylabel('P&L (€)')
                self.ax.grid(True, alpha=0.3)
                self.ax.legend()
                
                self.fig.autofmt_xdate()
            else:
                self.ax.text(0.5, 0.5, 'Keine vollständigen Trade-Daten verfügbar', 
                            ha='center', va='center', transform=self.ax.transAxes, fontsize=12)
        
        self.canvas.draw()
    
    def export_trades(self):
        """Cross-Platform CSV Export"""
        trades = self.db.get_all_trades()
        
        if not trades:
            messagebox.showinfo("Export", "Keine Trades zum Exportieren vorhanden")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Trades exportieren",
            initialdir=str(data_dir)
        )
        
        if filename:
            try:
                data = []
                for trade in trades:
                    data.append({
                        'ID': trade.id,
                        'Symbol': trade.symbol,
                        'Type': trade.type,
                        'Lots': trade.lots,
                        'Open Price': trade.open_price,
                        'Close Price': trade.close_price,
                        'Open Time': trade.open_time.isoformat() if trade.open_time else '',
                        'Close Time': trade.close_time.isoformat() if trade.close_time else '',
                        'Profit': trade.profit,
                        'Commission': trade.commission,
                        'Swap': trade.swap,
                        'Comment': trade.comment,
                        'Status': trade.status
                    })
                
                df = pd.DataFrame(data)
                df.to_csv(filename, index=False)
                
                messagebox.showinfo("Export", f"✅ {len(trades)} Trades erfolgreich exportiert!")
                
            except Exception as e:
                messagebox.showerror("Export Fehler", f"❌ Fehler: {str(e)}")
    
    def import_trades(self):
        """Cross-Platform CSV Import"""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Trades importieren",
            initialdir=str(data_dir)
        )
        
        if filename:
            try:
                df = pd.read_csv(filename)
                
                imported_count = 0
                for _, row in df.iterrows():
                    trade = Trade(
                        id=str(row.get('ID', f"IMPORT_{imported_count}")),
                        symbol=str(row.get('Symbol', '')),
                        type=str(row.get('Type', 'buy')),
                        lots=float(row.get('Lots', 0)),
                        open_price=float(row.get('Open Price', 0)),
                        close_price=float(row.get('Close Price', 0)) if pd.notna(row.get('Close Price')) else None,
                        open_time=datetime.fromisoformat(str(row.get('Open Time'))) if row.get('Open Time') and pd.notna(row.get('Open Time')) else None,
                        close_time=datetime.fromisoformat(str(row.get('Close Time'))) if row.get('Close Time') and pd.notna(row.get('Close Time')) else None,
                        profit=float(row.get('Profit', 0)),
                        commission=float(row.get('Commission', 0)),
                        swap=float(row.get('Swap', 0)),
                        comment=str(row.get('Comment', '')),
                        status=str(row.get('Status', 'closed'))
                    )
                    
                    self.db.save_trade(trade)
                    imported_count += 1
                
                self.refresh_all_data()
                messagebox.showinfo("Import", f"✅ {imported_count} Trades erfolgreich importiert!")
                
            except Exception as e:
                messagebox.showerror("Import Fehler", f"❌ Fehler: {str(e)}")
    
    def create_backup(self):
        """Cross-Platform Backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"drx_backup_{timestamp}.db"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            title="Backup speichern",
            initialdir=str(data_dir),
            initialfile=backup_name
        )
        
        if filename:
            try:
                import shutil
                shutil.copy2(DATABASE_FILE, filename)
                messagebox.showinfo("Backup", f"✅ Backup erfolgreich erstellt!")
            except Exception as e:
                messagebox.showerror("Backup Fehler", f"❌ Fehler: {str(e)}")
    
    def start_auto_sync(self):
        """Auto-Sync nur für Windows MT5"""
        if SYSTEM != "Windows":
            return
        
        def sync_worker():
            while True:
                time.sleep(5)
                if self.connector and self.connector.connected:
                    try:
                        open_trades = self.connector.get_open_trades()
                        for trade in open_trades:
                            self.db.save_trade(trade)
                        
                        self.root.after(0, self.refresh_all_data)
                    except Exception as e:
                        print(f"Auto-Sync Fehler: {e}")
        
        self.sync_thread = threading.Thread(target=sync_worker, daemon=True)
        self.sync_thread.start()
    
    def load_config(self):
        """Konfiguration laden"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    # Config laden wenn nötig
        except Exception as e:
            print(f"Config-Laden Fehler: {e}")
    
    def save_config(self):
        """Konfiguration speichern"""
        try:
            config = {
                'system': SYSTEM,
                'version': APP_VERSION,
                'data_dir': str(DATA_DIR)
            }
            
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Config-Speichern Fehler: {e}")
    
    def on_closing(self):
        """App schließen"""
        self.save_config()
        if self.connector:
            self.connector.disconnect()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """App starten"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initial Daten laden
        self.refresh_all_data()
        
        self.root.mainloop()

def main():
    """Hauptfunktion"""
    print(f"🎯 {APP_NAME} v{APP_VERSION}")
    print(f"📱 Platform: {SYSTEM}")
    print(f"📁 Daten: {DATA_DIR}")
    print("=" * 50)
    
    try:
        app = DRXTradingApp()
        app.run()
    except Exception as e:
        print(f"❌ Kritischer Fehler: {e}")
        messagebox.showerror("Kritischer Fehler", f"App konnte nicht gestartet werden:\n{str(e)}")

if __name__ == "__main__":
    main()