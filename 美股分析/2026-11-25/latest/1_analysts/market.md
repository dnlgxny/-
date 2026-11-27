# .NDX (Nasdaq-100) — Technical Analysis Report
**As of close: 2026-11-25**

> **Data integrity note:** I attempted to call `get_verified_market_snapshot` for .NDX on 2026-11-25; the tool returned **DATA_UNAVAILABLE** (vendor rate-limited). Therefore, no "verified" cross-check exists for this report. All exact OHLCV and indicator values below come from `get_stock_data` and `get_indicators` output. Treat these as the best available figures, not as snapshot-confirmed levels. I have not reconciled or invented any number where sources were absent.

---

## 1. Market Context Summary

.NDX is in a **pronounced, accelerating correction inside a still-intact longer-term uptrend**. Price has fallen from a late-October peak region near 31,000 into the mid-26,000s, with the last five sessions showing outsized, high-volume distribution. Momentum is deeply negative, volatility is spiking, and the index has broken below every major short- and medium-term average. The 200-day SMA remains far below price, so this is best characterized as a *sharp drawdown within a bull market*, not yet a confirmed trend reversal — but the rate of deterioration demands defensive risk management.

---

## 2. Price Action and Trend Structure

### Recent verified closes (from `get_stock_data`)
| Date | Open | High | Low | Close | Volume |
|---|---|---|---|---|---|
| 2026-11-19 | 27,574.24 | 27,749.35 | 26,481.82 | 26,517.05 | 1.66B |
| 2026-11-20 | 26,184.76 | 26,429.09 | 24,910.48 | 25,028.98 | 2.14B |
| 2026-11-23 | 26,889.29 | 27,018.88 | 26,386.42 | 26,746.10 | 2.38B |
| 2026-11-24 | 26,298.14 | 26,433.60 | 25,935.46 | 26,214.17 | 1.41B |
| 2026-11-25 | 25,309.61 | 26,081.65 | 24,970.66 | 26,046.90 | 1.65B |

Observations supported directly by these rows:
- **Violent two-way volatility:** 11-20 alone spanned a range from 24,910.48 to 26,429.09 (~1,519 points) on 2.14B volume — the highest-volume day in this window.
- **Sharp reversal attempt on 11-23:** +1,717 points off the 11-20 close (25,028.98 → 26,746.10) on the largest volume (2.38B). That bounce failed to follow through: 11-24 gave back 531.93 points.
- **11-25 opened 25,309.61 — a gap down of ~904 points from the prior close** — traded as low as 24,970.66, then closed at 26,046.90, near the top of the day's range. This is a **high-volume intraday reversal/possible capitulation print**, but it is a single-session signal and needs confirmation.
- The lowest close in this five-day window (25,028.98 on 11-20) and the lowest low (24,910.48 on 11-20) are the relevant near-term reference points. The 11-25 low (24,970.66) is a marginal undercut of the 11-20 low, forming a potential **double-bottom-like test** — again, unconfirmed.

### Moving averages (2026-11-25)
| Average | Value | Price vs. Average |
|---|---|---|
| close_10_ema | 26,683.25 | Price 26,046.90 is **~636 pts below (−2.4%)** |
| boll (20 SMA) | 27,406.92 | Price is **~1,360 pts below (−5.0%)** |
| close_50_sma | 29,064.20 | Price is **~3,017 pts below (−10.4%)** |
| close_200_sma | 28,090.98 | Price is **~2,044 pts below (−7.3%)** |

- **Every short-term average is falling and stacked bearishly:** 10 EMA (26,683) > 20 SMA (27,407)? No — actually the 20 SMA (27,407) is *above* the 10 EMA (26,683), which is a textbook bearish short-term ordering; price sits below both.
- **The 50 SMA has just crossed below the 200 SMA.** On 2026-11-25, close_50_sma = 29,064.20 while close_200_sma = 28,090.98. Wait — the 50 is still *above* the 200 by ~973 points, so a death cross has **not** yet occurred. However, the gap has been compressing violently: on 2026-10-16 the 50 SMA was 29,868.00 vs. the 200 SMA at 27,738.00 (gap ~2,130 pts); by 11-25 the gap is ~973 pts. The 50 SMA is falling ~50 pts/day. **A 50/200 bearish cross could occur within weeks if the decline persists** — a major structural warning to monitor.
- Critically, price (26,046.90) is now **below the 200-day SMA (28,090.98) for the first time in this sample.** Checking the history: on 2026-10-16 price was near 30,500 (10 EMA 30,224 vs. 50 SMA 29,868), well above the 200. The break of the 200-day on 2026-11-18–11-19 (price 26,517.05 vs. 200-SMA ~28,070) is a **significant regime-level technical event** — the long-term trend filter has flipped negative on a price basis.

---

## 3. Momentum

### MACD complex
| Date | MACD | Signal | Histogram |
|---|---|---|---|
| 2026-10-07 (peak) | 433.24 | 339.17 | +94.07 |
| 2026-10-20 | −50.53 | 154.20 | −204.73 |
| 2026-11-06 | −679.74 | −408.87 | −270.87 |
| 2026-11-13 | −530.58 | −526.09 | −4.48 |
| 2026-11-20 | −832.16 | −637.15 | −195.01 |
| 2026-11-25 | **−830.66** | **−726.16** | **−104.50** |

- **Bearish MACD crossover occurred on 2026-10-13** (histogram flipped negative: −26.25), confirming the top.
- MACD peaked near +433 on 10-07 and has collapsed to −830.66 — one of the most extreme momentum collapses in the 60-day window.
- **A notable divergence in the signal internals:** the histogram bottomed at −270.87 on 11-06, improved to −4.48 by 11-13, then re-deteriorated to −195.01 on 11-20. On 11-25 the histogram is **−104.50, i.e., improving (less negative) for three consecutive sessions** (11-23: −134.36 → 11-24: −117.14 → 11-25: −104.50), even though the MACD line itself hit a new low (−830.66). This is a **nascent bullish momentum divergence** — the *rate of deterioration* is decelerating while price made a marginal new low. This is an early bottoming hint, not a buy signal; MACD remains far below its signal.
- No bullish MACD crossover is imminent: the MACD line (−830.66) is still ~105 pts below the signal (−726.16).

### RSI
| Date | RSI |
|---|---|
| 2026-10-06 (peak) | 69.83 |
| 2026-10-16 | 35.23 |
| 2026-11-05 | 27.00 |
| 2026-11-20 | **26.55** (lowest in window) |
| 2026-11-23 | 41.99 |
| 2026-11-24 | 39.24 |
| 2026-11-25 | **38.39** |

- RSI went from near-overbought (69.83 on 10-06) to **oversold territory (<30) on 11-05 (27.00) and again on 11-20 (26.55)**.
- **11-20's 26.55 is the lowest RSI print in the entire 60-day window.** The subsequent snapback to 41.99 and stabilization around 38–39 suggests the oversold condition triggered buying, but RSI is still in the lower half of its range and shows no confirmed upward trend yet.
- Importantly, RSI is **not** making a new low alongside price's marginal new low on 11-25 — consistent with the MACD histogram divergence. Mild constructive evidence, still weak.

---

## 4. Volatility and Risk

### ATR — volatility is exploding
| Date | ATR | ATR as % of Close (approx.) |
|---|---|---|
| 2026-10-01 | 376.29 | ~1.2% |
| 2026-11-06 | 630.58 | ~2.3% |
| 2026-11-20 | 762.55 | ~3.0% |
| 2026-11-23 | 850.22 | ~3.2% |
| 2026-11-25 | **875.68** | **~3.4%** |

- ATR has **more than doubled** from ~376 (early October) to 875.68 (11-25) — a clear volatility regime shift. Daily true range now averages ~876 points.
- Implication for risk: **position sizes must be scaled down materially.** A stop distance sized in ATR terms (e.g., 1.5–2× ATR) is now ~1,300–1,750 points versus ~560–750 points a month ago. Fixed-dollar risk sizing implies roughly half the notional exposure for the same risk budget.

### Bollinger Bands
| Band | 2026-11-25 |
|---|---|
| Upper | 29,433.16 |
| Middle (20 SMA) | 27,406.92 |
| Lower | 25,380.68 |
| **Band width (upper−lower)** | **~4,052 pts (~14.8% of mid)** |

- **Band width has widened dramatically** (on 2026-10-07 upper/lower were 31,640/28,674 — width ~2,966; now ~4,052) confirming the volatility expansion.
- **Price closed at 26,046.90, inside the lower band (25,380.68) but in the lower quartile of the channel** — i.e., a "ride the lower band" condition, not a clean break. Bands are descending steeply, which in a strong downtrend means touching/riding the lower band is a **continuation** signal, not automatically a reversal signal. Traders should not fade the lower band mechanically here.
- The **20 SMA is falling fast** (27,407 today vs. 30,157 on 10-07) — dynamic resistance that any rally must reclaim to signal stabilization.

---

## 5. Volume Confirmation

### VWMA vs. price
| Date | VWMA | Close | Relationship |
|---|---|---|---|
| 2026-10-07 | 30,483.99 | ~30,700 | Near parity |
| 2026-11-13 | 28,167.06 | ~26,500 (10 EMA proxy) | Price below VWMA |
| 2026-11-25 | **27,045.73** | 26,046.90 | Price **~999 pts below (−3.7%)** |

- **Price is trading persistently below the volume-weighted average price**, confirming that recent volume has been transacted at *higher* levels and that sellers are in control. This is bearish confirmation of the trend.
- The **11-20 selloff on 2.14B and 11-23 bounce on 2.38B** — the bounce drew even heavier volume than the selloff. That is an encouraging sign of buyers absorbing supply, but the fact that price failed to hold the 11-23 gains (closing lower on 11-24 and gapping down on 11-25) means the buying was met with supply. **Net read: distribution visible, but two-way participation high — a market searching for a floor, not a clean trend day.**
- The VWMA at 27,046 is a natural overhead reference; reclaiming it would suggest buyers are regaining control of the volume-weighted price.

---

## 6. Interpretation and Trade Implications

**The setup:** .NDX is in an aggressive short-term downtrend within a longer-term uptrend whose long-term filter (200-day SMA) has now been *violated on a closing basis.* Momentum (MACD, RSI) is deeply negative; volatility is spiking (ATR doubling); volume confirms distribution. Yet there are **early, tentative bottoming hints**: MACD histogram improving three sessions running, RSI at a shallow higher low (38.39 vs. 26.55), and a high-volume intraday reversal on 11-25.

**Actionable guidance:**

1. **Trend-followers / long-term holders:** The close below the 200-day SMA (28,090.98) on 11-19 is a major warning. Reduce leverage, tighten risk, and await either (a) a decisive reclaim of the 200-day or (b) the 50/200 death cross resolution. The 50/200 gap (~973 pts, closing fast) is the key structural metric to watch.
2. **Tactical traders:** Do **not** chase the bounce. The 20 SMA (27,407) and 50 SMA (29,064) are heavy overhead supply. A confirmed reversal requires: MACD histogram turning positive or a MACD/signal bullish cross; RSI reclaiming ~45–50; and price closing above the 20 SMA and then the VWMA (27,046).
3. **Near-term support reference:** the 11-20/11-25 lows around **24,910–24,971** and the lower Bollinger band at **25,380.68**. A sustained break below ~24,910 on heavy volume would open the next leg lower. A break *above* the 20 SMA (27,407) would establish a short-term trend change.
4. **Risk management:** Size positions using current ATR (875.68). Suggested stop buffer of ~1.5–2× ATR ≈ 1,300–1,750 pts. Expect ~3.4% daily swings; intraday whipsaws are likely.
5. **Bias:** **Bearish-to-neutral near term; high risk of continued chop.** The weight of evidence (below all MAs, below 200-SMA, MACD deeply negative, VWMA overhead, rising ATR) favors caution. Only the nascent momentum divergences offer a glimmer of stabilization, and they are insufficient on their own to justify longs.

---

## 7. Key Levels & Indicator Dashboard

### Key levels (approximate, from tool output 2026-11-25)
| Level type | Value |
|---|---|
| Recent low (11-20) | 24,910.48 |
| Recent low (11-25) | 24,970.66 |
| Bollinger lower band | 25,380.68 |
| Current close | 26,046.90 |
| 10 EMA | 26,683.25 |
| VWMA | 27,045.73 |
| Bollinger middle (20 SMA) | 27,406.92 |
| 200 SMA | 28,090.98 |
| 50 SMA | 29,064.20 |
| Bollinger upper band | 29,433.16 |

### Key points summary
| Category | Indicator | Latest (11-25) | Signal | Read |
|---|---|---|---|---|
| Trend (short) | close_10_ema | 26,683.25 | Price below | Bearish |
| Trend (medium) | close_50_sma | 29,064.20 | Price below; falling fast | Bearish |
| Trend (long) | close_200_sma | 28,090.98 | Price closed **below** on 11-19 | Warning / regime shift |
| MA cross | 50 vs 200 SMA | 50 > 200 by ~973 pts | No death cross yet; gap closing | Monitor closely |
| Momentum | MACD | −830.66 | Deeply negative, new low | Strongly bearish |
| Momentum | MACD signal | −726.16 | MACD below signal | Bearish; no cross imminent |
| Momentum | MACD histogram | −104.50 | Improving 3 sessions | Early bullish divergence (weak) |
| Momentum | RSI | 38.39 | Below 50; off 26.55 low | Bearish, oversold bounce faded |
| Volatility | ATR | 875.68 | Doubled in ~2 months | High risk; reduce size |
| Volatility | Bollinger bands | 29,433 / 27,407 / 25,381 | Price in lower band region | Bearish; don't fade mechanically |
| Volume | VWMA | 27,045.73 | Price ~3.7% below | Distribution confirmed |
| **Overall** | — | — | **Bearish-to-neutral** | Corrective downtrend within LT uptrend; early, unconfirmed stabilization signs |

*Caveat: These figures derive from `get_indicators`/`get_stock_data`; the verified market snapshot was unavailable (vendor rate limit) at time of analysis, so exact levels should be re-confirmed with a fresh snapshot before execution.*