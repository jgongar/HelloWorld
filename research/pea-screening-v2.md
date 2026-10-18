# PEA screening v2: leads where consensus is well above the price

*Run 2 · data from Yahoo Finance, fetched 2026-10-18 · built from `research/data/2026-10-18/scored_universe.csv` · not investment advice — verify before acting.*

## 1. Summary

- Universe: **1,554 PEA-eligible companies** (EU/EEA registered office, market cap ≥ €50m, ≥ €100k traded per day). 248 excluded (banks, insurers, REITs, non-EU domicile, pre-revenue biotech).
- 428 pass the upside threshold (≥ 2 analysts; upside ≥ 35% small, ≥ 25% mid, ≥ 15% large); 428 of those have clean data (no `data_flag`).
- **Main list: 60 leads**, ranked by score (revisions 25, upside 20, quality 20, growth 15, valuation vs sector 15, balance sheet 5). Fortuneo access: 18 direct, 17 Xetra/Frankfurt, 15 German secondary line, 10 not online (flagged).
- Tiers: **A** 32 (revisions pillar ≥ 0.6 and quality ≥ 0.5), **B** 17, **C** 11 (revisions < 0.4 or quality < 0.35).
- 0 leads carry the high-risk flag (small cap, upside > 150%, fewer than 3 analysts).

## 2. Main list: 60 leads

| # | Company | Country / venue | Size | Fortuneo | Price → target (n) | Upside | Rev. 90d FY+1 | Fwd P/E | ROIC | Score | Tier | Lead type |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **I-Tech AB** | Sweden / Stockholm | S | **Not online** | SEK 65.00 → SEK 119.00 (2) | +83% | +13.3% | 10.3 | 122% | 81 | A | Revisions↑, Hidden assets / net cash, Niche leader / supply-chain theme |
| 2 | **FRIEDRICH VORWERK GROUP SE** | Germany / Xetra/Frankfurt (Prime Standard) | M | Xetra | EUR 66.05 → EUR 90.75 (4) | +37% | +15.2% | 11.4 | 258% | 76 | A | Revisions↑, Forecasts up / price down, Niche leader / supply-chain theme |
| 3 | **Eolus Aktiebolag (publ)** | Sweden / Stockholm | S | **Not online** | SEK 47.25 → SEK 87.55 (2) | +85% | +116.6% | 3.4 | -22% | 75 | C | Revisions↑, Cheap vs sector, Hidden assets / net cash |
| 4 | **HEIJMANS KON** | Netherlands / Euronext Amsterdam | M | Direct | EUR 82.70 → EUR 121.50 (2) | +47% | +13.3% | 10.5 | 28% | 75 | A | Revisions↑, Forecasts up / price down, Cheap vs sector, Niche leader / supply-chain theme |
| 5 | **LNA SANTE** | France / Euronext Paris | S | Direct | EUR 23.40 → EUR 41.10 (4) | +76% | +13.0% | 6.9 | 5% | 75 | A | Revisions↑, Forecasts up / price down, Cheap vs sector, Hidden assets / net cash |
| 6 | **HEXAOM** | France / Euronext Growth Paris | S | Direct | EUR 22.30 → EUR 48.67 (3) | +118% | +17.1% | 4.4 | 8% | 73 | A | Revisions↑, Forecasts up / price down, Cheap vs sector, Hidden assets / net cash |
| 7 | **Rainbow Tours S.A.** | Poland / Warsaw | S | **Not online** | PLN 126.70 → PLN 194.68 (4) | +54% | +12.0% | 7.9 | 102% | 73 | A | Revisions↑, Forecasts up / price down, Cheap vs sector, Hidden assets / net cash |
| 8 | **ASML HOLDING** | Netherlands / Euronext Amsterdam | L | Direct | EUR 1,477 → EUR 2,108 (33) | +43% | +11.0% | 26.4 | 78% | 72 | A | Revisions↑, Forecasts up / price down, Niche leader / supply-chain theme |
| 9 | **Obrascón Huarte Lain, S.A.** | Spain / MCE | S | DE 2nd line | EUR 0.33 → EUR 0.63 (3) | +88% | n/a | 33.4 | 20% | 72 | B | Cheap vs sector, Hidden assets / net cash, Niche leader / supply-chain theme |
| 10 | **FINCANTIERI** | Italy / Euronext Milan | M | DE 2nd line | EUR 12.52 → EUR 17.70 (10) | +41% | +28.4% | 15.2 | 9% | 72 | A | Revisions↑, Cheap vs sector, Niche leader / supply-chain theme |
| 11 | **ACS, Actividades de Construcción y Servicios, S.A.** | Spain / MCE | L | DE 2nd line | EUR 90.00 → EUR 132.71 (16) | +47% | +2.3% | 18.1 | 23% | 71 | A | Revisions↑, Forecasts up / price down, Niche leader / supply-chain theme |
| 12 | **ASM INTERNATIONAL** | Netherlands / Euronext Amsterdam | L | Direct | EUR 753.00 → EUR 1,148 (20) | +53% | +13.8% | 23.8 | 23% | 71 | A | Revisions↑, Forecasts up / price down, Niche leader / supply-chain theme |
| 13 | **TECHNOPROBE** | Italy / Euronext Milan | L | DE 2nd line | EUR 26.52 → EUR 42.80 (10) | +61% | +19.5% | 32.1 | 17% | 71 | A | Revisions↑, Forecasts up / price down, Niche leader / supply-chain theme |
| 14 | **SUSS MicroTec SE** | Germany / Xetra/Frankfurt (Prime Standard) | M | Xetra | EUR 56.35 → EUR 110.44 (8) | +96% | +8.3% | 14.6 | 19% | 70 | B | Revisions↑, Forecasts up / price down, Niche leader / supply-chain theme |
| 15 | **ZEAL NETWORK SE NA O.N.** | Germany / Xetra/Frankfurt (Prime Standard) | S | Xetra | EUR 40.10 → EUR 75.00 (5) | +87% | +3.1% | 16.2 | 23% | 70 | B | Revisions↑, Forecasts up / price down |
| 16 | **Técnicas Reunidas, S.A.** | Spain / MCE | M | DE 2nd line | EUR 26.38 → EUR 39.97 (9) | +52% | +3.9% | 8.1 | 67% | 69 | A | Revisions↑, Forecasts up / price down, Cheap vs sector, Niche leader / supply-chain theme |
| 17 | **HOCHTIEF AG** | Germany / Xetra/Frankfurt (Prime Standard) | L | Xetra | EUR 372.60 → EUR 506.93 (8) | +36% | +8.2% | 20.2 | 40% | 69 | A | Revisions↑, Forecasts up / price down, Niche leader / supply-chain theme |
| 18 | **ASTA Energy Solutions AG** | Austria / Xetra/Frankfurt (Prime Standard) | S | Xetra | EUR 52.60 → EUR 74.33 (3) | +41% | +3.2% | 17.5 | n/a | 69 | A | Revisions↑ |
| 19 | **Thrace Plastics Holding Company S.A.** | Greece / Athens | S | DE 2nd line | EUR 4.87 → EUR 7.58 (2) | +56% | +37.7% | 12.2 | 5% | 68 | A | Revisions↑, Hidden assets / net cash |
| 20 | **Exsitec Holding AB (publ)** | Sweden / Stockholm | S | **Not online** | SEK 109.50 → SEK 164.50 (2) | +50% | +0.2% | 11.8 | 12% | 68 | B | Cheap vs sector, Niche leader / supply-chain theme |
| 21 | **VEF AB (publ)** | Sweden / Stockholm | S | DE 2nd line | SEK 1.99 → SEK 3.01 (4) | +51% | n/a | -9.5 | 16% | 68 | B | Upside to consensus |
| 22 | **Paxman AB (publ)** | Sweden / Stockholm | S | **Not online** | SEK 63.30 → SEK 95.75 (2) | +51% | +11.1% | 13.8 | 1% | 68 | C | Revisions↑, Niche leader / supply-chain theme |
| 23 | **FABASOFT AG** | Austria / Xetra/Frankfurt (Prime Standard) | S | Xetra | EUR 16.15 → EUR 25.50 (2) | +58% | +0.5% | 15.2 | 172% | 68 | B | Cheap vs sector, Niche leader / supply-chain theme |
| 24 | **RVRC Holding AB (publ)** | Sweden / Stockholm | S | DE 2nd line | SEK 53.15 → SEK 80.80 (5) | +52% | +11.0% | 11.4 | 33% | 68 | A | Revisions↑, Forecasts up / price down |
| 25 | **GENERAL OCEANS** | Norway / Oslo Børs | S | DE 2nd line | NOK 20.20 → NOK 28.50 (2) | +41% | +0.0% | 15.9 | 28% | 68 | A | Revisions↑, Niche leader / supply-chain theme |
| 26 | **Truecaller AB (publ)** | Sweden / Stockholm | S | DE 2nd line | SEK 24.38 → SEK 37.17 (6) | +52% | +0.1% | 16.9 | 44% | 68 | B | Niche leader / supply-chain theme |
| 27 | **RugVista Group AB (publ)** | Sweden / Stockholm | S | **Not online** | SEK 67.30 → SEK 92.33 (3) | +37% | +5.8% | 13.2 | 13% | 68 | A | Revisions↑ |
| 28 | **AMG** | Netherlands / Euronext Amsterdam | S | Direct | EUR 25.84 → EUR 46.26 (6) | +79% | +23.8% | 7.6 | 7% | 67 | B | Revisions↑, Cheap vs sector, Niche leader / supply-chain theme |
| 29 | **AT & S Austria Technologie & Systemtechnik Aktiengesellschaft** | Austria / Vienna | L | DE 2nd line | EUR 174.20 → EUR 284.20 (5) | +63% | +75.8% | 14.8 | 2% | 67 | C | Revisions↑ |
| 30 | **WAVESTONE** | France / Euronext Paris | S | Direct | EUR 30.10 → EUR 44.10 (4) | +47% | -2.8% | 7.5 | 14% | 67 | C | Cheap vs sector, Niche leader / supply-chain theme |
| 31 | **SIEMENS ENERGY AG NA O.N.** | Germany / Xetra/Frankfurt (Prime Standard) | L | Xetra | EUR 134.98 → EUR 193.62 (28) | +43% | +3.9% | 21.6 | 37% | 67 | A | Revisions↑, Forecasts up / price down, Niche leader / supply-chain theme |
| 32 | **2CRSI** | France / Euronext Growth Paris | S | Direct | EUR 26.24 → EUR 47.30 (2) | +80% | +14.5% | 8.5 | -14% | 67 | C | Revisions↑, Niche leader / supply-chain theme |
| 33 | **VIRIDIEN** | France / Euronext Paris | S | Direct | EUR 87.90 → EUR 140.48 (6) | +60% | +2.7% | 6.1 | 7% | 67 | B | Cheap vs sector, Hidden assets / net cash |
| 34 | **WS WeSports Group AB (publ)** | Sweden / Stockholm | S | **Not online** | SEK 67.20 → SEK 101.33 (3) | +51% | +9.1% | 9.5 | 5% | 67 | A | Revisions↑ |
| 35 | **Cheffelo AB (publ)** | Sweden / Stockholm | S | **Not online** | SEK 100.00 → SEK 150.67 (3) | +51% | +10.7% | 11.8 | 16% | 67 | B | Revisions↑, Forecasts up / price down |
| 36 | **DIGITAL BROS** | Italy / Euronext Milan | S | **Not online** | EUR 10.40 → EUR 16.25 (2) | +56% | +15.1% | 6.5 | -1% | 67 | C | Revisions↑, Cheap vs sector |
| 37 | **INDUSTRIE DE NORA** | Italy / Euronext Milan | M | **Not online** | EUR 5.58 → EUR 9.30 (7) | +67% | +6.7% | 12.7 | 10% | 66 | A | Revisions↑, Forecasts up / price down, Niche leader / supply-chain theme |
| 38 | **NAPATECH** | Denmark / Oslo Børs | S | DE 2nd line | NOK 41.50 → NOK 73.88 (2) | +78% | +42.0% | 42.3 | -56% | 66 | C | Revisions↑ |
| 39 | **BASLER AG O.N.** | Germany / Xetra/Frankfurt (Prime Standard) | S | Xetra | EUR 21.00 → EUR 29.67 (3) | +41% | +25.1% | 18.1 | 8% | 66 | A | Revisions↑, Forecasts up / price down |
| 40 | **Grifols, S.A.** | Spain / MCE | L | DE 2nd line | EUR 10.18 → EUR 14.76 (12) | +45% | +2.0% | 8.9 | 6% | 66 | A | Cheap vs sector |
| 41 | **TSK Electrónica y Electricidad, S.A.** | Spain / MCE | S | DE 2nd line | EUR 6.58 → EUR 9.66 (3) | +47% | +1.6% | 10.3 | 28% | 66 | A | Revisions↑, Niche leader / supply-chain theme |
| 42 | **Bonesupport Holding AB (publ)** | Sweden / Stockholm | M | DE 2nd line | SEK 253.00 → SEK 357.42 (6) | +41% | +2.4% | 32.2 | 30% | 66 | A | Revisions↑, Niche leader / supply-chain theme |
| 43 | **NORDEX SE O.N.** | Germany / Xetra/Frankfurt (Prime Standard) | L | Xetra | EUR 39.14 → EUR 50.52 (15) | +29% | +10.8% | 14.9 | n/a | 66 | A | Revisions↑, Hidden assets / net cash, Niche leader / supply-chain theme |
| 44 | **ARGENX SE** | Netherlands / Euronext Brussels | L | Direct | EUR 727.60 → EUR 1,008 (15) | +39% | +5.7% | 19.4 | 25% | 66 | A | Revisions↑, Forecasts up / price down, Niche leader / supply-chain theme |
| 45 | **WESTWING GROUP  INH. O.N.** | Germany / Xetra/Frankfurt (Prime Standard) | S | Xetra | EUR 13.25 → EUR 22.17 (3) | +67% | +0.9% | 8.9 | 53% | 66 | B | Cheap vs sector |
| 46 | **AIXTRON SE NA O.N.** | Germany / Xetra/Frankfurt (Prime Standard) | M | Xetra | EUR 32.89 → EUR 48.21 (15) | +47% | +5.8% | 23.9 | 9% | 66 | B | Revisions↑, Forecasts up / price down, Niche leader / supply-chain theme |
| 47 | **MEDIOS AG  O.N.** | Germany / Xetra/Frankfurt (Prime Standard) | S | Xetra | EUR 10.38 → EUR 20.25 (4) | +95% | -11.4% | 6.8 | 6% | 66 | C | Cheap vs sector, Hidden assets / net cash |
| 48 | **BE SEMICONDUCTOR** | Netherlands / Euronext Amsterdam | L | Direct | EUR 155.55 → EUR 270.57 (23) | +74% | +4.2% | 23.7 | 24% | 65 | A | Revisions↑, Forecasts up / price down, Niche leader / supply-chain theme |
| 49 | **TECHNOTRANS SE NA O.N.** | Germany / Xetra/Frankfurt (Prime Standard) | S | Xetra | EUR 26.70 → EUR 39.50 (2) | +48% | +0.9% | 11.7 | 13% | 65 | B | Cheap vs sector, Niche leader / supply-chain theme |
| 50 | **SMCP** | France / Euronext Paris | S | Direct | EUR 5.75 → EUR 8.84 (5) | +54% | +4.2% | 7.3 | 3% | 65 | A | Revisions↑, Cheap vs sector, Hidden assets / net cash |
| 51 | **NEXANS** | France / Euronext Paris | L | Direct | EUR 126.70 → EUR 172.53 (15) | +36% | +1.2% | 13.6 | 12% | 65 | A | Revisions↑, Niche leader / supply-chain theme |
| 52 | **FLATEXDEGIRO SE** | Germany / Xetra/Frankfurt (Prime Standard) | M | Xetra | EUR 25.48 → EUR 43.33 (12) | +70% | +3.6% | 10.6 | n/a | 65 | B | Revisions↑, Forecasts up / price down, Cheap vs sector, Hidden assets / net cash |
| 53 | **DEUTSCHE ROHSTOFF AG NA O.N.** | Germany / Xetra/Frankfurt (Scale) | S | Xetra | EUR 83.50 → EUR 126.50 (2) | +52% | +17.4% | 5.0 | 10% | 64 | B | Revisions↑, Cheap vs sector |
| 54 | **Vusion** | France / Euronext Paris | M | Direct | EUR 123.50 → EUR 203.33 (6) | +65% | -3.0% | 11.1 | 103% | 64 | C | Niche leader / supply-chain theme |
| 55 | **INIT INNOVATION O.N.** | Germany / Xetra/Frankfurt (Prime Standard) | S | Xetra | EUR 42.50 → EUR 65.17 (3) | +53% | -2.1% | 14.0 | 14% | 64 | C | Cheap vs sector, Niche leader / supply-chain theme |
| 56 | **SFC ENERGY AG** | Germany / Xetra/Frankfurt (Prime Standard) | S | Xetra | EUR 18.62 → EUR 27.90 (5) | +50% | +14.0% | 17.1 | 3% | 64 | C | Revisions↑, Forecasts up / price down, Niche leader / supply-chain theme |
| 57 | **CENERGY** | Belgium / Euronext Brussels | M | Direct | EUR 21.80 → EUR 27.60 (3) | +27% | +11.7% | 16.3 | 21% | 64 | A | Revisions↑, Niche leader / supply-chain theme |
| 58 | **SEMCO TECHNOLOGIES** | France / Euronext Growth Paris | S | Direct | EUR 39.60 → EUR 57.40 (5) | +45% | +0.7% | 24.5 | 64% | 64 | B | Niche leader / supply-chain theme |
| 59 | **LAGARDERE SA** | France / Euronext Paris | M | Direct | EUR 18.34 → EUR 27.17 (3) | +48% | +2.3% | 7.7 | 8% | 63 | A | Revisions↑, Cheap vs sector |
| 60 | **VALLOUREC** | France / Euronext Paris | L | Direct | EUR 18.98 → EUR 26.14 (11) | +38% | -7.3% | 9.8 | 21% | 63 | B | Cheap vs sector |

⚠ = high risk (small cap, > 150% upside, fewer than 3 analysts).

## 3. Lead cards

### Tier A

#### 1. I-Tech AB (ITECH.ST) — tier A, score 81

- **What it does:** I-Tech AB provides antifouling coating products in Sweden. It offers Selektope, an antifouling solution, which operates by selectively stimulating octopamine receptors in barnacle larvae, triggering a temporary swimming behavior that causes the larva to detach from the treated surface without being harmed.
- **Listing:** Sweden, Stockholm · Specialty Chemicals · market cap €70m, €142k/day traded · ISIN n/a
- **Fortuneo:** **Not online** (sale by phone only)
- **Consensus:** SEK 65.00 → SEK 119.00 mean (range SEK 98.00–SEK 140.00, 2 analysts), upside **+83%**; recommendation 0.0 (1 = strong buy)
- **Revisions:** FY+1 EPS +6.0% (30d) / +13.3% (90d), 2 up / 0 down; current year -0.2% / +33.4%, 2 up / 0 down
- **Valuation:** fwd P/E 10.3, EV/EBITDA 9.5, FCF yield 5.3%, P/B 4.0
- **Quality:** ROIC 122%, operating margin 27%, Piotroski 4/7, FCF conversion 146%
- **Growth:** sales +23% and EPS +23% next year (consensus); 3-year sales CAGR +26%
- **Balance sheet:** net cash 23% of market cap
- **Momentum:** -4% (13w), -23% (52w), -23% from 52-week high; divergence flag: no
- **Rationale [Revisions↑ · Hidden assets / net cash · Niche leader / supply-chain theme]:** +83% to the mean target of 2 analysts; next-year EPS forecast +13.3% over 90 days (2 up / 0 down in 30 days), consensus EPS growth +23% next year, 10.3× forward earnings, ROIC 122%. Theme: chemicals / materials.
- **Key risk:** only 2 analysts; not buyable online at Fortuneo

#### 2. FRIEDRICH VORWERK GROUP SE (VH2.DE) — tier A, score 76

- **What it does:** Friedrich Vorwerk Group SE provides various solutions for transformation and transportation of energy in Germany and Europe. The company operates through Natural Gas, Electricity, Clean Hydrogen, and Adjacent Opportunities segments.
- **Listing:** Germany, Xetra/Frankfurt (Prime Standard) · Engineering & Construction · market cap €1.3bn, €2.5m/day traded · ISIN DE000A255F11
- **Fortuneo:** Xetra/Frankfurt
- **Consensus:** EUR 66.05 → EUR 90.75 mean (range EUR 70.00–EUR 111.00, 4 analysts), upside **+37%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +10.2% (30d) / +15.2% (90d), 2 up / 0 down; current year +10.5% / +19.4%, 3 up / 0 down
- **Valuation:** fwd P/E 11.4, EV/EBITDA 6.9, FCF yield 8.9%, P/B 4.2
- **Quality:** ROIC 258%, operating margin 20%, Piotroski 7/7, FCF conversion 196%
- **Growth:** sales +12% and EPS +4% next year (consensus); 3-year sales CAGR +24%
- **Balance sheet:** net cash 15% of market cap
- **Momentum:** -7% (13w), -17% (52w), -36% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Niche leader / supply-chain theme]:** +37% to the mean target of 4 analysts; next-year EPS forecast +15.2% over 90 days (2 up / 0 down in 30 days), consensus EPS growth +4% next year, 11.4× forward earnings, ROIC 258%. Theme: energy transition. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** nothing obvious in the data

#### 4. HEIJMANS KON (HEIJM.AS) — tier A, score 75

- **What it does:** Koninklijke Heijmans N.V. engages in the real estate, construction, and infrastructure businesses in the Netherlands and internationally. It focuses on the development of large and smaller-scale projects in urban and out-of-town areas, as well as acts as an initiator, developer, and seller of residential properties.
- **Listing:** Netherlands, Euronext Amsterdam · Engineering & Construction · market cap €2.3bn, €6.6m/day traded · ISIN NL0009269109
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 82.70 → EUR 121.50 mean (range EUR 120.00–EUR 123.00, 2 analysts), upside **+47%**; recommendation 1.0 (1 = strong buy)
- **Revisions:** FY+1 EPS +6.5% (30d) / +13.3% (90d), 1 up / 0 down; current year -8.0% / -1.5%, 1 up / 0 down
- **Valuation:** fwd P/E 10.5, EV/EBITDA 11.1, FCF yield 11.9%, P/B 4.1
- **Quality:** ROIC 28%, operating margin 6%, Piotroski 6/7, FCF conversion 174%
- **Growth:** sales +7% and EPS +31% next year (consensus); 3-year sales CAGR +15%
- **Balance sheet:** net cash 2% of market cap
- **Momentum:** -13% (13w), +41% (52w), -29% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Cheap vs sector · Niche leader / supply-chain theme]:** +47% to the mean target of 2 analysts; next-year EPS forecast +13.3% over 90 days (1 up / 0 down in 30 days), consensus EPS growth +31% next year, 10.5× forward earnings, ROIC 28%. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** only 2 analysts

#### 5. LNA SANTE (LNA.PA) — tier A, score 75

- **What it does:** LNA Santé SA engages in the management and operation of healthcare facilities and medical residences for able-bodied, semi-dependent, or dependent elderly people in France. The company operates medical care and rehabilitation units; mental health clinics; health centres; and care homes.
- **Listing:** France, Euronext Paris · Medical Care Facilities · market cap €241m, €145k/day traded · ISIN FR0004170017
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 23.40 → EUR 41.10 mean (range EUR 36.00–EUR 47.00, 4 analysts), upside **+76%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +3.6% (30d) / +13.0% (90d), 2 up / 0 down; current year -1.9% / +9.7%, 2 up / 0 down
- **Valuation:** fwd P/E 6.9, EV/EBITDA 11.1, FCF yield 39.0%, P/B 0.7
- **Quality:** ROIC 5%, operating margin 7%, Piotroski 6/7, FCF conversion 388%
- **Growth:** sales +6% and EPS +21% next year (consensus); 3-year sales CAGR +8%
- **Balance sheet:** net debt 8.6× EBITDA
- **Momentum:** -33% (13w), -0% (52w), -35% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Cheap vs sector · Hidden assets / net cash]:** +76% to the mean target of 4 analysts; next-year EPS forecast +13.0% over 90 days (2 up / 0 down in 30 days), consensus EPS growth +21% next year, 6.9× forward earnings, ROIC 5%. Theme: healthcare niche. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** high leverage (net debt 8.6× EBITDA)

#### 6. HEXAOM (ALHEX.PA) — tier A, score 73

- **What it does:** Hexaom S.A. engages in the land and real estate development, and house construction and renovation businesses in France. It also offers services, including financial brokerage and insurance; and offers partner network for kitchen design and installation, implementation of a monitoring system, construction of a swimming pool,….
- **Listing:** France, Euronext Growth Paris · Residential Construction · market cap €153m, €187k/day traded · ISIN FR0004159473
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 22.30 → EUR 48.67 mean (range EUR 44.00–EUR 55.00, 3 analysts), upside **+118%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +0.0% (30d) / +17.1% (90d), 1 up / 0 down; current year +1.0% / -4.5%, 1 up / 0 down
- **Valuation:** fwd P/E 4.4, EV/EBITDA 2.8, FCF yield 28.2%, P/B 0.6
- **Quality:** ROIC 8%, operating margin 6%, Piotroski 4/7, FCF conversion 123%
- **Growth:** sales +12% and EPS +34% next year (consensus); 3-year sales CAGR -14%
- **Balance sheet:** net cash 31% of market cap
- **Momentum:** -16% (13w), -24% (52w), -38% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Cheap vs sector · Hidden assets / net cash]:** +118% to the mean target of 3 analysts; next-year EPS forecast +17.1% over 90 days (1 up / 0 down in 30 days), consensus EPS growth +34% next year, 4.4× forward earnings, ROIC 8%. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** extreme upside (+118%) — check the targets are fresh

#### 7. Rainbow Tours S.A. (RBW.WA) — tier A, score 73

- **What it does:** Rainbow Tours S.A. operates as a tour operator in Poland. The company operates through Sale of Tourist Events, Hotel, and Others segments.
- **Listing:** Poland, Warsaw · Travel Services · market cap €422m, €829k/day traded · ISIN n/a
- **Fortuneo:** **Not online** (sale by phone only)
- **Consensus:** PLN 126.70 → PLN 194.68 mean (range PLN 169.00–PLN 225.00, 4 analysts), upside **+54%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +7.3% (30d) / +12.0% (90d), 0 up / 1 down; current year +7.3% / +8.7%, 1 up / 0 down
- **Valuation:** fwd P/E 7.9, EV/EBITDA 4.2, FCF yield 15.2%, P/B 3.8
- **Quality:** ROIC 102%, operating margin 2%, Piotroski 5/7, FCF conversion 112%
- **Growth:** sales +9% and EPS -6% next year (consensus); 3-year sales CAGR +24%
- **Balance sheet:** net cash 28% of market cap
- **Momentum:** -8% (13w), +3% (52w), -21% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Cheap vs sector · Hidden assets / net cash]:** +54% to the mean target of 4 analysts; next-year EPS forecast +12.0% over 90 days (0 up / 1 down in 30 days), consensus EPS growth -6% next year, 7.9× forward earnings, ROIC 102%. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** not buyable online at Fortuneo

#### 8. ASML HOLDING (ASML.AS) — tier A, score 72

- **What it does:** ASML Holding N.V. provides lithography solutions for the development, production, marketing, sales, upgrading, and servicing of advanced semiconductor equipment systems. The company offers lithography, metrology, and inspection systems.
- **Listing:** Netherlands, Euronext Amsterdam · Semiconductor Equipment & Materials · market cap €569.3bn, €875m/day traded · ISIN NL0010273215
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 1,477 → EUR 2,108 mean (range EUR 1,288–EUR 2,600, 33 analysts), upside **+43%**; recommendation 1.4 (1 = strong buy)
- **Revisions:** FY+1 EPS +8.1% (30d) / +11.0% (90d), 4 up / 1 down; current year +7.9% / +8.8%, 2 up / 1 down
- **Valuation:** fwd P/E 26.4, EV/EBITDA 34.3, FCF yield 1.8%, P/B 25.6
- **Quality:** ROIC 78%, operating margin 44%, Piotroski n/a/7, FCF conversion 93%
- **Growth:** sales +29% and EPS +36% next year (consensus); 3-year sales CAGR +16%
- **Balance sheet:** net cash 2% of market cap
- **Momentum:** -5% (13w), +69% (52w), -11% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Niche leader / supply-chain theme]:** +43% to the mean target of 33 analysts; next-year EPS forecast +11.0% over 90 days (4 up / 1 down in 30 days), consensus EPS growth +36% next year, 26.4× forward earnings, ROIC 78%. Theme: AI / data centres. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** wide spread of analyst targets

#### 10. FINCANTIERI (FCT.MI) — tier A, score 72

- **What it does:** Fincantieri S.p.A. operates in the shipbuilding industry worldwide. It operates through four segments: Shipbuilding; Offshore and Specialized Vessels; Underwater; and Equipment, Systems, and Infrastructure.
- **Listing:** Italy, Euronext Milan · Aerospace & Defense · market cap €4.7bn, €29m/day traded · ISIN IT0005599938
- **Fortuneo:** German secondary line (check liquidity)
- **Consensus:** EUR 12.52 → EUR 17.70 mean (range EUR 15.00–EUR 20.50, 10 analysts), upside **+41%**; recommendation 1.4 (1 = strong buy)
- **Revisions:** FY+1 EPS +1.8% (30d) / +28.4% (90d), 5 up / 0 down; current year -2.0% / +17.4%, 8 up / 0 down
- **Valuation:** fwd P/E 15.2, EV/EBITDA 10.5, FCF yield 13.8%, P/B 2.8
- **Quality:** ROIC 9%, operating margin 5%, Piotroski 7/7, FCF conversion 741%
- **Growth:** sales +12% and EPS +50% next year (consensus); 3-year sales CAGR +7%
- **Balance sheet:** net debt 3.2× EBITDA
- **Momentum:** -2% (13w), -43% (52w), -46% from 52-week high; divergence flag: no
- **Rationale [Revisions↑ · Cheap vs sector · Niche leader / supply-chain theme]:** +41% to the mean target of 10 analysts; next-year EPS forecast +28.4% over 90 days (5 up / 0 down in 30 days), consensus EPS growth +50% next year, 15.2× forward earnings, ROIC 9%. Theme: defence, energy transition.
- **Key risk:** high leverage (net debt 3.2× EBITDA); German secondary line: spreads may be wide

#### 11. ACS, Actividades de Construcción y Servicios, S.A. (ACS.MC) — tier A, score 71

- **What it does:** ACS, Actividades de Construcción y Servicios, S.A. provides construction and related services in Spain, the United States, Australia, Canada, Germany, the rest of Europe, and internationally. It operates through five segments: Turner, CIMIC, Engineering and Construction, Infrastructure, and Other.
- **Listing:** Spain, MCE · Engineering & Construction · market cap €23.5bn, €44m/day traded · ISIN n/a
- **Fortuneo:** German secondary line (check liquidity)
- **Consensus:** EUR 90.00 → EUR 132.71 mean (range EUR 93.00–EUR 159.00, 16 analysts), upside **+47%**; recommendation 1.9 (1 = strong buy)
- **Revisions:** FY+1 EPS +0.9% (30d) / +2.3% (90d), 3 up / 2 down; current year +0.3% / +1.6%, 3 up / 1 down
- **Valuation:** fwd P/E 18.1, EV/EBITDA 10.6, FCF yield 12.7%, P/B 4.0
- **Quality:** ROIC 23%, operating margin 4%, Piotroski 6/7, FCF conversion 213%
- **Growth:** sales +11% and EPS +19% next year (consensus); 3-year sales CAGR +14%
- **Balance sheet:** net debt 0.2× EBITDA
- **Momentum:** -22% (13w), +28% (52w), -34% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Niche leader / supply-chain theme]:** +47% to the mean target of 16 analysts; next-year EPS forecast +2.3% over 90 days (3 up / 2 down in 30 days), consensus EPS growth +19% next year, 18.1× forward earnings, ROIC 23%. Theme: AI / data centres, energy transition. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** German secondary line: spreads may be wide

#### 12. ASM INTERNATIONAL (ASM.AS) — tier A, score 71

- **What it does:** ASM International NV, together with its subsidiaries, engages in the research, development, manufacturing, marketing, and servicing of equipment and materials used to produce semiconductor devices in the United States, Europe, and Asia. The company offers equipment used in wafer processing, which encompasses the fabrication….
- **Listing:** Netherlands, Euronext Amsterdam · Semiconductor Equipment & Materials · market cap €36.8bn, €124m/day traded · ISIN NL0000334118
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 753.00 → EUR 1,148 mean (range EUR 690.00–EUR 1,457, 20 analysts), upside **+53%**; recommendation 1.6 (1 = strong buy)
- **Revisions:** FY+1 EPS +3.0% (30d) / +13.8% (90d), 4 up / 0 down; current year +0.3% / +5.3%, 2 up / 0 down
- **Valuation:** fwd P/E 23.8, EV/EBITDA 31.0, FCF yield 0.6%, P/B 8.3
- **Quality:** ROIC 23%, operating margin 32%, Piotroski 5/7, FCF conversion 71%
- **Growth:** sales +30% and EPS +35% next year (consensus); 3-year sales CAGR +10%
- **Balance sheet:** net cash 3% of market cap
- **Momentum:** -12% (13w), +41% (52w), -29% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Niche leader / supply-chain theme]:** +53% to the mean target of 20 analysts; next-year EPS forecast +13.8% over 90 days (4 up / 0 down in 30 days), consensus EPS growth +35% next year, 23.8× forward earnings, ROIC 23%. Theme: AI / data centres, chemicals / materials. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** wide spread of analyst targets

#### 13. TECHNOPROBE (TPRO.MI) — tier A, score 71

- **What it does:** Technoprobe S.p.A., together with its subsidiaries, produces and sells electronic circuits in Italy, Asia, the United States, and rest of Europe. The company provides mechanical interfaces for electrical contacting of hybrid circuits and semiconductor devices; and engages in the design, development, and production of probe….
- **Listing:** Italy, Euronext Milan · Semiconductors · market cap €17.0bn, €31m/day traded · ISIN IT0005482333
- **Fortuneo:** German secondary line (check liquidity)
- **Consensus:** EUR 26.52 → EUR 42.80 mean (range EUR 34.00–EUR 50.00, 10 analysts), upside **+61%**; recommendation 1.4 (1 = strong buy)
- **Revisions:** FY+1 EPS +4.1% (30d) / +19.5% (90d), 2 up / 0 down; current year +0.3% / +17.5%, 0 up / 1 down
- **Valuation:** fwd P/E 32.1, EV/EBITDA 57.0, FCF yield 0.3%, P/B 12.2
- **Quality:** ROIC 17%, operating margin 37%, Piotroski 7/7, FCF conversion 50%
- **Growth:** sales +44% and EPS +51% next year (consensus); 3-year sales CAGR +5%
- **Balance sheet:** net cash 4% of market cap
- **Momentum:** -11% (13w), +202% (52w), -29% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Niche leader / supply-chain theme]:** +61% to the mean target of 10 analysts; next-year EPS forecast +19.5% over 90 days (2 up / 0 down in 30 days), consensus EPS growth +51% next year, 32.1× forward earnings, ROIC 17%. Theme: AI / data centres. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** weak cash conversion (50% FCF/NI); German secondary line: spreads may be wide

#### 16. Técnicas Reunidas, S.A. (TRE.MC) — tier A, score 69

- **What it does:** Técnicas Reunidas, S.A., an engineering and construction company, designs and manages industrial plant projects worldwide. It operates through Upstream & Refining, Natural gas, Petrochemical, Low-carbon technologies, and Other segments.
- **Listing:** Spain, MCE · Engineering & Construction · market cap €2.0bn, €5.2m/day traded · ISIN n/a
- **Fortuneo:** German secondary line (check liquidity)
- **Consensus:** EUR 26.38 → EUR 39.97 mean (range EUR 28.50–EUR 49.00, 9 analysts), upside **+52%**; recommendation 1.7 (1 = strong buy)
- **Revisions:** FY+1 EPS +1.5% (30d) / +3.9% (90d), 1 up / 0 down; current year +0.1% / -8.7%, 0 up / 1 down
- **Valuation:** fwd P/E 8.1, EV/EBITDA 6.7, FCF yield 3.8%, P/B 3.4
- **Quality:** ROIC 67%, operating margin 2%, Piotroski 6/7, FCF conversion 88%
- **Growth:** sales +3% and EPS +38% next year (consensus); 3-year sales CAGR +15%
- **Balance sheet:** net cash 12% of market cap
- **Momentum:** -9% (13w), -14% (52w), -29% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Cheap vs sector · Niche leader / supply-chain theme]:** +52% to the mean target of 9 analysts; next-year EPS forecast +3.9% over 90 days (1 up / 0 down in 30 days), consensus EPS growth +38% next year, 8.1× forward earnings, ROIC 67%. Theme: chemicals / materials. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** wide spread of analyst targets; German secondary line: spreads may be wide

#### 17. HOCHTIEF AG (HOT.DE) — tier A, score 69

- **What it does:** HOCHTIEF Aktiengesellschaft engages in the construction business worldwide. It operates under Turner, CIMIC, Engineering and construction, and Abertis segment.
- **Listing:** Germany, Xetra/Frankfurt (Prime Standard) · Engineering & Construction · market cap €28.0bn, €24m/day traded · ISIN DE0006070006
- **Fortuneo:** Xetra/Frankfurt
- **Consensus:** EUR 372.60 → EUR 506.93 mean (range EUR 387.00–EUR 605.00, 8 analysts), upside **+36%**; recommendation 2.6 (1 = strong buy)
- **Revisions:** FY+1 EPS +2.7% (30d) / +8.2% (90d), 1 up / 1 down; current year +1.1% / +5.4%, 1 up / 0 down
- **Valuation:** fwd P/E 20.2, EV/EBITDA 17.4, FCF yield 8.0%, P/B 21.6
- **Quality:** ROIC 40%, operating margin 4%, Piotroski 6/7, FCF conversion 200%
- **Growth:** sales +13% and EPS +27% next year (consensus); 3-year sales CAGR +13%
- **Balance sheet:** net debt 0.6× EBITDA
- **Momentum:** -17% (13w), +48% (52w), -32% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Niche leader / supply-chain theme]:** +36% to the mean target of 8 analysts; next-year EPS forecast +8.2% over 90 days (1 up / 1 down in 30 days), consensus EPS growth +27% next year, 20.2× forward earnings, ROIC 40%. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** nothing obvious in the data

#### 18. ASTA Energy Solutions AG (1AST.DE) — tier A, score 69

- **What it does:** ASTA Energy Solutions AG produces and sells copper-based solutions for high-performance power transmission, generation, and e-mobility applications. It offers Roebelbars for use in generators; continuously transposed conductors for power and distribution transformers; and transaction transformer for rail transportation, as….
- **Listing:** Austria, Xetra/Frankfurt (Prime Standard) · Electrical Equipment & Parts · market cap €749m, €1.3m/day traded · ISIN AT100ASTA001
- **Fortuneo:** Xetra/Frankfurt
- **Consensus:** EUR 52.60 → EUR 74.33 mean (range EUR 64.00–EUR 90.00, 3 analysts), upside **+41%**; recommendation 1.3 (1 = strong buy)
- **Revisions:** FY+1 EPS +0.4% (30d) / +3.2% (90d), 2 up / 0 down; current year +9.4% / +9.4%, 1 up / 0 down
- **Valuation:** fwd P/E 17.5, EV/EBITDA 11.2, FCF yield n/a, P/B 3.2
- **Quality:** ROIC n/a, operating margin 8%, Piotroski n/a/7, FCF conversion n/a
- **Growth:** sales +13% and EPS +40% next year (consensus); 3-year sales CAGR n/a
- **Balance sheet:** net cash 6% of market cap
- **Momentum:** n/a (13w), n/a (52w), n/a from 52-week high; divergence flag: no
- **Rationale [Revisions↑]:** +41% to the mean target of 3 analysts; next-year EPS forecast +3.2% over 90 days (2 up / 0 down in 30 days), consensus EPS growth +40% next year, 17.5× forward earnings.
- **Key risk:** nothing obvious in the data

#### 19. Thrace Plastics Holding Company S.A. (PLAT.AT) — tier A, score 68

- **What it does:** Thrace Plastics Holding Company S.A. provides technical fabrics and packaging solutions in the United Kingdom, European Union, the rest of Europe, the United States, and internationally. It operates through Technical Fabrics, Packaging, and Other segments.
- **Listing:** Greece, Athens · Textile Manufacturing · market cap €209m, €197k/day traded · ISIN n/a
- **Fortuneo:** German secondary line (check liquidity)
- **Consensus:** EUR 4.87 → EUR 7.58 mean (range EUR 7.10–EUR 8.05, 2 analysts), upside **+56%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +37.7% (30d) / +37.7% (90d), 2 up / 0 down; current year +44.9% / +44.9%, 2 up / 0 down
- **Valuation:** fwd P/E 12.2, EV/EBITDA 4.8, FCF yield -1.6%, P/B 0.7
- **Quality:** ROIC 5%, operating margin 12%, Piotroski 6/7, FCF conversion 73%
- **Growth:** sales +6% and EPS n/a next year (consensus); 3-year sales CAGR -0%
- **Balance sheet:** net debt 1.2× EBITDA
- **Momentum:** +6% (13w), +23% (52w), -10% from 52-week high; divergence flag: no
- **Rationale [Revisions↑ · Hidden assets / net cash]:** +56% to the mean target of 2 analysts; next-year EPS forecast +37.7% over 90 days (2 up / 0 down in 30 days), 12.2× forward earnings, ROIC 5%. Theme: energy transition, healthcare niche.
- **Key risk:** only 2 analysts; German secondary line: spreads may be wide

#### 24. RVRC Holding AB (publ) (RVRC.ST) — tier A, score 68

- **What it does:** RVRC Holding AB (publ), together with its subsidiaries, engages in the e-commerce of active outdoor clothing and equipment in Germany, Sweden, and internationally. The company offers pants, alpine products for demanding conditions, cross-country skiing, cycling, outwear for cold climates, softshell and hybrid products,….
- **Listing:** Sweden, Stockholm · Apparel Retail · market cap €499m, €1.5m/day traded · ISIN n/a
- **Fortuneo:** German secondary line (check liquidity)
- **Consensus:** SEK 53.15 → SEK 80.80 mean (range SEK 77.00–SEK 85.00, 5 analysts), upside **+52%**; recommendation 1.2 (1 = strong buy)
- **Revisions:** FY+1 EPS -0.2% (30d) / +11.0% (90d), 0 up / 2 down; current year +0.8% / +9.6%, 2 up / 0 down
- **Valuation:** fwd P/E 11.4, EV/EBITDA 12.7, FCF yield 6.4%, P/B 4.4
- **Quality:** ROIC 33%, operating margin 16%, Piotroski 5/7, FCF conversion 106%
- **Growth:** sales +13% and EPS +16% next year (consensus); 3-year sales CAGR +9%
- **Balance sheet:** net cash 6% of market cap
- **Momentum:** -11% (13w), -2% (52w), -25% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down]:** +52% to the mean target of 5 analysts; next-year EPS forecast +11.0% over 90 days (0 up / 2 down in 30 days), consensus EPS growth +16% next year, 11.4× forward earnings, ROIC 33%. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** estimate cuts; German secondary line: spreads may be wide

#### 25. GENERAL OCEANS (GENO.OL) — tier A, score 68

- **What it does:** General Oceans ASA develops and manufactures oceanographic sensors, underwater vehicle systems, robotic manipulators, and software in Norway and Internationally. The company operates through two segments: Sensors and Robotics.
- **Listing:** Norway, Oslo Børs · Scientific & Technical Instruments · market cap €362m, €382k/day traded · ISIN NO0013713115
- **Fortuneo:** German secondary line (check liquidity)
- **Consensus:** NOK 20.20 → NOK 28.50 mean (range NOK 27.00–NOK 30.00, 2 analysts), upside **+41%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +0.0% (30d) / +0.0% (90d), 0 up / 0 down; current year +11.9% / +11.9%, 1 up / 0 down
- **Valuation:** fwd P/E 15.9, EV/EBITDA 16.3, FCF yield n/a, P/B 3.0
- **Quality:** ROIC 28%, operating margin 18%, Piotroski 7/7, FCF conversion 228%
- **Growth:** sales +10% and EPS +18% next year (consensus); 3-year sales CAGR n/a
- **Balance sheet:** net cash 12% of market cap
- **Momentum:** -3% (13w), -20% (52w), -35% from 52-week high; divergence flag: no
- **Rationale [Revisions↑ · Niche leader / supply-chain theme]:** +41% to the mean target of 2 analysts; next-year EPS forecast +0.0% over 90 days (0 up / 0 down in 30 days), consensus EPS growth +18% next year, 15.9× forward earnings, ROIC 28%. Theme: defence, automation / industrial tech.
- **Key risk:** only 2 analysts; German secondary line: spreads may be wide

#### 27. RugVista Group AB (publ) (RUG.ST) — tier A, score 68

- **What it does:** RugVista Group AB (publ) operates direct-to-consumer online platforms for carpet and rug sales in Sweden, Germany, Austria, Switzerland, and internationally. The company offers carpets and rugs under the RugVista and CarpetVista brands.
- **Listing:** Sweden, Stockholm · Home Improvement Retail · market cap €126m, €140k/day traded · ISIN n/a
- **Fortuneo:** **Not online** (sale by phone only)
- **Consensus:** SEK 67.30 → SEK 92.33 mean (range SEK 90.00–SEK 96.00, 3 analysts), upside **+37%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +0.9% (30d) / +5.8% (90d), 1 up / 0 down; current year +0.4% / +12.5%, 1 up / 0 down
- **Valuation:** fwd P/E 13.2, EV/EBITDA 12.8, FCF yield 6.0%, P/B 2.7
- **Quality:** ROIC 13%, operating margin 12%, Piotroski 5/7, FCF conversion 135%
- **Growth:** sales +10% and EPS +20% next year (consensus); 3-year sales CAGR +7%
- **Balance sheet:** net cash 1% of market cap
- **Momentum:** +9% (13w), -9% (52w), -14% from 52-week high; divergence flag: no
- **Rationale [Revisions↑]:** +37% to the mean target of 3 analysts; next-year EPS forecast +5.8% over 90 days (1 up / 0 down in 30 days), consensus EPS growth +20% next year, 13.2× forward earnings, ROIC 13%.
- **Key risk:** not buyable online at Fortuneo

#### 31. SIEMENS ENERGY AG NA O.N. (ENR.DE) — tier A, score 67

- **What it does:** Siemens Energy AG operates as an energy technology company worldwide. It operates through Gas Services, Grid Technologies, Transformation of Industry, and Siemens Gamesa segments.
- **Listing:** Germany, Xetra/Frankfurt (Prime Standard) · Specialty Industrial Machinery · market cap €114.8bn, €266m/day traded · ISIN DE000ENER6Y0
- **Fortuneo:** Xetra/Frankfurt
- **Consensus:** EUR 134.98 → EUR 193.62 mean (range EUR 100.00–EUR 260.00, 28 analysts), upside **+43%**; recommendation 1.9 (1 = strong buy)
- **Revisions:** FY+1 EPS +0.6% (30d) / +3.9% (90d), 7 up / 1 down; current year +1.0% / +3.6%, 5 up / 2 down
- **Valuation:** fwd P/E 21.6, EV/EBITDA 23.2, FCF yield 5.4%, P/B 10.7
- **Quality:** ROIC 37%, operating margin 13%, Piotroski 7/7, FCF conversion n/a
- **Growth:** sales +15% and EPS +38% next year (consensus); 3-year sales CAGR +10%
- **Balance sheet:** net cash 7% of market cap
- **Momentum:** -11% (13w), +34% (52w), -28% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Niche leader / supply-chain theme]:** +43% to the mean target of 28 analysts; next-year EPS forecast +3.9% over 90 days (7 up / 1 down in 30 days), consensus EPS growth +38% next year, 21.6× forward earnings, ROIC 37%. Theme: energy transition. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** wide spread of analyst targets

#### 34. WS WeSports Group AB (publ) (WSG.ST) — tier A, score 67

- **What it does:** WS WeSports Group AB (publ) distributes sports and leisure equipment in Sweden, Finland, Norway, Denmark, Germany, the Netherlands, and internationally. The company offers sports products related to cycling, fitness, running, hockey, football, skiing, golf, and outdoor.
- **Listing:** Sweden, Stockholm · Leisure · market cap €168m, €110k/day traded · ISIN n/a
- **Fortuneo:** **Not online** (sale by phone only)
- **Consensus:** SEK 67.20 → SEK 101.33 mean (range SEK 99.00–SEK 105.00, 3 analysts), upside **+51%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +0.0% (30d) / +9.1% (90d), 2 up / 1 down; current year +0.0% / +11.2%, 1 up / 1 down
- **Valuation:** fwd P/E 9.5, EV/EBITDA 8.1, FCF yield 1.3%, P/B 1.3
- **Quality:** ROIC 5%, operating margin 6%, Piotroski 6/7, FCF conversion n/a
- **Growth:** sales +9% and EPS +21% next year (consensus); 3-year sales CAGR +25%
- **Balance sheet:** net debt 0.8× EBITDA
- **Momentum:** +20% (13w), -1% (52w), -5% from 52-week high; divergence flag: no
- **Rationale [Revisions↑]:** +51% to the mean target of 3 analysts; next-year EPS forecast +9.1% over 90 days (2 up / 1 down in 30 days), consensus EPS growth +21% next year, 9.5× forward earnings, ROIC 5%.
- **Key risk:** not buyable online at Fortuneo

#### 37. INDUSTRIE DE NORA (DNR.MI) — tier A, score 66

- **What it does:** Industrie De Nora S.p.A., through its subsidiaries, delivers electrochemical solutions worldwide and operates through the Electrode Technologies, Water Technologies, and Energy Transition segments. Its Electrode Technologies segment offers metal electrodes coated with catalysts, electrolyzer components, and systems with….
- **Listing:** Italy, Euronext Milan · Electrical Equipment & Parts · market cap €1.1bn, €2.1m/day traded · ISIN IT0005186371
- **Fortuneo:** **Not online** (sale by phone only)
- **Consensus:** EUR 5.58 → EUR 9.30 mean (range EUR 7.00–EUR 15.10, 7 analysts), upside **+67%**; recommendation 1.9 (1 = strong buy)
- **Revisions:** FY+1 EPS +3.5% (30d) / +6.7% (90d), 3 up / 0 down; current year +1.7% / +3.1%, 2 up / 1 down
- **Valuation:** fwd P/E 12.7, EV/EBITDA 7.4, FCF yield -3.9%, P/B 1.1
- **Quality:** ROIC 10%, operating margin 16%, Piotroski 6/7, FCF conversion 36%
- **Growth:** sales +10% and EPS +28% next year (consensus); 3-year sales CAGR +1%
- **Balance sheet:** net debt 0.2× EBITDA
- **Momentum:** -8% (13w), -29% (52w), -29% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Niche leader / supply-chain theme]:** +67% to the mean target of 7 analysts; next-year EPS forecast +6.7% over 90 days (3 up / 0 down in 30 days), consensus EPS growth +28% next year, 12.7× forward earnings, ROIC 10%. Theme: chemicals / materials, energy transition. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** weak cash conversion (36% FCF/NI); wide spread of analyst targets; not buyable online at Fortuneo

#### 39. BASLER AG O.N. (BSL.DE) — tier A, score 66

- **What it does:** Basler Aktiengesellschaft engages in the development, manufacture, and sale of digital cameras for professional users in Germany and internationally. The company provides area scan, line scan, SWR and UV, and 3D- cameras; fixed focal lenses, telecentric lenses, and lens accessories; LED illumination, which include bar, ring,….
- **Listing:** Germany, Xetra/Frankfurt (Prime Standard) · Consumer Electronics · market cap €646m, €840k/day traded · ISIN DE0005102008
- **Fortuneo:** Xetra/Frankfurt
- **Consensus:** EUR 21.00 → EUR 29.67 mean (range EUR 29.00–EUR 31.00, 3 analysts), upside **+41%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +10.8% (30d) / +25.1% (90d), 1 up / 0 down; current year +5.4% / +22.0%, 1 up / 0 down
- **Valuation:** fwd P/E 18.1, EV/EBITDA 16.4, FCF yield 3.2%, P/B 4.2
- **Quality:** ROIC 8%, operating margin 14%, Piotroski 7/7, FCF conversion n/a
- **Growth:** sales +10% and EPS +19% next year (consensus); 3-year sales CAGR -6%
- **Balance sheet:** net debt 0.7× EBITDA
- **Momentum:** -21% (13w), +16% (52w), -33% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down]:** +41% to the mean target of 3 analysts; next-year EPS forecast +25.1% over 90 days (1 up / 0 down in 30 days), consensus EPS growth +19% next year, 18.1× forward earnings, ROIC 8%. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** nothing obvious in the data

#### 40. Grifols, S.A. (GRF.MC) — tier A, score 66

- **What it does:** Grifols, S.A., together with its subsidiaries, engages in the research, development, production, and marketing of plasma-derived medicines in the United States, Canada, Spain, Europe, and internationally. It operates through four segments: Biopharma, Diagnostic, Bio Supplies, and Others.
- **Listing:** Spain, MCE · Drug Manufacturers - General · market cap €6.9bn, €15m/day traded · ISIN n/a
- **Fortuneo:** German secondary line (check liquidity)
- **Consensus:** EUR 10.18 → EUR 14.76 mean (range EUR 9.00–EUR 23.00, 12 analysts), upside **+45%**; recommendation 2.0 (1 = strong buy)
- **Revisions:** FY+1 EPS +0.2% (30d) / +2.0% (90d), 2 up / 0 down; current year +0.1% / +5.0%, 1 up / 1 down
- **Valuation:** fwd P/E 8.9, EV/EBITDA 11.1, FCF yield 8.3%, P/B 1.2
- **Quality:** ROIC 6%, operating margin 16%, Piotroski 6/7, FCF conversion 177%
- **Growth:** sales +6% and EPS +27% next year (consensus); 3-year sales CAGR +7%
- **Balance sheet:** net debt 5.4× EBITDA
- **Momentum:** +5% (13w), -14% (52w), -14% from 52-week high; divergence flag: no
- **Rationale [Cheap vs sector]:** +45% to the mean target of 12 analysts; next-year EPS forecast +2.0% over 90 days (2 up / 0 down in 30 days), consensus EPS growth +27% next year, 8.9× forward earnings, ROIC 6%. Theme: healthcare niche.
- **Key risk:** high leverage (net debt 5.4× EBITDA); wide spread of analyst targets; German secondary line: spreads may be wide

#### 41. TSK Electrónica y Electricidad, S.A. (TSK.MC) — tier A, score 66

- **What it does:** TSK Electrónica y Electricidad, S.A. provides infrastructure solutions for the energy transition, digitalization, and critical raw material handling industry. It operates through two segments: Energy Transition and Digitalisation, and Handling and Mining.
- **Listing:** Spain, MCE · Engineering & Construction · market cap €783m, €1.2m/day traded · ISIN n/a
- **Fortuneo:** German secondary line (check liquidity)
- **Consensus:** EUR 6.58 → EUR 9.66 mean (range EUR 9.30–EUR 10.28, 3 analysts), upside **+47%**; recommendation 1.0 (1 = strong buy)
- **Revisions:** FY+1 EPS +0.0% (30d) / +1.6% (90d), 1 up / 0 down; current year +4.7% / +20.9%, 2 up / 0 down
- **Valuation:** fwd P/E 10.3, EV/EBITDA 10.9, FCF yield n/a, P/B 2.7
- **Quality:** ROIC 28%, operating margin 8%, Piotroski 6/7, FCF conversion -307%
- **Growth:** sales +11% and EPS +7% next year (consensus); 3-year sales CAGR n/a
- **Balance sheet:** net cash 14% of market cap
- **Momentum:** n/a (13w), n/a (52w), n/a from 52-week high; divergence flag: no
- **Rationale [Revisions↑ · Niche leader / supply-chain theme]:** +47% to the mean target of 3 analysts; next-year EPS forecast +1.6% over 90 days (1 up / 0 down in 30 days), consensus EPS growth +7% next year, 10.3× forward earnings, ROIC 28%. Theme: AI / data centres, automation / industrial tech.
- **Key risk:** weak cash conversion (-307% FCF/NI); German secondary line: spreads may be wide

#### 42. Bonesupport Holding AB (publ) (BONEX.ST) — tier A, score 66

- **What it does:** Bonesupport Holding AB (publ), an orthobiologics company, develops and commercializes injectable bio-ceramic bone graft substitutes in the United States, Europe, and internationally. The company offers CERAMENT Bone Void Filler, an injectable ceramic bone graft substitute that remodels to host bone; CERAMENT G, an injectable….
- **Listing:** Sweden, Stockholm · Medical Instruments & Supplies · market cap €1.5bn, €6.1m/day traded · ISIN n/a
- **Fortuneo:** German secondary line (check liquidity)
- **Consensus:** SEK 253.00 → SEK 357.42 mean (range SEK 280.00–SEK 416.00, 6 analysts), upside **+41%**; recommendation 1.0 (1 = strong buy)
- **Revisions:** FY+1 EPS +1.6% (30d) / +2.4% (90d), 2 up / 0 down; current year +4.7% / +3.6%, 2 up / 0 down
- **Valuation:** fwd P/E 32.2, EV/EBITDA 52.1, FCF yield 0.9%, P/B 17.5
- **Quality:** ROIC 30%, operating margin 24%, Piotroski 5/7, FCF conversion 48%
- **Growth:** sales +33% and EPS +57% next year (consensus); 3-year sales CAGR +53%
- **Balance sheet:** net cash 3% of market cap
- **Momentum:** +24% (13w), -2% (52w), -6% from 52-week high; divergence flag: no
- **Rationale [Revisions↑ · Niche leader / supply-chain theme]:** +41% to the mean target of 6 analysts; next-year EPS forecast +2.4% over 90 days (2 up / 0 down in 30 days), consensus EPS growth +57% next year, 32.2× forward earnings, ROIC 30%. Theme: healthcare niche, automation / industrial tech.
- **Key risk:** weak cash conversion (48% FCF/NI); German secondary line: spreads may be wide

#### 43. NORDEX SE O.N. (NDX1.DE) — tier A, score 66

- **What it does:** Nordex SE, together with its subsidiaries, develops, manufactures, and distributes multi-megawatt onshore wind turbines in Europe, North America, Latin America, and internationally. It operates in Projects and Services segments.
- **Listing:** Germany, Xetra/Frankfurt (Prime Standard) · Specialty Industrial Machinery · market cap €9.3bn, €21m/day traded · ISIN DE000A0D6554
- **Fortuneo:** Xetra/Frankfurt
- **Consensus:** EUR 39.14 → EUR 50.52 mean (range EUR 36.00–EUR 63.00, 15 analysts), upside **+29%**; recommendation 1.7 (1 = strong buy)
- **Revisions:** FY+1 EPS +5.1% (30d) / +10.8% (90d), 2 up / 3 down; current year +5.7% / +8.4%, 3 up / 1 down
- **Valuation:** fwd P/E 14.9, EV/EBITDA 9.8, FCF yield 4.9%, P/B 6.4
- **Quality:** ROIC n/a, operating margin 9%, Piotroski 6/7, FCF conversion n/a
- **Growth:** sales +9% and EPS +21% next year (consensus); 3-year sales CAGR +10%
- **Balance sheet:** net cash 16% of market cap
- **Momentum:** -2% (13w), +69% (52w), -19% from 52-week high; divergence flag: no
- **Rationale [Revisions↑ · Hidden assets / net cash · Niche leader / supply-chain theme]:** +29% to the mean target of 15 analysts; next-year EPS forecast +10.8% over 90 days (2 up / 3 down in 30 days), consensus EPS growth +21% next year, 14.9× forward earnings. Theme: energy transition.
- **Key risk:** wide spread of analyst targets

#### 44. ARGENX SE (ARGX.BR) — tier A, score 66

- **What it does:** argenx SE, a commercial-stage biopharma company, develops various therapies for the treatment of autoimmune diseases in the United States, Japan, China, the Netherlands, and internationally. The company offers VYVGART for the treatment of gMG and immune thrombocytopenia (ITP), and VYVGART HYTRULO for the treatment of gMG and….
- **Listing:** Netherlands, Euronext Brussels · Biotechnology · market cap €45.8bn, €62m/day traded · ISIN NL0010832176
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 727.60 → EUR 1,008 mean (range EUR 773.95–EUR 1,175, 15 analysts), upside **+39%**; recommendation 1.5 (1 = strong buy)
- **Revisions:** FY+1 EPS +5.3% (30d) / +5.7% (90d), 1 up / 1 down; current year +0.0% / +9.6%, 0 up / 1 down
- **Valuation:** fwd P/E 19.4, EV/EBITDA 25.0, FCF yield 1.5%, P/B 6.1
- **Quality:** ROIC 25%, operating margin 32%, Piotroski 6/7, FCF conversion -2%
- **Growth:** sales +23% and EPS +26% next year (consensus); 3-year sales CAGR +116%
- **Balance sheet:** net cash 10% of market cap
- **Momentum:** -10% (13w), +2% (52w), -19% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Niche leader / supply-chain theme]:** +39% to the mean target of 15 analysts; next-year EPS forecast +5.7% over 90 days (1 up / 1 down in 30 days), consensus EPS growth +26% next year, 19.4× forward earnings, ROIC 25%. Theme: healthcare niche. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** weak cash conversion (-2% FCF/NI)

#### 48. BE SEMICONDUCTOR (BESI.AS) — tier A, score 65

- **What it does:** BE Semiconductor Industries N.V. develops, manufactures, markets, sells, and services semiconductor assembly equipment for the semiconductor and electronics industries in the Netherlands, Switzerland, Austria, Singapore, Malaysia, and internationally. It operates through three segments: Die Attach, Packaging, and Plating.
- **Listing:** Netherlands, Euronext Amsterdam · Semiconductor Equipment & Materials · market cap €12.3bn, €77m/day traded · ISIN NL0012866412
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 155.55 → EUR 270.57 mean (range EUR 159.00–EUR 400.00, 23 analysts), upside **+74%**; recommendation 2.0 (1 = strong buy)
- **Revisions:** FY+1 EPS -0.5% (30d) / +4.2% (90d), 1 up / 5 down; current year +0.9% / +7.3%, 4 up / 0 down
- **Valuation:** fwd P/E 23.7, EV/EBITDA 44.6, FCF yield 1.4%, P/B 21.9
- **Quality:** ROIC 24%, operating margin 44%, Piotroski 4/7, FCF conversion 99%
- **Growth:** sales +34% and EPS +48% next year (consensus); 3-year sales CAGR -6%
- **Balance sheet:** net cash 1% of market cap
- **Momentum:** -31% (13w), +10% (52w), -51% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Niche leader / supply-chain theme]:** +74% to the mean target of 23 analysts; next-year EPS forecast +4.2% over 90 days (1 up / 5 down in 30 days), consensus EPS growth +48% next year, 23.7× forward earnings, ROIC 24%. Theme: AI / data centres. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** estimate cuts; wide spread of analyst targets

#### 50. SMCP (SMCP.PA) — tier A, score 65

- **What it does:** SMCP S.A. operates as an apparel and accessories retail company in France and internationally. The company offers suits and coats, ready-to-wear products, bags, shoes and accessories; fluidity and structure, lace and embroidery, knitwear and leather; and clothing, as well as footwear, jewellery, scarves, belts, and other….
- **Listing:** France, Euronext Paris · Apparel Retail · market cap €449m, €552k/day traded · ISIN FR0013214145
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 5.75 → EUR 8.84 mean (range EUR 8.10–EUR 10.40, 5 analysts), upside **+54%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +0.0% (30d) / +4.2% (90d), 2 up / 0 down; current year +3.8% / +5.6%, 2 up / 0 down
- **Valuation:** fwd P/E 7.3, EV/EBITDA 7.1, FCF yield 33.4%, P/B 0.4
- **Quality:** ROIC 3%, operating margin 8%, Piotroski 7/7, FCF conversion 13548%
- **Growth:** sales +3% and EPS +16% next year (consensus); 3-year sales CAGR +0%
- **Balance sheet:** net debt 3.8× EBITDA
- **Momentum:** +10% (13w), -5% (52w), -18% from 52-week high; divergence flag: no
- **Rationale [Revisions↑ · Cheap vs sector · Hidden assets / net cash]:** +54% to the mean target of 5 analysts; next-year EPS forecast +4.2% over 90 days (2 up / 0 down in 30 days), consensus EPS growth +16% next year, 7.3× forward earnings, ROIC 3%.
- **Key risk:** high leverage (net debt 3.8× EBITDA)

#### 51. NEXANS (NEX.PA) — tier A, score 65

- **What it does:** Nexans S.A. manufactures and sells cables in France, Canada, Norway, Italy, and internationally. It operates through PWR-Grid & Connect, PWR-Transmission, and Other segments.
- **Listing:** France, Euronext Paris · Electrical Equipment & Parts · market cap €5.5bn, €20m/day traded · ISIN FR0000044448
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 126.70 → EUR 172.53 mean (range EUR 150.00–EUR 190.00, 15 analysts), upside **+36%**; recommendation 1.6 (1 = strong buy)
- **Revisions:** FY+1 EPS +1.3% (30d) / +1.2% (90d), 3 up / 0 down; current year +2.1% / -2.4%, 3 up / 0 down
- **Valuation:** fwd P/E 13.6, EV/EBITDA 8.9, FCF yield -0.1%, P/B 2.6
- **Quality:** ROIC 12%, operating margin 6%, Piotroski 7/7, FCF conversion 146%
- **Growth:** sales +9% and EPS +30% next year (consensus); 3-year sales CAGR -2%
- **Balance sheet:** net debt 1.4× EBITDA
- **Momentum:** -4% (13w), +5% (52w), -22% from 52-week high; divergence flag: no
- **Rationale [Revisions↑ · Niche leader / supply-chain theme]:** +36% to the mean target of 15 analysts; next-year EPS forecast +1.2% over 90 days (3 up / 0 down in 30 days), consensus EPS growth +30% next year, 13.6× forward earnings, ROIC 12%. Theme: energy transition.
- **Key risk:** nothing obvious in the data

#### 57. CENERGY (CENER.BR) — tier A, score 64

- **What it does:** Cenergy Holdings SA manufactures and sells aluminium, copper, cables, steel and steel pipes, and other related products in Belgium, Greece, Germany, Romania, Other European Union countries, Other European countries, the United States, Asia, Africa, and internationally. It operates through two segments: Cables and Steel Pipes.
- **Listing:** Belgium, Euronext Brussels · Electrical Equipment & Parts · market cap €4.6bn, €282k/day traded · ISIN BE0974303357
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 21.80 → EUR 27.60 mean (range EUR 25.30–EUR 29.00, 3 analysts), upside **+27%**; recommendation 1.0 (1 = strong buy)
- **Revisions:** FY+1 EPS +4.7% (30d) / +11.7% (90d), 1 up / 0 down; current year +4.2% / +14.8%, 1 up / 0 down
- **Valuation:** fwd P/E 16.3, EV/EBITDA 13.1, FCF yield -1.6%, P/B 4.9
- **Quality:** ROIC 21%, operating margin 17%, Piotroski 7/7, FCF conversion 27%
- **Growth:** sales +12% and EPS +8% next year (consensus); 3-year sales CAGR +13%
- **Balance sheet:** net debt 1.1× EBITDA
- **Momentum:** +4% (13w), +67% (52w), -16% from 52-week high; divergence flag: no
- **Rationale [Revisions↑ · Niche leader / supply-chain theme]:** +27% to the mean target of 3 analysts; next-year EPS forecast +11.7% over 90 days (1 up / 0 down in 30 days), consensus EPS growth +8% next year, 16.3× forward earnings, ROIC 21%. Theme: energy transition.
- **Key risk:** weak cash conversion (27% FCF/NI)

#### 59. LAGARDERE SA (MMB.PA) — tier A, score 63

- **What it does:** Lagardere SA engages in content publishing, production, and broadcasting of media, entertainment, and the distribution of products and services in France, the United Kingdom, the United States, Canada, Spain, Latin America, and internationally. It operates through three segments: Lagardère Publishing, Lagardère Travel….
- **Listing:** France, Euronext Paris · Specialty Retail · market cap €2.6bn, €233k/day traded · ISIN FR0000130213
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 18.34 → EUR 27.17 mean (range EUR 23.50–EUR 34.50, 3 analysts), upside **+48%**; recommendation 2.3 (1 = strong buy)
- **Revisions:** FY+1 EPS +2.3% (30d) / +2.3% (90d), 1 up / 0 down; current year +3.5% / +3.5%, 1 up / 0 down
- **Valuation:** fwd P/E 7.7, EV/EBITDA 7.6, FCF yield 34.9%, P/B 3.0
- **Quality:** ROIC 8%, operating margin 5%, Piotroski 5/7, FCF conversion 540%
- **Growth:** sales +3% and EPS +6% next year (consensus); 3-year sales CAGR +11%
- **Balance sheet:** net debt 4.8× EBITDA
- **Momentum:** +3% (13w), -1% (52w), -8% from 52-week high; divergence flag: no
- **Rationale [Revisions↑ · Cheap vs sector]:** +48% to the mean target of 3 analysts; next-year EPS forecast +2.3% over 90 days (1 up / 0 down in 30 days), consensus EPS growth +6% next year, 7.7× forward earnings, ROIC 8%.
- **Key risk:** high leverage (net debt 4.8× EBITDA)

### Tier B

#### 9. Obrascón Huarte Lain, S.A. (OHLA.MC) — tier B, score 72

- **What it does:** Obrascón Huarte Lain, S.A. operates as an infrastructure company primarily in the United States, Europe, and Latin America. The company operates through Construction, Industrial, and Other segments.
- **Listing:** Spain, MCE · Engineering & Construction · market cap €461m, €2.6m/day traded · ISIN n/a
- **Fortuneo:** German secondary line (check liquidity)
- **Consensus:** EUR 0.33 → EUR 0.63 mean (range EUR 0.58–EUR 0.70, 3 analysts), upside **+88%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS n/a (30d) / n/a (90d), 0 up / 0 down; current year n/a / n/a, 0 up / 0 down
- **Valuation:** fwd P/E 33.4, EV/EBITDA 2.3, FCF yield 19.6%, P/B 0.7
- **Quality:** ROIC 20%, operating margin 3%, Piotroski 6/7, FCF conversion n/a
- **Growth:** sales +6% and EPS n/a next year (consensus); 3-year sales CAGR +6%
- **Balance sheet:** net cash 13% of market cap
- **Momentum:** -24% (13w), -30% (52w), -33% from 52-week high; divergence flag: no
- **Rationale [Cheap vs sector · Hidden assets / net cash · Niche leader / supply-chain theme]:** +88% to the mean target of 3 analysts; 33.4× forward earnings, ROIC 20%. Theme: energy transition.
- **Key risk:** German secondary line: spreads may be wide

#### 14. SUSS MicroTec SE (SMHN.DE) — tier B, score 70

- **What it does:** SUSS MicroTec SE, together with its subsidiaries, develops, manufactures, markets, and maintains systems to produce microelectronics, microelectromechanical systems, and related applications. It operates in two divisions, Advanced Backend Solutions and Photomask Solutions.
- **Listing:** Germany, Xetra/Frankfurt (Prime Standard) · Semiconductor Equipment & Materials · market cap €1.1bn, €5.3m/day traded · ISIN DE000A1K0235
- **Fortuneo:** Xetra/Frankfurt
- **Consensus:** EUR 56.35 → EUR 110.44 mean (range EUR 100.00–EUR 125.00, 8 analysts), upside **+96%**; recommendation 1.1 (1 = strong buy)
- **Revisions:** FY+1 EPS -0.3% (30d) / +8.3% (90d), 0 up / 2 down; current year -5.4% / -15.8%, 0 up / 4 down
- **Valuation:** fwd P/E 14.6, EV/EBITDA 24.4, FCF yield 2.1%, P/B 3.3
- **Quality:** ROIC 19%, operating margin 9%, Piotroski n/a/7, FCF conversion n/a
- **Growth:** sales +38% and EPS +131% next year (consensus); 3-year sales CAGR +25%
- **Balance sheet:** net cash 6% of market cap
- **Momentum:** -29% (13w), +61% (52w), -50% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Niche leader / supply-chain theme]:** +96% to the mean target of 8 analysts; next-year EPS forecast +8.3% over 90 days (0 up / 2 down in 30 days), consensus EPS growth +131% next year, 14.6× forward earnings, ROIC 19%. Theme: AI / data centres. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** estimate cuts

#### 15. ZEAL NETWORK SE NA O.N. (TIMA.DE) — tier B, score 70

- **What it does:** ZEAL Network SE engages in the online lottery brokerage business in Germany. The company operates through three segments: Germany, ONCE, and ZEAL Ventures.
- **Listing:** Germany, Xetra/Frankfurt (Prime Standard) · Gambling · market cap €846m, €107k/day traded · ISIN DE000ZEAL241
- **Fortuneo:** Xetra/Frankfurt
- **Consensus:** EUR 40.10 → EUR 75.00 mean (range EUR 70.00–EUR 83.00, 5 analysts), upside **+87%**; recommendation 1.2 (1 = strong buy)
- **Revisions:** FY+1 EPS +0.0% (30d) / +3.1% (90d), 4 up / 1 down; current year +0.0% / -0.6%, 1 up / 3 down
- **Valuation:** fwd P/E 16.2, EV/EBITDA 11.6, FCF yield 7.8%, P/B 3.8
- **Quality:** ROIC 23%, operating margin 31%, Piotroski 5/7, FCF conversion 142%
- **Growth:** sales +16% and EPS +30% next year (consensus); 3-year sales CAGR +28%
- **Balance sheet:** net cash 2% of market cap
- **Momentum:** -9% (13w), -18% (52w), -23% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down]:** +87% to the mean target of 5 analysts; next-year EPS forecast +3.1% over 90 days (4 up / 1 down in 30 days), consensus EPS growth +30% next year, 16.2× forward earnings, ROIC 23%. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** nothing obvious in the data

#### 20. Exsitec Holding AB (publ) (EXS.ST) — tier B, score 68

- **What it does:** Exsitec Holding AB (publ) provides digital solutions to medium-sized companies in Sweden, Norway, Denmark, and Finland. It offers ERP systems; AP automation; cloud-based payroll system; budget and forecasting; analytics and reporting; CRM system; procurement; warehouse management; service, construction, and contracting….
- **Listing:** Sweden, Stockholm · Information Technology Services · market cap €132m, €210k/day traded · ISIN n/a
- **Fortuneo:** **Not online** (sale by phone only)
- **Consensus:** SEK 109.50 → SEK 164.50 mean (range SEK 164.00–SEK 165.00, 2 analysts), upside **+50%**; recommendation 1.5 (1 = strong buy)
- **Revisions:** FY+1 EPS +0.2% (30d) / +0.2% (90d), 1 up / 0 down; current year -2.4% / -2.4%, 0 up / 1 down
- **Valuation:** fwd P/E 11.8, EV/EBITDA 11.7, FCF yield 9.3%, P/B 2.7
- **Quality:** ROIC 12%, operating margin 11%, Piotroski 7/7, FCF conversion 138%
- **Growth:** sales +17% and EPS +39% next year (consensus); 3-year sales CAGR +11%
- **Balance sheet:** net debt 2.5× EBITDA
- **Momentum:** +4% (13w), -20% (52w), -32% from 52-week high; divergence flag: no
- **Rationale [Cheap vs sector · Niche leader / supply-chain theme]:** +50% to the mean target of 2 analysts; next-year EPS forecast +0.2% over 90 days (1 up / 0 down in 30 days), consensus EPS growth +39% next year, 11.8× forward earnings, ROIC 12%. Theme: automation / industrial tech.
- **Key risk:** only 2 analysts; not buyable online at Fortuneo

#### 21. VEF AB (publ) (VEFAB.ST) — tier B, score 68

- **What it does:** VEF AB (publ) is a venture capital firm specializing in early venture, emerging growth and growth capital investments. The firm primarily invests in modern financial services and fintech sector.
- **Listing:** Sweden, Stockholm · Asset Management · market cap €182m, €170k/day traded · ISIN n/a
- **Fortuneo:** German secondary line (check liquidity)
- **Consensus:** SEK 1.99 → SEK 3.01 mean (range SEK 2.80–SEK 3.33, 4 analysts), upside **+51%**; recommendation 1.3 (1 = strong buy)
- **Revisions:** FY+1 EPS n/a (30d) / n/a (90d), 0 up / 0 down; current year n/a / n/a, 0 up / 0 down
- **Valuation:** fwd P/E -9.5, EV/EBITDA 59.4, FCF yield 9.4%, P/B 5.0
- **Quality:** ROIC 16%, operating margin 980%, Piotroski 4/7, FCF conversion 82%
- **Growth:** sales +100% and EPS n/a next year (consensus); 3-year sales CAGR n/a
- **Balance sheet:** net debt 0.5× EBITDA
- **Momentum:** +15% (13w), -12% (52w), -14% from 52-week high; divergence flag: no
- **Rationale [Upside to consensus]:** +51% to the mean target of 4 analysts; -9.5× forward earnings, ROIC 16%.
- **Key risk:** German secondary line: spreads may be wide

#### 23. FABASOFT AG (FAA.DE) — tier B, score 68

- **What it does:** Fabasoft AG, together with its subsidiaries, provides software products and cloud services for digital document, process, and file management in Austria, Germany, Switzerland, and internationally. The company offers Fabasphere, a cloud-based hub for documents and processes; and Fabasoft Cloud that provides content management….
- **Listing:** Austria, Xetra/Frankfurt (Prime Standard) · Software - Application · market cap €170m, €137k/day traded · ISIN AT0000785407
- **Fortuneo:** Xetra/Frankfurt
- **Consensus:** EUR 16.15 → EUR 25.50 mean (range EUR 24.00–EUR 27.00, 2 analysts), upside **+58%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +0.0% (30d) / +0.5% (90d), 1 up / 0 down; current year +1.1% / +0.0%, 0 up / 1 down
- **Valuation:** fwd P/E 15.2, EV/EBITDA 6.3, FCF yield 8.0%, P/B 3.9
- **Quality:** ROIC 172%, operating margin 21%, Piotroski 5/7, FCF conversion 98%
- **Growth:** sales +10% and EPS +16% next year (consensus); 3-year sales CAGR +9%
- **Balance sheet:** net cash 13% of market cap
- **Momentum:** +21% (13w), +3% (52w), -6% from 52-week high; divergence flag: no
- **Rationale [Cheap vs sector · Niche leader / supply-chain theme]:** +58% to the mean target of 2 analysts; next-year EPS forecast +0.5% over 90 days (1 up / 0 down in 30 days), consensus EPS growth +16% next year, 15.2× forward earnings, ROIC 172%. Theme: AI / data centres.
- **Key risk:** only 2 analysts

#### 26. Truecaller AB (publ) (TRUE-B.ST) — tier B, score 68

- **What it does:** Truecaller AB (publ), together with its subsidiaries, develops and publishes mobile caller ID applications for individuals and business in India, the Middle East, Africa, and internationally. The company operates a platform for verifying contacts and blocking unwanted communication under the Truecaller brand.
- **Listing:** Sweden, Stockholm · Software - Application · market cap €665m, €4.3m/day traded · ISIN n/a
- **Fortuneo:** German secondary line (check liquidity)
- **Consensus:** SEK 24.38 → SEK 37.17 mean (range SEK 20.00–SEK 68.00, 6 analysts), upside **+52%**; recommendation 1.8 (1 = strong buy)
- **Revisions:** FY+1 EPS +1.0% (30d) / +0.1% (90d), 1 up / 0 down; current year +3.1% / -4.9%, 0 up / 0 down
- **Valuation:** fwd P/E 16.9, EV/EBITDA 15.5, FCF yield 4.2%, P/B 7.3
- **Quality:** ROIC 44%, operating margin 24%, Piotroski 5/7, FCF conversion 112%
- **Growth:** sales +20% and EPS +42% next year (consensus); 3-year sales CAGR +3%
- **Balance sheet:** net cash 11% of market cap
- **Momentum:** +51% (13w), -37% (52w), -37% from 52-week high; divergence flag: no
- **Rationale [Niche leader / supply-chain theme]:** +52% to the mean target of 6 analysts; next-year EPS forecast +0.1% over 90 days (1 up / 0 down in 30 days), consensus EPS growth +42% next year, 16.9× forward earnings, ROIC 44%.
- **Key risk:** wide spread of analyst targets; German secondary line: spreads may be wide

#### 28. AMG (AMG.AS) — tier B, score 67

- **What it does:** AMG Critical Materials N.V., together with its subsidiaries, develops, produces, and sells energy storage materials in the United States, China, Germany, France, Japan, Brazil, Africa, and internationally. It operates through three segments: AMG Lithium, AMG Vanadium, and AMG Technologies.
- **Listing:** Netherlands, Euronext Amsterdam · Other Industrial Metals & Mining · market cap €920m, €5.3m/day traded · ISIN NL0000888691
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 25.84 → EUR 46.26 mean (range EUR 40.96–EUR 49.68, 6 analysts), upside **+79%**; recommendation 1.0 (1 = strong buy)
- **Revisions:** FY+1 EPS +7.1% (30d) / +23.8% (90d), 2 up / 0 down; current year +3.9% / -4.7%, 1 up / 0 down
- **Valuation:** fwd P/E 7.6, EV/EBITDA 5.1, FCF yield 0.4%, P/B 1.4
- **Quality:** ROIC 7%, operating margin 12%, Piotroski 6/7, FCF conversion -12%
- **Growth:** sales +7% and EPS +73% next year (consensus); 3-year sales CAGR +1%
- **Balance sheet:** net debt 1.8× EBITDA
- **Momentum:** -3% (13w), -17% (52w), -39% from 52-week high; divergence flag: no
- **Rationale [Revisions↑ · Cheap vs sector · Niche leader / supply-chain theme]:** +79% to the mean target of 6 analysts; next-year EPS forecast +23.8% over 90 days (2 up / 0 down in 30 days), consensus EPS growth +73% next year, 7.6× forward earnings, ROIC 7%. Theme: chemicals / materials, energy transition.
- **Key risk:** weak cash conversion (-12% FCF/NI)

#### 33. VIRIDIEN (VIRI.PA) — tier B, score 67

- **What it does:** Viridien Société anonyme provides earth science, data science, sensing, and monitoring data, products, services, and solutions in North America, Latin America, the Central and South Americas, Europe, Africa, the Middle East, and the Asia Pacific. It operates through two segments, Data, Digital & Energy Transition (DDE); and….
- **Listing:** France, Euronext Paris · Oil & Gas Equipment & Services · market cap €635m, €3.0m/day traded · ISIN FR001400PVN6
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 87.90 → EUR 140.48 mean (range EUR 102.32–EUR 200.41, 6 analysts), upside **+60%**; recommendation 1.5 (1 = strong buy)
- **Revisions:** FY+1 EPS +0.0% (30d) / +2.7% (90d), 0 up / 0 down; current year -17.3% / -22.6%, 0 up / 0 down
- **Valuation:** fwd P/E 6.1, EV/EBITDA 3.0, FCF yield 31.2%, P/B 0.6
- **Quality:** ROIC 7%, operating margin 1%, Piotroski 6/7, FCF conversion 461%
- **Growth:** sales +11% and EPS +129% next year (consensus); 3-year sales CAGR +5%
- **Balance sheet:** net debt 1.7× EBITDA
- **Momentum:** +5% (13w), +27% (52w), -43% from 52-week high; divergence flag: no
- **Rationale [Cheap vs sector · Hidden assets / net cash]:** +60% to the mean target of 6 analysts; next-year EPS forecast +2.7% over 90 days (0 up / 0 down in 30 days), consensus EPS growth +129% next year, 6.1× forward earnings, ROIC 7%.
- **Key risk:** wide spread of analyst targets

#### 35. Cheffelo AB (publ) (CHEF.ST) — tier B, score 67

- **What it does:** Cheffelo AB (publ) provides subscription-based meal kit solutions to various customers in Sweden, Norway, and Denmark. The company operates under the Linas Matkasse, Godtlevert, Adams Matkasse, and RetNemt brand names.
- **Listing:** Sweden, Stockholm · Food Distribution · market cap €117m, €508k/day traded · ISIN n/a
- **Fortuneo:** **Not online** (sale by phone only)
- **Consensus:** SEK 100.00 → SEK 150.67 mean (range SEK 145.00–SEK 157.00, 3 analysts), upside **+51%**; recommendation 1.5 (1 = strong buy)
- **Revisions:** FY+1 EPS -0.3% (30d) / +10.7% (90d), 0 up / 1 down; current year -0.3% / +9.5%, 0 up / 1 down
- **Valuation:** fwd P/E 11.8, EV/EBITDA 9.7, FCF yield 9.5%, P/B 3.0
- **Quality:** ROIC 16%, operating margin 13%, Piotroski 7/7, FCF conversion 236%
- **Growth:** sales +10% and EPS +19% next year (consensus); 3-year sales CAGR +3%
- **Balance sheet:** net cash 5% of market cap
- **Momentum:** -20% (13w), +25% (52w), -24% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down]:** +51% to the mean target of 3 analysts; next-year EPS forecast +10.7% over 90 days (0 up / 1 down in 30 days), consensus EPS growth +19% next year, 11.8× forward earnings, ROIC 16%. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** estimate cuts; not buyable online at Fortuneo

#### 45. WESTWING GROUP  INH. O.N. (WEW.DE) — tier B, score 66

- **What it does:** Westwing Group SE operates as an e-commerce retailer in the home and living sector. It operates in two segments, DACH and International.
- **Listing:** Germany, Xetra/Frankfurt (Prime Standard) · Furnishings, Fixtures & Appliances · market cap €250m, €330k/day traded · ISIN DE000A2N4H07
- **Fortuneo:** Xetra/Frankfurt
- **Consensus:** EUR 13.25 → EUR 22.17 mean (range EUR 19.00–EUR 24.00, 3 analysts), upside **+67%**; recommendation 1.0 (1 = strong buy)
- **Revisions:** FY+1 EPS +0.0% (30d) / +0.9% (90d), 1 up / 1 down; current year +0.0% / -0.6%, 1 up / 1 down
- **Valuation:** fwd P/E 8.9, EV/EBITDA 11.2, FCF yield 17.8%, P/B 3.1
- **Quality:** ROIC 53%, operating margin -1%, Piotroski 6/7, FCF conversion 554%
- **Growth:** sales +7% and EPS +28% next year (consensus); 3-year sales CAGR +1%
- **Balance sheet:** net cash 15% of market cap
- **Momentum:** -13% (13w), +16% (52w), -26% from 52-week high; divergence flag: no
- **Rationale [Cheap vs sector]:** +67% to the mean target of 3 analysts; next-year EPS forecast +0.9% over 90 days (1 up / 1 down in 30 days), consensus EPS growth +28% next year, 8.9× forward earnings, ROIC 53%.
- **Key risk:** loss-making at operating level

#### 46. AIXTRON SE NA O.N. (AIXA.DE) — tier B, score 66

- **What it does:** AIXTRON SE, together with its subsidiaries, manufactures and sells deposition equipment to the semiconductor industry in Asia, Europe, and the United States. The company offers G10-SiC, G10-GaN, G10-AsP, AIX G5+ C, Closed Coupled Showerhead systems for research and development, AIX 2800G4-TM, and AIX G5 WW C. It also….
- **Listing:** Germany, Xetra/Frankfurt (Prime Standard) · Semiconductor Equipment & Materials · market cap €3.7bn, €22m/day traded · ISIN DE000A0WMPJ6
- **Fortuneo:** Xetra/Frankfurt
- **Consensus:** EUR 32.89 → EUR 48.21 mean (range EUR 40.00–EUR 74.00, 15 analysts), upside **+47%**; recommendation 2.1 (1 = strong buy)
- **Revisions:** FY+1 EPS +1.3% (30d) / +5.8% (90d), 2 up / 2 down; current year -0.8% / +0.3%, 1 up / 3 down
- **Valuation:** fwd P/E 23.9, EV/EBITDA 37.7, FCF yield 6.9%, P/B 3.7
- **Quality:** ROIC 9%, operating margin 13%, Piotroski 4/7, FCF conversion -1%
- **Growth:** sales +42% and EPS +88% next year (consensus); 3-year sales CAGR +6%
- **Balance sheet:** net cash 13% of market cap
- **Momentum:** -18% (13w), +153% (52w), -45% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Niche leader / supply-chain theme]:** +47% to the mean target of 15 analysts; next-year EPS forecast +5.8% over 90 days (2 up / 2 down in 30 days), consensus EPS growth +88% next year, 23.9× forward earnings, ROIC 9%. Theme: AI / data centres. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** weak cash conversion (-1% FCF/NI); wide spread of analyst targets

#### 49. TECHNOTRANS SE NA O.N. (TTR1.DE) — tier B, score 65

- **What it does:** technotrans SE operates as a technology and services company in Germany, Europe, America, Asia, and internationally. It develops and produces cooling and temperature control systems, as well as systems for pumping, spraying, filtering, and separating liquids.
- **Listing:** Germany, Xetra/Frankfurt (Prime Standard) · Specialty Industrial Machinery · market cap €184m, €170k/day traded · ISIN DE000A0XYGA7
- **Fortuneo:** Xetra/Frankfurt
- **Consensus:** EUR 26.70 → EUR 39.50 mean (range EUR 38.00–EUR 41.00, 2 analysts), upside **+48%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +0.9% (30d) / +0.9% (90d), 1 up / 1 down; current year -1.4% / -1.4%, 0 up / 1 down
- **Valuation:** fwd P/E 11.7, EV/EBITDA 9.6, FCF yield 8.8%, P/B 1.7
- **Quality:** ROIC 13%, operating margin 7%, Piotroski 7/7, FCF conversion 138%
- **Growth:** sales +10% and EPS +28% next year (consensus); 3-year sales CAGR +1%
- **Balance sheet:** net debt 0.6× EBITDA
- **Momentum:** -8% (13w), -21% (52w), -25% from 52-week high; divergence flag: no
- **Rationale [Cheap vs sector · Niche leader / supply-chain theme]:** +48% to the mean target of 2 analysts; next-year EPS forecast +0.9% over 90 days (1 up / 1 down in 30 days), consensus EPS growth +28% next year, 11.7× forward earnings, ROIC 13%.
- **Key risk:** only 2 analysts

#### 52. FLATEXDEGIRO SE (FTK.DE) — tier B, score 65

- **What it does:** flatexDEGIRO SE, together with its subsidiaries, provides online brokerage and IT solutions for banking and securities in Europe. The company operates through two segments, flatex and DEGIRO. The company offers online brokerage services, including execution-only securities transactions under the flatex brand; funds, saving….
- **Listing:** Germany, Xetra/Frankfurt (Prime Standard) · Capital Markets · market cap €2.7bn, €9.0m/day traded · ISIN DE000FTG1111
- **Fortuneo:** Xetra/Frankfurt
- **Consensus:** EUR 25.48 → EUR 43.33 mean (range EUR 31.00–EUR 50.00, 12 analysts), upside **+70%**; recommendation 2.0 (1 = strong buy)
- **Revisions:** FY+1 EPS -1.0% (30d) / +3.6% (90d), 0 up / 4 down; current year -1.4% / +1.9%, 0 up / 4 down
- **Valuation:** fwd P/E 10.6, EV/EBITDA n/a, FCF yield n/a, P/B 2.8
- **Quality:** ROIC n/a, operating margin 56%, Piotroski 6/7, FCF conversion 86%
- **Growth:** sales +9% and EPS +15% next year (consensus); 3-year sales CAGR +16%
- **Balance sheet:** net cash 156% of market cap
- **Momentum:** -31% (13w), -20% (52w), -38% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Cheap vs sector · Hidden assets / net cash]:** +70% to the mean target of 12 analysts; next-year EPS forecast +3.6% over 90 days (0 up / 4 down in 30 days), consensus EPS growth +15% next year, 10.6× forward earnings. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** estimate cuts

#### 53. DEUTSCHE ROHSTOFF AG NA O.N. (DR0.DE) — tier B, score 64

- **What it does:** Deutsche Rohstoff AG, together with its subsidiaries, engages in the exploration and production of crude oil and natural gas. It also explores and develops gold, lithium, and tungsten mining projects.
- **Listing:** Germany, Xetra/Frankfurt (Scale) · Oil & Gas E&P · market cap €396m, €1.0m/day traded · ISIN DE000A0XYG76
- **Fortuneo:** Xetra/Frankfurt
- **Consensus:** EUR 83.50 → EUR 126.50 mean (range EUR 125.00–EUR 128.00, 2 analysts), upside **+52%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +19.2% (30d) / +17.4% (90d), 2 up / 0 down; current year +9.5% / +25.7%, 1 up / 1 down
- **Valuation:** fwd P/E 5.0, EV/EBITDA 2.1, FCF yield -7.0%, P/B 1.2
- **Quality:** ROIC 10%, operating margin 216%, Piotroski 3/7, FCF conversion -57%
- **Growth:** sales +3% and EPS -66% next year (consensus); 3-year sales CAGR +6%
- **Balance sheet:** net debt 0.4× EBITDA
- **Momentum:** -0% (13w), +70% (52w), -24% from 52-week high; divergence flag: no
- **Rationale [Revisions↑ · Cheap vs sector]:** +52% to the mean target of 2 analysts; next-year EPS forecast +17.4% over 90 days (2 up / 0 down in 30 days), consensus EPS growth -66% next year, 5.0× forward earnings, ROIC 10%. Theme: chemicals / materials.
- **Key risk:** only 2 analysts; weak cash conversion (-57% FCF/NI)

#### 58. SEMCO TECHNOLOGIES (ALSEM.PA) — tier B, score 64

- **What it does:** SEMCO Technologies Société anonyme designs, manufactures, and markets components for the manufacturing of semiconductor devices in France, Asia, the Americas, and Europe. The company offers electrostatic chucks offer smart solutions for the clamping and processing of various types of wafers; and design and manufacture of….
- **Listing:** France, Euronext Growth Paris · Semiconductor Equipment & Materials · market cap €408m, €718k/day traded · ISIN FR0014010H01
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 39.60 → EUR 57.40 mean (range EUR 48.00–EUR 68.00, 5 analysts), upside **+45%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +0.9% (30d) / +0.7% (90d), 0 up / 2 down; current year +2.4% / +2.4%, 1 up / 1 down
- **Valuation:** fwd P/E 24.5, EV/EBITDA 24.5, FCF yield n/a, P/B 17.4
- **Quality:** ROIC 64%, operating margin 38%, Piotroski 6/7, FCF conversion 83%
- **Growth:** sales +25% and EPS +28% next year (consensus); 3-year sales CAGR n/a
- **Balance sheet:** net cash 2% of market cap
- **Momentum:** -7% (13w), +51% (52w), -28% from 52-week high; divergence flag: no
- **Rationale [Niche leader / supply-chain theme]:** +45% to the mean target of 5 analysts; next-year EPS forecast +0.7% over 90 days (0 up / 2 down in 30 days), consensus EPS growth +28% next year, 24.5× forward earnings, ROIC 64%. Theme: AI / data centres.
- **Key risk:** nothing obvious in the data

#### 60. VALLOUREC (VK.PA) — tier B, score 63

- **What it does:** Vallourec S.A., through its subsidiaries, provides tubular solutions for the oil and gas, industry, and new energies markets in North America, South America, France, the Middle East, Indonesia, and East Asia. It operates through Tubes and Mine & Forests segments.
- **Listing:** France, Euronext Paris · Steel · market cap €5.1bn, €18m/day traded · ISIN FR0013506730
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 18.98 → EUR 26.14 mean (range EUR 21.50–EUR 28.00, 11 analysts), upside **+38%**; recommendation 1.4 (1 = strong buy)
- **Revisions:** FY+1 EPS -0.9% (30d) / -7.3% (90d), 1 up / 1 down; current year +0.9% / -19.6%, 1 up / 0 down
- **Valuation:** fwd P/E 9.8, EV/EBITDA 4.9, FCF yield 10.0%, P/B 1.7
- **Quality:** ROIC 21%, operating margin 14%, Piotroski 6/7, FCF conversion 91%
- **Growth:** sales +17% and EPS +55% next year (consensus); 3-year sales CAGR -8%
- **Balance sheet:** net cash 3% of market cap
- **Momentum:** -14% (13w), +25% (52w), -29% from 52-week high; divergence flag: no
- **Rationale [Cheap vs sector]:** +38% to the mean target of 11 analysts; next-year EPS forecast -7.3% over 90 days (1 up / 1 down in 30 days), consensus EPS growth +55% next year, 9.8× forward earnings, ROIC 21%. Theme: chemicals / materials.
- **Key risk:** estimate cuts

### Tier C

#### 3. Eolus Aktiebolag (publ) (EOLU-B.ST) — tier C, score 75

- **What it does:** Eolus Aktiebolag (publ) primarily engages in the development, construction, and operation of renewable energy assets in the Nordics region, the Baltics states, Poland, Spain, and the United States. It operates through Project Development and Asset Management segments.
- **Listing:** Sweden, Stockholm · Utilities - Renewable · market cap €105m, €185k/day traded · ISIN n/a
- **Fortuneo:** **Not online** (sale by phone only)
- **Consensus:** SEK 47.25 → SEK 87.55 mean (range SEK 80.00–SEK 95.10, 2 analysts), upside **+85%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +20.6% (30d) / +116.6% (90d), 2 up / 0 down; current year +83.3% / +17.6%, 2 up / 0 down
- **Valuation:** fwd P/E 3.4, EV/EBITDA -4.5, FCF yield 92.2%, P/B 0.9
- **Quality:** ROIC -22%, operating margin -550%, Piotroski 4/7, FCF conversion -45%
- **Growth:** sales +11% and EPS +34% next year (consensus); 3-year sales CAGR +18%
- **Balance sheet:** net cash 18% of market cap
- **Momentum:** +29% (13w), +13% (52w), -9% from 52-week high; divergence flag: no
- **Rationale [Revisions↑ · Cheap vs sector · Hidden assets / net cash]:** +85% to the mean target of 2 analysts; next-year EPS forecast +116.6% over 90 days (2 up / 0 down in 30 days), consensus EPS growth +34% next year, 3.4× forward earnings, ROIC -22%. Theme: energy transition.
- **Key risk:** only 2 analysts; weak cash conversion (-45% FCF/NI); loss-making at operating level; not buyable online at Fortuneo

#### 22. Paxman AB (publ) (PAX.ST) — tier C, score 68

- **What it does:** Paxman AB (publ), together with its subsidiaries, provides cryotherapy solutions in the United Kingdom, Europe, North and South America, Oceania, and Asia. The company offers Paxman scalp cooling system, a mechanized form of scalp cooling for the prevention of chemotherapy-induced alopecia.
- **Listing:** Sweden, Stockholm · Medical Devices · market cap €132m, €151k/day traded · ISIN n/a
- **Fortuneo:** **Not online** (sale by phone only)
- **Consensus:** SEK 63.30 → SEK 95.75 mean (range SEK 88.50–SEK 103.00, 2 analysts), upside **+51%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +11.1% (30d) / +11.1% (90d), 1 up / 0 down; current year +3.2% / +3.2%, 1 up / 0 down
- **Valuation:** fwd P/E 13.8, EV/EBITDA 36.8, FCF yield -2.1%, P/B 3.5
- **Quality:** ROIC 1%, operating margin 4%, Piotroski 3/7, FCF conversion -33%
- **Growth:** sales +27% and EPS +139% next year (consensus); 3-year sales CAGR +29%
- **Balance sheet:** net cash 6% of market cap
- **Momentum:** +35% (13w), -7% (52w), -7% from 52-week high; divergence flag: no
- **Rationale [Revisions↑ · Niche leader / supply-chain theme]:** +51% to the mean target of 2 analysts; next-year EPS forecast +11.1% over 90 days (1 up / 0 down in 30 days), consensus EPS growth +139% next year, 13.8× forward earnings, ROIC 1%. Theme: healthcare niche.
- **Key risk:** only 2 analysts; weak cash conversion (-33% FCF/NI); not buyable online at Fortuneo

#### 29. AT & S Austria Technologie & Systemtechnik Aktiengesellschaft (ATS.VI) — tier C, score 67

- **What it does:** AT & S Austria Technologie & Systemtechnik Aktiengesellschaft, together with its subsidiaries, manufactures, distributes, and sells printed circuit boards in Austria, Germany, rest of Europe, China, rest of Asia, and the Americas. The company operates through Electronics Solutions, Microelectronics, and Others segments.
- **Listing:** Austria, Vienna · Electronic Components · market cap €6.8bn, €23m/day traded · ISIN n/a
- **Fortuneo:** German secondary line (check liquidity)
- **Consensus:** EUR 174.20 → EUR 284.20 mean (range EUR 100.00–EUR 600.00, 5 analysts), upside **+63%**; recommendation 2.4 (1 = strong buy)
- **Revisions:** FY+1 EPS +38.0% (30d) / +75.8% (90d), 2 up / 0 down; current year +7.4% / n/a, 1 up / 0 down
- **Valuation:** fwd P/E 14.8, EV/EBITDA 15.4, FCF yield 1.6%, P/B 8.8
- **Quality:** ROIC 2%, operating margin 13%, Piotroski 3/7, FCF conversion -1684%
- **Growth:** sales +22% and EPS +36% next year (consensus); 3-year sales CAGR -0%
- **Balance sheet:** net debt 1.9× EBITDA
- **Momentum:** +10% (13w), +517% (52w), -23% from 52-week high; divergence flag: no
- **Rationale [Revisions↑]:** +63% to the mean target of 5 analysts; next-year EPS forecast +75.8% over 90 days (2 up / 0 down in 30 days), consensus EPS growth +36% next year, 14.8× forward earnings, ROIC 2%.
- **Key risk:** weak cash conversion (-1684% FCF/NI); wide spread of analyst targets; German secondary line: spreads may be wide

#### 30. WAVESTONE (WAVE.PA) — tier C, score 67

- **What it does:** Wavestone SA provides consulting services in France and internationally. The company offers tech driven solutions, such as artificial intelligence and data, cybersecurity, industry 5.0 and IoT, information technology strategy and CTO advisory, SAP consulting, software and application development and integration solutions;….
- **Listing:** France, Euronext Paris · Information Technology Services · market cap €739m, €977k/day traded · ISIN FR0013357621
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 30.10 → EUR 44.10 mean (range EUR 33.00–EUR 54.00, 4 analysts), upside **+47%**; recommendation 2.0 (1 = strong buy)
- **Revisions:** FY+1 EPS +3.9% (30d) / -2.8% (90d), 0 up / 1 down; current year -4.7% / -9.4%, 0 up / 1 down
- **Valuation:** fwd P/E 7.5, EV/EBITDA 4.9, FCF yield 16.9%, P/B 1.1
- **Quality:** ROIC 14%, operating margin 15%, Piotroski 6/7, FCF conversion 136%
- **Growth:** sales +4% and EPS +16% next year (consensus); 3-year sales CAGR +21%
- **Balance sheet:** net cash 14% of market cap
- **Momentum:** -23% (13w), -37% (52w), -51% from 52-week high; divergence flag: no
- **Rationale [Cheap vs sector · Niche leader / supply-chain theme]:** +47% to the mean target of 4 analysts; next-year EPS forecast -2.8% over 90 days (0 up / 1 down in 30 days), consensus EPS growth +16% next year, 7.5× forward earnings, ROIC 14%. Theme: AI / data centres.
- **Key risk:** nothing obvious in the data

#### 32. 2CRSI (AL2SI.PA) — tier C, score 67

- **What it does:** 2CRSI S.A., together with its subsidiaries, develops, manufactures, and distributes end-to-end computing solutions in France and internationally. The company offers servers and accessories, such as GPU and AI servers, mainstream compute servers, high density servers, rugged servers, and risers; OCP servers and racks,….
- **Listing:** France, Euronext Growth Paris · Computer Hardware · market cap €593m, €6.9m/day traded · ISIN FR0013341781
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 26.24 → EUR 47.30 mean (range EUR 30.00–EUR 64.60, 2 analysts), upside **+80%**; recommendation 2.0 (1 = strong buy)
- **Revisions:** FY+1 EPS +14.3% (30d) / +14.5% (90d), 1 up / 0 down; current year -1.6% / -5.6%, 0 up / 1 down
- **Valuation:** fwd P/E 8.5, EV/EBITDA 59.1, FCF yield 3.1%, P/B 20.1
- **Quality:** ROIC -14%, operating margin 4%, Piotroski 4/7, FCF conversion n/a
- **Growth:** sales +215% and EPS +235% next year (consensus); 3-year sales CAGR n/a
- **Balance sheet:** net debt 0.2× EBITDA
- **Momentum:** -5% (13w), +90% (52w), -49% from 52-week high; divergence flag: no
- **Rationale [Revisions↑ · Niche leader / supply-chain theme]:** +80% to the mean target of 2 analysts; next-year EPS forecast +14.5% over 90 days (1 up / 0 down in 30 days), consensus EPS growth +235% next year, 8.5× forward earnings, ROIC -14%. Theme: AI / data centres.
- **Key risk:** only 2 analysts; wide spread of analyst targets

#### 36. DIGITAL BROS (DIB.MI) — tier C, score 67

- **What it does:** Digital Bros S.p.A., together with its subsidiaries, engages in the development, publishing, distribution, and marketing of video games in Europe, the Americas, and internationally. It operates through Premium Games, Free to Play, Italian Distribution, and Other Activities segments.
- **Listing:** Italy, Euronext Milan · Electronic Gaming & Multimedia · market cap €149m, €200k/day traded · ISIN IT0001469995
- **Fortuneo:** **Not online** (sale by phone only)
- **Consensus:** EUR 10.40 → EUR 16.25 mean (range EUR 15.00–EUR 17.50, 2 analysts), upside **+56%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +15.1% (30d) / +15.1% (90d), 1 up / 0 down; current year -39.0% / -39.0%, 0 up / 1 down
- **Valuation:** fwd P/E 6.5, EV/EBITDA 2.8, FCF yield 6.5%, P/B 1.4
- **Quality:** ROIC -1%, operating margin 25%, Piotroski 4/7, FCF conversion -129%
- **Growth:** sales +9% and EPS +65% next year (consensus); 3-year sales CAGR n/a
- **Balance sheet:** net cash 0% of market cap
- **Momentum:** -3% (13w), -12% (52w), -27% from 52-week high; divergence flag: no
- **Rationale [Revisions↑ · Cheap vs sector]:** +56% to the mean target of 2 analysts; next-year EPS forecast +15.1% over 90 days (1 up / 0 down in 30 days), consensus EPS growth +65% next year, 6.5× forward earnings, ROIC -1%.
- **Key risk:** only 2 analysts; weak cash conversion (-129% FCF/NI); not buyable online at Fortuneo

#### 38. NAPATECH (NAPA.OL) — tier C, score 66

- **What it does:** Napatech A/S provides programmable smart network interface cards and data processing units solutions for cloud, enterprise, and telecom datacenter networks in the Americas and internationally. The company provides Link Capture Software that enables packet capture with nanosecond timestamping and replay with precise….
- **Listing:** Denmark, Oslo Børs · Communication Equipment · market cap €434m, €1.3m/day traded · ISIN DK0060520450
- **Fortuneo:** German secondary line (check liquidity)
- **Consensus:** NOK 41.50 → NOK 73.88 mean (range NOK 63.03–NOK 84.72, 2 analysts), upside **+78%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +7.1% (30d) / +42.0% (90d), 1 up / 0 down; current year -13.6% / +10.7%, 1 up / 0 down
- **Valuation:** fwd P/E 42.3, EV/EBITDA -79.8, FCF yield -0.6%, P/B 18.0
- **Quality:** ROIC -56%, operating margin -19%, Piotroski 5/7, FCF conversion n/a
- **Growth:** sales +166% and EPS +492% next year (consensus); 3-year sales CAGR -3%
- **Balance sheet:** net cash 2% of market cap
- **Momentum:** +6% (13w), +40% (52w), -29% from 52-week high; divergence flag: no
- **Rationale [Revisions↑]:** +78% to the mean target of 2 analysts; next-year EPS forecast +42.0% over 90 days (1 up / 0 down in 30 days), consensus EPS growth +492% next year, 42.3× forward earnings, ROIC -56%.
- **Key risk:** only 2 analysts; loss-making at operating level; German secondary line: spreads may be wide

#### 47. MEDIOS AG  O.N. (ILM1.DE) — tier C, score 66

- **What it does:** Medios AG, together with its subsidiaries, supplies specialty pharmaceutical drugs primarily in Germany. It operates through three segments: Patient-Specific Therapies; International Business; and Pharmaceutical Supply.
- **Listing:** Germany, Xetra/Frankfurt (Prime Standard) · Medical Distribution · market cap €265m, €404k/day traded · ISIN DE000A1MMCC8
- **Fortuneo:** Xetra/Frankfurt
- **Consensus:** EUR 10.38 → EUR 20.25 mean (range EUR 16.00–EUR 23.00, 4 analysts), upside **+95%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS -3.2% (30d) / -11.4% (90d), 0 up / 2 down; current year -5.9% / +8.2%, 0 up / 1 down
- **Valuation:** fwd P/E 6.8, EV/EBITDA 5.3, FCF yield 8.7%, P/B 0.5
- **Quality:** ROIC 6%, operating margin 2%, Piotroski 7/7, FCF conversion 271%
- **Growth:** sales +4% and EPS +30% next year (consensus); 3-year sales CAGR +9%
- **Balance sheet:** net debt 1.7× EBITDA
- **Momentum:** -17% (13w), -19% (52w), -39% from 52-week high; divergence flag: no
- **Rationale [Cheap vs sector · Hidden assets / net cash]:** +95% to the mean target of 4 analysts; next-year EPS forecast -11.4% over 90 days (0 up / 2 down in 30 days), consensus EPS growth +30% next year, 6.8× forward earnings, ROIC 6%. Theme: healthcare niche.
- **Key risk:** estimate cuts

#### 54. Vusion (VU.PA) — tier C, score 64

- **What it does:** Vusion S.A. engages in the provision of digitalization solutions for commerce in France, rest of Europe, the Middle East, Africa, Asia, and the Americas. The company offers computer vision and artificial intelligence (AI) platform, which provides inventory management with automatic monitoring and alerts; retail intelligence….
- **Listing:** France, Euronext Paris · Software - Application · market cap €2.1bn, €4.8m/day traded · ISIN FR0010282822
- **Fortuneo:** Direct (Paris/Brussels/Amsterdam)
- **Consensus:** EUR 123.50 → EUR 203.33 mean (range EUR 170.00–EUR 260.00, 6 analysts), upside **+65%**; recommendation 1.2 (1 = strong buy)
- **Revisions:** FY+1 EPS -2.8% (30d) / -3.0% (90d), 2 up / 2 down; current year -4.2% / -4.6%, 1 up / 3 down
- **Valuation:** fwd P/E 11.1, EV/EBITDA 9.2, FCF yield -25.6%, P/B 3.8
- **Quality:** ROIC 103%, operating margin 9%, Piotroski 7/7, FCF conversion 313%
- **Growth:** sales +9% and EPS +21% next year (consensus); 3-year sales CAGR +33%
- **Balance sheet:** net cash 9% of market cap
- **Momentum:** -5% (13w), -49% (52w), -49% from 52-week high; divergence flag: no
- **Rationale [Niche leader / supply-chain theme]:** +65% to the mean target of 6 analysts; next-year EPS forecast -3.0% over 90 days (2 up / 2 down in 30 days), consensus EPS growth +21% next year, 11.1× forward earnings, ROIC 103%. Theme: AI / data centres.
- **Key risk:** estimate cuts

#### 55. INIT INNOVATION O.N. (IXX.DE) — tier C, score 64

- **What it does:** init innovation in traffic systems SE, together with its subsidiaries, engages in the provision of intelligent transportation systems solutions for public transportation in Germany and internationally. It offers mobility and electromobility; planning and dispatching, ticketing and fare management, analyzing and optimizing,….
- **Listing:** Germany, Xetra/Frankfurt (Prime Standard) · Information Technology Services · market cap €465m, €223k/day traded · ISIN DE0005759807
- **Fortuneo:** Xetra/Frankfurt
- **Consensus:** EUR 42.50 → EUR 65.17 mean (range EUR 60.00–EUR 68.00, 3 analysts), upside **+53%**; recommendation 1.0 (1 = strong buy)
- **Revisions:** FY+1 EPS +0.0% (30d) / -2.1% (90d), 1 up / 1 down; current year +0.0% / -5.0%, 0 up / 2 down
- **Valuation:** fwd P/E 14.0, EV/EBITDA 10.0, FCF yield 5.0%, P/B 2.5
- **Quality:** ROIC 14%, operating margin 5%, Piotroski 7/7, FCF conversion 36%
- **Growth:** sales +13% and EPS +27% next year (consensus); 3-year sales CAGR +20%
- **Balance sheet:** net debt 0.4× EBITDA
- **Momentum:** -12% (13w), -11% (52w), -21% from 52-week high; divergence flag: no
- **Rationale [Cheap vs sector · Niche leader / supply-chain theme]:** +53% to the mean target of 3 analysts; next-year EPS forecast -2.1% over 90 days (1 up / 1 down in 30 days), consensus EPS growth +27% next year, 14.0× forward earnings, ROIC 14%.
- **Key risk:** weak cash conversion (36% FCF/NI)

#### 56. SFC ENERGY AG (F3C.DE) — tier C, score 64

- **What it does:** SFC Energy AG, together with its subsidiaries, develops, produces, and distributes systems and solutions for stationary and mobile off-grid power supply based on hydrogen and direct methanol fuel cells worldwide. The company operates in two segments, Clean Energy and Clean Power Management.
- **Listing:** Germany, Xetra/Frankfurt (Prime Standard) · Electrical Equipment & Parts · market cap €324m, €860k/day traded · ISIN DE0007568578
- **Fortuneo:** Xetra/Frankfurt
- **Consensus:** EUR 18.62 → EUR 27.90 mean (range EUR 26.00–EUR 31.00, 5 analysts), upside **+50%**; recommendation n/a (1 = strong buy)
- **Revisions:** FY+1 EPS +1.7% (30d) / +14.0% (90d), 2 up / 1 down; current year +0.6% / +31.1%, 2 up / 2 down
- **Valuation:** fwd P/E 17.1, EV/EBITDA 13.5, FCF yield 0.8%, P/B 2.2
- **Quality:** ROIC 3%, operating margin 22%, Piotroski 2/7, FCF conversion -22%
- **Growth:** sales +13% and EPS +18% next year (consensus); 3-year sales CAGR +19%
- **Balance sheet:** net cash 8% of market cap
- **Momentum:** -7% (13w), +16% (52w), -21% from 52-week high; divergence flag: **yes**
- **Rationale [Revisions↑ · Forecasts up / price down · Niche leader / supply-chain theme]:** +50% to the mean target of 5 analysts; next-year EPS forecast +14.0% over 90 days (2 up / 1 down in 30 days), consensus EPS growth +18% next year, 17.1× forward earnings, ROIC 3%. Theme: energy transition. Forecasts rose while the share price fell — the market may not have noticed.
- **Key risk:** weak cash conversion (-22% FCF/NI)

## 4. Uncovered gems (top 15)

No analyst consensus (so no upside figure), but high score on quality, growth, valuation and balance sheet. Fortuneo-accessible only.

| # | Company | Country / venue | Fortuneo | Industry | Mkt cap | Fwd/trailing P/E | EV/EBITDA | ROIC | Op. margin | Net cash / mcap | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **CALTAGIRONE** | Italy / Euronext Milan | DE 2nd line | Building Materials | €1.1bn | 6.6 | 6.5 | 15% | 8% | +24% | 76 |
| 2 | **Azkoyen, S.A.** | Spain / MCE | DE 2nd line | Business Equipment & Supplies | €251m | 16.1 | 8.5 | 15% | 10% | +5% | 74 |
| 3 | **NEURONES** | France / Euronext Paris | Direct | Information Technology Services | €881m | 16.8 | 7.2 | 68% | 9% | +30% | 73 |
| 4 | **Grupo Empresarial San José, S.A.** | Spain / MCE | DE 2nd line | Engineering & Construction | €453m | 10.4 | -0.7 | n/a | 3% | +119% | 72 |
| 5 | **FIERA MILANO** | Italy / Euronext Milan | DE 2nd line | Specialty Business Services | €513m | 10.6 | 7.7 | 18% | 23% | -33% | 71 |
| 6 | **Zinzino AB (publ)** | Sweden / Stockholm | DE 2nd line | Packaged Foods | €505m | 11.6 | 8.6 | n/a | 15% | +14% | 71 |
| 7 | **FORFARMERS** | Netherlands / Euronext Amsterdam | Direct | Packaged Foods | €512m | 9.4 | 4.7 | 13% | 3% | -18% | 70 |
| 8 | **Lubawa S.A.** | Poland / Warsaw | DE 2nd line | Conglomerates | €385m | 15.1 | 10.5 | 26% | 16% | +16% | 69 |
| 9 | **Euronext Athens Holding S.A.** | Greece / Athens | DE 2nd line | Financial Data & Stock Exchanges | €585m | 21.5 | 8.2 | 132% | 64% | +24% | 68 |
| 10 | **ELEC.STRASBOURG** | France / Euronext Paris | Direct | Utilities - Renewable | €1.1bn | 8.6 | 3.5 | 40% | 13% | +31% | 67 |
| 11 | **PRECIA** | France / Euronext Growth Paris | Direct | Specialty Industrial Machinery | €112m | 14.1 | 4.6 | 16% | 8% | +18% | 66 |
| 12 | **ZAPTEC** | nan / Oslo Børs | DE 2nd line | nan | €470m | n/a | n/a | 15% | n/a | n/a | 66 |
| 13 | **BIJOU BRIGITTE O.N.** | Germany / Xetra/Frankfurt (General Standard) | Xetra | Luxury Goods | €342m | 15.3 | 6.0 | 11% | 11% | -3% | 66 |
| 14 | **FM Mattsson AB (publ)** | Sweden / Stockholm | DE 2nd line | Building Products & Equipment | €454m | 16.0 | 17.5 | 16% | 15% | +4% | 66 |
| 15 | **Zespól Elektrocieplowni Wroclawskich KOGENERACJA S.A.** | Poland / Warsaw | DE 2nd line | Utilities - Regulated Electric | €274m | 2.2 | 2.4 | 9% | -3% | -31% | 65 |

## 5. Divergence: forecasts up, price down (top 15)

Next-year EPS forecast up > 2% over 90 days while the share price fell > 5% over 13 weeks; passes the upside threshold.

| # | Company | Country | Fortuneo | Upside | Rev. 90d FY+1 | Price 13w | Fwd P/E | Score | In main list |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **FRIEDRICH VORWERK GROUP SE** | Germany | Xetra | +37% | +15.2% | -7% | 11.4 | 76 | #2 |
| 2 | **HEIJMANS KON** | Netherlands | Direct | +47% | +13.3% | -13% | 10.5 | 75 | #4 |
| 3 | **LNA SANTE** | France | Direct | +76% | +13.0% | -33% | 6.9 | 75 | #5 |
| 4 | **Rainbow Tours S.A.** | Poland | **Not online** | +54% | +12.0% | -8% | 7.9 | 73 | #7 |
| 5 | **HEXAOM** | France | Direct | +118% | +17.1% | -16% | 4.4 | 73 | #6 |
| 6 | **ASML HOLDING** | Netherlands | Direct | +43% | +11.0% | -5% | 26.4 | 72 | #8 |
| 7 | **ACS, Actividades de Construcción y Servicios, S.A.** | Spain | DE 2nd line | +47% | +2.3% | -22% | 18.1 | 71 | #11 |
| 8 | **ASM INTERNATIONAL** | Netherlands | Direct | +53% | +13.8% | -12% | 23.8 | 71 | #12 |
| 9 | **TECHNOPROBE** | Italy | DE 2nd line | +61% | +19.5% | -11% | 32.1 | 71 | #13 |
| 10 | **SUSS MicroTec SE** | Germany | Xetra | +96% | +8.3% | -29% | 14.6 | 70 | #14 |
| 11 | **ZEAL NETWORK SE NA O.N.** | Germany | Xetra | +87% | +3.1% | -9% | 16.2 | 70 | #15 |
| 12 | **Técnicas Reunidas, S.A.** | Spain | DE 2nd line | +52% | +3.9% | -9% | 8.1 | 69 | #16 |
| 13 | **HOCHTIEF AG** | Germany | Xetra | +36% | +8.2% | -17% | 20.2 | 69 | #17 |
| 14 | **RVRC Holding AB (publ)** | Sweden | DE 2nd line | +52% | +11.0% | -11% | 11.4 | 68 | #24 |
| 15 | **SIEMENS ENERGY AG NA O.N.** | Germany | Xetra | +43% | +3.9% | -11% | 21.6 | 67 | #31 |

## 6. Comparison with run 1

Run 1 (`research/pea-screening.md`) had 48 core leads built from web research. **5 are still in the v2 main list.** Run 1 used fresh broker targets from news; v2 uses only the Yahoo consensus as of 18 Oct, so differences in upside are expected.

| Run-1 lead | Matched in v2 data | Status in v2 |
|---|---|---|
| Jenoptik | JENOPTIK AG  NA O.N. (JEN.DE) | passes threshold but outside top 60 (score 63) |
| Technoprobe | TECHNOPROBE (TPRO.MI) | **still in** — #13, tier A |
| Alten | ALTEN (ATE.PA) | dropped — threshold: upside +21% vs +25% needed |
| Ottobock | Ottobock SE & Co. KGaA (OBCK.DE) | passes threshold but outside top 60 (score 62) |
| AMG Critical Materials | AMG (AMG.AS) | **still in** — #28, tier B |
| Nolato | Nolato AB (publ) (NOLA-B.ST) | dropped — threshold: upside +16% vs +25% needed |
| ID Logistics | ID LOGISTICS GROUP (IDL.PA) | passes threshold but outside top 60 (score 56) |
| ALK-Abelló | ALK-Abelló A/S (ALK-B.CO) | passes threshold but outside top 60 (score 56) |
| Lectra | LECTRA (LSS.PA) | dropped — threshold: upside +11% vs +35% needed |
| Scout24 | SCOUT24 AG NA O.N. (G24.DE) | passes threshold but outside top 60 (score 58) |
| Titan Cement | Titan S.A. (TITC.AT) | passes threshold but outside top 60 (score 57) |
| Alzchem | ALZCHEM GROUP AG INH O.N. (ACT.DE) | passes threshold but outside top 60 (score 52) |
| Basic-Fit | BASIC-FIT (BFIT.AS) | passes threshold but outside top 60 (score 59) |
| SUSS MicroTec | SUSS MicroTec SE (SMHN.DE) | **still in** — #14, tier B |
| AT&S | AT & S Austria Technologie & Systemtechnik Aktiengesellschaft (ATS.VI) | **still in** — #29, tier C |
| Kontron | KONTRON AG O.N (KTN.DE) | passes threshold but outside top 60 (score 57) |
| VusionGroup | — | not matched in the v2 data (name or symbol missing) |
| Nabaltec | — | not matched in the v2 data (name or symbol missing) |
| Eckert & Ziegler | ECKERT+ZIEGLER SE O.N. (EUZ.DE) | passes threshold but outside top 60 (score 60) |
| Bonesupport | Bonesupport Holding AB (publ) (BONEX.ST) | **still in** — #42, tier A |
| Equasens | EQUASENS (EQS.PA) | passes threshold but outside top 60 (score 60) |
| Nemetschek | NEMETSCHEK SE O.N. (NEM.DE) | passes threshold but outside top 60 (score 56) |
| Atoss Software | ATOSS SOFTWARE SE (AOF.DE) | passes threshold but outside top 60 (score 60) |
| CTS Eventim | CTS EVENTIM KGAA (EVD.DE) | passes threshold but outside top 60 (score 55) |
| Mensch und Maschine | MENSCH UND MASCHINE SOFTWARE O.N. (MUM.DE) | passes threshold but outside top 60 (score 58) |
| Ipsos | IPSOS (IPS.PA) | passes threshold but outside top 60 (score 52) |
| Krones | KRONES AG O.N. (KRN.DE) | passes threshold but outside top 60 (score 50) |
| Interpump | INTERPUMP GROUP (IP.MI) | passes threshold but outside top 60 (score 52) |
| Palfinger | Palfinger AG (PAL.VI) | passes threshold but outside top 60 (score 59) |
| Elis | ELIS (ELIS.PA) | passes threshold but outside top 60 (score 54) |
| DO & CO | DO & CO Aktiengesellschaft (DOC.VI) | passes threshold but outside top 60 (score 60) |
| Fluidra | Fluidra, S.A. (FDR.MC) | passes threshold but outside top 60 (score 61) |
| Mips | Mips AB (publ) (MIPS.ST) | dropped — threshold: upside +26% vs +35% needed |
| Trigano | TRIGANO (TRI.PA) | passes threshold but outside top 60 (score 55) |
| Technogym | TECHNOGYM (TGYM.MI) | passes threshold but outside top 60 (score 56) |
| Sanlorenzo | SANLORENZO (SL.MI) | passes threshold but outside top 60 (score 55) |
| Invisio | — | not matched in the v2 data (name or symbol missing) |
| Renk | RENK GROUP AG (R3NK.DE) | passes threshold but outside top 60 (score 62) |
| Steyr Motors | Steyr Motors AG (4X0.DE) | passes threshold but outside top 60 (score 49) |
| Camurus | Camurus AB (publ) (CAMX.ST) | dropped — threshold: upside +24% vs +25% needed |
| Fagron | — | not matched in the v2 data (name or symbol missing) |
| Redcare Pharmacy | REDCARE PHARMACY N.V. (RDC.DE) | dropped — threshold: upside +19% vs +25% needed |
| Jungheinrich | JUNGHEINRICH AG O.N.VZO (JUN3.DE) | passes threshold but outside top 60 (score 51) |
| Stabilus | STABILUS SE INH. EO-,01 (STM.DE) | passes threshold but outside top 60 (score 58) |
| Vossloh | VOSSLOH AG O.N. (VOS.DE) | passes threshold but outside top 60 (score 51) |
| Fielmann | FIELMANN AG O.N. (FIE.DE) | passes threshold but outside top 60 (score 60) |
| Cadeler | CADELER (CADLR.OL) | passes threshold but outside top 60 (score 56) |
| Exor | EXOR NV (EXO.AS) | passes threshold but outside top 60 (score 40) |

## 7. Method and caveats

- **Source:** all figures come from Yahoo Finance, fetched on 18 Oct 2026. For small caps the consensus may be one or two brokers, sometimes stale or in the wrong currency; `data_flag` rows (upside outside −80%/+300%) are left out of the lists.
- **Scoring:** each pillar is the average of percentile ranks across the universe (0–1); score = 25 revisions + 20 upside + 20 quality + 15 growth + 15 valuation vs sector + 5 balance sheet. ROIC uses EBIT × 0.75.
- **Selection:** clean passing names sorted by score with a small bonus for easier Fortuneo access (direct +3, Xetra +2); at most 10 `not online` names.
- **Lead types** and themes are inferred automatically from industry, the Yahoo business description and the numbers; check them.
- **Coverage gaps:** exchanges in Croatia, Slovenia, Bulgaria, Slovakia, Cyprus and Malta are not covered; some German symbols are missing (e.g. K+S).
- **Fortuneo access** follows the official tariff brochure (https://www.fortuneo.fr/files/tarifs_fortuneo.pdf): Paris/Brussels/Amsterdam online; Xetra/Frankfurt at 0.20% (min €20, +€30 foreign fee, €400 minimum order); Milan, Madrid, Nordics, Vienna, Lisbon sale-only by phone.
- **Not investment advice — verify every figure (price, targets, latest results) before acting.**
