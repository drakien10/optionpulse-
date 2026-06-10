"""Minimal HTML rapor (Faz 4'te tam tasarima gececek)."""
import json, datetime as dt

def render(snapshot: dict) -> str:
    op = snapshot.get("optionpulse", {})
    rejim = op.get("rejim", {})
    rows = []
    for ad, blok in snapshot.get("makro", {}).items():
        d = blok.get("deger")
        rows.append(f"<tr><td>{ad}</td><td>{d if d is not None else '—'}</td>"
                    f"<td class='src'>{blok.get('kaynak','dogrulanamadi')}</td></tr>")
    fg = snapshot.get("sentiment", {}).get("cnn") or {}
    css = ("body{background:#0d1117;color:#e6edf3;font-family:system-ui;margin:0;padding:24px}"
           ".card{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:16px;margin:12px 0}"
           ".neg{color:#f85149}.pos{color:#3fb950}.warn{color:#d29922}"
           "table{width:100%;border-collapse:collapse}td{padding:6px;border-bottom:1px solid #21262d}"
           ".src{color:#8b949e;font-size:12px}h1{font-size:20px}")
    rejim_cls = "neg" if str(rejim.get("label","")).startswith("Negatif") else "pos"
    html = f"""<!doctype html><html lang="tr"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>OptionPulse — {snapshot.get('tarih','')}</title><style>{css}</style>
<h1>Gunluk Rapor · {snapshot.get('tarih','')}</h1>
<div class="card"><b>Bugunku Rejim:</b> <span class="{rejim_cls}">{rejim.get('label','—')}</span>
 · Guven {rejim.get('confidence','—')}/100<br>
 Net GEX: {op.get('net_gex_str','—')} · Flip: {op.get('flip','—')} · Spot: {op.get('spot','—')}<br>
 Max Pain (en yakin vade): {op.get('max_pain','—')} · Call wall: {op.get('call_wall','—')} · Put wall: {op.get('put_wall','—')}<br>
 VIX yapisi: {op.get('ts_label','—')}<br>
 <span class="src">Kaynak: CBOE delayed · {snapshot.get('uretim_zamani','')}</span></div>
<div class="card"><b>CNN Korku &amp; Acgozluluk:</b> {fg.get('skor','—')} ({fg.get('etiket','—')})</div>
<div class="card"><b>Makro (FRED)</b><table>{''.join(rows)}</table></div>
<div class="card"><b>Notlar</b><br>{'<br>'.join(rejim.get('notlar', []))}</div>
</html>"""
    return html
