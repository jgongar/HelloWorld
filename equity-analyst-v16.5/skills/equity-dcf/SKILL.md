---
name: equity-dcf
description: >
  DCF computation engine for equity analysis. Use this skill whenever running
  a DCF valuation, sensitivity analysis, scenario analysis, parameter override,
  or any command that requires financial computation (set, reset, run sensitivity,
  run scenario, what if). Also trigger when restoring a session from SESSION STATE.
  Read this SKILL.md BEFORE writing any Python script. Contains script templates,
  intra-session state rules, and the canonical accounting rules. Engine code lives
  in scripts/dcf_engine.py. (No session restore — every run is a cold start.)
---

# Equity DCF — Computation Skill (v16.5)

Engine version: v16.5. See `CHANGELOG.md` for version history.

**v16.5 in one paragraph:** the answer must survive its own discount-rate
uncertainty and its scenarios must reach the price. The kernel adds a fade
stage Y11..Y(CAP) when CAP > 10 (Rule 3D), asymmetric ΔNWC (no release on
revenue decline without evidence), optional operating leverage
(`fixed_cost_share`), `acquisition_spend` in UFCF and `other_claims` in the one
claims definition used by the bridge and every solver. New checks:
`check_growth_paid_for` (Rule 3E), `rating_robustness` across `wacc_range`,
`run_scenarios` (bracket test, worst-year bear floor) and
`build_market_consistent_scenario`, `gate_cap_check`. The gap waterfall gets a
discount-rate step; what-must-be-true shows the market-implied growth at both
ends of the WACC range and marks solver results at a bound as N/M. v16.4
inputs price identically unless revenue declines or `cap_years` > 10.

**v16.4 in one paragraph:** one lease convention (rent-as-opex: lease cash cost
haircuts every EBITDA margin inside the engine, lease liability is a memo, never
deducted); value-driver terminal value `TV = NOPAT₁₁ × (1 − tg/RONIC)/(WACC − tg)`
with a new `ronic` input that makes CAP matter beyond Y10 and makes tg
value-neutral when RONIC = WACC; Gate 4 replaced by a RONIC gate (pooled 3Y
incremental ROIC < WACC → RONIC = WACC); one projection kernel shared by every
solver; `what_must_be_true()` (per-driver market-implied values) and
`gap_waterfall()` (additive DCF-vs-market attribution) replace the reverse-CAP
solver; four modelling options; R8 advisory; R9 upside bug fixed.

## Core Rule

ALL financial calculations MUST execute via Python script.
Never compute DCF values in prose. Never present inline arithmetic.

## File Locations
- Engine: `/home/claude/dcf_engine.py` (copied from skill scripts/ on first run)
- State: `/home/claude/dcf_state.json` (single source of truth)
- Scenario files: `/home/claude/dcf_{label}.json`

## Workflow

**First DCF run (Step 7):** collect INPUTS → copy engine → write script from `scripts/dcf_template.py` → execute → save state.

**Subsequent runs (same conversation only):** load `/home/claude/dcf_state.json["inputs"]` → apply changes → re-run → show delta. Never reload a prior conversation's state.

**Error handling:** fix and retry ONCE. Second failure → STOP, "⚠ DCF COMPUTATION FAILED", multiples-only valuation, save partial state.

---

## ACCOUNTING RULES (canonical reference — prompt defers here)

### Rule 3 — EBITDA Normalisation

DCF projects NORMALISED EBITDA margins on a **rent-as-opex** basis (Rule 3C). UFCF formula
(identical in both engines — they differ only in how capex is specified):
`UFCF = EBIT × (1 − tax) + D&A − CapEx − ΔNWC`  ≡  `EBITDA × (1 − tax) + D&A × tax − CapEx − ΔNWC`

⛔ NEVER project EBIT margins directly.
⛔ NEVER use "adjusted/core/underlying EBITDA" as projection base. Build from IFRS EBIT upward. Flag gap to management.

**Build per FY:**
```
Normalised EBITDA = IFRS EBIT + D&A + Non-recurring impairments + Excess restructuring
```

Non-recurring = not expected to repeat. Recurring = embedded in operations. When in doubt: recurring (conservative).

**Required output table:**

| FY | IFRS EBIT | +D&A | +Impair | +Restruct | Norm EBITDA | Norm % | Mgmt % | Gap |

If |gap to mgmt| > 5% of revenue: investigate each item.

**Historical anchor:** 3Y pooled normalised EBITDA margin = sum(norm EBITDA FY-2..FY0) / sum(revenue FY-2..FY0). This is the M3 terminal anchor.

**Capitalised R&D (was Option 2):** if capitalised development > 10% of total R&D for 2+ years, re-expense it inside this build (EBIT − capitalised R&D + amortisation of capitalised R&D) and state the delta. Analyst adjustment, not an engine option.

### Rule 3C — Leases: ONE convention, rent-as-opex (v16.4, BINDING)

Leases are an operating cost that renews forever. The engine therefore:
1. subtracts `lease_cost_pct_of_revenue` = (repayment of lease liabilities + interest on leases, both from the cash-flow statement) ÷ revenue, 3Y pooled, from **every** projected EBITDA margin;
2. **never** deducts `lease_liabilities` in the equity bridge (memo line only);
3. computes ROIC on invested capital **ex-leases** with NOPAT = (EBIT − lease interest)(1 − t).

Supply IFRS-16 normalised margins + `lease_cost_pct_of_revenue`. If you built the normalised EBITDA already rent-inclusive, set `lease_cost_pct_of_revenue = 0` and say so in `derivations`. Never do both. `fy0_actuals.lease_cash_cost` keeps the FCF bridge on the same basis. Peer multiples stay on reported IFRS-16 EBITDA — they are a cross-check, not the answer; note the basis difference once.

### Rule 3D — Terminal value: value-driver formula + fade stage (v16.5, BINDING)

```
NOPAT₁₁ = NOPAT₁₀ × (1 + tg)
TV      = NOPAT₁₁ × (1 − tg / RONIC) / (WACC − tg)
```
`ronic` = return on new invested capital in perpetuity, set in Step 5 from CAP (see `quality-roic`). RONIC = WACC ⇒ growth is value-neutral (TV = NOPAT₁₁/WACC). Terminal reinvestment is `tg/RONIC × NOPAT`, replacing the frozen `capex_pct − da_pct` extrapolation. The engine prints the Gordon-on-UFCF₁₀ equivalent and the implied exit EV/EBITDA for reference.

**RONIC gate (replaces Gate 4):** pooled 3Y incremental ROIC < WACC → RONIC forced to WACC (`ronic_gate_fired`). Override with `ronic_override_justification`. No tg override exists any more.

**Fade stage (v16.5, BINDING when `cap_years` > 10):** the explicit forecast stops at Y10 but a CAP of 15–25 years means the growth advantage lasts longer. Supply `cap_years` from Step 5; the engine projects Y11..Y(CAP) on a NOPAT basis — margin held at Y10, growth fading linearly from Y10 growth to tg, reinvestment `g/RONIC × NOPAT` — and applies the value-driver TV at Y(CAP). With RONIC = WACC the stage is value-neutral (as it should be). `implied_exit_ev_ebitda` still values everything beyond Y10 at Y10, so it stays comparable. `fade_stage = "off"` only with a written reason.

### Rule 3E — Growth must be paid for (v16.5, BINDING)

Explicit-period growth is not free. `run_dcf` returns `growth_paid_for`: growth-driven ΔNOPAT Y1→Y10 ÷ net reinvestment Y1..Y9 (capex − D&A + ΔNWC + `acquisition_spend`), compared with the 5Y average ROIC and the pooled incremental ROIC.

- `ABOVE_HISTORY` (> best historical return + 5pp) or `UNFUNDED` (growth with ≤ 0 net reinvestment) → name the driver in derivations.
- ⛔ `GROWTH_NOT_PAID_FOR` (the above while the RONIC gate fired): either put the acquisitions that produce the growth into `acquisition_spend` (list of 10 amounts, or `acquisition_spend_pct_of_revenue`), or cut growth to the organic run-rate, or set `growth_funding_justification`. A gate that neutralises growth after Y10 but lets acquired growth through for free before Y10 is inconsistent.

### Rule 3B — D&A Definition

D&A = Depreciation of PP&E + Amortisation of intangibles, from income statement or EBITDA reconciliation.
⛔ NEVER use CF statement D&A (includes non-D&A items).

Source hierarchy: (1) EBITDA bridge in press release, (2) PP&E + intangibles notes summed, (3) StockAnalysis EBITDA−EBIT line.

**Validation (mandatory):** IFRS EBIT + D&A = EBITDA ± 2%. If >2%: stop, investigate, resolve.

D&A in DCF used ONLY for tax shield. `da_pct` = 3Y pooled. Flag if D&A% changes >200bps across 3Y window (M&A activity).

### Rule 5A — Consensus EBITDA Source

[M2] consensus EBITDA acceptable without GAAP override (pre-amortisation, less M&A-distorted than EBIT). If consensus tracks adjusted EBITDA and gap >300bps to normalised: skip [M2], apply [M3], flag.

### Net Debt & Equity Bridge

**NWC:** trade_receivables + inventories − trade_payables ONLY. No contract A/L, accruals, provisions (extended scope opt-in via Modelling Option 5).

**Net Debt:** ST borrowings + current LTD + LT debt + hybrid_instruments − cash + restricted_cash. EXCLUDE leases (memo only, Rule 3C) and pension (separate bridge line).

**⛔ R9 EXCLUSION:** If R9 triggers (see Rule 9 below), captive finance debt, subsidiary debt, and any debt matched by non-core receivables are STRIPPED from operating net debt before the bridge. They are not claims on operating equity.

Hybrid test: settles before common equity AND absent from diluted count? Perpetual notes YES, mandatorily convertibles NO.

**Latest balance sheet (v16.5, BINDING):** net debt, inventories, pension, minorities and every claim come from the LATEST published balance sheet — the interim if it is newer than FY0 — and covenants are tested on it. FY0 stays the base for P&L and cash-flow ratios.

**Cash quality (v16.5, BINDING):** build `net_debt` with `net_cash_quality(...)`: only liquid, free cash counts. Exclude long-dated placements, capitalisation contracts, structured notes, current accounts with related parties and trapped cash (list each). For seasonal businesses use the LOWER of year-end and latest-interim net cash. Deduct the consideration for acquisitions closed after the balance-sheet date whose revenue is already in Y1. The `excess_cash` it returns is what `wacc-capm` uses for the cash-adjusted beta.

**Other claims (v16.5):** anything else that ranks ahead of equity — deferred/contingent consideration, puts on minorities, the capitalised losses of a loss-making arm the growth plan depends on, a property book deficit — goes into `other_claims` [{label, amount}]. The engine uses the SAME claims in the bridge and in the market EV every solver targets; never deduct a claim outside the engine.

**EV = mcap + net_debt + pension + minorities + other_claims. Equity = EV − net_debt − pension − minorities − other_claims. (Symmetric; no leases.)**

With R9 active:
**EV_total = EV_operating (stripped DCF) + PV(non_core_dividend_stream) [+ Bull monetization overlay]**

### Tax Rate

`sum(tax_expense) / sum(pretax_income)` for positive-pretax years in {FY-2..FY0}. Extend to FY-4 if needed. If 5Y unavailable: search "{country} corporate tax rate {year}" → use statutory. Floor 15% (Pillar Two). Ceiling = country statutory.

**Tax fade:** Set `tax_fade = [t1..t10]` for year-by-year fade from current ETR toward statutory by Y10.

### ΔWC%

`sum(ΔNWC) / sum(ΔRev)` over {FY-2..FY0}. Sign convention: POSITIVE = drag, NEGATIVE = source.
Anomaly gate: >2,000bps deviation → drop year, use 2Y pool.
If ≤1 year or ΔRev≤0: sector default (Luxury 15%, Software 10%, Industrial 12%, Pharma 8%, Defense 10%, Semis 12%).

**Project-delivery override:** For EPC/long-cycle (Technip, Vinci-style) and advertising agencies, ΔWC% = 0% by default (milestone prepayment / structural negative NWC float).

**Asymmetry on decline (v16.5):** `dwc_pct` applies to revenue growth. On a revenue DECLINE the engine uses `dwc_pct_decline`, default `min(dwc_pct, 0)`: a business that ties up working capital when it grows does NOT get cash back when it shrinks unless its own downturns show it (supply `dwc_pct_decline` with the year cited). Negative-NWC businesses keep the symmetric drag (prepayments unwind).

### PPA Amortisation

PPA sits below EBITDA — no direct margin impact. Flows through D&A as tax shield only. As PPA rolls off, `da_pct` declines marginally (second-order).

If PPA > 100bps of revenue: split `da_pct_near` (3Y D&A incl. PPA, used to roll-off year) and `da_pct_terminal` (3Y D&A ex-PPA, used Y{end+1}+).

If no acquisition PPA: `ppa_schedule: {}` → skip.

### Cyclical Normalisation

For sectors in {Autos, Chemicals, Shipping, Steel, Construction Materials, Upstream Energy, Semis Equipment, Memory Semis, Airlines, Refining}:

- **Terminal EBITDA margin** = through-cycle average over whatever history the single StockAnalysis income-statement page provides (≥5Y). No extra searches for history; fall back to the `stress_tests.md` through-cycle table. Document the span.
- If FY0 margin > 10Y avg + 200bps: flag `cycle_peak_fy0 = true` in state. Add to red flags as item 13.
- Y1-Y2 may follow consensus (cycle-aware); Y3+ fades toward through-cycle anchor by Y5, holds to terminal.

This applies BEFORE the peer 75th pctile cap. Through-cycle margin can be below peer 75th; the cap doesn't override the cyclical anchor downward.

**Operating leverage (v16.5, BINDING for cyclicals and any name whose bear moves revenue):** set `fixed_cost_share` (fixed share of the cost base; `estimate_fixed_cost_share(rev_a, ebitda_a, rev_b, ebitda_b)` on the company's own worst year) and optionally `fixed_cost_adjustment_years` (default 3: fixed costs catch up with a new revenue path over three years). The base case is unchanged; growth solvers and scenarios that move revenue off the model path re-price margins through it, so a −30% year produces the margin collapse the company actually showed.

**Gates are ceilings, not targets (v16.5):** if a terminal margin sits at a gate cap (e.g. G3 through-cycle + 100bps, G2 peer 75th pct), run `gate_cap_check(inputs, anchor, cap)` and show the price at the anchor next to the price at the cap. The uplift needs evidence from ≥ 2 years not boosted by an identifiable one-off (policy stimulus, acquisition, FX).

### Rule 8 — Sign-Aware UFCF Unlevering (BINDING)

The unlevering step in the FCF bridge depends on the SIGN of net interest. The engine cannot infer this from input magnitude — the analyst must classify and provide signed values.

**INPUTS dict requires:**

```python
"net_interest_position_fy0": {
    "interest_expense": 0.0,        # gross, always POSITIVE [filing]
    "interest_income":  0.0,        # gross, always POSITIVE [filing]
    "net":              0.0,        # = expense − income; SIGNED (positive = net debt, negative = net cash)
    "tax_rate_applied": 0.28,       # for ATX adjustment
    "atx_net":          0.0,        # = net × (1 − tax_rate); SIGNED
    "bridge_direction": "...",      # "UFCF > FCF" (net debt) OR "UFCF < FCF" (net cash)
}
```

**Bridge sign convention:**
- Net debt company (`net > 0`, interest expense dominates): UFCF = FCF + atx_net → **UFCF > FCF**
- Net cash company (`net < 0`, interest income dominates): UFCF = FCF + atx_net (atx_net negative) → **UFCF < FCF**

The formula `UFCF = FCF + atx_net` is the same in both cases — the sign of `atx_net` carries the direction.

**Engine binding gate:** `enforce_ufcf_sign_rule(ufcf_fy0, fcf_fy0, atx_net_fy0)`, evaluated SAME-PERIOD. `build_fcf_bridge` reconciles a computed `UFCF_FY0` (from `inputs['ufcf_fy0']` or `inputs['fy0_actuals']`) to reported FCF_FY0, so the sign test is not contaminated by the FY0→Y1 growth/ΔWC/capex step (that step is reported separately as `growth_step_fy0_to_y1`, non-gated). It compares `sign(UFCF_FY0 − FCF_FY0)` to `sign(atx_net)`. If signs disagree above the 5% noise threshold, refuse to proceed:
> ⛔ R8 VIOLATION — UFCF unlevering direction inconsistent with net interest position. Verify net_interest_position_fy0.net is signed correctly (positive = net debt, negative = net cash).

If neither `ufcf_fy0` nor `fy0_actuals` is supplied, the bridge falls back to Y1 and **both the residual gate and R8 become ADVISORY (non-binding)** — supply FY0 UFCF to restore binding status.

Catches the common error of treating a net-cash company with the net-debt unlevering direction.

### Rule 9 — Non-Core Holdings: Strip-Out + Dividend-as-FCF (BINDING)

⛔ **Read `references/non_core_holdings.md` whenever R9 triggers.**

**Trigger:** Any one of:
1. Captive finance arm with separately reportable segment OI ≥10% of group OI
2. Equity-method stake with carrying value ≥10% of parent market cap OR ≥10% of net income
3. FVOCI / FVTPL equity investment with fair value ≥10% of parent market cap
4. Holding company structure with separately listed operating subsidiaries

**Treatment (binding):**
1. **Strip from operating DCF**: revenue, EBITDA, D&A, capex from each non-core holding
2. **Exclude from EV bridge**: captive debt, subsidiary debt, balance sheet debt matched by non-core receivables
3. **Value as dividend stream**: PV of actual dividends paid to parent, growing ≤2%/yr, terminal held flat. Discounted mid-year / calendar-aware (same offsets as the operating DCF), not full-year.
4. **NEVER add book/FV stake to bridge**: this would double-count with the dividend stream. Carrying value and look-through fair value ARE surfaced as INFO ONLY (`balance_sheet_info`, plus `total_carrying_value_info` / `total_fair_value_info` / `dividend_pv_vs_fair_value_pct` in the aggregate) — shown to size the conservatism of the dividend-only base case (so a retain-and-compound stake isn't silently zeroed), never credited to base-case EV.
5. **Bull-case overlay only**: monetization (IPO/sale at fair value × probability × (1 − friction)) modelled explicitly with named catalyst

Full schema, treatment matrix, engine helpers, and worked examples (Renault/Mobilize, Dassault Aviation/Thales, Exor, Stellantis, Berkshire) in `references/non_core_holdings.md`.

---

## Data Retrieval (Step 2)

Collect financials via web_search + web_fetch (Source hierarchy below). There is
no `data_retrieval.py` / yfinance fallback in this environment — Yahoo endpoints
are not reachable from the sandbox. If web sources are incomplete after the
fallback chain, mark fields N/A per R2 and, if >3 critical fields missing, STOP.

---

## Computation surface (no external scripts)

All computation lives in `scripts/dcf_engine.py`. Write a thin run-script from
`scripts/dcf_template.py` that imports the engine and calls these functions.
There are no separate `sensitivity.py` / `scenario.py` / `override.py` files —
they were never needed and are not shipped.

- **Initial DCF / re-run:** `run_dcf(inputs)` → `format_dcf_output(output, inputs)`
- **FCF bridge:** `build_fcf_bridge(output, inputs)` (attach to `output["fcf_bridge"]`)
- **Sensitivity (tornado):** `build_tornado(inputs)` → `format_tornado(t)`. Pinned
  8-variable set (`TORNADO_SPEC`, v16.4: RONIC in, tax out). R9-active runs auto-append a non-core dividend ±25%.
- **What must be true:** `out["what_must_be_true"]` is computed inside every `run_dcf`
  (per-driver market-implied values); print with `format_what_must_be_true(out["what_must_be_true"], ccy)`.
- **Gap waterfall:** `gap_waterfall(inputs, {"rev_growth":[c1,c2,c3], "ebitda_margins":[m1,m2,m3]})`
  → `format_gap_waterfall(wf, ccy)`. Consensus path on reported IFRS-16 basis (engine applies the same haircuts).
  v16.5: a discount-rate step moves WACC toward the market but only inside `wacc_range`; `gap_mostly` ∈
  {near-term, discount-rate, long-term}; `gap_closed_within_wacc_range` = True means there is no fundamental edge.
- **Scenarios (v16.5):** `run_scenarios(inputs, scenarios, history)` → `format_scenarios(res, ccy)`. Each
  scenario = one ROOT CAUSE with its linked moves (`lever` list, see `_apply_move`), `role`, `probability`.
  Flags: probabilities ≠ 100%, scenarios that do not bracket the price, a bear milder than the worst year
  on record (`history = {worst_revenue_growth, worst_margin_change_bps}`). When the flag fires, call
  `build_market_consistent_scenario(inputs, moves)` with the story the market might be pricing, give it a
  probability (printed before pricing like the others) and re-run.
- **Rating robustness (v16.5):** `rating_robustness(inputs, tier)` — rating at the model WACC and at both ends
  of `wacc_range`; different ratings → capped at HOLD, flip WACC printed.
- **Solvers:** `find_breakeven_wacc/tg`, `reverse_dcf(hold_years=…)`, `implied_terminal_margin`, `implied_ronic`.
- **WACC / beta / cash (v16.5):** `wacc_capm_range(...)` → `format_wacc_range(wr)`; `cash_adjusted_beta`,
  `blume_adjusted_beta`, `relever_beta`, `beta_quality_check`; `net_cash_quality(...)`; `estimate_fixed_cost_share`;
  `gate_cap_check`.
- **Override (`set ...`):** load state, mutate the field, re-run `run_dcf`, show delta.

---

## INPUTS Dict — Key Fields

Every value carries a source label per R7 (derivation metadata).

**Identifiers:** company, ticker, currency, date, analysis_date, fiscal_year_end_month, last_completed_fy

**Market data:** share_price, shares_outstanding [market/filing]

**Bridge:** net_debt (operating only per R9), minorities, pension_deficit [filing]; lease_liabilities [filing, MEMO ONLY]

**Leases (Rule 3C):** lease_cost_pct_of_revenue [filing, CF statement, 3Y pooled]

**Terminal (Rule 3D):** ronic [Step 5 CAP rule]; optional ronic_override_justification; cap_years [Step 5] (> 10 → fade stage); fade_stage ("auto" | "off")

**v16.5:** wacc_range {low, high, basis} [wacc-capm] · other_claims [{label, amount}] · acquisition_spend [10 amounts] or acquisition_spend_pct_of_revenue · growth_funding_justification (optional) · dwc_pct_decline (optional, evidence required) · fixed_cost_share / fixed_cost_adjustment_years (cyclicals) · operating_leverage_ref (set by the scenario helpers — never by hand)

**Base case:** base_revenue (FY0 operating only — stripped per R9) [filing]

**Discount:** wacc, terminal_growth, terminal_wacc (optional) [CAPM-lite / computed]

**Mechanicals:** tax_rate, da_pct, capex_pct, dwc_pct (3Y avg) [computed]; tax_fade (optional)

**Projections:** rev_growth[10], ebitda_margins[10] (each with rate, source, note) — operating only

**Reconciliation:** reported_fcf_fy0 [filing], net_debt_components

**Cyclical:** cycle_peak_fy0 (bool), through_cycle_margin (if applicable)

**PPA:** ppa_schedule {Y1..end_year} or {}

**R8 sign-aware unlevering:** net_interest_position_fy0 {expense, income, net, tax_rate_applied, atx_net, bridge_direction}

**R9 non-core holdings:** non_core_holdings (list of dicts per schema in `references/non_core_holdings.md`)

**Always:** margin_type = "normalised_EBITDA"

---

## Reference Files

The skill's `references/` directory contains:

| File | Loaded when |
|------|-------------|
| `non_core_holdings.md` | R9 trigger fires (Step 1b screen) |
| `reit_valuation.md` | Sector = REIT / Real Estate (Step 1b routing) |
| `utilities_regulated.md` | Sector = regulated Utilities (Step 1b routing) |
| `upstream_energy_nav.md` | Sector = Upstream Energy / E&P (Step 1b routing) |
| `stress_tests.md` | Step 7 scenarios (R9 dividend bear case, FX bear, holdco discount, Pillar Two) |

When the orchestrator hits one of the triggers above, it MUST read the corresponding reference file BEFORE writing any script.

---

## Engine Helpers

**Core valuation:**
- `run_dcf(inputs)` — main entry: routing → R9 strip → non-core PV → RONIC gate → `_project()` → bridge (no leases) → solvers. Output keys of note: `implied_price`, `upside_pct` (percent, both paths), `terminal_block` {ronic, ronic_basis, reinvestment_rate, implied_exit_ev_ebitda}, `terminal_value_gordon_equivalent`, `what_must_be_true`, `lease_adjustment`, `sbc_adjustment`, `ronic_gate_fired/message`, `enterprise_value_operating`, `non_core_pv_added`.
- `build_fcf_bridge(output, inputs)` — same-period reconciliation; R8 advisory; R9 dividend strip; residual ≤10% is the gate.
- `compute_ufcf_fy0(inputs)` — FY0 UFCF from `fy0_actuals` on the rent-as-opex (and SBC-consistent) basis.
- `what_must_be_true(inputs, non_core_pv=0, consensus=None)` — per-driver market-implied values (rev CAGR Y1–Y10, rev CAGR Y3–Y10 holding Y1–2, terminal margin Y10, WACC, tg, RONIC). `format_what_must_be_true(w, ccy)`.
- `gap_waterfall(inputs, consensus_path)` — DCF → consensus near-term growth → consensus near-term margin → WACC inside `wacc_range` → residual (LT path/TV) → market; `gap_mostly`; plus market-implied LT CAGR. `format_gap_waterfall(wf, ccy)`.
- v16.5 checks: `check_growth_paid_for` (auto in `run_dcf` → `growth_paid_for`), `run_scenarios` / `build_market_consistent_scenario` / `bear_floor_check` / `format_scenarios`, `rating_for_upside` / `rating_robustness`, `gate_cap_check`.
- v16.5 discount rate and claims: `wacc_capm_range` / `format_wacc_range`, `cash_adjusted_beta`, `blume_adjusted_beta`, `relever_beta`, `beta_quality_check`, `net_cash_quality`, `estimate_fixed_cost_share`.
- `run_dcf(inputs, _skip_solvers=True)` prices without the what-must-be-true solves (used inside the helpers).
- `reverse_dcf(inputs, offsets=None, non_core_pv=0, hold_years=0)` → `(cagr_pct, y10_revenue)` tuple. `find_breakeven_wacc/tg`, `implied_terminal_margin`, `implied_ronic`.
- `build_tornado(inputs)` / `format_tornado(t)` — pinned spec v16.4.

**Modelling options:** `resolve_modelling_options(sector, financials, non_core_holdings)` → (options, triggers) for the FOUR options; `compute_options_hash(options)`.

**Cyclical:** `is_cyclical_sector(sector)`, `cycle_position_check(fy0_margin, through_cycle_margin)`.

**Quality / ROIC / CAP:**
- `compute_roic_history(financials_5y, tax_rate, wacc)` — IC ex-leases, NOPAT lease-adjusted (optional `lease_interest` per FY), pooled 3Y `incremental_roic` (gate statistic), per-year `incremental_series` (info only), `roic_cv`.
- `compute_quality_score(roic_data, moat[5 ints], runway, capalloc_score, balance_sheet_data{net_debt (ex-leases), ebitda (rent-as-opex), ebit, interest_expense})`.
- `compute_capital_allocation_score(channels)` → float.
- `enforce_ronic_gate(inputs, roic_data)` — auto-called in `run_dcf`.
- `project_share_count(...)`, `check_base_rates(inputs)`, `format_quality_summary(...)`.

**Non-core (R9):** `strip_non_core_from_group`, `value_non_core_holding`, `compute_non_core_aggregate`, `validate_non_core_no_double_count` — unchanged.

**Removed in v16.4:** `compute_implied_cap`, `enforce_value_destruction_gate`, `_run_dcf_ebitda/_run_dcf_nopat` (merged into `_project`), Options 2/3/6/7, `lease_principal_fy0` (→ signed `lease_cash_adjustment_fy0`), `sanity_y1_vs_actual_pct`.

## SBC Cash-Cost Handling

When `modelling_options.sbc == "cash_cost"`, the engine subtracts `inputs["sbc_pct_of_revenue"]` from every projected EBITDA margin BEFORE the DCF computation (same mechanism as the lease cash-cost haircut, Rule 3C).

---

## Canonical Field Names

**financial_data.json:** revenue, gross_profit, ebitda, ebit, net_income, eps_diluted, interest_expense, interest_income, tax_expense, pretax_income, operating_cf, capex, da, cash, total_debt, total_equity, total_assets, goodwill, other_intangibles, trade_receivables, inventories, trade_payables, pension_deficit, lease_liabilities, hybrid_instruments, restricted_cash, shares_outstanding, ppe_net. Plus per-segment if R9: segment_revenue, segment_ebitda, segment_capex, segment_dividend_to_parent.

All values POSITIVE, in millions. Sign convention: capex/da/interest_expense/interest_income/tax_expense always positive in raw data. Signing applied in `net_interest_position_fy0.net` per R8.

**peers.json (per peer):** company, ticker, market_cap, ev, pe_fwd, ev_ebitda_fwd, ev_ebitda_ttm, ev_sales, ebit_margin, fcf_margin, roic, nd_ebitda, beta, div_yield, buyback_yield, net_shareholder_yield, tsr_1y, currency, notes. Top-level: company, ticker, currency, collection_date, peers[], subject_company_row.

**Critical disambiguation:**
- `ebit` = GAAP/IFRS operating income, NEVER adjusted
- `da` = per Rule 3B (EBITDA bridge preferred)
- `cash` = cash + ST investments, EXCLUDE restricted; EXCLUDE captive cash per R9
- `trade_receivables` = trade only, NOT contract assets, EXCLUDE captive receivables per R9
- `lease_liabilities` = gross IFRS16 current + non-current — MEMO ONLY in v16.4
- `lease_cash_cost` = repayment of lease liabilities + interest on leases (CF statement) — drives `lease_cost_pct_of_revenue`
- `lease_interest` (per FY, optional) = lease interest, for ROIC NOPAT adjustment
- `hybrid_instruments` = perpetual notes etc. (settle before common equity, absent from diluted count)
- `pension_deficit` = IAS19 net DB liability (net of plan assets)
- `interest_expense` / `interest_income` = gross from P&L (R8 requires both, signed in net field)
