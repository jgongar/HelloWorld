"""Step 4: compute metrics and composite scores for the PEA universe.

argv: universe.csv cache_dir out_prefix
Writes <out_prefix>_all.csv (every company with metrics + scores).
Weights (agreed with user): revisions 25, upside 20, quality 20, growth 15, valuation vs sector 15, balance sheet 5.
Companies with < 2 analysts get a separate "uncovered" score: quality 35, valuation 35, growth 15, balance sheet 15.
"""
import csv, json, math, statistics, sys, time
from pathlib import Path
from yfinance.data import YfData

universe_csv, cache, out_prefix = sys.argv[1], Path(sys.argv[2]), sys.argv[3]

EU_EEA_NAMES = {"Germany", "France", "Italy", "Spain", "Netherlands", "Belgium", "Portugal", "Austria", "Ireland",
                "Finland", "Sweden", "Denmark", "Norway", "Poland", "Greece", "Czech Republic", "Czechia", "Hungary",
                "Estonia", "Lithuania", "Latvia", "Iceland", "Romania", "Luxembourg", "Cyprus", "Malta", "Slovenia",
                "Slovakia", "Croatia", "Bulgaria", "Liechtenstein"}
EXCLUDED_INDUSTRY_WORDS = ["Banks", "Insurance", "REIT", "Mortgage Finance", "Shell Companies", "Credit Services"]
THRESH = [(5e9, 0.15), (1e9, 0.25), (0, 0.35)]  # mcap floor -> min upside

d = YfData()
fx = {"EUR": 1.0}
for cur in ["SEK", "DKK", "NOK", "PLN", "CZK", "HUF", "RON", "ISK", "USD", "GBP", "CHF"]:
    try:
        fx[cur] = d.get_raw_json("https://query1.finance.yahoo.com/v7/finance/quote",
                                 params={"symbols": f"EUR{cur}=X"})["quoteResponse"]["result"][0]["regularMarketPrice"]
    except Exception:
        pass
    time.sleep(0.2)

def g(dct, *path):
    for p in path:
        if not isinstance(dct, dict):
            return None
        dct = dct.get(p)
    if isinstance(dct, dict) and "raw" in dct:
        dct = dct["raw"]
    return dct if isinstance(dct, (int, float)) and not (isinstance(dct, float) and math.isnan(dct)) else (dct if isinstance(dct, str) else None)

def chg(cur, ago):
    if cur is None or ago in (None, 0):
        return None
    return (cur - ago) / abs(ago)

def series(ts, key):
    vals = sorted(ts.get("annual" + key, []))
    return [v for _, v in vals]

def metrics(row, rec):
    qs = rec.get("qs") or {}
    fd, ks, sd, pr, sp = (qs.get(k) or {} for k in ["financialData", "defaultKeyStatistics", "summaryDetail", "price", "summaryProfile"])
    m = {k: row[k] for k in ["symbol", "name", "isin", "venue", "src", "fortuneo", "all_lines"]}
    m["country"] = sp.get("country")
    m["sector"] = sp.get("sector")
    m["industry"] = sp.get("industry")
    m["employees"] = sp.get("fullTimeEmployees")
    m["website"] = sp.get("website")
    m["summary"] = (sp.get("longBusinessSummary") or "")[:600]
    trade_cur = pr.get("currency") or row["currency"]
    fin_cur = fd.get("financialCurrency") or trade_cur
    r_trade, r_fin = fx.get(trade_cur), fx.get(fin_cur)
    price = g(fd, "currentPrice") or g(pr, "regularMarketPrice")
    mcap = g(pr, "marketCap") or g(sd, "marketCap")
    m["currency"] = trade_cur
    m["price"] = price
    m["mcap_eur"] = mcap / r_trade if mcap and r_trade else float(row["mcap_eur"])
    m["adv_eur"] = float(row["adv_eur"])
    # consensus
    m["n_analysts"] = g(fd, "numberOfAnalystOpinions") or 0
    m["target_mean"] = g(fd, "targetMeanPrice")
    m["target_median"] = g(fd, "targetMedianPrice")
    m["target_high"], m["target_low"] = g(fd, "targetHighPrice"), g(fd, "targetLowPrice")
    m["reco_mean"] = g(fd, "recommendationMean")
    m["upside"] = (m["target_mean"] / price - 1) if m["target_mean"] and price else None
    if m["upside"] is not None and not (-0.8 < m["upside"] < 3.0):
        m["data_flag"] = "upside outlier (check currency/stale target)"
    m["target_dispersion"] = ((m["target_high"] - m["target_low"]) / m["target_mean"]) if m["target_high"] and m["target_low"] and m["target_mean"] else None
    # estimates & revisions
    trend = {t.get("period"): t for t in (qs.get("earningsTrend") or {}).get("trend", [])}
    for per, tag in [("0y", "fy0"), ("+1y", "fy1")]:
        t = trend.get(per) or {}
        et = t.get("epsTrend") or {}
        cur = g(et, "current")
        m[f"eps_{tag}"] = cur
        m[f"rev30_{tag}"] = chg(cur, g(et, "30daysAgo"))
        m[f"rev90_{tag}"] = chg(cur, g(et, "90daysAgo"))
        er = t.get("epsRevisions") or {}
        m[f"up30_{tag}"] = g(er, "upLast30days")
        m[f"down30_{tag}"] = g(er, "downLast30days")
        m[f"eps_growth_{tag}"] = g(t, "growth")
        m[f"rev_growth_{tag}"] = g(t, "revenueEstimate", "growth")
    ups = (m["up30_fy0"] or 0) + (m["up30_fy1"] or 0)
    downs = (m["down30_fy0"] or 0) + (m["down30_fy1"] or 0)
    m["net_revisions_30d"] = (ups - downs) / max(ups + downs, 1) if (ups + downs) else None
    rt = (qs.get("recommendationTrend") or {}).get("trend", [])
    def buy_share(p):
        x = next((t for t in rt if t.get("period") == p), None)
        if not x:
            return None
        tot = sum(x.get(k, 0) for k in ["strongBuy", "buy", "hold", "sell", "strongSell"])
        return (x.get("strongBuy", 0) + x.get("buy", 0)) / tot if tot else None
    b0, b3 = buy_share("0m"), buy_share("-3m")
    m["buy_share"] = b0
    m["buy_share_chg_3m"] = (b0 - b3) if b0 is not None and b3 is not None else None
    # price-target actions in the last 120 days (where Yahoo has them)
    now = time.time()
    pt_up = pt_down = 0
    for h in (qs.get("upgradeDowngradeHistory") or {}).get("history", []):
        if now - (h.get("epochGradeDate") or 0) > 120 * 86400:
            continue
        cpt, ppt = h.get("currentPriceTarget"), h.get("priorPriceTarget")
        if cpt and ppt:
            pt_up += cpt > ppt
            pt_down += cpt < ppt
    m["pt_raises_120d"], m["pt_cuts_120d"] = pt_up, pt_down
    # valuation
    m["fwd_pe"] = g(ks, "forwardPE") or g(sd, "forwardPE")
    m["trailing_pe"] = g(sd, "trailingPE")
    m["ev_ebitda"] = g(ks, "enterpriseToEbitda")
    m["ev_sales"] = g(ks, "enterpriseToRevenue")
    m["p_book"] = g(ks, "priceToBook")
    m["div_yield"] = g(sd, "dividendYield")
    fcf = g(fd, "freeCashflow")
    mcap_fin = mcap * r_fin / r_trade if mcap and r_fin and r_trade else None
    m["fcf_yield"] = fcf / mcap_fin if fcf is not None and mcap_fin else None
    eg = m["eps_growth_fy1"]
    m["peg"] = m["fwd_pe"] / (eg * 100) if m["fwd_pe"] and m["fwd_pe"] > 0 and eg and eg > 0.02 else None
    # balance sheet
    cash, debt, ebitda = g(fd, "totalCash"), g(fd, "totalDebt"), g(fd, "ebitda")
    m["net_cash_to_mcap"] = (cash - debt) / mcap_fin if cash is not None and debt is not None and mcap_fin else None
    m["net_debt_ebitda"] = (debt - cash) / ebitda if cash is not None and debt is not None and ebitda and ebitda > 0 else None
    # quality & growth from annual statements
    ts = rec.get("ts") or {}
    rev, ebit, ni = series(ts, "TotalRevenue"), series(ts, "EBIT") or series(ts, "OperatingIncome"), series(ts, "NetIncome")
    ocf, fcf_s, eq = series(ts, "OperatingCashFlow"), series(ts, "FreeCashFlow"), series(ts, "StockholdersEquity")
    tdebt, tcash, ta = series(ts, "TotalDebt"), series(ts, "CashAndCashEquivalents"), series(ts, "TotalAssets")
    m["op_margin"] = g(fd, "operatingMargins")
    m["gross_margin"] = g(fd, "grossMargins")
    m["roe"] = g(fd, "returnOnEquity")
    m["roic"] = None
    if ebit and eq and tdebt and tcash:
        ic = eq[-1] + tdebt[-1] - tcash[-1]
        m["roic"] = ebit[-1] * 0.75 / ic if ic > 0 else None
    margins = [e / r for e, r in zip(ebit[-4:], rev[-4:]) if r]
    m["op_margin_std"] = statistics.pstdev(margins) if len(margins) >= 3 else None
    m["fcf_conversion"] = (sum(fcf_s[-3:]) / sum(ni[-3:])) if len(fcf_s) >= 3 and len(ni) >= 3 and sum(ni[-3:]) > 0 else None
    m["rev_cagr_3y"] = ((rev[-1] / rev[-4]) ** (1 / 3) - 1) if len(rev) >= 4 and rev[-4] > 0 and rev[-1] > 0 else None
    m["revenue_eur"] = rev[-1] / r_fin if rev and r_fin else None
    # simplified Piotroski (up to 7 points, needs 2 years)
    pts = None
    if len(ni) >= 2 and len(ta) >= 2 and len(ocf) >= 1:
        pts = 0
        roa1, roa0 = ni[-1] / ta[-1], ni[-2] / ta[-2]
        pts += roa1 > 0
        pts += ocf[-1] > 0
        pts += roa1 > roa0
        pts += ocf[-1] > ni[-1]
        if len(tdebt) >= 2:
            pts += tdebt[-1] / ta[-1] <= tdebt[-2] / ta[-2]
        if len(rev) >= 2 and len(margins) >= 2:
            pts += margins[-1] >= margins[-2]
            pts += rev[-1] / ta[-1] >= rev[-2] / ta[-2]
    m["piotroski7"] = pts
    # price momentum
    ch = rec.get("chart") or {}
    closes = [c for c in (ch.get("close") or []) if c]
    if len(closes) >= 30:
        m["ret_13w"] = closes[-1] / closes[-14] - 1
        m["ret_26w"] = closes[-1] / closes[-27] - 1
        m["ret_52w"] = closes[-1] / closes[0] - 1
        m["drawdown_52w"] = closes[-1] / max(closes) - 1
    m["divergence"] = 1 if (m.get("rev90_fy1") or 0) > 0.02 and (m.get("ret_13w") or 0) < -0.05 else 0
    return m

rows = list(csv.DictReader(open(universe_csv)))
data = []
for row in rows:
    f = cache / f"{row['symbol']}.json"
    if not f.exists():
        continue
    rec = json.loads(f.read_text())
    m = metrics(row, rec)
    excluded = []
    if row["src"] == "yahoo_screener" and m["country"] not in EU_EEA_NAMES:
        excluded.append("non-EU/EEA domicile")
    ind = m["industry"] or ""
    if any(w in ind for w in EXCLUDED_INDUSTRY_WORDS) or m["sector"] == "Real Estate" and "Services" not in ind:
        excluded.append("financial/REIT excluded")
    if "Biotechnology" in ind and (m["revenue_eur"] or 0) < 20e6:
        excluded.append("pre-revenue biotech")
    m["excluded"] = "; ".join(excluded)
    data.append(m)

# the same company can appear via several venues (e.g. SAP.DE and SAP.VI): keep one line per company
def company_key(m):
    w = (m.get("website") or "").lower().replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
    if w:
        return "w:" + w.split("/")[0]
    n = (m.get("name") or "").lower()
    for junk in [" se", " ag", " sa", " s.a.", " nv", " n.v.", " spa", " s.p.a.", " ab", " asa", " oyj", " a/s", " plc", " publ", "(publ)"]:
        n = n.replace(junk, "")
    return "n:" + "".join(ch for ch in n if ch.isalnum())[:20] + "|" + (m.get("country") or "")
ACCESS_RANK = {"direct": 0, "Xetra/Frankfurt": 1, "German secondary line": 2, "not online": 3}
groups = {}
for m in data:
    groups.setdefault(company_key(m), []).append(m)
deduped = []
for lines in groups.values():
    lines.sort(key=lambda m: (-(m["n_analysts"] or 0), m["src"] == "yahoo_screener", -m["adv_eur"]))
    best = lines[0]
    if len(lines) > 1:
        best["all_lines"] = " ".join(sorted({s for l in lines for s in (l["all_lines"] or l["symbol"]).split()}))
        best["fortuneo"] = min((l["fortuneo"] for l in lines), key=lambda a: ACCESS_RANK.get(a.split(" (")[0], 9))
    deduped.append(best)
print(f"de-duplicated {len(data)} lines into {len(deduped)} companies", file=sys.stderr)
data = deduped

def pct_rank(vals, higher_better=True):
    xs = sorted(v for v in vals if v is not None)
    out = []
    for v in vals:
        if v is None or not xs:
            out.append(None)
            continue
        lo = sum(1 for x in xs if x < v)
        eq = sum(1 for x in xs if x == v)
        p = (lo + 0.5 * eq) / len(xs)
        out.append(p if higher_better else 1 - p)
    return out

active = [m for m in data if not m["excluded"]]
def add_rank(name, key, higher=True, by_sector=False, transform=None):
    groups = {}
    for m in active:
        groups.setdefault(m["sector"] if by_sector else "all", []).append(m)
    for grp in groups.values():
        vals = [transform(m) if transform else m.get(key) for m in grp]
        for m, p in zip(grp, pct_rank(vals, higher)):
            m["r_" + name] = p

pos = lambda k: (lambda m: m.get(k) if (m.get(k) or 0) > 0 else None)
add_rank("upside", "upside")
add_rank("rev90_fy1", "rev90_fy1"); add_rank("rev30_fy1", "rev30_fy1"); add_rank("rev90_fy0", "rev90_fy0")
add_rank("netrev", "net_revisions_30d"); add_rank("buychg", "buy_share_chg_3m")
add_rank("pe", None, False, True, pos("fwd_pe")); add_rank("evebitda", None, False, True, pos("ev_ebitda"))
add_rank("fcfy", "fcf_yield", True, True); add_rank("peg", None, False, True, pos("peg"))
add_rank("roic", "roic"); add_rank("opm", "op_margin", True, True); add_rank("opm_std", "op_margin_std", False)
add_rank("fcfconv", None, True, False, lambda m: min(m["fcf_conversion"], 2) if m.get("fcf_conversion") is not None else None)
add_rank("piotroski", "piotroski7")
add_rank("revg1", "rev_growth_fy1"); add_rank("epsg1", "eps_growth_fy1"); add_rank("cagr3", "rev_cagr_3y")
add_rank("netcash", "net_cash_to_mcap"); add_rank("nde", "net_debt_ebitda", False)

def avg(m, keys):
    v = [m.get("r_" + k) for k in keys if m.get("r_" + k) is not None]
    return sum(v) / len(v) if v else None

PILLARS = {
    "revisions": ["rev90_fy1", "rev30_fy1", "rev90_fy0", "netrev", "buychg"],
    "upside": ["upside"],
    "quality": ["roic", "opm", "opm_std", "fcfconv", "piotroski"],
    "growth": ["revg1", "epsg1", "cagr3"],
    "valuation": ["pe", "evebitda", "fcfy", "peg"],
    "balance": ["netcash", "nde"],
}
W_COV = {"revisions": .25, "upside": .20, "quality": .20, "growth": .15, "valuation": .15, "balance": .05}
W_UNC = {"quality": .35, "valuation": .35, "growth": .15, "balance": .15}
for m in data:
    for p, keys in PILLARS.items():
        m["p_" + p] = avg(m, keys) if not m["excluded"] else None
    covered = m["n_analysts"] >= 2
    w = W_COV if covered else W_UNC
    num = sum(w[p] * m["p_" + p] for p in w if m["p_" + p] is not None)
    den = sum(w[p] for p in w if m["p_" + p] is not None)
    m["score"] = round(100 * num / den, 1) if den >= 0.5 and not m["excluded"] else None
    m["coverage"] = "covered" if covered else "uncovered"
    thr = next(t for floor, t in THRESH if m["mcap_eur"] >= floor)
    m["size"] = "L" if m["mcap_eur"] >= 5e9 else "M" if m["mcap_eur"] >= 1e9 else "S"
    m["min_upside"] = thr
    m["passes_threshold"] = bool(covered and m["upside"] is not None and m["upside"] >= thr and not m.get("data_flag"))

cols = list(data[0].keys())
for m in data:
    for k in m:
        if k not in cols:
            cols.append(k)
data.sort(key=lambda m: (m["score"] is None, -(m["score"] or 0)))
with open(out_prefix + "_all.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for m in data:
        w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()})
n_pass = sum(m["passes_threshold"] for m in data)
print(f"scored {len(data)} companies; excluded {sum(1 for m in data if m['excluded'])}; "
      f"covered {sum(1 for m in data if m['coverage']=='covered')}; passing upside threshold {n_pass}", file=sys.stderr)
