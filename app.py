import os
import logging
import json
from flask import Flask, request, jsonify, render_template
from database import DatabaseManager
from ai_agent import AIAgent

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize components
db_manager = DatabaseManager()
ai_agent = AIAgent()

@app.route('/')
def index():
    """Main page with the query interface"""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    """API endpoint to process natural language questions"""
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
        
        return jsonify({
            'question': question,
            'sql_query': sql_query,
            'raw_results': results,
            'response': response,
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
        "Which products are not eligible and why?"
    ]
    
    return jsonify({
        'sample_questions': samples,
        'status': 'success'
    })

if __name__ == '__main__':
    # Initialize database with CSV data
    logger.info("Initializing database...")
    db_manager.initialize_database()
    logger.info("Database initialized successfully")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
