"""
MetaTrader5 Type Stubs
Löst Type-Checking Probleme für MT5 Integration
"""

from typing import Optional, Tuple, Any, NamedTuple
from datetime import datetime

class AccountInfo(NamedTuple):
    """MT5 Account Info Structure"""
    login: int
    trade_mode: int
    name: str
    server: str
    currency: str
    leverage: int
    limit_orders: int
    margin_so_mode: int
    trade_allowed: bool
    trade_expert: bool
    margin_mode: int
    currency_digits: int
    balance: float
    credit: float
    profit: float
    equity: float
    margin: float
    margin_free: float
    margin_level: float
    margin_so_call: float
    margin_so_so: float
    margin_initial: float
    margin_maintenance: float
    assets: float
    liabilities: float
    commission_blocked: float

class PositionInfo(NamedTuple):
    """MT5 Position Info Structure"""
    ticket: int
    time: int
    time_msc: int
    time_update: int
    time_update_msc: int
    type: int
    magic: int
    identifier: int
    reason: int
    volume: float
    price_open: float
    sl: float
    tp: float
    price_current: float
    swap: float
    profit: float
    symbol: str
    comment: str
    external_id: str

class DealInfo(NamedTuple):
    """MT5 Deal Info Structure"""
    ticket: int
    order: int
    time: int
    time_msc: int
    type: int
    entry: int
    magic: int
    position_id: int
    reason: int
    volume: float
    price: float
    commission: float
    swap: float
    profit: float
    fee: float
    symbol: str
    comment: str
    external_id: str

class TerminalInfo(NamedTuple):
    """MT5 Terminal Info Structure"""
    community_account: bool
    community_connection: bool
    connected: bool
    dlls_allowed: bool
    trade_allowed: bool
    tradeapi_disabled: bool
    email_enabled: bool
    ftp_enabled: bool
    notifications_enabled: bool
    mqid: bool
    build: int
    maxbars: int
    codepage: int
    ping_last: int
    community_balance: float
    retransmission: float
    company: str
    name: str
    language: str
    path: str
    data_path: str
    commondata_path: str

# Type stubs für MetaTrader5 Module
def initialize(path: Optional[str] = None, login: Optional[int] = None, 
               password: Optional[str] = None, server: Optional[str] = None, 
               timeout: Optional[int] = None, portable: bool = False) -> bool:
    """Initialize MT5 connection"""
    ...

def shutdown() -> None:
    """Shutdown MT5 connection"""
    ...

def login(login: int, password: str = "", server: str = "", timeout: int = 60000) -> bool:
    """Login to MT5 account"""
    ...

def account_info() -> Optional[AccountInfo]:
    """Get account information"""
    ...

def terminal_info() -> Optional[TerminalInfo]:
    """Get terminal information"""
    ...

def version() -> Tuple[int, int, str]:
    """Get MT5 version"""
    ...

def last_error() -> Tuple[int, str]:
    """Get last error"""
    ...

def positions_get(symbol: str = "", group: str = "", ticket: int = 0) -> Optional[Tuple[PositionInfo, ...]]:
    """Get open positions"""
    ...

def positions_total() -> int:
    """Get total positions count"""
    ...

def history_deals_get(date_from: Any = None, date_to: Any = None, 
                      group: str = "", ticket: int = 0, 
                      position: int = 0) -> Optional[Tuple[DealInfo, ...]]:
    """Get historical deals"""
    ...

def symbols_get(group: str = "") -> Optional[Tuple[Any, ...]]:
    """Get available symbols"""
    ...

def symbols_total() -> int:
    """Get total symbols count"""
    ...

def symbol_info(symbol: str) -> Optional[Any]:
    """Get symbol information"""
    ...

def symbol_info_tick(symbol: str) -> Optional[Any]:
    """Get symbol tick"""
    ...

def copy_rates_from(symbol: str, timeframe: int, date_from: Any, count: int) -> Optional[Any]:
    """Copy rates from date"""
    ...

def copy_rates_from_pos(symbol: str, timeframe: int, start_pos: int, count: int) -> Optional[Any]:
    """Copy rates from position"""
    ...

def copy_rates_range(symbol: str, timeframe: int, date_from: Any, date_to: Any) -> Optional[Any]:
    """Copy rates range"""
    ...

def copy_ticks_from(symbol: str, date_from: Any, count: int, flags: int) -> Optional[Any]:
    """Copy ticks from date"""
    ...

def copy_ticks_range(symbol: str, date_from: Any, date_to: Any, flags: int) -> Optional[Any]:
    """Copy ticks range"""
    ...

# Constants
TIMEFRAME_M1: int = 1
TIMEFRAME_M5: int = 5
TIMEFRAME_M15: int = 15
TIMEFRAME_M30: int = 30
TIMEFRAME_H1: int = 16385
TIMEFRAME_H4: int = 16388
TIMEFRAME_D1: int = 16408
TIMEFRAME_W1: int = 32769
TIMEFRAME_MN1: int = 49153

ORDER_TYPE_BUY: int = 0
ORDER_TYPE_SELL: int = 1
ORDER_TYPE_BUY_LIMIT: int = 2
ORDER_TYPE_SELL_LIMIT: int = 3
ORDER_TYPE_BUY_STOP: int = 4
ORDER_TYPE_SELL_STOP: int = 5
ORDER_TYPE_BUY_STOP_LIMIT: int = 6
ORDER_TYPE_SELL_STOP_LIMIT: int = 7

POSITION_TYPE_BUY: int = 0
POSITION_TYPE_SELL: int = 1

DEAL_TYPE_BUY: int = 0
DEAL_TYPE_SELL: int = 1
DEAL_TYPE_BALANCE: int = 2
DEAL_TYPE_CREDIT: int = 3
DEAL_TYPE_CHARGE: int = 4
DEAL_TYPE_CORRECTION: int = 5
DEAL_TYPE_BONUS: int = 6
DEAL_TYPE_COMMISSION: int = 7
DEAL_TYPE_COMMISSION_DAILY: int = 8
DEAL_TYPE_COMMISSION_MONTHLY: int = 9
DEAL_TYPE_COMMISSION_AGENT_DAILY: int = 10
DEAL_TYPE_COMMISSION_AGENT_MONTHLY: int = 11
DEAL_TYPE_INTEREST: int = 12
DEAL_TYPE_BUY_CANCELED: int = 13
DEAL_TYPE_SELL_CANCELED: int = 14
DEAL_TYPE_DIVIDEND: int = 15
DEAL_TYPE_DIVIDEND_FRANKED: int = 16
DEAL_TYPE_TAX: int = 17

DEAL_ENTRY_IN: int = 0
DEAL_ENTRY_OUT: int = 1
DEAL_ENTRY_INOUT: int = 2
DEAL_ENTRY_OUT_BY: int = 3

COPY_TICKS_ALL: int = -1
COPY_TICKS_INFO: int = 1
COPY_TICKS_TRADE: int = 2

# Error codes
RES_S_OK: int = 1
RES_E_FAIL: int = -1
RES_E_INVALID_PARAMS: int = -2
RES_E_NO_MEMORY: int = -3
RES_E_NOT_FOUND: int = -4
RES_E_INVALID_VERSION: int = -5
RES_E_AUTH_FAILED: int = -6
RES_E_UNSUPPORTED: int = -7
RES_E_AUTO_TRADING_DISABLED: int = -8
RES_E_INTERNAL_FAIL: int = -10000