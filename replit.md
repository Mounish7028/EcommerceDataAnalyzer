# E-commerce AI Agent

## Overview

This project is a web-based AI agent that allows users to query e-commerce data using natural language. The system converts natural language questions into SQL queries and executes them against a database containing advertising performance metrics, sales data, and product eligibility information. The application uses Google's Gemini AI model for natural language processing and provides a clean web interface for user interaction.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework for HTTP request handling and API endpoints
- **AI Integration**: Google Gemini AI for natural language to SQL conversion
- **Database**: SQLite for local data storage and querying
- **Data Processing**: Pandas for CSV data loading and manipulation

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default) for server-side rendering
- **UI Framework**: Bootstrap with dark theme for responsive design
- **JavaScript**: Client-side form handling and API communication
- **Styling**: Custom CSS with Font Awesome icons

### Data Layer
- **Database Engine**: SQLite for lightweight, file-based storage
- **Schema Design**: Three main tables (eligibility, ad_sales, total_sales) with proper indexing
- **Data Import**: CSV-to-SQL conversion pipeline using Pandas

## Key Components

### 1. AI Agent (`ai_agent.py`)
- **Purpose**: Converts natural language questions to SQL queries
- **Technology**: Google Gemini AI API
- **Features**: Schema-aware query generation with business metrics context
- **Business Logic**: Includes predefined calculations for RoAS, CPC, conversion rates, and CTR

### 2. Database Manager (`database.py`)
- **Purpose**: Handles data loading, database initialization, and query execution
- **Features**: 
  - Automatic CSV data import from attached_assets directory
  - Index creation for performance optimization
  - Connection management and error handling

### 3. Flask Application (`app.py`)
- **Purpose**: Web server and API endpoint management
- **Endpoints**:
  - `/` - Main interface (GET)
  - `/ask` - Question processing API (POST)
- **Features**: JSON API responses, error handling, logging

### 4. Web Interface (`templates/index.html`)
- **Purpose**: User-friendly interface for asking questions
- **Features**: Responsive design, dark theme, form validation
- **UX Elements**: Loading states, error messages, result display

## Data Flow

1. **Data Initialization**: CSV files are loaded into SQLite tables on startup
2. **User Interaction**: User submits natural language question via web form
3. **AI Processing**: Question is sent to Gemini AI with schema context
4. **SQL Generation**: AI returns SQL query based on the question
5. **Query Execution**: Generated SQL is executed against the database
6. **Response Formatting**: Results are formatted and returned to the user
7. **Display**: Results are shown in the web interface

## External Dependencies

### Required APIs
- **Google Gemini AI**: For natural language processing (requires GEMINI_API_KEY)

### Python Libraries
- `flask`: Web framework
- `pandas`: Data manipulation and CSV processing
- `sqlite3`: Database operations
- `google-genai`: Google Gemini AI client
- `logging`: Application logging
- `json`: JSON handling

### Frontend Dependencies
- **Bootstrap**: CSS framework with dark theme
- **Font Awesome**: Icon library
- **Custom CSS**: Additional styling

### Data Sources
- Three CSV files in `attached_assets/` directory:
  - Product-Level Eligibility Table
  - Product-Level Ad Sales and Metrics
  - Product-Level Total Sales and Metrics

## Deployment Strategy

### Environment Setup
- **Environment Variables**: 
  - `GEMINI_API_KEY`: Required for AI functionality
  - `SESSION_SECRET`: Optional Flask session security (defaults to dev key)

### Database Setup
- **Initialization**: Automatic database creation and data loading on startup
- **Storage**: Local SQLite file (`ecommerce_data.db`)
- **Data Refresh**: Database is recreated each time the application starts

### Development Mode
- **Debug Logging**: Enabled for development
- **Hot Reload**: Flask development server with auto-restart
- **Error Handling**: Comprehensive error messages and logging

### Production Considerations
- **Security**: Environment-based secret management
- **Performance**: Database indexing for optimized queries
- **Scalability**: SQLite suitable for moderate data volumes
- **Monitoring**: Structured logging for debugging and monitoring

### File Structure
```
├── app.py                 # Main Flask application
├── ai_agent.py           # AI query generation
├── database.py           # Database operations
├── templates/
│   └── index.html        # Web interface
├── static/
│   └── style.css         # Custom styling
└── attached_assets/      # CSV data files
```