"""Gunluk orkestrator: cek -> hesapla -> snapshot -> HTML.
GitHub Actions'ta calisir; her kaynak bagimsiz try/except, veri yoksa 'dogrulanamadi'.
"""
import json, os, datetime as dt
from src.fetchers import cboe, fred, sentiment
from src.core import gex as G
from src.core.term_structure import TermStructure
from src.core.regime import classify

def main(ticker="SPY"):
    today = dt.date.today()
    snap = {"tarih": str(today), "uretim_zamani": dt.datetime.utcnow().isoformat() + "Z"}

    # --- OptionPulse ---
    op = {}
    try:
        payload = cboe.fetch_chain(ticker)
        spot, rows = cboe.chain_to_rows(payload, max_dte=45, today=today)
        net = G.net_gex(rows, spot)
        flip = G.gamma_flip(rows, spot)
        # En yakin vade max pain
        nearest = min({r.expiry_years for r in rows})
        near_rows = [r for r in rows if abs(r.expiry_years - nearest) < 1e-9]
        w = G.walls(rows)
        op = {"spot": round(spot, 2),
              "net_gex": net, "net_gex_str": f"{net/1e6:+.2f}M$ /%1",
              "flip": round(flip, 1) if flip else None,
              "max_pain": G.max_pain(near_rows),
              "call_wall": w["call_wall"], "put_wall": w["put_wall"],
              "kontrat_sayisi": len(rows)}
    except Exception as e:
        op = {"durum": f"dogrulanamadi: {e}"}

    # --- VIX vade yapisi ---
    ts = None
    try:
        v9, v, v3m = (cboe.fetch_quote("_VIX9D"), cboe.fetch_quote("_VIX"),
                      cboe.fetch_quote("_VIX3M"))
        vv = cboe.fetch_quote("_VVIX")
        if all(x is not None for x in (v9, v, v3m)):
            ts = TermStructure(v9, v, v3m, vv)
            op.update({"vix9d": v9, "vix": v, "vix3m": v3m, "vvix": vv,
                       "ts_label": ts.label})
    except Exception:
        pass

    # --- Rejim ---
    if ts and "net_gex" in op:
        r = classify(op["net_gex"], op["spot"], op.get("flip"), ts,
                     data_fresh=True, event_yakin=False)
        op["rejim"] = {"label": r.label, "confidence": r.confidence,
                       "bilesenler": r.bilesenler, "notlar": r.notlar}
    snap["optionpulse"] = op

    # --- Makro + sentiment ---
    snap["makro"] = fred.fetch_all() if os.environ.get("FRED_API_KEY") else {}
    snap["sentiment"] = {"cnn": sentiment.cnn_fear_greed()}

    os.makedirs("reports", exist_ok=True)
    with open(f"reports/snapshot_{today}.json", "w") as f:
        json.dump(snap, f, indent=2, default=str, ensure_ascii=False)
    from src.report.render import render
    html = render(snap)
    with open("reports/index.html", "w") as f:
        f.write(html)
    print("OK ->", f"reports/snapshot_{today}.json")

if __name__ == "__main__":
    main()
