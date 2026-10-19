---
name: wacc-capm
description: >
  WACC derivation for equity analysis (v16.5). CAPM from live inputs with ONE
  coherent convention (spot Bund + Damodaran's current implied ERP), a
  cash-adjusted operating beta for net-cash companies, a beta-quality check for
  thin or implausibly low betas, country risk by revenue footprint, and a
  defensible WACC RANGE that the DCF uses for the rating-robustness test. Read
  this skill in Step 4 of every analysis. `show wacc capm` prints the full table.
---

# WACC — coherent CAPM, operating beta & defensible range (v16.5)

**Why v16.5 changed this skill.** v16.4 paired a spot Bund (searched today) with
a fixed 5.5% ERP labelled "Damodaran". Damodaran's measured implied ERP was
4.20% (1 Oct 2026). Pairing a spot rate with a fixed long-run premium makes the
expected market return move one-for-one with Bund yields, so at a 15-year high
in Bunds every long-duration compounder screened as SELL — a haircut hidden in
an input, which the prompt forbids. v16.4 also used the equity beta of net-cash
companies (the DCF discounts OPERATING cash flows, so it needs the operating
beta), took the French OAT for some French names and the Bund for others, and
accepted betas of 0.51 for thinly traded stocks. All four are fixed here.

⛔ All arithmetic runs in Python: `wacc_capm_range(...)` and the beta helpers in
`equity-dcf/scripts/dcf_engine.py`. No WACC arithmetic in prose.

## Default derivation (every analysis — Step 4)

```
Rf_spot  = 10Y sovereign of the CURRENCY, searched TODAY        [market, date]
           EUR → German Bund for EVERY euro issuer (never the domestic OAT/BTP/Bono)
           GBP → Gilt · CHF → Swiss Conf. · USD → UST
ERP_impl = Damodaran's current implied ERP (home page "Implied ERP on {date}",
           variant "Trailing 12 month, with adjusted payout")    [market, date]
CRP      = Σ revenue_share_c × CRP_c   (Damodaran ctryprem table; domicile irrelevant)
β        = 5Y monthly beta, StockAnalysis statistics page; note the benchmark  [market]
β_used   = beta_quality_check(β, …)["beta_used"]                (see Beta below)
β_op     = cash_adjusted_beta(β_used, mcap, excess_cash)        net cash only
Sp       = size premium (table below)
Ke       = Rf_spot + β_op × (ERP_impl + CRP) + Sp
WACC     = Ke                                   if net cash
         = E/(D+E)·Ke + D/(D+E)·Kd·(1−t)        if net debt (market weights, financial debt only)
Floor    = Rf_spot + 300bps
```

Run:

```python
wr = wacc_capm_range(rf_spot, beta_used, erp_implied,
                     erp_long_run=0.055, rf_normalised=RF_NORMALISED[ccy],
                     crp=crp, size_premium=sp, beta_alt=beta_alt,
                     market_cap=mcap, excess_cash=excess_cash,      # from net_cash_quality()
                     net_debt=net_debt_if_positive, kd_pre_tax=kd, tax_rate=t)
print(format_wacc_range(wr))
INPUTS["wacc"] = wr["central"]; INPUTS["wacc_range"] = wr["wacc_range"]
```

## The two conventions — never mixed

| Convention | Rf | ERP | Use |
|---|---|---|---|
| (a) Market-consistent | spot 10Y (today) | Damodaran current implied | **central WACC** |
| (b) Through-the-cycle | normalised (table) | long-run 5.5% | range edge only |

⛔ Spot Rf with the long-run ERP is the v16.4 error and is not allowed.

**Normalised Rf (house, editable):** EUR 2.50% · USD 3.50% · GBP 3.50% · CHF 1.00%.

**If Damodaran cannot be fetched** (2 tries: home page, then search "Damodaran implied equity risk premium {month} {year}"): log in 9b and use convention (b) as central, flagged `[convention b — implied ERP unavailable]`.

## The defensible range → `wacc_range`

`wacc_capm_range` computes every combination of {convention (a), (b)} × {primary β, alternative β} and returns `low`, `high`, `central`. Alternative β, in order:
1. the 2Y beta if StockAnalysis shows it (an equity beta — the function cash-adjusts it);
2. else the industry beta: Damodaran "Levered and Unlevered Betas by Industry" — HTML page `https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/Betas.html` (US; readable by web_fetch), or the regional `.xls` files (`pc/datasets/betaEurope.xls`, `betaGlobal.xls`) when the environment can read them. Pick the industry that matches the business model, not the GICS label (luxury ≠ mass apparel; say which and why). For a net-cash company pass the column "Unlevered beta corrected for cash" with `beta_alt_is_operating=True`; for a net-debt company relever it with `relever_beta(β_u, D/E, t)`;
3. else the Blume-adjusted beta.

Pass `wr["wacc_range"]` to the DCF. Downstream uses:
- `rating_robustness`: a rating that changes inside the range is capped at HOLD (prompt Step 8).
- `gap_waterfall`: the discount-rate step moves WACC only inside the range.
- `what_must_be_true`: market-implied growth is shown at both ends.

## Beta

1. **Primary:** StockAnalysis 5Y monthly beta (`https://stockanalysis.com/quote/{EXCHANGE}/{TICKER}/statistics/`). Note the benchmark; if it is a USD index for a non-USD stock, say so and lean on the alternative β.
2. **Quality check (BINDING):** `beta_quality_check(β, is_utility, adv_eur_m, beta_industry_relevered)`. Thinly traded stocks (average daily value < €1m) and non-utility betas < 0.70 are biased toward zero by non-synchronous trading → use the higher of measured, Blume-adjusted and industry relevered; print both. (LNA Santé: 0.51 measured.)
3. **Structural break:** if the 2Y and 5Y betas differ by > 0.3, use the 2Y beta and say why. If no 2Y beta is available, the industry relevered beta is the cross-check — the check is never skipped silently.
4. **Net cash:** `cash_adjusted_beta(β, mcap, excess_cash)` = β × E/(E − excess cash). Excess cash comes from `net_cash_quality()` (liquid, free cash only — never placements, related-party accounts or seasonal peaks). Example: Hermès β 1.04, mcap €140.1bn, excess cash €10.7bn → β_op 1.13.
5. **Hamada** for relevering an industry beta to a net-debt company: `relever_beta(β_u, D/E, t)`. Damodaran's cash-corrected unlevered beta is already an operating beta (`beta_alt_is_operating=True`).

"Exceptional business" is not a beta input. Low fundamental (cash-flow) beta is — argue it with an industry or peer beta, not with quality.

## Country risk

CRP enters through revenue exposure, not domicile: a French company selling 90% abroad does not carry French country risk; one selling 85% in France does. Take each country's CRP from Damodaran's table (`datafile/ctryprem.html`, column "Country Risk Premium") and weight by revenue. The Rf stays the Bund for every euro issuer.

## Size premium

| Market cap | Premium |
|---|---|
| ≥ €10bn | 0 bps |
| €5–10bn | +50 bps |
| €2–5bn | +100 bps |
| €1–2bn | +200 bps |
| < €1bn | +300 bps |

## Cost of debt (net-debt companies)

Step A: traded bond yield or rating spread over Rf [market]. Step B (rating table): AAA/AA +60 · A +90 · BBB +150 · BB +275 · B +400 bps. Step C (no rating, ND/EBITDA): <0x +60 · 0–1x +90 · 1–2x +150 · 2–3x +200 · >3x +300 bps. Cross-check against interest expense ÷ average debt (3Y); flag a gap > 150bps.

## Sector range table — bounds check only

| Sector | Default | Range |
|---|---|---|
| Large-cap pharma | 9.0% | 8.5–10.0% |
| Large-cap defense/aero | 8.5% | 8.0–9.5% |
| Large-cap software/SaaS | 10.0% | 9.0–11.0% |
| Large-cap semis | 10.0% | 9.0–11.0% |
| Large-cap luxury/consumer | 9.0% | 8.0–10.0% |
| Mid-cap industrial | 9.5% | 8.5–10.5% |
| Small-cap biotech | 12.5% | 11.0–14.0% |
| Large-cap utilities | 7.0% | 6.5–8.0% |
| Large-cap financials | 10.0% | 9.0–11.0% |
| Mid-cap tech | 11.0% | 10.0–12.0% |
| Other | 9.5% | 8.5–11.0% |

Symmetric rule: if the central WACC falls outside the sector range in EITHER direction, print both and keep the CAPM value with a one-line reason (regime, leverage, beta source). The sector default is a fallback only when β or Rf cannot be sourced (flag [LLM]); it is also the provisional WACC in Step 3c. No one-directional "recommend sector-adjusted" override; no net-cash discount (the operating beta handles cash).

## Terminal growth (owned by Step 4)

`tg` = long-run nominal growth proxy for the revenue footprint: default 2.5%, range 2.0–3.0% (2.0% ex-growth/domestic-mature, 3.0% global names with EM exposure). No haircut, no floor, no compounder exception: growth only creates value when RONIC > WACC (`equity-dcf` Rule 3D). `ronic` and `cap_years` are set in Step 5 (`quality-roic`).

## Output (chat, Step 4)

Print `format_wacc_range(wr)` and one line:

> "WACC {central}% (spot Bund {rf}% + β_op {b} × implied ERP {erp}% [+CRP {c}%] [+size {s}%]); defensible range {low}–{high}% [{basis}]. β: {measured} measured → {used} used ({reason}). Sector range {x}–{y}%: {inside/outside — reason}."

`show wacc capm` → the full table plus the β candidates, CRP weights and Kd derivation.
