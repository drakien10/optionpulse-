"""Dealer gamma (GEX) motoru.
Konvansiyon (SqueezeMetrics/standart): dealer call'larda LONG gamma,
put'larda SHORT gamma varsayilir -> call katkisi +, put katkisi -.
GEX birimi: spotta %1'lik harekete karsi dealer hedge akisi ($).
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
from .black_scholes import bs_greeks

CONTRACT_MULT = 100

@dataclass
class OptionRow:
    strike: float
    expiry_years: float
    opt_type: str          # 'c' / 'p'
    open_interest: int
    iv: float              # ondalik (0.20 = %20)

def _row_gamma_dollars(row: OptionRow, spot: float, r: float) -> float:
    g = bs_greeks(spot, row.strike, row.expiry_years, r, row.iv, row.opt_type).gamma
    sign = 1.0 if row.opt_type == "c" else -1.0
    return sign * g * row.open_interest * CONTRACT_MULT * spot * spot * 0.01

def gex_per_strike(rows: List[OptionRow], spot: float, r: float = 0.0) -> Dict[float, float]:
    out: Dict[float, float] = {}
    for row in rows:
        if row.open_interest <= 0 or row.iv <= 0 or row.expiry_years <= 0:
            continue
        out[row.strike] = out.get(row.strike, 0.0) + _row_gamma_dollars(row, spot, r)
    return dict(sorted(out.items()))

def net_gex(rows: List[OptionRow], spot: float, r: float = 0.0) -> float:
    return sum(gex_per_strike(rows, spot, r).values())

def gamma_flip(rows: List[OptionRow], spot: float, r: float = 0.0,
               span: float = 0.12, steps: int = 97) -> Optional[float]:
    """Net GEX(S)=0 oldugu spot seviyesi. Her aday spotta gamma YENIDEN
    hesaplanir (kumulatif-OI kestirmesi degil, gercek profil)."""
    lo, hi = spot * (1 - span), spot * (1 + span)
    prev_s = prev_v = None
    for i in range(steps):
        s = lo + (hi - lo) * i / (steps - 1)
        v = net_gex(rows, s, r)
        if prev_v is not None and prev_v * v < 0:
            return prev_s + (s - prev_s) * (0 - prev_v) / (v - prev_v)
        prev_s, prev_v = s, v
    return None

def max_pain(rows: List[OptionRow]) -> Optional[float]:
    """Tek vade icin: opsiyon sahiplerinin toplam kazancini minimize eden kapanis."""
    strikes = sorted({x.strike for x in rows})
    if not strikes:
        return None
    best, best_v = None, None
    for P in strikes:
        tot = 0.0
        for x in rows:
            pay = max(0.0, P - x.strike) if x.opt_type == "c" else max(0.0, x.strike - P)
            tot += pay * x.open_interest * CONTRACT_MULT
        if best_v is None or tot < best_v:
            best, best_v = P, tot
    return best

def walls(rows: List[OptionRow]) -> Dict[str, Optional[float]]:
    call_oi: Dict[float, int] = {}
    put_oi: Dict[float, int] = {}
    for x in rows:
        d = call_oi if x.opt_type == "c" else put_oi
        d[x.strike] = d.get(x.strike, 0) + x.open_interest
    return {
        "call_wall": max(call_oi, key=call_oi.get) if call_oi else None,
        "put_wall": max(put_oi, key=put_oi.get) if put_oi else None,
    }
