"""Step 3: fetch per-company data from Yahoo Finance into a JSON cache (resumable).

argv: universe.csv cache_dir [threads]
Per symbol: quoteSummary (consensus, estimates, revisions, multiples, profile),
weekly price history (1y) and annual fundamentals time series (up to 5y).
"""
import csv, json, sys, time, threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from yfinance.data import YfData

universe, cache = sys.argv[1], Path(sys.argv[2])
threads = int(sys.argv[3]) if len(sys.argv) > 3 else 4
cache.mkdir(parents=True, exist_ok=True)
d = YfData()
lock = threading.Lock()
done = [0]

MODULES = ("price,summaryProfile,financialData,defaultKeyStatistics,summaryDetail,"
           "earningsTrend,recommendationTrend,upgradeDowngradeHistory,calendarEvents")
TS_TYPES = ",".join("annual" + t for t in [
    "TotalRevenue", "GrossProfit", "OperatingIncome", "EBIT", "EBITDA", "NetIncome",
    "OperatingCashFlow", "CapitalExpenditure", "FreeCashFlow", "TotalAssets",
    "StockholdersEquity", "TotalDebt", "CashAndCashEquivalents", "CurrentAssets",
    "CurrentLiabilities", "OrdinarySharesNumber", "InvestedCapital"])

def get(url, params):
    for attempt in range(5):
        try:
            return d.get_raw_json(url, params=params)
        except Exception as e:
            msg = str(e)
            if "404" in msg or "Not Found" in msg:
                return None
            time.sleep(2 ** attempt)
    return None

def fetch(sym):
    out = cache / f"{sym}.json"
    if out.exists():
        return
    rec = {"symbol": sym, "fetched": time.strftime("%Y-%m-%d")}
    j = get(f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{sym}",
            {"modules": MODULES, "formatted": "false", "lang": "en-US", "region": "US"})
    try:
        rec["qs"] = j["quoteSummary"]["result"][0]
    except Exception:
        rec["qs"] = None
    j = get(f"https://query2.finance.yahoo.com/v8/finance/chart/{sym}", {"range": "1y", "interval": "1wk"})
    try:
        r = j["chart"]["result"][0]
        rec["chart"] = {"t": r["timestamp"], "close": r["indicators"]["quote"][0]["close"]}
    except Exception:
        rec["chart"] = None
    now = int(time.time())
    j = get(f"https://query2.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{sym}",
            {"type": TS_TYPES, "period1": now - 6 * 365 * 86400, "period2": now})
    ts = {}
    try:
        for item in j["timeseries"]["result"]:
            key = item["meta"]["type"][0]
            vals = item.get(key) or []
            ts[key] = [(v["asOfDate"], v["reportedValue"]["raw"]) for v in vals if v and v.get("reportedValue")]
    except Exception:
        pass
    rec["ts"] = ts
    out.write_text(json.dumps(rec))
    with lock:
        done[0] += 1
        if done[0] % 100 == 0:
            print(f"{done[0]} fetched", file=sys.stderr, flush=True)
    time.sleep(0.25)

syms = [r["symbol"] for r in csv.DictReader(open(universe))]
with ThreadPoolExecutor(threads) as ex:
    list(ex.map(fetch, syms))
n_ok = sum(1 for s in syms if (cache / f"{s}.json").exists())
print(f"cache has {n_ok}/{len(syms)} symbols", file=sys.stderr)
