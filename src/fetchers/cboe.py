"""CBOE ucretsiz gecikme'li veri (anahtar gerektirmez).
- Opsiyon zinciri: https://cdn.cboe.com/api/global/delayed_quotes/options/SPY.json
  (endeksler icin alt cizgi: _SPX, _VIX)
- Tekil kote:     https://cdn.cboe.com/api/global/delayed_quotes/quotes/_VIX.json
Opsiyon kodu formati: SPY260619C00500000 -> vade 2026-06-19, C, strike 500.000
"""
import re, datetime as dt
import requests
from typing import List, Optional
from ..core.gex import OptionRow

BASE = "https://cdn.cboe.com/api/global/delayed_quotes"
_OPT_RE = re.compile(r"^[A-Z^_]+(\d{6})([CP])(\d{8})$")

def _parse_symbol(sym: str):
    m = _OPT_RE.match(sym.replace(" ", ""))
    if not m:
        return None
    ymd, cp, k = m.groups()
    expiry = dt.date(2000 + int(ymd[:2]), int(ymd[2:4]), int(ymd[4:6]))
    return expiry, ("c" if cp == "C" else "p"), int(k) / 1000.0

def fetch_chain(ticker: str = "SPY", timeout: int = 30) -> dict:
    url = f"{BASE}/options/{ticker}.json"
    r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    return r.json()

def chain_to_rows(payload: dict, max_dte: int = 60,
                  today: Optional[dt.date] = None) -> tuple[float, List[OptionRow]]:
    today = today or dt.date.today()
    data = payload.get("data", {})
    spot = float(data.get("current_price") or data.get("close") or 0.0)
    rows: List[OptionRow] = []
    for o in data.get("options", []):
        parsed = _parse_symbol(o.get("option", ""))
        if not parsed:
            continue
        expiry, cp, strike = parsed
        dte = (expiry - today).days
        if dte <= 0 or dte > max_dte:
            continue
        oi = int(o.get("open_interest") or 0)
        iv = float(o.get("iv") or 0.0)
        if oi <= 0 or iv <= 0:
            continue
        rows.append(OptionRow(strike=strike, expiry_years=dte / 365.0,
                              opt_type=cp, open_interest=oi, iv=iv))
    return spot, rows

def fetch_quote(symbol: str, timeout: int = 20) -> Optional[float]:
    """VIX ailesi: _VIX, _VIX9D, _VIX3M, _VVIX."""
    try:
        r = requests.get(f"{BASE}/quotes/{symbol}.json", timeout=timeout,
                         headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        return float(r.json()["data"]["current_price"])
    except Exception:
        return None
