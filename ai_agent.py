import os
import logging
import json
import re
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class AIAgent:
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.schema_context = self._get_schema_context()
    
    def _get_schema_context(self) -> str:
        """Define the database schema context for the AI"""
        return """
        Database Schema:
        
        Table: eligibility
        Columns: eligibility_datetime_utc (TEXT), item_id (INTEGER), eligibility (TEXT), message (TEXT)
        Description: Contains product eligibility status for advertising
        
        Table: ad_sales
        Columns: date (TEXT), item_id (INTEGER), ad_sales (REAL), impressions (INTEGER), ad_spend (REAL), clicks (INTEGER), units_sold (INTEGER)
        Description: Contains advertising performance metrics and sales data
        
        Table: total_sales
        Columns: date (TEXT), item_id (INTEGER), total_sales (REAL), total_units_ordered (INTEGER)
        Description: Contains total sales performance data
        
        Key Business Metrics:
        - RoAS (Return on Ad Spend) = ad_sales / ad_spend
        - CPC (Cost Per Click) = ad_spend / clicks
        - Conversion Rate = units_sold / clicks
        - CTR (Click Through Rate) = clicks / impressions
        """
    
    def generate_sql_query(self, question: str) -> Optional[str]:
        """Generate SQL query from natural language question"""
        try:
            system_prompt = f"""
            You are an expert SQL query generator for an e-commerce analytics database.
            
            {self.schema_context}
            
            Rules:
            1. Generate ONLY the SQL query, no explanations
            2. Use proper SQL syntax for SQLite
            3. Handle date formats as TEXT
            4. For RoAS calculations: ad_sales / ad_spend (handle division by zero)
            5. For CPC calculations: ad_spend / clicks (handle division by zero)
            6. Use appropriate JOINs when data from multiple tables is needed
            7. Return meaningful column names
            8. Limit results to reasonable numbers (use LIMIT when appropriate)
            9. Handle NULL values appropriately
            10. Use CASE statements for calculations that might involve division by zero
            
            Common question patterns:
            - "Total sales" = SUM(total_sales) from total_sales table
            - "RoAS" = SUM(ad_sales) / SUM(ad_spend) from ad_sales table
            - "Highest CPC" = MAX(ad_spend / clicks) from ad_sales table where clicks > 0
            - "Eligible products" = COUNT(*) from eligibility where eligibility = 'TRUE'
            """
            
            user_prompt = f"""
            Generate a SQL query for this question: "{question}"
            
            Return only the SQL query, nothing else.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=f"{system_prompt}\n\n{user_prompt}")])
                ]
            )
            
            if not response.text:
                logger.error("Empty response from Gemini")
                return None
                
            # Extract SQL query from response
            sql_query = self._extract_sql_query(response.text)
            logger.info(f"Generated SQL query: {sql_query}")
            
            return sql_query
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {str(e)}")
            return None
    
    def _extract_sql_query(self, response_text: str) -> str:
        """Extract clean SQL query from AI response"""
        # Remove markdown code blocks if present
        response_text = re.sub(r'```sql\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        
        # Remove extra whitespace and newlines
        response_text = response_text.strip()
        
        # Ensure it ends with semicolon
        if not response_text.endswith(';'):
            response_text += ';'
            
        return response_text
    
    def generate_response(self, question: str, sql_query: str, results: List[Dict[str, Any]]) -> str:
        """Generate human-readable response from query results"""
        try:
            system_prompt = """
            You are an expert e-commerce data analyst. Your job is to interpret SQL query results and provide clear, business-friendly explanations.
            
            Guidelines:
            1. Provide clear, concise answers
            2. Include relevant numbers and percentages
            3. Explain what the data means in business terms
            4. If results are empty, explain what that means
            5. For financial metrics, format numbers appropriately
            6. Highlight key insights and actionable information
            7. Be conversational but professional
            """
            
            results_text = json.dumps(results, indent=2) if results else "No results found"
            
            user_prompt = f"""
            Question: "{question}"
            SQL Query: {sql_query}
            Results: {results_text}
            
            Please provide a clear, business-friendly interpretation of these results.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=f"{system_prompt}\n\n{user_prompt}")])
                ]
            )
            
            return response.text or "Unable to generate response"
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Error interpreting results: {str(e)}"
