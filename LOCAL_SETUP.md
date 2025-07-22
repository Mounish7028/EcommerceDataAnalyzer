# Local Development Setup Guide

## Prerequisites

Before running this project locally, make sure you have:

1. **Python 3.11+** installed on your machine
2. **PostgreSQL** installed and running (or use a cloud PostgreSQL service)
3. **VS Code** with Python extension
4. **Google Gemini API Key** (get from https://aistudio.google.com/app/apikey)

## Step 1: Project Setup

### 1.1 Clone/Download the Project
```bash
# If using git, clone the repository
git clone <your-repo-url>
cd your-project-folder

# Or download and extract the project files
```

### 1.2 Install Python Dependencies
```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 1.3 Create requirements.txt file
If not present, create `requirements.txt` with these dependencies:
```
flask==3.0.0
flask-sqlalchemy==3.1.1
google-genai==0.8.0
gunicorn==21.2.0
matplotlib==3.8.2
pandas==2.1.4
plotly==5.17.0
psycopg2-binary==2.9.9
seaborn==0.13.0
email-validator==2.1.0
sqlalchemy==2.0.23
```

## Step 2: Database Setup

### 2.1 PostgreSQL Installation

#### Option A: Local PostgreSQL
**Windows:**
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Install with default settings
3. Remember the password you set for 'postgres' user

**macOS:**
```bash
# Using Homebrew
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Option B: Cloud PostgreSQL (Easier)
- Use services like:
  - Neon.tech (free tier available)
  - Supabase (free tier available)
  - ElephantSQL (free tier available)
  - Heroku Postgres (free tier available)

### 2.2 Create Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ecommerce_ai;

# Create user (optional)
CREATE USER ecommerce_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ecommerce_ai TO ecommerce_user;

# Exit psql
\q
```

## Step 3: Environment Configuration

### 3.1 Create .env file
Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/ecommerce_ai

# Or if using cloud database:
# DATABASE_URL=postgresql://username:password@host:port/database_name

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

### 3.2 Install python-dotenv (if not already installed)
```bash
pip install python-dotenv
```

### 3.3 Update main.py to load environment variables
```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

## Step 4: VS Code Setup

### 4.1 Open Project in VS Code
```bash
code .
```

### 4.2 Configure Python Interpreter
1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
2. Type "Python: Select Interpreter"
3. Choose the Python interpreter from your virtual environment

### 4.3 Install Recommended VS Code Extensions
- Python
- Python Debugger
- SQLTools
- SQLTools PostgreSQL/MySQL/SQLite driver

### 4.4 Create VS Code Configuration
Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "program": "main.py",
            "env": {
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "1"
            },
            "args": [],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

## Step 5: Running the Project

### 5.1 Start the Application
```bash
# Method 1: Direct Python
python main.py

# Method 2: Using Flask command
flask run --host=0.0.0.0 --port=5000 --debug

# Method 3: Using Gunicorn (production-like)
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

### 5.2 Access the Application
Open your browser and go to:
- http://localhost:5000
- http://127.0.0.1:5000

## Step 6: Database Management & Viewing Data

### 6.1 Using pgAdmin (GUI Tool)
1. Download and install pgAdmin from https://www.pgadmin.org/
2. Connect to your PostgreSQL server
3. Navigate to your database to view tables and data

### 6.2 Using VS Code SQLTools Extension
1. Install SQLTools extension
2. Add new connection:
   - Connection type: PostgreSQL
   - Host: localhost (or your cloud host)
   - Port: 5432
   - Database: ecommerce_ai
   - Username/Password: your credentials

### 6.3 Command Line Access
```bash
# Connect to database
psql -U postgres -d ecommerce_ai

# View tables
\dt

# View query history
SELECT * FROM query_history ORDER BY created_at DESC LIMIT 10;

# View product data
SELECT * FROM total_sales LIMIT 5;
SELECT * FROM ad_sales LIMIT 5;
SELECT * FROM eligibility LIMIT 5;

# Exit
\q
```

### 6.4 Python Script to View Data
Create `view_data.py`:
```python
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
```

## Step 7: Gemini API Configuration

### 7.1 Get Gemini API Key
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Create new API key
4. Copy the key to your `.env` file

### 7.2 Test Gemini API
```python
# test_gemini.py
import os
from dotenv import load_dotenv
from ai_agent import AIAgent

load_dotenv()

agent = AIAgent()
result = agent.generate_sql_query("What is my total sales?", get_schema_info())
print("AI Response:", result)
```

## Step 8: Troubleshooting

### 8.1 Common Issues

**Database Connection Error:**
- Verify PostgreSQL is running
- Check DATABASE_URL format
- Ensure database exists

**Gemini API Error:**
- Verify API key is correct
- Check internet connection
- Ensure API quota is not exceeded

**Module Import Error:**
- Activate virtual environment
- Install missing dependencies: `pip install -r requirements.txt`

**Port Already in Use:**
- Change port in main.py: `app.run(port=5001)`
- Or kill process using port 5000

### 8.2 Development Tips

1. **Enable Debug Mode:**
   ```python
   app.run(debug=True)
   ```

2. **View Logs:**
   - Check terminal output for errors
   - Add logging statements for debugging

3. **Database Reset:**
   ```python
   # In Python console
   from database import DatabaseManager
   db = DatabaseManager()
   db.load_data()  # Reloads CSV data
   ```

## Features Available Locally

✅ **All features work locally exactly like in Replit:**
- Natural language to SQL conversion using Gemini AI
- Interactive data visualizations with Plotly
- Business analytics dashboard
- Query history tracking
- Product performance analysis
- Real-time chart generation

✅ **Additional local benefits:**
- Faster development with VS Code debugging
- Direct database access with GUI tools
- Custom environment configuration
- Local file system access

## Data Files Required

Make sure these CSV files are in the `attached_assets/` folder:
- `Product-Level Eligibility Table (mapped) - Product-Level Eligibility Table (mapped)_1753169615993.csv`
- `Product-Level Ad Sales and Metrics (mapped) - Product-Level Ad Sales and Metrics (mapped)_1753169682186.csv`
- `Product-Level Total Sales and Metrics (mapped) - Product-Level Total Sales and Metrics (mapped)_1753169682185.csv`

The application will automatically load this data into PostgreSQL on startup.