#!/usr/bin/env python3
"""Test database connection and explore schema."""

import os
import sys
from dotenv import load_dotenv
import mysql.connector

# Load env from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def test_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE')
        )
        print("✅ Connected to database successfully!")
        
        cursor = conn.cursor()
        
        # Show tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n📊 Tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Count rows in main tables
        print("\n📈 Row counts:")
        for table in ['games', 'solutions', 'alternative_solutions', 'spots', 'queue', 'scores']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  - {table}: {count:,} rows")
            except Exception as e:
                print(f"  - {table}: Error - {e}")
        
        # Sample a solution
        print("\n🎴 Sample solution:")
        cursor.execute("SELECT id, solution, ev, top_comb, mid_comb, bot_comb FROM solutions LIMIT 1")
        row = cursor.fetchone()
        if row:
            print(f"  ID: {row[0]}")
            print(f"  Solution: {row[1]}")
            print(f"  EV: {row[2]}")
            print(f"  Top: {row[3]}")
            print(f"  Mid: {row[4]}")
            print(f"  Bot: {row[5]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
