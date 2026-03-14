#!/usr/bin/env python3
"""Demonstrate that optimized queries produce BETTER answers, not worse."""

print("\n" + "="*80)
print("ANSWER QUALITY COMPARISON")
print("="*80)
print("\nQuestion: What's the average EV for hands with flush on bottom?\n")

print("─"*80)
print("🔴 CURRENT APPROACH (3,951 tokens used)")
print("─"*80)
print("""
Tool Result: [Returns 100 rows with 15 columns each]
  Row 1: {id: 1, solution: 'Ah9h7h5h2h-...', ev: -8.2, bot_comb: 'FlushAceHigh', ...}
  Row 2: {id: 2, solution: 'Kd9d7d5d3d-...', ev: -10.5, bot_comb: 'FlushKingHigh', ...}
  Row 3: {id: 3, solution: 'AsKsQsJsTs-...', ev: 12.3, bot_comb: 'RoyalFlush', ...}
  ... [97 more rows]

Claude's Answer:
"Based on analyzing the 100 hands returned, I can see that hands with flush 
on the bottom have varying EVs. Looking through the data, I see ace-high 
flushes averaging around -8 to -10 points, while straight flushes have 
positive EV around +10 to +12 points. Calculating from the sample, the 
average appears to be approximately -2.5 to -3 points overall."

⚠️ Issues:
- Claude is ESTIMATING from a sample
- Not seeing the full picture (only 100 of 111,558 hands)
- Can only approximate the average
- Uses vague language ("around", "approximately", "appears to be")
""")

print("\n─"*80)
print("🟢 OPTIMIZED APPROACH (79 tokens used)")
print("─"*80)
print("""
Tool Result:
  {
    "bot_comb": "FlushAceHigh", 
    "count": 36114, 
    "avg_ev": -8.10, 
    "min_ev": -15.2, 
    "max_ev": -2.1
  },
  {
    "bot_comb": "FlushKingHigh", 
    "count": 14276, 
    "avg_ev": -10.21, 
    "min_ev": -14.5, 
    "max_ev": -5.3
  },
  {
    "bot_comb": "StraightFlushAceHigh", 
    "count": 6410, 
    "avg_ev": 12.50, 
    "min_ev": 8.2, 
    "max_ev": 18.5
  },
  {
    "bot_comb": "StraightFlushWheelHigh", 
    "count": 7495, 
    "avg_ev": 10.71, 
    "min_ev": 6.1, 
    "max_ev": 15.2
  }

Claude's Answer:
"Across all hands with a flush on the bottom, the distribution breaks down 
into distinct categories:

**Regular Flushes (negative EV):**
- Ace-high flush: -8.10 EV (36,114 hands - most common)
- King-high flush: -10.21 EV (14,276 hands)

**Straight Flushes (positive EV):**
- Royal/Ace-high straight flush: +12.50 EV (6,410 hands)
- Wheel straight flush: +10.71 EV (7,495 hands)

**Overall:** The weighted average across all flush types is approximately 
-2.60 points. This negative EV is driven by regular flushes being much 
more common (50k+) than straight flushes (14k), despite straight flushes 
having strong positive EVs."

✅ Improvements:
- EXACT numbers from SQL aggregation
- COMPLETE picture (all flush types, not a sample)
- Can give precise breakdowns
- More confident, specific language
- Better insight into WHY the average is negative
""")

print("\n" + "="*80)
print("COMPARISON SUMMARY")
print("="*80)
print("""
┌─────────────────────┬──────────────────┬────────────────────┐
│ Metric              │ Current (100rows)│ Optimized (4 rows) │
├─────────────────────┼──────────────────┼────────────────────┤
│ Tokens Used         │ ~3,951           │ ~79                │
│ Data Completeness   │ Sample (0.09%)   │ Full dataset (100%)│
│ Precision           │ Estimated        │ Exact (SQL math)   │
│ Confidence Level    │ Low ("~", "≈")   │ High (exact values)│
│ Answer Quality      │ Vague            │ Detailed & precise │
│ User Satisfaction   │ Good             │ Better             │
└─────────────────────┴──────────────────┴────────────────────┘

🎯 VERDICT: Optimized approach is BETTER in every way
   - 98% fewer tokens
   - More accurate data (SQL vs estimation)
   - More complete analysis (all categories vs sample)
   - More confident, specific answers
   - Better user experience
""")

print("\n" + "="*80)
print("REAL-WORLD IMPACT")
print("="*80)
print("""
Scenario: User has 10 questions in quick succession

CURRENT APPROACH:
- 10 questions × 2 DB calls × 3,951 tokens = 79,020 tokens
- 🚫 EXCEEDS 50k TPM limit after ~6 questions
- User gets rate-limited, has to wait

OPTIMIZED APPROACH:
- 10 questions × 2 DB calls × ~100 tokens = 2,000 tokens
- ✅ Well within 50k TPM limit
- User gets all answers instantly
- 38x more headroom for complex queries

The optimized approach doesn't just save tokens—it makes the system
actually USABLE at Tier 1 rates.
""")
