"""Rejim siniflandirici + guven skoru.
Girdiler: net GEX, flip mesafesi, vade yapisi, VVIX, veri tazeligi.
"""
from dataclasses import dataclass, field
from typing import Optional, List
from .term_structure import TermStructure

@dataclass
class RegimeResult:
    label: str
    confidence: int           # 0-100
    bilesenler: dict = field(default_factory=dict)
    notlar: List[str] = field(default_factory=list)

def classify(net_gex_usd: float,
             spot: float,
             flip: Optional[float],
             ts: TermStructure,
             data_fresh: bool = True,
             event_yakin: bool = False,
             flip_yakinlik_pct: float = 1.5) -> RegimeResult:
    notlar = []
    # 1) Ana eksen: GEX isareti
    if net_gex_usd < 0:
        base = "Negatif Gamma / Refleksif"
        notlar.append("Dealer'lar piyasayla ayni yonde hedge eder — hareketler sertlesir, amortisor yok.")
    else:
        base = "Pozitif Gamma / Sonumleyici"
        notlar.append("Dealer hedge'i harekete karsi calisir — bant ici sonumlenme beklenir.")

    # 2) Flip mesafesi
    flip_uyari = False
    if flip is not None and spot > 0:
        dist_pct = abs(spot - flip) / spot * 100
        if dist_pct <= flip_yakinlik_pct:
            flip_uyari = True
            notlar.append(f"Spot, gamma flip seviyesine %{dist_pct:.1f} mesafede — rejim her an donebilir.")

    # 3) Vade yapisi katmani
    ts_skor = {"contango": 25, "karisik": 15, "on_uc_backwardation": 8, "tam_backwardation": 0}[ts.label]
    notlar.append(ts.aciklama)

    # Guven skoru: veri(40) + katman uyumu(40) + event(20)
    veri = 40 if data_fresh else 15
    uyum = 15
    if (net_gex_usd < 0) == (ts.label in ("on_uc_backwardation", "tam_backwardation")):
        uyum = 40  # GEX ve vol yapisi ayni hikayeyi anlatiyor
    elif flip_uyari:
        uyum = 20
    event = 8 if event_yakin else 20
    conf = min(100, veri + uyum + event - (10 if flip_uyari else 0))

    return RegimeResult(
        label=base,
        confidence=max(0, conf),
        bilesenler={"veri": veri, "katman_uyumu": uyum, "event": event,
                    "ts_label": ts.label, "ts_skor": ts_skor},
        notlar=notlar,
    )
