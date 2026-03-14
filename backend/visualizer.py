"""Card and hand visualization for OFC poker."""

from typing import Optional
from hand_parser import Card, OFCHand, parse_cards, parse_ofc_hand, detect_hand_type, SUIT_SYMBOLS


# ANSI color codes
class Colors:
    RED = '\033[91m'
    BLACK = '\033[90m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    BG_WHITE = '\033[107m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'


def colorize_card(card: Card, use_colors: bool = True) -> str:
    """Return a colorized card string for terminal display."""
    symbol = SUIT_SYMBOLS.get(card.suit, card.suit)
    
    if not use_colors:
        prefix = "*" if card.is_joker else ""
        return f"{prefix}{card.rank}{symbol}"
    
    # Color based on suit
    if card.suit in ('h', 'd'):
        color = Colors.RED
    else:
        color = Colors.BLACK
    
    prefix = f"{Colors.YELLOW}*" if card.is_joker else ""
    return f"{prefix}{color}{card.rank}{symbol}{Colors.RESET}"


def render_card_box(card: Card, use_colors: bool = True) -> list[str]:
    """Render a single card as ASCII art box (5 lines)."""
    symbol = SUIT_SYMBOLS.get(card.suit, card.suit)
    rank = card.rank
    
    if card.suit in ('h', 'd'):
        color = Colors.RED if use_colors else ""
    else:
        color = Colors.BLACK if use_colors else ""
    reset = Colors.RESET if use_colors else ""
    
    joker_mark = "*" if card.is_joker else " "
    
    # Adjust for 10
    if rank == 'T':
        rank_display = "10"
        top_rank = f"{rank_display}"
        bot_rank = f"{rank_display}"
    else:
        top_rank = f"{rank} "
        bot_rank = f" {rank}"
    
    return [
        f"┌───┐",
        f"│{joker_mark}{color}{top_rank}{reset}│",
        f"│ {color}{symbol}{reset} │",
        f"│{color}{bot_rank}{reset}{joker_mark}│",
        f"└───┘",
    ]


def render_cards_row(cards: list[Card], use_colors: bool = True) -> str:
    """Render a row of cards as ASCII art."""
    if not cards:
        return ""
    
    # Get card boxes
    boxes = [render_card_box(c, use_colors) for c in cards]
    
    # Combine horizontally
    lines = []
    for i in range(5):
        line = " ".join(box[i] for box in boxes)
        lines.append(line)
    
    return "\n".join(lines)


def render_ofc_hand(hand: OFCHand, use_colors: bool = True) -> str:
    """Render a full OFC hand with all three rows."""
    output = []
    
    # Detect hand types
    top_type = detect_hand_type(hand.top)
    mid_type = detect_hand_type(hand.middle)
    bot_type = detect_hand_type(hand.bottom)
    
    # Header
    if use_colors:
        output.append(f"{Colors.BOLD}═══════════════════════════════════════{Colors.RESET}")
    else:
        output.append("═" * 39)
    
    # Top row
    label = f"TOP ({top_type})"
    if use_colors:
        output.append(f"{Colors.BLUE}{label}{Colors.RESET}")
    else:
        output.append(label)
    output.append(render_cards_row(hand.top, use_colors))
    output.append("")
    
    # Middle row
    label = f"MIDDLE ({mid_type})"
    if use_colors:
        output.append(f"{Colors.GREEN}{label}{Colors.RESET}")
    else:
        output.append(label)
    output.append(render_cards_row(hand.middle, use_colors))
    output.append("")
    
    # Bottom row
    label = f"BOTTOM ({bot_type})"
    if use_colors:
        output.append(f"{Colors.YELLOW}{label}{Colors.RESET}")
    else:
        output.append(label)
    output.append(render_cards_row(hand.bottom, use_colors))
    
    # Footer
    if use_colors:
        output.append(f"{Colors.BOLD}═══════════════════════════════════════{Colors.RESET}")
    else:
        output.append("═" * 39)
    
    return "\n".join(output)


def render_solution(solution_str: str, use_colors: bool = True) -> str:
    """Parse and render a solution string from the database."""
    hand = parse_ofc_hand(solution_str)
    if hand:
        return render_ofc_hand(hand, use_colors)
    return f"Could not parse solution: {solution_str}"


def render_cards_inline(cards: list[Card], use_colors: bool = True) -> str:
    """Render cards in a single line with colors."""
    return " ".join(colorize_card(c, use_colors) for c in cards)


def render_comparison(solution1: str, solution2: str, 
                      ev1: float = None, ev2: float = None,
                      use_colors: bool = True) -> str:
    """Render two solutions side by side for comparison."""
    hand1 = parse_ofc_hand(solution1)
    hand2 = parse_ofc_hand(solution2)
    
    if not hand1 or not hand2:
        return "Could not parse solutions for comparison"
    
    output = []
    
    # Headers
    header1 = f"Solution 1" + (f" (EV: {ev1:+.2f})" if ev1 is not None else "")
    header2 = f"Solution 2" + (f" (EV: {ev2:+.2f})" if ev2 is not None else "")
    
    if use_colors:
        output.append(f"{Colors.BOLD}{header1:^30} │ {header2:^30}{Colors.RESET}")
    else:
        output.append(f"{header1:^30} │ {header2:^30}")
    
    output.append("─" * 30 + "─┼─" + "─" * 30)
    
    # Compare each row
    for row_name, cards1, cards2 in [
        ("Top", hand1.top, hand2.top),
        ("Middle", hand1.middle, hand2.middle),
        ("Bottom", hand1.bottom, hand2.bottom)
    ]:
        type1 = detect_hand_type(cards1)
        type2 = detect_hand_type(cards2)
        
        line1 = render_cards_inline(cards1, use_colors)
        line2 = render_cards_inline(cards2, use_colors)
        
        output.append(f"{row_name}: {line1:^24} │ {line2:^24}")
        output.append(f"      ({type1:^18}) │ ({type2:^18})")
    
    output.append("─" * 61)
    
    return "\n".join(output)


# HTML rendering for web frontend
def render_card_html(card: Card) -> str:
    """Render a card as HTML."""
    symbol = SUIT_SYMBOLS.get(card.suit, card.suit)
    color = "red" if card.suit in ('h', 'd') else "black"
    joker_class = "joker" if card.is_joker else ""
    
    return f'''<span class="card {color} {joker_class}">
        <span class="rank">{card.rank}</span>
        <span class="suit">{symbol}</span>
    </span>'''


def render_ofc_hand_html(hand: OFCHand) -> str:
    """Render a full OFC hand as HTML."""
    rows = []
    
    for row_name, cards in [("top", hand.top), ("middle", hand.middle), ("bottom", hand.bottom)]:
        hand_type = detect_hand_type(cards)
        cards_html = " ".join(render_card_html(c) for c in cards)
        rows.append(f'''
        <div class="ofc-row {row_name}">
            <div class="row-label">{row_name.upper()} <span class="hand-type">({hand_type})</span></div>
            <div class="cards">{cards_html}</div>
        </div>''')
    
    return f'''<div class="ofc-hand">{"".join(rows)}</div>'''


def get_card_css() -> str:
    """Return CSS for card styling."""
    return '''
    .ofc-hand {
        font-family: 'Courier New', monospace;
        background: #1a1a2e;
        padding: 20px;
        border-radius: 10px;
        display: inline-block;
    }
    .ofc-row {
        margin: 10px 0;
    }
    .row-label {
        color: #888;
        font-size: 12px;
        margin-bottom: 5px;
    }
    .hand-type {
        color: #666;
    }
    .card {
        display: inline-block;
        background: white;
        border-radius: 5px;
        padding: 8px 6px;
        margin: 2px;
        font-weight: bold;
        font-size: 16px;
        min-width: 30px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .card.red { color: #d32f2f; }
    .card.black { color: #212121; }
    .card.joker { 
        background: linear-gradient(135deg, #ffd700, #ffeb3b);
        border: 2px solid #ff9800;
    }
    .suit { font-size: 14px; }
    '''


# Test function
if __name__ == "__main__":
    # Test visualization
    test_solution = "Jh4s3h-As5c4c3c2h-KdJd9d7d3d"
    print(render_solution(test_solution))
    
    print("\n" + "="*50 + "\n")
    
    # Test with jokers
    joker_solution = "*Ad4s-7s6h5h4c3c-AsKhQsJdTd"
    print(render_solution(joker_solution))
