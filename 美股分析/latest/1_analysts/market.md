# `.NDX` — NASDAQ-100 Technical Report (Analysis Date: 2026-11-16)

## 1. Executive Summary

`.NDX` is in a confirmed, well-established **downtrend** that has been in force for roughly six weeks. The verified close on 2026-11-16 is **27,197.15**, down from **31,224.47** on 2026-10-06 — a decline of **4,027.32 points (−12.90%)** on a closing basis, computed directly from the verified close series. Price now sits **below every major moving average** (10 EMA 27,945.73; 200 SMA 28,047.57; 50 SMA 29,459.00), the 50 SMA is collapsing under price, MACD is deeply negative, and ATR is at the highest level in the 30-day window.

Importantly, the market is **not oversold on a reversal-ready basis yet**: RSI is 37.56 — weak but above 30 — and price is mid-way between the Bollinger lower band (26,641.51) and middle band (28,471.71). This is a "trend down, momentum weak, volatility expanding" regime where **selling rallies into resistance is the higher-probability play**, and any long exposure should be tactical and sized against ATR.

---

## 2. Indicators Selected and Rationale

| Indicator | Why it earned a slot in this regime |
|---|---|
| **close_50_sma** | The medium-term trend anchor; it is currently rolling over decisively, telling us the intermediate trend has flipped down. |
| **close_200_sma** | Strategic trend filter; price crossing below it is the defining event of the current move (a "death cross" setup is developing against the 50 SMA). |
| **close_10_ema** | Fast momentum read for timing entries/exits and identifying weak counter-trend bounces. |
| **macd + macds + macdh** | Trend/momentum engine; the histogram is the key discriminator between a fresh leg down and a forming bottom. Included as a single concept despite three columns. |
| **rsi** | Non-redundant with MACD: measures the *speed* of decline and whether the market is stretched enough to bounce. |
| **boll / boll_ub / boll_lb** | Volatility envelope + 20 SMA benchmark; defines where mean reversion is possible and where a "band ride" downside is in progress. |
| **atr** | Volatility has more than doubled in six weeks; ATR is essential for stops and position sizing. |
| **vwma** | Volume-weighted price confirms whether the decline is being *sold on real volume* (it is) vs. drifting. |

I deliberately **excluded stochrsi** (redundant with RSI) and did not include additional momentum oscillators, since the chosen set already spans trend, momentum, volatility, and volume without duplication.

---

## 3. Trend Structure

### 3.1 Moving average stack — fully bearish alignment
- **Close (27,197.15) < 200 SMA (28,047.57) < 50 SMA (29,459.00)**
- Normal bullish order would be price > 50 > 200. We have the **exact inverse**, which is a textbook bearish stack.
- The **50 SMA has fallen for 30 consecutive sessions**, from 29,580.59 (2026-10-06) to 29,459.00 (2026-11-16) — actually, more precisely it *peaked* around 29,871.71 on 2026-10-15 and has declined every session since to today's 29,459.00. That is a clear, unbroken roll-over.
- The **200 SMA is flat-to-slightly-up** (27,541.11 on 2026-10-06 → 28,047.57 on 2026-11-16). Price closing below a rising 200 SMA is characteristic of the *first* major breakdown of a long uptrend — a more serious signal than a break of a falling 200 SMA.
- Because the 50 SMA (29,459) is still far above the 200 SMA (28,048) and the 50 is falling while the 200 rises, the two are converging. A **death cross is not yet printed** — I will not claim one — but the trajectory points toward it if the current drift continues.

### 3.2 10 EMA — the "sell the rip" line
- 10 EMA is **27,945.73**, roughly **748 points above price**. Price has traded below its 10 EMA since 2026-10-14 (10 EMA 30,568.96 vs close 29,950.82) and has not reclaimed it on a closing basis since. That persistent sub-10-EMA behavior is the signature of a *continuous* downtrend rather than a choppy range.
- The 10 EMA has flattened modestly (28,149.49 → 28,112.08 → 27,945.73 over the last three sessions), showing the decline is decelerating, but it remains a clean overhead reference.

### 3.3 Swing structure from the verified close series
- Successive lower highs: 31,224.47 (10-06) → 30,664.70 (10-12) → 29,822.52 (10-21) → 29,813.16 (10-28) → 28,437.17 (11-04) → 28,374.25 (11-11).
- Successive lower lows: 28,958.69 (10-22) → 28,384.85 (10-30) → **26,629.81 (11-05)** → and the current session's low of **27,149.15** (11-16) has *not* undercut the 11-05 low on a closing basis (close 27,197.15 > 26,629.81). 

This is the most important nuance: **the 11-05 capitulation low (~26,630) is the line in the sand.** Today's session closed 567 points above it. As long as closes hold above 26,629.81, the structure is "downtrend with a possible double-bottom attempt"; a close below it would confirm a fresh low and likely trigger the next leg.

---

## 4. Momentum Analysis

### 4.1 MACD — bearish, but decelerating then re-buckling
| Date | MACD | Signal | Histogram |
|---|---:|---:|---:|
| 2026-10-06 | +414.41 | +315.65 | +98.76 |
| 2026-10-19 | +2.33 | +205.38 | −203.05 |
| 2026-11-06 | −679.74 | −408.87 | −270.87 |
| 2026-11-13 | −530.58 | −526.09 | −4.48 |
| 2026-11-16 | **−570.69** | **−535.01** | **−35.68** |

- **MACD line crossed below zero around 2026-10-20** (first negative reading −50.53 on that date) and crossed below its signal around 2026-10-13 (histogram first negative −26.25). Both bearish triggers fired long ago; they are *confirmed*, not new.
- The MACD line bottomed at **−679.74 on 2026-11-06** and recovered to **−530.58 by 11-13**, pulling the histogram from −270.87 up to nearly zero (−4.48). That was a genuine momentum recovery — and it **failed at the zero line**.
- On 2026-11-16 the histogram re-widened negative to **−35.68** and MACD rolled back to −570.69. This is a **bearish re-acceleration / failed-recovery** signature: the rally from 11-05 to 11-12 did not generate enough momentum to flip the histogram positive, and selling has resumed.

Interpretation: momentum is still down, the *rate* of decline is no longer the extreme of 11-06, but the nascent bottoming attempt has been rejected. This tilts the tactical bias back to the downside.

### 4.2 RSI — weak, not yet capitulatory
- Current RSI **37.56**, down from 42.66 on 11-13.
- The **low of the window was 27.00 on 2026-11-05** — RSI dropped below 30 exactly at the 26,629.81 capitulation close. That is the only oversold reading in the 30-day window.
- RSI then recovered 27.00 → 45.96 (11-11) → 42.66 (11-13) → 37.56 (11-16) — an **RSI lower high** versus the 49.43 print on 2026-10-28, consistent with the declining price highs.
- Critically, RSI at 37.5 is **in the bearish half of the range but not oversold**. There is room for another 6–8 RSI points of downside before a mechanical oversold bounce signal appears, unless the index gaps directly into the 11-05 low zone.
- No confirmed bullish divergence is present: the 11-05 price low (26,629.81) does not yet have a matching RSI low from a subsequent price low, because **no lower price low has been made since**.

---

## 5. Volatility and Band Structure

### 5.1 Bollinger Bands — downward-sloping, price in lower half
| Band | 2026-10-06 | 2026-11-16 | Change |
|---|---:|---:|---:|
| Upper | 31,511.25 | 30,301.91 | −1,209.34 |
| Middle (20 SMA) | 30,070.09 | 28,471.71 | −1,598.38 |
| Lower | 28,628.93 | 26,641.51 | −1,987.42 |

- **All three bands are falling**, and the lower band is falling fastest — that is **band expansion to the downside**, the classic signature of a trending (not mean-reverting) decline.
- Price (27,197.15) is **below the middle band (28,471.71)** and roughly **555 points above the lower band (26,641.51)**. So the index is in the lower quadrant but not pinned to the lower band.
- Band width is large: upper minus lower = **3,660.40 points** (2026-11-16). This is a wide envelope (~13.5% of price), reflecting the volatility expansion.
- Band width has actually *contracted marginally* over the last week (11-09 upper 30,952.88 / lower 26,953.31 = 3,999.57 width vs. 3,660.40 today), suggesting volatility is high but no longer expanding aggressively. If band width now contracts while price hugs the middle band, a base could form — but that is **not yet evidenced**, only a watch item.

### 5.2 ATR — volatility more than doubled
- ATR: **374.56 (2026-10-06) → 674.01 (2026-11-16)**, a **+299.45 point (+79.9%)** increase.
- ATR has made a **new high of the window on 2026-11-16** (prior peak 667.33 on 11-11), confirming that the most recent decline is occurring in the *highest-volatility* environment of the period.
- At ATR 674 on a 27,197 close, a 1×ATR daily move is **~2.5% of index value**. Practical implications:
  - Stops must be at least ~1.5×ATR (~1,010 points) beyond an entry to avoid noise stops.
  - Position size should be cut roughly in proportion — a position that sized correctly at ATR 375 should be **about 44% of its former notional** (375/674 ≈ 0.56, so reduce by ~44%) to hold risk constant.
- The 2026-11-16 session itself had a range of 472.49 points (27,621.64 − 27,149.15), a fairly normal day relative to current ATR — the day was a directional grind, not a shock.

---

## 6. Volume and Volume-Weighted Price

- **VWMA is 28,045.58**, essentially coincident with the 200 SMA (28,047.57) and ~848 points above price. Price below the VWMA means the *average dollar-weighted participant* over the period is underwater — a selling-pressure confirmation.
- VWMA has declined every session since 2026-10-13 (30,690.39) → 28,045.58 today, a continuous 20,000+ point aggregate roll-down.
- **Notable high-volume sessions** in the verified data:
  - **2026-11-12: 1.873e9** — the heaviest volume of the recent stretch, on an *up* close (28,289.19) after a 28,548.55 intraday high. That looks like **supply into strength** (rally rejected).
  - **2026-11-16: 1.494e9** — elevated volume on a **−746.59 point down day** (27,943.74 → 27,197.15 = −2.67%). Distribution on the decline.
  - **2026-11-11: 1.514e9** on the +633.46 point up day — buying happened there, but it was not sustained.
- ⚠️ **Discrepancy flag:** the verified snapshot reports 2026-11-16 volume as **9,208,530,000**, whereas the raw `get_stock_data` row shows **1.494e9** (approximately 1,494,171,000). The verified snapshot is treated as the source of truth for the exact figure, but I am flagging the ~6x inconsistency because it means I should not build a precise "relative volume ratio" argument. Qualitatively, in *both* datasets the recent sessions are among the heaviest in the window, and the 11-12 volume was the highest — so the directional conclusion ("volume expanded on the decline") holds, but the exact multiple is uncertain.

---

## 7. Synthesis: What Regime Are We In?

This is **late-stage corrective downtrend with volatility expansion** — not a garden-variety pullback. Key evidence:

1. Price has broken and closed below the **rising 200 SMA** — a strategic trend failure.
2. The **50 SMA is rolling over** and price is 2,262 points below it.
3. **MACD is deeply negative** with a freshly re-widening bearish histogram after a failed attempt to reclaim zero.
4. **ATR at a window high** (674) — risk per day is elevated.
5. **VWMA confirms** the average participant is underwater.
6. But: **RSI at 37.56 is not oversold**, price is **not at the lower band**, and the **11-05 low (26,629.81) has held** — so it is a *mature* decline rather than a fresh crash.

The balance of evidence favors **continuation risk with tactical bounce potential**. The bounce attempt from 11-05 to 11-12 (+1,744.44 points from 26,629.81 to 28,374.25, or **+6.55%**) stalled just under the 200 SMA (~28,048–28,100 zone) and reversed — meaning the 200 SMA has become **overhead resistance**, not support.

---

## 8. Actionable Trading Plan

### 8.1 Bias: Bearish / defensive
Avoid initiating new long exposure at the index level until price either reclaims the 200 SMA or prints a genuine oversold reversal at/below the 11-05 low.

### 8.2 Concrete levels (all from verified data)

| Level | Value | Significance |
|---|---:|---|
| Bollinger lower | 26,641.51 | Lower envelope; near 11-05 low |
| **11-05 capitulation low (close)** | **26,629.81** | **Key structural support** |
| Current close | 27,197.15 | — |
| 10 EMA | 27,945.73 | First resistance / trend-fade zone |
| **200 SMA** | **28,047.57** | **Major resistance — reject zone** |
| VWMA | 28,045.58 | Confirms 200 SMA as a magnet |
| Bollinger middle (20 SMA) | 28,471.71 | Second resistance |
| 11-12 rally high (intraday) | 28,548.55 | Swing high of failed bounce |
| 50 SMA | 29,459.00 | Strategic resistance; trend-flip line |
| Bollinger upper | 30,301.91 | Cycle-high overflow zone |
| **ATR** | **674.01** | Use for stops/sizing |

### 8.3 Trade ideas

**A. Short-the-rip (primary, trend-following)**
- **Entry zone:** 27,850–28,100 (10 EMA → 200 SMA cluster). This is where the 11-12 bounce was rejected and where the 200 SMA now caps.
- **Confirmation:** wait for a rejection candle (close back below 27,945) or MACD histogram re-widening negative — already partially triggered today.
- **Stop:** above **28,550** (11-12 intraday high) — roughly **1.0×ATR above the top of the entry zone**, appropriate given 674 ATR.
- **Target 1:** 26,641–26,630 (11-05 low / lower band) ≈ **4.5–5% downside from entry**.
- **Target 2:** if 26,630 breaks, project 1×ATR below → ~25,950, treating that as an extension target rather than a forecast.
- **Risk/reward:** ~1.0 ATR risk vs. ~2.0–2.5 ATR reward.

**B. Tactical long (secondary, counter-trend, small size)**
- **Trigger:** RSI ≤ 30 *while* price holds above 26,629.81, ideally with a positive MACD histogram divergence (price lower low, MACD line higher low).
- **Entry:** 26,700–26,900 zone, i.e., at/near the lower Bollinger band.
- **Stop:** below **26,300** (0.5×ATR below the 11-05 low) — a close below 26,630 invalidates the double-bottom thesis.
- **Target:** 27,900–28,050 (10 EMA / 200 SMA) ≈ 4–4.5% upside.
- **Caveat:** do **not** take this long until RSI actually reaches oversold. At 37.56 today, a long has no edge — it would be buying mid-range with downside momentum intact.

**C. Stop-loss and sizing discipline**
- Minimum stop distance: **1.0–1.5×ATR = 674–1,011 points** (~2.5–3.7%).
- Reduce position notional by roughly **(674/375 − 1) ≈ 80% reduction** versus what would have been appropriate at October's volatility, or equivalently multiply normal size by ~0.56, to maintain constant risk.

### 8.4 Invalidation / what would change the view
1. **Bullish:** Two consecutive closes **above 28,050** (200 SMA + VWMA cluster) and MACD histogram turning positive → trend-failure becomes a base; stand aside from shorts.
2. **Bullish (stronger):** Reclaim of the **Bollinger middle at 28,471.71** and then the 11-12 high at 28,548.55 → room to 50 SMA at 29,459.
3. **Bearish (confirmation of next leg):** A **close below 26,629.81** — this would confirm a lower low, keep MACD negative, and likely re-expand ATR further. Expect a fast move toward the 26,000 area.
4. **Watch:** 50/200 SMA convergence. The gap is now 29,459.00 − 28,047.57 = **1,411.43** points and shrinking; a death cross would be a multi-week strategic bear signal for the index.

---

## 9. Key Risks to This Read

- **Rally squeeze risk:** With RSI at 37.56 and a large gap between price (27,197) and the 200 SMA (28,048), a two-day short-squeeze to the 28,000 zone is entirely feasible on ~0.7×ATR moves. Shorts should be sized for this.
- **Oversold reflex bounce:** The 11-05 low was the one true oversold print. If RSI dips to 30 again and price holds 26,630, a sharp mean-reversion rally toward 28,000 is plausible.
- **Volume data inconsistency:** the verified snapshot (9.21e9) and the raw data (1.49e9) disagree materially on 2026-11-16 volume. Volume-based conclusions are directionally supported (volume rising on declines) but should not be used for precise ratio thresholds.
- **Index-level caveats:** `.NDX` is a capitalization-weighted index; a handful of mega-cap names dominate. The technical picture of the index can mask wide dispersion among constituents — position risk at the single-name level may be materially higher than ATR suggests.
- No claim of historical support/resistance validation is made; the levels above are derived purely from current indicator values and the verified price series.

---

## 10. Summary Table

| Category | Indicator | Latest Value (2026-11-16) | Signal / Interpretation | Action Implication |
|---|---|---:|---|---|
| Trend (medium) | close_50_sma | 29,459.00 | Price 2,261.85 below; SMA falling every session since 10-15 | Intermediate trend = down; 50 SMA is the trend-flip line |
| Trend (long) | close_200_sma | 28,047.57 | Price 850.42 below; SMA still rising → strategic breakdown | Bearish; this is now resistance, not support |
| Trend (short) | close_10_ema | 27,945.73 | Price 748.58 below; no close above since 10-14 | Sell rallies into 10 EMA |
| Momentum | macd | −570.69 | Deeply negative; rolled back down from −530.58 | Bearish re-acceleration |
| Momentum | macds | −535.01 | MACD below signal | Confirmed bearish regime |
| Momentum | macdh | −35.68 | Re-widened negative after near-zero (−4.48 on 11-13) → failed bounce | Bearish; attempt to flip positive failed |
| Momentum | rsi | 37.56 | Weak but **not** oversold; window low 27.00 on 11-05 | Room for further downside; no long edge yet |
| Volatility | boll | 28,471.71 | Price below middle band | Lower-half of range |
| Volatility | boll_ub | 30,301.91 | Falling and far above price | No breakout risk near term |
| Volatility | boll_lb | 26,641.51 | Falling fastest; ~555 below price | Downside magnet / entry zone for tactical long |
| Volatility | atr | 674.01 | **New window high**; +79.9% since 10-06 | Stops ≥674–1,011 pts; cut size ~44%+ |
| Volume | vwma | 28,045.58 | Price 848 below; VWMA declined 20 sessions straight | Confirms distribution / underwater average holder |
| Structure | 11-05 low | 26,629.81 | Held on closing basis through 11-16 | Pivotal support; break = fresh leg down |
| **Overall** | — | **27,197.15** | **Bearish trend, decelerating-then-re-buckling momentum, vol expanding** | **Fade rallies to 27,850–28,100; long only on RSI ≤30 at 26,700** |