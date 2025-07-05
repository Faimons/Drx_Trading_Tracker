# 🎯 DRX Trading Tracker

**Professionelles Trading Journal mit automatischer Broker-Integration**

[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)](https://github.com/drx-trading/tracker)
[![Python](https://img.shields.io/badge/Python-3.7%2B-green)](https://python.org)
[![License](https://img.shields.io/badge/License-Commercial-red)](https://drx-trading.com)

---

## 📋 Inhaltsverzeichnis

- [🚀 Schnellstart](#-schnellstart)
- [💻 System-Anforderungen](#-system-anforderungen)
- [📥 Installation](#-installation)
- [🔧 Setup für verschiedene Plattformen](#-setup-für-verschiedene-plattformen)
- [📊 Features](#-features)
- [🔌 Broker-Integration](#-broker-integration)
- [📈 Erste Schritte](#-erste-schritte)
- [🆘 Problembehandlung](#-problembehandlung)
- [📞 Support](#-support)

---

## 🚀 Schnellstart

### Für Eilige (Windows):
1. ⬇️ Lade `DRX_Trading_Tracker_Windows.zip` herunter
2. 📂 Entpacke die ZIP-Datei
3. ▶️ Führe `install.bat` aus
4. 🎉 Fertig! Die App startet automatisch

### Für alle anderen Plattformen:
Siehe detaillierte [Installation](#-installation) unten ⬇️

---

## 💻 System-Anforderungen

### ✅ Unterstützte Betriebssysteme:
- **Windows:** 7, 8, 10, 11 (32-bit & 64-bit)
- **macOS:** 10.12+ (Sierra und neuer)
- **Linux:** Ubuntu 18.04+, Debian 9+, Fedora 28+, andere Distributionen

### 🔧 Technische Anforderungen:
- **RAM:** Mindestens 2 GB (4 GB empfohlen)
- **Festplatte:** 100 MB freier Speicher
- **Python:** 3.7 oder neuer (falls Source-Installation)
- **Internet:** Für Broker-Verbindung und Updates

### 🔌 Broker-Kompatibilität:
| Broker | Windows | macOS | Linux | Status |
|--------|---------|-------|-------|--------|
| MetaTrader 5 | ✅ Vollständig | ❌ Nicht verfügbar | ❌ Nicht verfügbar | Aktiv |
| CSV Import/Export | ✅ Vollständig | ✅ Vollständig | ✅ Vollständig | Aktiv |
| Andere Broker | 🔧 In Entwicklung | 🔧 In Entwicklung | 🔧 In Entwicklung | Bald |

---

## 📥 Installation

### 🪟 Windows - Ein-Klick Installation

#### Option 1: Automatischer Installer (Empfohlen)
```bash
1. Lade DRX_Trading_Tracker_Windows.zip herunter
2. Entpacke die ZIP-Datei
3. Führe install.bat als Administrator aus
4. Folge den Anweisungen
```

#### Option 2: Portable Version
```bash
1. Lade DRX_Trading_Tracker_Windows.zip herunter
2. Entpacke die ZIP-Datei
3. Starte DRX_Trading_Tracker.exe direkt
```

#### Option 3: Python Source (Fortgeschrittene)
```bash
# 1. Python 3.7+ installieren von python.org
# 2. Repository klonen oder herunterladen
git clone https://github.com/drx-trading/tracker.git
cd tracker

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. App starten
python drx_trading_tracker_improved.py
```

### 🍎 macOS - Native App

#### Option 1: App Bundle (Empfohlen)
```bash
1. Lade DRX_Trading_Tracker_macOS.zip herunter
2. Entpacke die ZIP-Datei
3. Führe install.sh aus oder kopiere DRX_Trading_Tracker.app nach Applications
4. Starte über Launchpad oder Finder
```

#### Option 2: Python Source
```bash
# 1. Python 3.7+ installieren (empfohlen via Homebrew)
brew install python3

# 2. Repository klonen
git clone https://github.com/drx-trading/tracker.git
cd tracker

# 3. Abhängigkeiten installieren
pip3 install -r requirements.txt

# 4. App starten
python3 drx_trading_tracker_improved.py
```

### 🐧 Linux - Universal

#### Option 1: AppImage (Empfohlen)
```bash
# 1. Download
wget https://releases.drx-trading.com/DRX_Trading_Tracker_Linux.zip
unzip DRX_Trading_Tracker_Linux.zip

# 2. Installation
chmod +x install.sh
./install.sh

# 3. Start über Anwendungsmenü oder:
~/.local/bin/DRX_Trading_Tracker
```

#### Option 2: Python Source
```bash
# 1. Python 3.7+ installieren
sudo apt update
sudo apt install python3 python3-pip python3-tk

# Oder für Fedora/CentOS:
sudo dnf install python3 python3-pip python3-tkinter

# 2. Repository klonen
git clone https://github.com/drx-trading/tracker.git
cd tracker

# 3. Abhängigkeiten installieren
pip3 install -r requirements.txt --user

# 4. App starten
python3 drx_trading_tracker_improved.py
```

---

## 🔧 Setup für verschiedene Plattformen

### 🪟 Windows Setup

#### MetaTrader 5 Integration:
1. **MT5 installieren:**
   - Lade MT5 von [MetaQuotes](https://www.metatrader5.com/de/download) herunter
   - Installiere und starte MT5
   - Logge dich in dein Trading-Konto ein

2. **DRX Tracker konfigurieren:**
   ```
   Tab "Verbindung" öffnen
   → MetaTrader 5 auswählen
   → Kontodaten eingeben:
     • Konto-Nummer: [Deine MT5 Account-Nr]
     • Passwort: [Dein Trading-Passwort]
     • Server: [Dein Broker-Server]
   → "Verbinden" klicken
   ```

#### Problembehandlung Windows:
- **"MetaTrader5 nicht gefunden"**: `pip install MetaTrader5` ausführen
- **"Zugriff verweigert"**: Als Administrator ausführen
- **"MT5 Verbindung fehlgeschlagen"**: MT5 muss geöffnet und eingeloggt sein

### 🍎 macOS Setup

#### Besonderheiten für macOS:
- **Sicherheit:** Bei erster Ausführung Rechtsklick → "Öffnen"
- **Python-Installation:** Homebrew empfohlen: `brew install python3`
- **MT5:** Nicht verfügbar - nutze CSV Import/Export

#### Terminal-Installation:
```bash
# Xcode Command Line Tools
xcode-select --install

# Homebrew installieren (falls nicht vorhanden)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python und Abhängigkeiten
brew install python3
pip3 install -r requirements.txt
```

### 🐧 Linux Setup

#### Distribution-spezifisch:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk python3-dev
sudo apt install python3-matplotlib python3-pandas
```

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install python3 python3-pip python3-tkinter python3-devel
sudo dnf install python3-matplotlib python3-pandas
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip tk python-matplotlib python-pandas
```

#### Desktop-Integration:
```bash
# .desktop Datei erstellen für Anwendungsmenü
cat > ~/.local/share/applications/drx-trading-tracker.desktop << EOF
[Desktop Entry]
Name=DRX Trading Tracker
Comment=Professional Trading Journal
Exec=/path/to/drx_trading_tracker_improved.py
Icon=application-default-icon
Terminal=false
Type=Application
Categories=Office;Finance;
EOF
```

---

## 📊 Features

### 🔄 Automatische Synchronisation
- **MT5 Live-Verbindung** (Windows)
- **Echtzeit-Konto-Info** (Balance, Equity, Margin)
- **Automatischer Trade-Import**
- **Background-Sync** alle 5 Sekunden

### 📈 Trade-Management
- **Übersichtliche Trade-Tabelle**
- **Status-Tracking** (Offen, Geschlossen, Pending)
- **P&L Berechnung** mit Kommission und Swap
- **Trade-Details** (Symbol, Lots, Entry/Exit, Zeit)

### 📊 Analytics & Charts
- **Equity Curve** - Performanceverlauf
- **Win/Loss Ratio** - Erfolgsquote
- **P&L Verteilung** - Gewinn/Verlust-Analyse
- **Trading-Statistiken** (Win-Rate, Profit Factor, etc.)

### 💾 Daten-Management
- **CSV Import/Export** - Universell kompatibel
- **SQLite Datenbank** - Schnell und zuverlässig
- **Automatische Backups**
- **Demo-Daten** für Testing

### 🎨 Benutzerfreundlichkeit
- **Cross-Platform GUI** - Tkinter-basiert
- **Dunkles/Helles Theme** - Systemanpassung
- **Responsive Design** - Skaliert automatisch
- **Multi-Language Support** (Deutsch/Englisch)

---

## 🔌 Broker-Integration

### ✅ Aktuell unterstützt:

#### MetaTrader 5 (nur Windows)
- **Live-Verbindung** mit MT5 Terminal
- **Automatischer Trade-Import**
- **Echtzeit-Kontoinformationen**
- **Historische Daten** (bis zu 30 Tage)

**Setup:**
```python
1. MT5 installieren und einloggen
2. DRX Tracker starten
3. Tab "Verbindung" → MT5 auswählen
4. Kontodaten eingeben und verbinden
```

#### CSV Import/Export (alle Plattformen)
- **Universelles Format** für alle Broker
- **Batch-Import** von historischen Trades
- **Export** für Backup und Analyse
- **Custom CSV Mapping**

**Unterstützte CSV-Formate:**
```csv
# Standard Format
ID,Symbol,Type,Lots,Open Price,Close Price,Open Time,Close Time,Profit,Commission,Swap,Comment,Status

# MT5 Export Format
Ticket,Symbol,Type,Volume,Price Open,Price Close,Time Open,Time Close,Profit,Commission,Swap,Comment,State

# Vereinfachtes Format (Minimum)
Symbol,Type,Lots,Entry,Exit,PnL
```

### 🔧 In Entwicklung:

- **MetaTrader 4** (Windows) - Q2 2024
- **XTB API** (alle Plattformen) - Q3 2024
- **Plus500 API** (alle Plattformen) - Q3 2024
- **eToro API** (alle Plattformen) - Q4 2024
- **Interactive Brokers** (alle Plattformen) - Q4 2024

---

## 📈 Erste Schritte

### 1️⃣ Installation abschließen
- Download und Installation wie oben beschrieben
- App erfolgreich gestartet ✅

### 2️⃣ Erste Konfiguration
```
1. Tab "Einstellungen" öffnen
2. Daten-Ordner überprüfen
3. System-Informationen kontrollieren
4. Optional: Backup-Intervall einstellen
```

### 3️⃣ Daten importieren

#### Option A: MetaTrader 5 (Windows)
```
1. MT5 starten und einloggen
2. DRX Tracker → Tab "Verbindung"
3. MetaTrader 5 auswählen
4. Kontodaten eingeben
5. "Verbinden" klicken
6. Automatischer Import startet
```

#### Option B: CSV Import (alle Plattformen)
```
1. Trading-Daten als CSV exportieren
2. DRX Tracker → Tab "Trades"
3. "Import CSV" klicken
4. CSV-Datei auswählen
5. Import bestätigen
```

#### Option C: Demo-Daten (zum Testen)
```
1. Tab "Verbindung" öffnen
2. "Demo Daten" klicken
3. Beispiel-Trades werden geladen
4. Funktionen testen
```

### 4️⃣ Dashboard erkunden
```
1. Tab "Dashboard" öffnen
2. Kontoinformationen überprüfen
3. Performance-Chart betrachten
4. Auto-Sync aktivieren (falls MT5)
```

### 5️⃣ Analyse nutzen
```
1. Tab "Analyse" öffnen
2. Trading-Statistiken ansehen
3. Charts generieren:
   • Equity Curve
   • P&L Verteilung
   • Win/Loss Ratio
```

---

## 🆘 Problembehandlung

### 🚨 Häufige Probleme

#### 🪟 Windows-spezifisch

**Problem: "MetaTrader5 Modul nicht gefunden"**
```bash
# Lösung:
pip install MetaTrader5
# oder
pip install --upgrade MetaTrader5
```

**Problem: "MT5 Verbindung fehlgeschlagen"**
```
Prüfung:
1. ✅ MT5 ist geöffnet und eingeloggt
2. ✅ Kontodaten sind korrekt
3. ✅ Server ist erreichbar
4. ✅ DRX Tracker als Admin ausgeführt
```

**Problem: "Zugriff verweigert"**
```
Lösung:
1. Rechtsklick auf DRX_Trading_Tracker.exe
2. "Als Administrator ausführen"
3. Oder: Programm in andere Ordner verschieben
```

#### 🍎 macOS-spezifisch

**Problem: "App kann nicht geöffnet werden"**
```
Lösung:
1. Rechtsklick auf DRX_Trading_Tracker.app
2. "Öffnen" auswählen
3. Bei Warnung "Trotzdem öffnen"
```

**Problem: "Python-Module nicht gefunden"**
```bash
# Homebrew Installation prüfen:
brew doctor

# Python-Pfad prüfen:
which python3

# Module neu installieren:
pip3 install --user -r requirements.txt
```

#### 🐧 Linux-spezifisch

**Problem: "tkinter nicht gefunden"**
```bash
# Ubuntu/Debian:
sudo apt install python3-tk

# Fedora:
sudo dnf install python3-tkinter

# Arch:
sudo pacman -S tk
```

**Problem: "Permission denied"**
```bash
# Ausführberechtigung setzen:
chmod +x drx_trading_tracker_improved.py

# Oder via Python ausführen:
python3 drx_trading_tracker_improved.py
```

### 🔧 Allgemeine Probleme

#### "Datenbank-Fehler"
```
Lösung:
1. App schließen
2. Daten-Ordner öffnen (Tab "Einstellungen")
3. Backup der drx_trades.db erstellen
4. Datei löschen (wird neu erstellt)
5. App neu starten
```

#### "Charts werden nicht angezeigt"
```bash
# Matplotlib-Problem lösen:
pip install --upgrade matplotlib

# Oder Backend ändern:
export MPLBACKEND=TkAgg
```

#### "CSV Import schlägt fehl"
```
Prüfung:
1. ✅ CSV-Datei ist nicht geöffnet in Excel
2. ✅ Spaltenheader sind korrekt
3. ✅ Datenformat ist konsistent
4. ✅ Keine Sonderzeichen in Pfad
```

### 📋 Debug-Informationen sammeln

#### System-Info ausgeben:
```python
# In Python-Konsole ausführen:
import platform
import sys
print(f"System: {platform.platform()}")
print(f"Python: {sys.version}")
print(f"Architektur: {platform.architecture()}")
```

#### Log-Dateien finden:
```
Windows: %USERPROFILE%\Documents\DRX Trading Tracker\drx_log.txt
macOS: ~/Documents/DRX Trading Tracker/drx_log.txt
Linux: ~/.drx_trading_tracker/drx_log.txt
```

---

## 📞 Support

### 🆘 Sofortiger Support

#### 📧 E-Mail Support
- **Allgemeine Fragen:** info@drx-trading.com
- **Technische Probleme:** support@drx-trading.com
- **Feature-Anfragen:** features@drx-trading.com

#### 🌐 Online-Ressourcen
- **Website:** [www.drx-trading.com](https://www.drx-trading.com)
- **Dokumentation:** [docs.drx-trading.com](https://docs.drx-trading.com)
- **Video-Tutorials:** [youtube.com/drxtrading](https://youtube.com/drxtrading)
- **FAQ:** [faq.drx-trading.com](https://faq.drx-trading.com)

### 📋 Support-Anfrage stellen

**Bitte folgende Informationen mitschicken:**

```
1. Betriebssystem: [Windows 10/11, macOS 12.x, Ubuntu 20.04, etc.]
2. App-Version: [1.2.0]
3. Installation-Methode: [Installer/Portable/Python]
4. Fehlerbeschreibung: [Was passiert genau?]
5. Schritte zur Reproduktion: [Wie kann Fehler wiederholt werden?]
6. Screenshots: [Falls UI-Problem]
7. Log-Dateien: [Aus Daten-Ordner]
```

### 🎓 Lernressourcen

#### 📹 Video-Tutorials
- **Installation auf Windows** (5 Min)
- **MT5 Integration Setup** (8 Min)
- **CSV Import/Export** (6 Min)
- **Trading-Analyse nutzen** (12 Min)
- **Troubleshooting häufiger Probleme** (10 Min)

#### 📚 Dokumentation
- **Benutzerhandbuch** (PDF, 40 Seiten)
- **API-Referenz** für Entwickler
- **CSV-Format Spezifikation**
- **Best Practices** für Trading-Journale

### 🔄 Updates & Changelog

#### Aktuelle Version: 1.2.0
- ✅ Cross-Platform Support (Windows/macOS/Linux)
- ✅ Verbesserte MT5 Integration
- ✅ CSV Import/Export Funktionen
- ✅ Performance-Optimierungen
- ✅ Bug-Fixes und Stabilität

#### Geplante Features (Roadmap):
- **v1.3.0** - MetaTrader 4 Support
- **v1.4.0** - Zusätzliche Broker-APIs
- **v1.5.0** - Cloud-Sync Feature
- **v2.0.0** - Web-Interface

---

## 📄 Lizenz & Copyright

```
DRX Trading Tracker v1.2.0
© 2024 DRX Trading - Alle Rechte vorbehalten

Diese Software ist urheberrechtlich geschützt.
Kommerzielle Nutzung nur mit gültiger Lizenz.

Lizenz-Typ: Commercial Software
Support-Zeitraum: 12 Monate ab Kauf
Updates: Kostenlos für alle v1.x Versionen
```

### 🛡️ Haftungsausschluss

```
WICHTIGER HINWEIS:
Diese Software dient ausschließlich der Analyse und Dokumentation 
von Trading-Aktivitäten. Sie stellt keine Anlageberatung dar und 
übernimmt keine Haftung für Trading-Entscheidungen oder -Verluste.

Trading birgt erhebliche Risiken. Handeln Sie nur mit Geld, 
dessen Verlust Sie sich leisten können.
```

---

## 🙏 Danksagungen

- **Python Community** für die exzellenten Libraries
- **MetaQuotes** für die MT5 Python API
- **Tkinter Entwickler** für das GUI Framework
- **Matplotlib Team** für die Charting-Library
- **Beta-Tester** für wertvolles Feedback

---

## 📞 Kontakt

**DRX Trading**
- 🌐 Website: [www.drx-trading.com](https://www.drx-trading.com)
- 📧 E-Mail: info@drx-trading.com
- 📱 Telefon: +49 (0) 123 456 789
- 📍 Adresse: Musterstraße 123, 12345 Musterstadt, Deutschland

---

*Letzte Aktualisierung: Januar 2024*
*Version: 1.2.0*