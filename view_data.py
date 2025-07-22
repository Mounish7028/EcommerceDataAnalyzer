import os
from dotenv import load_dotenv
from database import DatabaseManager

load_dotenv()

db = DatabaseManager()

# View recent queries
print("=== Recent Query History ===")
history = db.get_query_history(limit=5)
for query in history:
    print(f"Question: {query['question']}")
    print(f"Time: {query['created_at']}")
    print(f"Execution: {query['execution_time_ms']}ms")
    print("-" * 50)

# View sample data
print("\n=== Sample Sales Data ===")
sales_data = db.execute_query("SELECT * FROM total_sales LIMIT 3")
for row in sales_data:
    print(row)