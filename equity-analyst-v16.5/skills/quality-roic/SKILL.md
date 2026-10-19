---
name: quality-roic
description: >
  Quality scoring, ROIC computation, and Competitive Advantage Period (CAP)
    framework for equity analysis (v16.5). Loaded at start of Step 5 of every
  non-financials analysis. Owns the quality score (1-10), the ROIC and
  incremental ROIC trajectory, the CAP duration assumption that drives the
  margin fade, the post-Y10 growth fade stage AND the terminal RONIC, and the
  competitive-position block that
  justifies the moat score. Also triggered by `show quality`, `show roic`,
  `set cap {years}`, `set ronic {x}`.
---

# Quality, ROIC & Competitive Advantage Period — v16.5

v16.5 changes: (1) CAP > 10 now runs an explicit growth fade stage Y11..Y(CAP)
in the engine (pass `cap_years`) — v16.4 dropped growth to tg straight after
Y10 even with a 20-year CAP; (2) the CAP table says exactly what CAP governs
(margins inside Y10, growth beyond Y10, terminal RONIC); (3) the pooled
incremental ROIC also feeds `check_growth_paid_for` (`equity-dcf` Rule 3E):
when it is below WACC, explicit-period growth must carry its acquisition spend.

v16.4 changes: (1) invested capital is EX-leases and NOPAT is lease-adjusted
(rent-as-opex, consistent with the DCF); (2) the gate statistic is the POOLED
3Y incremental ROIC — per-year ratios are information only; (3) CAP now drives
the terminal RONIC (value-driver TV), so CAP ≥ 15y has a valuation effect;
(4) the reverse-CAP solver is gone — "what the market prices" is the
per-driver `what_must_be_true` table from the engine; (5) a 5-line
competitive-position block precedes and justifies the moat sub-scores.

Step 5 reorders the analytical core around three questions:
1. **Is this a quality business?** — ROIC vs WACC
2. **For how long?** — Competitive Advantage Period (CAP)
3. **Where is the market wrong?** — mispricing thesis

DCF (Step 7) becomes confirmation, not source of answer.

Loads at Step 5 for non-financials. Financials route to `equity-financials` (RoTE for banks, RoEV for life insurers, combined ratio quality for P&C).

## ROIC — Definition and Computation

### Canonical Formula

```
ROIC = NOPAT / Invested Capital

NOPAT = (EBIT − lease interest) × (1 − cash tax rate)
Invested Capital (incl-GW) = Total Debt + Equity − Cash          (EX-leases)
Invested Capital (ex-GW)   = above − Goodwill
```

⛔ **Rent-as-opex consistency (v16.4).** The DCF treats leases as an operating
cost (Rule 3C), so ROIC must too: lease interest comes out of EBIT and the
lease liability stays out of IC. Supply `lease_interest` per FY (from the
finance-cost note or CF statement); if absent for a lease-heavy name the engine
raises `ic_leases_note` (ROIC modestly overstated) — log it in 9b.

**Two flavours, both reported:**

- **ROIC including goodwill**: shows the return management has actually
  earned on capital deployed (including acquisitions). The shareholder's
  perspective.
- **ROIC excluding goodwill**: shows the underlying operating economics.
  The franchise's perspective.

The gap between the two tells you whether M&A has destroyed or created
value. If ROIC-incl-goodwill < ROIC-ex-goodwill by >300bps for >2 years,
flag as capital allocation red flag (feeds into capital-allocation skill).

### Incremental ROIC (the compounding engine)

```
Incremental ROIC_Y = ΔNOPAT_Y / ΔInvested_Capital_(Y-1 → Y)
```

This is what determines whether reinvestment creates or destroys value.
A business earning 30% ROIC on legacy capital but 8% on incremental
capital is a melting ice cube dressed as a compounder.

**Gate statistic (v16.4): POOLED 3Y incremental ROIC** = ΔNOPAT(FY-3→FY0) /
ΔIC(FY-3→FY0), engine key `incremental_roic`. If it is below WACC the engine's
RONIC gate sets terminal RONIC = WACC (growth becomes value-neutral in the TV)
and prints the flag; the recommendation must note "reinvestment has not earned
its cost of capital". Per-year ratios (`incremental_series`) are shown for
information only — single-year ΔNOPAT/ΔIC is too noisy to gate on (commodity
cycles, OCI swings, M&A timing). ΔIC ≤ 0 over the span → gate inert (capital
returned is not reinvested badly). Collect 5 FYs of {ebit, total_debt,
total_equity, cash, goodwill, lease_interest}; 4 FYs is the minimum for a 3Y span.

### Computation Workflow

In Step 2 (data collection), the LLM must populate PER FY over **FY-4..FY0**
(5Y window — this is what makes Dim 2's CV rubric computable and Gate 4
engine-verifiable):
- `total_debt`, `total_equity`, `cash`, `goodwill`, `ebit`, `lease_interest` (0 if no leases)
- Latest FY only: `other_intangibles`, `ppe_net`, `working_capital`
  (derived: trade_recv + inventories − trade_payables)

The engine (`compute_roic_history`) then computes for each FY in the window:
```python
invested_capital_incl_gw = total_debt + total_equity - cash          # ex-leases
invested_capital_ex_gw   = invested_capital_incl_gw - goodwill
nopat = (ebit - lease_interest) * (1 - tax_rate)
roic_incl_gw = nopat / avg(invested_capital_incl_gw_Y, _Y-1)
roic_ex_gw   = nopat / avg(invested_capital_ex_gw_Y, _Y-1)
# plus: pooled 3Y incremental_roic (gate), per-year incremental_series (info),
# roic_cv over up to 4 observations
```

Output to chat (one line):
> "ROIC ({N}Y avg): {X}% incl-GW / {Y}% ex-GW (ex-leases IC). WACC: {W}%.
> Spread: {±X − W}ppt. Incremental ROIC (pooled 3Y): {Z}% — {above WACC / ⛔ below WACC → RONIC gate}." 

## Quality Score (1–10)

Six dimensions, each 1–10, equal-weighted. The composite quality score
is the arithmetic mean rounded to one decimal.

| # | Dimension | What scores high |
|---|-----------|------------------|
| 1 | **ROIC level vs WACC** | Sustained spread >1000bps = 10; below WACC = 1 |
| 2 | **ROIC stability** | Coefficient of variation (5Y) <10% = 10; >40% = 1 |
| 3 | **Moat** (qualitative) | Wide moat, multiple sources = 10; commodity = 1 |
| 4 | **Reinvestment runway** | Long, capital-light runway = 10; saturated = 1 |
| 5 | **Capital allocation track record** | (loaded from capital-allocation skill) |
| 6 | **Balance-sheet resilience** (v16.1) | Net cash = 10; ND/EBITDA <1x, strong coverage = 8–9; >4x or coverage <2x = 1–2 |

### Scoring Mechanics

**Dimension 1 — ROIC level vs WACC:**
```
Spread (bps) | Score
> 2000       | 10
1500-2000    | 9
1000-1500    | 8
700-1000     | 7
500-700      | 6
300-500      | 5
100-300      | 4
0-100        | 3
-200-0       | 2
< -200       | 1
```

**Dimension 2 — ROIC stability:**
Coefficient of variation of ROIC over last 5Y (excluding COVID year if
distortion >500bps documented). CV = σ / μ.
```
CV         | Score
< 0.05     | 10
0.05-0.10  | 9
0.10-0.15  | 8
0.15-0.20  | 7
0.20-0.25  | 6
0.25-0.30  | 5
0.30-0.40  | 4
0.40-0.50  | 3
0.50-0.75  | 2
> 0.75     | 1
```

**Dimension 3 — Moat (qualitative, 5 sub-factors) — preceded by the COMPETITIVE POSITION BLOCK (v16.4, mandatory):**

Five lines, each with a sourced fact, printed in chat before the moat scores:
1. **Cost/price position** — where the company sits on the industry cost curve or price ladder (gross margin vs peers, price premium/discount).
2. **Share trend (3Y)** — market share direction in the core segment, with the number.
3. **Pricing power** — realised price/mix vs CPI over 3Y (segment disclosure or guidance); measured, not assumed.
4. **Concentration** — top-customer / top-supplier / top-product share of revenue.
5. **Structural change** — the one industry event (technology, regulation, entrant, substitute) that would reset returns; probability band.

The moat sub-scores must be consistent with these five lines; an 18/25 with no pricing-power evidence is a scoring error. Score each sub-factor 1-5;
total /25, then map to 1-10 quality dimension. Sub-factors:
- Switching costs
- Network effects
- Cost advantages (scale, geography, process)
- Intangible assets (brand, IP, regulatory)
- Efficient scale (natural monopoly / oligopoly)

Mapping: ≥20 → 10; 17-19 → 8; 14-16 → 6; 11-13 → 4; ≤10 → 2.

**Dimension 4 — Reinvestment runway:**
What share of current FCF can be productively reinvested at attractive
returns, for how long?

| Profile | Score |
|---------|-------|
| Long runway (>15Y), high incremental ROIC, capital-light | 10 |
| Long runway, moderate incremental ROIC | 8 |
| Medium runway (5-15Y), high incremental ROIC | 7 |
| Medium runway, moderate returns | 5 |
| Short runway (<5Y) or saturating market | 3 |
| No reinvestment opportunity — return all capital | 5 (neutral, not bad) |
| Forced reinvestment at low returns | 1 |

Note: "no reinvestment, return capital" is neutral, not penalised — a
mature business that pays out 100% at 25% ROIC is a great holding.
What's penalised is forced low-return reinvestment.

**Dimension 5 — Capital allocation track record:**
Loaded from capital-allocation skill. Default if not run: 5 (neutral).
See capital-allocation/SKILL.md for the rubric.

**Dimension 6 — Balance-sheet resilience (v16.1):**

Rationale for the change: the old "earnings predictability" (revenue CV +
margin CV) was ~80% the same signal as Dim 2 (ROIC CV) — volatility was
double-counted while leverage, the classic quality-killer, was absent from the
composite entirely. Dim 6 now scores the balance sheet. Inputs (all already
collected in Step 2): `net_debt_incl_leases = total_debt + lease_liabilities −
cash`, FY0 normalised EBITDA, FY0 IFRS EBIT, FY0 gross interest expense.

```
ND(incl leases)/EBITDA | Base score
net cash (ND ≤ 0)      | 10
< 0.5x                 | 9
0.5–1.0x               | 8
1.0–1.5x               | 7
1.5–2.0x               | 6
2.0–2.5x               | 5
2.5–3.0x               | 4
3.0–4.0x               | 3
4.0–5.0x               | 2
> 5.0x                 | 1

Interest-coverage modifier (EBIT / gross interest expense):
  coverage < 4x → −1
  coverage < 2x (or EBIT ≤ 0 with interest due) → −2
Floor 1, cap 10.
```

Notes (v16.4): leases do NOT count as debt here (rent-as-opex — consistent with
the EV bridge and the ex-leases ROIC); use `net_debt` = total_debt − cash and the
rent-as-opex EBITDA. Excess-cash hoarding is NOT penalised in this dimension
— capital discipline is Dim 5's job. Financial-sector leverage is out of scope
(financials route to `equity-financials`). Pension deficits are excluded from
the ratio but a deficit >1x EBITDA warrants a −1 judgment adjustment, noted.

Engine implementation: `compute_quality_score(..., balance_sheet_data)` with
`{net_debt, ebitda, ebit, interest_expense}` (key `net_debt_incl_leases` still accepted).

### Quality Threshold (configurable, default 6.5)

The scored approach means valuation always runs, but the recommendation
prefix changes:

- Composite ≥ 8.0 → "HIGH QUALITY" prefix (e.g. "HIGH QUALITY BUY")
- Composite 6.5–7.9 → no prefix (standard recommendation)
- Composite 5.0–6.4 → "LOW QUALITY" prefix
- Composite < 5.0 → "VALUE TRAP RISK" prefix + mandatory pre-mortem
  emphasis on capital allocation

The threshold can be overridden per analysis with `set quality_threshold {X}`
if you're explicitly hunting deep value.

## Competitive Advantage Period (CAP)

### What CAP Actually Is

CAP is the number of years a business can sustain ROIC > WACC. In v16.5 it does
three jobs: it governs the margin fade inside the 10Y explicit forecast, it sets
the length of the post-Y10 growth fade stage (engine, Rule 3D), and it sets the
terminal RONIC in the value-driver TV. A CAP beyond Y10 is never decorative.

Mauboussin's empirical finding (Credit Suisse HOLT data, decades of work):
- Median CAP across all listed companies ≈ 8-10 years
- Wide-moat businesses (mostly franchise) can sustain 15-25 years
- A handful of legendary compounders sustain >25Y (Berkshire, Costco,
  Hermès, ASML — and the market typically prices these correctly)

### How CAP Drives the Assumption Table

CAP is an explicit input that drives the assumption table: it sets the fade
behaviour of the 10Y forecast (per the table above) rather than leaving "fade to
terminal" implicit and arbitrary.

| CAP (yrs) | Margins Y1–min(CAP, 10) | Y(CAP+1)–Y10 | Growth beyond Y10 (engine fade stage) | Terminal RONIC (`ronic`) |
|---|---|---|---|---|
| ≤ 5 (short) | Thesis | Linear fade to peer-median margin; growth fades to GDP | none — TV at Y10 | = WACC |
| 10 (median) | Thesis | — | none — TV at Y10 | = WACC |
| 15 (strong) | Thesis | — | Y11–Y15: growth fades linearly from Y10 growth to tg | = WACC + 50% × (ROIC ex-GW 5Y avg − WACC) |
| 20+ (wide moat) | Thesis | — | Y11–Y(CAP), max Y30: growth fades linearly to tg | = WACC + 100% × spread, capped at 25% |

What "thesis" means: margins follow the Step 6 thesis path (consensus/guidance
anchor Y1–Y2, thesis Y3+); CAP does not force them down inside its window. Revenue
growth inside Y1–Y10 is always the Step 6 driver path (decomposed Y1–Y3, thesis
Y4+); CAP does not fade growth inside Y10 — it decides how long growth keeps
earning more than WACC after Y10. Pass `cap_years` to the DCF: CAP > 10 runs the
fade stage (binding; `fade_stage="off"` only with a written reason). With the
RONIC gate fired (RONIC = WACC) the stage is value-neutral, as it should be.

Terminal growth `tg` is a long-run nominal growth proxy set in Step 4 (default
2.5%, range 2.0–3.0%); it creates value only through RONIC > WACC, so no
haircut, floor or compounder exception is needed. `ronic` must be ≥ tg. If the
RONIC gate fires (pooled 3Y incremental ROIC < WACC) the engine resets RONIC to
WACC regardless of CAP; override only with `ronic_override_justification`.

CAP and RONIC are set explicitly in Step 5, with justification, and feed Step 6.
Engine reads `cap_years` and `ronic` from inputs.

### CAP Estimation Rubric

This is judgement, not formula. Anchor with these tests:

**Default CAP by sector (starting point, must be defended):**
```
Sector                  | Default CAP (years)
Branded consumer/luxury | 15
Pharma (large-cap)      | 10
Software (mature)       | 12
Software (early)        | 8
Semiconductors          | 7
Industrial (cyclical)   | 7
Defense                 | 12
Utilities (regulated)   | 15
Consumer staples        | 13
Retail                  | 8
Energy (upstream)       | 5
Banks (handled separately)
Other                   | 10
```

**Adjust ±3 years based on:**
- Wide moat score (sub-factor total ≥20) → +3 to +5 years
- Pricing power evidence (>5Y of price increases ahead of inflation) → +2
- Reinvestment runway > 15Y → +2
- Regulatory positioning that durably protects returns → +2
- Patent cliff / LoE / contract concentration in next 5Y → −3
- Technology disruption likelihood (cite candidates) → −2 to −5
- New entrant track record in segment → −2

**Anchoring with base rates:**
Cross-check against base-rates skill (see Mauboussin growth-persistence
tables). The skill provides the empirical distribution of "how long do
companies starting at X ROIC sustain it?".

### CAP Plausibility Gate

⛔ CAP > 20 years requires moat score ≥22/25 AND documented historical
precedent of similar businesses sustaining >20Y. Otherwise revert to 15Y.
(This now matters: it moves RONIC from 50% to 100% of the spread.)

⛔ CAP < 5 years for non-cyclical, non-disrupted businesses requires
explicit named threat (regulatory action, technology shift, contract
loss).

## What the market prices (replaces reverse CAP, v16.4)

The engine's `what_must_be_true` table (computed in every `run_dcf`) gives the
market-implied value of each driver at the current price, holding the others at
model values: rev CAGR Y1–Y10, rev CAGR Y3–Y10 (Y1–2 held), Y10 margin, WACC,
tg, RONIC. Read RONIC and Y3+ CAGR together as the market's CAP statement:
> "At €{p} the market needs {a}% Y3–Y10 CAGR at our margins, or a {b}% Y10 margin
> at our growth, or RONIC of {r}%. We assume {x}% / {y}% / {z}% because {evidence}."

No separate solver, no 25-year ceiling, no reverse-CAP number.

## State File Schema

```json
{
  "quality": {
    "scores": {
      "roic_vs_wacc": 8,
      "roic_stability": 7,
      "moat": 9,
      "reinvestment_runway": 8,
      "capital_allocation": 7,
      "balance_sheet": 8
    },
    "composite": 8.0,
    "tier": "HIGH QUALITY",
    "threshold_used": 6.5
  },
  "roic": {
    "history": {
      "FY-4": {"incl_gw": 0.17, "ex_gw": 0.21, "invested_capital": 23000, "nopat": 4100},
      "FY-3": {...}, "FY-2": {...}, "FY-1": {...}, "FY0": {...}
    },
    "window_years": 5,
    "avg_roic_incl_gw": 0.185,
    "avg_roic_ex_gw":   0.225,
    "wacc": 0.085,
    "spread_to_wacc_bps_incl": 1000,
    "roic_cv": 0.08,
    "incremental_roic": 0.27,
    "incremental_series": [
      {"fy": "FY-3", "incremental_roic": 0.24, "below_wacc": false},
      {"fy": "FY-2", "incremental_roic": 0.29, "below_wacc": false},
      {"fy": "FY-1", "incremental_roic": 0.26, "below_wacc": false},
      {"fy": "FY0",  "incremental_roic": 0.27, "below_wacc": false}
    ],
    "incremental_destroys_value": false,
    "incremental_roic": 0.12, "incremental_span_years": 3
  },
  "cap": {
    "years": 15,
    "sector_default": 10,
    "adjustments": [
      {"factor": "wide_moat", "delta": +3, "evidence": "..."},
      {"factor": "pricing_power", "delta": +2, "evidence": "..."}
    ],
    "implied_by_market": 9,
    "thesis_gap": 6
  }
}
```

## Commands

- `show quality` → display the 6-dimension score table
- `show roic` → display ROIC history + incremental + value-creation flag
- `set cap {years}` → override CAP with justification prompt
- `set quality_threshold {X}` → adjust the prefix-threshold
- `recompute quality` → re-score after edits to financials or moat
