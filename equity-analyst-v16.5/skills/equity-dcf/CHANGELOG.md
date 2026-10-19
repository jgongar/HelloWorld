# Equity DCF Engine — Changelog

## v16.5 (2026-10-19) — robustness to the discount rate, scenarios that reach the price

Driven by four reviews (Hermès, Equasens, Hexaom, LNA Santé) where every v16.4 conclusion was more extreme than the review, in both directions, and no scenario set bracketed the price.

**Behavioural (numbers change only in these cases):**
- Fade stage Y11..Y(CAP) when `cap_years` > 10 (Rule 3D). Growth fades linearly from Y10 to tg, reinvestment g/RONIC, TV at Y(CAP). Value-neutral when RONIC = WACC. `tv_pct_of_ev` now = value beyond Y10 (stage + TV). `fade_stage="off"` restores v16.4.
- Asymmetric ΔNWC: revenue declines use `dwc_pct_decline` (default `min(dwc_pct, 0)`): no working-capital release without evidence. Growth years unchanged.
- `acquisition_spend` (list or % of revenue) is deducted from UFCF; yearly rows gain `acquisitions`.
- `other_claims` [{label, amount}] enter `_claims` → the bridge AND `_target_ev` (every solver).

**Added:** `check_growth_paid_for` (auto → `growth_paid_for`, Rule 3E); operating leverage (`fixed_cost_share`, `fixed_cost_adjustment_years`, `operating_leverage_ref`) in the kernel and solvers; `estimate_fixed_cost_share`; `wacc_capm_range` / `format_wacc_range`; `cash_adjusted_beta`, `blume_adjusted_beta`, `relever_beta`, `beta_quality_check`; `net_cash_quality`; `run_scenarios`, `build_market_consistent_scenario`, `bear_floor_check`, `format_scenarios`; `rating_for_upside`, `rating_robustness`, `RATING_THRESHOLDS`; `gate_cap_check`; `run_dcf(..., _skip_solvers=True)`; Homebuilding / Household Durables / Real Estate Development in `CYCLICAL_SECTORS`.

**Changed:** `gap_waterfall` adds a discount-rate step (WACC moved toward the market inside `wacc_range`) before the long-term residual and returns `gap_mostly`, `gap_closed_within_wacc_range`, `wacc_closing_gap_pct`. `what_must_be_true` adds the Y3–Y10 market-implied CAGR at both ends of `wacc_range`, marks growth solves at their bound and implausible breakeven WACCs as N/M. `format_dcf_output` prints the fade stage, other claims, acquisition spend and the growth-paid-for line.

**Regression:** v16.4 inputs with non-negative growth, no `cap_years` > 10 and none of the new keys price identically (tests/test_engine_v165.py).

## v16.4 (2026-09-04) — leases, terminal value, what-must-be-true, simplification

**Breaking (INPUTS):**
- `lease_liabilities` is MEMO ONLY — never deducted in the bridge. New `lease_cost_pct_of_revenue` (lease principal + interest paid ÷ revenue, 3Y pooled) is subtracted from every EBITDA margin in-engine (rent-as-opex, Rule 3C). Modelling Option 3 removed.
- New `ronic` (terminal return on new invested capital; default = WACC). Terminal value is value-driver: `TV = NOPAT₁₁ × (1 − tg/RONIC)/(WACC − tg)` (Rule 3D). `terminal_value_gordon_equivalent` reported for reference.
- `modelling_options` reduced to 4 keys (engine, sbc, nwc_scope, non_core_treatment) + constants (lease_convention, mid_year). Options 2/3/6/7 removed; capitalised R&D is a Rule 3 analyst adjustment; `terminal_wacc` stays an optional manual input.
- `lease_principal_fy0` → `lease_cash_adjustment_fy0` (SIGNED; negative when reported FCF excludes lease payments). `fy0_actuals` accepts `lease_cash_cost` and `sbc` for same-basis bridge.
- `compute_roic_history`: IC ex-leases; NOPAT = (EBIT − `lease_interest`)(1−t); gate statistic = POOLED 3Y `incremental_roic`; `incremental_destroys_3y_consecutive` removed (per-year series info only).
- `compute_quality_score` Dim 6 takes `net_debt` (ex-leases); `net_debt_incl_leases` still accepted.

**Removed:** `compute_implied_cap` (could not discriminate CAP > 10y — identical price for any CAP ≥ 10; bypassed Gate 4, R9 PV, NOPAT engine), `enforce_value_destruction_gate` (Gate 4), `_run_dcf_ebitda` / `_run_dcf_nopat` (merged into `_project`), `sanity_y1_vs_actual_pct`, `LEASE_HEAVY_SECTORS`.

**Added:** `_project()` shared kernel; `enforce_ronic_gate`; `what_must_be_true()` + `format_what_must_be_true()`; `gap_waterfall()` + `format_gap_waterfall()`; `implied_terminal_margin()`, `implied_ronic()`; `reverse_dcf(hold_years=…)`; `run_dcf` output keys `terminal_block`, `what_must_be_true`, `lease_adjustment`, `ronic_gate_fired/message`, `enterprise_value_operating`, `non_core_pv_added`, `lease_liabilities_memo`.

**Fixed:** R9 path `upside_pct` was a fraction (non-R9 a percentage); `reverse_dcf` ignored SBC haircut, targeted full mcap under R9 (non-core PV not subtracted), used EBITDA formula under NOPAT-native; breakeven solvers duplicated (and drifted from) the main loop; Option-3 trigger returned 0 for net-cash companies; `lease_intensity` double count.

**Behavioural:** R8 sign rule ADVISORY (never halts; residual ≤10% remains the bridge gate). Tornado spec v16.4: `tax_rate` out, `ronic` in. `format_dcf_output` rewritten: terminal block, WHAT MUST BE TRUE table, 4-option decisions block.

**Version comparability:** v16.4 prices are NOT comparable to v16.1: (a) lease-heavy names move (margin haircut ≈ perpetuity of lease cost vs a 3–7Y liability); (b) TV changes with RONIC (RONIC = WACC ⇒ TV = NOPAT₁₁/WACC, typically below Gordon-on-UFCF when capex ≈ D&A and tg > 0; RONIC ≫ WACC ⇒ above). Do not compare across engine versions.

## v16.1

Consistency-repair release following the v16 audit. Engine math changes are
deliberate and each moves the model toward internal consistency, not toward a
different valuation philosophy.

### Engine changes (affect numbers)

- **ROIC invested capital is lease-inclusive.** `IC = total_debt +
  lease_liabilities + total_equity − cash`. IFRS 16 boosts EBIT (rent replaced
  by lease D&A + below-EBIT interest) so NOPAT reflects lease capitalisation;
  excluding the matching liability overstated ROIC for lease-heavy names
  (retail networks, luxury). Missing `lease_liabilities` key → 0 + a visible
  `ic_leases_note` warning. **Impact:** lowers ROIC / Dim 1 spread for
  lease-heavy companies; no impact on lease-light industrials.
- **Mid-year convention applied consistently to terminal value.** With
  mid-year ON, TV is discounted at end-of-Y10 − 0.5y (uniform fallback: 9.5;
  calendar-aware: Y10 year-end offset − 0.5). Pre-v16.1 mixed mid-year explicit
  flows with an end-of-Y10 TV anchor — an undocumented ~(1+WACC)^0.5 haircut on
  PV(TV). **Impact:** raises implied prices ~2–5% depending on TV weight and
  WACC. Conservatism should live in assumptions (tg 2.0%, margin caps, gates),
  not in discounting artifacts. Exposed as
  `discount_offsets.terminal_mid_year_adjustment` for the transparency block.
- **R9 non-core dividend terminal: double half-year shift removed.**
  `end_offset = _disc_offset(horizon)` (was `+ 0.5` on top of the mid-year
  offset, which over-discounted the flat-perpetuity terminal under BOTH
  conventions). Dividend-only conservatism (flat terminal, 2% growth cap)
  unchanged.
- **Gate 4 self-verifying.** `compute_roic_history` accepts FY-4..FY0, emits a
  per-year `incremental_series`, and derives
  `incremental_destroys_3y_consecutive` in-engine (≥4 FYs required; `None`
  below that). `enforce_value_destruction_gate` consumes the engine flag first
  and falls back to the analyst-supplied boolean only when unverifiable. ΔIC ≤ 0
  years (capital returned) do not count toward the streak.
- **Quality Dimension 6 replaced.** "Earnings predictability" (~duplicated
  Dim 2's volatility signal) → **balance-sheet resilience**: ND/EBITDA
  (lease-inclusive) banded 10→1, with an interest-coverage modifier (EBIT/gross
  interest <4x → −1, <2x → −2). Net cash = 10. Leverage was previously absent
  from the quality composite entirely. Legacy predictability dicts still score
  the old way on state reload, with `dim6_legacy_warning`.
- **Bugfix:** `sanity_y1_vs_actual_pct` printed "N/A" for a genuine 0.0% delta
  (truthiness test → `is not None`).

### Template changes

- Header version stamp v16.1 (was stale at v15.1).
- `terminal_growth` comment corrected to the P1 rule — **2.0% flat default,
  3.50% hard cap via explicit user acceptance only, no Rf-based floor** (the
  stale `min(Rf+0.1pp, 3.5%)` comment was the pre-v16 rule and the most likely
  vector for tg drift, since the template is copied verbatim every run).
- `roic_data` / `incremental_destroys_3y_consecutive` wiring block added so
  Gate 4 is connected by default rather than by migration note.

### Orchestrator-side (prompt v16.1, not engine code)

- Step 3c aligned to the engine: the prescribed "Y5 exit-multiple deterministic
  reverse method" was never implemented and its inputs don't exist until Step 6.
  Step 3c is now a qualitative expectations read (consensus explicit CAGR,
  guidance gap); the formal reverse DCF + reverse CAP run at Step 7 on final
  model inputs, as the engine has always done.
- Step 2 ROIC collection extended: `total_debt, total_equity, cash, goodwill,
  lease_liabilities` per FY over FY-4..FY0 (income-statement fields stay 3Y).
- Dim 6 balance-sheet inputs (net debt incl. leases, EBITDA, EBIT, gross
  interest expense) — all already collected, no new fields.

### Migration from v16

- Supply per-FY `lease_liabilities` in the ROIC financials dict (else warning +
  ex-lease IC for those years).
- Supply 5 FYs of ROIC balance-sheet data to keep Gate 4 engine-verified.
- Pass `balance_sheet_data` (not `predictability_data`) as the 5th argument to
  `compute_quality_score`.
- Expect implied prices ~2–5% higher than identical v16 inputs (TV convention
  fix) — this is the removal of an undocumented haircut, not a change of view.

## v16

System-level cleanup and alignment release. The engine math is unchanged from
v15.2 (same UFCF formula, same R8/R9/Gate-4 logic, same tornado); only the
version stamp moves to `v16`. Changes are concentrated in the orchestrator and
the skill text, plus the xlsx export.

- **Terminal growth — single conservative rule (P1).** `tg = 2.0%` flat default
  for all markets, owned by orchestrator Step 4. Hard cap 3.50%, reachable only via
  explicit user acceptance for an outstanding compounder (CAP ≥15y AND moat ≥20/25
  AND documented pricing power); never auto-applied. Gate 4 still forces `tg ≤ 0%`
  for value destroyers. The prior Rf-based floor and the conflicting `min(Rf+10bps,
  3.5%)` / `Rf−100bps + tier` formulas are removed — a floor would raise tg and
  defeat conservatism. `wacc-capm` and `quality-roic` now defer to this rule.
- **Sector reference files completed (P2).** `defense.md`, `pharma.md`,
  `semiconductors.md`, `luxury.md`, `industrial.md` added under
  `sector-kpis/references/`; the router no longer points at missing files.
- **Default scenario block (P3).** Bear/base/bull with one-line driver + rough
  probability is now part of the default chat summary (was opt-in only).
- **Management guidance capture (P4).** Step 3 now captures the company's own
  guidance range alongside consensus and notes the gap as a signal.
- **xlsx export (P5).** `export_xlsx.py` reads `inputs["ebitda_margins"]` natively
  (legacy `ebit_margins` fallback retained) — the manual key patch is gone.
  `dcf_state.json` is the single required source; `financial_data.json`,
  `peers.json`, `confidence_data.json` are optional with graceful degradation.
- **Diff history removed from live instructions.** Version-change narration was
  stripped from the orchestrator and all skills; it lives here in the CHANGELOG.
- **R8 / R9 de-duplicated.** Each rule is stated once in DATA RULES and owned by
  its skill (`fcf-reconciliation`, `non_core_holdings.md`) rather than re-derived
  inline across every step.
- **Ceremony removed.** Dropped: the sha256 options-hash STOP-on-mismatch gate,
  legacy pre-v15.1/v15.2 state-reload detection, and the mandatory 2–4-sentence
  consensus-gap prose (demoted to a one-line gap reason). State files and R7
  derivation metadata are retained.
- **Option 8 simplified.** `book_value_add` and `consolidate_with_dividend_check`
  removed as selectable treatments; `dividend_only` (+ bull monetization overlay)
  is the supported method, with a one-line poor-disclosure fallback.

## v15.2

Fixes to four issues found in the v15.1 audit. All non-breaking (v15.1 INPUTS still run).

- **FCF bridge — same-period reconciliation.** `build_fcf_bridge` now reconciles a computed **UFCF_FY0** (from `inputs['ufcf_fy0']` or `inputs['fy0_actuals']`) to reported FCF_FY0, instead of comparing Y1 projected UFCF to FY0 reported FCF. The FY0→Y1 operating step (growth + ΔWC + capex) is reported separately as `growth_step_fy0_to_y1` and excluded from the residual gate. New helper `compute_ufcf_fy0()`. Fallback to Y1 makes the residual + R8 gates ADVISORY (non-binding) and says so.
- **R8 sign rule — same-period.** `enforce_ufcf_sign_rule` is now evaluated on `UFCF_FY0 − reported FCF_FY0`, removing the FY0→Y1 growth contamination that produced false violations (and false passes) for growing names.
- **R9 non-core dividend PV — mid-year/calendar-aware + FV info.** `value_non_core_holding` discounts with the parent's mid-year/calendar-aware offsets (was full-year `(1+r)^t`). Base case unchanged (dividend-only, conservative). Carrying value and look-through fair value are now surfaced as INFO ONLY (`balance_sheet_info`, aggregate `total_carrying_value_info` / `total_fair_value_info` / `dividend_pv_vs_fair_value_pct`) — never credited to base-case EV — so retain-and-compound stakes aren't silently zeroed.
- **Tornado pinned.** `TORNADO_SPEC` (8 variables) + `build_tornado()` / `format_tornado()` replace the never-shipped `sensitivity.py`. Versioned by `TORNADO_SPEC_VERSION`. R9-active runs append non-core dividend ±25%.
- **Calibration block.** `format_dcf_output` prints DCF implied vs consensus 12M target with the gap %, and a mandatory analyst gap-argument prompt.
- **Removed dead references.** `scenario.py`, `override.py`, `data_retrieval.py` (yfinance unreachable in sandbox), and `state_management.md` are no longer referenced — the engine functions cover them.


## v15.1 (current)

### New rules (skill-side)

- **Rule 8 — Sign-Aware UFCF Unlevering (BINDING)**: net interest position must be signed in INPUTS (`net_interest_position_fy0.net` positive for net debt, negative for net cash). Engine binding gate `enforce_ufcf_sign_rule` halts run if model UFCF direction disagrees with net interest sign (above 5% noise threshold). Catches the common error of treating net-cash companies (Renault, Dassault Aviation pre-Thales-distribution-flat, holding companies with cash reserves) with net-debt unlevering direction.
- **Rule 9 — Non-Core Holdings: Strip-Out + Dividend-as-FCF (BINDING)**: triggered by captive finance arms (≥10% group OI), equity-method stakes (≥10% mcap or NI), FVOCI/FVTPL equity stakes (≥10% mcap), or holding-co structures with separately listed subs. Strips revenue/EBITDA/D&A/capex from operating DCF, excludes captive debt from EV bridge, values stake as PV of actual dividend stream (cap 2% growth, terminal flat). Book/FV stake NEVER added to bridge (would double-count). Monetization optionality is a bull-case overlay only with named probability + friction discount. Full schema, treatment matrix, engine helpers, worked examples in `references/non_core_holdings.md`.

### New engine helpers (shipped in dcf_engine.py)

- `compute_net_interest_position(inputs)` — composes signed net interest from raw fields if user didn't pre-populate
- `enforce_ufcf_sign_rule(ufcf_y1, fcf_fy0, atx_net_fy0, noise_threshold=0.05)` — R8 binding gate, called automatically inside `build_fcf_bridge()`
- `strip_non_core_from_group(group_inputs, non_core_list)` — R9: returns operating-only inputs after stripping each non-core holding per Treatment Matrix. Respects `net_debt_basis` field to avoid double-stripping
- `value_non_core_holding(holding, parent_wacc, horizon)` — R9: PV of dividend stream + flat-terminal perpetuity, dividend growth capped at 2%
- `stress_test_dividend(holding, parent_wacc, floor_pct=0.30, wacc_premium_bps=200)` — R9: stress test for captive finance arms (historical worst-cycle dividend cuts to 25-40% of normal). Returns stress_pv used in bear-case scenarios
- `compute_non_core_aggregate(non_core_list, parent_wacc)` — R9: sums dividend PVs + bull monetization overlays + auto-applies stress test for captives
- `validate_non_core_no_double_count(state)` — R9: verifies no holding's book/FV appears in both dividend stream and any bridge line. Basis-aware: respects `net_debt_basis="operating_only"` (no strip expected)

### Engine behaviour changes (shipped)

- `run_dcf()` now auto-detects R9 via `non_core_holdings` field. If non-empty: calls `strip_non_core_from_group()` before dispatching to engine, then calls `compute_non_core_aggregate()` post-DCF to add PV to EV. Tracks pre-strip and post-strip totals for transparency (`enterprise_value_operating` vs `enterprise_value`).
- `run_dcf()` composes `net_interest_position_fy0` from raw fields if user didn't pre-populate (backwards compatible with `interest_expense_fy0`).
- `build_fcf_bridge()` rewritten with R8 sign-aware unlevering using signed `atx_net`. Subtracts sum of non-core dividends received from reported parent FCF before reconciling to operating UFCF (prevents double-count: dividends-received are in reported FCF but the DCF values them separately via R9). Embeds `r8_sign_check` and `r9_dividend_strip` blocks in returned bridge dict.
- `format_dcf_output()` extended to include: (a) R8 sign-direction confirmation line, (b) NON-CORE HOLDINGS block when R9 active, listing per-holding type, treatment, fy0_dividend, PV, stress test result, monetization overlay status, (c) expanded equity bridge showing `EV_operating + PV(non_core) − operating_net_debt − ...`, (d) Option 8 row in MODELLING DECISIONS APPLIED block.
- `resolve_modelling_options()` signature extended to accept `non_core_holdings` (third arg) and emits Option 8 resolution (default `dividend_only` when R9 fires, else `n_a`).

### Cyclical sector list expanded (v15.1)

Added: Container Shipping, Liner Shipping, Trucking, Road Transport, Aluminum, Copper, Base Metals, Paper & Packaging, Capital Equipment, Industrial Machinery, Construction Machinery, Specialty Chemicals.

Total cyclical sectors: 35 entries (was 18 in v15.0).

### net_debt contract (v15.1)

New top-level `net_debt_basis` field required when R9 active:
- `"operating_only"` — analyst pre-stripped (e.g., Renault auto net cash); engine doesn't double-strip
- `"group_consolidated"` (or absent) — engine strips captive debt and trapped cash

Wrong choice → engine prints `_strip_debt_reason` and the bridge errors visibly.

### Migration from v15.0

- Add `interest_expense` AND `interest_income` (gross, both positive) to financial_data.json. Compose `net_interest_position_fy0` in INPUTS per R8 schema. OR keep legacy `interest_expense_fy0` for backwards compatibility (engine assumes net debt direction).
- Add `non_core_holdings` (list, possibly empty) to INPUTS. Populate per schema in `references/non_core_holdings.md` whenever R9 triggers.
- Add `net_debt_basis` to top-level INPUTS when R9 active.
- Add `segment_revenue`, `segment_ebitda`, `segment_capex`, `segment_dividend_to_parent` (per non-core holding) to financial_data.json when R9 fires.
- Step 1b extended with R9 trigger screen.
- Step 2 extended with per-non-core-holding figure collection.
- Step 6.5 Option 8 added (now 8 options total).
- Step 7 FCF bridge: dividend strip line added; R8 sign gate enforced.

**Legacy state files** (pre-v15.1) with equity-method carrying value in bridge, captive EBITDA in group projections, or FVOCI fair value in bridge are flagged on reload. Affected: Renault (×3), Dassault Aviation (×2), Stellantis, Ferrari (×2 Exor cross-refs), Bolloré-related analyses. Re-run recommended.

### Sector-kpis additions (v15.1)

- `references/autos.md` — new file. Captive finance trigger thresholds for all major OEMs, through-cycle margins by sub-segment, BEV transition capex norms, CO2 fines exposure, Chinese OEM competition framing, quality scoring adjustments, capital allocation track record patterns.
- `references/software.md` — updated with deferred revenue/RPO handling, SaaS WC sub-default (`dwc_pct = -3%` when subscription >70%), currency hedging section, SaaS-specific red flags (NRR <100%, CAC payback >36m, SBC-vs-revenue growth, deferred revenue deceleration), worked examples (Pure SaaS / Hybrid / Services-heavy).

---

## v15

### New helpers (engine)

- `resolve_modelling_options(sector, financials)` — sector default resolution for all 7 options with triggers carrying reason + impact strings
- `is_cyclical_sector(sector)` — identifies sectors requiring 10Y through-cycle terminal margin
- `cycle_position_check(fy0_margin, through_cycle_margin)` — returns cycle status + cycle_peak_fy0 flag
- `enforce_value_destruction_gate(inputs, roic_data)` — BINDING GATE 4: caps tg at 0% when incremental ROIC < WACC for 3+ years (auto-called inside run_dcf)
- `compute_roic_history(financials, tax_rate, wacc)` — 3Y ROIC trajectory (incl/ex GW), incremental, CV
- `compute_quality_score(...)` — 6-dim composite + tier
- `compute_capital_allocation_score(channels)` — 5-channel weighted composite
- `compute_implied_cap(inputs, target_price)` — reverse CAP solver (bisection 3..25y)
- `project_share_count(...)` — buyback-adjusted per-year share trajectory
- `check_base_rates(inputs)` — Mauboussin plausibility checks
- `format_quality_summary(...)` — Step 5 chat block

### Engine behaviour changes

- **SBC cash-cost wiring**: when `modelling_options.sbc == "cash_cost"`, the EBITDA engine subtracts `sbc_pct_of_revenue` from every projected margin BEFORE the DCF run. Previously this option had no engine-side effect.
- **Cycle position auto-detection**: when `sector` + `fy0_normalised_ebitda_margin` + `through_cycle_margin` are in inputs, engine runs cycle position check and exposes `cycle_position` in output.
- **BINDING GATE 4 auto-enforcement**: `run_dcf` now calls `enforce_value_destruction_gate` before dispatching to engine. Sets `terminal_growth_pre_gate` in inputs metadata when fired, plus `binding_gate_4_fired` + `binding_gate_4_message` in output.
- **Transparency disclosure**: `format_dcf_output` rewritten with a "MODELLING DECISIONS APPLIED" block showing per-option status (DEFAULT / TRIGGERED / USER OVERRIDE), trigger reason, valuation impact, plus separate sub-blocks for SBC adjustment, cycle position, and any binding gate fired.

### New rules (skill-side, not engine code)

- Cyclical normalisation: through-cycle 10Y margin for {Autos, Chemicals, Shipping, Steel, Construction Materials, Upstream Energy, Semis Equipment, Memory Semis, Airlines, Refining}
- Quality-tiered recommendation thresholds (HIGH QUALITY +10% / standard +15% / LOW QUALITY +25% / VALUE TRAP RISK +40%)
- BINDING GATE 3: cyclical + terminal margin > through-cycle + 100bps → revert
- BINDING GATE 4: incremental ROIC < WACC 3+y → tg ≤ 0%
- 13 red flags (was 9): added incremental ROIC trend, M&A intensity vs multiples, share count trajectory, cycle position

### Preserved from v14

- Calendar-aware discounting (analysis_date, fiscal_year_end_month, last_completed_fy)
- NOPAT-native engine for asset-heavy sectors
- Tax fade (tax_fade[10])
- Terminal WACC override (Option 6)
- FCF reconciliation bridge (binding 10% residual)
- Modelling options hash for reproducibility
- Hard sector routing (banks/insurance → equity-financials)
- Engine emits engine_version, modelling_options_hash, discount_convention, derivations, consensus_snapshot

### Migration from v14

- Add `ppe_net` to financial_data.json (required for ROIC computation)
- Add `sbc_pct_of_revenue` to INPUTS when Option 4 = `cash_cost`
- Add `fy0_normalised_ebitda_margin` + `through_cycle_margin` + `sector` to INPUTS for cyclical sectors
- Add `roic_data` (from `compute_roic_history`) + `incremental_destroys_3y_consecutive` (bool) to INPUTS to enable BINDING GATE 4
- Step 5 reorganised around Quality / CAP / Capital Allocation / Mispricing (orchestrator-side)
- Recommendation thresholds quality-tiered in Step 8 (orchestrator-side)
- Red flag table extended to 13 items

---- (previous versions) ----
# equity-dcf — CHANGELOG

## v15.1 (current)

### New rules (skill-side)

- **Rule 8 — Sign-Aware UFCF Unlevering (BINDING)**: net interest position must be signed in INPUTS (`net_interest_position_fy0.net` positive for net debt, negative for net cash). Engine binding gate `enforce_ufcf_sign_rule` halts run if model UFCF direction disagrees with net interest sign (above 5% noise threshold). Catches the common error of treating net-cash companies (Renault, Dassault Aviation pre-Thales-distribution-flat, holding companies with cash reserves) with net-debt unlevering direction.
- **Rule 9 — Non-Core Holdings: Strip-Out + Dividend-as-FCF (BINDING)**: triggered by captive finance arms (≥10% group OI), equity-method stakes (≥10% mcap or NI), FVOCI/FVTPL equity stakes (≥10% mcap), or holding-co structures with separately listed subs. Strips revenue/EBITDA/D&A/capex from operating DCF, excludes captive debt from EV bridge, values stake as PV of actual dividend stream (cap 2% growth, terminal flat). Book/FV stake NEVER added to bridge (would double-count). Monetization optionality is a bull-case overlay only with named probability + friction discount. Full schema, treatment matrix, engine helpers, worked examples in `references/non_core_holdings.md`.

### New engine helpers (shipped in dcf_engine.py)

- `compute_net_interest_position(inputs)` — composes signed net interest from raw fields if user didn't pre-populate
- `enforce_ufcf_sign_rule(ufcf_y1, fcf_fy0, atx_net_fy0, noise_threshold=0.05)` — R8 binding gate, called automatically inside `build_fcf_bridge()`
- `strip_non_core_from_group(group_inputs, non_core_list)` — R9: returns operating-only inputs after stripping each non-core holding per Treatment Matrix. Respects `net_debt_basis` field to avoid double-stripping
- `value_non_core_holding(holding, parent_wacc, horizon)` — R9: PV of dividend stream + flat-terminal perpetuity, dividend growth capped at 2%
- `stress_test_dividend(holding, parent_wacc, floor_pct=0.30, wacc_premium_bps=200)` — R9: stress test for captive finance arms (historical worst-cycle dividend cuts to 25-40% of normal). Returns stress_pv used in bear-case scenarios
- `compute_non_core_aggregate(non_core_list, parent_wacc)` — R9: sums dividend PVs + bull monetization overlays + auto-applies stress test for captives
- `validate_non_core_no_double_count(state)` — R9: verifies no holding's book/FV appears in both dividend stream and any bridge line. Basis-aware: respects `net_debt_basis="operating_only"` (no strip expected)

### Engine behaviour changes (shipped)

- `run_dcf()` now auto-detects R9 via `non_core_holdings` field. If non-empty: calls `strip_non_core_from_group()` before dispatching to engine, then calls `compute_non_core_aggregate()` post-DCF to add PV to EV. Tracks pre-strip and post-strip totals for transparency (`enterprise_value_operating` vs `enterprise_value`).
- `run_dcf()` composes `net_interest_position_fy0` from raw fields if user didn't pre-populate (backwards compatible with `interest_expense_fy0`).
- `build_fcf_bridge()` rewritten with R8 sign-aware unlevering using signed `atx_net`. Subtracts sum of non-core dividends received from reported parent FCF before reconciling to operating UFCF (prevents double-count: dividends-received are in reported FCF but the DCF values them separately via R9). Embeds `r8_sign_check` and `r9_dividend_strip` blocks in returned bridge dict.
- `format_dcf_output()` extended to include: (a) R8 sign-direction confirmation line, (b) NON-CORE HOLDINGS block when R9 active, listing per-holding type, treatment, fy0_dividend, PV, stress test result, monetization overlay status, (c) expanded equity bridge showing `EV_operating + PV(non_core) − operating_net_debt − ...`, (d) Option 8 row in MODELLING DECISIONS APPLIED block.
- `resolve_modelling_options()` signature extended to accept `non_core_holdings` (third arg) and emits Option 8 resolution (default `dividend_only` when R9 fires, else `n_a`).

### Cyclical sector list expanded (v15.1)

Added: Container Shipping, Liner Shipping, Trucking, Road Transport, Aluminum, Copper, Base Metals, Paper & Packaging, Capital Equipment, Industrial Machinery, Construction Machinery, Specialty Chemicals.

Total cyclical sectors: 35 entries (was 18 in v15.0).

### net_debt contract (v15.1)

New top-level `net_debt_basis` field required when R9 active:
- `"operating_only"` — analyst pre-stripped (e.g., Renault auto net cash); engine doesn't double-strip
- `"group_consolidated"` (or absent) — engine strips captive debt and trapped cash

Wrong choice → engine prints `_strip_debt_reason` and the bridge errors visibly.

### Migration from v15.0

- Add `interest_expense` AND `interest_income` (gross, both positive) to financial_data.json. Compose `net_interest_position_fy0` in INPUTS per R8 schema. OR keep legacy `interest_expense_fy0` for backwards compatibility (engine assumes net debt direction).
- Add `non_core_holdings` (list, possibly empty) to INPUTS. Populate per schema in `references/non_core_holdings.md` whenever R9 triggers.
- Add `net_debt_basis` to top-level INPUTS when R9 active.
- Add `segment_revenue`, `segment_ebitda`, `segment_capex`, `segment_dividend_to_parent` (per non-core holding) to financial_data.json when R9 fires.
- Step 1b extended with R9 trigger screen.
- Step 2 extended with per-non-core-holding figure collection.
- Step 6.5 Option 8 added (now 8 options total).
- Step 7 FCF bridge: dividend strip line added; R8 sign gate enforced.

**Legacy state files** (pre-v15.1) with equity-method carrying value in bridge, captive EBITDA in group projections, or FVOCI fair value in bridge are flagged on reload. Affected: Renault (×3), Dassault Aviation (×2), Stellantis, Ferrari (×2 Exor cross-refs), Bolloré-related analyses. Re-run recommended.

### Sector-kpis additions (v15.1)

- `references/autos.md` — new file. Captive finance trigger thresholds for all major OEMs, through-cycle margins by sub-segment, BEV transition capex norms, CO2 fines exposure, Chinese OEM competition framing, quality scoring adjustments, capital allocation track record patterns.
- `references/software.md` — updated with deferred revenue/RPO handling, SaaS WC sub-default (`dwc_pct = -3%` when subscription >70%), currency hedging section, SaaS-specific red flags (NRR <100%, CAC payback >36m, SBC-vs-revenue growth, deferred revenue deceleration), worked examples (Pure SaaS / Hybrid / Services-heavy).

---

## v15

### New helpers (engine)

- `resolve_modelling_options(sector, financials)` — sector default resolution for all 7 options with triggers carrying reason + impact strings
- `is_cyclical_sector(sector)` — identifies sectors requiring 10Y through-cycle terminal margin
- `cycle_position_check(fy0_margin, through_cycle_margin)` — returns cycle status + cycle_peak_fy0 flag
- `enforce_value_destruction_gate(inputs, roic_data)` — BINDING GATE 4: caps tg at 0% when incremental ROIC < WACC for 3+ years (auto-called inside run_dcf)
- `compute_roic_history(financials, tax_rate, wacc)` — 3Y ROIC trajectory (incl/ex GW), incremental, CV
- `compute_quality_score(...)` — 6-dim composite + tier
- `compute_capital_allocation_score(channels)` — 5-channel weighted composite
- `compute_implied_cap(inputs, target_price)` — reverse CAP solver (bisection 3..25y)
- `project_share_count(...)` — buyback-adjusted per-year share trajectory
- `check_base_rates(inputs)` — Mauboussin plausibility checks
- `format_quality_summary(...)` — Step 5 chat block

### Engine behaviour changes

- **SBC cash-cost wiring**: when `modelling_options.sbc == "cash_cost"`, the EBITDA engine subtracts `sbc_pct_of_revenue` from every projected margin BEFORE the DCF run. Previously this option had no engine-side effect.
- **Cycle position auto-detection**: when `sector` + `fy0_normalised_ebitda_margin` + `through_cycle_margin` are in inputs, engine runs cycle position check and exposes `cycle_position` in output.
- **BINDING GATE 4 auto-enforcement**: `run_dcf` now calls `enforce_value_destruction_gate` before dispatching to engine. Sets `terminal_growth_pre_gate` in inputs metadata when fired, plus `binding_gate_4_fired` + `binding_gate_4_message` in output.
- **Transparency disclosure**: `format_dcf_output` rewritten with a "MODELLING DECISIONS APPLIED" block showing per-option status (DEFAULT / TRIGGERED / USER OVERRIDE), trigger reason, valuation impact, plus separate sub-blocks for SBC adjustment, cycle position, and any binding gate fired.

### New rules (skill-side, not engine code)

- Cyclical normalisation: through-cycle 10Y margin for {Autos, Chemicals, Shipping, Steel, Construction Materials, Upstream Energy, Semis Equipment, Memory Semis, Airlines, Refining}
- Quality-tiered recommendation thresholds (HIGH QUALITY +10% / standard +15% / LOW QUALITY +25% / VALUE TRAP RISK +40%)
- BINDING GATE 3: cyclical + terminal margin > through-cycle + 100bps → revert
- BINDING GATE 4: incremental ROIC < WACC 3+y → tg ≤ 0%
- 13 red flags (was 9): added incremental ROIC trend, M&A intensity vs multiples, share count trajectory, cycle position

### Preserved from v14

- Calendar-aware discounting (analysis_date, fiscal_year_end_month, last_completed_fy)
- NOPAT-native engine for asset-heavy sectors
- Tax fade (tax_fade[10])
- Terminal WACC override (Option 6)
- FCF reconciliation bridge (binding 10% residual)
- Modelling options hash for reproducibility
- Hard sector routing (banks/insurance → equity-financials)
- Engine emits engine_version, modelling_options_hash, discount_convention, derivations, consensus_snapshot

### Migration from v14

- Add `ppe_net` to financial_data.json (required for ROIC computation)
- Add `sbc_pct_of_revenue` to INPUTS when Option 4 = `cash_cost`
- Add `fy0_normalised_ebitda_margin` + `through_cycle_margin` + `sector` to INPUTS for cyclical sectors
- Add `roic_data` (from `compute_roic_history`) + `incremental_destroys_3y_consecutive` (bool) to INPUTS to enable BINDING GATE 4
- Step 5 reorganised around Quality / CAP / Capital Allocation / Mispricing (orchestrator-side)
- Recommendation thresholds quality-tiered in Step 8 (orchestrator-side)
- Red flag table extended to 13 items
