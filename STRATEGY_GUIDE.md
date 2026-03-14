# OFC Solver AI - Strategic Knowledge System

## Overview

The OFC Solver AI now has **built-in strategic knowledge** that allows it to provide expert advice for common hand patterns **without needing exact cards**.

This is perfect for questions like:
- "If I have 5 pairs and 3 singles, how should I play it?"
- "What's the best way to distribute trips and pairs?"
- "How do I play a flush draw?"

## How It Works

The system has two modes:

### 1. **Strategic Pattern Advice** (New!)
- **When to use:** General questions about hand patterns
- **No cards needed:** Just describe the pattern
- **Instant response:** No solver computation required
- **Expert guidance:** Based on proven strategic principles

### 2. **Exact Hand Solving** (Original)
- **When to use:** You have specific 13 cards
- **Cards required:** Must provide exact cards
- **GTO solution:** Uses CFR solver for mathematically optimal play
- **Detailed analysis:** EVs, frequencies, alternatives

## Available Patterns

The system knows about these common patterns:

1. **5 Pairs + 3 Singles** ✅
   - Distribution: Pair / Two-Pair / Two-Pair (highest pair on top)
   - High royalty potential (QQ+ on top)
   - Very low foul risk

2. **4 Pairs + 5 Singles**
   - Distribution: High card / Two-Pair / Two-Pair
   - Medium royalty potential
   - Low foul risk

3. **6 Pairs + 1 Single**
   - Distribution: Pair / Two-Pair / Trips or Two-Pair
   - High royalty potential
   - Low foul risk

4. **3 Trips**
   - Distribution: Trips / Trips / Trips (lowest to highest)
   - Extreme royalty potential
   - No foul risk

5. **Trips + Pairs**
   - Distribution: Pair / Trips or Two-Pair / Full House
   - Very high royalty potential (full house on bottom)
   - Low-medium foul risk

6. **Straight Draw**
   - Focus on completing straight on bottom
   - High royalty potential
   - Medium foul risk

7. **Flush Draw**
   - Always put flush on bottom (if possible)
   - High royalty potential
   - Medium foul risk

8. **High Cards Only**
   - Descending distribution (highest on top)
   - Low royalty potential
   - High foul risk

9. **Low Cards**
   - Focus on not fouling
   - Very low royalty potential
   - High foul risk

## Example Usage

### Before (Required exact cards):
```
User: "I have pairs but not sure how to arrange them"
Agent: "Please provide your 13 cards so I can solve it for you"
```

### After (Pattern-based advice):
```
User: "If I have 5 pairs and 3 singles, how should I play it?"
Agent: "With 5 pairs and 3 singles, the optimal strategy is:

Put your HIGHEST pair on top (AA > KK > QQ for max royalties)
Split remaining pairs BALANCED to create THREE STRONG HANDS
Don't dump all strength into bottom - you need to win middle too!

Key insight: AAx-QQ99x-KK77x beats AAx-9977x-KKQQx because the middle
is much stronger (QQ99 vs 9977) while KK77 still wins most bottoms.

For example:
- AAx-QQ99x-KK77x (AA top for 9pts, balanced two-pairs = 3 strong hands)
- KKx-QQ88x-AA99x (KK top for 8pts, balanced middle/bottom)

Royalty potential: High (QQ=7, KK=8, AA=9 points on top)
Foul risk: Very low (pairs guarantee ascending hand strength)"
```

## Strategic Principles

The system also has deep knowledge of:

### Royalty Maximization
- Top royalties: Pairs 66+ and trips (highest multipliers)
- Middle royalties: Trips, straights, flushes, full houses, quads
- Bottom royalties: Straights, flushes, full houses, quads

Key insight: **Middle royalties are often more valuable** than bottom for the same hand type (flush in middle = 12 pts vs 4 pts on bottom).

### Foul Avoidance
- Never let top > middle or middle > bottom
- Safe structures: Pair/2P/2P, High/Pair/2P, Pair/Trips/FH
- Pairs are your friend (pair/2pair/2pair never fouls if ordered correctly)

### Joker Strategy (Versions 2, 4-7)
- Complete premium hands (quads, straight flushes)
- Middle quads = highest royalty value (20-35 pts)
- Top trips = also very high (10-22 pts)

### EV Thinking
- Balance royalty chasing vs foul avoidance
- Safe structures have positive EV floor
- Middle royalties often the highest EV target

## Implementation

### New Tool: `get_strategy`

The agent now has a `get_strategy` tool that:
- Accepts natural language pattern descriptions
- Returns expert strategic advice
- Works without exact cards
- Provides examples and reasoning

### Backend Files

- `backend/strategy.py` - Strategic knowledge base (9 patterns, principles, royalty tables)
- `backend/prompts.py` - Updated to prioritize strategy for pattern questions
- `backend/agent.py` - Added strategy tool handler

### Testing

Run the tests to verify:

```bash
cd backend

# Test strategy module
python3 test_strategy.py

# Test agent integration
python3 test_agent_strategy.py
```

## Next Steps

### Expand Pattern Library
Add more patterns:
- Quads + other cards
- Two trips + singles
- Straight flush draws
- Specific pair/trip combinations

### Add Opponent Modeling
- Adjust strategy based on opponent tendencies
- Multi-player considerations
- Dead card implications

### Interactive Learning
- Let users submit their own patterns
- Learn from solved hands to identify new patterns
- Update strategies based on usage

## Benefits

1. **Faster responses** - No solver needed for pattern questions
2. **Better learning** - Users understand WHY, not just WHAT
3. **Fills knowledge gaps** - Answers questions like "what if..." without exact cards
4. **Educational** - Teaches strategic thinking, not just solutions
5. **Scalable** - Easy to add new patterns and principles

## Conclusion

The strategic knowledge system transforms the OFC Solver from a "give me cards, I'll solve them" tool into a **true poker coach** that can teach strategy, answer hypotheticals, and explain the reasoning behind optimal play.

Your example of "5 pairs and 3 singles → how to play it" is now trivially answered without needing exact cards!
