"""Database connection and query execution. Supports SQLite and MySQL."""

import os
import sqlite3
from contextlib import contextmanager
from typing import Any


class DatabaseError(Exception):
    """Custom database error."""
    def __init__(self, msg, errno=None):
        super().__init__(msg)
        self.errno = errno


class Database:
    def __init__(self):
        # Check for SQLite first (preferred for simple deployments)
        self._sqlite_path = os.getenv('SQLITE_DB_PATH', '')
        self._use_sqlite = bool(self._sqlite_path)
        
        if self._use_sqlite:
            self._available = True
            print(f"✅ Using SQLite database: {self._sqlite_path}")
        else:
            # Fall back to MySQL
            self._mysql_config = {
                'host': os.getenv('MYSQL_HOST', 'ofc.coach'),
                'port': int(os.getenv('MYSQL_PORT', 3306)),
                'user': os.getenv('MYSQL_USER'),
                'password': os.getenv('MYSQL_PASSWORD'),
                'database': os.getenv('MYSQL_DATABASE', 'cfr'),
            }
            self._available = bool(self._mysql_config['user'] and self._mysql_config['password'])
            if not self._available:
                print("⚠️  Database not configured. Set SQLITE_DB_PATH or MYSQL_USER/MYSQL_PASSWORD.")
    
    @property
    def available(self) -> bool:
        return self._available

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        if not self._available:
            raise DatabaseError("Database not configured. Set SQLITE_DB_PATH or MYSQL_USER and MYSQL_PASSWORD.")
        
        conn = None
        try:
            if self._use_sqlite:
                conn = sqlite3.connect(self._sqlite_path)
                conn.row_factory = sqlite3.Row
                yield conn
            else:
                import mysql.connector
                conn = mysql.connector.connect(**self._mysql_config)
                yield conn
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    def execute_query(self, query: str, params: tuple = None, max_rows: int = 100) -> dict[str, Any]:
        """Execute a SQL query and return results."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchmany(max_rows + 1)
                    
                    truncated = len(rows) > max_rows
                    if truncated:
                        rows = rows[:max_rows]
                    
                    rows = [list(row) for row in rows]
                    
                    return {
                        'success': True,
                        'columns': columns,
                        'rows': rows,
                        'row_count': len(rows),
                        'truncated': truncated,
                    }
                else:
                    conn.commit()
                    return {
                        'success': True,
                        'affected_rows': cursor.rowcount,
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': getattr(e, 'errno', None),
            }
    
    def get_schema_summary(self) -> str:
        """Get a summary of the database schema for the LLM."""
        schema_info = []
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if self._use_sqlite:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    
                    col_info = []
                    for col in columns:
                        name = col[1]
                        dtype = col[2]
                        pk = " [PRI]" if col[5] else ""
                        col_info.append(f"    - {name}: {dtype}{pk}")
                    
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    
                    schema_info.append(f"  {table} ({count:,} rows):\n" + "\n".join(col_info))
            else:
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
                    
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    
                    schema_info.append(f"  {table} ({count:,} rows):\n" + "\n".join(col_info))
        
        return "Database Schema:\n" + "\n\n".join(schema_info)


# Singleton instance
db = Database()
