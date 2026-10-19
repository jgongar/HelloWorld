"""Approximate rebuild of the Hermès v16.4 run (inputs read off its summary; D&A,
minorities and pensions are guesses) and the same case under v16.5 rules.
Not a valuation — a check that the v16.5 rules move the answer the way the review argued."""
import copy, importlib.util, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("E", os.path.join(HERE, "..", "skills", "equity-dcf", "scripts", "dcf_engine.py"))
E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)

lease = 0.0238
g = [.03, .07, .08, .08, .08, .075, .07, .065, .06, .055]
m_rao = [.439, .440] + [.445] * 8
tax = [.33, .28] + [round(.28 - (.28 - .258) * k / 8, 4) for k in range(1, 9)]
v164 = {
    "company": "Hermès (approx.)", "ticker": "RMS", "currency": "EUR", "date": "2026-10-17",
    "share_price": 1337.5, "shares_outstanding": 104.74, "net_debt": -10700.0, "minorities": 30.0,
    "pension_deficit": 0.0, "lease_cost_pct_of_revenue": lease, "base_revenue": 16000.0,
    "wacc": 0.0914, "terminal_growth": 0.03, "ronic": 0.25, "tax_rate": .33, "tax_fade": tax,
    "da_pct": float(sys.argv[1]) if len(sys.argv) > 1 else 0.035, "capex_pct": 0.063, "dwc_pct": 0.20,
    "rev_growth": [{"year": i + 1, "rate": x} for i, x in enumerate(g)],
    "ebitda_margins": [{"year": i + 1, "margin": x + lease} for i, x in enumerate(m_rao)],
    "analysis_date": "2026-10-17", "fiscal_year_end_month": 12, "last_completed_fy": 2025,
    "sector": "Textiles, Apparel & Luxury Goods", "modelling_options": {"engine": "ebitda_native"},
}

o = E.run_dcf(copy.deepcopy(dict(v164, fade_stage="off")))
w = o["what_must_be_true"]
print(f"v16.4 rules: €{o['implied_price']} ({o['upside_pct']:+.1f}%) · TV {o['tv_pct_of_ev']}% · exit "
      f"{o['terminal_block']['implied_exit_ev_ebitda']}x · breakeven WACC {w['wacc']['market_implied']}% · "
      f"mkt Y3–Y10 CAGR {w['rev_cagr_y3_y10']['market_implied']}%")
print("  (published run: €1,094, TV 61.3%, exit 10.1x, breakeven 7.94%, mkt CAGR 11.0%)\n")

wr = E.wacc_capm_range(0.0342, 1.04, 0.042, erp_long_run=0.055, rf_normalised=0.025,
                       market_cap=1337.5 * 104.74, excess_cash=10700.0)
print(E.format_wacc_range(wr), "\n")
v165 = dict(copy.deepcopy(v164), wacc=wr["central"], wacc_range=wr["wacc_range"], cap_years=20)
o2 = E.run_dcf(copy.deepcopy(v165))
print(f"v16.5 rules: €{o2['implied_price']} ({o2['upside_pct']:+.1f}%) · fade stage {o2['fade_stage']['years']}y · "
      f"value beyond Y10 {o2['tv_pct_of_ev']}% · exit {o2['terminal_block']['implied_exit_ev_ebitda']}x")
print(E.format_what_must_be_true(o2["what_must_be_true"]))
wf = E.gap_waterfall(copy.deepcopy(v165), {"rev_growth": [.046, .077], "ebitda_margins": [.439 + lease, .440 + lease]})
print(E.format_gap_waterfall(wf, "EUR"))
rr = E.rating_robustness(copy.deepcopy(v165), "HIGH QUALITY")
print(rr["message"])
sc = E.run_scenarios(copy.deepcopy(v165), [
    {"name": "Bear", "role": "bear", "probability": .25, "root_cause": "Chinese demand reset", "moves": [{"lever": "growth_far", "delta": -.025}]},
    {"name": "Base", "role": "base", "probability": .50, "root_cause": "", "moves": []},
    {"name": "Bull", "role": "bull", "probability": .25, "root_cause": "historical compounding", "moves": [{"lever": "growth_far", "delta": .025}]},
])
print(E.format_scenarios(sc, "EUR"))
