import os
import logging
import json
from flask import Flask, request, jsonify, render_template
from database import DatabaseManager
from ai_agent import AIAgent
from visualization import VisualizationEngine
from analytics import AdvancedAnalytics

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize components
db_manager = DatabaseManager()
ai_agent = AIAgent()
viz_engine = VisualizationEngine()
analytics = AdvancedAnalytics()

@app.route('/')
def index():
    """Main page with the query interface"""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    """API endpoint to process natural language questions"""
    import time
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Question is required',
                'status': 'error'
            }), 400
            
        question = data['question'].strip()
        if not question:
            return jsonify({
                'error': 'Question cannot be empty',
                'status': 'error'
            }), 400
            
        logger.info(f"Processing question: {question}")
        
        # Generate SQL query using AI
        sql_query = ai_agent.generate_sql_query(question)
        logger.info(f"Generated SQL: {sql_query}")
        
        if not sql_query:
            return jsonify({
                'error': 'Could not generate SQL query from the question',
                'status': 'error'
            }), 400
            
        # Execute query
        results = db_manager.execute_query(sql_query)
        logger.info(f"Query results: {results}")
        
        # Generate human-readable response
        response = ai_agent.generate_response(question, sql_query, results)
        
        # Try to generate visualization
        visualization = viz_engine.get_visualization_for_question(question, results)
        
        # Calculate execution time and save to history
        execution_time = int((time.time() - start_time) * 1000)
        
        # Extract summary from response (first 100 characters)
        response_summary = response[:100] + "..." if len(response) > 100 else response
        
        # Save to history
        db_manager.save_query_history(question, sql_query, response_summary, execution_time)
        
        return jsonify({
            'question': question,
            'sql_query': sql_query,
            'raw_results': results,
            'response': response,
            'visualization': visualization,
            'execution_time_ms': execution_time,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return jsonify({
            'error': f'An error occurred while processing your question: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'ai_agent': 'ready'
    })

@app.route('/sample-questions', methods=['GET'])
def sample_questions():
    """Get sample questions for testing"""
    samples = [
        "What is my total sales?",
        "Calculate the RoAS (Return on Ad Spend)",
        "Which product had the highest CPC (Cost Per Click)?",
        "How many products are eligible for advertising?",
        "What are the top 5 products by total sales?",
        "Which products have the best conversion rate?",
        "What is the average ad spend per product?",
        "Show me products with negative sales",
        "Which products are not eligible and why?",
        "Show me sales trends over time",
        "Display RoAS by product with visualization",
        "Create a chart of product eligibility distribution",
        "Show ad performance scatter plot"
    ]
    
    return jsonify({
        'sample_questions': samples,
        'status': 'success'
    })

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Get comprehensive business dashboard data"""
    try:
        business_summary = analytics.get_business_summary()
        product_analysis = analytics.get_product_performance_analysis(limit=15)
        time_analysis = analytics.get_time_based_analysis(days=7)
        
        # Get key visualizations
        sales_trend = viz_engine.create_sales_trend_chart()
        top_products = viz_engine.create_top_products_chart(limit=10)
        roas_chart = viz_engine.create_roas_by_product_chart(limit=10)
        eligibility_chart = viz_engine.create_eligibility_pie_chart()
        
        return jsonify({
            'business_summary': business_summary,
            'product_analysis': product_analysis,
            'time_analysis': time_analysis,
            'visualizations': {
                'sales_trend': sales_trend,
                'top_products': top_products,
                'roas_chart': roas_chart,
                'eligibility_chart': eligibility_chart
            },
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error generating dashboard: {str(e)}")
        return jsonify({
            'error': f'Error generating dashboard: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/analytics/products', methods=['GET'])
def product_analytics():
    """Get detailed product performance analytics"""
    try:
        limit = request.args.get('limit', 20, type=int)
        product_analysis = analytics.get_product_performance_analysis(limit=limit)
        
        return jsonify({
            'products': product_analysis,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error getting product analytics: {str(e)}")
        return jsonify({
            'error': f'Error getting product analytics: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/visualizations/<chart_type>', methods=['GET'])
def get_visualization(chart_type):
    """Get specific visualization charts"""
    try:
        chart_data = None
        
        if chart_type == 'sales-trend':
            chart_data = viz_engine.create_sales_trend_chart()
        elif chart_type == 'top-products':
            limit = request.args.get('limit', 10, type=int)
            chart_data = viz_engine.create_top_products_chart(limit=limit)
        elif chart_type == 'roas':
            limit = request.args.get('limit', 15, type=int)
            chart_data = viz_engine.create_roas_by_product_chart(limit=limit)
        elif chart_type == 'eligibility':
            chart_data = viz_engine.create_eligibility_pie_chart()
        elif chart_type == 'ad-performance':
            chart_data = viz_engine.create_ad_performance_scatter()
        else:
            return jsonify({
                'error': 'Unknown chart type',
                'status': 'error'
            }), 400
        
        if chart_data:
            return jsonify({
                'chart_data': chart_data,
                'status': 'success'
            })
        else:
            return jsonify({
                'error': 'Could not generate chart',
                'status': 'error'
            }), 500
            
    except Exception as e:
        logger.error(f"Error generating visualization: {str(e)}")
        return jsonify({
            'error': f'Error generating visualization: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/history', methods=['GET'])
def get_query_history():
    """Get query history with basic details"""
    try:
        limit = request.args.get('limit', 20, type=int)
        history = db_manager.get_query_history(limit)
        return jsonify({
            'history': history,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        return jsonify({
            'error': f'History error: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/history/<int:query_id>', methods=['GET'])
def get_query_detail(query_id):
    """Get detailed information about a specific query"""
    try:
        detail = db_manager.get_query_detail(query_id)
        if not detail:
            return jsonify({
                'error': 'Query not found',
                'status': 'error'
            }), 404
        return jsonify({
            'query': detail,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error getting query detail: {str(e)}")
        return jsonify({
            'error': f'Query detail error: {str(e)}',
            'status': 'error'
        }), 500

if __name__ == '__main__':
    # Initialize database with CSV data
    logger.info("Initializing database...")
    db_manager.initialize_database()
    logger.info("Database initialized successfully")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
