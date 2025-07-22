from app import app
import logging
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
    app.run(host='0.0.0.0', port=5000, debug=True)