"""Step 1: enumerate EU/EEA-listed equities via the Yahoo Finance screener.

Writes one CSV row per listing (all exchanges, including foreign cross-listings);
domicile filtering and de-duplication happen later in build.py.
"""
import csv, json, sys, time
from pathlib import Path
import yfinance as yf
from yfinance import EquityQuery as EQ

OUT = Path(sys.argv[1])
REGIONS = ["fr", "de", "it", "es", "nl", "be", "pt", "at", "ie", "fi", "se", "dk",
           "no", "pl", "gr", "cz", "hu", "ee", "lt", "lv", "is", "ro"]
FIELDS = ["symbol", "shortName", "longName", "exchange", "fullExchangeName", "quoteType",
          "currency", "marketCap", "regularMarketPrice", "averageDailyVolume3Month",
          "averageDailyVolume10Day", "region", "market"]

rows = []
for r in REGIONS:
    offset, total = 0, None
    while total is None or offset < total:
        q = EQ("and", [EQ("eq", ["region", r]), EQ("gt", ["intradaymarketcap", 40_000_000])])
        for attempt in range(4):
            try:
                res = yf.screen(q, offset=offset, size=250, sortField="intradaymarketcap", sortAsc=False)
                break
            except Exception as e:  # rate limit / transient
                time.sleep(3 * (attempt + 1))
        else:
            print(f"{r}: giving up at offset {offset}", file=sys.stderr)
            break
        total = res.get("total", 0)
        quotes = res.get("quotes", [])
        for qd in quotes:
            row = {k: qd.get(k) for k in FIELDS}
            row["screen_region"] = r
            rows.append(row)
        if not quotes:
            break
        offset += len(quotes)
        time.sleep(0.4)
    print(f"{r}: {total} listings", file=sys.stderr)

with OUT.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS + ["screen_region"])
    w.writeheader()
    w.writerows(rows)
print(f"wrote {len(rows)} rows to {OUT}", file=sys.stderr)
