#!/usr/bin/env python3
"""
DCF Computation Template — {Company} ({Ticker})
Engine: v16.5
Generated: {date}

INSTRUCTIONS FOR LLM:
1. Copy this template into a new script
2. Fill in ALL values in the INPUTS dict from Steps 1–8
3. Every value must have a source comment
4. Populate `net_interest_position_fy0` per R8 (signed!)
5. Populate `non_core_holdings` per R9 (list, possibly empty)
6. Execute with bash_tool
7. Present stdout verbatim
"""
import json, sys, os, shutil
from datetime import datetime

# ══════════════════════════════════════════════════
# INPUTS — fill in every value with source label
# ══════════════════════════════════════════════════
INPUTS = {
    "company": "{Company Name}",
    "ticker": "{TICKER}",
    "currency": "{CCY}",
    "date": "{ISO date}",
    "share_price": 0.00,          # [market, {date}]
    "shares_outstanding": 0.0,    # millions [filing]

    # ⛔ R9: net_debt is OPERATING ONLY (excl. captive/sub debt). See `references/non_core_holdings.md`.
    "net_debt": 0.0,              # millions [filing] (negative = net cash)
    # v15.1 — required when R9 active. "operating_only" if analyst already pre-stripped,
    # "group_consolidated" if engine should strip captive debt.
    "net_debt_basis": "operating_only",   # operating_only | group_consolidated
    "minorities": 0.0,            # millions [filing]
    "pension_deficit": 0.0,       # millions [filing] (0 if N/A)
    # v16.5 — net_debt from net_cash_quality(): liquid, free cash only; LATEST balance sheet (interim if newer)
    "other_claims": [],           # v16.5 [{"label": "...", "amount": 0.0}] — deferred consideration, puts on minorities,
                                  #   capitalised losses of a loss-making arm, book deficits. Same claims in bridge AND solvers.
    "lease_liabilities": 0.0,     # millions [filing] MEMO ONLY (v16.4: NOT deducted in bridge — rent-as-opex)
    "lease_cost_pct_of_revenue": 0.0,   # (lease principal + lease interest paid) / revenue, 3Y pooled [filing, CF statement]. Engine subtracts from every EBITDA margin. 0 if margins already rent-inclusive.
    "base_revenue": 0.0,          # FY0 revenue, OPERATING ONLY per R9, millions [filing]
    "wacc": 0.00,                 # decimal — wacc_capm_range(...)["central"] (spot Rf + implied ERP) [computed]
    "wacc_range": {"low": 0.00, "high": 0.00, "basis": ""},   # v16.5 wacc_capm_range(...)["wacc_range"]
    "terminal_growth": 0.02,      # decimal — long-run nominal growth proxy (Step 4). Value created by tg depends on RONIC > WACC, not on tg itself.
    "ronic": None,                # decimal — terminal return on new invested capital (Step 5 CAP rule). None → WACC (growth value-neutral). RONIC gate forces WACC if pooled 3Y incremental ROIC < WACC.
    # "ronic_override_justification": "",   # set to keep RONIC > WACC despite the gate
    "cap_years": 10,              # v16.5 Step 5 CAP; > 10 → fade stage Y11..Y(CAP) (Rule 3D)
    "tax_rate": 0.00,             # decimal, 3Y avg effective [computed]
    "da_pct": 0.00,               # D&A as % of revenue, 3Y avg [computed]
    "capex_pct": 0.00,            # Capex as % of revenue, 3Y avg [computed]
    "dwc_pct": 0.00,              # ΔWC as % of ΔRevenue, 3Y avg [computed]
    # "dwc_pct_decline": 0.0,     # v16.5 only with evidence from the company's own downturn (default min(dwc_pct, 0))
    "acquisition_spend": [0.0] * 10,   # v16.5 Rule 3E — cash for the acquisitions inside rev_growth (millions/yr)
    # "growth_funding_justification": "",   # v16.5 only if GROWTH_NOT_PAID_FOR is wrong — say why

    # Revenue growth Y1–Y10 — OPERATING ONLY per R9
    "rev_growth": [
        {"year": 1, "rate": 0.00, "source": "[P?]", "note": ""},
        {"year": 2, "rate": 0.00, "source": "[P?]", "note": ""},
        {"year": 3, "rate": 0.00, "source": "[P?]", "note": ""},
        {"year": 4, "rate": 0.00, "source": "[P?]", "note": ""},
        {"year": 5, "rate": 0.00, "source": "[P?]", "note": ""},
        {"year": 6, "rate": 0.00, "source": "[P?]", "note": ""},
        {"year": 7, "rate": 0.00, "source": "[P?]", "note": ""},
        {"year": 8, "rate": 0.00, "source": "[P?]", "note": ""},
        {"year": 9, "rate": 0.00, "source": "[P?]", "note": ""},
        {"year": 10, "rate": 0.00, "source": "[P?]", "note": ""},
    ],

    # EBITDA margins Y1–Y10 (normalised, per Rule 3) — OPERATING ONLY per R9
    "ebitda_margins": [
        {"year": 1, "margin": 0.00, "source": "[M?]", "note": ""},
        {"year": 2, "margin": 0.00, "source": "[M?]", "note": ""},
        {"year": 3, "margin": 0.00, "source": "[M?]", "note": ""},
        {"year": 4, "margin": 0.00, "source": "[M?]", "note": ""},
        {"year": 5, "margin": 0.00, "source": "[M?]", "note": ""},
        {"year": 6, "margin": 0.00, "source": "[M?]", "note": ""},
        {"year": 7, "margin": 0.00, "source": "[M?]", "note": ""},
        {"year": 8, "margin": 0.00, "source": "[M?]", "note": ""},
        {"year": 9, "margin": 0.00, "source": "[M?]", "note": ""},
        {"year": 10, "margin": 0.00, "source": "[M?]", "note": ""},
    ],

    # Metadata
    "wacc_source": "[sector-adj]",
    "margin_type": "normalised_EBITDA",
    "base_revenue_fy": "FY{year}",
    "reported_fcf_fy0": 0.0,  # PARENT reported FCF, includes dividends-received from non-core [filing]
    # v15.2 — SAME-PERIOD bridge target. Provide ONE of:
    #   "ufcf_fy0": <number>           # analyst-computed FY0 UFCF, OR
    #   "fy0_actuals": {...}           # engine derives UFCF_FY0 from FY0 actuals
    # If neither is supplied, the bridge falls back to Y1 and the residual + R8
    # sign gates become ADVISORY (non-binding) because of FY0->Y1 growth contamination.
    "fy0_actuals": {
        "ebitda": 0.0,      # FY0 normalised EBITDA (operating only if R9) [filing]
        "da":     0.0,      # FY0 D&A (per Rule 3B) [filing]
        "capex":  0.0,      # FY0 capex [filing]
        "dnwc":   0.0,      # FY0 ΔNWC (positive = drag) [computed]
        "tax_rate": 0.0,    # FY0 effective tax (defaults to inputs['tax_rate'])
        "lease_cash_cost": 0.0,   # FY0 lease principal + interest paid — engine subtracts (rent-as-opex)
        "sbc": 0.0,               # FY0 SBC — subtracted only when option sbc == cash_cost
    },
    "net_debt_components": {
        "financial_debt": 0.0,
        "cash": 0.0,
        "pension_deficit": 0.0,
        "lease_liabilities": 0.0,
    },

    # ══════════════════════════════════════════════════
    # v16.4 — RONIC GATE WIRING
    # Compute BEFORE the DCF run:
    #   roic_data = dcf_engine.compute_roic_history(financials_5y, tax_rate, wacc)
    # with financials_5y keyed "FY-4".."FY0", each FY:
    #   {ebit, total_debt, total_equity, cash, goodwill[, lease_interest]}
    # IC is EX-leases; NOPAT = (EBIT − lease_interest)(1−t)  (rent-as-opex basis).
    # The gate statistic is the POOLED 3Y incremental ROIC (not per-year).
    # ══════════════════════════════════════════════════
    "roic_data": None,                              # ← set to compute_roic_history(...) output
    # v16.4 — optional consensus drivers for the WHAT-MUST-BE-TRUE consensus column
    # "consensus_drivers": {"rev_cagr_y3_y10": 5.0, "terminal_margin": 24.0},   # in %

    # ══════════════════════════════════════════════════
    # v14 — calendar-aware discounting
    # ══════════════════════════════════════════════════
    "analysis_date": "2026-MM-DD",
    "fiscal_year_end_month": 12,
    "last_completed_fy": 2025,
    "sector": "{GICS sector}",
    "sub_industry": "{GICS sub-industry}",
    # v16.5 operating leverage (cyclicals; any name whose bear moves revenue)
    # "fixed_cost_share": 0.0,            # estimate_fixed_cost_share(rev_a, ebitda_a, rev_b, ebitda_b) on the worst year
    # "fixed_cost_adjustment_years": 3,   # years for fixed costs to catch up with a new revenue path

    # v14 — Modelling options (set by modelling-options skill, Step 6.5)
    # v16.4 — FOUR options (set by resolve_modelling_options, Step 6.5); constants recorded alongside
    "modelling_options": {
        "engine": "ebitda_native",          # ebitda_native | nopat_native
        "sbc": "non_cash_addback",          # non_cash_addback | cash_cost  (cash_cost → set sbc_pct_of_revenue)
        "nwc_scope": "trade_only",          # trade_only | extended
        "non_core_treatment": "n_a",        # dividend_only when R9 fires
        "lease_convention": "rent_as_opex", # constant
        "mid_year": "on",                   # constant
        "triggers_at_run_time": [],
        "user_overrides": [],
    },
    # "sbc_pct_of_revenue": 0.0,          # required if sbc == cash_cost

    # v14 — Consensus snapshot
    "consensus_snapshot": {
        "as_of_date": "{date}",
        "source": "{Zonebourse|MarketScreener|...}",
        "analyst_count": 0,
        "revenue": {"Y1": 0.0, "Y2": 0.0},
        "ebitda": {"Y1": 0.0, "Y2": 0.0},
        "ufcf": {"Y1": None, "Y2": None},
        "eps": {"Y1": 0.0, "Y2": 0.0},
        "target_price_12m": {"value": 0.0, "high": 0.0, "low": 0.0},
    },

    # v14 — Derivation metadata (R7)
    "derivations": {
        "da_pct": {
            "formula": "sum(da_FY-2..FY0) / sum(revenue_FY-2..FY0)",
            "inputs_used": {},
            "period": "FY-2..FY0",
            "exclusions": [],
        },
        "capex_pct": {
            "formula": "sum(capex_FY-2..FY0) / sum(revenue_FY-2..FY0)",
            "inputs_used": {},
            "period": "FY-2..FY0",
            "exclusions": [],
        },
    },

    # ══════════════════════════════════════════════════
    # v15.1 — R8 SIGN-AWARE UFCF UNLEVERING (BINDING)
    # ══════════════════════════════════════════════════
    # interest_expense and interest_income are gross POSITIVE values from P&L.
    # `net` is SIGNED: positive = net debt (interest expense dominates), negative = net cash.
    # v16.4: ADVISORY — a direction mismatch is flagged, never halts.
    "net_interest_position_fy0": {
        "interest_expense": 0.0,    # gross, positive [filing]
        "interest_income":  0.0,    # gross, positive [filing]
        "net":              0.0,    # = expense - income; SIGNED
        "tax_rate_applied": 0.28,
        "atx_net":          0.0,    # = net * (1 - tax_rate); SIGNED
        "bridge_direction": "...",  # "UFCF > FCF" (net debt) OR "UFCF < FCF" (net cash)
    },

    # FCF bridge line items (used by build_fcf_bridge). Interest unlevering comes from net_interest_position_fy0 (R8).
    # v16.4: SIGNED lease line — NEGATIVE (−principal −interest) when the reported FCF definition
    # excludes lease payments (post-IFRS16 "OCF − capex"), so reported FCF becomes rent-inclusive like model UFCF.
    "lease_cash_adjustment_fy0": 0.0,
    # Optional:
    # "restructuring_cash_fy0": 0.0,
    # "pension_topup_fy0": 0.0,
    # "acquisition_cash_in_fcf_fy0": 0.0,
    # "capitalised_rd_fy0": 0.0,
    # "contract_wc_fy0": 0.0,
    # "sbc_fy0": 0.0,
    # "other_reconcile_fy0": 0.0,

    # ══════════════════════════════════════════════════
    # v15.1 — R9 NON-CORE HOLDINGS (BINDING when triggered)
    # ══════════════════════════════════════════════════
    # See `references/non_core_holdings.md` for full schema, treatment matrix,
    # worked examples (Renault/Mobilize, Dassault/Thales, Exor, Stellantis).
    #
    # Trigger any of:
    #   - Captive finance arm with segment OI >= 10% of group OI
    #   - Equity-method stake with carrying value >= 10% mcap OR >= 10% NI
    #   - FVOCI/FVTPL stake with fair value >= 10% mcap
    #   - Holding co with separately listed subs
    #
    # Treatment: strip operating figures, exclude captive debt from EV bridge,
    #            value as PV of actual dividend stream (cap 2% growth, terminal flat).
    #            NEVER add book/FV to bridge.
    "non_core_holdings": [
        # Example entry (Renault/Mobilize):
        # {
        #     "name": "Mobilize Financial Services",
        #     "ticker": None,
        #     "type": "captive_finance",   # captive_finance | equity_method | fvoci | fvtpl | listed_subsidiary
        #     "ownership_pct": 1.00,
        #     "treatment": "dividend_only",
        #     "rationale": "Captive finance arm; debt is operating raw material",
        #     "fy0_revenue":       6400.0,
        #     "fy0_ebitda":        1500.0,
        #     "fy0_da":             400.0,
        #     "fy0_capex":         3500.0,   # receivables build
        #     "fy0_dwc":              0.0,
        #     "fy0_dividend_paid":  300.0,
        #     "fy0_book_equity":   3200.0,
        #     "fy0_market_value":  None,
        #     "dividend_growth":   0.02,
        #     "discount_rate":     0.090,
        #     "horizon_years":     10,
        #     "balance_sheet_debt_to_exclude": 60000.0,
        #     "balance_sheet_cash_in_captive":  2000.0,
        #     "monetization_overlay": {
        #         "active":              False,
        #         "probability":         0.0,
        #         "fair_value":          0.0,
        #         "friction_discount":   0.20,
        #         "timeline_months":     24,
        #         "catalyst":            "",
        #     },
        # },
    ],

    # v14 — Optional advanced flags
    # "tax_fade": [t1, t2, ..., t10],
    # "terminal_wacc": 0.085,
}

# ══════════════════════════════════════════════════
# COPY ENGINE MODULE (first run)
# ══════════════════════════════════════════════════
ENGINE_DEST = "/home/claude/dcf_engine.py"
ENGINE_SRC = "/mnt/skills/user/equity-dcf/scripts/dcf_engine.py"

if not os.path.exists(ENGINE_DEST):
    if os.path.exists(ENGINE_SRC):
        shutil.copy2(ENGINE_SRC, ENGINE_DEST)
        print(f"  Engine copied from skill: {ENGINE_SRC}")
    else:
        print(f"  ⚠ Engine source not found at {ENGINE_SRC}")
        sys.exit(1)

FIN_DATA_PATH = "/home/claude/financial_data.json"
if os.path.exists(FIN_DATA_PATH):
    with open(FIN_DATA_PATH) as f:
        fin_data = json.load(f)
    print(f"  financial_data.json loaded ({len(fin_data.get('fiscal_years', {}))} years)")
    validation = fin_data.get("validation", {})
    for k, v in validation.items():
        if k != "yfinance_errors" and "FAIL" in str(v):
            print(f"  ⚠ DATA VALIDATION: {v}")
else:
    print(f"  Note: No financial_data.json found. Using manually populated INPUTS.")

sys.path.insert(0, "/home/claude")
from dcf_engine import run_dcf, format_dcf_output

if __name__ == "__main__":
    try:
        output = run_dcf(INPUTS)
    except Exception as e:
        print(f"\n⛔ DCF COMPUTATION FAILED: {e}")
        print(f"   Saving inputs-only state file for inspection.")
        partial = {
            "inputs": INPUTS,
            "error": str(e),
            "computation_timestamp": datetime.now().isoformat()
        }
        with open("/home/claude/dcf_state.json", "w") as f:
            json.dump(partial, f, indent=2)
        sys.exit(1)

    if output.get("status") == "WRONG_ENGINE":
        print(f"\n⛔ {output['reason']}")
        print(f"   This company requires the equity-financials skill, not equity-dcf.")
        sys.exit(2)

    try:
        from dcf_engine import build_fcf_bridge
        bridge = build_fcf_bridge(output, INPUTS)
        output["fcf_bridge"] = bridge
        if bridge.get("residual_ok") is False:
            print(f"\n⚠ FCF BRIDGE DOES NOT BALANCE")
            print(f"   Residual: {bridge['residual_pct_of_reported']:.1%} of reported FCF (tolerance: 10%)")
            print(f"   Reported FCF FY0: {bridge['reported_fcf_fy0']:,.0f}")
            print(f"   Investigate: ΔNWC sign, D&A double-count, capex timing,")
            print(f"                non-recurring items in operating_cf, JV equity income,")
            print(f"                R8 sign-aware unlevering, R9 non-core dividend strip.")
    except Exception as bridge_err:
        print(f"\n  (FCF bridge skipped: {bridge_err})")

    # v15.1: R9 validation
    if INPUTS.get("non_core_holdings"):
        try:
            from dcf_engine import validate_non_core_no_double_count
            dc_check = validate_non_core_no_double_count(output)
            if not dc_check.get("ok"):
                print(f"\n⛔ R9 VIOLATION — double-count detected: {dc_check.get('detail')}")
        except Exception as e:
            print(f"\n  (R9 double-count check skipped: {e})")

    state_path = "/home/claude/dcf_state.json"
    with open(state_path, "w") as f:
        json.dump(output, f, indent=2)

    format_dcf_output(output, INPUTS)

    print(f"\n  State saved to: {state_path}")
    print(f"  Engine at: {ENGINE_DEST}")

    # ══════════════════════════════════════════════════
    # v16.5 — Step 7 add-ons (run in the same script or a follow-up one)
    # ══════════════════════════════════════════════════
    # from dcf_engine import (gap_waterfall, format_gap_waterfall, run_scenarios, format_scenarios,
    #                         build_market_consistent_scenario, rating_robustness)
    # wf = gap_waterfall(INPUTS, {"rev_growth": [c1, c2], "ebitda_margins": [m1, m2]}); print(format_gap_waterfall(wf, INPUTS["currency"]))
    # SCENARIOS = [   # probabilities printed BEFORE this call (probability lock)
    #   {"name": "Bear", "role": "bear", "probability": 0.25, "root_cause": "...",
    #    "moves": [{"lever": "set_growth_years", "years": [1, 2], "rates": [-0.30, -0.10]}, {"lever": "wacc", "delta": 0.005}]},
    #   {"name": "Base", "role": "base", "probability": 0.50, "root_cause": "", "moves": []},
    #   {"name": "Bull", "role": "bull", "probability": 0.25, "root_cause": "...", "moves": [{"lever": "growth_far", "delta": 0.02}]},
    # ]
    # res = run_scenarios(INPUTS, SCENARIOS, history={"worst_revenue_growth": -0.29, "worst_margin_change_bps": -500})
    # print(format_scenarios(res, INPUTS["currency"]))
    # if not res["brackets_price"]:   # ⛔ build the market-consistent scenario, give it a probability, re-run
    #     mc = build_market_consistent_scenario(INPUTS, [{"lever": "growth_far", "delta": -0.03}, {"lever": "margin_tail", "delta": -0.02}])
    # rr = rating_robustness(INPUTS, "HIGH QUALITY"); print(rr["message"])
