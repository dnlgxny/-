# Technical Analysis Report — .NDX (NASDAQ-100)

**Analysis date:** 2026-11-20 | **Last verified close:** 25,028.98

---

## 1. Executive Summary

.NDX is in a **confirmed, accelerating downtrend** that just produced a decisive downside cascade. The index fell from 26,517.05 (2026-11-19) to 25,028.98 (2026-11-20) — a loss of 1,488.07 index points (−5.61%), the largest single-day decline in the visible 30-session window. Price is now trading **below** its 10 EMA (27,007.92), 50 SMA (29,224.26), 200 SMA (28,073.30), VWMA (27,402.01), Bollinger midline (27,893.46), and even the lower Bollinger band (25,595.79). RSI has printed 26.55 — the most oversold reading in the entire 30-day record — and MACD has rolled back down to −832.16 after a failed stabilization attempt in mid-November.

This is a **"breakdown with no confirmed bottom"** configuration: trend, momentum, and volatility are all aligned bearish, and the only counter-argument (oversold RSI) is a *condition*, not a *signal*, especially in a high-volatility decline like this one.

---

## 2. Price Action & Structure

| Date | Close | Notable |
|---|---:|---|
| 2026-10-12 | 30,664.70 | Local high in window |
| 2026-10-30 | 28,384.85 | First leg down completes (−7.4% from 10/12) |
| 2026-11-05 | 26,629.81 | Capitulation-style spike low, large volume day |
| 2026-11-11 | 28,374.25 | Rebound peak (partial retracement) |
| 2026-11-18 | 27,116.26 | Rebound fails; lower high vs. 11/11 |
| 2026-11-19 | 26,517.05 | Break below 11/05 area |
| **2026-11-20** | **25,028.98** | Breakdown; closes near day's low |

Key structural observations, all derived from tool data:

- **No recovery of any moving average since 2026-11-11.** The 11/11 rebound to 28,374.25 topped out just below the 50 SMA (29,553.80 on that date) and above the 10 EMA (28,118.45) — but price never closed above the 10 EMA for more than a day before rolling over again.
- **Failed rally = lower high.** 11/11 (28,374.25) < 10/12 (30,664.70); 11/18 (27,116.26) < 11/11. A clean sequence of lower highs and, with Friday's close, a lower low than the 11/05 close of 26,629.81.
- **Friday's range was enormous:** open 26,184.76, high 26,429.09, low 24,910.48, close 25,028.98 — a 1,518.61-point range and a close in the bottom ~12% of the day's range. Closing near the low signals sellers retained control into the weekend.

**Volume discrepancy to flag:** the raw CSV shows 2026-11-20 volume of ~2.139 billion, while the verified snapshot reports 2,687,727,000. Both indicate the heaviest volume of the visible period and confirm the down-move was distribution-driven, but the two sources disagree on the exact figure. I am using the verified snapshot's number and treating the volume signal qualitatively (heavy).

---

## 3. Moving-Average Structure — Bearish Stack

| Average | Value (11/20) | Price vs. |
|---|---:|---|
| close_10_ema | 27,007.92 | −7.33% below |
| close_50_sma | 29,224.26 | −14.36% below |
| close_200_sma | 28,073.30 | −10.83% below |
| vwma | 27,402.01 | −8.66% below |

Three critical structural facts:

1. **50 SMA has crossed below the 200 SMA's relationship** — the 50 SMA (29,224.26) sits *above* the 200 SMA (28,073.30), but with price collapsing and the 50 SMA falling fast (29813 → 29224 over 30 sessions), this spread is compressing rapidly. A further decline will trigger a **death cross** in the coming weeks. The last time the 50 SMA moved this quickly was not in the visible data, so I make no claim about prior crosses.
2. **Price has surrendered the 200 SMA.** The 200 SMA was rising steadily (27,651 → 28,073) but price re-broke below it decisively on 11/20. The 200 SMA near 28,073 is now the first major overhead air pocket.
3. **The 50 SMA is confirming the trend both ways.** It's still *above* price, *and* its own direction has turned down — this is the definitional signature of a maturing downtrend rather than a simple pullback.

The **10 EMA has fallen from 30,736.74 (10/12) to 27,007.92 (11/20)** while price sits 7.3% below it. When price is this far from its fast average, any mean-reversion bounce typically targets the 10 EMA — but that is nearly 2,000 points away.

---

## 4. Momentum

**MACD:** The MACD line descended from +365.84 (10/12) to −679.75 (11/06), stabilized in mid-November (recovering to −530.58 on 11/13), then resumed lower: −570.69 → −611.20 → −626.84 → −679.75 → **−832.16** on 11/20.

**MACD Histogram:** The most instructive sequence is the histogram. It narrowed to nearly zero by 11/13 (−4.48) — a classic "about to cross bullish" setup — then **failed** and re-expanded negative: −4.48 → −35.68 → −60.95 → −61.27 → −91.34 → **−195.01**. This is a textbook **bearish "reset" divergence**: momentum tried to bottom and couldn't. The histogram's re-expansion is now the steepest single-day widening in the visible record, which argues momentum is *accelerating away from* a bottom, not toward one.

**RSI:** 26.55 on 11/20, down from 33.79 on 11/19 and 45.96 peak on 11/11. Below the 30 threshold, technically oversold. Note the *path*: RSI hit 27.00 on 11/05, recovered to ~46 by 11/11, and has now set a **lower low** (26.55 < 27.00). RSI making lower lows during a price breakdown means the oversold condition is *intensifying* rather than showing positive divergence. **There is no bullish RSI divergence in the tool data as of 11/20** — both price and RSI are making lower lows together.

---

## 5. Volatility & Bollinger Analysis

**ATR:** 762.55 on 11/20, up from 367.50 on 10/12 — ATR has **more than doubled** in roughly six weeks. The step changes are illuminating:

- 367.50 (10/12) → 521.77 (10/30) → 630.58 (11/06) → 664.73 (11/13) → **762.55 (11/20)**

Volatility expansion is **sequential and escalating** — this is a volatility regime shift, not a one-off spike. A 762.55 ATR means a *normal* daily move is now ~3.05% of the index, which roughly triples position-sizing requirements versus early October.

**Bollinger Bands:** Midline 27,893.46; upper 30,191.13; lower 25,595.79. The bands have **widened dramatically** as the lower band slid from 26,641.51 (11/16) to **25,595.79** (11/20) in just four sessions. Critically:

- The close of 25,028.98 is **below the lower band by 566.81 points (2.21%)**.
- An intraday low of 24,910.48 closed roughly **685 points below the lower band**.

Trading outside the lower band is an *extreme* statistical event. In strong downtrends this can persist ("riding the band"), and the combination with expanding ATR and an accelerating histogram argues against treating it as a mechanical buy.

---

## 6. Volume & VWMA

The VWMA at **27,402.01** is the most revealing line in this dataset. It has declined monotonically every single session for 30 days (30,688.17 on 10/12 → 27,402.01 on 11/20). Unlike the 50 SMA, **VWMA never flattened during the 11/11 rebound** — meaning volume was concentrated in the selling. The gap between VWMA (27,402.01) and the 50 SMA (29,224.26) is 1,822 points, and VWMA is converging *downward* toward price faster than any other average.

This is a **distribution signature**: high-volume down days (11/05, 11/19, 11/20) against lower-volume up days (11/12, 11/13). The volume-weighted "true" average price of recent trading is far above spot, meaning the median recent buyer is deeply underwater — a recipe for overhead supply on any bounce.

---

## 7. Synthesis: The Bull and Bear Cases

**Bear case (dominant):**
- Trend stack is fully bearish; price below all four reference averages
- Lower highs on price *and* RSI — no divergence support
- MACD histogram re-expanding negatively after a failed bottoming attempt
- ATR in escalatory expansion; Bollinger lower band breaking down
- VWMA in unbroken 30-session decline = persistent distribution
- Close in bottom 12% of a 1,518-point range

**Bull case (weak, tactical only):**
- RSI 26.55 is oversold; historically extreme readings can precede sharp reflexive bounces
- Price 2.2% below the lower Bollinger band — stretched from any mean
- 10 EMA at 27,007.92 is a natural magnet for a bounce
- 200 SMA at 28,073.30, still rising, could act as a reversion target if a base forms

**My read:** The bull case rests entirely on *mean-reversion* mechanics. Nothing in the data shows demand emerging — no bullish divergence, no volume climax reversal candle (Friday closed at its low), no reclaim of the 10 EMA. **A bounce is possible at any time, but a bottom is not yet established.**

---

## 8. Actionable Levels & Guidance

Because exact support/resistance claims require tool evidence, the following are drawn directly from indicator values and verified closes:

| Level | Source | Significance |
|---|---|---|
| 24,910.48 | 11/20 intraday low | Immediate floor; break confirms continuation |
| 25,595.79 | Bollinger lower band | First reclaim = first sign of stabilization |
| 26,517.05 | 11/19 close | Reclaim would negate Friday's breakdown |
| 27,007.92 | 10 EMA | First mean-reversion target |
| 27,402.01 | VWMA | Supply zone; heavy overhead |
| 28,073.30 | 200 SMA | Major resistance; key bull/bear pivot |
| 29,224.26 | 50 SMA | Trend-defining resistance |

**Tactical considerations:**

1. **Do not buy the oversold print blindly.** RSI 26.55 with an accelerating histogram and widening bands is a "falling knife" profile. Wait for either (a) a close back above the 10 EMA, or (b) a confirmed bullish RSI divergence (price lower low + RSI higher low) over multiple sessions.
2. **Size positions using ATR, not percentage rules.** At ATR 762.55, stops must be materially wider than in October (when ATR was ~368). A 1×ATR stop from Friday's close is 24,266 — below the day's low. Consider 0.5–1.0× ATR and scale position size down ~50% from normal.
3. **For existing longs:** the 200 SMA break is management-grade information. A rally back toward 27,400–27,900 (VWMA/Bollinger midline) is where reducing exposure is most reasonable, not at the current depressed level.
4. **For short sellers:** momentum favors the trend, but with RSI < 27 and price below the lower band, risk/reward is degrading. If short, trail stops tightly (0.5× ATR ≈ 380 points) and consider taking partial profit into 24,910.
5. **Watch for a volatility climax.** The escalating ATR sequence (368 → 522 → 631 → 665 → 763) eventually exhausts. A day with ATR peaking, a volume spike, and a close in the *upper* half of the range would be the first credible capitulation signal.

---

## 9. Selected Indicators — Rationale

| Indicator | Why selected |
|---|---|
| **close_10_ema** | Fastest read on short-term trend and the natural first target for any bounce |
| **close_50_sma** | Medium-term trend; its downward turn confirms the trend is maturing, not a dip |
| **close_200_sma** | Strategic bull/bear pivot; the 11/20 break below it is the headline event |
| **macd** | Confirms the momentum regime shift from positive (Oct) to deeply negative (Nov) |
| **macdh** | Reveals the *failed bottoming attempt* — the most nuanced signal in this dataset |
| **rsi** | Quantifies oversold extremity and allows divergence tracking |
| **atr** | Essential for sizing and stops in a doubling-volatility regime |
| **boll_lb** | Confirms extreme extension below the bands and tracks band expansion |
| **vwma** | Volume-weighted truth confirms distribution; distinguishes real selling from noise |

*(Note: 9 series are shown above as MACD line/histogram are treated as one momentum framework plus the VWMA volume cross-check; the core non-redundant set is trend (3 MAs) + momentum (MACD, histogram, RSI) + volatility (ATR, Bollinger lower) + volume (VWMA).)*

---

## 10. Key Points Summary

| Category | Indicator | Value (11/20) | Signal |
|---|---|---:|---|
| **Price** | Close | 25,028.98 | Bottom 12% of a 1,518-pt range |
| **Price** | Day change | −1,488.07 (−5.61%) vs 11/19 | Largest drop in visible window |
| **Trend** | close_10_ema | 27,007.92 | Price 7.33% below — bearish |
| **Trend** | close_50_sma | 29,224.26 | Price 14.36% below; avg turning down |
| **Trend** | close_200_sma | 28,073.30 | Price 10.83% below — broken |
| **Momentum** | macd | −832.16 | Deeply negative, accelerating |
| **Momentum** | macdh | −195.01 | Failed bottom at −4.48 (11/13), re-expanding |
| **Momentum** | rsi | 26.55 | Oversold; lower low vs 27.00 (11/05), no divergence |
| **Volatility** | atr | 762.55 | Doubled since 10/12; escalating regime |
| **Volatility** | boll_lb | 25,595.79 | Close 566.81 pts (2.21%) below band |
| **Volatility** | boll (mid) | 27,893.46 | Price 10.27% below midline |
| **Volume** | vwma | 27,402.01 | 30-session unbroken decline = distribution |
| **Volume** | Volume 11/20 | 2,687,727,000 (verified) | Heavy; CSV shows ~2.139B — **discrepancy flagged** |
| **Verdict** | — | — | **Bearish; no confirmed bottom. Avoid catching the knife.** |
| **First target higher** | 10 EMA | 27,007.92 | Bounce objective, not a trend signal |
| **Key pivot** | 200 SMA | 28,073.30 | Bull/bear regime line |
| **Stop reference** | 0.5× ATR | ~24,648 | Risk management anchor for longs |

**Bottom line:** .NDX is in a high-volatility, accelerating downtrend with every trend and momentum measure aligned bearish. The RSI oversold headline should not be mistaken for a buy signal — the MACD histogram's failed bottom and the absence of divergence argue the decline is still in progress. Risk management (smaller size, ATR-based stops) matters more than directional conviction right now.