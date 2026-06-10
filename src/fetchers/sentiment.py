"""CNN Fear & Greed + CBOE Put/Call."""
import requests
from typing import Optional

def cnn_fear_greed(timeout: int = 20) -> Optional[dict]:
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        fg = r.json().get("fear_and_greed", {})
        return {"skor": round(float(fg["score"])), "etiket": fg.get("rating"),
                "onceki_kapanis": fg.get("previous_close"), "kaynak": "CNN F&G"}
    except Exception:
        return None
