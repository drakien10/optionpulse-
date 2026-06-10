# OptionPulse — Gunluk Piyasa Analiz Motoru

Portfoysuz v0: GEX rejimi + VIX vade yapisi + makro panel + sentiment.

## Kurulum (tek seferlik, ~15 dk)
1. GitHub'da yeni repo olustur (private olabilir), bu klasoru yukle.
2. https://fred.stlouisfed.org/docs/api/api_key.html adresinden ucretsiz FRED anahtari al.
3. Repo > Settings > Secrets and variables > Actions > New secret:
   `FRED_API_KEY` = anahtarin.
4. Actions sekmesinden `daily-report` > Run workflow ile ilk calistirmayi yap.
5. Rapor her sabah TSI 07:30'da `reports/index.html` olarak guncellenir
   (Settings > Pages acarsan URL'den okursun).

## Mimari
- `src/core/` — Black-Scholes, GEX (per-strike, gercek flip, max pain, walls),
  vade yapisi, rejim siniflandirici + guven skoru
- `src/fetchers/` — CBOE delayed (ucretsiz, anahtarsiz), FRED, CNN F&G
- `src/run_daily.py` — orkestrator; kaynak basina try/except, veri yoksa "dogrulanamadi"
- `tests/` — Hull ders kitabi BS dogrulamasi + GEX mantik testleri (10/10)

## GEX konvansiyonu
Dealer call'larda long, put'larda short gamma varsayimi (standart).
Flip noktasi kumulatif-OI kestirmesi DEGIL: her aday spotta gamma yeniden
hesaplanarak net GEX(S)=0 kokunden bulunur.

## Yol haritasi
F3: Claude API ile "Gunun Hikayesi" + senaryo agaci (Tetik/Hedef/Sebep/Iptal)
F4: React dashboard (GEX profil grafigi, VIX egri grafigi, sektor isi haritasi)
F5: Protect-lite (parametrik hedge paketleri)
