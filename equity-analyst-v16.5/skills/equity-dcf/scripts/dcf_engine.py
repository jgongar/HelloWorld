"""
DCF Engine — shared computation module (v16.5).

v16.5 CHANGES (behavioural where noted; v16.4 inputs run unchanged):
- FADE STAGE: when `cap_years` > 10 the kernel projects Y11..Y(CAP) on a
  NOPAT basis with growth fading linearly from Y10 growth to tg, reinvesting
  g/RONIC, then applies the value-driver TV at Y(CAP). Removes the Y10 growth
  cliff for long-CAP names. `fade_stage="off"` disables.  [behavioural]
- ASYMMETRIC ΔNWC: revenue declines use `dwc_pct_decline` (default
  min(dwc_pct, 0) — no working-capital release without evidence from the
  company's own downturns).  [behavioural, decline years only]
- OPERATING LEVERAGE: optional `fixed_cost_share`; growth solvers and
  scenarios that move revenue off the model path re-price margins through the
  fixed-cost share instead of holding margins fixed. Fixed costs catch up with
  the new revenue path over `fixed_cost_adjustment_years` (default 3).
- `acquisition_spend` (list or % of revenue) is a cash outflow in UFCF;
  `check_growth_paid_for()` compares the implied return on explicit-period
  reinvestment with history (⛔ when the RONIC gate fired).
- `other_claims` enter the equity bridge AND the market EV used by every
  solver (one claims definition everywhere).
- what_must_be_true: market-implied Y3–Y10 CAGR also at the ends of
  `wacc_range`; solver results at a bound or implausible are marked N/M.
- gap_waterfall: separate discount-rate step (WACC moved inside `wacc_range`)
  before the long-term residual; returns `gap_mostly`.
- NEW helpers: wacc_capm_range, cash_adjusted_beta, blume_adjusted_beta,
  relever_beta, beta_quality_check, net_cash_quality, estimate_fixed_cost_share,
  run_scenarios / build_market_consistent_scenario / bear_floor_check,
  rating_for_upside / rating_robustness, gate_cap_check.

v16.4 CHANGES (breaking where noted):
- SINGLE LEASE CONVENTION: rent-as-opex. `lease_cost_pct_of_revenue` (total
  lease cash payments ÷ revenue, principal + interest) is subtracted from every
  projected EBITDA margin inside the engine, and `lease_liabilities` is NO LONGER
  deducted in the equity bridge (memo only). Removes the v16.1 double count
  (margin haircut + liability deduction) and the unpriced-renewal problem of the
  IFRS16-as-debt convention. Modelling Option 3 removed.  [breaking]
- VALUE-DRIVER TERMINAL VALUE: TV = NOPAT_11 × (1 − tg/RONIC) / (WACC − tg).
  Terminal reinvestment is derived from tg and RONIC instead of a frozen
  capex_pct. New input `ronic` (default = WACC → growth is value-neutral).
  Gordon-equivalent TV is reported alongside for reference.  [breaking]
- GATE 4 REPLACED by `enforce_ronic_gate`: pooled 3Y incremental ROIC < WACC
  → RONIC forced to WACC (growth adds nothing in TV). No tg override, no
  3-consecutive-year test on single-year ratios.
- ONE PROJECTION KERNEL `_project()` shared by run_dcf, breakevens, reverse
  DCF, implied-margin / implied-RONIC solvers, tornado and waterfall — the
  SBC/lease haircuts, R9 non-core PV and engine choice are applied identically
  everywhere (fixes v16.1 reverse_dcf inconsistencies).
- NEW `what_must_be_true()` — per-driver market-implied values (Y3+ CAGR,
  Y10 margin, WACC, RONIC, tg) at the current price, each holding the other
  inputs at model values. Replaces `compute_implied_cap` (removed: could not
  discriminate CAP > 10y and bypassed gates/R9).
- NEW `gap_waterfall()` — additive attribution of DCF-vs-market gap:
  near-term growth (consensus swap) → near-term margin (consensus swap) →
  long-term path/TV/WACC residual, plus market-implied LT CAGR at consensus
  near-term.
- ROIC: invested capital EX-leases, NOPAT = (EBIT − lease_interest)(1 − t)
  (rent-as-opex consistency). Pooled 3Y incremental ROIC is the gate statistic;
  per-year series retained as information only.
- Modelling options reduced to 4: engine, sbc, nwc_scope, non_core_treatment.
  `lease_convention` and `mid_year` are recorded constants, not options.
- Bug fixes: R9 path upside_pct now a percentage like the non-R9 path;
  `sanity_y1_vs_actual_pct` removed (levered vs unlevered comparison);
  R8 sign rule is ADVISORY (never halts) — residual ≤10% remains the bridge gate.
- Tornado: tax_rate replaced by RONIC (±500bps).

PRESERVED: calendar-aware/mid-year discounting (TV at end-Y10 − 0.5y), R8
signed unlevering, R9 strip-out + dividend-as-FCF, SBC cash-cost wiring,
cyclical through-cycle handling, quality/ROIC/CAP helpers, options hash.

Imported by all DCF scripts. No LLM judgment in this file.
"""
import hashlib
import json
import copy
from datetime import datetime, date

# v15.2 ADDITIONS (non-breaking):
# - Rule 8 fix: enforce_ufcf_sign_rule now evaluates SAME-PERIOD (UFCF_FY0 vs
#   reported FCF_FY0), removing FY0->Y1 growth contamination. build_fcf_bridge
#   reconciles a same-period UFCF_FY0 target; the FY0->Y1 move is a separate,
#   non-gated "growth_step" line. Falls back to Y1 (advisory, non-binding) only
#   when no FY0 UFCF data is supplied.
# - FCF bridge: residual gate + R8 sign gate are BINDING only on the same-period
#   reconciliation; advisory when FY0 data absent.
# - R9 dividend PV: value_non_core_holding now uses mid-year / calendar-aware
#   discounting (consistent with operating DCF) instead of full-year (1+r)^t,
#   and exposes balance-sheet carrying value + look-through fair value as
#   INFO ONLY (never credited to base-case EV).
# - TORNADO_SPEC + build_tornado(): pinned 8-variable sensitivity set (was an
#   un-versioned external script). Reproducible via TORNADO_SPEC_VERSION.
# - format_dcf_output: adds a CALIBRATION block (DCF implied vs consensus 12M
#   target, with a mandatory analyst gap-argument prompt) and an R9 balance-sheet
#   INFO line.

ENGINE_VERSION = "v16.5"
TORNADO_SPEC_VERSION = "v16.4"
LEASE_CONVENTION = "rent_as_opex"   # v16.4 — single convention, not an option

# Pinned tornado spec (v16.4): tax_rate dropped, RONIC added.
# The set is versioned so tornado output is reproducible.
TORNADO_SPEC = [
    {"key": "wacc",              "kind": "add_scalar",       "delta": 0.010, "label": "WACC (±100bps)"},
    {"key": "terminal_growth",   "kind": "add_scalar",       "delta": 0.005, "label": "Terminal growth (±50bps)"},
    {"key": "ronic",             "kind": "add_scalar",       "delta": 0.050, "label": "Terminal RONIC (±500bps)"},
    {"key": "_ebitda_tail",      "kind": "add_margin_tail",  "delta": 0.020, "label": "Terminal EBITDA margin Y3+ (±200bps)"},
    {"key": "_cagr_near",        "kind": "add_growth_near",  "delta": 0.020, "label": "Near-term rev CAGR Y1-2 (±200bps)"},
    {"key": "_cagr_far",         "kind": "add_growth_far",   "delta": 0.020, "label": "Far rev CAGR Y3+ (±200bps)"},
    {"key": "capex_pct",         "kind": "add_scalar",       "delta": 0.010, "label": "Capex % of revenue (±100bps)"},
    {"key": "dwc_pct",           "kind": "add_scalar",       "delta": 0.030, "label": "ΔWC % of ΔRevenue (±300bps)"},
]
# Cyclical sectors requiring 10Y through-cycle terminal margin (v15 + v15.1 additions)
CYCLICAL_SECTORS = {
    "Autos", "Automobiles", "Auto Components",
    "Chemicals", "Commodity Chemicals", "Specialty Chemicals",
    "Shipping", "Marine",
    "Container Shipping", "Liner Shipping",            # v15.1
    "Trucking", "Road Transport",                      # v15.1
    "Steel", "Metals & Mining",
    "Aluminum", "Copper", "Base Metals",               # v15.1
    "Construction Materials", "Cement",
    "Paper & Packaging", "Paper Products", "Packaging", # v15.1
    "Upstream Energy", "Oil & Gas Exploration",
    "Semis Equipment", "Semiconductor Equipment",
    "Memory Semis", "Memory Semiconductors",
    "Airlines",
    "Refining", "Oil Refining",
    "Capital Equipment", "Industrial Machinery",       # v15.1
    "Machinery", "Construction Machinery",
    "Homebuilding", "Homebuilders", "Residential Construction",   # v16.5
    "Household Durables", "Real Estate Development",              # v16.5
}

# v16.5 — rating thresholds on base-case upside (%), by quality tier.
RATING_THRESHOLDS = {
    "HIGH QUALITY":    {"buy": 10.0, "sell": -10.0},
    "STANDARD":        {"buy": 15.0, "sell": -15.0},
    "LOW QUALITY":     {"buy": 25.0, "sell": -10.0},
    "VALUE TRAP RISK": {"buy": 40.0, "sell": 0.0},
}
REVERSE_DCF_BOUNDS = (-0.20, 0.50)     # growth solver range (decimal CAGR)
DEFAULT_WACC_RANGE_HALF_WIDTH = 0.0075  # used only when wacc_range is not supplied

ASSET_HEAVY_SECTORS = {
    "Utilities", "Electric Utilities", "Gas Utilities", "Multi-Utilities",
    "Telecom", "Telecommunications", "Diversified Telecom",
    "Real Estate", "Equity REITs",
    "Upstream Energy",
    "Mining", "Metals & Mining",
    "Pipelines", "Oil & Gas Storage & Transportation",
    "Railroads",
}

CONTRACT_INTENSIVE_SECTORS = {
    "Aerospace & Defense",
    "Construction & Engineering",
    "Engineering",
    "Software", "Application Software", "Systems Software",
    "Pharmaceuticals",
}


def compute_options_hash(options):
    """Stable sha256 over canonical-JSON of modelling_options (excluding hash field)."""
    if not options:
        return None
    clean = {k: v for k, v in options.items() if k != "hash"}
    canon = json.dumps(clean, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canon.encode()).hexdigest()


def resolve_modelling_options(sector, financials, non_core_holdings=None):
    """
    v16.4 — resolve sector defaults for the FOUR modelling options.
    Returns (options_dict, triggers_list).

    Options: engine · sbc · nwc_scope · non_core_treatment.
    Constants (recorded, not choosable): lease_convention = rent_as_opex,
    mid_year = on. Capitalised R&D is an analyst adjustment inside the
    normalised-EBITDA build (Rule 3), not an option.

    financials keys used (all optional): da_capex_ratio_3y, da_ebitda_3y,
    sbc_revenue_ratio, contract_al_revenue_ratio.
    """
    options = {
        "engine": "ebitda_native",
        "sbc": "non_cash_addback",
        "nwc_scope": "trade_only",
        "non_core_treatment": "n_a",
        "lease_convention": LEASE_CONVENTION,   # constant
        "mid_year": "on",                       # constant
    }
    triggers = []

    # Option 1: Projection engine
    if sector in ASSET_HEAVY_SECTORS:
        options["engine"] = "nopat_native"
        triggers.append({"option": "engine", "recommended": "nopat_native",
                         "reason": f"Asset-heavy sector ({sector})",
                         "impact": "Explicit maint/growth capex split instead of D&A tax-shield approximation."})
    elif financials.get("da_capex_ratio_3y", 1.0) < 0.7:
        options["engine"] = "nopat_native"
        triggers.append({"option": "engine", "recommended": "nopat_native",
                         "reason": f"D&A/capex 3Y = {financials['da_capex_ratio_3y']:.2f} (< 0.7)",
                         "impact": "Capex chronically exceeds D&A — explicit capex projection."})
    elif financials.get("da_ebitda_3y", 0) > 0.40:
        options["engine"] = "nopat_native"
        triggers.append({"option": "engine", "recommended": "nopat_native",
                         "reason": f"D&A/EBITDA 3Y = {financials['da_ebitda_3y']:.1%} (> 40%)",
                         "impact": "Asset consumption dominates economics."})

    # Option 2: SBC treatment
    sbc_to_rev = financials.get("sbc_revenue_ratio", 0)
    if sbc_to_rev > 0.05:
        options["sbc"] = "cash_cost"
        triggers.append({"option": "sbc", "recommended": "cash_cost",
                         "reason": f"SBC = {sbc_to_rev:.1%} of revenue (> 5%)",
                         "impact": f"EBITDA margins reduced by ~{sbc_to_rev*100:.1f}ppt in every projection year."})

    # Option 3: NWC scope
    contract_ratio = financials.get("contract_al_revenue_ratio", 0)
    if sector in CONTRACT_INTENSIVE_SECTORS or contract_ratio > 0.10:
        options["nwc_scope"] = "extended"
        reason = (f"Contract-intensive sector ({sector})" if sector in CONTRACT_INTENSIVE_SECTORS
                  else f"Contract A/L = {contract_ratio:.1%} of revenue (> 10%)")
        triggers.append({"option": "nwc_scope", "recommended": "extended",
                         "reason": reason,
                         "impact": "Contract assets/liabilities included in NWC; forward ΔNWC% set per skill (0% default for project-delivery)."})

    # Option 4: Non-core holding treatment (R9)
    if non_core_holdings:
        options["non_core_treatment"] = "dividend_only"
        names = ", ".join(h.get("name", "?") for h in non_core_holdings[:3])
        extra = f" + {len(non_core_holdings)-3} more" if len(non_core_holdings) > 3 else ""
        triggers.append({"option": "non_core_treatment", "recommended": "dividend_only",
                         "reason": f"R9 fired: {len(non_core_holdings)} non-core holding(s) [{names}{extra}]",
                         "impact": "Operating figures stripped; captive debt excluded from bridge; non-core valued as PV(dividend stream). Monetization = bull overlay only."})

    return options, triggers


def enforce_ronic_gate(inputs, roic_data):
    """
    v16.4 — replaces BINDING GATE 4.

    Terminal reinvestment economics: TV = NOPAT_11 × (1 − tg/RONIC)/(WACC − tg).
    If the pooled 3Y incremental ROIC (roic_data['incremental_roic']) is below
    WACC and the analyst set RONIC > WACC, RONIC is forced to WACC — growth then
    adds nothing to terminal value (not a penalty, a neutralisation). Override
    by supplying inputs['ronic_override_justification'] (string): RONIC is
    kept as supplied and the override is surfaced.

    If `ronic` is absent it defaults to WACC (neutral) with basis recorded.
    Returns (adjusted_inputs, gate_fired_bool, message).
    """
    wacc = inputs["wacc"]
    ronic = inputs.get("ronic")
    adj = dict(inputs)
    if ronic is None:
        adj["ronic"] = wacc
        adj["ronic_basis"] = "default_wacc_neutral"
        return adj, False, None

    if not roic_data:
        return adj, False, None

    incr = roic_data.get("incremental_roic")
    if incr is None or incr >= wacc or ronic <= wacc:
        return adj, False, None

    if inputs.get("ronic_override_justification"):
        msg = (f"⚠ RONIC GATE OVERRIDDEN: pooled 3Y incremental ROIC {incr:.1%} < WACC {wacc:.1%} "
               f"but RONIC kept at {ronic:.1%}. Justification: {inputs['ronic_override_justification']}")
        adj["ronic_gate_overridden"] = True
        return adj, False, msg

    adj["ronic_pre_gate"] = ronic
    adj["ronic"] = wacc
    adj["ronic_basis"] = "gate_forced_to_wacc"
    msg = (f"⛔ RONIC GATE: pooled 3Y incremental ROIC {incr:.1%} < WACC {wacc:.1%}. "
           f"Terminal RONIC set to WACC (was {ronic:.1%}) — terminal growth is value-neutral. "
           f"Override with inputs['ronic_override_justification'].")
    return adj, True, msg


def is_cyclical_sector(sector):
    """Check whether a sector requires through-cycle terminal margin (v15)."""
    return sector in CYCLICAL_SECTORS


def cycle_position_check(fy0_margin, through_cycle_margin):
    """
    Returns dict with cycle position status. Flags cycle peak if FY0 margin
    exceeds through-cycle by >200bps.
    """
    if through_cycle_margin is None or fy0_margin is None:
        return {"status": "UNKNOWN", "cycle_peak_fy0": False}

    spread_bps = (fy0_margin - through_cycle_margin) * 10000
    cycle_peak = spread_bps > 200

    if spread_bps > 200:
        status = "PEAK"
    elif spread_bps > 50:
        status = "ELEVATED"
    elif spread_bps < -200:
        status = "TROUGH"
    elif spread_bps < -50:
        status = "BELOW_CYCLE"
    else:
        status = "MID_CYCLE"

    return {
        "status": status,
        "cycle_peak_fy0": cycle_peak,
        "fy0_margin": fy0_margin,
        "through_cycle_margin": through_cycle_margin,
        "spread_bps": round(spread_bps, 0),
    }


# ═══════════════════════════════════════════════════════════════════

def compute_net_interest_position(inputs):
    """
    Compose `net_interest_position_fy0` from raw interest fields. Returns the
    signed-net dict. If user already populated it, validates consistency.

    Convention:
      net = interest_expense - interest_income  (signed)
      atx_net = net * (1 - tax_rate_applied)    (signed)
      positive = net debt, negative = net cash
    """
    nip = inputs.get("net_interest_position_fy0")
    if nip and "net" in nip and "atx_net" in nip:
        return nip

    # Compose from raw fields
    interest_exp = inputs.get("interest_expense_fy0", 0)
    interest_inc = inputs.get("interest_income_fy0", 0)
    if nip:
        interest_exp = nip.get("interest_expense", interest_exp)
        interest_inc = nip.get("interest_income", interest_inc)

    net = interest_exp - interest_inc
    tax = inputs.get("tax_rate", 0.25)
    if nip and "tax_rate_applied" in nip:
        tax = nip["tax_rate_applied"]
    atx_net = net * (1 - tax)

    direction = "UFCF > FCF" if net > 0 else "UFCF < FCF" if net < 0 else "UFCF ≈ FCF"

    return {
        "interest_expense": interest_exp,
        "interest_income":  interest_inc,
        "net":              net,
        "tax_rate_applied": tax,
        "atx_net":          atx_net,
        "bridge_direction": direction,
    }


def enforce_ufcf_sign_rule(ufcf_y1, fcf_fy0, atx_net_fy0, noise_threshold=0.05):
    """
    v16.4 ADVISORY (was binding): UFCF/FCF direction should agree with signed net interest. Never halts.

    Returns dict {passed, expected_direction, observed_direction, message}.

    Rule:
      sign(ufcf - fcf) must == sign(atx_net)
    Below `noise_threshold` of |fcf| → pass (rounding/timing noise).
    """
    if fcf_fy0 == 0:
        return {
            "passed": True, "skipped": True,
            "expected_direction": "n/a (no reported FCF)",
            "observed_direction": "n/a",
            "message": "R8 skipped: no reported_fcf_fy0",
        }

    delta = ufcf_y1 - fcf_fy0
    abs_pct = abs(delta) / abs(fcf_fy0)

    sign_observed = "positive" if delta > 0 else "negative" if delta < 0 else "zero"
    sign_expected = "positive" if atx_net_fy0 > 0 else "negative" if atx_net_fy0 < 0 else "zero"

    obs_dir = "UFCF > FCF" if delta > 0 else "UFCF < FCF" if delta < 0 else "UFCF = FCF"
    exp_dir = "UFCF > FCF" if atx_net_fy0 > 0 else "UFCF < FCF" if atx_net_fy0 < 0 else "UFCF = FCF"

    # Below noise threshold → passes (cannot reliably infer sign)
    if abs_pct < noise_threshold:
        return {
            "passed": True,
            "expected_direction": exp_dir,
            "observed_direction": obs_dir,
            "delta": round(delta, 1),
            "delta_pct_of_fcf": round(abs_pct, 4),
            "atx_net": round(atx_net_fy0, 1),
            "message": f"R8: gap {abs_pct:.1%} below {noise_threshold:.0%} noise threshold — pass",
        }

    passed = (sign_observed == sign_expected) or (sign_expected == "zero")
    msg = (f"R8 sign check: expected {exp_dir} (atx_net={atx_net_fy0:+.1f}), "
           f"observed {obs_dir} (Δ={delta:+.1f}, {abs_pct:.1%} of |FCF|).")
    if not passed:
        msg = ("⚠ R8 ADVISORY — UFCF unlevering direction inconsistent with net interest position. "
               f"Net interest signed: {atx_net_fy0:+.1f} (positive = net debt, negative = net cash). "
               f"UFCF − FCF observed: {delta:+.1f}. "
               "Verify net_interest_position_fy0.net is signed correctly OR investigate other bridge lines.")

    return {
        "passed": passed,
        "expected_direction": exp_dir,
        "observed_direction": obs_dir,
        "delta": round(delta, 1),
        "delta_pct_of_fcf": round(abs_pct, 4),
        "atx_net": round(atx_net_fy0, 1),
        "message": msg,
    }


# ═══════════════════════════════════════════════════════════════════
# v15.1: R9 NON-CORE HOLDINGS — STRIP-OUT + DIVIDEND-AS-FCF
# ═══════════════════════════════════════════════════════════════════

VALID_NON_CORE_TYPES = {
    "captive_finance", "equity_method", "fvoci", "fvtpl", "listed_subsidiary"
}


def strip_non_core_from_group(group_inputs, non_core_list):
    """
    v15.1 R9: Return operating-only inputs after stripping non-core figures.
    Strips: revenue, EBITDA, D&A, capex contributions per non-core holding.
    Also strips: balance_sheet_debt_to_exclude from net_debt, captive cash.

    Returns (stripped_inputs, strip_report).
    """
    if not non_core_list:
        return group_inputs, {"applied": False}

    stripped = dict(group_inputs)
    report = {"applied": True, "holdings_stripped": [], "totals": {}}

    # Sum strip values across all non-core holdings
    rev_strip   = sum(h.get("fy0_revenue", 0)   for h in non_core_list)
    ebitda_strip= sum(h.get("fy0_ebitda", 0)    for h in non_core_list)
    da_strip    = sum(h.get("fy0_da", 0)        for h in non_core_list)
    capex_strip = sum(h.get("fy0_capex", 0)     for h in non_core_list)
    debt_strip  = sum(h.get("balance_sheet_debt_to_exclude", 0) for h in non_core_list)
    cash_strip  = sum(h.get("balance_sheet_cash_in_captive", 0) for h in non_core_list)

    # Strip revenue (base + reported)
    pre_rev = stripped.get("base_revenue", 0)
    if pre_rev > 0:
        stripped["base_revenue_pre_strip"] = pre_rev
        stripped["base_revenue"] = max(0, pre_rev - rev_strip)

    # Strip net_debt: captive debt EXCLUDED from operating EV bridge (per R9)
    # CONTRACT: if user provides `net_debt_basis = "operating_only"`, trust them and skip strip.
    # If `net_debt_basis = "group_consolidated"` or absent and balance_sheet_debt_to_exclude > 0,
    # strip the captive debt and trapped cash.
    pre_nd = stripped.get("net_debt", 0)
    nd_basis = stripped.get("net_debt_basis", None)
    stripped["net_debt_pre_strip"] = pre_nd
    if nd_basis == "operating_only":
        # Analyst already provided operating-only net debt (e.g., Renault's "auto net cash" disclosure)
        # Don't double-strip; just record the flag
        stripped["net_debt"] = pre_nd
        stripped["_strip_debt_applied"] = False
        stripped["_strip_debt_reason"] = "net_debt_basis='operating_only' — analyst-provided, no strip applied"
    else:
        # Apply strip: remove captive debt, remove trapped captive cash
        stripped["net_debt"] = pre_nd - debt_strip + cash_strip
        stripped["_strip_debt_applied"] = True
        stripped["_strip_debt_reason"] = (
            f"Stripped €{debt_strip:.0f}m captive debt + €{cash_strip:.0f}m trapped cash "
            f"from net_debt (basis: {nd_basis or 'group_consolidated_assumed'})"
        )

    # Track contribution adjustments (used by ebitda/capex/da % derivations
    # if the analyst hasn't already given operating-only percentages)
    stripped["_non_core_strip"] = {
        "fy0_revenue_stripped": rev_strip,
        "fy0_ebitda_stripped":  ebitda_strip,
        "fy0_da_stripped":      da_strip,
        "fy0_capex_stripped":   capex_strip,
        "balance_sheet_debt_excluded": debt_strip,
        "captive_cash_excluded": cash_strip,
    }

    for h in non_core_list:
        report["holdings_stripped"].append({
            "name": h.get("name", "?"),
            "type": h.get("type", "?"),
            "fy0_revenue": h.get("fy0_revenue", 0),
            "fy0_ebitda":  h.get("fy0_ebitda", 0),
            "fy0_da":      h.get("fy0_da", 0),
            "fy0_capex":   h.get("fy0_capex", 0),
            "fy0_dividend_paid": h.get("fy0_dividend_paid", 0),
            "balance_sheet_debt_excluded": h.get("balance_sheet_debt_to_exclude", 0),
        })

    report["totals"] = {
        "revenue_stripped":   rev_strip,
        "ebitda_stripped":    ebitda_strip,
        "da_stripped":        da_strip,
        "capex_stripped":     capex_strip,
        "debt_stripped":      debt_strip,
        "cash_stripped":      cash_strip,
        "operating_revenue":  stripped.get("base_revenue", 0),
        "operating_net_debt": stripped.get("net_debt", 0),
    }

    return stripped, report


def value_non_core_holding(holding, parent_wacc, default_horizon=10, offsets=None):
    """
    v15.1 R9 / v15.2: Value a non-core holding as PV(dividend stream) + PV(terminal flat).

    Conservative defaults (UNCHANGED — base case stays dividend-only):
      - dividend_growth capped at 2%/yr
      - terminal: dividend held flat (no perpetual growth)
      - discount rate defaults to parent_wacc unless holding overrides

    v15.2 changes:
      - Discounting is mid-year (t−0.5) by default, or uses the parent's
        calendar-aware `offsets` when supplied — consistent with the operating
        DCF instead of the old full-year (1+r)^t.
      - Exposes balance_sheet_info: carrying value + look-through fair value,
        INFO ONLY. Never credited to base-case EV. Surfaces how far the
        dividend-only PV sits below book/market — i.e. the size of the
        conservatism, so a retain-and-compound stake isn't silently zeroed.
    """
    carrying = holding.get("fy0_book_equity", holding.get("fy0_carrying_value", 0)) or 0
    fair_value = holding.get("fy0_market_value", holding.get("fy0_fair_value", 0)) or 0
    bs_info = {
        "carrying_value": carrying,
        "fair_value": fair_value,
        "ownership_pct": holding.get("ownership_pct", 1.0),
        "note": ("INFO ONLY — balance-sheet carrying value / look-through fair value. "
                 "NOT credited to base-case EV (dividend PV is the base case). Shown to "
                 "size the gap vs dividend-only conservatism; monetization belongs in the "
                 "bull overlay."),
    }

    div0 = holding.get("fy0_dividend_paid", 0)
    horizon = holding.get("horizon_years", default_horizon)

    def _disc_offset(t):
        # t is 1-indexed explicit year; use calendar offset if available else mid-year
        if offsets and len(offsets) >= t:
            return offsets[t - 1]
        return t - 0.5  # mid-year

    if div0 <= 0:
        return {
            "pv_explicit": 0.0, "pv_terminal": 0.0, "pv_total": 0.0,
            "g_applied": 0.0,
            "r_applied": holding.get("discount_rate", parent_wacc),
            "horizon": horizon,
            "discount_convention": "mid_year_or_offsets",
            "balance_sheet_info": bs_info,
            "note": "No dividend paid — base PV = 0; consider monetization overlay in bull case.",
        }

    g_raw = holding.get("dividend_growth", 0.0)
    g = min(g_raw, 0.02)  # CAP at 2%
    r = holding.get("discount_rate", parent_wacc)

    # Explicit horizon PV (years 1..horizon), mid-year / calendar-aware
    pv_explicit = sum(
        div0 * (1 + g) ** t / (1 + r) ** _disc_offset(t)
        for t in range(1, horizon + 1)
    )

    # Terminal: flat perpetuity of mid-year flows. v16.1 — discounted at the
    # horizon year's OWN offset (mid-year point), consistent with the operating
    # TV treatment: Gordon assumes end-of-year flows, mid-year flows shift the
    # consistent discount point back by 0.5y, i.e. exactly _disc_offset(horizon).
    # (Pre-v16.1 the +0.5 add-on double-shifted, over-discounting the terminal.)
    terminal_div = div0 * (1 + g) ** horizon
    end_offset = _disc_offset(horizon)
    pv_terminal = (terminal_div / r) / (1 + r) ** end_offset

    return {
        "pv_explicit": round(pv_explicit, 1),
        "pv_terminal": round(pv_terminal, 1),
        "pv_total":    round(pv_explicit + pv_terminal, 1),
        "g_applied":   g,
        "g_capped":    g_raw > 0.02,
        "r_applied":   r,
        "horizon":     horizon,
        "div0":        div0,
        "discount_convention": "calendar_aware" if offsets else "mid_year",
        "balance_sheet_info": bs_info,
        "note": "Conservative: g capped at 2%, terminal held flat (no perpetual growth).",
    }


def stress_test_dividend(holding, parent_wacc, floor_pct=0.30, wacc_premium_bps=200):
    """
    v15.1 R9: stress-test captive finance dividend sustainability.

    Historical worst-cycle behaviour: captives cut to 25-40% of normal in 2008-09, 2020.
    Floor at 30%, add 200bps WACC premium for uncertainty.

    Returns dict with stress_pv, sustainability_buffer (= 1 - stress/base), and applied params.
    Used by bear-case scenarios and as a sensitivity overlay.
    """
    if holding.get("type") != "captive_finance":
        return {"applied": False, "reason": "Stress test only applicable to captive_finance type"}

    div0 = holding.get("fy0_dividend_paid", 0)
    if div0 <= 0:
        return {"applied": False, "reason": "No dividend to stress"}

    stress = dict(holding)
    stress["fy0_dividend_paid"] = div0 * floor_pct
    stress_wacc = (holding.get("discount_rate") or parent_wacc) + wacc_premium_bps / 10000.0
    stress["discount_rate"] = stress_wacc
    horizon = holding.get("horizon_years", 10)

    stress_pv = value_non_core_holding(stress, stress_wacc, horizon)
    base_pv   = value_non_core_holding(holding, holding.get("discount_rate") or parent_wacc, horizon)

    base_total = base_pv["pv_total"]
    stress_total = stress_pv["pv_total"]
    buffer = (base_total - stress_total) / base_total if base_total > 0 else 0.0

    return {
        "applied":              True,
        "holding_name":         holding.get("name", "?"),
        "floor_pct":            floor_pct,
        "wacc_premium_bps":     wacc_premium_bps,
        "stress_dividend":      round(div0 * floor_pct, 1),
        "stress_wacc":          stress_wacc,
        "base_pv":              base_total,
        "stress_pv":            stress_total,
        "sustainability_buffer": round(buffer, 4),
        "note": (
            f"Stress: dividend cut to {floor_pct:.0%} of normal (€{div0:.0f}m → €{div0*floor_pct:.0f}m), "
            f"WACC + {wacc_premium_bps}bps. Bear-case PV: €{stress_total:.0f}m vs base €{base_total:.0f}m "
            f"({buffer:.0%} loss)."
        ),
    }


def _monetization_overlay_value(holding, base_pv):
    """v15.1 R9: bull-case monetization overlay — only included when active."""
    m = holding.get("monetization_overlay") or {}
    if not m.get("active", False):
        return {"value": 0.0, "active": False}
    prob = m.get("probability", 0.0)
    fv = m.get("fair_value", 0.0)
    friction = m.get("friction_discount", 0.20)
    realized = fv * (1 - friction)
    incremental = max(0.0, realized - base_pv)
    return {
        "value": round(prob * incremental, 1),
        "active": True,
        "probability": prob,
        "fair_value": fv,
        "friction": friction,
        "realized_post_friction": round(realized, 1),
        "incremental_vs_dividend_pv": round(incremental, 1),
        "timeline_months": m.get("timeline_months"),
        "catalyst": m.get("catalyst", ""),
    }


def compute_non_core_aggregate(non_core_list, parent_wacc, include_bull_overlay=False, offsets=None):
    """
    v15.1 R9 / v15.2: Aggregate dividend-stream PVs across all non-core holdings.
    Optionally adds monetization overlays (bull case only).
    v15.2: passes `offsets` for mid-year/calendar-aware discounting and aggregates
    balance-sheet carrying value + look-through fair value (INFO ONLY).

    Returns dict with per-holding detail and totals.
    """
    if not non_core_list:
        return {"active": False, "total_pv": 0.0, "holdings": []}

    per_holding = []
    total_base_pv = 0.0
    total_bull_overlay = 0.0
    total_stress_pv = 0.0
    total_carrying = 0.0
    total_fair_value = 0.0
    any_stress_active = False

    for h in non_core_list:
        pv = value_non_core_holding(h, parent_wacc, offsets=offsets)
        overlay = _monetization_overlay_value(h, pv["pv_total"])
        bull_contribution = overlay["value"] if include_bull_overlay else 0.0
        stress = stress_test_dividend(h, parent_wacc)
        bs = pv.get("balance_sheet_info", {})

        per_holding.append({
            "name": h.get("name", "?"),
            "type": h.get("type", "?"),
            "ownership_pct": h.get("ownership_pct", 1.0),
            "rationale": h.get("rationale", ""),
            "fy0_dividend": h.get("fy0_dividend_paid", 0),
            "dividend_pv": pv,
            "balance_sheet_info": bs,
            "monetization_overlay": overlay,
            "stress_test": stress,
            "contribution_base": pv["pv_total"],
            "contribution_bull_overlay": bull_contribution,
        })
        total_base_pv += pv["pv_total"]
        total_carrying += bs.get("carrying_value", 0) or 0
        total_fair_value += bs.get("fair_value", 0) or 0
        if include_bull_overlay:
            total_bull_overlay += bull_contribution
        # Stress aggregate: use stress_pv for captives, base_pv for others
        if stress.get("applied"):
            total_stress_pv += stress["stress_pv"]
            any_stress_active = True
        else:
            total_stress_pv += pv["pv_total"]

    return {
        "active": True,
        "n_holdings": len(non_core_list),
        "holdings": per_holding,
        "total_base_pv": round(total_base_pv, 1),
        "total_bull_overlay": round(total_bull_overlay, 1) if include_bull_overlay else 0.0,
        "total_pv": round(total_base_pv + total_bull_overlay, 1),
        "total_stress_pv": round(total_stress_pv, 1),     # for bear-case scenarios
        # v15.2 — INFO ONLY (not credited to base-case EV)
        "total_carrying_value_info": round(total_carrying, 1),
        "total_fair_value_info": round(total_fair_value, 1),
        "dividend_pv_vs_fair_value_pct": (round(total_base_pv / total_fair_value, 4)
                                          if total_fair_value else None),
        "stress_active": any_stress_active,
        "include_bull_overlay": include_bull_overlay,
        "wacc_applied": parent_wacc,
    }


def validate_non_core_no_double_count(state):
    """
    v15.1 R9: Verify no non-core holding's book/FV appears in BOTH the dividend
    stream AND any bridge line. Common error: legacy state files added
    equity-method carrying value to bridge AND credited dividend stream.

    Returns dict {ok, violations}.
    """
    inputs = state.get("inputs", {})
    non_core = inputs.get("non_core_holdings", [])
    if not non_core:
        return {"ok": True, "applied": False}

    violations = []
    # Check 1: if net_debt_basis = group_consolidated, the strip must have applied
    nd_basis = inputs.get("net_debt_basis")
    strip_applied = inputs.get("_strip_debt_applied", None)
    debt_to_strip = sum(h.get("balance_sheet_debt_to_exclude", 0) for h in non_core)

    if nd_basis == "operating_only":
        # User asserts net_debt is already operating-only; no strip expected.
        # Nothing to check on the debt side.
        pass
    else:
        # Group-consolidated basis (or unspecified): strip must have happened
        if debt_to_strip > 0 and strip_applied is False:
            violations.append({
                "type": "missing_strip",
                "detail": (f"non_core debt €{debt_to_strip:.0f}m should be excluded from net_debt "
                           f"but strip did not apply. Either set net_debt_basis='operating_only' "
                           f"or ensure analyst-provided net_debt is group-consolidated."),
            })

    # Check 2: book_equity should NOT be added to bridge anywhere
    for h in non_core:
        book = h.get("fy0_book_equity", 0)
        treatment = h.get("treatment", "dividend_only")
        if treatment == "book_value_add" and book > 0:
            violations.append({
                "type": "book_value_add_legacy",
                "detail": (f"Holding '{h.get('name','?')}' uses treatment='book_value_add' "
                           f"(€{book:.0f}m book) — disallowed by default; requires explicit override + rationale"),
            })

    # Check 3: dividend stream computed AND market_value also added → double-count risk flag
    for h in non_core:
        mv = h.get("fy0_market_value", 0)
        div = h.get("fy0_dividend_paid", 0)
        if mv > 0 and div > 0 and h.get("type") in {"fvoci", "fvtpl", "listed_subsidiary"}:
            # Only flag if MV explicitly added to bridge somewhere (we can't fully detect from state,
            # so this is informational)
            pass  # detection requires bridge-side instrumentation; skip for now

    return {
        "ok": len(violations) == 0,
        "applied": True,
        "n_holdings_checked": len(non_core),
        "violations": violations,
    }


def _resolve_tax(inputs, year_idx):
    """Year-by-year tax rate. v14: if tax_fade present, use schedule; else flat."""
    fade = inputs.get("tax_fade")
    if fade and len(fade) >= 10:
        return fade[year_idx]
    return inputs["tax_rate"]


# ═══════════════════════════════════════════════════════════════════
# v14: Calendar-aware discounting
# ═══════════════════════════════════════════════════════════════════

def _parse_iso_date(d):
    if isinstance(d, date) and not isinstance(d, datetime):
        return d
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, str):
        return datetime.strptime(d[:10], "%Y-%m-%d").date()
    return None


def _compute_time_offsets(inputs):
    """
    Compute the discount-time (in years) from analysis_date to each forecast
    year's mid-cash-flow point and to the terminal-value date.

    Conventions:
    - inputs["analysis_date"] = ISO date string when the valuation is being done
      (default: today)
    - inputs["fiscal_year_end_month"] = 1..12, the month in which the fiscal
      year ends (default: 12)
    - "Y1" is the first forecast fiscal year — the FY immediately following
      the most recent completed FY0.
      Example: if FY0 ended Dec 2025 and analysis_date = 2026-05-17,
      then Y1 = FY2026, mid-cash-flow point = 2026-06-30 (mid of Y1).
      Discount horizon to Y1 = (2026-06-30 − 2026-05-17) / 365.25
                             ≈ 0.124 years (NOT 0.5).

    - Terminal value (v16.1): when mid-year is ON, TV is discounted at
      end-of-Y10 MINUS 0.5y so the Gordon perpetuity carries the same
      mid-year convention as the explicit flows (raises PV(TV) by
      ≈(1+WACC)^0.5 vs the pre-v16.1 end-of-Y10 anchor). When mid-year is
      OFF, TV stays at Y10's end-of-year offset.

    Returns:
    {
      "mid_year_offsets":  [t1, t2, ..., t10],  # years from analysis_date
      "terminal_offset":   t_end_y10,
      "convention": "calendar_aware" | "uniform_t_minus_0_5" | "end_of_year",
      "fy0_year_end": "YYYY-MM-DD",
      "y10_year_end": "YYYY-MM-DD",
    }
    """
    mid_year = inputs.get("modelling_options", {}).get("mid_year", "on") == "on"
    if "mid_year" in inputs and isinstance(inputs["mid_year"], bool):
        mid_year = inputs["mid_year"]

    analysis_date = _parse_iso_date(inputs.get("analysis_date") or inputs.get("date"))
    fye_month = inputs.get("fiscal_year_end_month", 12)
    last_fy_actual = inputs.get("last_completed_fy")  # int, e.g. 2025

    # Fall back to legacy behaviour if we lack the inputs to compute calendar offsets
    if not analysis_date or not last_fy_actual:
        if mid_year:
            # v13 convention: yr=1..10, df = 1/(1+w)^(yr-0.5), so offsets = [0.5, 1.5, ..., 9.5]
            # v16.1: TV carries the SAME mid-year adjustment (terminal offset 9.5,
            # not 10.0). Gordon TV assumes end-of-year perpetuity flows; under a
            # mid-year convention the Y11+ flows also arrive mid-year, so the
            # consistent discount point is end-of-Y10 − 0.5. The previous mix
            # (explicit flows mid-year, TV end-year) understated PV(TV) by
            # ≈(1+WACC)^0.5 without documenting the choice.
            return {
                "mid_year_offsets": [i - 0.5 for i in range(1, 11)],
                "terminal_offset": 9.5,
                "terminal_mid_year_adjustment": True,
                "convention": "uniform_t_minus_0_5",
                "fy0_year_end": None,
                "y10_year_end": None,
            }
        else:
            return {
                "mid_year_offsets": [float(i) for i in range(1, 11)],
                "terminal_offset": 10.0,
                "terminal_mid_year_adjustment": False,
                "convention": "end_of_year",
                "fy0_year_end": None,
                "y10_year_end": None,
            }

    # FY0 year-end date
    fy0_year_end = date(last_fy_actual, fye_month, _last_day_of_month(last_fy_actual, fye_month))

    offsets = []
    for k in range(1, 11):
        fy_end = date(last_fy_actual + k, fye_month, _last_day_of_month(last_fy_actual + k, fye_month))
        # Start of this forecast year = day after previous FY end
        fy_start = date(last_fy_actual + k - 1, fye_month, _last_day_of_month(last_fy_actual + k - 1, fye_month))
        # Mid-cash-flow point = midpoint of [fy_start+1day, fy_end]
        # Approximate as midpoint of fy_start..fy_end
        mid_days = (fy_end - fy_start).days // 2
        mid_point = fy_start + _days(mid_days)
        if mid_year:
            target = mid_point
        else:
            target = fy_end
        delta_days = (target - analysis_date).days
        offset_years = delta_days / 365.25
        offsets.append(offset_years)

    # Terminal value discount point (v16.1):
    # - mid-year ON: end-of-Y10 minus half a year, so the Gordon perpetuity
    #   (whose flows arrive mid-year under this convention) is discounted
    #   consistently with the explicit years.
    # - mid-year OFF: end of Y10 (flows crystallise at year-end).
    y10_end = date(last_fy_actual + 10, fye_month, _last_day_of_month(last_fy_actual + 10, fye_month))
    terminal_offset = (y10_end - analysis_date).days / 365.25
    if mid_year:
        terminal_offset -= 0.5

    return {
        "mid_year_offsets": offsets,
        "terminal_offset": terminal_offset,
        "terminal_mid_year_adjustment": bool(mid_year),
        "convention": "calendar_aware",
        "fy0_year_end": fy0_year_end.isoformat(),
        "y10_year_end": y10_end.isoformat(),
        "analysis_date": analysis_date.isoformat(),
    }


def _days(n):
    from datetime import timedelta
    return timedelta(days=n)


def _last_day_of_month(year, month):
    if month == 12:
        return 31
    from datetime import date as _d
    return (_d(year, month + 1, 1) - _days(1)).day


def _pv_factor(wacc, time_offset):
    """PV factor = 1 / (1+wacc)^t where t is years from analysis_date."""
    return 1 / ((1 + wacc) ** time_offset)


# ═══════════════════════════════════════════════════════════════════
# v14: Engine routing guard
# ═══════════════════════════════════════════════════════════════════

def _check_engine_routing(inputs):
    """Refuse to run UFCF on banks/insurance — they need equity-financials skill."""
    sector = inputs.get("sector", "") or ""
    sub = inputs.get("sub_industry", "") or ""
    sector_lc = sector.lower()
    if "bank" in sector_lc and "asset management" not in sub.lower():
        return ("WRONG_ENGINE",
                f"Sector '{sector}' requires equity-financials skill (banks engine). "
                f"UFCF is structurally inappropriate for banks.")
    if "insurance" in sector_lc:
        return ("WRONG_ENGINE",
                f"Sector '{sector}' requires equity-financials skill (insurance engine). "
                f"UFCF is structurally inappropriate for insurers.")
    return None


# ═══════════════════════════════════════════════════════════════════
# Main entry
# ═══════════════════════════════════════════════════════════════════

def run_dcf(inputs, _skip_solvers=False):
    """Main DCF entry (v16.5).

    Order: engine routing → R9 strip-out → net-interest composition → R9
    non-core PV (needed by the solvers) → RONIC gate → projection kernel →
    equity bridge (no lease deduction) → solvers / what-must-be-true.
    `_skip_solvers=True` prices only (used inside scenario / robustness solvers).
    """
    routing_block = _check_engine_routing(inputs)
    if routing_block:
        return {"status": routing_block[0], "reason": routing_block[1],
                "engine_version": ENGINE_VERSION}

    non_core_list = inputs.get("non_core_holdings", [])
    strip_report = {"applied": False}
    if non_core_list:
        inputs, strip_report = strip_non_core_from_group(inputs, non_core_list)

    inputs["net_interest_position_fy0"] = compute_net_interest_position(inputs)

    # R9 non-core PV computed FIRST so every solver targets the operating EV.
    non_core_agg = None
    non_core_pv = 0.0
    if non_core_list:
        _offsets = _compute_time_offsets(inputs).get("mid_year_offsets")
        non_core_agg = compute_non_core_aggregate(
            non_core_list, inputs.get("wacc", 0.09), include_bull_overlay=False, offsets=_offsets)
        non_core_pv = non_core_agg["total_pv"]

    roic_data = inputs.get("roic_data")
    inputs, gate_fired, gate_msg = enforce_ronic_gate(inputs, roic_data)

    result = _run_dcf_core(inputs, non_core_pv=non_core_pv, skip_solvers=_skip_solvers)
    if not _skip_solvers:
        result["growth_paid_for"] = check_growth_paid_for(result, inputs, roic_data)

    result["ronic_gate_fired"] = gate_fired
    result["ronic_gate_message"] = gate_msg
    # Backward-compatible keys for downstream readers
    result["binding_gate_4_fired"] = gate_fired
    result["binding_gate_4_message"] = gate_msg

    if non_core_list:
        result["non_core_holdings_strip"] = strip_report
        result["non_core_holdings"] = non_core_agg
        result["non_core_holdings_pv_total"] = non_core_pv
        result["non_core_double_count_check"] = validate_non_core_no_double_count({"inputs": inputs})

    return result


def _margins_applied(inputs):
    """EBITDA margins after engine-applied haircuts.

    - SBC: subtracted only when modelling_options.sbc == 'cash_cost'
    - Lease cash cost: ALWAYS subtracted (rent-as-opex convention, v16.4).
      inputs['lease_cost_pct_of_revenue'] = (lease principal + lease interest
      paid) ÷ revenue, 3Y pooled. 0 when the analyst already built the
      normalised EBITDA on a rent-as-opex basis (state that in derivations).
    Returns (margins_list, sbc_pct, lease_pct).
    """
    options = inputs.get("modelling_options") or {}
    sbc_pct = inputs.get("sbc_pct_of_revenue", 0.0) if options.get("sbc", "non_cash_addback") == "cash_cost" else 0.0
    lease_pct = inputs.get("lease_cost_pct_of_revenue", 0.0) or 0.0
    raw = [m["margin"] for m in inputs["ebitda_margins"]]
    return [m - sbc_pct - lease_pct for m in raw], sbc_pct, lease_pct


def _terminal_value(nopat10, ufcf10, tg, terminal_wacc, ronic):
    """Value-driver TV with Gordon-equivalent for reference.
    TV = NOPAT_11 × (1 − tg/RONIC) / (WACC − tg).  tg ≤ 0 → no reinvestment."""
    if terminal_wacc <= tg:
        raise ValueError(f"Terminal WACC ({terminal_wacc}) must exceed terminal growth ({tg})")
    nopat11 = nopat10 * (1 + tg)
    if tg <= 0:
        reinvest_rate = 0.0
    else:
        ronic_eff = max(ronic, tg + 0.005)   # RONIC must exceed tg for a finite reinvestment rate
        reinvest_rate = tg / ronic_eff
    terminal_fcf = nopat11 * (1 - reinvest_rate)
    tv = terminal_fcf / (terminal_wacc - tg)
    tv_gordon = ufcf10 * (1 + tg) / (terminal_wacc - tg)
    return {
        "nopat_y11": nopat11,
        "reinvestment_rate": reinvest_rate,
        "terminal_fcf": terminal_fcf,
        "tv": tv,
        "tv_gordon_equivalent": tv_gordon,
    }


def _model_revenue_path(inputs):
    """Revenue Y1..Y10 on the model's own growth path (reference for operating leverage)."""
    path, prev = [], inputs["base_revenue"]
    for r in inputs["rev_growth"]:
        prev = prev * (1 + r["rate"])
        path.append(prev)
    return path


def _operating_leverage_margin(margin, rev_ref, rev_new, fixed_share):
    """Margin when revenue moves from rev_ref to rev_new with a fixed-cost share
    of the cost base (cost base = revenue × (1 − margin) on the reference path).
    margin_new = 1 − (1 − m) × (f × rev_ref / rev_new + (1 − f)).
    rev_ref here is the fixed-cost base already adjusted for restructuring
    (see the partial-adjustment step in _project)."""
    if not fixed_share or rev_new <= 0 or rev_ref <= 0:
        return margin
    m = 1 - (1 - margin) * (fixed_share * rev_ref / rev_new + (1 - fixed_share))
    return max(m, -1.0)


def _acquisition_spend(inputs, i, rev):
    """v16.5: acquisition cash out in year i (0-based): list of amounts or % of revenue."""
    lst = inputs.get("acquisition_spend")
    if lst:
        return float(lst[i]) if i < len(lst) and lst[i] is not None else 0.0
    return rev * (inputs.get("acquisition_spend_pct_of_revenue") or 0.0)


def _project(inputs, rev_growth, margins, wacc, tg, offsets, terminal_wacc=None, ronic=None, engine=None,
             rev_ref=None):
    """Shared projection kernel (v16.5). Used by run_dcf and every solver.

    margins: EBITDA margins ALREADY haircut (EBITDA-native) or EBIT margins
    (NOPAT-native). Both engines reduce to UFCF = NOPAT + D&A − capex − ΔNWC
    − acquisitions; they differ only in how capex is specified.
    rev_ref (v16.5): reference revenue path for operating leverage — when given
    and `fixed_cost_share` > 0, margins re-price as revenue departs from it.
    Fade stage (v16.5): `cap_years` > 10 → Y11..Y(CAP) on a NOPAT basis with
    growth fading linearly to tg and reinvestment g/RONIC, TV at Y(CAP).
    Returns dict with yearly rows, sum_pv, terminal block, ev.
    """
    engine = engine or (inputs.get("modelling_options") or {}).get("engine", "ebitda_native")
    terminal_wacc = terminal_wacc if terminal_wacc is not None else wacc
    ronic = ronic if ronic is not None else inputs.get("ronic", wacc)
    da_pct = inputs["da_pct"]
    dwc_pct = inputs["dwc_pct"]
    dwc_pct_decline = inputs.get("dwc_pct_decline")
    if dwc_pct_decline is None:
        dwc_pct_decline = min(dwc_pct, 0.0)   # no release on decline without evidence
    fixed_share = inputs.get("fixed_cost_share", 0.0) or 0.0
    # fixed costs catch up with the new revenue path over N years (restructuring); 0 → never
    adj_years = inputs.get("fixed_cost_adjustment_years", 3)
    lam = 1.0 / adj_years if adj_years else 0.0
    fixed_ratio = 1.0
    base_rev = inputs["base_revenue"]
    if engine == "nopat_native":
        maint_pct = inputs.get("maint_capex_pct", da_pct)
        growth_pct = inputs.get("growth_capex_pct", max(0.0, inputs["capex_pct"] - maint_pct))
        capex_pct = maint_pct + growth_pct
    else:
        capex_pct = inputs["capex_pct"]

    yearly = []
    prev = base_rev
    sum_pv = 0.0
    nopat10 = ufcf10 = ebitda10 = ebit10 = 0.0
    for i in range(10):
        tax = _resolve_tax(inputs, i)
        rev = prev * (1 + rev_growth[i])
        da = rev * da_pct
        m_i = margins[i]
        if rev_ref is not None and fixed_share > 0:
            fixed_ratio += (rev / rev_ref[i] - fixed_ratio) * lam
            m_i = _operating_leverage_margin(m_i, rev_ref[i] * fixed_ratio, rev, fixed_share)
        if engine == "nopat_native":
            ebit = rev * m_i
            ebitda = ebit + da
        else:
            ebitda = rev * m_i
            ebit = ebitda - da
        nopat = ebit * (1 - tax)
        capex = rev * capex_pct
        d_rev = rev - prev
        dwc = d_rev * (dwc_pct if d_rev >= 0 else dwc_pct_decline)
        acq = _acquisition_spend(inputs, i, rev)
        ufcf = nopat + da - capex - dwc - acq
        t_off = offsets["mid_year_offsets"][i]
        df = _pv_factor(wacc, t_off)
        pv = ufcf * df
        sum_pv += pv
        yearly.append({
            "year": i + 1,
            "revenue": round(rev, 0),
            "rev_growth_pct": round(rev_growth[i] * 100, 1),
            "ebitda_margin_pct": round(ebitda / rev * 100, 1) if rev else 0.0,
            "ebitda": round(ebitda, 0),
            "ebit": round(ebit, 0),
            "tax_rate": round(tax, 4),
            "nopat": round(nopat, 0),
            "da": round(da, 0),
            "capex": round(-capex, 0),
            "dwc": round(-dwc, 0),
            "acquisitions": round(-acq, 0),
            "ufcf": round(ufcf, 0),
            "ufcf_margin_pct": round(ufcf / rev * 100, 1) if rev else 0.0,
            "time_offset_years": round(t_off, 4),
            "discount_factor": round(df, 4),
            "pv_ufcf": round(pv, 0),
        })
        if i == 9:
            nopat10, ufcf10, ebitda10, ebit10 = nopat, ufcf, ebitda, ebit
        prev = rev

    # v16.5 fade stage: Y11..Y(CAP) when CAP > 10 (growth fades linearly to tg).
    cap = inputs.get("cap_years") or 0
    n2 = int(min(cap, 30)) - 10 if (inputs.get("fade_stage", "auto") != "off" and cap > 10) else 0
    g10 = rev_growth[9]
    stage_rows, pv_stage, nopat_end = [], 0.0, nopat10
    if n2 > 0:
        gs = [g10 + (tg - g10) * k / n2 for k in range(1, n2 + 1)] + [tg]
        for k in range(1, n2 + 1):
            g_k, g_next = gs[k - 1], gs[k]
            nopat_end = nopat_end * (1 + g_k)
            reinvest = 0.0 if g_next <= 0 else nopat_end * g_next / max(ronic, g_next + 0.005)
            fcf = nopat_end - reinvest
            t_off = offsets["mid_year_offsets"][9] + k
            pv = fcf * _pv_factor(wacc, t_off)
            pv_stage += pv
            stage_rows.append({"year": 10 + k, "growth_pct": round(g_k * 100, 2), "nopat": round(nopat_end, 0),
                               "reinvestment": round(reinvest, 0), "fcf": round(fcf, 0), "pv": round(pv, 0)})

    term = _terminal_value(nopat_end, ufcf10, tg, terminal_wacc, ronic)
    tv_offset = offsets["terminal_offset"] + n2
    pv_tv = term["tv"] * _pv_factor(wacc, tv_offset)
    # Exit multiple at Y10 on everything beyond Y10 (stage + TV), so it stays comparable to v16.4.
    beyond_y10_at_y10 = (pv_stage + pv_tv) / _pv_factor(wacc, offsets["terminal_offset"])
    return {
        "yearly": yearly,
        "sum_pv": sum_pv,
        "terminal": {**term, "ronic": ronic, "tg": tg, "terminal_wacc": terminal_wacc,
                     "y10_ebitda": ebitda10, "y10_ebit": ebit10, "y10_ufcf": ufcf10,
                     "fade_stage_years": n2, "fade_stage_rows": stage_rows,
                     "implied_exit_ev_ebitda": beyond_y10_at_y10 / ebitda10 if ebitda10 else None},
        "pv_fade_stage": pv_stage,
        "pv_tv": pv_tv,
        "ev": sum_pv + pv_stage + pv_tv,
        "y10_revenue": prev,
    }


def _other_claims_total(inputs):
    """v16.5: extra claims (deferred consideration, capitalised loss-making arms,
    puts on minorities, unpaid post-period acquisitions…) — list of
    {label, amount} or a number. Same definition in the bridge and the solvers."""
    oc = inputs.get("other_claims") or []
    if isinstance(oc, (int, float)):
        return float(oc)
    return sum(float(c.get("amount", 0.0)) for c in oc)


def _claims(inputs):
    """Equity-bridge claims (v16.4: NO lease liabilities; v16.5: + other_claims)."""
    return (inputs["net_debt"] + inputs.get("pension_deficit", 0.0) + inputs["minorities"]
            + _other_claims_total(inputs))


def _price_from_ev(ev, inputs, non_core_pv=0.0):
    eq = ev + non_core_pv - _claims(inputs)
    sh = inputs["shares_outstanding"]
    return eq / sh if sh else 0.0


def _target_ev(inputs, non_core_pv=0.0):
    """Operating EV the market is paying: mcap + claims − PV(non-core)."""
    return inputs["share_price"] * inputs["shares_outstanding"] + _claims(inputs) - non_core_pv


def _run_dcf_core(inputs, non_core_pv=0.0, skip_solvers=False):
    wacc = inputs["wacc"]
    tg = inputs["terminal_growth"]
    terminal_wacc = inputs.get("terminal_wacc", wacc)
    offsets = _compute_time_offsets(inputs)
    engine = (inputs.get("modelling_options") or {}).get("engine", "ebitda_native")
    rev_growth = [r["rate"] for r in inputs["rev_growth"]]

    if engine == "nopat_native":
        if "ebit_margins" in inputs:
            margins = [m["margin"] for m in inputs["ebit_margins"]]
            sbc_pct = lease_pct = 0.0
        else:
            ebitda_adj, sbc_pct, lease_pct = _margins_applied(inputs)
            margins = [m - inputs["da_pct"] for m in ebitda_adj]
    else:
        margins, sbc_pct, lease_pct = _margins_applied(inputs)

    proj = _project(inputs, rev_growth, margins, wacc, tg, offsets, terminal_wacc, inputs.get("ronic"), engine,
                    rev_ref=inputs.get("operating_leverage_ref"))
    ev_op = proj["ev"]
    ev = ev_op + non_core_pv
    claims = _claims(inputs)
    equity = ev - claims
    shares = inputs["shares_outstanding"]
    price = inputs["share_price"]
    implied = equity / shares if shares else 0.0
    upside = (implied / price - 1) * 100 if price else 0.0

    if skip_solvers:
        return {"status": "OK", "engine_version": ENGINE_VERSION, "inputs": inputs,
                "yearly": proj["yearly"], "implied_price": round(implied, 2), "current_price": price,
                "upside_pct": round(upside, 1), "enterprise_value_operating": round(ev_op, 0),
                "equity_value": round(equity, 0),
                "tv_pct_of_ev": round((proj["pv_tv"] + proj["pv_fade_stage"]) / ev_op * 100, 1) if ev_op else 0.0}

    try:
        wmbt = what_must_be_true(inputs, non_core_pv=non_core_pv, _margins=margins, _offsets=offsets, _engine=engine)
    except Exception as e:  # never let a solver kill the base run
        wmbt = {"status": "FAILED", "error": str(e)}

    options = inputs.get("modelling_options")
    term = proj["terminal"]
    sector = inputs.get("sector", "")
    fy0_margin = inputs.get("fy0_normalised_ebitda_margin")
    through_cycle = inputs.get("through_cycle_margin")
    cycle_data = None
    if is_cyclical_sector(sector) and fy0_margin is not None and through_cycle is not None:
        cycle_data = cycle_position_check(fy0_margin, through_cycle)

    return {
        "status": "OK",
        "engine_version": ENGINE_VERSION,
        "engine": engine,
        "inputs": inputs,
        "yearly": proj["yearly"],
        "sum_pv_ufcf": round(proj["sum_pv"], 0),
        "y10_ufcf": round(term["y10_ufcf"], 0),
        "terminal_value": round(term["tv"], 0),
        "terminal_value_gordon_equivalent": round(term["tv_gordon_equivalent"], 0),
        "terminal_block": {
            "method": "value_driver",
            "nopat_y11": round(term["nopat_y11"], 0),
            "ronic": term["ronic"],
            "ronic_basis": inputs.get("ronic_basis", "analyst"),
            "tg": tg,
            "terminal_wacc": terminal_wacc,
            "reinvestment_rate": round(term["reinvestment_rate"], 4),
            "terminal_fcf": round(term["terminal_fcf"], 0),
            "implied_exit_ev_ebitda": round(term["implied_exit_ev_ebitda"], 2) if term["implied_exit_ev_ebitda"] else None,
            "y10_ebitda": round(term["y10_ebitda"], 0),
            "fade_stage_years": term["fade_stage_years"],
            "cap_years": inputs.get("cap_years"),
        },
        "fade_stage": {"years": term["fade_stage_years"], "pv": round(proj["pv_fade_stage"], 0),
                       "rows": term["fade_stage_rows"]},
        "pv_terminal_value": round(proj["pv_tv"], 0),
        "enterprise_value_operating": round(ev_op, 0),
        "non_core_pv_added": round(non_core_pv, 0),
        "enterprise_value": round(ev, 0),
        # v16.5: value beyond Y10 (fade stage + TV) as % of operating EV
        "tv_pct_of_ev": round((proj["pv_tv"] + proj["pv_fade_stage"]) / ev_op * 100, 1) if ev_op else 0.0,
        "net_debt": inputs["net_debt"],
        "pension_deficit": inputs.get("pension_deficit", 0.0),
        "other_claims": inputs.get("other_claims") or [],
        "other_claims_total": round(_other_claims_total(inputs), 1),
        "lease_liabilities_memo": inputs.get("lease_liabilities", 0.0),
        "total_debt_claims": claims - inputs["minorities"],
        "minorities": inputs["minorities"],
        "equity_value": round(equity, 0),
        "shares": shares,
        "implied_price": round(implied, 1),
        "current_price": price,
        "upside_pct": round(upside, 1),
        "breakeven_wacc": wmbt.get("wacc", {}).get("market_implied"),
        "breakeven_tg": wmbt.get("terminal_growth", {}).get("market_implied"),
        "market_implied_cagr": wmbt.get("rev_cagr_y1_y10", {}).get("market_implied"),
        "market_implied_y10_rev": wmbt.get("rev_cagr_y1_y10", {}).get("implied_y10_revenue"),
        "what_must_be_true": wmbt,
        "modelling_options": options,
        "modelling_options_hash": compute_options_hash(options) if options else None,
        "lease_convention": LEASE_CONVENTION,
        "sbc_adjustment": ({"applied": True, "sbc_pct_of_revenue": sbc_pct, "treatment": "cash_cost",
                            "ebitda_margin_haircut_ppt": round(sbc_pct * 100, 2)} if sbc_pct > 0 else None),
        "lease_adjustment": ({"applied": True, "lease_cost_pct_of_revenue": lease_pct,
                              "ebitda_margin_haircut_ppt": round(lease_pct * 100, 2)} if lease_pct > 0 else None),
        "cycle_position": cycle_data,
        "derivations": inputs.get("derivations"),
        "consensus_snapshot": inputs.get("consensus_snapshot"),
        "terminal_wacc_used": terminal_wacc,
        "discount_convention": offsets["convention"],
        "discount_offsets": {
            "mid_year_offsets": [round(o, 4) for o in offsets["mid_year_offsets"]],
            "terminal_offset": round(offsets["terminal_offset"], 4),
            "terminal_mid_year_adjustment": offsets.get("terminal_mid_year_adjustment", False),
            "fy0_year_end": offsets.get("fy0_year_end"),
            "y10_year_end": offsets.get("y10_year_end"),
            "analysis_date": offsets.get("analysis_date"),
        },
        "computation_timestamp": datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════
# Solvers — all through _project() (v16.4; v16.5 operating-leverage reference path)
# ═══════════════════════════════════════════════════════════════════

def _solver_context(inputs, _margins=None, _offsets=None, _engine=None):
    engine = _engine or (inputs.get("modelling_options") or {}).get("engine", "ebitda_native")
    offsets = _offsets or _compute_time_offsets(inputs)
    if _margins is None:
        if engine == "nopat_native" and "ebit_margins" in inputs:
            margins = [m["margin"] for m in inputs["ebit_margins"]]
        else:
            margins, _, _ = _margins_applied(inputs)
            if engine == "nopat_native":
                margins = [m - inputs["da_pct"] for m in margins]
    else:
        margins = list(_margins)
    growth = [r["rate"] for r in inputs["rev_growth"]]
    return engine, offsets, margins, growth


def _ref_path(inputs):
    """Operating-leverage reference: the scenario's base path if set, else the model path."""
    return inputs.get("operating_leverage_ref") or _model_revenue_path(inputs)


def _bisect(f, lo, hi, target, iters=200, tol=1e-6, increasing=True):
    """Solve f(x) = target on [lo, hi]. `increasing`: f rises with x."""
    for _ in range(iters):
        mid = (lo + hi) / 2
        v = f(mid)
        if abs(v - target) <= tol * max(1.0, abs(target)):
            return mid
        if (v < target) == increasing:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def find_breakeven_wacc(inputs, non_core_pv=0.0, **ctx):
    """WACC at which implied price = current price (RONIC tracks WACC when it
    was defaulted to WACC; terminal WACC tracks when not overridden)."""
    engine, offsets, margins, growth = _solver_context(inputs, **ctx)
    rev_ref = _ref_path(inputs)
    tg = inputs["terminal_growth"]
    ronic_tracks = inputs.get("ronic_basis", "") in ("default_wacc_neutral", "gate_forced_to_wacc")
    twacc_tracks = "terminal_wacc" not in inputs or inputs.get("terminal_wacc") == inputs["wacc"]
    target = inputs["share_price"]

    def price_at(w):
        if w <= tg + 0.002:
            return float("inf")
        p = _project(inputs, growth, margins, w, tg, offsets,
                     w if twacc_tracks else inputs["terminal_wacc"],
                     w if ronic_tracks else inputs.get("ronic"), engine, rev_ref=rev_ref)
        return _price_from_ev(p["ev"], inputs, non_core_pv)

    lo, hi = max(tg + 0.005, 0.01), 0.50
    if price_at(hi) > target:
        return round(hi * 100, 2)
    if price_at(lo) < target:
        return round(lo * 100, 2)
    return round(_bisect(price_at, lo, hi, target, increasing=False) * 100, 2)


def find_breakeven_tg(inputs, non_core_pv=0.0, **ctx):
    """Terminal growth at which implied price = current price."""
    engine, offsets, margins, growth = _solver_context(inputs, **ctx)
    rev_ref = _ref_path(inputs)
    w = inputs["wacc"]
    twacc = inputs.get("terminal_wacc", w)
    target = inputs["share_price"]

    def price_at(tg):
        p = _project(inputs, growth, margins, w, tg, offsets, twacc, inputs.get("ronic"), engine, rev_ref=rev_ref)
        return _price_from_ev(p["ev"], inputs, non_core_pv)

    lo, hi = -0.10, twacc - 0.005
    if price_at(hi) < target:
        return round(hi * 100, 2)
    if price_at(lo) > target:
        return round(lo * 100, 2)
    return round(_bisect(price_at, lo, hi, target, increasing=True) * 100, 2)


def reverse_dcf(inputs, offsets=None, non_core_pv=0.0, hold_years=0, **ctx):
    """Uniform revenue CAGR the market prices, holding model margins/WACC/tg/RONIC.
    hold_years=n keeps the model's Y1..Yn growth and solves the CAGR for Y(n+1)..Y10.
    Returns (cagr_pct, implied_y10_revenue) — tuple, for backward compatibility."""
    if offsets is not None:
        ctx["_offsets"] = offsets
    engine, offsets, margins, growth = _solver_context(inputs, **ctx)
    rev_ref = _ref_path(inputs)
    w, tg = inputs["wacc"], inputs["terminal_growth"]
    twacc = inputs.get("terminal_wacc", w)
    target = _target_ev(inputs, non_core_pv)

    def ev_at(c):
        g = [growth[i] if i < hold_years else c for i in range(10)]
        return _project(inputs, g, margins, w, tg, offsets, twacc, inputs.get("ronic"), engine, rev_ref=rev_ref)

    lo, hi = REVERSE_DCF_BOUNDS
    if ev_at(hi)["ev"] < target:
        c = hi
    elif ev_at(lo)["ev"] > target:
        c = lo
    else:
        c = _bisect(lambda x: ev_at(x)["ev"], lo, hi, target, tol=1e-4, increasing=True)
    return round(c * 100, 2), round(ev_at(c)["y10_revenue"], 0)


def implied_terminal_margin(inputs, non_core_pv=0.0, from_year=3, **ctx):
    """Parallel shift of Y{from_year}..Y10 margins that hits the current price.
    Returns (implied_y10_margin, shift) as decimals, or (None, None) if unbounded."""
    engine, offsets, margins, growth = _solver_context(inputs, **ctx)
    rev_ref = _ref_path(inputs)
    w, tg = inputs["wacc"], inputs["terminal_growth"]
    twacc = inputs.get("terminal_wacc", w)
    target = _target_ev(inputs, non_core_pv)

    def ev_at(shift):
        m = [margins[i] + (shift if i >= from_year - 1 else 0.0) for i in range(10)]
        return _project(inputs, growth, m, w, tg, offsets, twacc, inputs.get("ronic"), engine, rev_ref=rev_ref)["ev"]

    lo, hi = -0.40, 0.40
    if ev_at(hi) < target or ev_at(lo) > target:
        return None, None
    s = _bisect(ev_at, lo, hi, target, tol=1e-4, increasing=True)
    return margins[-1] + s, s


def implied_ronic(inputs, non_core_pv=0.0, **ctx):
    """RONIC that hits the current price (all else at model values).
    Returns decimal, or None with reason when the price cannot be reached
    within [WACC, 60%] (tg ≤ 0 or price below the RONIC=WACC value)."""
    engine, offsets, margins, growth = _solver_context(inputs, **ctx)
    rev_ref = _ref_path(inputs)
    w, tg = inputs["wacc"], inputs["terminal_growth"]
    twacc = inputs.get("terminal_wacc", w)
    target = _target_ev(inputs, non_core_pv)
    if tg <= 0:
        return None, "tg ≤ 0 — RONIC irrelevant"

    def ev_at(r):
        return _project(inputs, growth, margins, w, tg, offsets, twacc, r, engine, rev_ref=rev_ref)["ev"]

    lo, hi = w, 0.60
    if ev_at(lo) > target:
        return None, "price below RONIC=WACC value — market implies RONIC ≤ WACC (or lower growth/margins)"
    if ev_at(hi) < target:
        return None, "price above RONIC=60% value — market implies more than terminal reinvestment economics"
    return _bisect(ev_at, lo, hi, target, tol=1e-4, increasing=True), None


def what_must_be_true(inputs, non_core_pv=0.0, consensus=None, **ctx):
    """Per-driver market-implied values at the current price, each holding every
    other input at its model value. This is the 'what is priced' statement
    (v16.4) — replaces the single-number reverse DCF and the reverse-CAP solver.

    consensus (optional): {"rev_cagr_y3_y10": x, "terminal_margin": y} adds a
    consensus column where the analyst has it.
    Returns dict keyed by driver → {ours, market_implied, consensus, note}.
    """
    engine, offsets, margins, growth = _solver_context(inputs, **ctx)
    rev_ref = _ref_path(inputs)
    ctx2 = {"_margins": margins, "_offsets": offsets, "_engine": engine}
    consensus = consensus or inputs.get("consensus_drivers") or {}
    out = {"status": "OK", "current_price": inputs["share_price"], "non_core_pv_excluded": round(non_core_pv, 0)}

    # 1. Growth — full-horizon uniform CAGR (legacy) and Y3+ CAGR holding Y1–Y2
    c_all, y10_all = reverse_dcf(inputs, non_core_pv=non_core_pv, hold_years=0, **ctx2)
    c_lt, _ = reverse_dcf(inputs, non_core_pv=non_core_pv, hold_years=2, **ctx2)
    geo = 1.0
    for g in growth:
        geo *= (1 + g)
    ours_all = geo ** (1 / 10) - 1
    geo_lt = 1.0
    for g in growth[2:]:
        geo_lt *= (1 + g)
    ours_lt = geo_lt ** (1 / 8) - 1
    out["rev_cagr_y1_y10"] = {"ours": round(ours_all * 100, 2), "market_implied": c_all,
                              "implied_y10_revenue": y10_all, "unit": "% CAGR"}
    out["rev_cagr_y3_y10"] = {"ours": round(ours_lt * 100, 2), "market_implied": c_lt,
                              "consensus": consensus.get("rev_cagr_y3_y10"), "unit": "% CAGR (Y1–Y2 held at model)"}
    # v16.5: a solver pinned at its bound is not a market view
    for key, c in (("rev_cagr_y1_y10", c_all), ("rev_cagr_y3_y10", c_lt)):
        if c is not None and (abs(c / 100 - REVERSE_DCF_BOUNDS[0]) < 1e-6 or abs(c / 100 - REVERSE_DCF_BOUNDS[1]) < 1e-6):
            out[key]["note"] = "N/M — solver hit its bound; the price is not reachable by growth alone"
            out[key]["market_implied_nm"] = True
    # v16.5: the growth the market needs depends on the discount rate — show it at both ends of wacc_range
    w_lo, w_hi, w_basis = _wacc_range(inputs)
    for tag, w_alt in (("low", w_lo), ("high", w_hi)):
        try:
            alt = _inputs_at_wacc(inputs, w_alt)
            c_alt, _ = reverse_dcf(alt, non_core_pv=non_core_pv, hold_years=2,
                                   _margins=margins, _offsets=offsets, _engine=engine)
            out["rev_cagr_y3_y10"][f"market_implied_at_wacc_{tag}"] = c_alt
        except Exception:
            out["rev_cagr_y3_y10"][f"market_implied_at_wacc_{tag}"] = None
    out["wacc_range"] = {"low": round(w_lo * 100, 2), "high": round(w_hi * 100, 2), "basis": w_basis}

    # 2. Terminal margin (Y10) — parallel shift of Y3+
    m_impl, shift = implied_terminal_margin(inputs, non_core_pv=non_core_pv, **ctx2)
    out["terminal_margin_y10"] = {"ours": round(margins[-1] * 100, 2),
                                  "market_implied": round(m_impl * 100, 2) if m_impl is not None else None,
                                  "shift_bps": round(shift * 10000, 0) if shift is not None else None,
                                  "consensus": consensus.get("terminal_margin"),
                                  "unit": "% margin (post SBC/lease haircut)",
                                  "note": None if m_impl is not None else "outside ±40pp solve range"}

    # 3. WACC
    be_w = find_breakeven_wacc(inputs, non_core_pv=non_core_pv, **ctx2)
    out["wacc"] = {"ours": round(inputs["wacc"] * 100, 2), "market_implied": be_w, "unit": "%"}
    if be_w is not None and (be_w >= 49.99 or be_w > max(20.0, 2 * inputs["wacc"] * 100)):
        out["wacc"]["note"] = ("N/M — implausible discount rate: the market is pricing different cash flows, "
                               "read the growth/margin rows")
        out["wacc"]["market_implied_nm"] = True
    elif be_w is not None and w_lo * 100 <= be_w <= w_hi * 100:
        out["wacc"]["note"] = "inside the defensible WACC range — the gap is a discount-rate call"

    # 4. Terminal growth
    out["terminal_growth"] = {"ours": round(inputs["terminal_growth"] * 100, 2),
                              "market_implied": find_breakeven_tg(inputs, non_core_pv=non_core_pv, **ctx2), "unit": "%"}

    # 5. RONIC
    r_impl, r_note = implied_ronic(inputs, non_core_pv=non_core_pv, **ctx2)
    out["ronic"] = {"ours": round(inputs.get("ronic", inputs["wacc"]) * 100, 2),
                    "market_implied": round(r_impl * 100, 2) if r_impl is not None else None,
                    "note": r_note, "unit": "%"}
    return out


def gap_waterfall(inputs, consensus_path, non_core_pv=None):
    """Additive attribution of the DCF-vs-market gap (v16.4, E1).

    consensus_path = {"rev_growth": [g1, g2, (g3)], "ebitda_margins": [m1, m2, (m3)]}
      — consensus near-term path (decimals, IFRS-16 reported basis: the engine
      applies the same SBC/lease haircuts to both paths).

    Steps: P0 = our DCF price
           P1 = swap Y1..n growth to consensus
           P2 = + swap Y1..n margins to consensus
           residual = market price − P2 = long-term path (Y(n+1)–Y10), TV, WACC
    Also solves the uniform Y(n+1)–Y10 CAGR that reaches the market price with
    consensus near-term inputs and our margins/WACC/tg/RONIC.
    """
    base = run_dcf(copy.deepcopy(inputs))
    if base.get("status") != "OK":
        return {"status": "FAILED", "reason": base.get("reason")}
    ncpv = base.get("non_core_pv_added", 0.0) if non_core_pv is None else non_core_pv
    p0 = base["implied_price"]
    n = min(len(consensus_path.get("rev_growth", [])), 3)
    steps = [{"step": "DCF (model)", "price": p0, "delta": 0.0}]

    inp1 = copy.deepcopy(inputs)
    for i in range(n):
        inp1["rev_growth"][i]["rate"] = consensus_path["rev_growth"][i]
    r1 = run_dcf(inp1)
    p1 = r1["implied_price"]
    steps.append({"step": f"Y1–Y{n} growth → consensus", "price": p1, "delta": round(p1 - p0, 2)})

    inp2 = copy.deepcopy(inp1)
    nm = min(len(consensus_path.get("ebitda_margins", [])), n)
    for i in range(nm):
        inp2["ebitda_margins"][i]["margin"] = consensus_path["ebitda_margins"][i]
    r2 = run_dcf(inp2)
    p2 = r2["implied_price"]
    steps.append({"step": f"Y1–Y{nm} margin → consensus", "price": p2, "delta": round(p2 - p1, 2)})

    mkt = inputs["share_price"]

    # v16.5 discount-rate step: move WACC toward the market, but only inside wacc_range.
    w_lo, w_hi, w_basis = _wacc_range(inputs)
    w_edge = w_lo if mkt > p2 else w_hi
    price_at = lambda w: run_dcf(_inputs_at_wacc(copy.deepcopy(inp2), w), _skip_solvers=True)["implied_price"]
    p3 = price_at(w_edge)
    closed, w_star = False, None
    if (p2 - mkt) * (p3 - mkt) <= 0:          # market price reachable inside the range
        lo, hi = sorted((inputs["wacc"], w_edge))
        w_star = _bisect(price_at, lo, hi, mkt, tol=1e-5, increasing=False)
        p3, closed = mkt, True
    steps.append({"step": f"WACC {inputs['wacc']*100:.2f}% → {(w_star or w_edge)*100:.2f}% (inside range)",
                  "price": round(p3, 2), "delta": round(p3 - p2, 2)})
    steps.append({"step": f"Long-term path Y{n+1}–Y10 + TV (residual)", "price": mkt, "delta": round(mkt - p3, 2)})

    near = abs(p1 - p0) + abs(p2 - p1)
    rate = abs(p3 - p2)
    lt = abs(mkt - p3)
    mostly = max((("near-term", near), ("discount-rate", rate), ("long-term", lt)), key=lambda x: x[1])[0]

    # Market-implied LT CAGR with consensus near-term
    stripped = r2["inputs"]
    lt_cagr, _ = reverse_dcf(stripped, non_core_pv=ncpv, hold_years=n)
    g_lt = [r["rate"] for r in inputs["rev_growth"]][n:]
    geo = 1.0
    for g in g_lt:
        geo *= (1 + g)
    ours_lt = (geo ** (1 / len(g_lt)) - 1) * 100 if g_lt else None
    return {
        "status": "OK",
        "market_price": mkt,
        "steps": steps,
        "total_gap": round(mkt - p0, 2),
        "total_gap_pct": round((mkt / p0 - 1) * 100, 1) if p0 else None,
        "gap_mostly": mostly,
        "gap_closed_within_wacc_range": closed,
        "wacc_closing_gap_pct": round(w_star * 100, 2) if w_star else None,
        "wacc_range": {"low": round(w_lo * 100, 2), "high": round(w_hi * 100, 2), "basis": w_basis},
        "lt_cagr_market_implied_pct": lt_cagr,
        "lt_cagr_ours_pct": round(ours_lt, 2) if ours_lt is not None else None,
        "near_term_years": n,
    }


def _wacc_range(inputs):
    """(low, high, basis) — inputs['wacc_range'] = {'low','high','basis'} from wacc-capm
    (decimals); default ±75bps around the model WACC, flagged as default."""
    wr = inputs.get("wacc_range") or {}
    w = inputs["wacc"]
    if wr.get("low") is not None and wr.get("high") is not None:
        lo, hi = min(wr["low"], w), max(wr["high"], w)
        return lo, hi, wr.get("basis", "wacc-capm range")
    return w - DEFAULT_WACC_RANGE_HALF_WIDTH, w + DEFAULT_WACC_RANGE_HALF_WIDTH, "default ±75bps (supply wacc_range)"


def _inputs_at_wacc(inputs, w):
    """Copy of inputs at WACC w. RONIC follows WACC when it was WACC-neutral or
    gate-forced; terminal WACC follows when it was not overridden."""
    alt = copy.deepcopy(inputs)
    old = alt["wacc"]
    alt["wacc"] = w
    if alt.get("ronic_basis") in ("default_wacc_neutral", "gate_forced_to_wacc") or alt.get("ronic") is None:
        alt["ronic"] = w
    if alt.get("terminal_wacc") is not None and abs(alt["terminal_wacc"] - old) < 1e-12:
        alt["terminal_wacc"] = w
    return alt


def format_what_must_be_true(w, ccy=""):
    """Compact table for chat/stdout."""
    if not w or w.get("status") != "OK":
        return "  (what-must-be-true unavailable)"
    rows = [
        ("Rev CAGR Y1–Y10", w["rev_cagr_y1_y10"]),
        ("Rev CAGR Y3–Y10 (Y1–2 held)", w["rev_cagr_y3_y10"]),
        ("Terminal margin Y10", w["terminal_margin_y10"]),
        ("WACC", w["wacc"]),
        ("Terminal growth", w["terminal_growth"]),
        ("RONIC", w["ronic"]),
    ]
    lines = [f"  {'Driver':<30} {'Ours':>9} {'Mkt-implied':>12} {'Consensus':>10}"]
    lines.append("  " + "-" * 64)
    for label, d in rows:
        o = d.get("ours"); m = d.get("market_implied"); c = d.get("consensus")
        fo = f"{o:.2f}" if isinstance(o, (int, float)) else "N/A"
        fm = f"{m:.2f}" if isinstance(m, (int, float)) else "N/A"
        fc = f"{c:.2f}" if isinstance(c, (int, float)) else "—"
        note = f"  ({d['note']})" if d.get("note") else ""
        lines.append(f"  {label:<30} {fo:>9} {fm:>12} {fc:>10}{note}")
    # v16.5: growth the market needs at the ends of the defensible WACC range
    lt, wr = w.get("rev_cagr_y3_y10", {}), w.get("wacc_range")
    if wr and ("market_implied_at_wacc_low" in lt):
        f = lambda v: f"{v:.2f}%" if isinstance(v, (int, float)) else "N/A"
        lines.append(f"  Market-implied Y3–Y10 CAGR at WACC {wr['low']:.2f}%: {f(lt.get('market_implied_at_wacc_low'))}"
                     f" · at {wr['high']:.2f}%: {f(lt.get('market_implied_at_wacc_high'))}  [range: {wr['basis']}]")
    return "\n".join(lines)


def format_gap_waterfall(wf, ccy=""):
    if not wf or wf.get("status") != "OK":
        return "  (gap waterfall unavailable)"
    lines = [f"--- GAP WATERFALL: DCF → market ({ccy}) ---"]
    for s in wf["steps"]:
        lines.append(f"  {s['step']:<48} {s['price']:>9.1f}  {s['delta']:>+8.1f}")
    lines.append(f"  Total gap: {wf['total_gap']:+.1f} ({wf['total_gap_pct']:+.1f}%) → mostly {wf.get('gap_mostly', '?')}")
    if wf.get("gap_closed_within_wacc_range"):
        lines.append(f"  ⚠ The whole remaining gap closes at WACC {wf['wacc_closing_gap_pct']}% — inside the defensible "
                     f"range {wf['wacc_range']['low']}–{wf['wacc_range']['high']}%: no fundamental edge on growth/margins.")
    lines.append(f"  LT CAGR Y{wf['near_term_years']+1}–Y10: ours {wf['lt_cagr_ours_pct']}% vs market-implied "
                 f"{wf['lt_cagr_market_implied_pct']}% (at consensus near-term, our margins/WACC/tg/RONIC)")
    return "\n".join(lines)
# ═══════════════════════════════════════════════════════════════════
# v15.2: Tornado sensitivity (pinned 8-variable set)
# ═══════════════════════════════════════════════════════════════════

def _apply_tornado_perturbation(inp, spec, sign):
    """Mutate a (deep-copied) inputs dict in place for one tornado variable.
    sign = +1 (high case) or −1 (low case)."""
    kind = spec["kind"]
    d = spec["delta"] * sign
    if kind == "add_scalar":
        inp[spec["key"]] = inp.get(spec["key"], 0.0) + d
    elif kind == "add_margin_tail":
        for i in range(2, len(inp.get("ebitda_margins", []))):
            inp["ebitda_margins"][i]["margin"] += d
    elif kind == "add_growth_near":
        for i in range(0, min(2, len(inp.get("rev_growth", [])))):
            inp["rev_growth"][i]["rate"] += d
    elif kind == "add_growth_far":
        for i in range(2, len(inp.get("rev_growth", []))):
            inp["rev_growth"][i]["rate"] += d
    elif kind == "scale_non_core_dividend":
        for h in inp.get("non_core_holdings", []):
            h["fy0_dividend_paid"] = h.get("fy0_dividend_paid", 0) * (1 + d)


def _price_for_perturbation(base_inputs, spec, sign):
    inp = copy.deepcopy(base_inputs)
    _apply_tornado_perturbation(inp, spec, sign)
    try:
        out = run_dcf(inp)
        if out.get("status") != "OK":
            return None
        return out.get("implied_price")
    except Exception:
        return None


def build_tornado(inputs, spec=None):
    """v15.2: Pinned 8-variable tornado. Re-runs run_dcf() for low/high of each
    variable and returns variables sorted by absolute price swing.

    The variable set, deltas, and ordering live in TORNADO_SPEC (versioned by
    TORNADO_SPEC_VERSION) so the tornado is reproducible — this replaces the
    previously-referenced-but-missing sensitivity.py script.

    When R9 is active, appends a non-core dividend ±25% variable.
    """
    spec = list(spec or TORNADO_SPEC)
    if inputs.get("non_core_holdings"):
        spec = spec + [{
            "key": "_non_core_div", "kind": "scale_non_core_dividend",
            "delta": 0.25, "label": "Non-core dividend (±25%) [R9]",
        }]

    base = run_dcf(copy.deepcopy(inputs))
    base_price = base.get("implied_price") if base.get("status") == "OK" else None

    rows = []
    for s in spec:
        low = _price_for_perturbation(inputs, s, -1)
        high = _price_for_perturbation(inputs, s, +1)
        swing = None
        if low is not None and high is not None:
            swing = abs(high - low)
        rows.append({
            "label": s["label"],
            "key": s["key"],
            "delta": s["delta"],
            "low_price": round(low, 1) if low is not None else "N/A",
            "high_price": round(high, 1) if high is not None else "N/A",
            "swing": round(swing, 1) if swing is not None else None,
        })

    rows.sort(key=lambda r: (r["swing"] is None, -(r["swing"] or 0)))
    return {
        "base_price": round(base_price, 1) if base_price is not None else "N/A",
        "currency": inputs.get("currency", ""),
        "spec_version": TORNADO_SPEC_VERSION,
        "n_variables": len(rows),
        "variables": rows,
    }


def format_tornado(tornado):
    """Print a text tornado (widest swing first)."""
    ccy = tornado.get("currency", "")
    print(f"\n--- Tornado sensitivity ({tornado['n_variables']} variables, "
          f"base {ccy} {tornado['base_price']}, spec {tornado['spec_version']}) ---")
    print(f"  {'Variable':<42} {'Low':>10} {'High':>10} {'Swing':>10}")
    print("  " + "-" * 74)
    for r in tornado["variables"]:
        sw = f"{r['swing']:,.1f}" if r["swing"] is not None else "N/A"
        print(f"  {r['label']:<42} {str(r['low_price']):>10} {str(r['high_price']):>10} {sw:>10}")


# ═══════════════════════════════════════════════════════════════════
# v14: FCF Bridge construction
# ═══════════════════════════════════════════════════════════════════

def compute_ufcf_fy0(inputs):
    """v15.2: same-period FY0 UFCF — the bridge reconciliation target.

    The pre-v15.2 bridge reconciled to Y1 projected UFCF, contaminating the
    residual and the R8 sign test with one year of growth / ΔWC / capex change.
    This recomputes UFCF for FY0 itself so the reconciliation is same-period.

    Priority:
      1. explicit inputs['ufcf_fy0']  (analyst-supplied number)
      2. derived from inputs['fy0_actuals'] = {ebitda, da, capex, dnwc[, tax_rate]}
      3. None  → caller falls back to Y1 (advisory, non-binding)

    Returns (ufcf_fy0_or_None, basis_str).
    """
    if inputs.get("ufcf_fy0") is not None:
        return float(inputs["ufcf_fy0"]), "explicit"
    fa = inputs.get("fy0_actuals")
    if fa and all(k in fa for k in ("ebitda", "da", "capex", "dnwc")):
        t = fa.get("tax_rate", inputs.get("tax_rate", 0.25))
        # v16.4: same-basis EBITDA — rent-as-opex always; SBC only under cash_cost
        sbc_cash = (inputs.get("modelling_options") or {}).get("sbc") == "cash_cost"
        ebitda_adj = fa["ebitda"] - (fa.get("lease_cash_cost", 0) or 0) - ((fa.get("sbc", 0) or 0) if sbc_cash else 0)
        ufcf = ebitda_adj * (1 - t) + fa["da"] * t - fa["capex"] - fa["dnwc"]
        return float(ufcf), "derived_from_fy0_actuals"
    return None, "unavailable"


def build_fcf_bridge(state, inputs):
    """Build FCF reconciliation bridge: Reported FCF FY0 → Computed UFCF.
    Returns dict with lines, residual, ok flag.

    v15.1:
      - R8 sign-aware unlevering: uses signed atx_net from net_interest_position_fy0.
        Halts with violation if observed UFCF direction disagrees with net interest sign.
      - R9 dividend strip: subtracts non-core dividends received from reported FCF
        before reconciling to operating UFCF (prevents double-count: dividends-received
        are in reported FCF but R9 values them separately via PV).
    """
    reported = inputs.get("reported_fcf_fy0", 0)
    if reported == 0:
        return {
            "status": "SKIPPED",
            "reason": "No reported_fcf_fy0 in inputs",
        }

    tax = inputs["tax_rate"]
    lines = []

    # v15.1 — R8: sign-aware interest unlevering
    nip = inputs.get("net_interest_position_fy0") or compute_net_interest_position(inputs)
    atx_net = nip.get("atx_net", 0)

    # Backwards compatibility: if old single-field interest_expense_fy0 used and no nip
    if atx_net == 0 and inputs.get("interest_expense_fy0", 0) != 0 and nip.get("interest_expense") == 0:
        # Old-style input — treat as net debt company
        legacy_interest = inputs["interest_expense_fy0"]
        atx_net = legacy_interest * (1 - tax)
        nip = {**nip, "interest_expense": legacy_interest, "atx_net": atx_net, "net": legacy_interest,
               "bridge_direction": "UFCF > FCF (legacy field, R8 sign assumed positive)"}

    if atx_net != 0:
        lines.append({
            "label": "ATX net interest (R8 sign-aware)",
            "amount": round(atx_net, 1),
            "direction": "+" if atx_net > 0 else "−",
            "source": "computed",
            "explanation": (f"Unlevering: net interest = {nip.get('interest_expense', 0):.0f} expense "
                            f"− {nip.get('interest_income', 0):.0f} income = {nip.get('net', 0):+.0f}; "
                            f"× (1 − {tax:.0%}) = {atx_net:+.0f}m. Direction: {nip.get('bridge_direction', '?')}"),
        })

    # Standard optional lines (v15)
    optional_lines = [
        ("lease_cash_adjustment_fy0", "Lease cash adjustment (rent-as-opex)", "filing",
         "SIGNED: negative when the reported FCF definition excludes lease payments (post-IFRS16 OCF−capex) — "
         "subtract principal+interest so FCF is rent-inclusive like the model UFCF; 0 if already deducted"),
        ("restructuring_cash_fy0", "Restructuring cash outflow", "filing",
         "Non-recurring restructuring removed from FCF"),
        ("pension_topup_fy0", "Pension cash top-up (above service cost)",
         "filing", "Non-recurring top-up removed from FCF"),
        ("acquisition_cash_in_fcf_fy0", "Acquisition cash classified as capex",
         "filing", "M&A cash removed if classified as capex"),
        ("capitalised_rd_fy0", "Capitalised R&D adjustment",
         "filing", "If option 2 = capitalise_and_amortise"),
        ("contract_wc_fy0", "Contract WC items",
         "filing", "If option 5 = extended NWC"),
        ("sbc_fy0", "SBC adjustment",
         "filing", "If option 4 = cash_cost"),
        ("other_reconcile_fy0", "Other reconciling items",
         "computed", "Documented item-by-item"),
    ]
    for key, label, source, default_expl in optional_lines:
        val = inputs.get(key, 0)
        if val:
            lines.append({
                "label": label,
                "amount": round(val, 1),
                "direction": "+" if val > 0 else "−",
                "source": source,
                "explanation": inputs.get(f"{key}_note", default_expl),
            })

    # v15.1 — R9: strip non-core dividends from reported FCF basis
    # Parent reported FCF includes inbound dividends from associates/captives/subs.
    # The DCF will value those separately via R9 PV; subtract here to avoid double-count.
    non_core = inputs.get("non_core_holdings", [])
    non_core_div_strip = 0
    if non_core:
        non_core_div_strip = sum(h.get("fy0_dividend_paid", 0) for h in non_core)
        if non_core_div_strip > 0:
            holdings_names = ", ".join(h.get("name", "?") for h in non_core)
            lines.append({
                "label": "− Σ dividends received from non-core holdings (R9)",
                "amount": round(-non_core_div_strip, 1),
                "direction": "−",
                "source": "filing",
                "explanation": (f"R9 strip: parent reported FCF includes €{non_core_div_strip:.0f}m of inbound "
                                f"dividends from {holdings_names}. These are valued separately via PV(dividend stream). "
                                f"Stripped here to prevent double-count."),
            })

    sum_adjustments = sum(line["amount"] for line in lines)
    proxy_ufcf = reported + sum_adjustments
    actual_ufcf_y1 = state["yearly"][0]["ufcf"]

    # v15.2 — reconcile SAME-PERIOD: target = computed UFCF_FY0, not Y1.
    ufcf_fy0, ufcf_fy0_basis = compute_ufcf_fy0(inputs)
    if ufcf_fy0 is not None:
        target_ufcf = ufcf_fy0
        reconciliation_basis = f"same_period_fy0 ({ufcf_fy0_basis})"
        gates_binding = True
    else:
        # Fallback: Y1 (legacy). Gates downgraded to ADVISORY — the FY0->Y1
        # growth delta cannot be separated from reconciliation noise.
        target_ufcf = actual_ufcf_y1
        reconciliation_basis = "y1_fallback_ADVISORY (no fy0 UFCF supplied)"
        gates_binding = False

    residual = target_ufcf - proxy_ufcf
    residual_pct = abs(residual) / abs(reported) if reported else float("inf")
    ok = residual_pct <= 0.10

    # v15.2 — R8 sign check on the SAME-PERIOD figure (or Y1 advisory fallback)
    r8_check = enforce_ufcf_sign_rule(target_ufcf, reported, atx_net)
    r8_check["binding"] = gates_binding
    r8_check["basis"] = reconciliation_basis
    if not gates_binding:
        r8_check["passed"] = True  # never halt on the advisory fallback
        r8_check["message"] = (
            "R8 ADVISORY (no FY0 UFCF supplied — evaluated on Y1, growth-contaminated). "
            "Provide inputs['ufcf_fy0'] or inputs['fy0_actuals'] to make this binding. "
            + r8_check.get("message", "")
        )

    # v15.2 — FY0 -> Y1 operating growth step (informational, NOT gated)
    growth_step = {
        "ufcf_fy0": round(ufcf_fy0, 1) if ufcf_fy0 is not None else None,
        "ufcf_y1": actual_ufcf_y1,
        "delta": round(actual_ufcf_y1 - ufcf_fy0, 1) if ufcf_fy0 is not None else None,
        "delta_pct": round((actual_ufcf_y1 / ufcf_fy0 - 1), 4) if ufcf_fy0 else None,
        "note": ("FY0->Y1 step = operating growth + ΔWC + capex change. Expected and "
                 "thesis-driven; excluded from the reconciliation residual and the R8 sign test."),
    }

    bridge = {
        "as_of": "FY0 reported, Y1 computed (one-year offset)",
        "reported_fcf_fy0": reported,
        "lines": lines,
        "proxy_computed_ufcf": round(proxy_ufcf, 1),
        "actual_computed_ufcf_y1": actual_ufcf_y1,
        # v15.2 — same-period reconciliation
        "target_ufcf_fy0": round(target_ufcf, 1),
        "reconciliation_basis": reconciliation_basis,
        "gates_binding": gates_binding,
        "growth_step_fy0_to_y1": growth_step,
        "residual": round(residual, 1),
        "residual_pct_of_reported": round(residual_pct, 4),
        "residual_ok": ok,
        "tolerance_pct": 0.10,
        # v15.1 additions:
        "r8_sign_check": r8_check,
        "r9_dividend_strip": {
            "active": bool(non_core_div_strip > 0),
            "amount": round(non_core_div_strip, 1),
            "holdings": [h.get("name", "?") for h in non_core] if non_core else [],
        },
    }

    consensus = inputs.get("consensus_snapshot", {})
    consensus_ufcf_y1 = (consensus.get("ufcf") or {}).get("Y1") if consensus else None
    if consensus_ufcf_y1:
        # v15.1: unlever consensus FCF with R8 sign (atx_net) AND strip non-core dividends
        implied_consensus_ufcf = consensus_ufcf_y1 + atx_net - non_core_div_strip
        delta = actual_ufcf_y1 - implied_consensus_ufcf
        delta_pct = delta / implied_consensus_ufcf if implied_consensus_ufcf else 0
        bridge["consensus_comparison"] = {
            "consensus_fcf_y1": consensus_ufcf_y1,
            "atx_net_y1_applied": round(atx_net, 1),
            "non_core_dividend_strip_y1": round(non_core_div_strip, 1),
            "implied_consensus_ufcf_y1": round(implied_consensus_ufcf, 1),
            "model_ufcf_y1": actual_ufcf_y1,
            "delta": round(delta, 1),
            "delta_pct": round(delta_pct, 4),
        }

    return bridge


# ═══════════════════════════════════════════════════════════════════
# Formatted output
# ═══════════════════════════════════════════════════════════════════

def format_dcf_output(output, inputs):
    """Print formatted DCF results to stdout (v16.4)."""
    ccy = inputs["currency"]
    engine = output.get("engine", "ebitda_native")
    tb = output.get("terminal_block", {})

    print(f"\n{'='*100}")
    print(f"  DCF — {inputs['company']} ({inputs['ticker']})  [engine: {engine}, {output.get('engine_version', '?')}, leases: rent-as-opex]")
    tax_y1 = output["yearly"][0].get("tax_rate", inputs["tax_rate"])
    print(f"  WACC: {inputs['wacc']*100:.1f}%  |  tg: {inputs['terminal_growth']*100:.1f}%  |  RONIC: {tb.get('ronic', inputs['wacc'])*100:.1f}% [{tb.get('ronic_basis','?')}]  |  Tax Y1: {tax_y1*100:.1f}%")
    print(f"  Base revenue ({inputs.get('base_revenue_fy','FY0')}): {ccy} {inputs['base_revenue']:,.0f}m")
    conv = output.get("discount_convention", "uniform_t_minus_0_5")
    if conv == "calendar_aware":
        do = output["discount_offsets"]
        print(f"  Discounting: calendar-aware | analysis {do['analysis_date']} | Y1 mid-CF {do['mid_year_offsets'][0]:.3f}y | TV {do['terminal_offset']:.3f}y")
    else:
        print(f"  Discounting: {conv}")
    if output.get("terminal_wacc_used") and output["terminal_wacc_used"] != inputs["wacc"]:
        print(f"  Terminal WACC override: {output['terminal_wacc_used']*100:.1f}% (Y11+)")
    print(f"{'='*100}")

    print(f"\n{'Yr':<4} {'Rev':>9} {'Grw%':>6} {'Mg%':>6} {'EBITDA':>9} {'EBIT':>9} {'NOPAT':>9} {'D&A':>8} {'Capex':>9} {'dWC':>7} {'UFCF':>9} {'DF':>7} {'PV':>9}")
    print("-" * 112)
    for r in output["yearly"]:
        print(f"Y{r['year']:<3} {r['revenue']:>9,.0f} {r['rev_growth_pct']:>5.1f}% {r['ebitda_margin_pct']:>5.1f}% "
              f"{r['ebitda']:>9,.0f} {r['ebit']:>9,.0f} {r['nopat']:>9,.0f} {r['da']:>8,.0f} {r['capex']:>9,.0f} "
              f"{r['dwc']:>7,.0f} {r['ufcf']:>9,.0f} {r['discount_factor']:>6.4f} {r['pv_ufcf']:>9,.0f}")

    acq_total = -sum(r.get("acquisitions", 0) for r in output["yearly"])
    if acq_total:
        print(f"  Acquisition spend Y1–Y10 (in UFCF): {acq_total:,.0f}")

    fs = output.get("fade_stage") or {}
    if fs.get("years"):
        rows = fs["rows"]
        print(f"\n--- Fade stage Y11–Y{10 + fs['years']} (CAP {tb.get('cap_years')}y; growth {rows[0]['growth_pct']:.1f}% → "
              f"{rows[-1]['growth_pct']:.1f}%, reinvestment g/RONIC) ---")
        print(f"  PV(fade stage):            {fs['pv']:>13,.0f}")

    print(f"\n--- Terminal value (value-driver) ---")
    print(f"  NOPAT at TV start:         {tb.get('nopat_y11', 0):>13,.0f}")
    print(f"  Reinvestment rate tg/RONIC: {tb.get('reinvestment_rate', 0):>12.1%}")
    print(f"  Terminal FCF:              {tb.get('terminal_fcf', 0):>13,.0f}")
    print(f"  TV:                        {output['terminal_value']:>13,.0f}   (Gordon on UFCF10 would give {output.get('terminal_value_gordon_equivalent', 0):,.0f})")
    if tb.get("implied_exit_ev_ebitda"):
        print(f"  Implied exit EV/EBITDA Y10: {tb['implied_exit_ev_ebitda']:>11.1f}x   (rent-as-opex EBITDA {tb.get('y10_ebitda', 0):,.0f})")
    print(f"  PV(TV):                    {output['pv_terminal_value']:>13,.0f}   (value beyond Y10 = {output['tv_pct_of_ev']:.1f}% of operating EV)")

    print(f"\n--- Bridge to Equity ({ccy}m) ---")
    print(f"  Σ PV of UFCFs (Y1–Y10):    {output['sum_pv_ufcf']:>13,.0f}")
    if (output.get("fade_stage") or {}).get("years"):
        print(f"  + PV(fade stage):          {output['fade_stage']['pv']:>13,.0f}")
    print(f"  + PV(TV):                  {output['pv_terminal_value']:>13,.0f}")
    print(f"  = EV (operating):          {output['enterprise_value_operating']:>13,.0f}")
    if output.get("non_core_pv_added"):
        print(f"  + PV(non-core dividends):  {output['non_core_pv_added']:>13,.0f}   [R9]")
        print(f"  = EV (total):              {output['enterprise_value']:>13,.0f}")
    print(f"  − Net debt (operating):    {-output['net_debt']:>13,.0f}")
    if output.get("pension_deficit"):
        print(f"  − Pension deficit:         {-output['pension_deficit']:>13,.0f}")
    if output.get("lease_liabilities_memo"):
        print(f"  (memo) Lease liabilities:  {output['lease_liabilities_memo']:>13,.0f}   NOT deducted — rent already in margins")
    print(f"  − Minorities:              {-output['minorities']:>13,.0f}")
    for c in (output.get("other_claims") or []):
        if isinstance(c, dict):
            print(f"  − {c.get('label', 'Other claim')[:24]:<24} {-float(c.get('amount', 0)):>13,.0f}")
    print(f"  = Equity value:            {output['equity_value']:>13,.0f}")
    print(f"  ÷ Shares:                  {output['shares']:>13,.1f}m")
    print(f"  = Implied price:       {ccy} {output['implied_price']:>9.1f}")
    print(f"  Current price:         {ccy} {output['current_price']}")
    print(f"  Upside:                {output['upside_pct']:>+9.1f}%")
    if output["tv_pct_of_ev"] > 75:
        print(f"  ⚠ TV = {output['tv_pct_of_ev']:.1f}% of operating EV (>75%)")

    print(f"\n--- WHAT MUST BE TRUE at {ccy} {output['current_price']} (each driver solved holding the others at model) ---")
    print(format_what_must_be_true(output.get("what_must_be_true"), ccy))

    gpf = output.get("growth_paid_for")
    if gpf:
        print(f"\n--- GROWTH PAID FOR? (explicit period) ---")
        print(f"  {gpf['message']}")

    # Calibration vs consensus 12M target
    consensus = inputs.get("consensus_snapshot") or output.get("consensus_snapshot") or {}
    tgt = consensus.get("target_price_12m") or {}
    tgt_val = tgt.get("value") if isinstance(tgt, dict) else tgt
    if not tgt_val:
        tgt_val = consensus.get("target_price") or consensus.get("price_target")
    cur = output.get("current_price") or inputs.get("share_price")
    implied = output.get("implied_price")
    print(f"\n--- CALIBRATION: DCF vs consensus 12M target ---")
    if tgt_val and implied and cur:
        print(f"  DCF {ccy} {implied:.1f} ({(implied/cur-1)*100:+.1f}%) vs consensus {ccy} {tgt_val:.1f} "
              f"({(tgt_val/cur-1)*100:+.1f}%) [{consensus.get('analyst_count','?')} analysts, {consensus.get('as_of_date','?')}] "
              f"→ DCF vs target {(implied/tgt_val-1)*100:+.1f}%. One-line gap reason required in chat.")
    else:
        print(f"  ⚠ No consensus 12M target in consensus_snapshot.target_price_12m — line omitted.")

    # Modelling decisions
    opts = output.get("modelling_options") or {}
    print(f"\n--- MODELLING DECISIONS APPLIED ---")
    DEFAULTS = {"engine": "ebitda_native", "sbc": "non_cash_addback", "nwc_scope": "trade_only", "non_core_treatment": "n_a"}
    triggers = {}
    for t in (opts.get("triggers_at_run_time") or []):
        if isinstance(t, dict):
            triggers[t.get("option")] = t
        elif isinstance(t, (list, tuple)) and len(t) >= 2:
            triggers[t[0]] = {"reason": t[1]}
    overrides = set()
    for o in (opts.get("user_overrides") or []):
        overrides.add(o.get("option") if isinstance(o, dict) else o)
    any_non_default = False
    for key in ["engine", "sbc", "nwc_scope", "non_core_treatment"]:
        if key not in opts:
            continue
        v = opts[key]
        if v == DEFAULTS[key] and key not in overrides:
            continue
        any_non_default = True
        status = "USER OVERRIDE" if key in overrides else ("TRIGGERED" if key in triggers else "NON-DEFAULT")
        print(f"  {key:<20}: {v:<20} [⚠ {status}]")
        t = triggers.get(key)
        if t:
            if t.get("reason"):
                print(f"      ↳ Why: {t['reason']}")
            if t.get("impact"):
                print(f"      ↳ Impact: {t['impact']}")
    if output.get("sbc_adjustment"):
        print(f"  ► SBC cash-cost haircut: −{output['sbc_adjustment']['ebitda_margin_haircut_ppt']:.2f}ppt on every EBITDA margin")
    if output.get("lease_adjustment"):
        print(f"  ► Lease cash-cost haircut (rent-as-opex): −{output['lease_adjustment']['ebitda_margin_haircut_ppt']:.2f}ppt on every EBITDA margin; lease liability NOT in bridge")
    else:
        print(f"  ► Leases: rent-as-opex — lease_cost_pct_of_revenue = 0 (margins supplied already rent-inclusive, or no leases); lease liability NOT in bridge")
    if output.get("ronic_gate_message"):
        print(f"  ► {output['ronic_gate_message']}")
    cp = output.get("cycle_position")
    if cp:
        print(f"  ► CYCLE POSITION: {cp['status']} — FY0 margin {cp['fy0_margin']:.1%} vs through-cycle {cp['through_cycle_margin']:.1%} ({cp['spread_bps']:+.0f}bps)")
    bridge = output.get("fcf_bridge", {}) or {}
    r8 = bridge.get("r8_sign_check")
    if r8:
        mark = "✓" if r8.get("passed") else "⚠"
        print(f"  {mark} R8 (advisory): {r8.get('observed_direction','?')} expected {r8.get('expected_direction','?')} (atx_net={r8.get('atx_net',0):+.0f}m)")
    if not any_non_default and not output.get("sbc_adjustment"):
        print(f"  All sector defaults.")

    # R9 block
    nca = output.get("non_core_holdings")
    if nca and nca.get("active"):
        print(f"\n--- NON-CORE HOLDINGS (R9) ---")
        strip = output.get("non_core_holdings_strip", {})
        if strip.get("applied"):
            tot = strip.get("totals", {})
            print(f"  Stripped: revenue {tot.get('revenue_stripped',0):,.0f} | EBITDA {tot.get('ebitda_stripped',0):,.0f} | "
                  f"capex {tot.get('capex_stripped',0):,.0f} | debt {tot.get('debt_stripped',0):,.0f} excluded from bridge")
        for h in nca.get("holdings", []):
            pv = h["dividend_pv"]
            print(f"  • {h['name']} ({h['type']}): div FY0 {h['fy0_dividend']:,.0f} → PV {pv['pv_total']:,.0f} (g={pv['g_applied']:.1%}, r={pv['r_applied']:.1%})")
            bs = h.get("balance_sheet_info", {})
            if bs.get("carrying_value") or bs.get("fair_value"):
                print(f"      ℹ INFO (not in EV): carrying {bs.get('carrying_value') or 0:,.0f} | look-through FV {bs.get('fair_value') or 0:,.0f}")
            m = h.get("monetization_overlay", {})
            if m.get("active"):
                print(f"      Bull overlay: {m['probability']:.0%} × FV {m['fair_value']:,.0f} × (1−{m['friction']:.0%}) = {m['value']:,.0f}")
        print(f"  TOTAL non-core PV (base): {nca['total_base_pv']:,.0f} — added to EV")
        dc = output.get("non_core_double_count_check", {})
        if dc.get("violations"):
            print(f"  ⛔ R9 DOUBLE-COUNT VIOLATIONS:")
            for v in dc["violations"]:
                print(f"      • [{v['type']}] {v['detail']}")

    if output.get("modelling_options_hash"):
        print(f"\n  Reproducibility hash: {output['modelling_options_hash']}")
    print(f"\n{'='*100}")

# ═══════════════════════════════════════════════════════════════════
# v15: Quality / ROIC / CAP / Capital Allocation
# ═══════════════════════════════════════════════════════════════════

def compute_roic_history(financials, tax_rate, wacc):
    """
    ROIC over up to a 5-year window (FY-4..FY0) — v16.4 rent-as-opex basis.

    financials: dict keyed "FY-4".."FY0" with sub-keys
        ebit, total_debt, total_equity, cash, goodwill
        [lease_interest — optional; subtracted from EBIT so NOPAT is on the same
         rent-as-opex basis as the DCF. If absent while lease_liabilities > 0 a
         note is raised (ROIC modestly overstated).]

    Invested capital EX-leases:  IC = total_debt + total_equity − cash
    NOPAT = (EBIT − lease_interest) × (1 − t)

    Incremental ROIC (gate statistic): POOLED over the last 3 years of change,
    ΔNOPAT(FY-3→FY0) / ΔIC(FY-3→FY0) — or the longest span available if <4 FYs.
    Per-year series is information only (single-year ratios are too noisy to gate).
    """
    out = {"history": {}}
    ics_incl, ics_ex, nopats, labels = [], [], [], []
    lease_note = False

    for fy in ["FY-4", "FY-3", "FY-2", "FY-1", "FY0"]:
        f = financials.get(fy)
        if not f:
            continue
        li = f.get("lease_interest", 0) or 0
        if f.get("lease_liabilities", 0) and "lease_interest" not in f:
            lease_note = True
        ic_incl = f["total_debt"] + f["total_equity"] - f["cash"]
        ic_ex = ic_incl - f.get("goodwill", 0)
        nopat = (f["ebit"] - li) * (1 - tax_rate)
        out["history"][fy] = {"ebit": f["ebit"], "lease_interest": li, "nopat": round(nopat, 0),
                              "invested_capital_incl_gw": round(ic_incl, 0),
                              "invested_capital_ex_gw": round(ic_ex, 0)}
        ics_incl.append(ic_incl); ics_ex.append(ic_ex); nopats.append(nopat); labels.append(fy)

    out["window_years"] = len(nopats)
    out["ic_basis"] = "ex_leases_rent_as_opex"
    if lease_note:
        out["ic_leases_note"] = ("⚠ lease_interest absent for ≥1 FY with leases — NOPAT not lease-adjusted; "
                                 "ROIC modestly overstated for lease-heavy businesses.")
    if len(nopats) < 2:
        out["status"] = "INSUFFICIENT_DATA"
        return out

    roics_incl, roics_ex = [], []
    for i in range(1, len(nopats)):
        a_incl = (ics_incl[i] + ics_incl[i-1]) / 2
        a_ex = (ics_ex[i] + ics_ex[i-1]) / 2
        if a_incl > 0:
            r = nopats[i] / a_incl; roics_incl.append(r)
            out["history"][labels[i]]["roic_incl_gw"] = round(r, 4)
        if a_ex > 0:
            r = nopats[i] / a_ex; roics_ex.append(r)
            out["history"][labels[i]]["roic_ex_gw"] = round(r, 4)

    if roics_incl:
        out["avg_roic_incl_gw"] = round(sum(roics_incl) / len(roics_incl), 4)
        out["spread_to_wacc_bps_incl"] = round((out["avg_roic_incl_gw"] - wacc) * 10000, 0)
    if roics_ex:
        out["avg_roic_ex_gw"] = round(sum(roics_ex) / len(roics_ex), 4)
        out["spread_to_wacc_bps_ex"] = round((out["avg_roic_ex_gw"] - wacc) * 10000, 0)

    # Pooled incremental ROIC — last 3 years of change (FY-3→FY0) or longest available
    span = min(3, len(nopats) - 1)
    d_n = nopats[-1] - nopats[-1 - span]
    d_ic = ics_incl[-1] - ics_incl[-1 - span]
    out["incremental_span_years"] = span
    if d_ic > 0:
        out["incremental_roic"] = round(d_n / d_ic, 4)
        out["incremental_destroys_value"] = out["incremental_roic"] < wacc
    else:
        out["incremental_roic"] = None
        out["incremental_destroys_value"] = None
        out["incremental_note"] = "Net capital returned over the span — incremental ROIC undefined (RONIC gate inert)"

    # Per-year series — INFORMATION ONLY (v16.4: not a gate statistic)
    series = []
    for i in range(1, len(nopats)):
        dn = nopats[i] - nopats[i-1]; dic = ics_incl[i] - ics_incl[i-1]
        if dic > 0:
            series.append({"fy": labels[i], "incremental_roic": round(dn / dic, 4), "below_wacc": dn / dic < wacc})
        else:
            series.append({"fy": labels[i], "incremental_roic": None, "below_wacc": False, "note": "ΔIC ≤ 0"})
    out["incremental_series"] = series
    out["incremental_series_note"] = "information only — the RONIC gate uses the pooled figure"

    if len(roics_incl) >= 2:
        mean = sum(roics_incl) / len(roics_incl)
        if mean > 0:
            var = sum((r - mean) ** 2 for r in roics_incl) / len(roics_incl)
            out["roic_cv"] = round(var ** 0.5 / mean, 4)

    out["wacc"] = wacc
    return out
def compute_quality_score(roic_data, moat_subscores, reinvestment_runway,
                          capital_allocation_score, balance_sheet_data):
    """
    Compute 6-dimension quality score (1-10 each, composite is mean).

    Inputs:
    - roic_data: from compute_roic_history()
    - moat_subscores: list of 5 sub-scores (1-5 each) for switching/network/cost/intangible/scale
    - reinvestment_runway: integer 1-10 (qualitative input)
    - capital_allocation_score: integer 1-10 (from capital-allocation skill)
    - balance_sheet_data (v16.1, Dimension 6): dict with
        net_debt_incl_leases  (total_debt + lease_liabilities − cash; negative = net cash)
        ebitda                (FY0 normalised EBITDA)
        ebit                  (FY0 IFRS EBIT)
        interest_expense      (FY0 gross)

    v16.1 — Dimension 6 changed from "earnings predictability" (which ~duplicated
    Dimension 2's volatility signal) to "balance-sheet resilience" (ND/EBITDA +
    interest coverage), previously absent from the quality composite entirely.
    Legacy dicts with revenue_cv_5y/ebitda_margin_cv_5y are still accepted
    (old state reload) and score the legacy way, with a warning field.
    """
    scores = {}

    # Dimension 1: ROIC level vs WACC
    spread_bps = roic_data.get("spread_to_wacc_bps_incl", 0)
    if spread_bps > 2000:    scores["roic_vs_wacc"] = 10
    elif spread_bps > 1500:  scores["roic_vs_wacc"] = 9
    elif spread_bps > 1000:  scores["roic_vs_wacc"] = 8
    elif spread_bps > 700:   scores["roic_vs_wacc"] = 7
    elif spread_bps > 500:   scores["roic_vs_wacc"] = 6
    elif spread_bps > 300:   scores["roic_vs_wacc"] = 5
    elif spread_bps > 100:   scores["roic_vs_wacc"] = 4
    elif spread_bps > 0:     scores["roic_vs_wacc"] = 3
    elif spread_bps > -200:  scores["roic_vs_wacc"] = 2
    else:                    scores["roic_vs_wacc"] = 1

    # Dimension 2: ROIC stability (CV)
    cv = roic_data.get("roic_cv", 0.5)
    if cv < 0.05:    scores["roic_stability"] = 10
    elif cv < 0.10:  scores["roic_stability"] = 9
    elif cv < 0.15:  scores["roic_stability"] = 8
    elif cv < 0.20:  scores["roic_stability"] = 7
    elif cv < 0.25:  scores["roic_stability"] = 6
    elif cv < 0.30:  scores["roic_stability"] = 5
    elif cv < 0.40:  scores["roic_stability"] = 4
    elif cv < 0.50:  scores["roic_stability"] = 3
    elif cv < 0.75:  scores["roic_stability"] = 2
    else:            scores["roic_stability"] = 1

    # Dimension 3: Moat (sum of 5 sub-scores out of 5 = 0-25, mapped to 2-10)
    moat_total = sum(moat_subscores) if len(moat_subscores) == 5 else 12
    if moat_total >= 20:    scores["moat"] = 10
    elif moat_total >= 17:  scores["moat"] = 8
    elif moat_total >= 14:  scores["moat"] = 6
    elif moat_total >= 11:  scores["moat"] = 4
    else:                   scores["moat"] = 2

    # Dimension 4: Reinvestment runway (direct input)
    scores["reinvestment_runway"] = max(1, min(10, int(reinvestment_runway)))

    # Dimension 5: Capital allocation (loaded from skill)
    scores["capital_allocation"] = max(1, min(10, int(capital_allocation_score)))

    # Dimension 6 (v16.1): Balance-sheet resilience
    legacy_warning = None
    if balance_sheet_data and "revenue_cv_5y" in balance_sheet_data:
        # Legacy predictability dict (pre-v16.1 state reload) — score old way, warn.
        rev_cv = balance_sheet_data.get("revenue_cv_5y", 0.3)
        margin_cv = balance_sheet_data.get("ebitda_margin_cv_5y", 0.2)
        pred = 1 / (1 + 0.5 * rev_cv + 1.0 * margin_cv)
        scores["earnings_predictability"] = max(1, min(10, round(pred * 10)))
        legacy_warning = ("⚠ Dim 6 scored with LEGACY earnings-predictability inputs "
                          "(pre-v16.1 state). Supply balance_sheet_data for v16.1 scoring.")
    else:
        bs = balance_sheet_data or {}
        nd = bs.get("net_debt", bs.get("net_debt_incl_leases"))  # v16.4: ex-leases (rent-as-opex)
        ebitda = bs.get("ebitda", 0)
        ebit = bs.get("ebit", 0)
        int_exp = bs.get("interest_expense", 0)
        if nd is None or ebitda <= 0:
            scores["balance_sheet"] = 5  # neutral, insufficient data
        else:
            nd_ebitda = nd / ebitda
            if nd <= 0:              bs_score = 10   # net cash (ex-leases)
            elif nd_ebitda < 0.5:    bs_score = 9
            elif nd_ebitda < 1.0:    bs_score = 8
            elif nd_ebitda < 1.5:    bs_score = 7
            elif nd_ebitda < 2.0:    bs_score = 6
            elif nd_ebitda < 2.5:    bs_score = 5
            elif nd_ebitda < 3.0:    bs_score = 4
            elif nd_ebitda < 4.0:    bs_score = 3
            elif nd_ebitda < 5.0:    bs_score = 2
            else:                    bs_score = 1
            # Interest coverage modifier (EBIT / gross interest expense)
            if int_exp > 0 and ebit > 0:
                coverage = ebit / int_exp
                if coverage < 2:   bs_score -= 2
                elif coverage < 4: bs_score -= 1
            elif int_exp > 0 and ebit <= 0:
                bs_score -= 2
            scores["balance_sheet"] = max(1, min(10, bs_score))

    composite = sum(scores.values()) / 6
    composite_rounded = round(composite, 1)

    if composite_rounded >= 8.0:
        tier = "HIGH QUALITY"
    elif composite_rounded >= 6.5:
        tier = "STANDARD"
    elif composite_rounded >= 5.0:
        tier = "LOW QUALITY"
    else:
        tier = "VALUE TRAP RISK"

    result = {
        "scores": scores,
        "composite": composite_rounded,
        "tier": tier,
        "threshold_used": 6.5,
    }
    if legacy_warning:
        result["dim6_legacy_warning"] = legacy_warning
    return result


def compute_capital_allocation_score(channels):
    """
    Capital allocation track record composite.

    channels: dict with keys reinvest, m_and_a, dividends, buybacks, debt
              each value = {"score": 1-10, "weight": 0-1}
    """
    total_weight = sum(c["weight"] for c in channels.values())
    if total_weight == 0:
        return 5  # neutral

    weighted = sum(c["score"] * c["weight"] for c in channels.values()) / total_weight
    return round(weighted, 1)


def project_share_count(starting_shares, share_price_y, fcf_y, buyback_pct_of_fcf):
    """
    Project per-year share count given forward buyback intent.

    Simplification: assumes buybacks executed at year-average price.
    """
    shares = [starting_shares]
    for y in range(len(fcf_y)):
        if buyback_pct_of_fcf[y] > 0 and share_price_y[y] > 0:
            buyback_value = fcf_y[y] * buyback_pct_of_fcf[y]
            shares_bought = buyback_value / share_price_y[y]
            shares.append(shares[-1] - shares_bought)
        else:
            shares.append(shares[-1])
    return shares


def check_base_rates(inputs):
    """
    Run base-rate plausibility checks against assumption table.
    Returns list of flag dicts (may be empty if all assumptions in median band).

    References: Mauboussin 'The Base Rate Book' 2016, Bessembinder 2018.
    """
    flags = []
    rev_growth = [r["rate"] for r in inputs["rev_growth"]]
    base_rev = inputs.get("base_revenue", 0)
    margins = [m["margin"] for m in inputs["ebitda_margins"]]

    # Check 1: Y1-Y5 average growth persistence (Mauboussin Table 1)
    avg_5y = sum(rev_growth[:5]) / 5
    if base_rev > 1000:  # >$1bn revenue cohort
        if 0.20 <= avg_5y:
            flags.append({
                "param": "rev_growth_y1_y5",
                "value": round(avg_5y, 4),
                "base_rate_pct": 0.02,
                "source": "Mauboussin Base Rate Book 2016, Table 1",
                "message": f"Y1-Y5 avg growth {avg_5y:.0%} implies top-2% growth persistence among $1bn+ companies."
            })
        elif 0.15 <= avg_5y < 0.20:
            flags.append({
                "param": "rev_growth_y1_y5",
                "value": round(avg_5y, 4),
                "base_rate_pct": 0.04,
                "source": "Mauboussin Base Rate Book 2016, Table 1",
                "message": f"Y1-Y5 avg growth {avg_5y:.0%} implies top-4% growth persistence. Defensible only with documented compounder evidence."
            })

    # Check 2: Margin expansion (Mauboussin Table 5)
    if len(margins) >= 3:
        expansion_bps = (margins[2] - margins[0]) * 10000
        if expansion_bps > 200:
            flags.append({
                "param": "ebitda_margin_3y_expansion",
                "value_bps": int(expansion_bps),
                "base_rate_pct": 0.22,
                "source": "Mauboussin reversion-to-mean 2007, Table 5",
                "message": f"3Y EBITDA expansion of {expansion_bps:.0f}bps occurs in ~22% of cases. Requires named driver."
            })

    # Check 3: CAP > 15 (ROIC persistence, Mauboussin Table 3)
    cap_y = inputs.get("cap_years")
    if cap_y and cap_y > 15:
        flags.append({
            "param": "cap_years",
            "value": cap_y,
            "base_rate_pct": 0.05,
            "source": "Mauboussin Base Rates of Excellence 2023, Table 3",
            "message": f"CAP {cap_y}y requires top-5% ROIC persistence. Need moat ≥22/25 and historical precedent."
        })

    return flags


def format_quality_summary(quality_data, roic_data, cap_data, capital_alloc_data):
    """One-screen chat summary of Step 5 (quality core) — v16.4."""
    lines = [f"\n--- Step 5: Quality Core ---"]
    if quality_data:
        q = quality_data
        lines.append(f"Composite: {q['composite']}/10 ({q['tier']})")
        for dim, sc in q['scores'].items():
            lines.append(f"  {dim:<28}: {sc}/10")
    if roic_data:
        r = roic_data
        n = r.get("window_years", "?")
        if 'avg_roic_incl_gw' in r:
            lines.append(f"ROIC {n}Y avg (incl-GW, ex-leases): {r['avg_roic_incl_gw']:.1%}  "
                         f"(spread {r.get('spread_to_wacc_bps_incl', 0):+.0f}bps vs WACC)")
        if 'avg_roic_ex_gw' in r:
            lines.append(f"ROIC {n}Y avg (ex-GW):             {r['avg_roic_ex_gw']:.1%}")
        if r.get('incremental_roic') is not None:
            flag = "⛔ below WACC → RONIC gate" if r.get('incremental_destroys_value') else "above WACC"
            lines.append(f"Incremental ROIC (pooled {r.get('incremental_span_years','?')}Y): {r['incremental_roic']:.1%}  ({flag})")
        elif r.get("incremental_note"):
            lines.append(f"Incremental ROIC: {r['incremental_note']}")
        if r.get("ic_leases_note"):
            lines.append(f"  {r['ic_leases_note']}")
    if cap_data:
        lines.append(f"CAP: {cap_data['years']}y (sector default {cap_data.get('sector_default', '?')}y) "
                     f"→ RONIC {cap_data.get('ronic', 0)*100:.1f}% [{cap_data.get('ronic_basis', '?')}]")
    if capital_alloc_data:
        ca = capital_alloc_data
        lines.append(f"Capital allocation: {ca.get('track_record', {}).get('composite', '?')}/10")
        if ca.get('penalty_flag'):
            lines.append(f"  ⛔ Below-threshold capital allocator")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# v16.5: growth paid for · discount-rate helpers · cash quality ·
#        operating leverage · scenarios · rating robustness · gate caps
# ═══════════════════════════════════════════════════════════════════

def check_growth_paid_for(output, inputs, roic_data=None):
    """Implied return on the explicit period's reinvestment, against history.

    implied = growth-driven ΔNOPAT Y1→Y10 (at Y1 margin and tax) ÷ Σ net
    reinvestment Y1..Y9 (capex − D&A + ΔNWC + acquisitions).
    Status: OK · ABOVE_HISTORY (> max(avg ROIC incl-GW, pooled incremental
    ROIC, WACC) + 5pp) · UNFUNDED (growth with ≤ 0 net reinvestment) ·
    GROWTH_NOT_PAID_FOR (⛔ ABOVE_HISTORY/UNFUNDED while the RONIC gate fired,
    with no `growth_funding_justification`): add `acquisition_spend` or cut
    growth to the organic run-rate.
    """
    y = output.get("yearly") or []
    if len(y) < 10:
        return None
    n1, r1, r10 = y[0]["nopat"], y[0]["revenue"], y[9]["revenue"]
    d_nopat = n1 * (r10 / r1 - 1) if r1 else 0.0
    reinvest = sum(-r["capex"] - r["da"] - r["dwc"] - r.get("acquisitions", 0) for r in y[:9])
    wacc = inputs["wacc"]
    hist_avg = (roic_data or {}).get("avg_roic_incl_gw")
    hist_incr = (roic_data or {}).get("incremental_roic")
    bench = max(x for x in (hist_avg, hist_incr, wacc) if x is not None)
    gate = hist_incr is not None and hist_incr < wacc
    implied = None
    if d_nopat <= 0:
        status = "OK"
    elif reinvest <= 0:
        status = "UNFUNDED"
    else:
        implied = d_nopat / reinvest
        status = "ABOVE_HISTORY" if implied > bench + 0.05 else "OK"
    if gate and status in ("UNFUNDED", "ABOVE_HISTORY") and not inputs.get("growth_funding_justification"):
        status = "GROWTH_NOT_PAID_FOR"
    imp_txt = f"{implied:.1%}" if implied is not None else "n/a (no net reinvestment)"
    hist_txt = (f"history: avg ROIC {hist_avg:.1%}" if hist_avg is not None else "history: n/a") + \
               (f", pooled incremental {hist_incr:.1%}" if hist_incr is not None else "")
    msg = {
        "OK": f"✓ Explicit-period return on reinvestment {imp_txt} ({hist_txt}).",
        "ABOVE_HISTORY": f"⚠ Explicit growth earns {imp_txt} on new capital — above anything in its {hist_txt}. Name the driver.",
        "UNFUNDED": f"⚠ Revenue grows with ≤ 0 net reinvestment ({hist_txt}). Check capex/ΔNWC/acquisitions.",
        "GROWTH_NOT_PAID_FOR": (f"⛔ GROWTH NOT PAID FOR: implied {imp_txt} on new capital while pooled incremental ROIC "
                                f"is below WACC ({hist_txt}). Add acquisition_spend, cut growth to the organic run-rate, "
                                f"or set growth_funding_justification."),
    }[status]
    return {"status": status, "implied_return_on_reinvestment": round(implied, 4) if implied is not None else None,
            "growth_nopat_y1_y10": round(d_nopat, 0), "net_reinvestment_y1_y9": round(reinvest, 0),
            "benchmark": round(bench, 4), "ronic_gate_fired": gate, "message": msg}


# ── Discount rate ────────────────────────────────────────────────────

def blume_adjusted_beta(beta_raw):
    """Blume adjustment toward 1: 0.67 × β + 0.33."""
    return 0.67 * beta_raw + 0.33


def relever_beta(beta_unlevered, debt_to_equity, tax_rate):
    """Hamada: β_L = β_U × (1 + (1 − t) × D/E)."""
    return beta_unlevered * (1 + (1 - tax_rate) * max(debt_to_equity, 0.0))


def cash_adjusted_beta(beta_equity, market_cap, excess_cash):
    """Operating beta of a net-cash company (cash beta ≈ 0): β_E × E / (E − excess cash).
    The DCF discounts operating cash flows and adds the cash back, so it needs the
    operating beta, not the equity beta. Use EXCESS cash (net_cash_quality) only."""
    if not excess_cash or excess_cash <= 0 or not market_cap or market_cap <= excess_cash:
        return beta_equity
    return beta_equity * market_cap / (market_cap - excess_cash)


def beta_quality_check(beta_measured, is_utility=False, adv_eur_m=None, beta_industry_relevered=None):
    """Thin trading biases measured beta toward zero. If β < 0.7 (non-utility) or
    average daily value traded < €1m, use max(measured, Blume, industry relevered)."""
    flags = []
    thin = adv_eur_m is not None and adv_eur_m < 1.0
    low = beta_measured < 0.7 and not is_utility
    if thin:
        flags.append(f"thinly traded (ADV €{adv_eur_m:.2f}m < €1m)")
    if low:
        flags.append(f"measured β {beta_measured:.2f} < 0.70 for a non-utility")
    cands = {"measured": beta_measured}
    if thin or low:
        cands["blume"] = blume_adjusted_beta(beta_measured)
        if beta_industry_relevered:
            cands["industry_relevered"] = beta_industry_relevered
    basis, used = max(cands.items(), key=lambda kv: kv[1])
    return {"beta_used": round(used, 3), "basis": basis, "beta_measured": beta_measured,
            "candidates": {k: round(v, 3) for k, v in cands.items()}, "flags": flags,
            "message": ("✓ β accepted as measured" if not flags else
                        f"⚠ β quality: {'; '.join(flags)} → using {basis} β {used:.2f} (print both)")}


def wacc_capm_range(rf_spot, beta, erp_implied, *, erp_long_run=None, rf_normalised=None, crp=0.0,
                    size_premium=0.0, beta_alt=None, beta_alt_is_operating=False, market_cap=None,
                    excess_cash=0.0, net_debt=0.0, kd_pre_tax=None, tax_rate=0.25):
    """v16.5 WACC from two COHERENT conventions — never spot Rf with a long-run ERP:
      (a) spot Rf + current implied ERP (Damodaran, fetched this run)   → central
      (b) normalised Rf + long-run ERP                                   → range only
    Beta variants (primary, beta_alt) widen the range. Net cash → operating beta
    on excess cash; net debt → market-value weights with Kd. Floor Rf + 300bps.
    beta_alt_is_operating=True when beta_alt is already an operating beta (e.g.
    Damodaran's industry 'unlevered beta corrected for cash') — no second cash adjustment.
    All inputs decimals. Returns central / low / high and the full table; pass
    {'low','high','basis'} to the DCF as inputs['wacc_range']."""
    conventions = [("spot Rf + implied ERP", rf_spot, erp_implied)]
    if erp_long_run is not None and rf_normalised is not None:
        conventions.append(("normalised Rf + long-run ERP", rf_normalised, erp_long_run))
    betas = [("primary", beta)] + ([("alt", beta_alt)] if beta_alt else [])
    rows = []
    for cname, rf, erp in conventions:
        for bname, b in betas:
            already_op = bname == "alt" and beta_alt_is_operating
            b_op = cash_adjusted_beta(b, market_cap, excess_cash) if (net_debt <= 0 and excess_cash and not already_op) else b
            ke = rf + b_op * (erp + crp) + size_premium
            if net_debt > 0 and market_cap:
                kd = kd_pre_tax if kd_pre_tax is not None else rf + 0.015
                we = market_cap / (market_cap + net_debt)
                w = we * ke + (1 - we) * kd * (1 - tax_rate)
            else:
                w = ke
            w = max(w, rf_spot + 0.03)
            rows.append({"convention": cname, "beta": bname, "beta_input": round(b, 3), "beta_operating": round(b_op, 3),
                         "rf": rf, "erp": erp, "crp": crp, "size_premium": size_premium,
                         "ke": round(ke, 5), "wacc": round(w, 5)})
    lo, hi = min(r["wacc"] for r in rows), max(r["wacc"] for r in rows)
    basis = " / ".join(sorted({r["convention"] for r in rows})) + (" × β variants" if beta_alt else "")
    return {"central": rows[0]["wacc"], "low": lo, "high": hi, "basis": basis, "table": rows,
            "wacc_range": {"low": lo, "high": hi, "basis": basis}}


def format_wacc_range(wr):
    lines = ["--- WACC (v16.5: coherent conventions only) ---",
             f"  {'Convention':<30} {'β':>6} {'β op':>6} {'Rf':>6} {'ERP':>6} {'CRP':>5} {'Size':>5} {'Ke':>7} {'WACC':>7}"]
    for r in wr["table"]:
        lines.append(f"  {r['convention']:<30} {r['beta_input']:>6.2f} {r['beta_operating']:>6.2f} {r['rf']*100:>5.2f}% "
                     f"{r['erp']*100:>5.2f}% {r['crp']*100:>4.2f}% {r['size_premium']*100:>4.2f}% {r['ke']*100:>6.2f}% {r['wacc']*100:>6.2f}%")
    lines.append(f"  Central {wr['central']*100:.2f}% · range {wr['low']*100:.2f}–{wr['high']*100:.2f}% [{wr['basis']}]")
    return "\n".join(lines)


# ── Cash quality and operating leverage ─────────────────────────────

def net_cash_quality(gross_cash, financial_debt, *, exclusions=None, interim_net_cash=None,
                     operating_cash_need=0.0, post_period_acquisitions=None):
    """v16.5 net debt for the bridge from LIQUID, EXCESS cash only.
    exclusions: [{label, amount, reason}] — long-dated placements, structured notes,
      capitalisation contracts, related-party current accounts, trapped/restricted cash.
    interim_net_cash: latest interim net cash on the same basis (after exclusions);
      the LOWER of year-end and interim is used (seasonal businesses).
    operating_cash_need: cash the business needs to operate (deposits float, minimum till).
    post_period_acquisitions: [{label, amount}] consideration for deals closed after the
      balance-sheet date whose revenue is already in Y1.
    Returns {'net_debt' (signed, + = net debt), 'excess_cash', 'log'}."""
    log = []
    excl = 0.0
    for e in (exclusions or []):
        excl += float(e["amount"])
        log.append(f"− {e['label']}: {e['amount']:,.1f} ({e.get('reason', 'not liquid / not free')})")
    used = gross_cash - excl - financial_debt
    log.insert(0, f"Year-end liquid net cash: {gross_cash:,.1f} − {excl:,.1f} excluded − {financial_debt:,.1f} debt = {used:,.1f}")
    if interim_net_cash is not None and interim_net_cash < used:
        log.append(f"Seasonality: interim net cash {interim_net_cash:,.1f} < year-end {used:,.1f} → interim used")
        used = interim_net_cash
    if operating_cash_need:
        used -= operating_cash_need
        log.append(f"− operating cash need: {operating_cash_need:,.1f}")
    for a in (post_period_acquisitions or []):
        used -= float(a["amount"])
        log.append(f"− post-period acquisition {a['label']}: {a['amount']:,.1f}")
    log.append(f"→ net cash for the bridge {used:,.1f} (net_debt = {-used:,.1f})")
    return {"net_debt": -used, "excess_cash": max(used, 0.0), "log": log}


def estimate_fixed_cost_share(rev_a, ebitda_a, rev_b, ebitda_b):
    """Fixed share of the cost base from two years (ideally a downturn):
    variable share v = (Δcost/cost) ÷ (Δrev/rev); fixed share = 1 − v, clamped 0–0.95."""
    cost_a, cost_b = rev_a - ebitda_a, rev_b - ebitda_b
    dr = rev_b / rev_a - 1
    if abs(dr) < 1e-6 or cost_a <= 0:
        return None
    v = (cost_b / cost_a - 1) / dr
    return round(min(max(1 - v, 0.0), 0.95), 3)


# ── Scenarios ────────────────────────────────────────────────────────

def _apply_move(inp, mv, scale=1.0):
    """One lever of a scenario, scaled. Levers: growth_years{years,delta} ·
    growth_near · growth_far · growth_all · set_growth_years{years,rates} ·
    margin_years{years,delta} · margin_tail (Y3+) · margin_all · wacc ·
    terminal_growth · ronic · capex_pct · dwc_pct · net_debt (add) ·
    claim{label,amount} (adds to other_claims)."""
    lev, d = mv["lever"], mv.get("delta", 0.0) * scale
    yrs = {"growth_near": range(0, 2), "growth_far": range(2, 10), "growth_all": range(0, 10),
           "margin_tail": range(2, 10), "margin_all": range(0, 10)}
    if lev in ("growth_near", "growth_far", "growth_all"):
        for i in yrs[lev]:
            inp["rev_growth"][i]["rate"] += d
    elif lev == "growth_years":
        for y in mv["years"]:
            inp["rev_growth"][y - 1]["rate"] += d
    elif lev == "set_growth_years":
        for y, r in zip(mv["years"], mv["rates"]):
            old = inp["rev_growth"][y - 1]["rate"]
            inp["rev_growth"][y - 1]["rate"] = old + scale * (r - old)
    elif lev in ("margin_tail", "margin_all"):
        for i in yrs[lev]:
            inp["ebitda_margins"][i]["margin"] += d
    elif lev == "margin_years":
        for y in mv["years"]:
            inp["ebitda_margins"][y - 1]["margin"] += d
    elif lev == "wacc":
        old = inp["wacc"]
        inp["wacc"] = old + d
        if inp.get("terminal_wacc") is not None and abs(inp["terminal_wacc"] - old) < 1e-12:
            inp["terminal_wacc"] = inp["wacc"]
    elif lev in ("terminal_growth", "ronic", "capex_pct", "dwc_pct", "net_debt"):
        base = inp.get(lev)
        if base is None and lev == "ronic":
            base = inp["wacc"]
        inp[lev] = (base or 0.0) + d
    elif lev == "claim":
        inp.setdefault("other_claims", [])
        if not isinstance(inp["other_claims"], list):
            inp["other_claims"] = [{"label": "other claims", "amount": float(inp["other_claims"])}]
        inp["other_claims"].append({"label": mv.get("label", "scenario claim"), "amount": mv["amount"] * scale})
    else:
        raise ValueError(f"Unknown scenario lever: {lev}")


def _scenario_inputs(base_inputs, moves, scale=1.0, operating_leverage=True):
    inp = copy.deepcopy(base_inputs)
    for mv in moves:
        _apply_move(inp, mv, scale)
    if operating_leverage and (inp.get("fixed_cost_share") or 0) > 0:
        inp["operating_leverage_ref"] = _model_revenue_path(base_inputs)
    return inp


def run_scenarios(base_inputs, scenarios, history=None):
    """v16.5 scenarios. Each scenario = {name, role (bear/base/bull/market_consistent),
    probability, root_cause, moves: [{lever, …}], operating_leverage (default True)}.
    One ROOT CAUSE per scenario; the drivers it mechanically moves (margin via
    fixed costs, rates and yields together…) move with it.
    history (optional) = {worst_revenue_growth, worst_margin_change_bps} → bear floor check.
    Flags: probabilities ≠ 100%, scenarios that do not bracket the price (requires a
    market-consistent scenario with its own probability)."""
    mkt = base_inputs["share_price"]
    base_out = run_dcf(copy.deepcopy(base_inputs), _skip_solvers=True)
    rows = []
    for sc in scenarios:
        inp = _scenario_inputs(base_inputs, sc.get("moves", []), 1.0, sc.get("operating_leverage", True))
        out = run_dcf(inp, _skip_solvers=True)
        rows.append({"name": sc["name"], "role": sc.get("role", ""), "probability": sc.get("probability", 0.0),
                     "root_cause": sc.get("root_cause", ""), "moves": sc.get("moves", []),
                     "price": out["implied_price"], "upside_pct": out["upside_pct"], "yearly": out["yearly"]})
    psum = sum(r["probability"] for r in rows)
    weighted = sum(r["probability"] * r["price"] for r in rows) / psum if psum else None
    flags = []
    if abs(psum - 1.0) > 1e-6:
        flags.append(f"⚠ probabilities sum to {psum:.0%}, not 100%")
    has_mc = any(r["role"] == "market_consistent" for r in rows)
    above = all(r["price"] > mkt for r in rows)
    below = all(r["price"] < mkt for r in rows)
    brackets = not (above or below)
    if not brackets and not has_mc:
        side = "above" if above else "below"
        flags.append(f"⛔ SCENARIOS DO NOT BRACKET THE PRICE (all {side} {mkt}). Build the market-consistent "
                     f"scenario (build_market_consistent_scenario) and give it its own probability.")
    bear_check = None
    bear = next((r for r in rows if r["role"] == "bear"), None)
    if history and bear:
        bear_check = bear_floor_check(bear["yearly"], base_out["yearly"], history)
        if not bear_check["passes"]:
            flags.append(bear_check["message"])
    return {"market_price": mkt, "base_price": base_out["implied_price"], "scenarios": rows,
            "probability_sum": round(psum, 4), "weighted_price": round(weighted, 2) if weighted else None,
            "weighted_upside_pct": round((weighted / mkt - 1) * 100, 1) if weighted and mkt else None,
            "brackets_price": brackets, "bear_floor_check": bear_check, "flags": flags}


def build_market_consistent_scenario(base_inputs, moves, name="Market-consistent", operating_leverage=True,
                                     max_severity=5.0):
    """Scale ONE coherent set of moves (the story the market might be pricing) until
    the DCF equals the market price. Returns a scenario dict (role market_consistent)
    with the scaled moves, the severity and the implied drivers; the analyst assigns
    its probability before re-running run_scenarios."""
    mkt = base_inputs["share_price"]
    price_at = lambda s: run_dcf(_scenario_inputs(base_inputs, moves, s, operating_leverage),
                                 _skip_solvers=True)["implied_price"]
    p0, p_max = price_at(0.0), price_at(max_severity)
    if (p0 - mkt) * (p_max - mkt) > 0:
        return {"status": "UNREACHABLE", "name": name, "price_at_max_severity": p_max,
                "message": f"These moves cannot reach {mkt} within {max_severity}× — the market prices a different story."}
    s = _bisect(price_at, 0.0, max_severity, mkt, tol=1e-5, increasing=p_max > p0)
    scaled = []
    for mv in moves:
        m2 = dict(mv)
        if "delta" in m2:
            m2["delta"] = mv["delta"] * s
        if "amount" in m2:
            m2["amount"] = mv["amount"] * s
        if "rates" in m2:
            base_r = [base_inputs["rev_growth"][y - 1]["rate"] for y in mv["years"]]
            m2["rates"] = [b + s * (r - b) for b, r in zip(base_r, mv["rates"])]
        scaled.append(m2)
    inp = _scenario_inputs(base_inputs, moves, s, operating_leverage)
    g = [r["rate"] for r in inp["rev_growth"]]
    geo = 1.0
    for x in g[2:]:
        geo *= (1 + x)
    return {"status": "OK", "name": name, "role": "market_consistent", "probability": None,
            "operating_leverage": operating_leverage, "moves": scaled, "severity": round(s, 3),
            "price": mkt, "implied": {"rev_cagr_y3_y10_pct": round((geo ** (1 / 8) - 1) * 100, 2),
                                      "y10_margin_pct": round(inp["ebitda_margins"][9]["margin"] * 100, 2),
                                      "wacc_pct": round(inp["wacc"] * 100, 2)},
            "message": f"Market price reached at {s:.2f}× the stated moves. Assign a probability, then re-run run_scenarios."}


def bear_floor_check(bear_yearly, base_yearly, history):
    """The bear must be at least as severe as the company's worst year on record:
    min bear growth ≤ worst_revenue_growth, OR the bear's largest margin gap vs base
    ≤ worst_margin_change_bps."""
    min_g = min(r["rev_growth_pct"] for r in bear_yearly) / 100
    gap_bps = min((b["ebitda_margin_pct"] - a["ebitda_margin_pct"]) * 100 for b, a in zip(bear_yearly, base_yearly))
    wg, wm = history.get("worst_revenue_growth"), history.get("worst_margin_change_bps")
    ok_g = wg is not None and min_g <= wg + 1e-9
    ok_m = wm is not None and gap_bps <= wm + 1e-9
    passes = ok_g or ok_m
    msg = ("✓ bear at least as severe as the worst year on record" if passes else
           f"⛔ BEAR TOO MILD: worst bear growth {min_g:.1%} vs history {wg:.1%}; largest bear margin gap "
           f"{gap_bps:+.0f}bps vs history {wm:+.0f}bps. Re-cut the bear from the company's own worst year.")
    return {"passes": passes, "bear_min_growth": round(min_g, 4), "bear_max_margin_gap_bps": round(gap_bps, 0),
            "history": history, "message": msg}


def format_scenarios(res, ccy=""):
    lines = [f"--- SCENARIOS (market {ccy} {res['market_price']}) ---",
             f"  {'Scenario':<22} {'Prob':>5} {'Price':>10} {'Upside':>8}  Root cause"]
    for r in res["scenarios"]:
        lines.append(f"  {r['name']:<22} {r['probability']:>5.0%} {r['price']:>10.1f} {r['upside_pct']:>+7.1f}%  {r['root_cause']}")
    if res.get("weighted_price") is not None:
        lines.append(f"  Probability-weighted: {ccy} {res['weighted_price']:.1f} ({res['weighted_upside_pct']:+.1f}%)")
    lines.append(f"  Brackets the price: {'yes' if res['brackets_price'] else 'NO'}")
    for f in res["flags"]:
        lines.append(f"  {f}")
    return "\n".join(lines)


# ── Rating robustness and gate caps ─────────────────────────────────

def rating_for_upside(upside_pct, tier="STANDARD"):
    t = RATING_THRESHOLDS.get((tier or "STANDARD").upper(), RATING_THRESHOLDS["STANDARD"])
    return "BUY" if upside_pct > t["buy"] else ("SELL" if upside_pct < t["sell"] else "HOLD")


def rating_robustness(inputs, tier="STANDARD"):
    """Rating at the model WACC and at both ends of wacc_range. If they differ the
    rating is not robust to the discount rate → capped at HOLD, and the WACC at
    which it flips is printed."""
    w_lo, w_hi, basis = _wacc_range(inputs)
    rows = []
    for tag, w in (("low", w_lo), ("model", inputs["wacc"]), ("high", w_hi)):
        out = run_dcf(_inputs_at_wacc(inputs, w), _skip_solvers=True)
        rows.append({"case": tag, "wacc_pct": round(w * 100, 2), "price": out["implied_price"],
                     "upside_pct": out["upside_pct"], "rating": rating_for_upside(out["upside_pct"], tier)})
    model = rows[1]["rating"]
    robust = len({r["rating"] for r in rows}) == 1
    flip = None
    if not robust and model != "HOLD":
        t = RATING_THRESHOLDS.get((tier or "STANDARD").upper(), RATING_THRESHOLDS["STANDARD"])
        target = inputs["share_price"] * (1 + (t["sell"] if model == "SELL" else t["buy"]) / 100)
        edge = w_lo if model == "SELL" else w_hi
        price_at = lambda w: run_dcf(_inputs_at_wacc(inputs, w), _skip_solvers=True)["implied_price"]
        lo, hi = sorted((inputs["wacc"], edge))
        flip = round(_bisect(price_at, lo, hi, target, tol=1e-5, increasing=False) * 100, 2)
    final = model if robust else "HOLD"
    msg = (f"✓ {model} holds across WACC {w_lo*100:.2f}–{w_hi*100:.2f}%" if robust else
           f"⚠ RATING NOT ROBUST TO THE DISCOUNT RATE: " +
           ", ".join(f"{r['rating']} at {r['wacc_pct']:.2f}%" for r in rows) +
           (f"; {model} only holds {'above' if model == 'SELL' else 'below'} WACC {flip:.2f}%" if flip else "") +
           " → rating capped at HOLD")
    return {"tier": tier, "rows": rows, "robust": robust, "model_rating": model, "final_rating": final,
            "flip_wacc_pct": flip, "wacc_range_basis": basis, "message": msg}


def gate_cap_check(inputs, anchor_margin, cap_margin, from_year=3, tol=0.001):
    """A gate is a ceiling, not a target. If the Y10 EBITDA margin (same basis as
    inputs['ebitda_margins']) sits at the gate cap, report the price at the
    unadjusted anchor (through-cycle / 3Y pooled) alongside."""
    m10 = inputs["ebitda_margins"][9]["margin"]
    if m10 < cap_margin - tol:
        return {"binding": False, "message": "✓ terminal margin below the gate cap"}
    alt = copy.deepcopy(inputs)
    shift = anchor_margin - m10
    for i in range(from_year - 1, 10):
        alt["ebitda_margins"][i]["margin"] += shift
    p_cap = run_dcf(copy.deepcopy(inputs), _skip_solvers=True)["implied_price"]
    p_anchor = run_dcf(alt, _skip_solvers=True)["implied_price"]
    return {"binding": True, "price_at_cap": p_cap, "price_at_anchor": p_anchor,
            "message": (f"⚠ AT GATE CAP: Y10 margin {m10:.1%} = cap {cap_margin:.1%}. Price {p_cap:.1f} at the cap "
                        f"vs {p_anchor:.1f} at the anchor {anchor_margin:.1%} — show both; the uplift needs evidence "
                        f"from ≥2 years not boosted by one-offs.")}
