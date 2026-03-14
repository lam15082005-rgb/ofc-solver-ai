# Data-Driven OFC Strategy Insights

## Source Data
- **327,673 GTO-solved hands** from CFR (Counterfactual Regret Minimization) solver
- All insights backed by empirical EV (Expected Value) data

---

## Key Insight #1: Top Pair Selection

**Always put your HIGHEST pair on top.**

| Top Pair | Avg EV | vs AA |
|----------|--------|-------|
| AA | -1.19 | — |
| KK | -4.40 | 3.2 worse |
| QQ | -5.45 | 4.3 worse |
| JJ | -7.28 | 6.1 worse |
| TT | -7.65 | 6.5 worse |

**Why it matters:** The 3.2 EV difference between AA and KK is like winning an extra row every ~3 hands. This is HUGE over many hands.

---

## Key Insight #2: Trips Placement (CRITICAL!)

**Put trips on TOP whenever possible.**

| Position | Avg EV | vs Top |
|----------|--------|--------|
| Trips on TOP | +25.16 | — |
| Trips in MIDDLE | -8.49 | 33.6 worse |
| Trips on BOTTOM | -16.58 | 41.7 worse |

**Why it matters:** Top row trips royalties (10-22 points depending on rank) dominate the EV calculation. A 33+ EV swing is enormous!

---

## Key Insight #3: Premium Hands in Middle = MULTIPLE Premium Hands

**This is CORRELATION, not a strategy recommendation!**

| Hand Type | MIDDLE EV | BOTTOM EV |
|-----------|-----------|-----------|
| Quads | +42.83 | +5.86 |
| Full House | +10.50 | -8.69 |
| Flush | +0.65 | -9.72 |

**Why the EV difference?** Because middle must be WEAKER than bottom!
- If flush is in middle → bottom must be full house, quads, or straight flush
- So "flush in middle" really means "I have TWO premium hands"
- The high EV comes from having multiple premium hands, not from placement

**Correct interpretation:**
- ONE premium hand → it goes on bottom (only valid option)
- TWO premium hands → weaker in middle, stronger on bottom (forced by rules)
- The data shows that having multiple premium hands is very profitable

**Royalty note:** Yes, middle royalties are higher (flush=12pts vs 4pts), but you can only exploit this when your bottom is even stronger than a flush!

---

## Key Insight #4: Bottom Row Reality Check

**Only premium hands have POSITIVE EV on bottom:**

| Hand Type | Bottom EV |
|-----------|-----------|
| Five of a Kind (jokers) | +20.41 |
| Straight Flush | +5 to +12 |
| Four of a Kind | +5.86 |
| Full House | **-8.69** |
| Flush | **-9.72** |
| Straight | **-11.00** |

**Why it matters:** Flushes and straights on bottom are NEGATIVE EV! Don't chase bottom strength at the expense of middle/top value.

---

## Key Insight #5: Three Strong Hands Principle

**Balanced structures beat "dump everything into bottom".**

### Example: 5 Pairs (AA, KK, QQ, 99, 77)

**WRONG:** KK-9977-AAQQ
- Top: KK (8 royalty pts)
- Middle: 9977 (weak - loses rows often)
- Bottom: AAQQ (very strong)
- **Problem:** Weak middle loses too many row matchups

**RIGHT:** AA-QQ99-KK77
- Top: AA (9 royalty pts, +1 over KK!)
- Middle: QQ99 (competitive - wins rows)
- Bottom: KK77 (still wins most matchups)
- **Result:** +1 royalty point AND better overall row win rate

---

## Summary: GTO Hierarchy of Priorities

Based on the data, here's the optimal decision hierarchy:

1. **Maximize top royalties** (AA > KK > QQ, trips on top = +25 EV)
2. **Build THREE competitive hands** (don't sacrifice middle for bottom)
3. **Multiple premium hands are very profitable** (if you have them, structure correctly)
4. **Don't foul** (structure must be valid: top < middle < bottom)

---

## Implementation

These insights are now embedded in:
- `backend/strategy_data.py` - Raw EV data and insights
- `backend/strategy.py` - Pattern-based strategic advice
- `backend/prompts.py` - AI agent system prompt
- AI agent uses these insights to explain WHY plays are optimal

---

## How to Use

### Ask the AI:
- "What's the EV difference between AA and KK on top?"
- "Should I put trips on top or bottom?"
- "Is it better to have a flush in middle or bottom?"
- "How should I distribute 5 pairs and 3 singles?"

### The AI will:
1. Provide the data-backed answer
2. Explain the EV reasoning
3. Give concrete examples
4. Show the strategic principle

---

*All data derived from CFR solver analysis of 327,673 hands.*
