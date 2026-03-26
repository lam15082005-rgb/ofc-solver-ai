#!/usr/bin/env python3
"""
GTO Solution Database Populator

Generates random OFC hands, solves them using the C++ CFR solver,
and stores the results in MySQL. Designed to run autonomously in the background.
"""

import os
import sys
import time
import random
import signal
import traceback
from datetime import datetime

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(__file__))

import mysql.connector
from mysql.connector import Error
from solver import OFCSolver, GAME_VERSIONS, card_to_string, cards_to_string, action_to_solution, ACTIONS
from hand_parser import detect_hand_type, Card as HPCard
from poker.constants import NUM_REGULAR_CARDS, CARD_JOKER, RANKS, SUITS, NUM_SUITS
from poker.ofc.constants import NUM_HOLE_CARDS, NUM_DEAD_CARDS, NUM_JOKERS
from poker.ofc.utils import generate_deck
import numpy as np

# Configuration
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'ofc')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'ofcsolver2024')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'cfr')

# Solver settings
DEFAULT_GAME_VERSION = 2
DEFAULT_ITERATIONS = 1000
DEFAULT_TRAVERSALS = 10
TOP_N_ALTERNATIVES = 5

# How many solutions to generate
BATCH_SIZE = 10  # commit every N solutions
REPORT_INTERVAL = 50  # print progress every N solutions

# Graceful shutdown
shutdown_requested = False

def signal_handler(sig, frame):
    global shutdown_requested
    print(f"\n[{datetime.now()}] Shutdown requested. Finishing current solve...")
    shutdown_requested = True

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def get_db_connection():
    """Get a MySQL connection."""
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )


def card_value_to_hpcard(card_value):
    """Convert a numeric card value to a hand_parser Card for detect_hand_type."""
    if card_value == CARD_JOKER:
        return HPCard(rank='*', suit='*', is_joker=True)
    rank = card_value // NUM_SUITS
    suit = card_value % NUM_SUITS
    return HPCard(rank=RANKS[rank], suit=SUITS[suit], is_joker=False)


def generate_random_hand(game_version=2):
    """Generate a random 13-card hand and dead cards for the given game version."""
    game = GAME_VERSIONS[game_version]
    deck = generate_deck(game["players"], game["jokers"])
    
    random.shuffle(deck)
    
    hole_cards = deck[:NUM_HOLE_CARDS]
    dead_cards = deck[NUM_HOLE_CARDS:NUM_HOLE_CARDS + game["dead"]]
    
    return hole_cards, dead_cards


def solve_and_store(solver, conn, cursor, game_version=2, iterations=DEFAULT_ITERATIONS, traversals=DEFAULT_TRAVERSALS):
    """Generate a random hand, solve it, and store the result in the database."""
    game = GAME_VERSIONS[game_version]
    
    # Generate random hand
    hole_cards, dead_cards = generate_random_hand(game_version)
    
    hole_str = " ".join(card_to_string(c) for c in hole_cards)
    dead_str = " ".join(card_to_string(c) for c in dead_cards)
    
    # Solve
    result = solver.solve(
        hole_str, dead_str,
        game_version=game_version,
        iterations=iterations,
        traversals=traversals,
        top_n=TOP_N_ALTERNATIVES
    )
    
    # Insert main solution
    cursor.execute("""
        INSERT INTO solutions (hole_cards, dead_cards, solution, ev, frequency, 
                               top_comb, mid_comb, bot_comb, game_version, dead,
                               iterations, traversals)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        hole_str,
        dead_str,
        result.solution,
        result.ev,
        result.frequency,
        result.alternatives[0]["top"]["hand_type"] if result.alternatives else None,
        result.alternatives[0]["middle"]["hand_type"] if result.alternatives else None,
        result.alternatives[0]["bottom"]["hand_type"] if result.alternatives else None,
        game_version,
        dead_str,
        iterations,
        traversals
    ))
    
    solution_id = cursor.lastrowid
    
    # Insert alternatives
    for rank_order, alt in enumerate(result.alternatives):
        cursor.execute("""
            INSERT INTO alternative_solutions (solution_id, solution, ev, frequency,
                                               top_comb, mid_comb, bot_comb, rank_order)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            solution_id,
            alt["solution"],
            alt["ev"],
            alt["frequency"],
            alt["top"]["hand_type"],
            alt["middle"]["hand_type"],
            alt["bottom"]["hand_type"],
            rank_order
        ))
    
    return solution_id, result


def get_solution_count(conn):
    """Get current number of solutions in the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM solutions")
    count = cursor.fetchone()[0]
    cursor.close()
    return count


def main():
    global shutdown_requested
    
    print(f"[{datetime.now()}] OFC GTO Solution Populator starting...")
    print(f"  MySQL: {MYSQL_USER}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")
    print(f"  Game version: {DEFAULT_GAME_VERSION}")
    print(f"  Iterations: {DEFAULT_ITERATIONS}, Traversals: {DEFAULT_TRAVERSALS}")
    print(f"  Batch size: {BATCH_SIZE}, Report interval: {REPORT_INTERVAL}")
    print()
    
    # Initialize solver
    print("Initializing solver...")
    solver = OFCSolver()
    print("Solver ready!")
    
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    initial_count = get_solution_count(conn)
    print(f"Current solutions in database: {initial_count:,}")
    print(f"[{datetime.now()}] Starting solution generation...\n")
    
    total_generated = 0
    batch_count = 0
    start_time = time.time()
    batch_start = time.time()
    
    try:
        while not shutdown_requested:
            try:
                solution_id, result = solve_and_store(solver, conn, cursor, DEFAULT_GAME_VERSION)
                total_generated += 1
                batch_count += 1
                
                # Commit in batches
                if batch_count >= BATCH_SIZE:
                    conn.commit()
                    batch_count = 0
                
                # Report progress
                if total_generated % REPORT_INTERVAL == 0:
                    elapsed = time.time() - start_time
                    rate = total_generated / elapsed if elapsed > 0 else 0
                    total_in_db = initial_count + total_generated
                    print(f"[{datetime.now()}] Generated {total_generated:,} solutions "
                          f"({total_in_db:,} total in DB) | "
                          f"Rate: {rate:.1f} solutions/sec | "
                          f"Last EV: {result.ev:.4f}")
                    
            except Exception as e:
                print(f"[{datetime.now()}] Error solving hand: {e}")
                traceback.print_exc()
                # Rollback and reconnect if needed
                try:
                    conn.rollback()
                except:
                    pass
                try:
                    conn.close()
                except:
                    pass
                time.sleep(1)
                total_generated -= batch_count  # Adjust for rolled-back solutions
                batch_count = 0
                conn = get_db_connection()
                cursor = conn.cursor()
                continue
    
    finally:
        # Final commit
        if batch_count > 0:
            try:
                conn.commit()
            except:
                pass
        
        elapsed = time.time() - start_time
        rate = total_generated / elapsed if elapsed > 0 else 0
        total_in_db = initial_count + total_generated
        
        print(f"\n[{datetime.now()}] Populator shutting down.")
        print(f"  Generated {total_generated:,} solutions in {elapsed:.0f}s ({rate:.1f}/sec)")
        print(f"  Total solutions in database: {total_in_db:,}")
        
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
