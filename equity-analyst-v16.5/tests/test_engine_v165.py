"""Regression + feature tests for dcf_engine v16.5.

Run:  python3 tests/test_engine_v165.py [path/to/v16.4/dcf_engine.py]
The optional v16.4 path enables the price-identity regression test.
"""
import copy, importlib.util, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "skills", "equity-dcf", "scripts", "dcf_engine.py")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


E = load(ENGINE, "engine_v165")
OLD = load(sys.argv[1], "engine_v164") if len(sys.argv) > 1 else None


def base_inputs(**kw):
    """Generic mid-cap, net cash, growing — no v16.5-only keys."""
    inp = {
        "company": "TestCo", "ticker": "TST", "currency": "EUR", "date": "2026-10-19",
        "share_price": 50.0, "shares_outstanding": 100.0,
        "net_debt": -300.0, "minorities": 20.0, "pension_deficit": 30.0,
        "lease_liabilities": 150.0, "lease_cost_pct_of_revenue": 0.02,
        "base_revenue": 2000.0, "wacc": 0.09, "terminal_growth": 0.025, "ronic": 0.15,
        "tax_rate": 0.25, "da_pct": 0.04, "capex_pct": 0.05, "dwc_pct": 0.12,
        "rev_growth": [{"year": i + 1, "rate": g} for i, g in enumerate([.05, .05, .045, .04, .04, .035, .035, .03, .03, .03])],
        "ebitda_margins": [{"year": i + 1, "margin": 0.22} for i in range(10)],
        "analysis_date": "2026-10-19", "fiscal_year_end_month": 12, "last_completed_fy": 2025,
        "sector": "Specialty Retail", "modelling_options": {"engine": "ebitda_native"},
    }
    inp.update(kw)
    return inp


def price(mod, inp, **kw):
    return mod.run_dcf(copy.deepcopy(inp), **kw)["implied_price"]


results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


# 1. Regression: v16.4 inputs (no new keys, growth ≥ 0) price identically.
if OLD:
    for label, inp in [("growing", base_inputs()),
                       ("ronic=None", base_inputs(ronic=None)),
                       ("tax fade", base_inputs(tax_fade=[.30, .29, .28, .27, .26, .25, .25, .25, .25, .25]))]:
        a, b = price(OLD, inp), price(E, inp)
        check(f"regression v16.4 == v16.5 [{label}]", abs(a - b) < 0.05, f"{a} vs {b}")

# 2. Asymmetric ΔNWC: declines release no cash by default; explicit dwc_pct_decline restores symmetry.
dec = base_inputs(rev_growth=[{"year": i + 1, "rate": g} for i, g in enumerate([-.25, -.10, .05, .05, .04, .04, .03, .03, .03, .03])])
p_new = price(E, dec)
p_sym = price(E, dict(copy.deepcopy(dec), dwc_pct_decline=dec["dwc_pct"]))
check("decline: default no WC release lowers value", p_new < p_sym, f"{p_new} < {p_sym}")
if OLD:
    check("decline: dwc_pct_decline=dwc_pct reproduces v16.4", abs(p_sym - price(OLD, dec)) < 0.05)

# 3. Fade stage: CAP 20 with RONIC > WACC adds value; RONIC = WACC ≈ value-neutral.
p0 = price(E, base_inputs())
p20 = price(E, base_inputs(cap_years=20))
check("fade stage adds value when RONIC > WACC", p20 > p0, f"{p0} → {p20}")
pn0 = price(E, base_inputs(ronic=0.09))
pn20 = price(E, base_inputs(ronic=0.09, cap_years=20))
check("fade stage ≈ value-neutral when RONIC = WACC", abs(pn20 / pn0 - 1) < 0.03, f"{pn0} → {pn20}")
check("fade_stage='off' disables", abs(price(E, base_inputs(cap_years=20, fade_stage="off")) - p0) < 1e-6)

# 4. Operating leverage: when the market is below the DCF, implied growth is less negative with fixed costs.
lo_px = base_inputs(share_price=25.0)
w_plain = E.run_dcf(copy.deepcopy(lo_px))["what_must_be_true"]["rev_cagr_y3_y10"]["market_implied"]
w_lev = E.run_dcf(copy.deepcopy(dict(lo_px, fixed_cost_share=0.5)))["what_must_be_true"]["rev_cagr_y3_y10"]["market_implied"]
check("operating leverage: market needs a smaller revenue fall", w_lev > w_plain, f"{w_plain}% → {w_lev}%")
check("operating leverage: base price unchanged", abs(price(E, dict(base_inputs(), fixed_cost_share=0.5)) - p0) < 1e-6)

# 5. other_claims: same claims in bridge and solvers.
oc = base_inputs(other_claims=[{"label": "Deferred consideration", "amount": 200.0}])
p_oc = price(E, oc)
check("other_claims reduce equity per share", abs((p0 - p_oc) - 2.0) < 0.01, f"{p0} − {p_oc}")
oc_at_dcf = dict(copy.deepcopy(oc), share_price=p_oc)
be = E.run_dcf(oc_at_dcf)["what_must_be_true"]["wacc"]["market_implied"]
check("breakeven WACC = model WACC when price = DCF (claims consistent)", abs(be - 9.0) < 0.05, f"{be}%")

# 6. Gap waterfall: additive, discount-rate step inside range, classification.
wf = E.gap_waterfall(base_inputs(share_price=p0 * 1.08, wacc_range={"low": 0.08, "high": 0.10, "basis": "test"}),
                     {"rev_growth": [0.05, 0.05], "ebitda_margins": [0.22, 0.22]})
total = sum(s["delta"] for s in wf["steps"])
check("waterfall steps add up to the gap", abs(total - wf["total_gap"]) < 0.05, f"{total:.2f} vs {wf['total_gap']}")
check("waterfall: gap closed inside WACC range → discount-rate", wf["gap_closed_within_wacc_range"] and wf["gap_mostly"] == "discount-rate",
      f"{wf['gap_mostly']} @ {wf['wacc_closing_gap_pct']}%")

# 7. Solver bound → N/M.
far = E.run_dcf(base_inputs(share_price=1.0))["what_must_be_true"]
check("growth solver at bound marked N/M", far["rev_cagr_y3_y10"].get("market_implied_nm") is True, far["rev_cagr_y3_y10"].get("note", ""))

# 8. Growth paid for.
roic_bad = {"avg_roic_incl_gw": 0.20, "incremental_roic": -0.10}
gpf = E.run_dcf(base_inputs(capex_pct=0.04, roic_data=roic_bad))["growth_paid_for"]
check("growth not paid for flagged when gate fired and capex = D&A", gpf["status"] == "GROWTH_NOT_PAID_FOR", gpf["status"])
gpf_ok = E.run_dcf(base_inputs(roic_data={"avg_roic_incl_gw": 0.30, "incremental_roic": 0.25}))["growth_paid_for"]
check("growth paid for OK with consistent history", gpf_ok["status"] == "OK", gpf_ok["message"])
gpf_acq = E.run_dcf(base_inputs(capex_pct=0.04, roic_data=roic_bad, acquisition_spend=[150.0] * 10))
check("acquisition spend lowers value and clears the flag",
      gpf_acq["implied_price"] < price(E, base_inputs(capex_pct=0.04)) and gpf_acq["growth_paid_for"]["status"] != "GROWTH_NOT_PAID_FOR",
      gpf_acq["growth_paid_for"]["message"])

# 9. Scenarios: bracket check, market-consistent scenario, bear floor.
inp9 = base_inputs(share_price=p0 * 0.6, fixed_cost_share=0.4)
scen = [
    {"name": "Bear", "role": "bear", "probability": 0.25, "root_cause": "demand reset", "moves": [{"lever": "growth_far", "delta": -0.02}]},
    {"name": "Base", "role": "base", "probability": 0.5, "root_cause": "", "moves": []},
    {"name": "Bull", "role": "bull", "probability": 0.25, "root_cause": "share gains", "moves": [{"lever": "growth_far", "delta": 0.02}]},
]
r9 = E.run_scenarios(inp9, scen, history={"worst_revenue_growth": -0.25, "worst_margin_change_bps": -500})
check("scenarios that miss the price are flagged", not r9["brackets_price"] and any("BRACKET" in f for f in r9["flags"]))
check("mild bear fails the worst-year floor", r9["bear_floor_check"] and not r9["bear_floor_check"]["passes"])
mc = E.build_market_consistent_scenario(inp9, [{"lever": "set_growth_years", "years": [1, 2], "rates": [-0.25, -0.05]},
                                               {"lever": "margin_tail", "delta": -0.03}])
check("market-consistent scenario reaches the price", mc["status"] == "OK", f"severity {mc.get('severity')}")
mc["probability"] = 0.2
scen2 = [dict(scen[0], probability=0.2), dict(scen[1], probability=0.4), dict(scen[2], probability=0.2), mc]
r9b = E.run_scenarios(inp9, scen2)
mc_row = next(r for r in r9b["scenarios"] if r["role"] == "market_consistent")
check("market-consistent row prices at market", abs(mc_row["price"] - inp9["share_price"]) < 0.1, f"{mc_row['price']}")
check("no bracket flag once market-consistent scenario is included", not any("BRACKET" in f for f in r9b["flags"]))

# 10. Rating robustness.
rr = E.rating_robustness(base_inputs(share_price=p0 * 1.12, wacc_range={"low": 0.08, "high": 0.10, "basis": "test"}), "HIGH QUALITY")
check("rating not robust across WACC range → HOLD", (not rr["robust"]) and rr["final_rating"] == "HOLD", rr["message"])
rr2 = E.rating_robustness(base_inputs(share_price=p0 * 0.5, wacc_range={"low": 0.085, "high": 0.095, "basis": "test"}), "STANDARD")
check("robust BUY stays BUY", rr2["robust"] and rr2["final_rating"] == "BUY", rr2["message"])

# 11. WACC helpers.
wr = E.wacc_capm_range(0.0342, 1.04, 0.042, erp_long_run=0.055, rf_normalised=0.0275, market_cap=140100, excess_cash=10700)
check("cash-adjusted operating beta > equity beta", wr["table"][0]["beta_operating"] > 1.04, str(wr["table"][0]["beta_operating"]))
check("central = spot Rf + implied ERP", abs(wr["central"] - (0.0342 + 1.04 * 140100 / 129400 * 0.042)) < 1e-4, f"{wr['central']:.4f}")
bq = E.beta_quality_check(0.51, adv_eur_m=0.3, beta_industry_relevered=0.85)
check("thin/low beta replaced", bq["beta_used"] == 0.85, bq["message"])
nc = E.net_cash_quality(137.0, 53.4, exclusions=[{"label": "Placements", "amount": 50.0}], interim_net_cash=20.0)
check("cash quality takes the lower interim figure", abs(nc["net_debt"] + 20.0) < 1e-9, " | ".join(nc["log"]))
check("fixed-cost share estimate", E.estimate_fixed_cost_share(1000, 100, 700, 20) is not None)

# 12. Gate cap.
gc = E.gate_cap_check(base_inputs(), anchor_margin=0.21, cap_margin=0.22)
check("gate cap binding reports anchor price", gc["binding"] and gc["price_at_anchor"] < gc["price_at_cap"], gc["message"])

# 13. Output formatter runs end to end.
import io, contextlib
out = E.run_dcf(base_inputs(cap_years=20, other_claims=[{"label": "Earn-out", "amount": 50}],
                            acquisition_spend=[20] * 10, wacc_range={"low": 0.08, "high": 0.10, "basis": "test"}))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    E.format_dcf_output(out, base_inputs())
check("format_dcf_output renders v16.5 blocks", "Fade stage" in buf.getvalue() and "Earn-out" in buf.getvalue() and "GROWTH PAID FOR" in buf.getvalue())

failed = [r for r in results if not r[1]]
print(f"\n{len(results) - len(failed)}/{len(results)} passed")
sys.exit(1 if failed else 0)
