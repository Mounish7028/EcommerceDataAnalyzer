import psycopg2
import psycopg2.extras
import pandas as pd
import logging
import os
from typing import List, Dict, Any
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.database_url = os.environ.get("DATABASE_URL")
        if not self.database_url:
            # Fallback to SQLite for development
            self.database_url = "sqlite:///ecommerce_data.db"
            self.use_postgres = False
            logger.info("Using SQLite database (PostgreSQL URL not found)")
        else:
            self.use_postgres = True
            logger.info("Using PostgreSQL database")
        
        self.engine = create_engine(self.database_url)
        
    def initialize_database(self):
        """Initialize the database and load CSV data"""
        try:
            # Load eligibility data
            eligibility_file = 'attached_assets/Product-Level Eligibility Table (mapped) - Product-Level Eligibility Table (mapped)_1753169615993.csv'
            if os.path.exists(eligibility_file):
                df_eligibility = pd.read_csv(eligibility_file)
                df_eligibility.to_sql('eligibility', self.engine, index=False, if_exists='replace')
                logger.info(f"Loaded {len(df_eligibility)} eligibility records")
            
            # Load ad sales data
            ad_sales_file = 'attached_assets/Product-Level Ad Sales and Metrics (mapped) - Product-Level Ad Sales and Metrics (mapped)_1753169682186.csv'
            if os.path.exists(ad_sales_file):
                df_ad_sales = pd.read_csv(ad_sales_file)
                df_ad_sales.to_sql('ad_sales', self.engine, index=False, if_exists='replace')
                logger.info(f"Loaded {len(df_ad_sales)} ad sales records")
            
            # Load total sales data
            total_sales_file = 'attached_assets/Product-Level Total Sales and Metrics (mapped) - Product-Level Total Sales and Metrics (mapped)_1753169682185.csv'
            if os.path.exists(total_sales_file):
                df_total_sales = pd.read_csv(total_sales_file)
                df_total_sales.to_sql('total_sales', self.engine, index=False, if_exists='replace')
                logger.info(f"Loaded {len(df_total_sales)} total sales records")
            
            # Create query history table (persistent across restarts)
            with self.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS query_history (
                        id SERIAL PRIMARY KEY,
                        question TEXT NOT NULL,
                        sql_query TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        response_summary TEXT,
                        execution_time_ms INTEGER
                    )
                """))
                conn.commit()
                
                # Create indexes for better performance
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_eligibility_item_id ON eligibility(item_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ad_sales_item_id ON ad_sales(item_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ad_sales_date ON ad_sales(date)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_total_sales_item_id ON total_sales(item_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_total_sales_date ON total_sales(date)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_history_created_at ON query_history(created_at)"))
                conn.commit()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results as list of dictionaries"""
        try:
            with self.engine.connect() as conn:
                from sqlalchemy import text
                result = conn.execute(text(query))
                rows = result.fetchall()
                
                # Convert to list of dictionaries
                if rows:
                    columns = result.keys()
                    results = [dict(zip(columns, row)) for row in rows]
                else:
                    results = []
                
                return results
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
    
    def save_query_history(self, question: str, sql_query: str, response_summary: str, execution_time_ms: int = None):
        """Save query to history table"""
        try:
            with self.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("""
                    INSERT INTO query_history (question, sql_query, response_summary, execution_time_ms)
                    VALUES (:question, :sql_query, :response_summary, :execution_time_ms)
                """), {
                    'question': question,
                    'sql_query': sql_query,
                    'response_summary': response_summary[:500] if response_summary else None,  # Limit summary length
                    'execution_time_ms': execution_time_ms
                })
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error saving query history: {str(e)}")
    
    def get_query_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get query history with basic details"""
        try:
            with self.engine.connect() as conn:
                from sqlalchemy import text
                result = conn.execute(text("""
                    SELECT 
                        id,
                        question,
                        SUBSTRING(response_summary FROM 1 FOR 100) as summary,
                        created_at,
                        execution_time_ms
                    FROM query_history 
                    ORDER BY created_at DESC 
                    LIMIT :limit
                """), {'limit': limit})
                
                rows = result.fetchall()
                
                if rows:
                    columns = result.keys()
                    results = [dict(zip(columns, row)) for row in rows]
                else:
                    results = []
                
                return results
                
        except Exception as e:
            logger.error(f"Error getting query history: {str(e)}")
            return []
    
    def get_query_detail(self, query_id: int) -> Dict[str, Any]:
        """Get full details of a specific query"""
        try:
            with self.engine.connect() as conn:
                from sqlalchemy import text
                result = conn.execute(text("""
                    SELECT * FROM query_history WHERE id = :id
                """), {'id': query_id})
                
                row = result.fetchone()
                
                if row:
                    columns = result.keys()
                    return dict(zip(columns, row))
                else:
                    return {}
                
        except Exception as e:
            logger.error(f"Error getting query detail: {str(e)}")
            return {}
    
    def get_schema_info(self) -> str:
        """Get database schema information for AI context"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            schema_info = []
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                column_info = []
                for col in columns:
                    column_info.append(f"{col[1]} ({col[2]})")
                
                schema_info.append(f"Table: {table_name}")
                schema_info.append(f"Columns: {', '.join(column_info)}")
                schema_info.append("")
            
            conn.close()
            return "\n".join(schema_info)
            
        except Exception as e:
            logger.error(f"Error getting schema info: {str(e)}")
            return "Schema information not available"
