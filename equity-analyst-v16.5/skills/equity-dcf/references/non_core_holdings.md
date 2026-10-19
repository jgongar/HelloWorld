# Non-Core Holdings — Strip-Out + Dividend-as-FCF Rule (R9)

**Reference file for `equity-dcf` skill, v15.1+.**
Loaded when R9 trigger fires in Step 1b. Owns the rules for captive finance arms, equity-method associates, FVOCI/FVTPL equity stakes, and listed subsidiaries inside conglomerate parents.

---

## Core Principle

> **Only cash that reaches the listed parent's shareholders may appear in the parent's DCF.**

Trapped capital inside non-controlled or structurally captive entities is excluded from EV and operating projections. It enters valuation only via the cash actually distributed (dividend stream), valued at PV.

This eliminates four common errors:
1. **Double-counting**: adding equity-method carrying value AND consolidated income to bridge
2. **Phantom cash**: projecting captive EBITDA as if it converts to parent FCF at normal rates
3. **Wrong leverage**: including captive debt (matched by receivables) in operating EV bridge
4. **Implicit monetization assumption**: book-value treatment assumes a sale or spin that may never happen

---

## R9 Triggers (any one activates the rule)

1. **Captive finance arm** with separately reportable segment OI ≥10% of group OI
   - Examples: Renault/Mobilize, Stellantis/SFS, Caterpillar/Cat Financial, Deere/JDF, BMW/Mercedes/VW captive banks, Ford Credit, GM Financial, AvtoVAZ historically

2. **Equity-method stake** with carrying value ≥10% of parent market cap OR contributing ≥10% of net income
   - Examples: Dassault Aviation/Thales (~26%), Renault/Nissan pre-FY25 (35.7%), Bolloré/Vivendi historically

3. **FVOCI / FVTPL equity investment** with fair value ≥10% of parent market cap
   - Examples: Renault/Nissan post-FY25 (FVOCI accounting change)

4. **Holding company structure** where the listed entity holds shares in operating subsidiaries that are themselves separately listed
   - Examples: Exor, Wendel, Eurazeo, Investor AB, Industrivärden, GBL, Brookfield Corp

**Borderline threshold (5-10%)**: case-by-case judgment. Document decision in `non_core_holdings_borderline_note` field. Default: apply R9 if facts justify.

---

## Treatment Matrix

| Item | Captive finance | Equity-method assoc | FVOCI stake | Listed sub (controlled) |
|---|---|---|---|---|
| Revenue in group DCF | ⛔ STRIPPED | already excluded (equity income line) | already excluded | ⛔ STRIPPED if reported separately |
| EBITDA in group DCF | ⛔ STRIPPED | n/a | n/a | ⛔ STRIPPED |
| D&A in group DCF | ⛔ STRIPPED | n/a | n/a | ⛔ STRIPPED |
| Capex in group DCF | ⛔ STRIPPED | n/a | n/a | ⛔ STRIPPED |
| Debt in EV bridge | ⛔ EXCLUDED | n/a | n/a | ⛔ EXCLUDED (consolidated incorrectly) |
| Dividend received | ✅ PV stream → EV | ✅ PV stream → EV | ✅ PV stream → EV | ✅ PV stream → EV |
| Book/FV stake in bridge | ⛔ NEVER | ⛔ NEVER | ⛔ NEVER | ⛔ NEVER |

**The historical practice** of "add equity-method carrying value to bridge" or "add FVOCI fair value to bridge" is **DISALLOWED**. It double-counts with the dividend stream.

---

## Schema — `net_debt_basis` (top-level INPUTS, required when R9 active)

Before listing non-core holdings, the analyst MUST specify which basis the provided `net_debt` value uses:

```python
"net_debt_basis": "operating_only",   # OR "group_consolidated"
"net_debt": -7400.0,                  # operating-only example: Renault auto net cash
```

- `"operating_only"` — analyst provides operating-business net debt directly (e.g., Renault's "automotive net cash position", Stellantis "industrial cash"). Engine does NOT strip; `balance_sheet_debt_to_exclude` is informational only.
- `"group_consolidated"` — analyst provides group consolidated net debt (which includes captive debt and trapped cash). Engine strips `balance_sheet_debt_to_exclude` and `balance_sheet_cash_in_captive`.

Wrong choice → bridge errors by the size of the captive debt (often €30-60bn). Engine prints `_strip_debt_reason` to confirm which path was taken.

---

## Schema — `non_core_holdings` in INPUTS

```python
"non_core_holdings": [
    {
        "name": "Mobilize Financial Services",
        "ticker": None,                          # if listed
        "type": "captive_finance",
        # one of: captive_finance | equity_method | fvoci | fvtpl | listed_subsidiary
        "ownership_pct": 1.00,
        "treatment": "dividend_only",
        "rationale": "Captive finance arm; debt is operating raw material, not industrial leverage",

        # Figures to STRIP from group consolidated (per Treatment Matrix)
        "fy0_revenue":       6400.0,             # [filing, segment disclosure]
        "fy0_ebitda":        1500.0,             # [filing or computed: segment OI + segment D&A]
        "fy0_da":             400.0,             # [filing or LLM]
        "fy0_capex":         3500.0,             # for captive: receivables build = capex equivalent
        "fy0_dwc":              0.0,             # usually 0 for finance (balance sheet expansion captured in capex)

        # Figure that ENTERS parent DCF as cash inflow
        "fy0_dividend_paid":  300.0,             # [filing, parent CF statement: "dividends from associates" or segment note]

        # Reference values (for bull-case overlay only, NEVER for base bridge)
        "fy0_book_equity":   3200.0,             # [filing]
        "fy0_market_value":  None,               # [market] if listed, else None

        # Dividend stream modelling
        "dividend_growth":   0.02,               # cap at 2%/yr; flat preferred for captives
        "discount_rate":     0.090,              # default = parent WACC
        "horizon_years":     10,                 # match parent DCF horizon

        # Balance sheet items to EXCLUDE from operating EV bridge
        "balance_sheet_debt_to_exclude": 60000.0,   # captive debt (matched by receivables)
        "balance_sheet_cash_in_captive":  2000.0,   # captive cash (trapped, not parent cash)

        # Bull-case monetization overlay (optional, requires named probability)
        "monetization_overlay": {
            "active": False,
            "probability": 0.0,                  # 0.0 to 1.0
            "fair_value": 4000.0,                # IPO/sale at book or peer multiple
            "friction_discount": 0.20,           # 15-25% execution risk
            "timeline_months": 24,
            "catalyst": "...",
        },
    },
    # Additional holdings: Nissan FVOCI, etc.
]
```

---

## Dividend PV Computation

```python
def value_non_core_holding(holding, parent_wacc, horizon=10):
    """
    Value as PV(dividend stream) over explicit horizon + PV(terminal dividend perpetuity).
    Conservative defaults: g_div capped at 2%, terminal held flat (no perpetual growth).
    """
    div0 = holding["fy0_dividend_paid"]
    g    = min(holding["dividend_growth"], 0.02)
    r    = holding["discount_rate"]

    # Explicit-horizon PV
    pv_explicit = sum(
        div0 * (1 + g) ** t / (1 + r) ** t
        for t in range(1, horizon + 1)
    )

    # Terminal: dividend held flat (no perpetual growth) — conservative
    terminal_div = div0 * (1 + g) ** horizon
    pv_terminal  = terminal_div / r / (1 + r) ** horizon

    return {
        "pv_explicit": pv_explicit,
        "pv_terminal": pv_terminal,
        "pv_total":    pv_explicit + pv_terminal,
        "g_applied":   g,
        "r_applied":   r,
        "horizon":     horizon,
    }
```

**Bull-case overlay:**
```python
def monetization_overlay_value(holding):
    m = holding["monetization_overlay"]
    if not m["active"]:
        return 0.0
    base_pv = holding.get("_div_pv", 0.0)  # already-computed dividend PV
    realized = m["fair_value"] * (1 - m["friction_discount"])
    incremental = max(0, realized - base_pv)
    return m["probability"] * incremental
```

---

## Engine Helpers

The following are added in v15.1 to `dcf_engine.py`:

- `strip_non_core_from_group(group_inputs, non_core_list)` — returns operating-only inputs (revenue, EBITDA, D&A, capex stripped per Treatment Matrix). Respects `net_debt_basis` field to avoid double-stripping.
- `value_non_core_holding(holding, parent_wacc, horizon)` — dividend stream PV
- `compute_non_core_aggregate(non_core_list, parent_wacc)` — sum of PVs + monetization overlays
- `validate_non_core_no_double_count(state)` — verifies no holding's book/FV appears in BOTH dividend stream AND any bridge line
- `enforce_ufcf_sign_rule(ufcf_y1, fcf_fy0, net_interest_signed)` — R8 binding gate

All called automatically by `run_dcf()` when `non_core_holdings` is non-empty.

## net_debt Contract (avoiding double-strip)

When R9 fires, the analyst MUST specify `net_debt_basis` in INPUTS:

- `net_debt_basis = "operating_only"` — analyst already provides operating-only net debt (e.g., Renault's published "automotive net cash"). Engine does NOT strip; `balance_sheet_debt_to_exclude` is informational only.
- `net_debt_basis = "group_consolidated"` (or absent) — analyst provides group consolidated; engine strips `balance_sheet_debt_to_exclude` and `balance_sheet_cash_in_captive`.

Wrong choice → bridge errors by the size of the captive debt (often €30-60bn).

---

## Dividend Sustainability Stress Test (v15.1)

R9 takes `fy0_dividend_paid` as given. In stressed cycles, captive finance arms cut dividends sharply (Renault Mobilize did this in 2020; Ford Credit cut dividends to parent in 2008-09 and 2020). The base-case PV calculation should be supplemented by a stress test:

### Stress test formula

```
stress_dividend = max(0.30 × normal_dividend, 0)
stress_pv = value_non_core_holding(holding with stress_dividend, parent_wacc + 200bps, horizon)
sustainability_buffer = (base_pv - stress_pv) / base_pv
```

A 30% floor reflects historical worst-cycle behaviour: even in 2008-09 and 2020, captives didn't fully suspend dividends — they cut to 25-40% of normal. The +200bps WACC premium reflects increased uncertainty in stressed scenarios.

### When to apply
- ALL captive finance arms (R9 type `captive_finance`)
- Listed subsidiaries trading at materially below NAV (suggests market doubts dividend durability)
- NOT applicable to equity-method stakes (those dividends already reflect arms-length governance)

### Output (added to NON-CORE HOLDINGS block when active)

```
Stress test (captive_finance only):
  Holding 'Mobilize':
    Base dividend €500m → base PV €6,395m
    Stress dividend €150m (30% floor) @ WACC+200bps → stress PV €1,275m
    Sustainability buffer: 80% (loss in stress)
    Action: include stress_pv in bear case, base_pv in base case
```

### Implementation
Engine helper `stress_test_dividend(holding, parent_wacc)`:
```python
def stress_test_dividend(holding, parent_wacc, floor_pct=0.30, wacc_premium_bps=200):
    stress = dict(holding)
    stress["fy0_dividend_paid"] = holding["fy0_dividend_paid"] * floor_pct
    stress["discount_rate"] = parent_wacc + wacc_premium_bps / 10000
    return value_non_core_holding(stress, stress["discount_rate"], holding.get("horizon_years", 10))
```

Call automatically inside `compute_non_core_aggregate()` for captive_finance type. Returns both `base_pv` and `stress_pv` per holding; bear-case scenarios use stress_pv automatically.

---

## Output Structure

### Bridge to Equity (expanded with R9):

```
EV (operating biz, from stripped DCF)              X
+ PV(non_core_dividend_stream)                     Y
+ Bull overlay: monetization optionality           Z   (bull case only)
−────────────────────────────────────────────────────
= Total Enterprise Value                           X + Y + Z

− Operating net debt (excl captive debt)           a
− Pension deficit                                  b
− Lease liabilities (operating only)               c
− Minorities                                       d
─────────────────────────────────────────────────────
= Equity Value                                     (X+Y+Z) − (a+b+c+d)
÷ Shares                                           n
= Implied Price                                    €P
```

### Chat output addition (mandatory when R9 fires):

```
Non-core holdings (R9):
  - {Name 1} ({type}): dividend €{X}m → PV €{Y}m at {WACC}%
  - {Name 2} ({type}): dividend €{X}m → PV €{Y}m at {WACC}%
  Total non-core value (base):     €{Z}m
  Bull monetization overlay:        €{W}m  ({P}% × {fair_value} × {friction})
```

---

## Worked Examples

### Example 1 — Renault (captive finance + FVOCI stake)

**Strip from group DCF:**
- Revenue −€6,400m (Mobilize)
- EBITDA −€1,500m (Mobilize)
- D&A −€400m (Mobilize)
- Capex −€3,500m (Mobilize receivables build)
- Debt from EV bridge: −€60,000m (Mobilize liabilities)
- Cash from EV bridge: −€2,000m (Mobilize cash, trapped)

**Add as dividend stream:**
- Mobilize: €500m/yr growing 2% @ 9% WACC over 10y horizon + flat terminal perpetuity ≈ €5,600m PV
- Nissan FVOCI: €0/yr current dividend → PV = €0 base case. Bull overlay: 25% prob × €2.6bn FV × 0.80 friction = €520m (only if catalyst named)

**Result:** auto-only DCF runs on €51.4bn revenue, true through-cycle OM ~3-4%. Total non-core value ≈ €5.6bn base, +€520m bull overlay.

### Example 2 — Dassault Aviation (equity-method stake in Thales ~26%)

**Already excluded from group EBIT (Thales is equity-method line below operating income).**

- Thales dividend to Dassault Aviation FY0 ≈ €200m
- PV(€200m/yr growing 2% @ 9% WACC) ≈ €2,500m → added to EV
- Dassault's Thales carrying value (~€3,500m book) — **NOT added** (would double-count dividend)
- Bull overlay: Dassault sells Thales stake at market — 20% prob × (€5,000m mkt value − €2,500m dividend PV) × 0.80 friction = €400m

### Example 3 — Exor (multiple listed subsidiaries)

For each of Ferrari, Stellantis, CNH, Iveco, Philips:
- Strip from consolidated revenue/EBITDA/capex
- Strip subsidiary debt from EV bridge
- Add subsidiary dividend stream → PV at parent WACC
- Bull overlay: subsidiary sale/IPO at market value, friction-adjusted

**Holding company discount** (separate from R9): apply ONLY if explicitly justified after R9 — R9 already eliminates most of what the holdco discount was historically capturing. Default: no additional discount after R9.

### Example 4 — Stellantis (captive finance via SFS)

Same pattern as Renault. SFS revenue/EBITDA stripped, SFS debt excluded from EV, SFS dividend (~€700m/yr) added as PV stream.

### Example 5 — Berkshire Hathaway (extreme conglomerate case)

R9 applies at scale: insurance subs handled via equity-financials skill (not DCF), wholly-owned operating subs (BNSF, BHE) projected with their own cash flows then their dividends to parent rolled up. Listed equity stakes (Apple, etc.) handled as FVOCI/FVTPL per R9 — dividend stream only, never market value in bridge.

---

## Migration Note (legacy state files)

Any `dcf_state.json` from prior analyses (Renault, Dassault Aviation, Stellantis, Exor) that includes:
- Equity-method carrying value in the bridge, OR
- Captive EBITDA in group projections, OR
- FVOCI/FVTPL stake at fair value in the bridge

...is flagged as **v15.0-legacy** on reload. Engine prints:
> ⚠ State predates v15.1 R9. Non-core treatment is inconsistent with current methodology. Re-run recommended to apply strip-out + dividend-as-FCF rule.

Specifically affects: Renault (×3), Dassault Aviation (×2), Stellantis, Ferrari (×2 — Exor parent comparisons), Bolloré-related analyses.

---

## Common Pitfalls

1. **Forgetting to strip captive D&A** — D&A double-count error. Group D&A includes captive; if you strip revenue/EBITDA but keep D&A, the tax shield calculation breaks.

2. **Double-counting cash** — captive's cash (e.g., €2bn) is on group balance sheet but trapped in the captive. Don't add it to operating net cash.

3. **Forgetting consolidated minorities** — if subsidiary is partially owned, parent only gets pro-rata of dividend. `fy0_dividend_paid` must be the actual amount received by parent, not the subsidiary's total dividend declaration.

4. **Wrong sign on captive dividend in FCF bridge** — Step 7 FCF bridge must SUBTRACT non-core dividend from reported parent FCF to derive operating-only UFCF basis. Reason: reported parent FCF includes dividends-received; the DCF will count them separately via R9.

5. **Using book equity for dividend-stream stake (the historical mistake)** — book equity / FV is a relevant input ONLY for the bull-case monetization overlay, never for the base bridge.

6. **WACC mismatch** — captive may carry different risk than parent. Default: same WACC (consistent capital cost). Exception requires named justification + sensitivity disclosure.
