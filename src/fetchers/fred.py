"""FRED makro serileri (ucretsiz API anahtari: fred.stlouisfed.org)."""
import os, requests
from typing import Optional

SERIES = {
    "10y": "DGS10", "2y": "DGS2", "30y": "DGS30", "10y_reel": "DFII10",
    "10y2y_spread": "T10Y2Y", "10y3m_spread": "T10Y3M",
    "fed_funds_eff": "DFF", "sofr": "SOFR", "fed_bilanco": "WALCL",
    "hy_spread": "BAMLH0A0HYM2", "nfci": "NFCI", "sahm": "SAHMREALTIME",
    "issizlik": "UNRATE", "mortgage30": "MORTGAGE30US",
}

def fetch_series(series_id: str, api_key: Optional[str] = None,
                 limit: int = 5) -> Optional[list]:
    key = api_key or os.environ.get("FRED_API_KEY")
    if not key:
        return None
    url = ("https://api.stlouisfed.org/fred/series/observations"
           f"?series_id={series_id}&api_key={key}&file_type=json"
           f"&sort_order=desc&limit={limit}")
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        obs = [o for o in r.json().get("observations", []) if o["value"] != "."]
        return [(o["date"], float(o["value"])) for o in obs]
    except Exception:
        return None

def fetch_all(api_key: Optional[str] = None) -> dict:
    out = {}
    for ad, sid in SERIES.items():
        data = fetch_series(sid, api_key)
        out[ad] = {"deger": data[0][1], "tarih": data[0][0],
                   "onceki": data[1][1] if len(data) > 1 else None,
                   "kaynak": f"FRED {sid}"} if data else {"deger": None, "durum": "dogrulanamadi"}
    return out
