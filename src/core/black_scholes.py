"""Black-Scholes greek motoru — bagimsiz, saf Python (scipy gerekmez)."""
import math
from dataclasses import dataclass

_SQRT_2PI = math.sqrt(2.0 * math.pi)

def _phi(x: float) -> float:
    return math.exp(-0.5 * x * x) / _SQRT_2PI

def _N(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

@dataclass
class Greeks:
    price: float
    delta: float
    gamma: float
    vega: float   # 1 puanlik IV degisimi basina (%1)
    theta: float  # gunluk

def bs_greeks(S, K, T, r, sigma, opt_type="c", q=0.0) -> Greeks:
    """Avrupa tipi BS. opt_type: 'c' veya 'p'. T yil cinsinden."""
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return Greeks(0.0, 0.0, 0.0, 0.0, 0.0)
    sqT = math.sqrt(T)
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqT)
    d2 = d1 - sigma * sqT
    dq, dr = math.exp(-q * T), math.exp(-r * T)
    gamma = dq * _phi(d1) / (S * sigma * sqT)
    vega = S * dq * _phi(d1) * sqT / 100.0
    if opt_type == "c":
        price = S * dq * _N(d1) - K * dr * _N(d2)
        delta = dq * _N(d1)
        theta = (-S * dq * _phi(d1) * sigma / (2 * sqT)
                 - r * K * dr * _N(d2) + q * S * dq * _N(d1)) / 365.0
    else:
        price = K * dr * _N(-d2) - S * dq * _N(-d1)
        delta = -dq * _N(-d1)
        theta = (-S * dq * _phi(d1) * sigma / (2 * sqT)
                 + r * K * dr * _N(-d2) - q * S * dq * _N(-d1)) / 365.0
    return Greeks(price, delta, gamma, vega, theta)
