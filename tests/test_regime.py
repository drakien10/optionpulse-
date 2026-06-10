from src.core.term_structure import TermStructure
from src.core.regime import classify

def test_backwardation_negative_gamma_high_confidence():
    ts = TermStructure(vix9d=22.16, vix=19.87, vix3m=21.31)
    assert ts.label == "tam_backwardation"
    r = classify(net_gex_usd=-0.63e6, spot=737.05, flip=745.0, ts=ts,
                 data_fresh=True, event_yakin=True)
    assert r.label.startswith("Negatif")
    assert 50 <= r.confidence <= 90   # event yakin oldugu icin tavan degil

def test_calm_positive():
    ts = TermStructure(vix9d=13.0, vix=15.0, vix3m=17.0)
    assert ts.label == "contango"
    r = classify(net_gex_usd=2.5e6, spot=700, flip=660, ts=ts)
    assert r.label.startswith("Pozitif")
