# Upstream Energy — NAV Overlay Sub-Skill (v15.1)

Use for: GICS Oil & Gas Exploration & Production. Standard DCF on commodity producers misses two structural realities: (1) reserves are exhaustible, (2) commodity prices drive everything.

⛔ Route to `equity-dcf` with `engine: nopat_native` + this NAV overlay. DCF is a SECONDARY valuation, not primary.

---

## Three Required Valuations (triangulate)

### 1. NAV per 2P Reserve (PRIMARY)

```
NAV = Σ(per-field discounted cash flow at strip + LT prices) − Net Debt − ARO
```

Where 2P = Proved + Probable reserves. Must be disclosed under SEC PV-10 (US filers) or NI 51-101 (Canadian) or SPE-PRMS (international).

**Discount rate convention**:
- PV-10 mandates 10% (SEC fixed)
- Most analysts also model PV-15 for risk-adjusted (sensitivity)
- For European/IFRS filers, use NPV at 8-10% as the standard

**Pricing deck**:
- Strip prices for first 3-5 years (forward curve)
- Long-term price for years 5+ — analyst judgment
- Differentials: brent-WTI, light-heavy, NA gas vs Henry Hub vs European TTF

### 2. EV / Production (multiple-based, secondary)

```
EV per flowing boe = EV / current production (boepd)
```

Peer-group ranges (current cycle):
- Pure oil onshore US: $25-40k/boepd
- Offshore conventional: $40-60k/boepd
- Deepwater / FPSO: $60-100k/boepd
- LNG-integrated: $80-120k/boepd
- Stranded/marginal: <$15k/boepd

Apply to current production. Cross-check NAV.

### 3. EV / EBITDA × commodity deck (DCF-style, tertiary)

If using EBITDA DCF as supplementary check: hold commodity prices flat (e.g., strip prices for 5 years, then LT price), project production decline, project capex needs. NOPAT-native preferred over EBITDA-native given high capex.

---

## Required Inputs (upstream-specific)

1. **2P reserves** (in boe; mboe; or mmboe scale per filing)
2. **R/P ratio** (reserves / annual production)
3. **Production decline rate** (10-15% mature onshore; 25-35% shale)
4. **Maintenance capex** ($/boe to keep production flat)
5. **Growth capex** (for new development drilling)
6. **F&D cost** (finding & development, $/boe added to reserves) — quality KPI
7. **Realized prices** by product (oil, gas, NGLs) net of differentials
8. **Lifting cost** ($/boe operating cost)
9. **Royalties + taxes** by jurisdiction
10. **Hedging positions** — covered % of next 12-24 months production, strike prices
11. **ARO (Asset Retirement Obligation)** — undiscounted and discounted
12. **Decommissioning timing** — front- vs back-loaded

---

## Commodity Price Sensitivity (MANDATORY)

For oil-focused producer, must show sensitivity table:

| Scenario | LT Brent | NAV per share | Implied price |
|---|---|---|---|
| Bear | $55 | xx | xx |
| Base | $75 | xx | xx |
| Bull | $95 | xx | xx |

For gas: LT TTF €/MWh or Henry Hub $/MMBtu.

For LNG-integrated: oil-link or TTF-link basis matters more than absolute price.

Each scenario must include production decline + reserve replacement assumptions consistent with the price scenario (low prices → less drilling → faster decline; high prices → more drilling → more reserves).

---

## WACC for Upstream

- Higher than market due to reserve risk and commodity exposure
- Pureplay onshore US: 9-11%
- Offshore conventional: 10-12%
- Frontier / exploration-heavy: 12-15%
- Apply Pillar Two and country tax floors

---

## Terminal Treatment (Critical)

Upstream is NOT a perpetual business. Reserves are exhaustible.

**Three options for terminal:**

1. **Reserve life run-off** (most realistic): no perpetuity; explicit forecast through to end of 2P reserves + decommissioning, NPV everything.
2. **Reserve replacement perpetuity** (most common): assume F&D maintains reserves, perpetuity at LT commodity prices. Terminal growth 0% (no real growth, just maintenance).
3. **Liquidation NAV**: assume management harvests cash and returns capital. NPV remaining reserves + return to zero.

⛔ Upstream: RONIC = WACC unless F&D cost is consistently below replacement cost (documented 5Y); with RONIC = WACC terminal growth is value-neutral, which is the correct treatment for a depleting asset base. tg ≤ 0% remains appropriate for mature basins (reserve-life fade).

---

## Modelling Options Defaults (Upstream)

- Option 1: `nopat_native` ✓ TRIGGERED (asset-heavy, capex >> D&A)
- Option 5: `trade_only` typically (no significant contract WC for E&P)
- Option 6: `hold_current` unless reserve life <10y (then de-lever for terminal)
- Option 8: `dividend_only` if R9 fires (integrated O&G with downstream subs, midstream MLPs)

Cyclical sector: terminal commodity price IS the through-cycle anchor (Gate 3 binds via price, not margin).

---

## Red Flags (upstream-specific)

- **Reserve replacement ratio <100%** for 2+ years → reserve base declining
- **Production decline accelerating** beyond guidance → field issues or capex underfunding
- **F&D cost rising 20%+** vs prior 3Y → diminishing prospect quality
- **Hedge ratio dropping** going into price weakness → naked exposure rising
- **ARO underfunded** relative to mature wells → liability overhang
- **Lifting cost rising** despite production flat → field deterioration
- **Country concentration >50%** in single jurisdiction → political/tax risk

---

## State File Schema (upstream)

```json
{
  "engine": "nopat_native",
  "sub_overlay": "upstream_nav",
  "primary_valuation": {
    "nav_2p": {
      "pv_at_10pct": 0.0,
      "price_deck_used": {"oil_strip_y1_5": [...], "oil_lt": 75.0, "gas_lt_eu_mwh": 35.0},
      "implied_price": 0.0
    },
    "ev_per_production": {"ev_per_boepd": 0.0, "implied_price": 0.0},
    "dcf_supplementary": {"implied_price": 0.0, "note": "Tertiary check"}
  },
  "reserves": {
    "2P_boe": 0.0,
    "rp_ratio_years": 0.0,
    "decline_rate_pct": 0.0
  },
  "triangulated_price": 0.0
}
```
