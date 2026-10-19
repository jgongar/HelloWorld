# REIT / Real Estate — Valuation Sub-Skill (v15.1)

Use for: GICS Equity REITs, Real Estate Operating Companies (REOCs) where AFFO/FFO/NAV are the primary cash KPIs.

⛔ **Override standard equity-dcf.** REIT valuation uses AFFO multiples + NAV + dividend discount, NOT UFCF DCF. UFCF on a REIT systematically distorts because:
1. Depreciation does NOT track economic deterioration (real estate appreciates)
2. Capex includes acquisitions which are NOT "maintenance"
3. Capital structure relies on tax-mandated dividend payouts (US: 90% of REIT taxable income)
4. Cap rates are the actual discount mechanism, not WACC

---

## Three Required Approaches (triangulate)

### 1. AFFO Multiple (primary)

```
AFFO = FFO − Recurring CapEx − Straight-line rent adjustments + Stock-based comp
FFO  = Net Income + Depreciation & Amortization − Gains on sale + Impairments
```

**Multiple range** by property type (US, fwd P/AFFO):

| Property type | High-quality | Mid | Low |
|---|---|---|---|
| Industrial / logistics | 22-28x | 18-22x | 14-18x |
| Apartments / multifamily | 18-22x | 15-18x | 12-15x |
| Healthcare (senior housing) | 16-20x | 13-16x | 10-13x |
| Office (Class A) | 12-16x | 9-12x | 6-9x |
| Retail (open-air strip) | 14-18x | 11-14x | 8-11x |
| Mall (Class A) | 13-17x | 10-13x | 6-10x |
| Mall (Class B/C) | 6-9x | 4-6x | 2-4x |
| Data centers | 22-28x | 18-22x | 14-18x |
| Self-storage | 20-24x | 16-20x | 13-16x |

Apply peer-group median × forward AFFO. Bear/base/bull = trough/cycle-mid/peak multiples.

### 2. NAV (Net Asset Value)

```
NAV = (NOI / cap rate) − Net Debt − Preferred − Minorities + Land/Development at cost
```

NOI by property segment / appropriate cap rate per segment. Cap rates published in IPD, MSCI, Green Street, NCREIF.

If trading at >15% discount to NAV: flag as deep value (but check for liquidity / governance reasons first).
If trading at >10% premium to NAV: implies growth optionality being priced; verify.

### 3. Dividend Discount Model

```
Equity value = Dividend per share / (Cost of equity − Dividend growth)
```

REIT dividends are tax-mandated payouts; quality and growth more relevant than UFCF.

---

## Required Inputs (instead of standard DCF)

- AFFO per share (3Y history + forward consensus)
- FFO per share (history + forward)
- Recurring capex per share (mandatory subtraction from FFO → AFFO)
- Same-store NOI growth %
- Occupancy %
- Re-leasing spreads % (positive = pricing power; negative = roll-down risk)
- WALE (weighted-average lease expiry) in years
- Cap rate (current, by segment)
- LTV (loan-to-value)
- ND/EBITDA (or ND/AFFO)
- Dividend per share + payout ratio
- Net acquisitions / disposals (YTD)

---

## DCF Adjustments — If Forced to Run UFCF (DISCOURAGED)

Only run UFCF as a tertiary check, never as primary valuation. If used:

- **Cap "maintenance capex"** at 5-7% of revenue (REIT recurring capex disclosures often understate)
- **Tax rate = 0%** (REITs pass through to shareholders)
- **Terminal growth = inflation** (real estate is an inflation hedge in principle; 2.5% in developed markets)
- **Use property-type cap rate as WACC proxy** — typically 4.5-7.5% depending on quality
- **Add back gains on sale below the line**

Document why UFCF DCF is being used + flag prominently as "tertiary check, not primary valuation."

---

## Modelling Options Override

- Option 1: NOT `nopat_native` and NOT `ebitda_native` — use REIT-specific valuation
- Leases: REITs are lessors — `lease_cost_pct_of_revenue` = 0 (ground-rent only, if any); the rent-as-opex convention concerns lessee costs
- NWC scope (Option 3): `extended` (rent receivables, lease accounting items material)

---

## Red Flag Triggers (Step 9 — REIT-specific)

- **Occupancy <90%** for stabilized portfolio → leasing pressure
- **Negative re-leasing spreads** for 2+ consecutive quarters → pricing power gone
- **LTV >50%** combined with rising rates → refi risk
- **Dividend coverage AFFO <85%** → cut likely
- **Recurring capex >50% of NOI** → property is over-depreciated, replacement looming
- **WALE <3 years** with rate environment hostile → re-leasing risk concentrated

---

## Worked Example — Generic Industrial REIT

- Revenue (rental income): €500m
- NOI: €350m (70% margin)
- D&A: €100m (large; book vs economic)
- FFO: €280m
- Recurring capex: €40m
- AFFO: €240m
- Shares: 100m → AFFO/sh = €2.40
- Peer median fwd P/AFFO: 20x → implied price €48.00

NAV cross-check:
- Cap rate 5% on industrial → property value = €350m / 5% = €7,000m
- Net debt €2,500m → NAV equity = €4,500m / 100m shares = €45.00/sh

DDM cross-check:
- Dividend €2.00/sh, growth 3%, ke 7% → value = 2.00 / (0.07 − 0.03) = €50/sh

Triangulated fair value €45-50, base €48.

---

## State File Schema (when REIT)

```json
{
  "engine": "reit_valuation",
  "primary_valuation": {
    "affo_multiple": {"affo_per_share": 2.40, "multiple": 20.0, "implied_price": 48.0},
    "nav": {"property_value": 7000.0, "net_debt": 2500.0, "implied_price": 45.0},
    "ddm": {"div": 2.00, "g": 0.03, "ke": 0.07, "implied_price": 50.0}
  },
  "triangulated_price": 48.0,
  "ufcf_dcf_tertiary": null,
  "modelling_options": {"engine": "reit_valuation", ...}
}
```

The `ufcf_dcf_tertiary` field stays null unless explicitly requested by user with documented rationale.
