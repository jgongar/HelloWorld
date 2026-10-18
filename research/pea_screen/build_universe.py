"""Step 2: merge official exchange lists + Yahoo screener into one PEA candidate universe.

Inputs (argv): euronext.csv, Listed-companies.xlsx (Deutsche Boerse), listings.csv (Yahoo screener), out.csv
- Euronext + Deutsche Boerse lists carry ISINs -> domicile from ISIN prefix.
- Other exchanges come from the Yahoo screener; domicile is checked later from the company profile.
Then a batch quote pass keeps listings with market cap >= EUR 50m and >= EUR 100k traded per day.
"""
import csv, sys, time
import openpyxl
from yfinance.data import YfData

EU_EEA = set("AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE IS LI NO".split())
EURONEXT_SUFFIX = [("Paris", ".PA"), ("Amsterdam", ".AS"), ("Brussels", ".BR"), ("Lisbon", ".LS"),
                   ("Dublin", ".IR"), ("Milan", ".MI"), ("Oslo", ".OL")]
OTHER_EXCH = {"MCE", "VIE", "STO", "HEL", "CPH", "ICE", "TAL", "RIS", "LIT", "WSE", "ATH", "PRA", "BUD", "BVB"}
FORTUNEO_DIRECT = {".PA", ".AS", ".BR"}  # Euronext Paris/Amsterdam/Brussels (+ Xetra/Frankfurt at higher fees)
MIN_MCAP_EUR, MIN_ADV_EUR = 50e6, 100e3

euronext_csv, de_xlsx, screener_csv, out_csv = sys.argv[1:5]
cands = {}  # yahoo symbol -> dict

def add(sym, **kw):
    cands.setdefault(sym, {"symbol": sym}).update(kw)

# Euronext official list
with open(euronext_csv, encoding="utf-8-sig") as f:
    rows = list(csv.reader(f, delimiter=";"))
for r in rows[1:]:
    if len(r) < 4 or not r[1] or len(r[1]) != 12:
        continue
    name, isin, ticker, market = r[0], r[1], r[2], r[3]
    suffix = next((s for k, s in EURONEXT_SUFFIX if k in market), None)
    if not suffix or isin[:2] not in EU_EEA:
        continue
    add(ticker.replace(" ", "-") + suffix, name=name, isin=isin, venue=market, src="euronext")

# Deutsche Boerse listed companies (Prime, General, Scale, Basic Board)
wb = openpyxl.load_workbook(de_xlsx, read_only=True)
for sheet in ["Prime Standard", "General Standard", "Scale", "Basic Board"]:
    for row in wb[sheet].iter_rows(min_row=9, values_only=True):
        isin, sym, name = row[0], row[1], row[2]
        if not isin or not sym or not isinstance(isin, str) or len(isin) != 12:
            continue
        if isin[:2] not in EU_EEA:
            continue
        add(str(sym).strip() + ".DE", name=str(name).strip(), isin=isin, venue=f"Xetra/Frankfurt ({sheet})", src="deutsche_boerse")

# Yahoo screener for the remaining EU/EEA exchanges (domicile checked later)
german_lines = {}
with open(screener_csv) as f:
    for r in csv.DictReader(f):
        if r["exchange"] in OTHER_EXCH and r["quoteType"] == "EQUITY":
            add(r["symbol"], name=r["longName"] or r["shortName"], isin="", venue=r["fullExchangeName"], src="yahoo_screener")
        elif r["screen_region"] == "de":
            german_lines.setdefault((r["longName"] or r["shortName"] or "").lower().strip(), []).append(r["symbol"])

print(f"candidates before quote filter: {len(cands)}", file=sys.stderr)

d = YfData()
def get(url, params, attempts=5):
    for attempt in range(attempts):
        try:
            return d.get_raw_json(url, params=params)
        except Exception as e:
            time.sleep(2 * (attempt + 1))
    return None

fx = {"EUR": 1.0}
for cur in ["SEK", "DKK", "NOK", "PLN", "CZK", "HUF", "RON", "ISK", "USD", "GBP"]:
    j = get("https://query1.finance.yahoo.com/v7/finance/quote", {"symbols": f"EUR{cur}=X"})
    try:
        fx[cur] = j["quoteResponse"]["result"][0]["regularMarketPrice"]
    except Exception:
        print(f"fx missing {cur}", file=sys.stderr)
fx["GBp"] = fx.get("GBP", 0.85) * 100

syms = list(cands)
kept = []
for i in range(0, len(syms), 100):
    j = get("https://query1.finance.yahoo.com/v7/finance/quote", {"symbols": ",".join(syms[i:i + 100])})
    for q in (j or {}).get("quoteResponse", {}).get("result", []):
        c = cands.get(q["symbol"])
        if not c:
            continue
        rate = fx.get(q.get("currency"))
        if not rate:
            continue
        mcap = (q.get("marketCap") or 0) / rate
        price = q.get("regularMarketPrice") or 0
        adv = (q.get("averageDailyVolume3Month") or 0) * price / rate
        c.update(currency=q.get("currency"), price=price, mcap_eur=round(mcap), adv_eur=round(adv),
                 yahoo_name=q.get("longName") or q.get("shortName"))
    time.sleep(0.3)

# batch quotes silently drop some symbols: retry those one by one via the price module
missing = [c for c in cands.values() if "mcap_eur" not in c]
print(f"retrying {len(missing)} unquoted symbols individually", file=sys.stderr)
for c in missing:
    j = get(f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{c['symbol']}",
            {"modules": "price,summaryDetail", "formatted": "false"}, attempts=1)
    try:
        res = j["quoteSummary"]["result"][0]
        p, sd = res["price"], res.get("summaryDetail", {})
    except Exception:
        continue
    rate = fx.get(p.get("currency"))
    if not rate:
        continue
    price = p.get("regularMarketPrice") or 0
    vol = p.get("averageDailyVolume3Month") or sd.get("averageVolume") or 0
    c.update(currency=p.get("currency"), price=price, mcap_eur=round((p.get("marketCap") or sd.get("marketCap") or 0) / rate),
             adv_eur=round(vol * price / rate), yahoo_name=p.get("longName") or p.get("shortName"))
    time.sleep(0.1)

# de-duplicate companies listed on several venues (same ISIN): keep the most liquid line
by_key = {}
for c in cands.values():
    if "mcap_eur" not in c:
        continue
    key = c["isin"] or c["symbol"]
    by_key.setdefault(key, []).append(c)
for key, lines in by_key.items():
    lines.sort(key=lambda x: x["adv_eur"], reverse=True)
    best = dict(lines[0])
    best["all_lines"] = " ".join(l["symbol"] for l in lines)
    suffixes = {"." + l["symbol"].rsplit(".", 1)[-1] for l in lines}
    nm = (best.get("yahoo_name") or "").lower().strip()
    if suffixes & FORTUNEO_DIRECT:
        best["fortuneo"] = "direct (Euronext P/A/B)"
    elif ".DE" in suffixes:
        best["fortuneo"] = "Xetra/Frankfurt (higher fees)"
    elif nm and nm in german_lines:
        best["fortuneo"] = "German secondary line (" + " ".join(german_lines[nm][:3]) + ") - check liquidity"
    else:
        best["fortuneo"] = "not online"
    if best["mcap_eur"] >= MIN_MCAP_EUR and best["adv_eur"] >= MIN_ADV_EUR:
        kept.append(best)

cols = ["symbol", "name", "yahoo_name", "isin", "venue", "src", "currency", "price", "mcap_eur", "adv_eur", "fortuneo", "all_lines"]
with open(out_csv, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    w.writerows(sorted(kept, key=lambda x: -x["mcap_eur"]))
print(f"kept {len(kept)} companies (mcap>=50m, adv>=100k) out of {len(by_key)} quoted", file=sys.stderr)
