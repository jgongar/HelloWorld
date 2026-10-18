# Handoff: PEA screening, run 2 (finish from saved data)

You are continuing work started in an earlier session. Everything you need is in this repository on branch `claude/gifted-clarke-6uhqqg`. **Commit and push to that same branch.**

## The user and the goal

- The user is a French retail investor. The task is a systematic screen of **PEA-eligible companies**: registered office in the EU or EEA (Norway, Iceland, Liechtenstein), all sizes.
- The goal is to find **leads where the analyst consensus target is well above the price**. Signals that matter:
  - consensus revisions going up (the "derivative of consensus");
  - growth prospects;
  - balance-sheet strength and hidden assets;
  - moat and market leadership;
  - niche suppliers within supply chains that serve high-demand markets.
- **Style:** quality growth. **Themes:** supply chain, chemicals, alternative themes. **Focus:** medium-sized niche companies; the user already knows the big caps.
- **Thresholds:**
  - market cap ≥ €50m;
  - ≥ €100k traded per day;
  - ≥ 2 analysts;
  - minimum upside to the average target of 35% (small, < €1bn), 25% (mid, €1–5bn) and 15% (large, > €5bn).
- **Scoring weights (agreed):** revisions 25, upside 20, quality 20, growth 15, valuation versus sector 15, balance sheet 5.
- **Broker: Fortuneo.** In a PEA, Fortuneo allows online buying on:
  - Euronext Paris, Brussels and Amsterdam (column `fortuneo` = `direct`);
  - Xetra/Frankfurt at 0.20% with a €20 minimum, €30 foreign broker fee and €400 minimum order (`Xetra/Frankfurt`).
  - Companies with only an open-market Frankfurt line are tagged `German secondary line … check liquidity`. They are buyable in principle, but spreads may be wide.
  - Milan, Madrid, Nordic exchanges, Vienna and Lisbon are **sale-only by phone** (`not online`).
  - Source: Fortuneo's official tariff brochure, https://www.fortuneo.fr/files/tarifs_fortuneo.pdf.
- **The user is budget-constrained (about $65 of usage left).**
  - Do **not** launch parallel agents or workflows.
  - Keep tool calls few.
  - Use **no web research** unless the user explicitly asks for "option B": a light news and consensus check of the top 15 only, with about 1 search per company.

## What is already done

1. Built the universe from three sources (scripts in `research/pea_screen/`):
   - the official Euronext list (ISIN);
   - the Deutsche Börse listed-companies file (ISIN);
   - the Yahoo screener for Madrid, Vienna, the Nordics, Warsaw, Athens, Prague, Budapest, Bucharest and the Baltics.

   After the size and liquidity filters: 1,626 listings, de-duplicated to **1,554 companies**.
2. Fetched Yahoo Finance data on **18 Oct 2026** for every company:
   - consensus targets and analyst count;
   - EPS trend now versus 7, 30, 60 and 90 days ago, plus up/down revision counts;
   - recommendation trend;
   - multiples, margins, cash and debt;
   - 5 years of annual statements;
   - 1 year of weekly prices.
3. Scored every company with `score.py`. **Results: `research/data/2026-10-18/scored_universe.csv`.**
   - 248 companies are excluded: banks, insurers, REITs, non-EU domicile, pre-revenue biotech (column `excluded`).
   - 1,244 have at least 2 analysts.
   - **428 pass the upside threshold and are not excluded.** By Fortuneo access: 130 direct, 97 Xetra/Frankfurt, 165 German secondary line, 36 not online.

There is no need to re-fetch anything. The data is already dated 18 Oct 2026.

## Key columns in `scored_universe.csv`

**Identity and access**
- `symbol`, `name`, `isin`, `venue`, `country`, `sector`, `industry`, `summary` (Yahoo business description), `website`
- `fortuneo`: Fortuneo access
- `all_lines`: every listing of the company
- `size`: S, M or L
- `mcap_eur`, `adv_eur`: market cap and average daily traded value, in euros

**Consensus**
- `price`, `currency`, `n_analysts`
- `target_mean`, `target_median`, `target_high`, `target_low`
- `upside`: mean target ÷ price − 1
- `target_dispersion`
- `reco_mean`: 1 = strong buy, 5 = sell

**Revisions (the consensus derivative)**
- `rev30_fy1`, `rev90_fy1`: change in next year's EPS forecast over 30 and 90 days
- `rev30_fy0`, `rev90_fy0`: the same for the current year
- `up30_*`, `down30_*`: number of analysts who raised or cut, by period
- `net_revisions_30d`
- `buy_share`, `buy_share_chg_3m`: share of Buy ratings and its change over 3 months
- `pt_raises_120d`, `pt_cuts_120d`: price-target raises and cuts over 120 days (sparse for European stocks)

**Growth**
- `eps_growth_fy0`, `eps_growth_fy1`, `rev_growth_fy0`, `rev_growth_fy1`: consensus growth
- `rev_cagr_3y`: historical revenue growth over 3 years

**Valuation**
- `fwd_pe`, `trailing_pe`, `ev_ebitda`, `ev_sales`, `p_book`, `div_yield`, `fcf_yield`
- `peg`: forward P/E relative to forecast growth

**Quality**
- `roic`: return on invested capital, from EBIT × 0.75
- `op_margin`, `gross_margin`, `roe`
- `op_margin_std`: stability of the operating margin over 4 years
- `fcf_conversion`: free cash flow ÷ net income, 3 years
- `piotroski7`: simplified Piotroski financial-health score, 0–7

**Balance sheet**
- `net_cash_to_mcap`, `net_debt_ebitda`

**Momentum**
- `ret_13w`, `ret_26w`, `ret_52w`: price returns over 13, 26 and 52 weeks
- `drawdown_52w`: distance from the 52-week high
- `divergence`: 1 if next year's EPS rose more than 2% over 90 days while the price fell more than 5% over 13 weeks (the "market hasn't noticed" signal)

**Scores**
- `p_revisions`, `p_upside`, `p_quality`, `p_growth`, `p_valuation`, `p_balance`: pillar scores, 0–1 percentile averages
- `score`: 0–100
- `coverage`: covered or uncovered
- `passes_threshold`
- `data_flag`: upside outside −80% to +300%, likely a currency or stale-target issue. Exclude or flag these.
- `r_*`: the individual percentile ranks

## What to produce (option A)

1. **`research/pea-screening-v2.md`**: the final report, built with a short Python script from the CSV.
   - Keep tool calls few; write the narrative per company from the data and the Yahoo `summary`, with no web calls.
   - **Main list: 60 leads.** Take them from `passes_threshold == True`, `excluded` empty and no `data_flag`.
     - Prefer Fortuneo access: `direct`, then `Xetra/Frankfurt`, then German secondary line.
     - Within the main list, show at most about 10 `not online` names, clearly flagged.
     - Rank by `score`, but sanity-check the extremes: for small caps with upside above 150%, check that `n_analysts ≥ 3` or flag them as high risk.
   - **Tiers:**
     - **A:** revisions pillar ≥ 0.6 and quality ≥ 0.5.
     - **B:** neither of those failed badly.
     - **C:** revisions < 0.4 (consensus falling) or quality < 0.35.
   - **For each lead:**
     - what it does (from `summary`, 1–2 sentences);
     - country and venue;
     - Fortuneo access;
     - price → target (number of analysts) and upside;
     - revisions over 30 and 90 days, plus up/down counts;
     - forward P/E, EV/EBITDA and FCF yield;
     - ROIC, margin and Piotroski score;
     - growth;
     - net cash or debt;
     - momentum and the divergence flag;
     - a 2–3 line rationale tagged with a lead type:
       - Revisions↑
       - Forecasts up / price down
       - Cheap vs sector
       - Hidden assets / net cash
       - Niche leader / supply-chain theme (infer from industry and summary)
     - the key risk visible in the data: high leverage, cuts, extreme upside, few analysts, weak cash conversion.
   - **Extra sections:**
     - a top-15 "uncovered gems" table: `coverage == uncovered`, Fortuneo-accessible, highest `score`;
     - a top-15 "divergence" table: `divergence == 1` and passes the threshold;
     - a short comparison with run 1 (`research/pea-screening.md`): which run-1 leads are still in, which dropped out and why (threshold or score).
   - **Method and caveats:**
     - data is from Yahoo Finance and can be stale or single-source for small caps;
     - exchanges in Croatia, Slovenia, Bulgaria, Slovakia, Cyprus and Malta are not covered;
     - some German symbols are missing (e.g. K+S);
     - "not investment advice — verify before acting".
2. **`research/pea-screening-v2.pdf`**: convert with pandoc → HTML → Chromium:
   - `pandoc in.md -f gfm -t html5 -s --metadata pagetitle="PEA screening v2" --css research/pea_screen/pdf/style.css --embed-resources -o out.html`
   - then `NODE_PATH=$(npm root -g) node research/pea_screen/pdf/topdf.js /abs/path/out.html /abs/path/out.pdf`
   - Output is A4 landscape. Playwright is preinstalled globally and Chromium is at /opt/pw-browsers.
3. **`research/pea-screening-v2.xlsx`**:
   - sheet "Leads": the 60;
   - sheet "All passing": the 428;
   - sheet "Universe": all 1,554, with readable column headers, frozen top row and filters.
   - Use openpyxl; install it with pip if missing.
4. Commit and push. Then tell the user, in plain words, what's in the files and the top 10 names.

Finally, ask whether they want option B (a light web check of the top 15) before doing it.
