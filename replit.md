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
- **Database Engine**: PostgreSQL for production-grade performance and scalability
- **Schema Design**: Three main tables (eligibility, ad_sales, total_sales) with proper indexing
- **Data Import**: CSV-to-SQL conversion pipeline using Pandas and SQLAlchemy
- **Connection**: SQLAlchemy ORM for database abstraction and compatibility

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

### 3. Visualization Engine (`visualization.py`)
- **Purpose**: Creates interactive charts and graphs using Plotly
- **Features**: 
  - Sales trend charts with time-series data
  - Top products bar charts with revenue analysis
  - RoAS performance charts with color-coded performance levels
  - Product eligibility pie charts
  - Ad performance scatter plots (CPC vs Conversion Rate)
  - Automatic chart selection based on question context

### 4. Advanced Analytics (`analytics.py`)
- **Purpose**: Provides comprehensive business intelligence and product analysis
- **Features**: 
  - Business summary dashboard with key metrics
  - Product performance scoring (0-100 scale)
  - Automated recommendations based on performance
  - Time-based trend analysis
  - ROI calculations and efficiency metrics

### 5. Flask Application (`app.py`)
- **Purpose**: Web server and comprehensive API endpoint management
- **Endpoints**:
  - `/` - Main interface (GET)
  - `/ask` - Question processing API with visualization support (POST)
  - `/dashboard` - Comprehensive business dashboard (GET)
  - `/analytics/products` - Detailed product performance analytics (GET)
  - `/visualizations/<chart_type>` - Individual chart generation (GET)
  - `/sample-questions` - Enhanced sample questions (GET)
- **Features**: JSON API responses, error handling, logging, visualization integration

### 6. Enhanced Web Interface (`templates/index.html`)
- **Purpose**: Full-featured business intelligence interface
- **Features**: 
  - Multi-tab interface (Questions, Dashboard, Analytics)
  - Interactive Plotly charts with responsive design
  - Real-time business summary cards
  - Product performance tables with scoring
  - Automated recommendations display
  - Bootstrap dark theme with professional styling

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
- `plotly`: Interactive data visualization
- `matplotlib`: Statistical plotting
- `seaborn`: Advanced statistical visualization
- `logging`: Application logging
- `json`: JSON handling

### Frontend Dependencies
- **Bootstrap**: CSS framework with dark theme
- **Font Awesome**: Icon library
- **Plotly.js**: Interactive charting library
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
- **Storage**: PostgreSQL database (production-ready)
- **Data Refresh**: Database tables are recreated each time the application starts
- **Connection**: Managed through DATABASE_URL environment variable

### Development Mode
- **Debug Logging**: Enabled for development
- **Hot Reload**: Flask development server with auto-restart
- **Error Handling**: Comprehensive error messages and logging

### Production Considerations
- **Security**: Environment-based secret management
- **Performance**: Database indexing for optimized queries
- **Scalability**: PostgreSQL suitable for production workloads and large data volumes
- **Monitoring**: Structured logging for debugging and monitoring

### File Structure
```
├── app.py                 # Main Flask application
├── ai_agent.py           # AI query generation
├── database.py           # Database operations
├── visualization.py      # Interactive chart generation
├── analytics.py          # Business intelligence & analytics
├── main.py               # Application entry point
├── templates/
│   └── index.html        # Enhanced web interface
├── static/
│   └── style.css         # Custom styling
└── attached_assets/      # CSV data files
```

## Recent Changes (July 22, 2025)

### Added Comprehensive Additional Features
- **Data Visualization**: Implemented complete Plotly-based charting system
  - Sales trend charts with time-series analysis
  - Top products bar charts with revenue breakdown
  - RoAS performance analysis with color-coded performance indicators
  - Product eligibility distribution pie charts
  - Advanced scatter plots for ad performance analysis (CPC vs Conversion Rate)

- **Advanced Analytics**: Built comprehensive business intelligence module
  - Product performance scoring system (0-100 scale)
  - Automated performance recommendations based on metrics
  - Business summary dashboard with key KPIs
  - Time-based trend analysis for sales and ad performance
  - ROI and efficiency calculations

- **Enhanced User Interface**: Upgraded to multi-functional business dashboard
  - Added Dashboard tab with real-time business metrics
  - Added Analytics tab with detailed product performance tables
  - Integrated interactive Plotly charts directly in web interface
  - Enhanced sample questions to include visualization requests
  - Professional Bootstrap styling with responsive design

- **Extended API Endpoints**: Added comprehensive API coverage
  - `/dashboard` - Complete business summary with visualizations
  - `/analytics/products` - Detailed product performance analysis
  - `/visualizations/<chart_type>` - Individual chart generation
  - Enhanced `/ask` endpoint with automatic visualization detection

### Performance & User Experience Improvements
- Automatic chart generation based on question context
- Real-time loading indicators for all operations
- Comprehensive error handling across all features
- Responsive design for mobile and desktop use
- Performance scoring and actionable recommendations for products

### Database Migration to PostgreSQL (July 22, 2025)
- **Upgraded Database**: Migrated from SQLite to PostgreSQL for production-grade performance
- **Enhanced Scalability**: PostgreSQL supports larger datasets and concurrent connections
- **SQLAlchemy Integration**: Added proper ORM layer for better database abstraction
- **Improved Performance**: Better query optimization and indexing capabilities
- **Production Ready**: Database now suitable for deployment and scaling

### History Feature Implementation (July 22, 2025)
- **Query History Tracking**: Added persistent storage of user questions and responses in PostgreSQL
- **History Dashboard**: Created dedicated History tab in web interface showing past queries
- **Query Reuse Functionality**: Users can click to reuse previous questions for easy re-execution
- **Performance Metrics**: Tracks and displays execution time for each query
- **Database Schema**: Added query_history table with question, SQL query, summary, timestamp, and execution time

### Local Development Support (July 22, 2025)
- **Local Setup Guide**: Created comprehensive LOCAL_SETUP.md with step-by-step instructions
- **Environment Variable Support**: Added .env file support for local development with python-dotenv
- **Setup Verification Script**: Created setup_local.py to check local environment requirements
- **Database Viewer Tool**: Added view_database.py for local PostgreSQL data inspection and querying
- **VS Code Integration**: Provided configuration files and debugging setup for VS Code development
- **Full Feature Compatibility**: All features work identically in local environment as in Replit