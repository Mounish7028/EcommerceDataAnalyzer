# Load environment variables from .env file if it exists (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("ℹ️ python-dotenv not installed, using system environment variables")

from app import app
import logging
import os
from database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize database on startup
db_manager = DatabaseManager()
logger.info("Initializing database...")
db_manager.initialize_database()
logger.info("Database initialized successfully")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    app.run(host='0.0.0.0', port=port, debug=debug_mode)