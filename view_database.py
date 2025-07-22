#!/usr/bin/env python3
"""
Database viewer script for local development
Use this to view your PostgreSQL data and query history
"""

import os
import sys
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Install python-dotenv to load .env file: pip install python-dotenv")

try:
    from database import DatabaseManager
    from analytics import AnalyticsEngine
    from visualization import VisualizationEngine
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're in the project directory and dependencies are installed")
    sys.exit(1)

def show_database_stats():
    """Show basic database statistics"""
    try:
        db = DatabaseManager()
        
        print("=" * 60)
        print("📊 DATABASE STATISTICS")
        print("=" * 60)
        
        # Count records in each table
        tables = ['eligibility', 'ad_sales', 'total_sales', 'query_history']
        for table in tables:
            try:
                result = db.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                count = result[0]['count'] if result else 0
                print(f"📈 {table.title()}: {count:,} records")
            except Exception as e:
                print(f"❌ Error counting {table}: {str(e)}")
        
        print()
        
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")

def show_query_history(limit=10):
    """Show recent query history"""
    try:
        db = DatabaseManager()
        
        print("=" * 60)
        print(f"📝 RECENT QUERY HISTORY (Last {limit})")
        print("=" * 60)
        
        history = db.get_query_history(limit=limit)
        
        if not history:
            print("No query history found")
            return
            
        for i, query in enumerate(history, 1):
            print(f"\n{i}. Question: {query['question']}")
            print(f"   Time: {query['created_at']}")
            print(f"   Execution: {query.get('execution_time_ms', 'N/A')}ms")
            summary = query.get('summary', 'No summary')
            print(f"   Summary: {summary[:100]}{'...' if len(summary) > 100 else ''}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error fetching query history: {str(e)}")

def show_sample_data():
    """Show sample data from each table"""
    try:
        db = DatabaseManager()
        
        print("=" * 60)
        print("📋 SAMPLE DATA")
        print("=" * 60)
        
        # Sample from each table
        tables = {
            'total_sales': 'SELECT item_id, date, total_sales, total_units_ordered FROM total_sales ORDER BY total_sales DESC LIMIT 3',
            'ad_sales': 'SELECT item_id, date, ad_sales, ad_spend, impressions, clicks FROM ad_sales WHERE ad_spend > 0 ORDER BY ad_spend DESC LIMIT 3',
            'eligibility': 'SELECT item_id, eligibility, eligibility_datetime_utc FROM eligibility WHERE eligibility = \'TRUE\' LIMIT 3'
        }
        
        for table_name, query in tables.items():
            print(f"\n🔸 {table_name.upper()} (Top 3 records):")
            try:
                results = db.execute_query(query)
                if results:
                    for row in results:
                        print(f"   {row}")
                else:
                    print("   No data found")
            except Exception as e:
                print(f"   Error: {str(e)}")
            print()
            
    except Exception as e:
        print(f"Error fetching sample data: {str(e)}")

def show_business_summary():
    """Show business analytics summary"""
    try:
        analytics = AnalyticsEngine()
        
        print("=" * 60)
        print("💼 BUSINESS SUMMARY")
        print("=" * 60)
        
        summary = analytics.generate_business_summary()
        
        if summary:
            sales_metrics = summary.get('sales_metrics', {})
            ad_metrics = summary.get('ad_metrics', {})
            eligibility_metrics = summary.get('eligibility_metrics', {})
            
            print("📈 SALES METRICS:")
            print(f"   Total Revenue: ${sales_metrics.get('total_revenue', 0):,.2f}")
            print(f"   Total Units: {sales_metrics.get('total_units', 0):,}")
            print(f"   Active Products: {sales_metrics.get('active_products', 0):,}")
            
            print("\n📊 ADVERTISING METRICS:")
            print(f"   Ad Revenue: ${ad_metrics.get('total_ad_revenue', 0):,.2f}")
            print(f"   Ad Spend: ${ad_metrics.get('total_ad_spend', 0):,.2f}")
            print(f"   Overall RoAS: {ad_metrics.get('overall_roas', 0):.2f}")
            print(f"   Average CPC: ${ad_metrics.get('avg_cpc', 0):.2f}")
            
            print("\n✅ ELIGIBILITY METRICS:")
            print(f"   Eligible Products: {eligibility_metrics.get('eligible_products', 0):,}")
            print(f"   Total Checked: {eligibility_metrics.get('total_products_checked', 0):,}")
            print(f"   Eligibility Rate: {eligibility_metrics.get('eligibility_rate', 0):.1f}%")
        else:
            print("No business summary available")
            
    except Exception as e:
        print(f"Error generating business summary: {str(e)}")

def interactive_query():
    """Allow user to run custom SQL queries"""
    try:
        db = DatabaseManager()
        
        print("=" * 60)
        print("🔍 INTERACTIVE SQL QUERY")
        print("=" * 60)
        print("Enter your SQL query (or 'quit' to exit):")
        print("Example: SELECT item_id, total_sales FROM total_sales ORDER BY total_sales DESC LIMIT 5")
        print()
        
        while True:
            query = input("SQL> ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
                
            if not query:
                continue
                
            try:
                results = db.execute_query(query)
                print(f"\n📊 Results ({len(results)} rows):")
                for i, row in enumerate(results):
                    print(f"   {i+1}. {row}")
                    if i >= 9:  # Limit to 10 rows for readability
                        print(f"   ... and {len(results) - 10} more rows")
                        break
                print()
            except Exception as e:
                print(f"❌ Query error: {str(e)}\n")
                
    except Exception as e:
        print(f"Error in interactive mode: {str(e)}")

def main():
    """Main function with menu"""
    print("🚀 E-commerce AI Agent - Database Viewer")
    print("=" * 60)
    
    while True:
        print("\nChoose an option:")
        print("1. Database Statistics")
        print("2. Query History")
        print("3. Sample Data")
        print("4. Business Summary")
        print("5. Interactive SQL Query")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            show_database_stats()
        elif choice == '2':
            try:
                limit = int(input("How many recent queries to show? (default 10): ") or "10")
                show_query_history(limit)
            except ValueError:
                show_query_history(10)
        elif choice == '3':
            show_sample_data()
        elif choice == '4':
            show_business_summary()
        elif choice == '5':
            interactive_query()
        elif choice == '6':
            print("👋 Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()