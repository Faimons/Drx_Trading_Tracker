#!/usr/bin/env python3
"""
DRX Trading Tracker - Production Version
KEINE DEMO-DATEN - Nur Live-Trading oder Import
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

# System-spezifische Imports
SYSTEM = platform.system()
winshell_available = False
mt5_available = False

if SYSTEM == "Windows":
    try:
        import winshell
        winshell_available = True
    except ImportError:
        winshell_available = False
    
    try:
        import MetaTrader5
        mt5_available = True
    except ImportError:
        mt5_available = False

# Konfiguration
APP_VERSION = "1.2.1"
APP_NAME = "DRX Trading Tracker"

# Platform-spezifische Pfade
if SYSTEM == "Windows":
    data_dir = Path.home() / "Documents" / "DRX Trading Tracker"
elif SYSTEM == "Darwin":
    data_dir = Path.home() / "Documents" / "DRX Trading Tracker"
else:
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
    type: str
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
    status: str = "open"

class DatabaseManager:
    """Datenbank-Manager"""
    
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
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Datenbank-Fehler: {e}")
    
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
            print(f"Trade-Speichern Fehler: {e}")
    
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
    """Basis-Klasse für Broker-Verbindungen"""
    
    def __init__(self, broker_name: str):
        super().__init__()
        self.broker_name = broker_name
        self.connected = False
        self.account_info = {}
        self.credentials = {}
        self.system = SYSTEM
    
    def connect(self, credentials: Dict) -> bool:
        """Verbindung herstellen"""
        self.credentials = credentials
        return True
    
    def disconnect(self):
        """Verbindung trennen"""
        self.connected = False
        self.account_info = {}
    
    def get_account_info(self) -> Dict:
        """Account-Info"""
        return self.account_info
    
    def get_open_trades(self) -> List[Trade]:
        """Offene Trades"""
        return []

class MT5Connector(BrokerConnector):
    """MetaTrader 5 Connector"""
    
    def __init__(self):
        super().__init__("MetaTrader 5")
        self.mt5_available = mt5_available
        self.mt5 = None
        
        if SYSTEM == "Windows" and mt5_available:
            try:
                import MetaTrader5 as mt5
                self.mt5 = mt5
                self.mt5_available = True
                print("✅ MT5 verfügbar")
            except ImportError as e:
                print(f"❌ MT5 Fehler: {e}")
                self.mt5_available = False
        else:
            print(f"ℹ️ MT5 nur unter Windows (aktuell: {SYSTEM})")
    
    def connect(self, credentials: Dict) -> bool:
        """MT5 Verbindung"""
        if not self.mt5_available or self.mt5 is None:
            print(f"❌ MT5 nicht verfügbar unter {SYSTEM}!")
            return False
        
        try:
            if not self.mt5.initialize():
                error_code = self.mt5.last_error()
                print(f"❌ MT5 Init fehlgeschlagen: {error_code}")
                return False
            
            account = int(credentials.get('account', ''))
            password = credentials.get('password', '')
            server = credentials.get('server', '')
            
            if not self.mt5.login(account, password=password, server=server):
                error_code = self.mt5.last_error()
                print(f"❌ MT5 Login fehlgeschlagen: {error_code}")
                return False
            
            account_info = self.mt5.account_info()
            if account_info is None:
                print("❌ Kontoinfo nicht verfügbar!")
                return False
            
            self.connected = True
            self.account_info = account_info._asdict()
            
            print(f"✅ MT5 VERBUNDEN!")
            print(f"   Account: {self.account_info.get('login')}")
            print(f"   Balance: €{self.account_info.get('balance', 0):.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ MT5 Verbindung: {e}")
            return False
    
    def get_open_trades(self) -> List[Trade]:
        """MT5 Trades laden"""
        if not self.connected or not self.mt5_available or self.mt5 is None:
            return []
        
        try:
            positions = self.mt5.positions_get()
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
            print(f"❌ Trade-Laden: {e}")
            return []

def open_file_manager(path: Path):
    """Datei-Manager öffnen"""
    try:
        if SYSTEM == "Windows":
            os.startfile(path)
        elif SYSTEM == "Darwin":
            subprocess.run(["open", str(path)])
        else:
            subprocess.run(["xdg-open", str(path)])
    except Exception as e:
        print(f"Datei-Manager Fehler: {e}")

class DRXTradingApp:
    """DRX Trading Tracker Main App"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{APP_VERSION} - {SYSTEM}")
        self.root.geometry("1400x900")
        
        # Instanzvariablen initialisieren
        self.notebook: Optional[ttk.Notebook] = None
        self.connection_status: Optional[ttk.Label] = None
        self.broker_var: Optional[tk.StringVar] = None
        self.details_frame: Optional[ttk.LabelFrame] = None
        self.connect_btn: Optional[ttk.Button] = None
        self.account_entry: Optional[ttk.Entry] = None
        self.password_entry: Optional[ttk.Entry] = None
        self.server_entry: Optional[ttk.Entry] = None
        self.info_labels: Dict[str, ttk.Label] = {}
        self.fig = None
        self.ax = None
        self.canvas = None
        self.trades_tree: Optional[ttk.Treeview] = None
        
        # Icon laden
        self.load_icon()
        
        # Core Components
        self.db = DatabaseManager()
        self.connector = None
        self.auto_sync = False
        self.sync_thread = None
        
        # UI aufbauen
        self.setup_styles()
        self.create_widgets()
        self.load_config()
        
        # Auto-Sync für Windows
        if SYSTEM == "Windows":
            self.start_auto_sync()
    
    def load_icon(self):
        """Icon laden"""
        try:
            icon_files = ["icon.ico", "app_icon.ico", "drx_icon.ico"]
            
            for icon_file in icon_files:
                icon_path = Path(icon_file)
                if icon_path.exists():
                    self.root.iconbitmap(str(icon_path))
                    print(f"✅ Icon geladen: {icon_file}")
                    return
            
            print("ℹ️ Kein Icon gefunden")
            
        except Exception as e:
            print(f"Icon-Fehler: {e}")
    
    def setup_styles(self):
        """UI-Styles"""
        style = ttk.Style()
        
        if SYSTEM == "Windows":
            style.theme_use('winnative')
        elif SYSTEM == "Darwin":
            style.theme_use('aqua')
        else:
            style.theme_use('clam')
        
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Success.TLabel', foreground='#00C851')
        style.configure('Error.TLabel', foreground='#ff4444')
    
    def create_widgets(self):
        """UI erstellen"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_header(main_frame)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, pady=10)
        
        self.create_connection_tab()
        self.create_dashboard_tab()
        self.create_trades_tab()
        self.create_settings_tab()
    
    def create_header(self, parent):
        """Header"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', pady=(0, 10))
        
        title_text = f"🎯 {APP_NAME} v{APP_VERSION}"
        title_label = ttk.Label(header_frame, text=title_text, style='Title.TLabel')
        title_label.pack(side='left')
        
        system_info = ttk.Label(header_frame, text=f"📱 {SYSTEM}")
        system_info.pack(side='right', padx=10)
        
        self.connection_status = ttk.Label(header_frame, text="❌ Nicht verbunden", 
                                         style='Error.TLabel')
        self.connection_status.pack(side='right', padx=10)
    
    def create_connection_tab(self):
        """Verbindungs-Tab - MIT LOGIN BUTTON!"""
        conn_frame = ttk.Frame(self.notebook)
        self.notebook.add(conn_frame, text='🔗 Verbindung')
        
        # System Info
        info_frame = ttk.LabelFrame(conn_frame, text="System Information", padding=20)
        info_frame.pack(fill='x', padx=20, pady=20)
        
        system_text = f"""
🖥️ System: {SYSTEM} {platform.release()}
🐍 Python: {sys.version_info.major}.{sys.version_info.minor}
📁 Daten: {data_dir}
🔌 MT5: {'✅ Verfügbar' if SYSTEM == 'Windows' else '❌ Nur Windows'}
        """
        ttk.Label(info_frame, text=system_text, justify='left').pack()
        
        # Broker-Auswahl
        broker_frame = ttk.LabelFrame(conn_frame, text="Broker-Integration", padding=20)
        broker_frame.pack(fill='x', padx=20, pady=20)
        
        self.broker_var = tk.StringVar(value="mt5")
        
        if SYSTEM == "Windows":
            brokers = [
                ("✅ MetaTrader 5 (Live Trading)", "mt5"),
                ("📊 CSV Import/Export", "csv")
            ]
        else:
            brokers = [
                ("❌ MetaTrader 5 (nur Windows)", "mt5"),
                ("📊 CSV Import/Export", "csv")
            ]
        
        for text, value in brokers:
            btn = ttk.Radiobutton(broker_frame, text=text, variable=self.broker_var, 
                                 value=value, command=self.on_broker_change)
            btn.pack(anchor='w', pady=5)
            
            if value == "mt5" and SYSTEM != "Windows":
                btn.config(state='disabled')
        
        # Login-Formular
        self.details_frame = ttk.LabelFrame(conn_frame, text="Login", padding=20)
        self.details_frame.pack(fill='x', padx=20, pady=20)
        
        self.create_connection_form()
        
        # WICHTIG: Button-Frame - HIER WAR DER FEHLER!
        button_frame = ttk.Frame(conn_frame)
        button_frame.pack(fill='x', padx=20, pady=20)
        
        # Login-Button für Windows
        if SYSTEM == "Windows":
            self.connect_btn = ttk.Button(button_frame, text="🔗 MT5 Verbinden", 
                                         command=self.connect_broker,
                                         style='Accent.TButton')
            self.connect_btn.pack(side='left', padx=10)
        
        # Import/Export Buttons
        ttk.Button(button_frame, text="📁 CSV Import", 
                  command=self.import_trades).pack(side='left', padx=10)
        
        ttk.Button(button_frame, text="📊 CSV Export", 
                  command=self.export_trades).pack(side='left', padx=10)
        
        # Rechts: System Info
        ttk.Button(button_frame, text="ℹ️ System Info", 
                  command=self.show_system_info).pack(side='right', padx=10)
    
    def create_connection_form(self):
        """Login-Formular"""
        if not self.details_frame:
            return
            
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        broker = self.broker_var.get() if self.broker_var else "mt5"
        
        if broker == "mt5" and SYSTEM == "Windows":
            # MT5 Login-Felder
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
            
            # Hilfe
            help_text = ttk.Label(self.details_frame, 
                text="💡 Starte MT5 zuerst, logge dich ein, dann hier verbinden!", 
                foreground='blue')
            help_text.pack(pady=10)
        
        elif broker == "csv":
            # CSV Info
            csv_info = ttk.Label(self.details_frame, 
                text="📊 CSV Import/Export für alle Plattformen!\n\n" +
                     "• Importiere bestehende Trading-Daten\n" +
                     "• Exportiere für Analyse und Backup\n" +
                     "• Standard-Format wird unterstützt", 
                justify='left')
            csv_info.pack(pady=10)
    
    def create_dashboard_tab(self):
        """Dashboard"""
        dash_frame = ttk.Frame(self.notebook)
        self.notebook.add(dash_frame, text='📊 Dashboard')
        
        # Account Info
        account_frame = ttk.LabelFrame(dash_frame, text="Account Overview", padding=20)
        account_frame.pack(fill='x', padx=20, pady=20)
        
        info_frame = ttk.Frame(account_frame)
        info_frame.pack(fill='x')
        
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
        chart_frame = ttk.LabelFrame(dash_frame, text="Performance", padding=20)
        chart_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.create_performance_chart(chart_frame)
        
        # Actions
        actions_frame = ttk.Frame(dash_frame)
        actions_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(actions_frame, text="🔄 Aktualisieren", 
                  command=self.refresh_all_data).pack(side='left', padx=10)
        
        ttk.Button(actions_frame, text="📁 Daten-Ordner", 
                  command=lambda: open_file_manager(data_dir)).pack(side='left', padx=10)
    
    def create_performance_chart(self, parent):
        """Performance Chart"""
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.fig.patch.set_facecolor('white')
        
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        self.update_performance_chart()
    
    def create_trades_tab(self):
        """Trades Tab"""
        trades_frame = ttk.Frame(self.notebook)
        self.notebook.add(trades_frame, text='📈 Trades')
        
        # Controls
        controls_frame = ttk.Frame(trades_frame)
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(controls_frame, text="🔄 Aktualisieren", 
                  command=self.refresh_trades).pack(side='left', padx=10)
        
        ttk.Button(controls_frame, text="📊 Export", 
                  command=self.export_trades).pack(side='left', padx=10)
        
        ttk.Button(controls_frame, text="📁 Import", 
                  command=self.import_trades).pack(side='left', padx=10)
        
        # Trades Table
        table_frame = ttk.Frame(trades_frame)
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('ID', 'Symbol', 'Typ', 'Lots', 'Entry', 'Exit', 'P&L', 'Status')
        self.trades_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.trades_tree.heading(col, text=col)
            self.trades_tree.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.trades_tree.yview)
        self.trades_tree.configure(yscrollcommand=v_scrollbar.set)
        
        self.trades_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
    
    def create_settings_tab(self):
        """Settings"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text='⚙️ Einstellungen')
        
        # System
        system_frame = ttk.LabelFrame(settings_frame, text="System", padding=20)
        system_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(system_frame, text="📁 Daten-Ordner", 
                  command=lambda: open_file_manager(data_dir)).pack(side='left', padx=10)
        
        ttk.Button(system_frame, text="💾 Backup", 
                  command=self.create_backup).pack(side='left', padx=10)
        
        # About
        about_frame = ttk.LabelFrame(settings_frame, text="Über", padding=20)
        about_frame.pack(fill='x', padx=20, pady=20)
        
        about_text = f"""
{APP_NAME} v{APP_VERSION}
Professional Trading Journal

🖥️ Platform: {SYSTEM}
📁 Daten: {data_dir}

© 2024 DRX Trading
        """
        
        ttk.Label(about_frame, text=about_text, justify='left').pack()
    
    # =============================================================================
    # CORE METHODS
    # =============================================================================
    
    def on_broker_change(self):
        """Broker-Wechsel"""
        self.create_connection_form()
    
    def connect_broker(self):
        """MT5 Verbinden"""
        if SYSTEM != "Windows":
            messagebox.showwarning("Platform", "MetaTrader 5 nur unter Windows!")
            return
        
        try:
            self.connector = MT5Connector()
            if not self.connector.mt5_available:
                messagebox.showerror("MT5 Fehler", 
                    "MetaTrader 5 nicht installiert!\n\n" +
                    "1. MT5 von MetaQuotes herunterladen\n" +
                    "2. pip install MetaTrader5\n" +
                    "3. MT5 starten und einloggen")
                return
            
            credentials = {
                'account': self.account_entry.get() if self.account_entry else '',
                'password': self.password_entry.get() if self.password_entry else '',
                'server': self.server_entry.get() if self.server_entry else ''
            }
            
            if not all(credentials.values()):
                messagebox.showerror("Fehler", "Alle Felder ausfüllen!")
                return
            
            if self.connector.connect(credentials):
                if self.connection_status:
                    self.connection_status.config(text="✅ MT5 Verbunden", style='Success.TLabel')
                messagebox.showinfo("Erfolg", "MT5 erfolgreich verbunden!")
                self.refresh_all_data()
                if self.notebook:
                    self.notebook.select(1)  # Dashboard
            else:
                messagebox.showerror("Fehler", "MT5 Verbindung fehlgeschlagen!")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Verbindungsfehler: {str(e)}")
    
    def refresh_all_data(self):
        """Daten aktualisieren"""
        self.refresh_trades()
        self.update_dashboard_info()
        self.update_performance_chart()
    
    def update_dashboard_info(self):
        """Dashboard aktualisieren"""
        trades = self.db.get_all_trades()
        
        total_trades = len(trades)
        open_trades = len([t for t in trades if t.status == 'open'])
        closed_trades = [t for t in trades if t.status == 'closed']
        
        win_trades = len([t for t in closed_trades if t.profit and t.profit > 0])
        win_rate = (win_trades / len(closed_trades) * 100) if closed_trades else 0
        
        total_pnl = sum(t.profit for t in trades if t.profit is not None)
        
        if self.info_labels:
            self.info_labels['total_trades'].config(text=str(total_trades))
            self.info_labels['open_positions'].config(text=str(open_trades))
            self.info_labels['win_rate'].config(text=f"{win_rate:.1f}%")
            self.info_labels['total_pnl'].config(text=f"€{total_pnl:.2f}")
            
            if total_pnl > 0:
                self.info_labels['total_pnl'].config(foreground='#00C851')
            elif total_pnl < 0:
                self.info_labels['total_pnl'].config(foreground='#ff4444')
    
    def refresh_trades(self):
        """Trades-Tabelle aktualisieren"""
        if not self.trades_tree:
            return
            
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
                trade.status.upper()
            )
            
            tags = ()
            if trade.profit and trade.profit > 0:
                tags = ('profit',)
            elif trade.profit and trade.profit < 0:
                tags = ('loss',)
            
            self.trades_tree.insert('', 'end', values=values, tags=tags)
        
        self.trades_tree.tag_configure('profit', foreground='#00C851')
        self.trades_tree.tag_configure('loss', foreground='#ff4444')
    
    def update_performance_chart(self):
        """Performance Chart"""
        if not self.ax:
            return
            
        trades = self.db.get_all_trades()
        closed_trades = [t for t in trades if t.status == 'closed' and t.close_time]
        
        self.ax.clear()
        
        if not closed_trades:
            self.ax.text(0.5, 0.5, 'Keine Daten\n\nImportiere CSV oder verbinde MT5', 
                        ha='center', va='center', transform=self.ax.transAxes, fontsize=12)
        else:
            closed_trades.sort(key=lambda x: x.close_time or datetime.min)
            
            cumulative_pnl = []
            running_total = 0
            dates = []
            
            for trade in closed_trades:
                if trade.profit is not None and trade.close_time:
                    running_total += trade.profit
                    cumulative_pnl.append(running_total)
                    dates.append(trade.close_time)
            
            if dates and cumulative_pnl:
                self.ax.plot(dates, cumulative_pnl, 'b-', linewidth=2, label='Equity Curve')
                self.ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
                self.ax.set_title('Performance')
                self.ax.set_ylabel('P&L (€)')
                self.ax.grid(True, alpha=0.3)
                self.ax.legend()
                self.fig.autofmt_xdate()
        
        if self.canvas:
            self.canvas.draw()
    
    def export_trades(self):
        """CSV Export"""
        trades = self.db.get_all_trades()
        
        if not trades:
            messagebox.showinfo("Export", "Keine Trades vorhanden")
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
                
                messagebox.showinfo("Export", f"✅ {len(trades)} Trades exportiert!")
                
            except Exception as e:
                messagebox.showerror("Export Fehler", f"❌ {e}")
    
    def import_trades(self):
        """CSV Import"""
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
                messagebox.showinfo("Import", f"✅ {imported_count} Trades importiert!")
                
            except Exception as e:
                messagebox.showerror("Import Fehler", f"❌ {e}")
    
    def create_backup(self):
        """Backup erstellen"""
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
                messagebox.showinfo("Backup", "✅ Backup erstellt!")
            except Exception as e:
                messagebox.showerror("Backup Fehler", f"❌ {e}")
    
    def show_system_info(self):
        """System Info anzeigen"""
        info = f"""
🖥️ System Information
━━━━━━━━━━━━━━━━━━━━━━━━━

OS: {platform.system()} {platform.release()}
Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
App: {APP_NAME} v{APP_VERSION}

📁 Daten: {data_dir}
💾 DB: {DATABASE_FILE}

🔌 MT5: {'✅ Verfügbar' if SYSTEM == 'Windows' else '❌ Nur Windows'}
        """
        messagebox.showinfo("System Info", info)
    
    def start_auto_sync(self):
        """Auto-Sync für MT5"""
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
        """Config laden"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    print(f"Config geladen: {len(config)} Einträge")
        except Exception as e:
            print(f"Config Fehler: {e}")
    
    def save_config(self):
        """Config speichern"""
        try:
            config = {
                'system': SYSTEM,
                'version': APP_VERSION,
                'data_dir': str(data_dir)
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
        self.refresh_all_data()
        self.root.mainloop()

def main():
    """Hauptfunktion"""
    print(f"🎯 {APP_NAME} v{APP_VERSION}")
    print(f"📱 Platform: {SYSTEM}")
    print(f"📁 Daten: {data_dir}")
    print("=" * 50)
    
    try:
        app = DRXTradingApp()
        app.run()
    except Exception as e:
        print(f"❌ Kritischer Fehler: {e}")
        messagebox.showerror("Kritischer Fehler", f"App konnte nicht gestartet werden:\n{str(e)}")

if __name__ == "__main__":
    main()