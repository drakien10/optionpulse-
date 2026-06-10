"""BS dogrulamasi — Hull ders kitabi degerleri: S=100,K=100,r=%5,sigma=%20,T=1y"""
from src.core.black_scholes import bs_greeks

def test_call_textbook():
    g = bs_greeks(100, 100, 1.0, 0.05, 0.20, "c")
    assert abs(g.price - 10.4506) < 1e-3
    assert abs(g.delta - 0.6368) < 1e-3
    assert abs(g.gamma - 0.018762) < 1e-5
    assert abs(g.vega - 0.37524) < 1e-4   # 1 IV puani basina

def test_put_call_parity():
    c = bs_greeks(100, 100, 1.0, 0.05, 0.20, "c").price
    p = bs_greeks(100, 100, 1.0, 0.05, 0.20, "p").price
    import math
    assert abs((c - p) - (100 - 100 * math.exp(-0.05))) < 1e-9

def test_degenerate():
    g = bs_greeks(100, 100, 0.0, 0.05, 0.20, "c")
    assert g.price == 0.0 and g.gamma == 0.0
