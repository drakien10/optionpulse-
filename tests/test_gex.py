from src.core.gex import OptionRow, net_gex, gamma_flip, max_pain, walls

def _book():
    # Spot 100: altinda put agirligi, ustunde call agirligi -> flip ~100 civari
    rows = []
    for k in (90, 92, 95, 97):
        rows.append(OptionRow(k, 30/365, "p", 5000, 0.22))
    for k in (103, 105, 108, 110):
        rows.append(OptionRow(k, 30/365, "c", 5000, 0.20))
    return rows

def test_sign_convention():
    only_puts = [OptionRow(100, 30/365, "p", 1000, 0.2)]
    only_calls = [OptionRow(100, 30/365, "c", 1000, 0.2)]
    assert net_gex(only_puts, 100) < 0
    assert net_gex(only_calls, 100) > 0

def test_flip_exists_and_reasonable():
    f = gamma_flip(_book(), spot=100.0)
    assert f is not None and 96 < f < 104

def test_regime_sides_of_flip():
    rows = _book()
    f = gamma_flip(rows, 100.0)
    assert net_gex(rows, f - 3) < 0   # flip altinda negatif gamma
    assert net_gex(rows, f + 3) > 0   # ustunde pozitif

def test_max_pain():
    rows = [OptionRow(100, 30/365, "c", 10, 0.2),
            OptionRow(120, 30/365, "p", 5, 0.2)]
    # P=100: put kaybi 20*5*100=10k | P=120: call kaybi 20*10*100=20k -> 100
    assert max_pain(rows) == 100

def test_walls():
    rows = [OptionRow(105, 30/365, "c", 9000, 0.2),
            OptionRow(100, 30/365, "c", 100, 0.2),
            OptionRow(95, 30/365, "p", 8000, 0.2)]
    w = walls(rows)
    assert w["call_wall"] == 105 and w["put_wall"] == 95
