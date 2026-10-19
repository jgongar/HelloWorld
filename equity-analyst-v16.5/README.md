# Equity Analyst v16.5 — patch for the v16.4 prompt and skills

v16.5 fixes the problems found when four v16.4 analyses (Hermès, Equasens, Hexaom, LNA Santé) were re-checked. Each v16.4 conclusion was more extreme than the review, in both directions. None of the scenario sets bracketed the price, and the Hermès SELL was a discount-rate choice presented as a growth edge.

## What to install

| File | Where it goes |
|---|---|
| `zips/equity-dcf.zip` | claude.ai → Settings → Capabilities → Skills: replace the existing **equity-dcf** skill |
| `zips/wacc-capm.zip` | same place: replace **wacc-capm** |
| `zips/quality-roic.zip` | same place: replace **quality-roic** |
| `SYSTEM_PROMPT_v16.5.md` | paste over the v16.4 text in your project's instructions |

Each zip holds one folder named after the skill, with `SKILL.md` inside; that is the layout claude.ai expects. Skills not listed here (base-rates, capital-allocation, fcf-reconciliation, modelling-options, sector-kpis, export-md, export-xlsx, equity-financials) are unchanged and still compatible: the engine only added output keys.

**Check before uploading:** these files are built on the v16.4 skills synced to your account on 19 Oct 2026, whose engine still reports `v16.4`. The Equasens session drafted an `equity-dcf` v16.4.1, with a sensitivity-grid function and an analysis-pack helper for the new Excel template. If you uploaded that afterwards, this zip replaces it, and those two functions would need to be merged back in.

## What changed and why

| Problem found in the reviews | Seen in | v16.5 fix | Where |
|---|---|---|---|
| Spot Bund paired with a fixed 5.5% "Damodaran" ERP (measured: 4.20%) | Hermès | One coherent convention: spot Bund + Damodaran's current implied ERP. Normalised Rf + long-run ERP is used only for the range | wacc-capm, `wacc_capm_range` |
| Equity beta used for a net-cash company | Hermès | Operating beta on excess cash | `cash_adjusted_beta` |
| OAT for some French names, Bund for others | Hexaom, Equasens, LNA vs Hermès | Bund for every euro issuer; country risk premium (CRP) weighted by revenue | wacc-capm |
| Betas of 0.51 / 0.58 for thinly traded stocks | LNA, Equasens | Beta-quality check: highest of measured, Blume-adjusted and industry beta | `beta_quality_check` |
| WACC uncertainty never tested | all | Defensible `wacc_range`; a rating that changes inside it is capped at HOLD | `rating_robustness`, Step 7e/8 |
| Waterfall lumped WACC with long-term growth, so a rate gap was read as a growth edge | Hermès | Separate discount-rate step inside the range; `gap_mostly` | `gap_waterfall` |
| "What the price assumes" shown at one WACC only | Hermès | Implied growth also shown at both ends of the range | `what_must_be_true` |
| Edge template forced a story | all four | Third form: "no fundamental edge, discount rate" (caps at HOLD); catalyst must remove the persistence reason; a sudden fall must be explained first | prompt Step 5.6 |
| Growth to terminal rate right after Y10 despite a 20-year CAP | Hermès | Fade stage Y11–Y(CAP) | Rule 3D, quality-roic |
| Scenarios move one driver; bears too mild; none reaches the price | all four | One root cause with linked drivers, bear floor at the company's worst year, mandatory market-consistent scenario | `run_scenarios`, `build_market_consistent_scenario` |
| Acquisition-driven growth with no acquisition spending | Equasens | Growth-paid-for check (⛔ when the RONIC gate fired); `acquisition_spend` in UFCF | Rule 3E |
| Working capital released cash as revenue fell | Hexaom | Asymmetric ΔNWC: no release on decline without evidence | `_project` |
| Margins held fixed while revenue collapsed | Hexaom | Optional operating leverage (`fixed_cost_share`, 3-year cost catch-up) | `_project`, solvers |
| Margin set exactly at the gate cap | Hexaom | `gate_cap_check`: price at the anchor shown alongside | Step 6 |
| Placements, related-party accounts and seasonal peaks counted as spare cash; post-period acquisition not deducted | Equasens, Hexaom | `net_cash_quality` | R12 |
| Stale FY25 balance sheet when H1-26 was out; wrong debt figure | LNA | Latest balance sheet rule (R4b) | prompt |
| Claims deducted outside the engine, so the market EV and the DCF bridge disagreed | LNA | `other_claims`, one claims definition everywhere | `_claims` |
| Headline not updated after follow-ups contradicted it | Equasens, Hexaom, LNA | Follow-up rule: re-run and restate the rating | prompt |
| Consensus target stale after a 23% price fall; exit triggers that fire on seasonality | Hexaom | R5 staleness includes price move; exit triggers back-tested on 3 years | prompt |
| Peer-multiple value shown when meaningless | Hermès, LNA | € value only if margin ≤ 1.5× peer 75th percentile | Step 7c |

**Rating thresholds:** v16.4 gave SELL thresholds only for HIGH QUALITY and VALUE TRAP RISK. v16.5 adds Standard SELL < −15% and LOW QUALITY SELL < −10%. These are my choice; change `RATING_THRESHOLDS` in the engine and Step 8 if you prefer others.

## Tests

`python3 tests/test_engine_v165.py [path/to/v16.4/dcf_engine.py]`: 32 checks, all passing.
- v16.4 inputs price identically under v16.5.
- Each new rule moves the value in the intended direction.
- The waterfall still adds up, and solvers at their bounds are marked N/M.
- Scenario bracket check, market-consistent scenario, bear floor, rating robustness, WACC helpers, cash quality and gate cap all behave as specified.

`python3 tests/hermes_reconstruction.py` rebuilds the Hermès v16.4 run from its published summary. D&A of 3.5% (ex right-of-use), minorities and pensions are my estimates. The rebuild reproduces the published run: €1,096 vs €1,094, TV 61.3%, exit 10.1x, breakeven WACC 7.94%, implied Y3–Y10 CAGR 11.0%.

Under v16.5 rules, the same inputs give:
- WACC 8.15% (spot Bund 3.42% + operating β 1.13 × implied ERP 4.20%), range 8.15–8.69%;
- with CAP 20, €1,353 (+1.2%): a HOLD that holds across the range;
- a gap that is mostly discount rate and closes at 8.32%;
- scenarios that bracket the price.

This is a rebuild, not a new analysis: a real v16.5 run re-sources every input.
