# Stress Tests & Sustainability Checks (v15.1)

Reference file for `equity-dcf` skill. Provides empirical anchors for R9 dividend sustainability, holdco discount baselines, and cross-sector currency hedging conventions.

---

## R9 Captive Dividend Sustainability (BEAR CASE)

The R9 default assumes the captive's dividend continues at `fy0_dividend_paid` growing 2%/yr. In credit cycles, captives **cut dividends sharply** to preserve regulatory capital.

**Bear-case floor (mandatory if running scenarios):**
- Floor captive dividend at **30% of fy0_dividend_paid** for 24 months
- Recovers linearly to 75% by month 36, then back to fy0 trajectory

**Historical reference points:**

| Captive | Dividend cut vs prior year | Trigger | Recovery time |
|---|---|---|---|
| Renault RCI Banque 2020 | -65% | COVID + credit stress | 18 months |
| Ford Credit 2008-09 | -85% | GFC + auto demand collapse | 36 months |
| GMAC 2008 | -100% | Bailout / GM bankruptcy | restructured entirely |
| Caterpillar Financial 2009 | -40% | Equipment finance defaults | 24 months |
| GE Capital 2009-15 | -90% to -100% | divestiture / wind-down | n/a, structurally exited |

**Apply in bear case** for any company where R9 fires with captive_finance type.

Formula in scenario script:
```python
def bear_case_captive_dividend(fy0_div):
    return [
        fy0_div * 0.30,  # Y1: floor
        fy0_div * 0.35,  # Y2: still stressed
        fy0_div * 0.75,  # Y3: recovery
        fy0_div * 0.90,  # Y4
        fy0_div * 1.00,  # Y5+: back to fy0 trajectory
    ]
```

---

## Holdco Discount Baselines (post-R9)

The v15.1 default is **no additional discount after R9** because R9 already isolates the holding's value via dividend stream. However, **empirical evidence** shows persistent discounts to SOTP even after careful adjustment.

**Reference table of long-run avg discounts** (post-SOTP, post-double-count adjustment):

| Holding type | Long-run avg discount to SOTP | When wider | When narrower |
|---|---|---|---|
| Investor AB / Industrivärden (Swedish industrial holdco) | 15-25% | Recession, IPO-light periods | Buyback announcements |
| Wendel / Eurazeo (private equity holdco) | 20-35% | When unrealized gains dominate NAV | Cash-rich + large realisations |
| Exor (multi-asset, listed subs) | 25-40% | When Ferrari outperforms (concentration) | Spinoff catalysts |
| Bolloré / Pinault (French complex) | 30-45% | Governance overhang, related-party | Simplification announcements |
| Renault (French govt 15% stake) | 15-25% | Political interference, strategic noise | Capital allocation discipline |
| Berkshire Hathaway (Buffett-blessed) | 0-10% | Buffett health, mega-cap drag | Stock recovery / buyback |
| Korean chaebol (Samsung, LG) | 35-50% | Governance, family transitions | Reform announcements |

**Apply with discipline:**
- Document the reason (governance, complexity, illiquidity, capital allocation history)
- Calibrate to historical 5Y-10Y avg discount for THIS holding (not generic peer)
- Apply to operating equity value, NOT to non-core PV (which is already conservatively valued)
- If applied: state as separate line in equity bridge

```
Operating equity (R9-adjusted DCF)        X
+ PV non-core dividends                   Y
= Total equity (theoretical)              X + Y
× (1 − Holdco discount %)                 = Implied price
```

⛔ Holdco discount is NEVER a substitute for R9. R9 first, holdco discount second (and only with empirical anchor).

---

## Currency Hedging — Cross-Sector Modelling (v15.1)

Material when:
- >25% of revenue in a non-reporting currency, AND
- Cost base ≠ revenue currency by ≥25%

**Documentation requirement** in INPUTS:

```python
"fx_exposure": {
    "reporting_currency": "EUR",
    "primary_exposure_pair": "EUR/USD",
    "revenue_in_non_reporting_pct": 0.45,
    "cost_in_non_reporting_pct": 0.15,
    "natural_hedge_ratio": 0.33,        # 15%/45%
    "explicit_hedging_coverage_12m": 0.60,  # 60% of 12M USD revenue hedged
    "hedge_strike_avg": 1.10,           # vs spot 1.08
    "current_spot": 1.08,
    "forward_12m_implied": 1.09,
},
```

**Scenario sensitivities** (mandatory in .md when FX exposure flagged):

| Scenario | FX assumption | Margin impact | Revenue impact |
|---|---|---|---|
| Base | Forward rate path | as modelled | as modelled |
| FX Bear | -15% adverse vs reporting ccy, sustained 2y | -200-400 bps EBITDA | -5 to -10% |
| FX Bull | +5% favourable | +100 bps | +2-3% |

**Hedging accounting**:
- Hedged portion (typically 50-80% of 12M revenue): use hedge strike rate
- Unhedged: use forward implied
- Beyond 12M: assume natural hedge ratio holds, unhedged exposure flows through

**Examples to model**:
- SAP (EUR-reporting, ~50% USD revenue) — primary EUR/USD exposure; natural hedge ~30% (some USD costs); explicit hedging typical 50-70% 12M
- ASML (EUR-reporting, ~85% USD/JPY revenue) — very high exposure; explicit hedging usually 80%+
- Capgemini (EUR-reporting, multi-currency revenue + INR cost) — basket exposure; hedging ~50%
- Pharma majors (Sanofi, Roche, Novartis) — large USD revenue, multi-currency cost
- Luxury (LVMH, Hermès) — USD/JPY/CNY revenue, EUR cost base; natural hedge low; explicit hedging substantial

**Red flag triggers**:
- Natural hedge ratio <30% AND explicit hedging <40% → high FX risk → 🔴
- Hedge strike rate materially favourable but rolling off in <12 months → cliff risk → 🟡
- Reporting currency dominant in costs but revenue in 3+ other currencies → multi-currency basket → adopt average

---

## Sector-Adjusted SBC Defaults (v15.1)

Standard `non_cash_addback` is wrong for software/biotech, where SBC is structurally material.

**Default trigger for Option 4 = `cash_cost`**:
- Software: ALWAYS trigger if SBC >5% of revenue (sector norm)
- Biotech: ALWAYS trigger (development-stage biotechs often have SBC 20-50% of revenue or negative revenue)
- Tech services: trigger if SBC >3% of revenue
- All other sectors: standard 5% threshold

**When `cash_cost` applied**: subtract SBC% from EVERY projected EBITDA margin in the DCF, and document the haircut:

```
EBITDA margin (reported, including SBC addback): 28%
− SBC: 12% of revenue
= EBITDA margin (cash-cost basis): 16%
```

This is the basis used in the DCF projection. Multiple ratchet effects (compounding):
- Lower projected margins → lower projected UFCF
- May trip the RONIC gate (pooled 3Y incremental ROIC < WACC → terminal RONIC = WACC)

---

## Cyclical Sector Through-Cycle Reference (v15.1 expanded)

| Sector | 10Y avg EBITDA margin | Source |
|---|---|---|
| Autos — European volume | 9-10% | Renault, Stellantis 2014-2024 |
| Autos — European premium | 13-15% | Mercedes, BMW 2014-2024 |
| Autos — Japanese | 12-14% | Toyota 2014-2024 |
| Chemicals — basic | 11-14% | BASF, Dow 2014-2024 |
| Chemicals — specialty | 18-22% | Linde, Air Liquide |
| Steel | 9-13% | ArcelorMittal, ThyssenKrupp |
| Aluminum | 12-15% | Norsk Hydro, Alcoa |
| Copper | 25-30% | Antofagasta, Freeport |
| Container Shipping | 16-22% | Maersk, Hapag-Lloyd (post-pandemic adjusted) |
| Dry Bulk | 20-28% | Star Bulk, Golden Ocean |
| Refining | 6-10% | Valero, MPC |
| Construction Materials | 18-23% | Holcim, Heidelberg, CRH |
| Airlines | 10-14% | IAG, Lufthansa, AF-KLM |
| Memory Semis | 22-30% | Micron, SK Hynix (highly variable) |
| Semis Equipment | 28-35% | Applied Materials, Lam Research |
| Heavy Trucks | 9-12% | Volvo, Daimler Trucks |
| Capital Equipment | 16-20% | Caterpillar, Deere (with R9 strip of captive) |
| Pulp & Paper | 16-20% | UPM, Stora Enso |
| Homebuilders | 10-13% | Lennar, D.R. Horton |

⛔ These are advisory defaults. Always compute 10Y avg for the specific company first; use the table as cross-check only.

---

## Pillar Two Tax Floor (v15.1 advisory)

OECD Pillar Two minimum global tax 15% applies to MNEs with >€750m group revenue (effective various from 2024). For DCF with long fade horizon:

- Apply floor of 15% on effective tax rate from Y5+ for in-scope companies
- Companies with current ETR <15% (Ireland-domiciled software, Caribbean-domiciled shipping, Bermuda-domiciled insurance, etc.) face mechanical step-up
- Document in derivation: `tax_fade` must reach minimum 15% by Y5 for in-scope companies

Example fade for Irish-domiciled software currently at 12% ETR:
```python
"tax_fade": [0.12, 0.13, 0.14, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15]
```

---

## Summary — When to Read This File

Load `stress_tests.md` from `equity-dcf/references/`:
- Step 7 bear scenario construction (R9 captive dividend cuts)
- Step 7 holdco discount application (if SOTP + concentration risk)
- Step 4 / Step 6 when FX exposure flagged in Step 1c
- Step 6 SBC sector defaults
- Step 6 through-cycle margin anchoring for any cyclical sector
- Step 4 tax fade for in-scope MNE
