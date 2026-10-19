# Regulated Utilities — Valuation Sub-Skill (v15.1)

Use for: GICS Electric Utilities, Gas Utilities, Water Utilities, Multi-Utilities. Network operators with rate-regulated returns (Enel, EDF, National Grid, Iberdrola, NextEra, Duke Energy).

⛔ Route to `equity-dcf` with `engine: nopat_native` + this regulated-utility overlay. Standard EBITDA-native overstates UFCF because capex chronically exceeds D&A by 30-50%.

---

## Core Principle: Regulated Asset Base (RAB)

The earnings of a regulated utility are determined by:
```
Allowed earnings = RAB × Allowed Return (real, regulated)
```

Where:
- **RAB** = depreciated value of regulated assets, indexed by regulator
- **Allowed return** = real WACC set by regulator (typically 4-6% real, 6-8% nominal)
- **Cost pass-through** = fuel, grid losses, certain opex (depends on regime)

The DCF inputs must reflect this regulatory mechanism, not just historical EBITDA.

---

## Required Inputs (regulated utility-specific)

1. **RAB by jurisdiction** — current value + 5-10Y trajectory disclosed in IR
2. **Allowed real return** (per regulator filing)
3. **Inflation index** applied to RAB (typically CPI or RPI)
4. **Regulatory review cycle remaining** (years until next review)
5. **Capex pipeline** — committed RAB additions (these are growth, not maintenance)
6. **Earned vs allowed return spread** — utilities sometimes earn above/below allowed
7. **Unregulated activities revenue / EBITDA** — separately modelled

---

## DCF Inputs Translation

```
Revenue       ≈ RAB × allowed return × (1 + inflation) + cost pass-through + unregulated
EBITDA        ≈ Revenue − opex (pass-through and non-passable separately)
Capex_total   = Growth capex (RAB additions) + maintenance capex (D&A-equivalent)
NOPAT (terminal) ≈ RAB(terminal) × real allowed return
Terminal growth ≈ inflation (RAB grows with CPI by construction) + real capex/RAB growth
```

**NOPAT-native engine required** (Option 1 = `nopat_native`):
- Set `maint_capex_pct` ≈ D&A% (utilities are at maintenance equilibrium)
- Set `growth_capex_pct` = capex above maintenance (RAB additions)
- UFCF = EBIT × (1−t) + D&A − Maint_CapEx − ΔNWC − Growth_CapEx

The growth capex is value-destroying ONLY if allowed return < WACC. With allowed return ≥ WACC + 50bps, growth capex creates value.

---

## WACC Rules for Utilities

- **Use the regulator's allowed nominal WACC as floor**: utilities cannot meaningfully diverge in equilibrium
- Default range: 6.0-8.0% nominal for European/US regulated networks
- Beta typically 0.4-0.7 (utilities trade like bond proxies)
- High leverage typical (60-65% debt) — confirm with peer median

---

## Terminal Growth

- **Terminal growth = inflation rate** (2.0-2.5% developed markets)
- RAB grows with inflation by construction → revenue grows with inflation
- Real growth above inflation requires explicit RAB additions justified by regulator approval

RONIC for regulated utilities = allowed return on RAB (post-tax, nominal). If allowed return ≥ WACC, RAB growth creates value and RONIC > WACC is justified — set `ronic_override_justification` = "allowed return {x}% ≥ WACC {y}%, RAB growth {z}%" if the RONIC gate fires on a capex-heavy build phase.

---

## Cash Flow Quirks

- **Deferred revenue from prepaid grid usage** can be material — Option 5 `extended` often triggers
- **Smart meter / digital infrastructure capex** is current-cycle growth capex
- **Decommissioning provisions** (nuclear especially) — model separately as future cash drain
- **Network connection fees** — non-recurring revenue, normalize out

---

## Red Flags

- **Allowed return cut** in pending regulatory review — material near-term re-rating
- **Stranded asset risk** — coal plants, legacy gas networks in energy transition
- **Political interference** — windfall taxes, price caps (UK 2022-23, France EDF 2022)
- **Unregulated business expansion** — moves utility from bond-proxy to industrial risk
- **Decommissioning underfunding** — nuclear-heavy operators

---

## Modelling Options Defaults (Utilities)

- Option 1: `nopat_native` ✓ TRIGGERED (asset-heavy)
- Option 5: `extended` ✓ likely TRIGGERED (deferred revenue, decommissioning)
- Option 6: `hold_current` (no normalisation; D/E is structural)
- Option 8: `dividend_only` if R9 fires (utility holding co with multiple regulated subs)

---

## Worked Example — Generic European Network Utility

- RAB: €30bn, allowed return 6% nominal → annual allowed EBIT €1.8bn
- Plus unregulated retail/services: €200m EBIT → group EBIT €2bn
- D&A: €1.5bn; capex €2.2bn (growth + maintenance)
- Tax 25% → NOPAT ~€1.5bn
- UFCF (NOPAT-native): 1.5 + 1.5 − 1.5 − 0.7 = €0.8bn
- Terminal growth = inflation 2.0%; WACC 6.5% (peer median)
- Terminal value = 0.8 × 1.02 / (0.065 − 0.02) = €18.1bn
- EV ≈ €25-30bn (depending on explicit horizon NPV)
- Bridge: + RAB-indexed minus net debt (typically €18-22bn for this profile)

---

## State File Schema (regulated utility)

```json
{
  "engine": "nopat_native",
  "sub_overlay": "regulated_utility",
  "rab_data": {
    "current_rab": 30000.0,
    "allowed_real_return": 0.045,
    "allowed_nominal_return": 0.065,
    "review_cycle_remaining_years": 3,
    "inflation_index": "CPI",
  },
  "unregulated_business": {
    "revenue": 1500.0,
    "ebitda": 250.0,
    "treatment": "consolidated"
  }
}
```
