"""Database connection and query execution."""

import os
from contextlib import contextmanager
from typing import Any
import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        self.config = {
            'host': os.getenv('MYSQL_HOST', 'ofc.coach'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'user': os.getenv('MYSQL_USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DATABASE', 'cfr'),
        }
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = mysql.connector.connect(**self.config)
            yield conn
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    def execute_query(self, query: str, params: tuple = None, max_rows: int = 100) -> dict[str, Any]:
        """
        Execute a SQL query and return results.
        
        Returns:
            dict with 'columns', 'rows', 'row_count', and 'truncated' keys
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                # Check if it's a SELECT query
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchmany(max_rows + 1)
                    
                    truncated = len(rows) > max_rows
                    if truncated:
                        rows = rows[:max_rows]
                    
                    return {
                        'success': True,
                        'columns': columns,
                        'rows': [list(row) for row in rows],
                        'row_count': len(rows),
                        'truncated': truncated,
                    }
                else:
                    # Non-SELECT query (INSERT, UPDATE, etc.)
                    conn.commit()
                    return {
                        'success': True,
                        'affected_rows': cursor.rowcount,
                    }
                    
        except Error as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': e.errno if hasattr(e, 'errno') else None,
            }
    
    def get_schema_summary(self) -> str:
        """Get a summary of the database schema for the LLM."""
        schema_info = []
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get tables
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                
                col_info = []
                for col in columns:
                    name, dtype, null, key, default, extra = col
                    key_str = f" [{key}]" if key else ""
                    col_info.append(f"    - {name}: {dtype}{key_str}")
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                schema_info.append(f"  {table} ({count:,} rows):\n" + "\n".join(col_info))
        
        return "Database Schema:\n" + "\n\n".join(schema_info)


# Singleton instance
db = Database()
