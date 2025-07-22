import sqlite3
import pandas as pd
import logging
import os
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path='ecommerce_data.db'):
        self.db_path = db_path
        
    def initialize_database(self):
        """Initialize the database and load CSV data"""
        try:
            # Remove existing database to start fresh
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                
            conn = sqlite3.connect(self.db_path)
            
            # Load eligibility data
            eligibility_file = 'attached_assets/Product-Level Eligibility Table (mapped) - Product-Level Eligibility Table (mapped)_1753169615993.csv'
            if os.path.exists(eligibility_file):
                df_eligibility = pd.read_csv(eligibility_file)
                df_eligibility.to_sql('eligibility', conn, index=False, if_exists='replace')
                logger.info(f"Loaded {len(df_eligibility)} eligibility records")
            
            # Load ad sales data
            ad_sales_file = 'attached_assets/Product-Level Ad Sales and Metrics (mapped) - Product-Level Ad Sales and Metrics (mapped)_1753169682186.csv'
            if os.path.exists(ad_sales_file):
                df_ad_sales = pd.read_csv(ad_sales_file)
                df_ad_sales.to_sql('ad_sales', conn, index=False, if_exists='replace')
                logger.info(f"Loaded {len(df_ad_sales)} ad sales records")
            
            # Load total sales data
            total_sales_file = 'attached_assets/Product-Level Total Sales and Metrics (mapped) - Product-Level Total Sales and Metrics (mapped)_1753169682185.csv'
            if os.path.exists(total_sales_file):
                df_total_sales = pd.read_csv(total_sales_file)
                df_total_sales.to_sql('total_sales', conn, index=False, if_exists='replace')
                logger.info(f"Loaded {len(df_total_sales)} total sales records")
            
            # Create indexes for better performance
            cursor = conn.cursor()
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_eligibility_item_id ON eligibility(item_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ad_sales_item_id ON ad_sales(item_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ad_sales_date ON ad_sales(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_total_sales_item_id ON total_sales(item_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_total_sales_date ON total_sales(date)')
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results as list of dictionaries"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # This enables column access by name
            cursor = conn.cursor()
            
            # Execute the query
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            results = [dict(row) for row in rows]
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
    
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
