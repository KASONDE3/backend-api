# Reports API Documentation

This document describes the Reports API routes for detecting recurring tickets in the IT Support Ticketing System.

## Available Routes

### 1. Basic Ticket Filtering
- **Endpoint**: `GET /reports/tickets/filter`
- **Description**: Filter tickets by category_id, user_id, and/or title
- **Query Parameters**:
  - `category_id` (optional): Filter by category ID
  - `user_id` (optional): Filter by user ID
  - `title` (optional): Filter by title (partial match)

### 2. Basic Recurring Ticket Detection
- **Endpoint**: `GET /reports/tickets/recurring-basic`
- **Description**: Find recurring tickets with exact matches on title, category_id, and user_id
- **Features**: No external API required, fast processing
- **Returns**: List of tickets that have exact duplicates

### 3. AI-Powered Recurring Ticket Detection
- **Endpoint**: `GET /reports/tickets/recurring-ai`
- **Description**: Use Gemini API for intelligent pattern recognition
- **Requirements**: GEMINI_API_KEY environment variable must be set
- **Features**: Can detect similar titles, same category, same user patterns

### 4. Comprehensive Recurring Analysis
- **Endpoint**: `GET /reports/tickets/recurring-analysis`
- **Description**: Detailed analysis of recurring patterns with statistics
- **Returns**: JSON with grouped analysis and summary statistics
- **Features**: Groups by different criteria (title, category+user, full match)

### 5. 3-Conditions Recurring Detection
- **Endpoint**: `GET /reports/tickets/recurring-3-conditions`
- **Description**: Find tickets where ALL 3 conditions match (title, category_id, user_id)
- **Features**: Most precise detection of exact recurring issues
- **Returns**: List of tickets with detailed logging of patterns found

## Setup Instructions

### 1. Environment Variables
Set the following environment variables:

```bash
# For Gemini API (required for AI-powered detection)
export GEMINI_API_KEY="your_actual_gemini_api_key_here"

# Database configuration (if not using .env file)
export DB_HOST="localhost"
export DB_PORT="3306"
export DB_USER="your_username"
export DB_PASSWORD="your_password"
export DB_NAME="your_database"
```

### 2. Alternative Configuration
Create a `config.py` file based on `config_example.py`:

```python
# Copy config_example.py to config.py and update with your actual values
GEMINI_API_KEY = "your_actual_gemini_api_key_here"
```

### 3. Gemini API Key
To get a Gemini API key:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Set it as an environment variable or in your config file

## Usage Examples

### Basic Recurring Detection
```bash
curl "http://localhost:8000/reports/tickets/recurring-basic"
```

### AI-Powered Detection
```bash
curl "http://localhost:8000/reports/tickets/recurring-ai"
```

### Comprehensive Analysis
```bash
curl "http://localhost:8000/reports/tickets/recurring-analysis"
```

### 3-Conditions Detection
```bash
curl "http://localhost:8000/reports/tickets/recurring-3-conditions"
```

## Response Formats

### Ticket List Response
```json
[
  {
    "ticket_id": 1,
    "user_id": 123,
    "category_id": 5,
    "title": "Printer not working",
    "description": "Office printer shows error message"
  }
]
```

### Analysis Response
```json
{
  "total_tickets": 100,
  "recurring_by_title": [...],
  "recurring_by_category_user": [...],
  "recurring_by_full_match": [...],
  "summary": {
    "tickets_with_recurring_titles": 15,
    "tickets_with_recurring_category_user": 8,
    "tickets_with_full_recurring_match": 5,
    "total_recurring_tickets": 25
  }
}
```

## Error Handling

- **404**: No tickets found in the system
- **500**: Internal server error or Gemini API configuration issue
- **500**: Gemini API key not configured (for AI routes)

## Logging

All routes include comprehensive logging:
- Info level: Successful operations and patterns found
- Error level: API failures and processing errors
- Debug level: Detailed processing information

## Performance Considerations

- **Basic routes**: Fast, database-only operations
- **AI routes**: Slower due to external API calls (30s timeout)
- **Analysis route**: Moderate performance, processes all tickets in memory
- **3-conditions route**: Fast, efficient grouping algorithm

## Security Notes

- Gemini API key should be kept secure and not committed to version control
- Use environment variables or secure configuration management
- Consider rate limiting for AI-powered routes in production
