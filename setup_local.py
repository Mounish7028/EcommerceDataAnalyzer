#!/usr/bin/env python3
"""
Local setup script for the E-commerce AI Agent
Run this script to check your local environment and setup
"""

import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print("✅ Python version:", sys.version.split()[0])
    return True

def check_postgresql():
    """Check if PostgreSQL is accessible"""
    try:
        import psycopg2
        print("✅ psycopg2 (PostgreSQL driver) is installed")
        return True
    except ImportError:
        print("❌ psycopg2 not found. Install with: pip install psycopg2-binary")
        return False

def check_env_file():
    """Check if .env file exists"""
    if os.path.exists('.env'):
        print("✅ .env file found")
        with open('.env', 'r') as f:
            content = f.read()
            if 'DATABASE_URL' in content:
                print("✅ DATABASE_URL configured")
            else:
                print("❌ DATABASE_URL not found in .env")
            if 'GEMINI_API_KEY' in content:
                print("✅ GEMINI_API_KEY configured")
            else:
                print("❌ GEMINI_API_KEY not found in .env")
        return True
    else:
        print("❌ .env file not found. Creating template...")
        create_env_template()
        return False

def create_env_template():
    """Create a template .env file"""
    template = """# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/ecommerce_ai

# Gemini API Configuration  
GEMINI_API_KEY=your_gemini_api_key_here

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=True
"""
    with open('.env', 'w') as f:
        f.write(template)
    print("📝 Created .env template. Please update with your actual values.")

def check_csv_files():
    """Check if required CSV files exist"""
    required_files = [
        "attached_assets/Product-Level Eligibility Table (mapped) - Product-Level Eligibility Table (mapped)_1753169615993.csv",
        "attached_assets/Product-Level Ad Sales and Metrics (mapped) - Product-Level Ad Sales and Metrics (mapped)_1753169682186.csv", 
        "attached_assets/Product-Level Total Sales and Metrics (mapped) - Product-Level Total Sales and Metrics (mapped)_1753169682185.csv"
    ]
    
    all_found = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ Found: {os.path.basename(file_path)}")
        else:
            print(f"❌ Missing: {os.path.basename(file_path)}")
            all_found = False
    
    return all_found

def install_dependencies():
    """Install required Python packages"""
    packages = [
        "flask==3.0.0",
        "flask-sqlalchemy==3.1.1", 
        "google-genai==0.8.0",
        "gunicorn==21.2.0",
        "matplotlib==3.8.2",
        "pandas==2.1.4", 
        "plotly==5.17.0",
        "psycopg2-binary==2.9.9",
        "seaborn==0.13.0",
        "email-validator==2.1.0",
        "sqlalchemy==2.0.23",
        "python-dotenv==1.0.0"
    ]
    
    print("\n📦 Installing Python dependencies...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed: {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install: {package}")

def main():
    """Main setup check"""
    print("🚀 E-commerce AI Agent - Local Setup Check\n")
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check environment file
    check_env_file()
    
    # Check PostgreSQL driver
    check_postgresql()
    
    # Check CSV files
    check_csv_files()
    
    print("\n" + "="*50)
    print("📋 SETUP INSTRUCTIONS:")
    print("="*50)
    print("1. Update .env file with your actual database and API credentials")
    print("2. Ensure PostgreSQL is running on your system")
    print("3. Copy the 3 CSV files to the attached_assets/ folder")
    print("4. Run: python main.py")
    print("5. Open browser to: http://localhost:5000")
    print("\n💡 For detailed setup guide, see LOCAL_SETUP.md")

if __name__ == "__main__":
    main()