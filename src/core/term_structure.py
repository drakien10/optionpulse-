"""VIX vade yapisi siniflandirici: VIX9D / VIX / VIX3M."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class TermStructure:
    vix9d: float
    vix: float
    vix3m: float
    vvix: Optional[float] = None

    @property
    def label(self) -> str:
        if self.vix9d < self.vix < self.vix3m:
            return "contango"            # saglikli: kisa < orta < uzun
        if self.vix9d > self.vix and self.vix9d > self.vix3m:
            return "tam_backwardation"   # akut stres
        if self.vix9d > self.vix:
            return "on_uc_backwardation" # front-end kink
        return "karisik"

    @property
    def aciklama(self) -> str:
        return {
            "contango": "Normal vade yapisi — yakin vadede stres fiyatlanmiyor.",
            "on_uc_backwardation": "VIX9D > VIX: yakin gunlerde olay riski fiyatlaniyor, dikkat.",
            "tam_backwardation": "VIX9D hem VIX'i hem VIX3M'i gecti — akut kisa vade stresi.",
            "karisik": "Egri duz/karisik — gecis donemi.",
        }[self.label]
